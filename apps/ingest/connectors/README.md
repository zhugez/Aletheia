# Ingest Connectors

## AIStudio Layout Parsing Connector

Files:
- `aistudio_layout.py`
- `scripts/test_layout_api.py`

### Environment
- `ALETHEIA_LAYOUT_API_TOKEN` (required)
- `ALETHEIA_LAYOUT_API_URL` (optional, defaults to provided endpoint)
- `ALETHEIA_LAYOUT_TIMEOUT` (optional, default `90`)
- `ALETHEIA_LAYOUT_RETRIES` (optional, default `3`)

### Run
```bash
export ALETHEIA_LAYOUT_API_TOKEN=***
PYTHONPATH=. python scripts/test_layout_api.py /path/to/file.pdf
```

### Security
Do NOT commit tokens. Use env vars/secrets manager only.
