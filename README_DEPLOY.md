# README_DEPLOY (Contabo Ubuntu)

## 1. Pré-requisitos na VPS
```bash
sudo apt update && sudo apt install -y ca-certificates curl gnupg
```

Instalar Docker + Compose plugin (oficial):
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

## 2. Subir API
```bash
cd /opt
sudo git clone <repo-url> openclaw-control-api
cd openclaw-control-api
cp .env.example .env
# editar .env com tokens/senhas reais

docker compose up -d --build
```

## 3. Verificações
```bash
docker compose ps
curl -sS http://127.0.0.1:${API_PORT:-8000}/health
curl -sS http://127.0.0.1:${NGINX_PORT:-80}/health
```

## 4. Hardening mínimo recomendado
- `INGEST_API_TOKEN` forte (>= 32 chars)
- `JWT_SECRET_KEY` forte (>= 32 chars)
- Firewall liberando só portas necessárias (`80/443`)
- Se usar domínio público, colocar TLS (Nginx + certbot)
- Backup periódico do volume do Postgres

## 5. Atualização
```bash
cd /opt/openclaw-control-api
git pull
docker compose up -d --build
```

## 6. Rollback rápido
```bash
docker image ls | head
# escolher imagem anterior
# ajustar compose para tag desejada e subir novamente
```
