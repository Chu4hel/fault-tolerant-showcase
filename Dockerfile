FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Ограничения окружения и оптимизация Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

# Установка uv для детерминированной сборки
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копирование спецификаций зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей проекта в виртуальное окружение без dev-пакетов
RUN uv sync --frozen --no-dev --no-install-project

# Копирование конфигурации и исходного кода
COPY config.yml ./
COPY src/ ./src/

# Открытие порта 8000 согласно ТЗ
EXPOSE 8000

# Запуск службы через прямой бинарник uvicorn из .venv (не требует интернета в рантайме)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
