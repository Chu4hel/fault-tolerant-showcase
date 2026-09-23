"""Маршрутизатор чтения цитат читателями."""

from fastapi import APIRouter, Response

from src.domain.models.quote import Quote

router = APIRouter(prefix="/quotes", tags=["Quotes"])


@router.get("/{quote_id}", response_model=Quote)
async def get_quote(quote_id: str, response: Response) -> Quote:
    """Чтение цитаты читателем с заголовком X-Source (LOCAL / CATALOG)."""
    raise NotImplementedError
