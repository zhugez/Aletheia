# Ingest Queue Plan (Redis)

## Job shape
```json
{
  "job_id": "uuid",
  "source_uri": "s3://bucket/file.pdf",
  "source_type": "book",
  "status": "queued",
  "created_at": "ISO8601"
}
```

## Stages
1. register_source
2. parse_or_ocr
3. semantic_chunk
4. embed
5. index_lexical (OpenSearch)
6. index_vector (Qdrant)
7. done / failed
