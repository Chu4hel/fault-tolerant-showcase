"""Зависимости приложения и внедрение сервисов через контейнер chutils."""

from chutils import default_container

from src.application.quote_service import QuoteService
from src.config import settings
from src.domain.interfaces.catalog_client import ICatalogClient
from src.domain.interfaces.quote_storage import IQuoteStorage
from src.infrastructure.catalog_client.http_catalog_client import HttpCatalogClient
from src.infrastructure.storage.memory_storage import MemoryQuoteStorage


def create_quote_storage() -> IQuoteStorage:
    """Создает экземпляр хранилища цитат.

    Returns:
        Экземпляр хранилища цитат в памяти.
    """
    return MemoryQuoteStorage(
        max_bytes=settings.max_cache_bytes,
        max_age_seconds=settings.quote_max_age_seconds,
    )


def create_catalog_client() -> ICatalogClient:
    """Создает экземпляр HTTP клиента каталога.

    Returns:
        Экземпляр клиента удаленного каталога.
    """
    return HttpCatalogClient(
        timeout_seconds=settings.quote_read_timeout_seconds - 0.5,
    )


def create_quote_service(
    storage: IQuoteStorage,
    catalog_client: ICatalogClient,
) -> QuoteService:
    """Создает экземпляр QuoteService через автовайринг зависимостей.

    Args:
        storage: Хранилище цитат.
        catalog_client: Клиент для обращения к удаленному каталогу.

    Returns:
        Сконфигурированный экземпляр QuoteService.
    """
    return QuoteService(
        storage=storage,
        catalog_client=catalog_client,
        max_age_seconds=settings.quote_max_age_seconds,
    )


def setup_container() -> None:
    """Регистрирует интерфейсы и реализации в DI-контейнере chutils."""
    default_container.register(IQuoteStorage, create_quote_storage, scope="singleton")
    default_container.register(ICatalogClient, create_catalog_client, scope="singleton")
    default_container.register(QuoteService, create_quote_service, scope="singleton")


# Первичная инициализация контейнера
setup_container()


def get_quote_service() -> QuoteService:
    """Возвращает экземпляр QuoteService из DI-контейнера chutils.

    Returns:
        Экземпляр QuoteService.
    """
    service: QuoteService = default_container.resolve(QuoteService)
    return service
