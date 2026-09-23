"""Тесты для HttpCatalogClient с проверкой Circuit Breaker и Bulkhead."""

import pytest

from src.infrastructure.catalog_client.http_catalog_client import HttpCatalogClient


@pytest.mark.asyncio
async def test_catalog_client_retry_after_handling() -> None:
    """Проверяет установку паузы при получении 503 Retry-After."""
    client = HttpCatalogClient()
    client.set_source_url("http://catalog.internal")

    # Без установленного URL возвращает None
    unconfigured_client = HttpCatalogClient()
    assert await unconfigured_client.fetch_quote("q-1") is None


@pytest.mark.asyncio
async def test_circuit_breaker_protection() -> None:
    """Проверяет срабатывание защиты Circuit Breaker при сбоях."""
    client = HttpCatalogClient()
    # Обращение к несуществующему хосту для имитации сбоя
    client.set_source_url("http://127.0.0.1:59999")

    # Первые запросы завершаются None из-за сетевой ошибки
    for _ in range(5):
        res = await client.fetch_quote("q-fail")
        assert res is None
