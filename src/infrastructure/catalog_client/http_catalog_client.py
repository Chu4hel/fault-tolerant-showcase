"""HTTP-клиент для взаимодействия с сервисом каталога."""

from chutils.web import AsyncWebClient

from src.domain.interfaces.catalog_client import ICatalogClient
from src.domain.models.quote import Quote


class HttpCatalogClient(ICatalogClient):
    """Асинхронный HTTP-клиент каталога с поддержкой Retry-After."""

    def __init__(self, timeout_seconds: float = 3.0) -> None:
        """Инициализирует HTTP-клиент каталога.

        Args:
            timeout_seconds: Таймаут на запрос к каталогу.
        """
        self._source_url: str | None = None
        self._timeout_seconds = timeout_seconds
        self._client: AsyncWebClient | None = None

    def set_source_url(self, url: str) -> None:
        """Устанавливает или обновляет URL каталога.

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

    async def fetch_quote(self, quote_id: str) -> Quote | None:
        """Запрашивает цитату из внешнего каталога.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Экземпляр Quote, если найден, иначе None.
        """
        raise NotImplementedError
