# Aletheia MCP Server

MCP tools exposed:
- `search_knowledge(query, top_k, domain?)`
- `ask_knowledge(question, top_k, mode)`
- `get_source(source_id)`
- `ingest_source(source_uri, source_type, metadata)`
- `ingest_status(job_id)`

## Run
```bash
cd apps/mcp_server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

## Env
- `ALETHEIA_API_BASE` (default: `http://127.0.0.1:8080`)
- `ALETHEIA_API_KEY` (optional)
