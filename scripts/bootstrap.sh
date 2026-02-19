#!/usr/bin/env bash
set -euo pipefail

cp -n .env.example .env || true
echo "[Aletheia] Bootstrapping local infra..."
docker compose -f infra/docker/docker-compose.yml up -d
echo "[Aletheia] Infra started."
