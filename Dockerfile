# Используем официальный образ Python с указанием точной версии
FROM python:3.13.3-slim

ENV POETRY_VERSION=2.1.3
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get purge -y curl && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app/app

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false \
 && poetry install --no-root --no-interaction --no-ansi

COPY . /app/
