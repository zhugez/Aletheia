# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Aletheia is a research-grade RAG (Retrieval-Augmented Generation) platform for high-recall retrieval across large-scale book knowledge bases (10k–15k books). It follows a modular monolith architecture with citation-first answers (book/chapter/page references).

## Common Commands

### Full Stack (Docker)
```bash
cp .env.example .env          # first time only
docker compose up -d --build   # start everything
curl -sS http://127.0.0.1:40007/health   # verify API
curl -sS http://127.0.0.1:40008/health   # verify bridge
```

### API Service (local dev)
```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
granian --interface asgi --host 127.0.0.1 --port 8080 --reload main:app
```

### Web Frontend
```bash
cd apps/web
npm install
npm run dev      # dev server at localhost:4321
npm run build    # production build to ./dist/
```

### Benchmarks
```bash
python3 scripts/benchmark_retrieval_real_case.py
```

## Architecture

### Services (`apps/`)

| Service | Port | Stack | Purpose |
|---------|------|-------|---------|
| `api` | 40007 | FastAPI (Python 3.11) | HTTP API: `/search`, `/ask`, `/ingest`, `/upload`, `/jobs/{id}`, `/cache/clear` |
| `bridge` | 40008 | FastAPI (Python 3.11) | OpenClaw integration layer with token auth + rate limiting |
| `worker` | — | RQ (Python 3.11) | Background job processing from Redis queue |
| `web` | 40009 | Astro + Tailwind → Nginx | Frontend UI |

### Infrastructure (via Docker Compose)

- **PostgreSQL 16** (40001) — metadata store (`sources` + `chunks` tables, schema in `schemas/metadata.sql`)
- **Redis 7** (40002) — job queue (RQ) + cache layer
- **OpenSearch 2.15** (40003) — BM25 full-text search
- **Qdrant v1.12** (40004) — vector similarity search
- **RustFS** (40005/40006) — object storage for uploads

### Key Data Flow

**Search:** Request → cache check → OpenSearch BM25 + Qdrant vector (parallel) → score normalization → weighted merge (BM25: 0.65, Vector: 0.35) → deduplicated top-k with citations → cache result

**Ingest:** Upload → enqueue to Redis (`aletheia_ingest` queue) → worker picks up → (parse → chunk → embed → index) → client polls `/jobs/{id}`

**Supported upload formats:** PDF, EPUB, and images (JPG, PNG, WebP, BMP, TIFF). EPUB files are parsed chapter-by-chapter (spine order) via `apps/ingest/parsers/epub_parser.py`.

### Code Layout Within `apps/api/`

- `main.py` — FastAPI app with all route handlers
- `services/retrieval.py` — hybrid search orchestration (BM25 + vector merge)
- `services/cache_store.py` — Redis cache with namespace-based TTL and invalidation
- `services/job_queue.py` — RQ job management (enqueue, status, retry, cancel)
- `adapters/opensearch_adapter.py` — OpenSearch BM25 queries and bulk indexing
- `adapters/qdrant_adapter.py` — Qdrant vector upsert/search (currently SHA256-based 64-dim deterministic embeddings)

### Citation Contract

Every returned chunk must include: `source_id`, `title`, `chapter`, `page_start`, `page_end`, `score`.

## Key Design Decisions

- **Graceful degradation**: all services return fallback results when backends are unavailable
- **Deterministic embeddings (MVP)**: SHA256-based 64-dim vectors avoid model dependency; will be replaced with real embeddings
- **Idempotent ingestion**: Qdrant upsert prevents duplicate chunks
- **Configurable retrieval weights**: BM25/vector balance tunable via env vars (`RETRIEVAL_BM25_WEIGHT`, `RETRIEVAL_VECTOR_WEIGHT`)
- **Docker hardening**: read-only FS, cap_drop ALL, no-new-privileges, non-root users

## Environment Variables

See `.env.example` for full list. Key ones:
- `RETRIEVAL_BM25_WEIGHT` / `RETRIEVAL_VECTOR_WEIGHT` — hybrid search balance
- `SEARCH_CACHE_TTL` / `ASK_CACHE_TTL` — cache lifetimes in seconds
- `ALETHEIA_QUEUE` — Redis queue name for ingest jobs
- `ALETHEIA_BRIDGE_TOKEN` — auth token for bridge service

## Documentation

Detailed docs live in `docs/`:
- `ARCHITECTURE.md` — data flow and core services
- `API_CONTRACT.md` — endpoint request/response specs
- `BATCH_UPLOAD_DESIGN.md` / `BATCH_UPLOAD_PRD.md` — batch upload feature design
- `INGEST_QUEUE.md` — job shape and ingestion stages
- `OPENCLAW_INTEGRATION.md` — bridge setup and security
- `DEPLOY_RUNBOOK.md` / `DOKPLOY_RUNBOOK.md` — deployment guides
