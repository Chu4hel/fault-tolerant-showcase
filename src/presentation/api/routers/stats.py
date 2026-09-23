"""Маршрутизатор эксплуатационной сводки."""

from fastapi import APIRouter

from src.domain.models.stats import ShowcaseStats

router = APIRouter(tags=["Stats"])


@router.get("/stats", response_model=ShowcaseStats)
async def get_stats() -> ShowcaseStats:
    """Получение эксплуатационной статистики службы."""
    raise NotImplementedError
