"""Пакет интерфейсов доменного слоя."""

from src.domain.interfaces.catalog_client import ICatalogClient
from src.domain.interfaces.quote_storage import IQuoteStorage

__all__ = [
    "ICatalogClient",
    "IQuoteStorage",
]
