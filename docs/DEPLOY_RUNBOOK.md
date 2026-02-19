# Deploy Runbook (API + MCP + OpenClaw Bridge)

## 1) Start core infra
```bash
docker compose -f infra/docker/docker-compose.yml pull

docker compose -f infra/docker/docker-compose.yml up -d
```

## 2) Start app services
```bash
docker compose -f infra/docker/docker-compose.apps.yml up -d --build
```

## 3) Verify health
```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8090/health
```

## 4) Verify bridge tool call
```bash
curl -X POST http://127.0.0.1:8090/tool/search_knowledge \
  -H 'content-type: application/json' \
  -d '{"token":"change-me","query":"retrieval quality","top_k":3}'
```

## 5) OpenClaw integration
Configure a custom HTTP tool/plugin in OpenClaw that calls:
- `POST /tool/search_knowledge`
- `POST /tool/ask_knowledge`

Include `token` payload field with your `ALETHEIA_BRIDGE_TOKEN`.

## 6) Production hardening checklist
- [ ] Replace default bridge token
- [ ] Restrict bridge to private network / localhost
- [ ] Add reverse proxy with TLS
- [ ] Enable request logs + monitoring
- [ ] Rotate secrets regularly
