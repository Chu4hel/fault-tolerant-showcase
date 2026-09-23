"""Маршрутизатор чтения цитат читателями."""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse

from src.application.quote_service import QuoteService
from src.dependencies import get_quote_service
from src.domain.models.quote import Quote

router = APIRouter(prefix="/quotes", tags=["Quotes"])


@router.get("/{quote_id}", response_model=Quote)
async def get_quote(
    quote_id: str,
    response: Response,
    service: QuoteService = Depends(get_quote_service),
) -> JSONResponse:
    """Чтение цитаты читателем с установкой заголовка X-Source (LOCAL / CATALOG).

    Args:
        quote_id: Идентификатор запрашиваемой цитаты.
        response: Объект ответа FastAPI.
        service: Сервис витрины цитат.

    Returns:
        JSONResponse с объектом цитаты и заголовком X-Source.

    Raises:
        HTTPException: 404, если цитата не найдена.
    """
    result = await service.get_quote_for_reader(quote_id)
    if result is None:
        raise HTTPException(status_code=404, detail="not found")

    quote, source = result
    headers = {"X-Source": source.value}
    return JSONResponse(content=quote.model_dump(), headers=headers)
