"""Маршрутизатор проверки жизнеспособности сервиса."""

from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Модель ответа ручки /health."""

    status: str = "healthy"


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def check_health() -> HealthResponse:
    """Возвращает статус здоровья сервиса.

    Должен отвечать 200 сразу после старта процесса и все время работы.

    Returns:
        Объект HealthResponse со статусом "healthy".
    """
    return HealthResponse()
