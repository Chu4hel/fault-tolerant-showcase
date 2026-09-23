"""HTTP-клиент для взаимодействия с сервисом каталога."""

from typing import Optional

import httpx

from src.domain.interfaces.catalog_client import ICatalogClient
from src.domain.models.quote import Quote


class HttpCatalogClient(ICatalogClient):
    """Асинхронный HTTP-клиент каталога с поддержкой Retry-After."""

    def __init__(self, timeout_seconds: float = 3.0) -> None:
        """Инициализирует HTTP-клиент каталога.

        Args:
            timeout_seconds: Таймаут на запрос к каталогу.
        """
        self._source_url: Optional[str] = None
        self._timeout_seconds = timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None

    def set_source_url(self, url: str) -> None:
        """Устанавливает или обновляет URL каталога."""
        self._source_url = url.rstrip("/")

    def get_source_url(self) -> Optional[str]:
        """Возвращает текущий URL каталога."""
        return self._source_url

    async def fetch_quote(self, quote_id: str) -> Optional[Quote]:
        """Запрашивает цитату из внешнего каталога."""
        raise NotImplementedError
