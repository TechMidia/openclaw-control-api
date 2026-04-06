# openclaw-control-api

Backend da VPS para receber ingestão do `openclaw-sync-bridge`, persistir no PostgreSQL e expor endpoints para o dashboard.

## Stack
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL
- Redis opcional
- Nginx
- Docker / Docker Compose
- Auth por token de ingestão e JWT para dashboard

## Fluxo
`Mac Mini (Bridge) -> /ingest/* -> PostgreSQL -> /dashboard/* -> Front v0`

## Endpoints

### Entrada (Bridge -> VPS)
- `POST /ingest/full`
- `POST /ingest/operations`
- `POST /ingest/projects`
- `POST /ingest/financial`
- `POST /ingest/governance`
- `POST /ingest/consumption`

Auth ingestão:
- `X-Ingest-Token: <INGEST_API_TOKEN>`
- ou `Authorization: Bearer <INGEST_API_TOKEN>`

### Saída (Dashboard)
- `GET /dashboard/summary`
- `GET /dashboard/command-center`
- `GET /dashboard/inbox`
- `GET /dashboard/alerts`
- `GET /dashboard/decisions`
- `GET /operations/today`
- `GET /finance/summary`
- `GET /projects/techmidia`
- `GET /projects/doncarmo`
- `GET /projects/personal`
- `GET /governance/agents`
- `GET /governance/heartbeats`
- `GET /governance/consumption`
- `GET /history/events`

Auth dashboard:
- `POST /auth/login`
- `Authorization: Bearer <jwt>` nos endpoints protegidos.

### Saúde
- `GET /health`

## Configuração
```bash
cp .env.example .env
```

Variáveis críticas:
- `DATABASE_URL`
- `INGEST_API_TOKEN`
- `JWT_SECRET_KEY`
- `ADMIN_DEFAULT_USERNAME`
- `ADMIN_DEFAULT_PASSWORD`
- `ALLOWED_ORIGINS`

## Rodar sem Docker
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. alembic upgrade head
PYTHONPATH=. python scripts/seed.py
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8088
```

## Rodar com Docker
```bash
docker compose up -d --build
```

## Testes rápidos (scripts)
```bash
./scripts/test_health.sh
INGEST_API_TOKEN=<token> ./scripts/test_ingest.sh
ADMIN_DEFAULT_USERNAME=admin ADMIN_DEFAULT_PASSWORD=<senha> ./scripts/test_dashboard.sh
```

## Logs
- `logs/api.log`
- `logs/ingest.log`
- `logs/errors.log`

## Documentação adicional
- `api_contract.md`
- `README_VPS_API.md`
- `README_DEPLOY.md`
