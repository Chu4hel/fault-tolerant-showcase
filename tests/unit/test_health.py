"""Тест эндпоинта проверки жизнеспособности /health."""

from fastapi.testclient import TestClient

from src.main import app


def test_health_endpoint() -> None:
    """Проверяет, что эндпоинт /health сразу после запуска возвращает 200 и статус healthy."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
