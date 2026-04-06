# API Contract — openclaw-control-api

## 1. Envelope de ingestão
Todos os endpoints `POST /ingest/*` aceitam envelope:

```json
{
  "bridge": "openclaw-sync-bridge",
  "block": "full",
  "source": "mac-mini-openclaw",
  "sent_at": "2026-04-06T20:00:00Z",
  "data": {}
}
```

Também é aceito payload direto (sem envelope); a API normaliza internamente.

## 2. Endpoints de entrada (Bridge -> VPS)
- `POST /ingest/full`
- `POST /ingest/operations`
- `POST /ingest/projects`
- `POST /ingest/financial`
- `POST /ingest/governance`
- `POST /ingest/consumption`

Auth ingestão:
- `X-Ingest-Token: <INGEST_API_TOKEN>`
- ou `Authorization: Bearer <INGEST_API_TOKEN>`

Resposta padrão:

```json
{
  "accepted": true,
  "block": "full",
  "source": "mac-mini-openclaw",
  "stored_at": "2026-04-06T20:00:00Z",
  "detail": "ok"
}
```

## 3. Endpoints de saída (Dashboard)
Todos exigem JWT:
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

## 4. Payloads para o front (v0)

### 4.1 Centro de Comando
`GET /dashboard/command-center`

```json
{
  "generated_at": "2026-04-06T20:22:24.313232Z",
  "operations": {
    "id": 1,
    "date": "2026-04-06",
    "summary": "sync test",
    "tasks": [
      {"id": 1, "title": "task 1", "status": "pending", "priority": "high"}
    ]
  },
  "finance": {
    "id": 1,
    "cash_position": "R$ 100",
    "receivables_summary": "R$ 40",
    "payables_summary": "R$ 20"
  },
  "projects": [
    {"slug": "techmidia", "name": "TechMidia", "latest_status": {"summary": "ok"}},
    {"slug": "doncarmo", "name": "DonCarmo", "latest_status": {"summary": "ok"}},
    {"slug": "personal", "name": "Vida Pessoal", "latest_status": {"summary": "ok"}}
  ],
  "top_alerts": [],
  "pending_decisions": []
}
```

### 4.2 Inbox Operacional
`GET /dashboard/inbox`

```json
{
  "generated_at": "2026-04-06T20:22:24.323455Z",
  "alerts": [],
  "decisions": [],
  "history": []
}
```

### 4.3 Operação do Dia
`GET /operations/today`

```json
{
  "id": 1,
  "date": "2026-04-06",
  "summary": "sync test",
  "payload": {},
  "tasks": [],
  "created_at": "2026-04-06T20:22:24.280535Z"
}
```

### 4.4 Financeiro
`GET /finance/summary`

```json
{
  "id": 1,
  "cash_position": "R$ 100",
  "receivables_summary": "R$ 40",
  "payables_summary": "R$ 20",
  "payload": {},
  "created_at": "2026-04-06T20:22:24.285112Z"
}
```

### 4.5 Governança
- `GET /governance/agents`
- `GET /governance/heartbeats`
- `GET /governance/consumption`

### 4.6 Histórico
`GET /history/events`

```json
[
  {
    "id": 2,
    "block": "full",
    "source_instance": "mac-mini-openclaw-dev",
    "status": "ok",
    "detail": "results=...",
    "payload_size": 13503,
    "created_at": "2026-04-06T20:22:55.438650Z"
  }
]
```

## 5. Login e JWT
`POST /auth/login`

```json
{
  "username": "admin",
  "password": "<senha>"
}
```

Resposta:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in_minutes": 1440
}
```
