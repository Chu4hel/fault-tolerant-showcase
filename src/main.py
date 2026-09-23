"""Точка входа FastAPI приложения витрины цитатника."""

from fastapi import FastAPI

from src.presentation.api.routers import (
    catalog_router,
    health_router,
    import_snapshot_router,
    quotes_router,
    stats_router,
)


def create_app() -> FastAPI:
    """Создает и настраивает экземпляр приложения FastAPI.

    Returns:
        Сконфигурированный экземпляр FastAPI.
    """
    app = FastAPI(
        title="Витрина цитатника",
        description="Высокопроизводительный in-memory сервис витрины цитат",
        version="0.1.0",
    )

    # Подключение маршрутизаторов
    app.include_router(health_router)
    app.include_router(catalog_router)
    app.include_router(import_snapshot_router)
    app.include_router(quotes_router)
    app.include_router(stats_router)

    return app


app = create_app()
