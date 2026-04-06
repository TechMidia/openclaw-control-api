from __future__ import annotations

import os
import time
from urllib.parse import urlparse

import psycopg2


MAX_RETRIES = 40
SLEEP_SECONDS = 2


def _normalize_db_url(raw_url: str) -> str:
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql://", 1)
    return raw_url.replace("+psycopg2", "")


def wait_for_database() -> None:
    raw_url = os.environ["DATABASE_URL"]
    parsed = urlparse(_normalize_db_url(raw_url))

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn = psycopg2.connect(
                dbname=parsed.path.lstrip("/"),
                user=parsed.username,
                password=parsed.password,
                host=parsed.hostname,
                port=parsed.port or 5432,
            )
            conn.close()
            print("database ready")
            return
        except Exception:
            print(f"database not ready yet (attempt {attempt}/{MAX_RETRIES})")
            time.sleep(SLEEP_SECONDS)

    raise SystemExit("database not ready")


if __name__ == "__main__":
    wait_for_database()
