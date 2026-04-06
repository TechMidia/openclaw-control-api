PYTHON ?= python3
APP_PORT ?= 8088

.PHONY: install run migrate seed test up down check-health check-ingest check-dashboard

install:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	. .venv/bin/activate && PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port $(APP_PORT)

migrate:
	. .venv/bin/activate && PYTHONPATH=. alembic upgrade head

seed:
	. .venv/bin/activate && PYTHONPATH=. python scripts/seed.py

test:
	. .venv/bin/activate && PYTHONPATH=. pytest -q

up:
	docker compose up -d --build

down:
	docker compose down

check-health:
	./scripts/test_health.sh

check-ingest:
	./scripts/test_ingest.sh

check-dashboard:
	./scripts/test_dashboard.sh
