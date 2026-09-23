"""Маршрутизатор операций взаимодействия с каталогом и редакцией."""

from fastapi import APIRouter
from pydantic import BaseModel

from src.domain.models.quote import Quote, QuoteUpsertPayload, SourceConfigPayload

router = APIRouter(prefix="/catalog", tags=["Catalog"])


class SourceResponse(BaseModel):
    """Модель ответа на установку адреса каталога."""

    source: str


class DeleteResponse(BaseModel):
    """Модель ответа на удаление цитаты."""

    deleted: bool = True


@router.post("/source", response_model=SourceResponse)
async def set_source(payload: SourceConfigPayload) -> SourceResponse:
    """Установка или обновление адреса каталога.

    Args:
        payload: Модель с адресом каталога.

    Returns:
        Объект SourceResponse с подтвержденным адресом источника.
    """
    raise NotImplementedError


@router.put("/{quote_id}", response_model=Quote)
async def upsert_quote(quote_id: str, payload: QuoteUpsertPayload) -> Quote:
    """Добавление или замена цитаты редакцией через витрину.

    Args:
        quote_id: Идентификатор цитаты.
        payload: Данные автора и текста цитаты.

    Returns:
        Созданная или обновленная цитата Quote.
    """
    raise NotImplementedError


@router.delete("/{quote_id}", response_model=DeleteResponse)
async def delete_quote(quote_id: str) -> DeleteResponse:
    """Снятие цитаты с публикации редакцией через витрину.

    Args:
        quote_id: Идентификатор удаляемой цитаты.

    Returns:
        Подтверждение удаления DeleteResponse.
    """
    raise NotImplementedError
