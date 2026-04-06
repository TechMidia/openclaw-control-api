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

BASE_URL="${BASE_URL:-http://127.0.0.1:${APP_PORT:-8088}}"
ADMIN_USER="${ADMIN_DEFAULT_USERNAME:-admin}"
ADMIN_PASSWORD="${ADMIN_DEFAULT_PASSWORD:-change-me-now}"

JWT="$(curl -sS -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${ADMIN_USER}\",\"password\":\"${ADMIN_PASSWORD}\"}" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("access_token",""))')"

if [[ -z "${JWT}" ]]; then
  echo "Falha ao obter JWT de /auth/login"
  exit 1
fi

curl -sS "${BASE_URL}/dashboard/summary" -H "Authorization: Bearer ${JWT}" | python3 -m json.tool
