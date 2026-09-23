"""Реализация in-memory хранилища цитат с контролем потребления памяти."""

import time
from collections import OrderedDict
from collections.abc import AsyncIterator

import orjson

from src.domain.interfaces.quote_storage import IQuoteStorage
from src.domain.models.quote import Quote
from src.domain.models.stats import ShowcaseStats


class MemoryQuoteStorage(IQuoteStorage):
    """In-memory реализация хранилища цитат с LRU-кэшем и компактным индексом каталога."""

    def __init__(
        self,
        max_bytes: int = 64 * 1024 * 1024,
        max_age_seconds: float = 60.0,
    ) -> None:
        """Инициализирует in-memory хранилище.

        Args:
            max_bytes: Максимальный лимит байтов под локальный кэш цитат.
            max_age_seconds: Максимальный возраст актуальности кэшированной цитаты (60 с).
        """
        self._max_bytes = max_bytes
        self._max_age_seconds = max_age_seconds

        # Кэш горячих цитат: quote_id -> (quote, cached_at, byte_size)
        self._cache: OrderedDict[str, tuple[Quote, float, int]] = OrderedDict()
        self._current_cache_bytes: int = 0

        # Множество известных ID каталога для компактного отслеживания
        self._known_catalog_ids: set[str] = set()

        # Множество ID, скрытых редакцией (до следующего снимка)
        self._deleted_ids: set[str] = set()

        # Флаг, был ли хотя бы один снимок импортирован
        self._has_imported_snapshot: bool = False

        # Счетчики статистики (только растут с момента запуска)
        self._served_local: int = 0
        self._served_from_catalog: int = 0
        self._catalog_reads: int = 0
        self._evictions: int = 0

    @property
    def known_catalog_ids(self) -> set[str]:
        """Возвращает множество известных ID цитат в каталоге.

        Returns:
            Множество строк с идентификаторами цитат.
        """
        return self._known_catalog_ids

    @property
    def deleted_ids(self) -> set[str]:
        """Возвращает множество удаленных редакцией ID цитат.

        Returns:
            Множество строк с идентификаторами цитат.
        """
        return self._deleted_ids

    def is_deleted(self, quote_id: str) -> bool:
        """Проверяет, помечена ли цитата как удаленная редакцией.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            True, если цитата снята с публикации до следующего снимка.
        """
        return quote_id in self._deleted_ids

    def increment_served_local(self) -> None:
        """Увеличивает счетчик ответов, отданных локально."""
        self._served_local += 1

    def increment_served_from_catalog(self) -> None:
        """Увеличивает счетчик ответов, потребовавших обращения в каталог."""
        self._served_from_catalog += 1

    def increment_catalog_reads(self) -> None:
        """Увеличивает счетчик запросов, отправленных в каталог."""
        self._catalog_reads += 1

    def get_cached_with_age(self, quote_id: str) -> tuple[Quote, float] | None:
        """Получить цитату из локального кэша и ее возраст в секундах.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Кортеж (Quote, age_seconds) или None, если запись отсутствует.
        """
        if quote_id in self._deleted_ids or quote_id not in self._cache:
            return None

        quote, cached_at, _ = self._cache[quote_id]
        age = time.monotonic() - cached_at
        self._cache.move_to_end(quote_id)
        return quote, age

    async def get(self, quote_id: str) -> Quote | None:
        """Получить цитату из локального кэша, если она не старше допустимого возраста.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Объект Quote или None, если запись отсутствует или устарела.
        """
        entry = self.get_cached_with_age(quote_id)
        if entry is None:
            return None

        quote, age = entry
        if age > self._max_age_seconds:
            return None

        return quote

    async def put(self, quote: Quote) -> None:
        """Сохранить или обновить цитату в локальном кэше с контролем объема памяти.

        Args:
            quote: Объект цитаты для сохранения.
        """
        quote_id = quote.id

        # Если цитата была в удаленных, редакция ее актуализировала
        self._deleted_ids.discard(quote_id)
        self._known_catalog_ids.add(quote_id)

        # Вычисляем точный размер цитаты в байтах
        serialized = orjson.dumps(quote.model_dump())
        quote_size = len(serialized)

        # Если цитата уже есть в кэше, корректируем размер
        if quote_id in self._cache:
            _, _, old_size = self._cache[quote_id]
            self._current_cache_bytes -= old_size
            del self._cache[quote_id]

        # Если размер кэша превышает лимит, вытесняем старые записи (LRU)
        while self._current_cache_bytes + quote_size > self._max_bytes and len(self._cache) > 0:
            _, (_, _, evicted_size) = self._cache.popitem(last=False)
            self._current_cache_bytes -= evicted_size
            self._evictions += 1

        self._cache[quote_id] = (quote, time.monotonic(), quote_size)
        self._current_cache_bytes += quote_size

    async def delete(self, quote_id: str) -> bool:
        """Удалить цитату из локального кэша и пометить как снятую с публикации.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            True, если цитата присутствовала в каталоге или кэше, иначе False.
        """
        is_known = quote_id in self._known_catalog_ids or quote_id in self._cache
        if not is_known:
            return False

        # Удаляем из кэша, если есть
        if quote_id in self._cache:
            _, _, size = self._cache.pop(quote_id)
            self._current_cache_bytes -= size

        # Помечаем как снятую с публикации
        self._deleted_ids.add(quote_id)
        self._known_catalog_ids.discard(quote_id)
        return True

    async def import_snapshot_stream(self, stream: AsyncIterator[bytes]) -> tuple[int, int]:
        """Потоковая обработка и импорт полного снимка каталога.

        Гарантия формата снимка:
        {"quotes":[ на первой строке, затем по одной записи в строке,
        записи разделены запятой в конце строки, ]} на последней.

        Обязательные поля записи: id, author, text.

        Args:
            stream: Поток байт входного снимка.

        Returns:
            Кортеж (imported_count, dropped_count).

        Raises:
            ValueError: При некорректном формате данных снимка.
        """
        new_ids: set[str] = set()
        buffer = bytearray()
        first_line_checked = False
        now = time.monotonic()

        async for chunk in stream:
            buffer.extend(chunk)
            while True:
                newline_pos = buffer.find(b"\n")
                if newline_pos == -1:
                    break

                line = bytes(buffer[:newline_pos]).strip()
                del buffer[: newline_pos + 1]

                if not line:
                    continue

                if not first_line_checked:
                    if not line.startswith(b'{"quotes":['):
                        raise ValueError("Некорректная заглавная строка снимка каталога")
                    first_line_checked = True
                    line = line[len(b'{"quotes":[') :].strip()
                    if not line:
                        continue

                # Проверка завершающей строки снимка
                if line == b"]}":
                    continue

                # Удаление запятой в конце строки, если она есть
                if line.endswith(b","):
                    line = line[:-1].rstrip()

                if line == b"]}" or not line:
                    continue

                try:
                    record = orjson.loads(line)
                    if (
                        isinstance(record, dict)
                        and "id" in record
                        and "author" in record
                        and "text" in record
                    ):
                        qid = str(record["id"])
                        new_ids.add(qid)

                        # Кэшируем запись, если есть свободное место в лимите памяти
                        line_len = len(line)
                        if (
                            self._current_cache_bytes + line_len <= self._max_bytes
                            or qid in self._cache
                        ):
                            if qid in self._cache:
                                _, _, old_sz = self._cache[qid]
                                self._current_cache_bytes -= old_sz

                            quote = Quote.model_validate(record)
                            self._cache[qid] = (quote, now, line_len)
                            self._current_cache_bytes += line_len
                    else:
                        raise ValueError(
                            "Запись снимка не содержит обязательных полей id/author/text"
                        )
                except Exception as err:
                    raise ValueError(f"Ошибка парсинга строки снимка: {err}") from err

        # Обработка оставшегося хвоста буфера
        tail = bytes(buffer).strip()
        if tail and tail != b"]}":
            if tail.endswith(b","):
                tail = tail[:-1].rstrip()
            if tail != b"]}" and tail:
                try:
                    record = orjson.loads(tail)
                    if (
                        isinstance(record, dict)
                        and "id" in record
                        and "author" in record
                        and "text" in record
                    ):
                        qid = str(record["id"])
                        new_ids.add(qid)
                        line_len = len(tail)
                        if (
                            self._current_cache_bytes + line_len <= self._max_bytes
                            or qid in self._cache
                        ):
                            if qid in self._cache:
                                _, _, old_sz = self._cache[qid]
                                self._current_cache_bytes -= old_sz
                            quote = Quote.model_validate(record)
                            self._cache[qid] = (quote, now, line_len)
                            self._current_cache_bytes += line_len
                    else:
                        raise ValueError(
                            "Запись снимка не содержит обязательных полей id/author/text"
                        )
                except Exception as err:
                    raise ValueError(f"Ошибка парсинга хвоста снимка: {err}") from err

        if not first_line_checked:
            raise ValueError("Пустой или поврежденный снимок")

        imported_count = len(new_ids)
        if self._has_imported_snapshot:
            # dropped: сколько цитат покинуло каталог по сравнению с прошлым снимком
            dropped_count = len(self._known_catalog_ids - new_ids)
        else:
            dropped_count = 0
            self._has_imported_snapshot = True

        # Обновляем состав каталога
        self._known_catalog_ids = new_ids
        # Сброс удаленных записей: снятая цитата не отдается до следующего снимка
        self._deleted_ids.clear()

        # Удаляем из кэша цитаты, которые покинули каталог (без увеличения evictions)
        cached_ids = list(self._cache.keys())
        for cid in cached_ids:
            if cid not in new_ids:
                _, _, sz = self._cache.pop(cid)
                self._current_cache_bytes -= sz

        return imported_count, dropped_count

    async def get_stats(self) -> ShowcaseStats:
        """Получить текущую сводку статистики.

        Returns:
            Экземпляр ShowcaseStats с актуальными метриками.
        """
        return ShowcaseStats(
            served_local=self._served_local,
            served_from_catalog=self._served_from_catalog,
            catalog_reads=self._catalog_reads,
            evictions=self._evictions,
            local=len(self._cache),
            bytes=self._current_cache_bytes,
            catalog=len(self._known_catalog_ids),
        )
