"""Маршрутизатор импорта полного снимка каталога."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(tags=["Import"])


class ImportResponse(BaseModel):
    """Модель ответа на импорт снимка каталога."""

    imported: int
    dropped: int


@router.post("/import", response_model=ImportResponse)
async def import_snapshot(request: Request) -> ImportResponse:
    """Прием полного снимка каталога через потоковую обработку тела.

    Args:
        request: HTTP-запрос FastAPI с потоком данных.

    Returns:
        Сводка импорта ImportResponse с количеством imported и dropped.
    """
    raise NotImplementedError
