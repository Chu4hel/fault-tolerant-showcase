"""Интерфейс локального хранилища цитат."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from src.domain.models.quote import Quote
from src.domain.models.stats import ShowcaseStats


class IQuoteStorage(ABC):
    """Абстрактный интерфейс in-memory хранилища цитат."""

    @abstractmethod
    def is_deleted(self, quote_id: str) -> bool:
        """Проверить, помечена ли цитата как удаленная редакцией.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            True, если цитата снята с публикации до следующего снимка.
        """
        pass

    @abstractmethod
    def get_cached_with_age(self, quote_id: str) -> tuple[Quote, float] | None:
        """Получить цитату и ее возраст из кэша.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Кортеж (Quote, age_seconds) или None, если запись отсутствует.
        """
        pass

    @abstractmethod
    def increment_served_local(self) -> None:
        """Увеличить счетчик локально отданных ответов."""
        pass

    @abstractmethod
    def increment_served_from_catalog(self) -> None:
        """Увеличить счетчик ответов, потребовавших каталог."""
        pass

    @abstractmethod
    def increment_catalog_reads(self) -> None:
        """Увеличить счетчик запросов в каталог."""
        pass

    @abstractmethod
    async def get(self, quote_id: str) -> Quote | None:
        """Получить цитату по идентификатору из локального хранилища.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Объект цитаты или None, если запись отсутствует.
        """
        pass

    @abstractmethod
    async def put(self, quote: Quote) -> None:
        """Сохранить или обновить цитату в хранилище.

        Args:
            quote: Объект цитаты.
        """
        pass

    @abstractmethod
    async def delete(self, quote_id: str) -> bool:
        """Удалить цитату из локального хранилища.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            True, если цитата была найдена и удалена, иначе False.
        """
        pass

    @abstractmethod
    async def import_snapshot_stream(self, stream: AsyncIterator[bytes]) -> tuple[int, int]:
        """Импортировать снимок каталога из потока данных.

        Args:
            stream: Асинхронный поток сырых байтов снимка.

        Returns:
            Кортеж (imported_count, dropped_count).
        """
        pass

    @abstractmethod
    async def get_stats(self) -> ShowcaseStats:
        """Получить текущую эксплуатационную статистику хранилища.

        Returns:
            Экземпляр модели ShowcaseStats.
        """
        pass
