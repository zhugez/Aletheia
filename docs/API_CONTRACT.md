# API Contract (v0.2)

## POST /search
Request:
```json
{
  "query": "what is retrieval augmented generation",
  "top_k": 5,
  "domain": "ai"
}
```

Response:
```json
{
  "request_id": "uuid",
  "query": "...",
  "domain": "ai",
  "results": [
    {
      "text": "...",
      "source_id": "...",
      "title": "...",
      "author": "...",
      "chapter": "...",
      "page_start": 1,
      "page_end": 2,
      "score": 0.82
    }
  ]
}
```

## POST /ask
Request:
```json
{
  "question": "How to improve retrieval quality?",
  "top_k": 5,
  "mode": "grounded"
}
```

Response includes:
- `answer`
- `confidence` (low/medium/high)
- `insufficient_evidence` (boolean)
- `citations[]` with provenance fields
