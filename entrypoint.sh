#!/bin/sh

echo "Waiting for PostgreSQL..."
# ожидание, пока порт 5432 внутри контейнера базы станет доступен
while ! nc -z postgres 5432; do
  sleep 0.5
done
echo "PostgreSQL started!"

echo "Running Alembic Migrations..."
alembic upgrade head

echo "Seeding initial data..."
python init_db.py

echo "Starting Uvicorn..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8989