# Aletheia

Research-grade RAG platform for large-scale book knowledge bases (10k–15k books).

## Goals
- High-recall retrieval across books and papers
- Citation-first answers (book/chapter/page)
- Scalable ingestion + hybrid search + reranking

## Architecture (modular monolith)
- `apps/api` — HTTP API (`/search`, `/ask`, `/ingest`, `/jobs/{id}`)
- `apps/worker` — background worker process (RQ)
- shared storage/index backends: Postgres, OpenSearch, Qdrant, Redis, RustFS

## One-command startup

```bash
cp .env.example .env
docker compose up -d --build
```

This brings up everything:
- infra services
- migration job (`schemas/metadata.sql`)
- API + bridge + background worker

## Verify

```bash
curl -sS http://127.0.0.1:40007/health
curl -sS http://127.0.0.1:40008/health
```

## Real retrieval benchmark

```bash
python3 scripts/benchmark_retrieval_real_case.py
```

## Queue example

```bash
curl -sS -X POST http://127.0.0.1:40007/ingest \
  -H 'Content-Type: application/json' \
  -d '{"source_uri":"file:///data/book.pdf","source_type":"book","metadata":{"lang":"vi"}}'

curl -sS http://127.0.0.1:40007/jobs/<job_id>
```

## Important files
- `docker-compose.yml` — unified local stack
- `infra/dokploy/docker-compose.dokploy.yml` — Dokploy stack
- `docs/DOKPLOY_RUNBOOK.md` — Dokploy deployment guide

## Status
MVP upgraded with cache + queue + worker baseline.


## MinerU Full Ingest (one command)

```bash
python3 scripts/ingest_pdf_full_mineru.py /path/to/book.pdf --out /tmp/aletheia_mineru_output --backend pipeline
```

This runs end-to-end:
1. MinerU parse (PDF -> merged markdown)
2. Markdown chunk ingest into Postgres/OpenSearch/Qdrant
