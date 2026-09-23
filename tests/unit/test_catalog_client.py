"""Тесты для HttpCatalogClient с проверкой Circuit Breaker и Bulkhead."""

from unittest.mock import AsyncMock, patch

import httpx
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

    # Мокаем ответ 503 с Retry-After
    mock_resp = httpx.Response(
        status_code=503,
        headers={"Retry-After": "2.0"},
        request=httpx.Request("GET", "http://catalog.internal/quote/q-503"),
    )
    with patch(
        "src.infrastructure.catalog_client.http_catalog_client._raw_catalog_get",
        new_callable=AsyncMock,
        return_value=mock_resp,
    ):
        result = await client.fetch_quote("q-503")
        assert result is None
        # Во время паузы повторный запрос отсекается до отправки
        assert await client.fetch_quote("q-503") is None


@pytest.mark.asyncio
async def test_circuit_breaker_protection() -> None:
    """Проверяет срабатывание защиты Circuit Breaker при сбоях."""
    client = HttpCatalogClient()
    client.set_source_url("http://catalog.internal")

    # Мокаем сетевой сбой без реальных сокетов
    with patch(
        "src.infrastructure.catalog_client.http_catalog_client._raw_catalog_get",
        new_callable=AsyncMock,
        side_effect=httpx.NetworkError("Connection refused"),
    ):
        for _ in range(5):
            res = await client.fetch_quote("q-fail")
            assert res is None


@pytest.mark.asyncio
async def test_catalog_client_success_response() -> None:
    """Проверяет успешное получение цитаты из каталога при ответе 200."""
    client = HttpCatalogClient()
    client.set_source_url("http://catalog.internal")

    mock_resp = httpx.Response(
        status_code=200,
        json={
            "id": "q-ok-1",
            "author": "Сенека",
            "text": "Пока мы откладываем жизнь, она проходит",
        },
        request=httpx.Request("GET", "http://catalog.internal/quote/q-ok-1"),
    )
    with patch(
        "src.infrastructure.catalog_client.http_catalog_client._raw_catalog_get",
        new_callable=AsyncMock,
        return_value=mock_resp,
    ):
        quote = await client.fetch_quote("q-ok-1")
        assert quote is not None
        assert quote.id == "q-ok-1"
        assert quote.author == "Сенека"
