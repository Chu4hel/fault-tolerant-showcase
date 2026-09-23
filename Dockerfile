FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Ограничения окружения и оптимизация Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Установка uv для быстрой установки зависимостей
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копирование файлов зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей проекта без dev-пакетов
RUN uv sync --frozen --no-dev --no-install-project

# Копирование исходного кода
COPY src/ ./src/

# Открытие порта 8000 согласно ТЗ
EXPOSE 8000

# Запуск сервиса на порту 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
