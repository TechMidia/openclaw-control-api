# README_VPS_API

## 1. Objetivo
`openclaw-control-api` é o backend receptor no servidor (VPS), com ingestão autenticada e consulta consolidada para o dashboard.

## 2. Componentes
- API FastAPI (`app/main.py`)
- Persistência PostgreSQL
- Migrações Alembic (`migrations/`)
- Seed inicial (`scripts/seed.py`)
- Reverse proxy Nginx (`nginx/nginx.conf`)

## 3. Tabelas principais
- `users`, `roles`, `sessions_audit`
- `projects`, `operations_snapshots`, `tasks`
- `financial_snapshots`, `receivables`, `payables`
- `alerts`, `decisions`, `agents`, `heartbeats`
- `governance_snapshots`, `consumption_snapshots`
- `ingest_logs`

## 4. Auth
### Ingestão
Header:
- `X-Ingest-Token: <INGEST_API_TOKEN>`
- ou `Authorization: Bearer <INGEST_API_TOKEN>`

### Dashboard
- Login em `POST /auth/login`
- Uso de JWT no header `Authorization: Bearer <jwt>`

## 5. Comandos úteis
```bash
# build + up
docker compose up -d --build

# status
docker compose ps

# logs
docker compose logs -f api

# migrate manual
source .venv/bin/activate
PYTHONPATH=. alembic upgrade head

# seed manual
PYTHONPATH=. python scripts/seed.py
```

## 6. Validação mínima
```bash
curl http://127.0.0.1:8000/health
```

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"<senha>"}'
```

```bash
curl -X POST http://127.0.0.1:8000/ingest/full \
  -H 'X-Ingest-Token: <INGEST_API_TOKEN>' \
  -H 'Content-Type: application/json' \
  -d '{"data":{"operations_day":{"date":"2026-04-06","summary":"ok"}}}'
```
