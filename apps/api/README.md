# API Service

Run locally:

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

Endpoints:
- `GET /health`
- `POST /search` (hybrid retrieval: OpenSearch BM25 + Qdrant vector, with graceful fallback to empty results)
- `POST /ask` (grounded synthesis from retrieved chunks + citations; graceful fallback when indexes/services are unavailable)
