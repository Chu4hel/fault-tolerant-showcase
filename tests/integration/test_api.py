"""Интеграционные тесты для API эндпоинтов витрины цитатника."""

import collections.abc

import pytest
from fastapi.testclient import TestClient

from src.domain.interfaces.catalog_client import ICatalogClient
from src.domain.models.quote import Quote
from src.main import app


class DummyCatalogClient(ICatalogClient):
    """Тестовый клиент каталога для проверки интеграции."""

    def __init__(self) -> None:
        """Инициализирует тестовый каталог."""
        self.url: str | None = None
        self.quotes: dict[str, Quote] = {}

    def set_source_url(self, url: str) -> None:
        """Установить URL каталога."""
        self.url = url

    def get_source_url(self) -> str | None:
        """Получить URL каталога."""
        return self.url

    async def fetch_quote(self, quote_id: str) -> Quote | None:
        """Получить цитату из тестового каталога."""
        return self.quotes.get(quote_id)


@pytest.fixture(autouse=True)
def dummy_catalog() -> collections.abc.Generator[DummyCatalogClient, None, None]:
    """Автоматически подменяет сетевой клиент каталога на мок для изоляции тестов."""
    from src.dependencies import get_quote_service

    service = get_quote_service()
    dummy = DummyCatalogClient()
    saved = service._catalog_client
    service._catalog_client = dummy
    yield dummy
    service._catalog_client = saved


@pytest.fixture
def client() -> TestClient:
    """Фикстура TestClient для FastAPI приложения."""
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Проверяет эндпоинт /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_set_catalog_source(client: TestClient) -> None:
    """Проверяет установку адреса каталога."""
    response = client.post("/catalog/source", json={"url": "http://catalog.internal:9000"})
    assert response.status_code == 200
    assert response.json() == {"source": "http://catalog.internal:9000"}


def test_upsert_and_read_quote(client: TestClient) -> None:
    """Проверяет добавление цитаты редакцией и чтение читателем."""
    quote_id = "test-q-1"
    payload = {"author": "Марк Аврелий", "text": "Начни утро с мысли о прекрасном."}

    # Редакция сохраняет цитату
    put_resp = client.put(f"/catalog/{quote_id}", json=payload)
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data["id"] == quote_id
    assert data["author"] == payload["author"]
    assert data["text"] == payload["text"]

    # Читатель читает цитату
    get_resp = client.get(f"/quotes/{quote_id}")
    assert get_resp.status_code == 200
    assert get_resp.headers.get("X-Source") == "LOCAL"
    assert get_resp.json()["id"] == quote_id


def test_upsert_validation_bounds(client: TestClient) -> None:
    """Проверяет валидацию ограничений полей author и text (422)."""
    # Пустой автор
    r1 = client.put("/catalog/q-val-1", json={"author": "", "text": "Валидный текст"})
    assert r1.status_code == 422

    # Автор длиннее 200 знаков
    r2 = client.put(
        "/catalog/q-val-2",
        json={"author": "A" * 201, "text": "Валидный текст"},
    )
    assert r2.status_code == 422

    # Текст длиннее 16384 знаков
    r3 = client.put(
        "/catalog/q-val-3",
        json={"author": "Автор", "text": "T" * 16385},
    )
    assert r3.status_code == 422


def test_delete_quote(client: TestClient) -> None:
    """Проверяет удаление цитаты редакцией."""
    quote_id = "test-del-1"
    client.put(f"/catalog/{quote_id}", json={"author": "Автор", "text": "Текст"})

    # Удаление
    del_resp = client.delete(f"/catalog/{quote_id}")
    assert del_resp.status_code == 200
    assert del_resp.json() == {"deleted": True}

    # Повторный запрос от читателя должен вернуть 404
    get_resp = client.get(f"/quotes/{quote_id}")
    assert get_resp.status_code == 404

    # Удаление несуществующей цитаты -> 404
    del_not_found = client.delete("/catalog/non-existing-quote-id")
    assert del_not_found.status_code == 404


def test_import_snapshot_and_stats(client: TestClient) -> None:
    """Проверяет импорт снимка и получение статистики /stats."""
    snapshot_body = (
        '{"quotes":[\n'
        '{"id": "snap-q-1", "author": "Сократ", "text": "Я знаю, что ничего не знаю"},\n'
        '{"id": "snap-q-2", "author": "Платон", "text": "Красота в глазах смотрящего"}\n'
        "]}"
    )

    imp_resp = client.post(
        "/import",
        content=snapshot_body.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    assert imp_resp.status_code == 200
    imp_data = imp_resp.json()
    assert imp_data["imported"] >= 2

    # Читатель запрашивает цитату из снимка — должна отдаваться мгновенно из LOCAL
    reader_resp = client.get("/quotes/snap-q-1")
    assert reader_resp.status_code == 200
    assert reader_resp.headers.get("X-Source") == "LOCAL"
    assert reader_resp.json()["author"] == "Сократ"

    # Некорректный снимок без обязательного поля author -> 400
    invalid_snap = '{"quotes":[\n{"id": "bad-1", "text": "Без автора"}\n]}'
    bad_resp = client.post(
        "/import",
        content=invalid_snap.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    assert bad_resp.status_code == 400

    # Проверка /stats
    stats_resp = client.get("/stats")
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    for field in [
        "served_local",
        "served_from_catalog",
        "catalog_reads",
        "evictions",
        "local",
        "bytes",
        "catalog",
    ]:
        assert field in stats_data
