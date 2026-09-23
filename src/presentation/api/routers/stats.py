"""Маршрутизатор эксплуатационной сводки."""

from fastapi import APIRouter, Depends

from src.application.quote_service import QuoteService
from src.dependencies import get_quote_service
from src.domain.models.stats import ShowcaseStats

router = APIRouter(tags=["Stats"])


@router.get("/stats", response_model=ShowcaseStats)
async def get_stats(
    service: QuoteService = Depends(get_quote_service),
) -> ShowcaseStats:
    """Получение эксплуатационной статистики службы.

    Args:
        service: Сервис витрины цитат.

    Returns:
        Объект ShowcaseStats с накопленными метриками работы витрины.
    """
    return await service.get_stats()
