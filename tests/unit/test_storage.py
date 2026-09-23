"""Модульные тесты для MemoryQuoteStorage."""

from collections.abc import AsyncIterator

import pytest

from src.domain.models.quote import Quote
from src.infrastructure.storage.memory_storage import MemoryQuoteStorage


async def _make_stream(data: bytes, chunk_size: int = 16) -> AsyncIterator[bytes]:
    """Вспомогательный генератор асинхронного потока байт."""
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


@pytest.mark.asyncio
async def test_storage_put_and_get() -> None:
    """Проверяет сохранение и извлечение цитаты из кэша."""
    storage = MemoryQuoteStorage()
    quote = Quote(id="q-1", author="Тест", text="Текст цитаты")

    await storage.put(quote)
    retrieved = await storage.get("q-1")

    assert retrieved is not None
    assert retrieved.id == "q-1"
    assert retrieved.author == "Тест"
    assert retrieved.text == "Текст цитаты"


@pytest.mark.asyncio
async def test_storage_eviction_on_byte_limit() -> None:
    """Проверяет вытеснение старейших цитат при достижении лимита памяти."""
    # Задаем очень маленький лимит памяти, достаточный только для одной цитаты
    storage = MemoryQuoteStorage(max_bytes=60)
    q1 = Quote(id="q-1", author="A", text="Text 1")
    q2 = Quote(id="q-2", author="B", text="Text 2")

    await storage.put(q1)
    stats1 = await storage.get_stats()
    assert stats1.local == 1
    assert stats1.evictions == 0

    # Добавляем вторую цитату — первая должна быть вытеснена
    await storage.put(q2)
    stats2 = await storage.get_stats()
    assert stats2.local == 1
    assert stats2.evictions == 1
    assert await storage.get("q-1") is None
    assert await storage.get("q-2") is not None


@pytest.mark.asyncio
async def test_storage_delete_and_snapshot_reset() -> None:
    """Проверяет удаление цитаты и восстановление видимости после нового снимка."""
    storage = MemoryQuoteStorage()
    quote = Quote(id="q-1", author="Автор", text="Текст")
    await storage.put(quote)

    # Удаляем через витрину
    deleted = await storage.delete("q-1")
    assert deleted is True
    assert await storage.get("q-1") is None
    assert storage.is_deleted("q-1") is True

    # Приходит новый снимок с этой же цитатой
    raw_json = '{"quotes":[\n{"id": "q-1", "author": "Автор", "text": "Текст"}\n]}'
    snapshot_data = raw_json.encode("utf-8")
    imported, dropped = await storage.import_snapshot_stream(_make_stream(snapshot_data))

    assert imported == 1
    assert dropped == 0
    # После снимка удаление сброшено
    assert storage.is_deleted("q-1") is False


@pytest.mark.asyncio
async def test_storage_import_snapshot_dropped_count() -> None:
    """Проверяет расчет dropped при изменении состава снимка."""
    storage = MemoryQuoteStorage()

    # Первый снимок: q-1, q-2
    snap1 = (
        b'{"quotes":[\n{"id": "q-1", "author": "A", "text": "T"},\n'
        b'{"id": "q-2", "author": "B", "text": "T"}\n]}'
    )
    imp1, drop1 = await storage.import_snapshot_stream(_make_stream(snap1))
    assert imp1 == 2
    assert drop1 == 0

    # Второй снимок: q-2, q-3 (q-1 удалена из каталога)
    snap2 = (
        b'{"quotes":[\n{"id": "q-2", "author": "B", "text": "T"},\n'
        b'{"id": "q-3", "author": "C", "text": "T"}\n]}'
    )
    imp2, drop2 = await storage.import_snapshot_stream(_make_stream(snap2))
    assert imp2 == 2
    assert drop2 == 1  # q-1 покинула каталог
