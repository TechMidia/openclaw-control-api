#!/bin/sh
set -e

echo "[entrypoint] waiting db..."
python scripts/wait_db.py

echo "[entrypoint] running migrations..."
alembic upgrade head

echo "[entrypoint] running seed..."
python scripts/seed.py || true

echo "[entrypoint] starting api..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
