"""Доменные модели для эксплуатационной статистики."""

from pydantic import BaseModel


class ShowcaseStats(BaseModel):
    """Эксплуатационная сводка сервиса.

    Attributes:
        served_local: Количество ответов, отданных без обращения в каталог.
        served_from_catalog: Количество ответов, потребовавших обращения в каталог.
        catalog_reads: Количество запросов, отправленных в каталог.
        evictions: Количество записей, удаленных при вытеснении из кэша.
        local: Количество записей, удерживаемых в локальном кэше сейчас.
        bytes: Размер памяти в байтах, занимаемый локальными записями сейчас.
        catalog: Количество цитат, известных витрине на данный момент.
    """

    served_local: int = 0
    served_from_catalog: int = 0
    catalog_reads: int = 0
    evictions: int = 0
    local: int = 0
    bytes: int = 0
    catalog: int = 0
