"""E2E симуляция условий проверки ТЗ тестирующей системой.

Проверяет:
1. Запуск сервиса один раз на весь прогон.
2. Первичную проверку GET /health -> 200 сразу после старта.
3. Установку адреса внешнего каталога через POST /catalog/source.
4. Изоляцию проверок по уникальным quote_id.
5. Проверку счетчиков /stats (разница до и после каждой операции).
6. Коды ответов, тела, заголовки (X-Source) и время ответа (<= 3.0 с).
7. Поведение при 503 Retry-After и защите Circuit Breaker / Bulkhead.
8. Импорт снимка POST /import и мгновенную доступность GET /health после него.
"""

import json
import time
import urllib.parse
from typing import Any

import pytest
from chutils.scraping.testing.server import LocalTestServer, _CustomHTTPServer, _TestHandler
from fastapi.testclient import TestClient

from src.main import app


class CatalogMockHandler(_TestHandler):  # type: ignore[misc]
    """Кастомный обработчик запросов каталога с поддержкой задержек и Retry-After."""

    def _handle_request(self, method: str) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = parsed.query

        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b""

        headers_dict = {k: v for k, v in self.headers.items()}
        from chutils.scraping.testing.server import RecordedRequest

        rec = RecordedRequest(
            method=method,
            path=path,
            headers=headers_dict,
            body=body,
            query=query,
        )
        self.server.owner.requests_log.append(rec)

        custom_routes = getattr(self.server.owner, "_custom_catalog_routes", {})
        if path in custom_routes:
            status_code, resp_headers, resp_bytes, delay = custom_routes[path]
            if delay > 0:
                time.sleep(delay)

            self.send_response(status_code)
            for h_key, h_val in resp_headers.items():
                self.send_header(h_key, h_val)
            self.send_header("Content-Length", str(len(resp_bytes)))
            self.end_headers()
            if method != "HEAD":
                self.wfile.write(resp_bytes)
                self.wfile.flush()
            return

        super()._handle_request(method)


class CatalogMockServer(LocalTestServer):  # type: ignore[misc]
    """Тестовый сервер каталога на базе LocalTestServer из chutils."""

    def __init__(self) -> None:
        super().__init__(host="127.0.0.1", port=0)
        self._custom_catalog_routes: dict[str, tuple[int, dict[str, str], bytes, float]] = {}

    def set_quote(self, quote_id: str, data: dict[str, Any], delay: float = 0.0) -> None:
        """Регистрирует цитату в каталоге."""
        path = f"/quote/{quote_id}"
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json; charset=utf-8"}
        self._custom_catalog_routes[path] = (200, headers, payload, delay)

    def set_busy(self, quote_id: str, retry_after: int = 2) -> None:
        """Имитирует перегрузку каталога 503 с заголовком Retry-After."""
        path = f"/quote/{quote_id}"
        payload = json.dumps({"detail": "busy"}).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Retry-After": str(retry_after),
        }
        self._custom_catalog_routes[path] = (503, headers, payload, 0.0)

    def set_not_found(self, quote_id: str) -> None:
        """Имитирует отсутствие цитаты в каталоге 404."""
        path = f"/quote/{quote_id}"
        payload = json.dumps({"detail": "not found"}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        self._custom_catalog_routes[path] = (404, headers, payload, 0.0)

    def start(self) -> "CatalogMockServer":
        """Запускает кастомный сервер с CatalogMockHandler."""
        if self.is_running:
            return self

        import threading

        self._httpd = _CustomHTTPServer(
            (self.host, self._requested_port),
            CatalogMockHandler,
            owner=self,
        )
        self._actual_port = self._httpd.server_address[1]

        self._thread = threading.Thread(
            target=self._httpd.serve_forever,
            daemon=True,
            name=f"CatalogMockServer-{self.port}",
        )
        self._thread.start()
        return self


@pytest.fixture(scope="module")
def catalog_server() -> Any:
    """Запускает мок-сервер каталога один раз на модуль тестов."""
    server = CatalogMockServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture(scope="module")
def e2e_client() -> TestClient:
    """Клиент витрины один раз на модуль тестов (имитация единого процесса)."""
    return TestClient(app)


def test_e2e_judging_workflow(e2e_client: TestClient, catalog_server: CatalogMockServer) -> None:
    """Полная эмуляция жизненного цикла и проверок проверяющей платформы."""
    # 1. Проверяется, что /health отвечает 200 сразу после старта
    resp = e2e_client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}

    # 2. Сразу после старта витрине сообщают адрес каталога
    catalog_base_url = f"http://127.0.0.1:{catalog_server.port}"
    resp_source = e2e_client.post("/catalog/source", json={"url": catalog_base_url})
    assert resp_source.status_code == 200
    assert resp_source.json()["source"] == catalog_base_url

    # 3. Базовый замер /stats
    initial_stats = e2e_client.get("/stats").json()
    assert "served_local" in initial_stats

    # --- Проверка 1: Доставка цитаты из каталога (X-Source: CATALOG) ---
    catalog_server.set_quote(
        "q-judging-1",
        {"id": "q-judging-1", "author": "Лао-цзы", "text": "Знающий не говорит"},
    )
    stats_before = e2e_client.get("/stats").json()

    start_time = time.perf_counter()
    resp_quote = e2e_client.get("/quotes/q-judging-1")
    duration = time.perf_counter() - start_time

    assert duration <= 3.0, f"Время ответа читателю ({duration:.3f} с) превысило лимит 3 с"
    assert resp_quote.status_code == 200
    assert resp_quote.headers.get("X-Source") == "CATALOG"
    assert resp_quote.json()["id"] == "q-judging-1"
    assert resp_quote.json()["author"] == "Лао-цзы"

    stats_after = e2e_client.get("/stats").json()
    assert stats_after["served_from_catalog"] - stats_before["served_from_catalog"] == 1
    assert stats_after["catalog_reads"] - stats_before["catalog_reads"] == 1

    # --- Проверка 2: Повторный запрос читателем (X-Source: LOCAL, быстро) ---
    stats_before = e2e_client.get("/stats").json()

    start_time = time.perf_counter()
    resp_cached = e2e_client.get("/quotes/q-judging-1")
    duration = time.perf_counter() - start_time

    assert duration < 0.1, f"Локальный кэш должен отвечать мгновенно: {duration:.3f} с"
    assert resp_cached.status_code == 200
    assert resp_cached.headers.get("X-Source") == "LOCAL"
    assert resp_cached.json()["author"] == "Лао-цзы"

    stats_after = e2e_client.get("/stats").json()
    assert stats_after["served_local"] - stats_before["served_local"] == 1
    assert stats_after["catalog_reads"] - stats_before["catalog_reads"] == 0

    # --- Проверка 3: Редакция обновляет цитату PUT /catalog/{id} ---
    stats_before = e2e_client.get("/stats").json()
    resp_put = e2e_client.put(
        "/catalog/q-judging-2",
        json={"author": "Эпиктет", "text": "Людей мучают не вещи, а представления о них"},
    )
    assert resp_put.status_code == 200
    assert resp_put.json()["id"] == "q-judging-2"

    # Читатель сразу получает новую цитату из LOCAL
    resp_read_put = e2e_client.get("/quotes/q-judging-2")
    assert resp_read_put.status_code == 200
    assert resp_read_put.headers.get("X-Source") == "LOCAL"
    assert resp_read_put.json()["author"] == "Эпиктет"

    # --- Проверка 4: Редакция удаляет цитату DELETE /catalog/{id} ---
    resp_del = e2e_client.delete("/catalog/q-judging-2")
    assert resp_del.status_code == 200
    assert resp_del.json()["deleted"] is True

    # Читатель получает 404
    resp_del_read = e2e_client.get("/quotes/q-judging-2")
    assert resp_del_read.status_code == 404

    # --- Проверка 5: Каталог перегружен 503 Retry-After ---
    catalog_server.set_busy("q-judging-busy", retry_after=2)
    stats_before = e2e_client.get("/stats").json()

    start_time = time.perf_counter()
    resp_busy = e2e_client.get("/quotes/q-judging-busy")
    duration = time.perf_counter() - start_time

    assert duration <= 3.0, "Читатель не должен ждать свыше 3 с даже при отказе каталога"
    assert resp_busy.status_code == 404

    # Повторный запрос в период паузы: витрина не долбит каталог повторно
    catalog_reads_before = len(catalog_server.requests_log)
    e2e_client.get("/quotes/q-judging-busy")
    catalog_reads_after = len(catalog_server.requests_log)
    assert catalog_reads_after == catalog_reads_before, "Витрина должна соблюдать паузу Retry-After"

    # --- Проверка 6: Прием снимка каталога POST /import и проверка живучести ---
    snapshot_lines = [
        '{"quotes":[',
        '{"id": "q-snap-1", "author": "Платон", "text": "Основа всякой мудрости — терпение"},',
        '{"id": "q-snap-2", "author": "Сократ", "text": "Я знаю, что ничего не знаю"}',
        "]}",
    ]
    snapshot_payload = "\n".join(snapshot_lines).encode("utf-8")

    stats_before = e2e_client.get("/stats").json()
    resp_import = e2e_client.post(
        "/import",
        content=snapshot_payload,
        headers={"Content-Type": "application/json"},
    )
    assert resp_import.status_code == 200
    import_data = resp_import.json()
    assert import_data["imported"] == 2

    # КРИТИЧЕСКИЙ ПУНКТ ТЗ: Процесс жив и отвечает 200 на /health сразу после импорта
    resp_health_post_import = e2e_client.get("/health")
    assert resp_health_post_import.status_code == 200
    assert resp_health_post_import.json() == {"status": "healthy"}

    # Проверяем доступность импортированных цитат
    resp_snap_quote = e2e_client.get("/quotes/q-snap-1")
    assert resp_snap_quote.status_code == 200
    assert resp_snap_quote.headers.get("X-Source") == "LOCAL"
    assert resp_snap_quote.json()["author"] == "Платон"

    stats_final = e2e_client.get("/stats").json()
    assert stats_final["catalog"] == 2
    assert stats_final["local"] >= 2
