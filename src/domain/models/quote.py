"""Доменные модели для цитат и источников каталога."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class QuoteSource(StrEnum):
    """Источник происхождения отданной цитаты."""

    LOCAL = "LOCAL"
    CATALOG = "CATALOG"


class Quote(BaseModel):
    """Модель цитаты.

    Attributes:
        id: Уникальный идентификатор цитаты.
        author: Автор цитаты.
        text: Текст цитаты.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    author: str
    text: str


class QuoteUpsertPayload(BaseModel):
    """Полезная нагрузка для добавления или изменения цитаты через витрину.

    Attributes:
        author: Имя автора (от 1 до 200 знаков).
        text: Текст цитаты (от 1 до 16384 знаков).
    """

    author: str = Field(..., min_length=1, max_length=200)
    text: str = Field(..., min_length=1, max_length=16384)


class SourceConfigPayload(BaseModel):
    """Полезная нагрузка для задания адреса каталога.

    Attributes:
        url: URL-адрес каталога.
    """

    url: str
