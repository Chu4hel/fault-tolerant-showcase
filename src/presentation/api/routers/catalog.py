"""Маршрутизатор операций взаимодействия с каталогом и редакцией."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.application.quote_service import QuoteService
from src.dependencies import get_quote_service
from src.domain.models.quote import Quote, QuoteUpsertPayload, SourceConfigPayload

router = APIRouter(prefix="/catalog", tags=["Catalog"])


class SourceResponse(BaseModel):
    """Модель ответа на установку адреса каталога."""

    source: str


class DeleteResponse(BaseModel):
    """Модель ответа на удаление цитаты."""

    deleted: bool = True


@router.post("/source", response_model=SourceResponse)
async def set_source(
    payload: SourceConfigPayload,
    service: QuoteService = Depends(get_quote_service),
) -> SourceResponse:
    """Установка или обновление адреса каталога.

    Args:
        payload: Модель с адресом каталога.
        service: Сервис витрины цитат.

    Returns:
        Объект SourceResponse с подтвержденным адресом источника.
    """
    source_url = service.set_catalog_source(payload.url)
    return SourceResponse(source=source_url)


@router.put("/{quote_id}", response_model=Quote)
async def upsert_quote(
    quote_id: str,
    payload: QuoteUpsertPayload,
    service: QuoteService = Depends(get_quote_service),
) -> Quote:
    """Добавление или замена цитаты редакцией через витрину.

    Args:
        quote_id: Идентификатор цитаты.
        payload: Данные автора и текста цитаты.
        service: Сервис витрины цитат.

    Returns:
        Созданная или обновленная цитата Quote.
    """
    return await service.upsert_quote(quote_id, payload)


@router.delete("/{quote_id}", response_model=DeleteResponse)
async def delete_quote(
    quote_id: str,
    service: QuoteService = Depends(get_quote_service),
) -> DeleteResponse:
    """Снятие цитаты с публикации редакцией через витрину.

    Args:
        quote_id: Идентификатор удаляемой цитаты.
        service: Сервис витрины цитат.

    Returns:
        Подтверждение удаления DeleteResponse.

    Raises:
        HTTPException: 404, если цитата не найдена.
    """
    deleted = await service.delete_quote(quote_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="not found")
    return DeleteResponse(deleted=True)
