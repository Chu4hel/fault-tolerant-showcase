"""Конфигурация приложения и константы."""

from chutils import get_config
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
    max_cache_bytes: int = Field(default=64 * 1024 * 1024)
    quote_read_timeout_seconds: float = 3.0
    quote_max_age_seconds: float = 60.0


def load_settings() -> Settings:
    """Загружает настройки из config.yml через провайдер chutils с валидацией Pydantic.

    Returns:
        Экземпляр модели Settings.
    """
    try:
        loaded = get_config(model=Settings)
        if isinstance(loaded, Settings):
            return loaded
        return Settings.model_validate(loaded)
    except Exception:
        return Settings()


settings: Settings = load_settings()
"""Глобальный объект конфигурации приложения."""
