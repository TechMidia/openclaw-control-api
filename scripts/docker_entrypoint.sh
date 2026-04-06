#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=/app

echo "[entrypoint] waiting db..."
python - <<'PY'
import os
import time
import psycopg2
from urllib.parse import urlparse

url = os.environ["DATABASE_URL"].replace("+psycopg2", "")
parsed = urlparse(url)
for _ in range(40):
    try:
        conn = psycopg2.connect(
            dbname=parsed.path.strip("/"),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
        )
        conn.close()
        print("database ready")
        break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit("database not ready")
PY

alembic upgrade head
python scripts/seed.py

exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT:-8088}"

