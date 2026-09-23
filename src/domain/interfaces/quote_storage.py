"""Интерфейс локального хранилища цитат."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from src.domain.models.quote import Quote
from src.domain.models.stats import ShowcaseStats


class IQuoteStorage(ABC):
    """Абстрактный интерфейс in-memory хранилища цитат."""

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
