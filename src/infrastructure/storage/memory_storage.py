"""Реализация in-memory хранилища цитат с контролем потребления памяти."""

from typing import AsyncIterator, Optional, Tuple

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

    async def get(self, quote_id: str) -> Optional[Quote]:
        """Получить цитату из локального кэша."""
        raise NotImplementedError

    async def put(self, quote: Quote) -> None:
        """Сохранить или обновить цитату в локальном кэше."""
        raise NotImplementedError

    async def delete(self, quote_id: str) -> bool:
        """Удалить цитату из локального кэша и пометить как снятую."""
        raise NotImplementedError

    async def import_snapshot_stream(
        self, stream: AsyncIterator[bytes]
    ) -> Tuple[int, int]:
        """Потоковая обработка и импорт снимка каталога."""
        raise NotImplementedError

    async def get_stats(self) -> ShowcaseStats:
        """Получить текущую сводку статистики."""
        raise NotImplementedError
