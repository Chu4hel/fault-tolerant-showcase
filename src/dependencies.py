"""Зависимости приложения и внедрение сервисов (Dependency Injection)."""

from src.application.quote_service import QuoteService
from src.config import settings
from src.infrastructure.catalog_client.http_catalog_client import HttpCatalogClient
from src.infrastructure.storage.memory_storage import MemoryQuoteStorage

storage_instance = MemoryQuoteStorage(
    max_bytes=settings.max_cache_bytes,
    max_age_seconds=settings.quote_max_age_seconds,
)
"""Глобальный экземпляр in-memory хранилища цитат."""

catalog_client_instance = HttpCatalogClient(
    timeout_seconds=settings.quote_read_timeout_seconds - 0.5,
)
"""Глобальный экземпляр HTTP-клиента каталога."""

quote_service_instance = QuoteService(
    storage=storage_instance,
    catalog_client=catalog_client_instance,
)
"""Глобальный экземпляр сервиса витрины цитат."""


def get_quote_service() -> QuoteService:
    """Возвращает глобальный экземпляр QuoteService для внедрения в маршрутизаторы.

    Returns:
        Экземпляр QuoteService.
    """
    return quote_service_instance
