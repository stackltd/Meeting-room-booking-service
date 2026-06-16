FROM python:3.12-slim as builder

# Установка системных зависимостей для сборки пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Настройки Poetry
ENV POETRY_VERSION=2.0.1 \
    POETRY_HOME="/root/.local" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Скачивание установщика poetry, запуск его через python
RUN curl -sSL https://install.python-poetry.org | python3 -

# Добавление пути в PATH для текущего этапа сборки
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Копирование файлов poetry
COPY pyproject.toml poetry.lock* ./

# установка только внешних библиотеки(--no-root), игнорирование приложений из dev (--only main)
RUN /root/.local/bin/poetry lock && \
    /root/.local/bin/poetry install --no-root --only main

# Финальный контейнер
FROM python:3.12-slim

# Установка минимального набора для работы PostgreSQL (libpq5) и команды nc (netcat-openbsd) для скрипта entrypoint.sh
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование установленных библиотеки из builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# делает скрипт запуска исполняемым
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]