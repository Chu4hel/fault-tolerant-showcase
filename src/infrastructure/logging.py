"""Модуль централизованного логирования на базе chutils."""

from chutils import setup_logger

logger = setup_logger(
    name="quote_showcase",
    no_file=True,
)
"""Централизованный структурированный логгер приложения."""
