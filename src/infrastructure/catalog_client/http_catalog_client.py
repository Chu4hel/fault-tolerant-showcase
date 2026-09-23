"""HTTP-клиент для взаимодействия с сервисом каталога."""

import asyncio
import time

import httpx  # chutils: ignore[ChutilsIntegrationRule]
from chutils.web import AsyncWebClient

from src.domain.interfaces.catalog_client import ICatalogClient
from src.domain.models.quote import Quote


class HttpCatalogClient(ICatalogClient):
    """Асинхронный HTTP-клиент каталога с защитой от перегрузки и поддержкой Retry-After."""

    def __init__(self, timeout_seconds: float = 2.5) -> None:
        """Инициализирует HTTP-клиент каталога.

        Args:
            timeout_seconds: Таймаут на запрос к каталогу (по ТЗ читатель ждет до 3 сек).
        """
        self._source_url: str | None = None
        self._timeout_seconds = timeout_seconds
        self._client: AsyncWebClient | None = None

        # Временная метка, до которой каталог заблокирован по Retry-After или сбою
        self._busy_until: float = 0.0

        # Request coalescing (singleflight) для предотвращения дублирующих запросов
        self._in_flight: dict[str, asyncio.Future[Quote | None]] = {}

    def set_source_url(self, url: str) -> None:
        """Устанавливает или обновляет базовый URL каталога.

        Args:
            url: URL каталога.
        """
        self._source_url = url.rstrip("/")

    def get_source_url(self) -> str | None:
        """Возвращает текущий URL каталога.

        Returns:
            Строка с URL или None, если адрес не задан.
        """
        return self._source_url

    async def _get_client(self) -> AsyncWebClient:
        """Ленивая инициализация пула HTTP-клиента.

        Returns:
            Экземпляр AsyncWebClient.
        """
        if self._client is None or self._client.is_closed:
            self._client = AsyncWebClient(
                timeout=httpx.Timeout(self._timeout_seconds),
                limits=httpx.Limits(max_keepalive_connections=32, max_connections=64),
            )
        return self._client

    async def close(self) -> None:
        """Закрывает базовый пул HTTP-соединений."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def fetch_quote(self, quote_id: str) -> Quote | None:
        """Запрашивает цитату из внешнего каталога с дедупликацией и защитой от перегрузки.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Экземпляр Quote, если найден (200), либо None при 404, 503 или недоступности.
        """
        if not self._source_url:
            return None

        # Если каталог попросил подождать (Retry-After) или лежит, не долбим его
        now = time.monotonic()
        if now < self._busy_until:
            return None

        # Singleflight: если запрос по этой цитате уже выполняется, подключаемся к нему
        if quote_id in self._in_flight:
            return await self._in_flight[quote_id]

        loop = asyncio.get_running_loop()
        future: asyncio.Future[Quote | None] = loop.create_future()
        self._in_flight[quote_id] = future

        try:
            result = await self._execute_request(quote_id)
            future.set_result(result)
            return result
        except Exception:
            future.set_result(None)
            return None
        finally:
            self._in_flight.pop(quote_id, None)

    async def _execute_request(self, quote_id: str) -> Quote | None:
        """Выполняет реальный сетевой запрос к каталогу.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Объект Quote или None.
        """
        if not self._source_url:
            return None

        client = await self._get_client()
        url = f"{self._source_url}/quote/{quote_id}"

        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                return Quote.model_validate(data)

            if response.status_code == 404:
                return None

            if response.status_code == 503:
                # Читаем заголовок Retry-After
                retry_after_header = response.headers.get("Retry-After", "1.0")
                try:
                    retry_seconds = float(retry_after_header)
                except ValueError:
                    retry_seconds = 1.0

                self._busy_until = time.monotonic() + retry_seconds
                return None

            return None
        except (httpx.TimeoutException, httpx.NetworkError):
            # Каталог упал или не отвечает — пауза 2 секунды, чтобы дать ему подняться
            self._busy_until = time.monotonic() + 2.0
            return None
        except Exception:
            return None
