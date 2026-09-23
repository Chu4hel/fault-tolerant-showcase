"""Пакет маршрутизаторов API."""

from src.presentation.api.routers.catalog import router as catalog_router
from src.presentation.api.routers.health import router as health_router
from src.presentation.api.routers.import_snapshot import (
    router as import_snapshot_router,
)
from src.presentation.api.routers.quotes import router as quotes_router
from src.presentation.api.routers.stats import router as stats_router

__all__ = [
    "catalog_router",
    "health_router",
    "import_snapshot_router",
    "quotes_router",
    "stats_router",
]
