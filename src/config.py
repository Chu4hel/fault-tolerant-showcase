"""Конфигурация приложения и константы."""

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Настройки сервиса витрины цитатника.

    Attributes:
        app_host: Хост для запуска сервера.
        app_port: Порт для запуска сервера (по ТЗ: 8000).
        max_cache_bytes: Максимальный объем памяти под кэш цитат в байтах.
        quote_read_timeout_seconds: Таймаут ожидания ответа читателем (по ТЗ: до 3 сек).
        quote_max_age_seconds: Максимальный возраст данных у читателя (по ТЗ: 60 сек).
    """

    app_host: str = "0.0.0.0"
    app_port: int = 8000
    max_cache_bytes: int = Field(default=120 * 1024 * 1024)
    quote_read_timeout_seconds: float = 3.0
    quote_max_age_seconds: float = 60.0


settings = Settings()
