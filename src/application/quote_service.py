"""Сервис оркестрации бизнес-логики витрины цитат."""

from typing import AsyncIterator, Optional, Tuple

from src.domain.interfaces.catalog_client import ICatalogClient
from src.domain.interfaces.quote_storage import IQuoteStorage
from src.domain.models.quote import Quote, QuoteSource, QuoteUpsertPayload
from src.domain.models.stats import ShowcaseStats


class QuoteService:
    """Сервис для работы с цитатами, каталогом и статистикой."""

    def __init__(
        self,
        storage: IQuoteStorage,
        catalog_client: ICatalogClient,
    ) -> None:
        """Инициализирует сервис витрины цитат.

        Args:
            storage: Реализация хранилища цитат (Dependency Inversion).
            catalog_client: Реализация клиента каталога (Dependency Inversion).
        """
        self._storage = storage
        self._catalog_client = catalog_client

    def set_catalog_source(self, url: str) -> str:
        """Задает или обновляет адрес каталога.

        Args:
            url: URL источника каталога.

        Returns:
            Установленный URL.
        """
        self._catalog_client.set_source_url(url)
        return url

    async def get_quote_for_reader(
        self, quote_id: str
    ) -> Optional[Tuple[Quote, QuoteSource]]:
        """Получить цитату для читателя с указанием источника (LOCAL / CATALOG).

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Кортеж (Quote, QuoteSource) или None, если цитата не найдена.
        """
        raise NotImplementedError

    async def upsert_quote(self, quote_id: str, payload: QuoteUpsertPayload) -> Quote:
        """Добавить или обновить цитату редакцией.

        Args:
            quote_id: Идентификатор цитаты.
            payload: Данные цитаты от редакции.

        Returns:
            Актуализированный объект Quote.
        """
        raise NotImplementedError

    async def delete_quote(self, quote_id: str) -> bool:
        """Снять цитату с публикации редакцией.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            True, если цитата снята с публикации, иначе False.
        """
        raise NotImplementedError

    async def import_snapshot(
        self, stream: AsyncIterator[bytes]
    ) -> Tuple[int, int]:
        """Принять и обработать полный снимок каталога.

        Args:
            stream: Поток байт входного JSON-снимка.

        Returns:
            Кортеж (imported_count, dropped_count).
        """
        raise NotImplementedError

    async def get_stats(self) -> ShowcaseStats:
        """Получить актуальную статистику витрины.

        Returns:
            Сводка статистики ShowcaseStats.
        """
        raise NotImplementedError
