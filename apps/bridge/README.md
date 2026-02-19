# OpenClaw Bridge (HTTP)

Thin bridge that exposes Aletheia tools via HTTP endpoints for OpenClaw plugin/tool integration.

## Endpoints
- `GET /health`
- `POST /tool/search_knowledge`
- `POST /tool/ask_knowledge`

## Run
```bash
cd apps/bridge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ALETHEIA_API_BASE=http://127.0.0.1:8080 \
ALETHEIA_BRIDGE_TOKEN=change-me \
uvicorn openclaw_bridge:app --host 0.0.0.0 --port 8090
```

## Request example
```bash
curl -X POST http://127.0.0.1:8090/tool/search_knowledge \
  -H 'content-type: application/json' \
  -d '{"token":"change-me","query":"rag citation","top_k":3}'
```
