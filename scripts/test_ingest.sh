#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

BASE_URL="${BASE_URL:-http://127.0.0.1:${APP_PORT:-8000}}"
INGEST_TOKEN="${INGEST_API_TOKEN:-}"

if [[ -z "${INGEST_TOKEN}" ]]; then
  echo "INGEST_API_TOKEN não definido no ambiente."
  exit 1
fi

curl -sS -X POST "${BASE_URL}/ingest/full" \
  -H "X-Ingest-Token: ${INGEST_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "bridge": "manual-test",
    "block": "full",
    "source": "mac-mini-test",
    "data": {
      "operations_day": {
        "date": "2026-04-06",
        "summary": "manual ingest",
        "tasks": [
          {"title": "validar ingest", "status": "pending", "priority": "high"}
        ]
      },
      "projects_status": {
        "techmidia": {"summary": "ok"},
        "doncarmo": {"summary": "ok"},
        "personal": {"summary": "ok"}
      },
      "financial_summary": {
        "cash_position": "R$ 100",
        "receivables": "R$ 50",
        "payables": "R$ 10"
      },
      "governance_state": {
        "policies": ["auditar ingest"]
      },
      "consumption_metrics": {
        "tokens": "1000"
      }
    }
  }' | python3 -m json.tool
