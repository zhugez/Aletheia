# Aletheia Architecture (MVP)

## Data Flow
1. Upload book/document to object storage (MinIO/S3)
2. Ingest service extracts metadata and text/OCR
3. Worker chunks content with provenance fields
4. Index lexical fields in OpenSearch and embeddings in Qdrant
5. API executes hybrid retrieval + rerank + citation formatting

## Core Services
- API service: query, answer orchestration, auth
- Ingest service: source registration and job creation
- Worker service: parse, OCR, chunk, embed, index
- Metadata DB (Postgres): source of truth
- Redis queue: async jobs

## Citation Contract
Every returned chunk must include:
- source_id
- title
- chapter
- page_start
- page_end
- score
