"""Маршрутизатор импорта полного снимка каталога."""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from src.application.quote_service import QuoteService
from src.dependencies import get_quote_service

router = APIRouter(tags=["Import"])


class ImportResponse(BaseModel):
    """Модель ответа на импорт снимка каталога."""

    imported: int
    dropped: int


@router.post("/import", response_model=ImportResponse)
async def import_snapshot(
    request: Request,
    service: QuoteService = Depends(get_quote_service),
) -> ImportResponse:
    """Прием полного снимка каталога через потоковую обработку тела.

    Args:
        request: HTTP-запрос FastAPI с потоком данных.
        service: Сервис витрины цитат.

    Returns:
        Сводка импорта ImportResponse с количеством imported и dropped.

    Raises:
        HTTPException: 400, если формат снимка некорректен.
    """
    try:
        imported, dropped = await service.import_snapshot(request.stream())
        return ImportResponse(imported=imported, dropped=dropped)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err
