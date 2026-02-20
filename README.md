# Aletheia

Research-grade RAG platform for large-scale book knowledge bases (10k–15k books).

## Goals
- High-recall retrieval across books and papers
- Citation-first answers (book/chapter/page)
- Scalable ingestion + hybrid search + reranking

## One-command local startup

```bash
cp .env.example .env

docker compose up -d --build
```

That single command will:
- start Postgres / Redis / OpenSearch / Qdrant / MinIO
- run DB migration (`schemas/metadata.sql`) via `migrate` service
- start `aletheia-api` and `aletheia-bridge`

## Verify

```bash
curl -sS http://127.0.0.1:8080/health
curl -sS http://127.0.0.1:8090/health
```

## Quick retrieval test

```bash
python3 scripts/benchmark_retrieval_real_case.py
```

## Important files
- `docker-compose.yml` — unified stack for one-command startup
- `infra/dokploy/docker-compose.dokploy.yml` — Dokploy deploy stack
- `docs/DOKPLOY_RUNBOOK.md` — Dokploy deployment steps

## Status
MVP stack up and retrieval benchmarked with grounded citations.
