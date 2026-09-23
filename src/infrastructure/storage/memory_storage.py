"""Реализация in-memory хранилища цитат с контролем потребления памяти."""

from collections.abc import AsyncIterator

from src.domain.interfaces.quote_storage import IQuoteStorage
from src.domain.models.quote import Quote
from src.domain.models.stats import ShowcaseStats


class MemoryQuoteStorage(IQuoteStorage):
    """In-memory реализация хранилища цитат с поддержкой LRU-вытеснения."""

    def __init__(self, max_bytes: int = 120 * 1024 * 1024) -> None:
        """Инициализирует in-memory хранилище.

        Args:
            max_bytes: Максимальный лимит байтов под локальный кэш цитат.
        """
        self._max_bytes = max_bytes

    async def get(self, quote_id: str) -> Quote | None:
        """Получить цитату из локального кэша.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Объект Quote или None, если запись отсутствует в кэше.
        """
        raise NotImplementedError

    async def put(self, quote: Quote) -> None:
        """Сохранить или обновить цитату в локальном кэше.

        Args:
            quote: Объект цитаты.
        """
        raise NotImplementedError

    async def delete(self, quote_id: str) -> bool:
        """Удалить цитату из локального кэша и пометить как снятую.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            True, если цитата была удалена, иначе False.
        """
        raise NotImplementedError

    async def import_snapshot_stream(
        self, stream: AsyncIterator[bytes]
    ) -> tuple[int, int]:
        """Потоковая обработка и импорт снимка каталога.

        Args:
            stream: Поток байт входного снимка.

        Returns:
            Кортеж (imported_count, dropped_count).
        """
        raise NotImplementedError

    async def get_stats(self) -> ShowcaseStats:
        """Получить текущую сводку статистики.

        Returns:
            Экземпляр ShowcaseStats.
        """
        raise NotImplementedError
