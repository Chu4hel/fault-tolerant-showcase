"""Сервис оркестрации бизнес-логики витрины цитат."""

from collections.abc import AsyncIterator

from src.domain.interfaces.catalog_client import ICatalogClient
from src.domain.interfaces.quote_storage import IQuoteStorage
from src.domain.models.quote import Quote, QuoteSource, QuoteUpsertPayload
from src.domain.models.stats import ShowcaseStats


class QuoteService:
    """Сервис для координации работы с кэшем, каталогом и метриками."""

    def __init__(
        self,
        storage: IQuoteStorage,
        catalog_client: ICatalogClient,
        max_age_seconds: float = 60.0,
    ) -> None:
        """Инициализирует сервис витрины цитат.

        Args:
            storage: Реализация хранилища цитат (Dependency Inversion).
            catalog_client: Реализация клиента каталога (Dependency Inversion).
            max_age_seconds: Максимальный возраст данных у читателя (60 с по ТЗ).
        """
        self._storage = storage
        self._catalog_client = catalog_client
        self._max_age_seconds = max_age_seconds

    def set_catalog_source(self, url: str) -> str:
        """Задает или обновляет адрес каталога.

        Args:
            url: URL источника каталога.

        Returns:
            Установленный URL.
        """
        self._catalog_client.set_source_url(url)
        return url

    def get_catalog_source(self) -> str | None:
        """Возвращает текущий адрес каталога.

        Returns:
            Строка URL или None.
        """
        return self._catalog_client.get_source_url()

    async def get_quote_for_reader(self, quote_id: str) -> tuple[Quote, QuoteSource] | None:
        """Получить цитату для читателя с фиксацией источника (LOCAL / CATALOG).

        Если цитаты нет ни у витрины, ни в каталоге — возвращает None.
        Что цитаты нет, витрина не запоминает: редакция заводит их постоянно,
        и читатель, пришедший по свежей ссылке, обязан увидеть цитату сразу.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            Кортеж (Quote, QuoteSource) или None, если цитата не найдена.
        """
        # 1. Если цитата снята редакцией через DELETE — она скрыта до нового снимка
        if self._storage.is_deleted(quote_id):
            return None

        # 2. Проверяем наличие в локальном кэше
        cached_entry = self._storage.get_cached_with_age(quote_id)

        if cached_entry is not None:
            cached_quote, age = cached_entry
            # Если запись свежая (младше 60 секунд) — отдаем локально без каталога
            if age <= self._max_age_seconds:
                self._storage.increment_served_local()
                return cached_quote, QuoteSource.LOCAL

        # 3. Запись отсутствует или старше 60 секунд — обращаемся в каталог
        self._storage.increment_catalog_reads()
        catalog_quote = await self._catalog_client.fetch_quote(quote_id)

        if catalog_quote is not None:
            # Каталог вернул актуальную запись — обновляем локальный кэш
            await self._storage.put(catalog_quote)
            self._storage.increment_served_from_catalog()
            return catalog_quote, QuoteSource.CATALOG

        # 4. Если каталог недоступен, но у нас есть сохраненная локальная копия
        if cached_entry is not None:
            cached_quote, _ = cached_entry
            self._storage.increment_served_local()
            return cached_quote, QuoteSource.LOCAL

        return None

    async def upsert_quote(self, quote_id: str, payload: QuoteUpsertPayload) -> Quote:
        """Добавить или обновить цитату редакцией.

        Запись актуальна по определению: читателю она отдается сразу после ответа
        и перечитывать ее из каталога не нужно.

        Args:
            quote_id: Идентификатор цитаты.
            payload: Данные автора и текста цитаты от редакции.

        Returns:
            Созданный или обновленный объект Quote.
        """
        quote = Quote(
            id=quote_id,
            author=payload.author,
            text=payload.text,
        )
        await self._storage.put(quote)
        return quote

    async def delete_quote(self, quote_id: str) -> bool:
        """Снять цитату с публикации редакцией через витрину.

        Снятая цитата читателям не отдается, даже если в каталоге она еще есть,
        до следующего снимка.

        Args:
            quote_id: Идентификатор цитаты.

        Returns:
            True, если цитата была найдена и снята с публикации, иначе False.
        """
        return await self._storage.delete(quote_id)

    async def import_snapshot(self, stream: AsyncIterator[bytes]) -> tuple[int, int]:
        """Принять и обработать полный снимок каталога.

        Args:
            stream: Поток байт входного JSON-снимка.

        Returns:
            Кортеж (imported_count, dropped_count).
        """
        return await self._storage.import_snapshot_stream(stream)

    async def get_stats(self) -> ShowcaseStats:
        """Получить актуальную статистику витрины.

        Returns:
            Сводка статистики ShowcaseStats.
        """
        return await self._storage.get_stats()
