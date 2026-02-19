# Aletheia

Research-grade RAG platform for large-scale book knowledge bases (10k–15k books).

## Goals
- High-recall retrieval across books and papers
- Citation-first answers (book/chapter/page)
- Scalable ingestion + hybrid search + reranking

## Architecture (MVP)
- `apps/api` — query API (`/search`, `/ask`)
- `apps/ingest` — ingestion pipeline entrypoint
- `apps/worker` — background parsing/chunking/indexing
- `schemas` — DB + metadata schema
- `infra/docker` — local stack (Postgres, OpenSearch, Qdrant, MinIO, Redis)

## Quick start
1. Copy `.env.example` to `.env`
2. Start dependencies via Docker compose
3. Run migrations and boot API/worker

## Status
Scaffold initialized.
