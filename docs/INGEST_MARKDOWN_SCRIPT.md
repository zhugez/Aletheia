# Minimal Markdown Ingest Script

Script: `scripts/ingest_markdown_chunks.py`

Purpose:
- Read markdown files from `/tmp/aletheia_layout_output` (or `--input-dir`)
- Chunk text
- Ingest into Postgres (`sources`, `chunks`), OpenSearch (`aletheia_chunks`), and Qdrant (`aletheia_chunks`)
- Preserve metadata: `title`, `chapter`, `page_start`, `page_end`, `source_id`, `chunk_id`

Usage:

```bash
python3 scripts/ingest_markdown_chunks.py --input-dir /tmp/aletheia_layout_output
```

Notes:
- If `psycopg` is missing, Postgres ingest is skipped with a warning.
- OpenSearch/Qdrant failures are logged and do not stop ingesting other backends.
- Designed as a minimal production-safe bootstrap script for MVP indexing.
