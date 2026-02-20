# Dokploy Runbook (Aletheia)

## 1) Create app in Dokploy
- Type: **Docker Compose**
- Compose path: `infra/dokploy/docker-compose.dokploy.yml`
- Environment file: copy `infra/dokploy/dokploy.env.sample` and set real secrets.

## 2) Expose only public services
Public:
- `aletheia-api` (port 8080) if you need direct API access
- `aletheia-bridge` (port 8090) for OpenClaw tool calls

Private/internal only:
- postgres, redis, opensearch, qdrant, minio

## 3) First deploy bootstrap
After first deploy, run migration inside Postgres container:

```bash
docker exec -i <postgres-container> psql -U $POSTGRES_USER -d $POSTGRES_DB < schemas/metadata.sql
```

Then ingest a quick sample:

```bash
python3 scripts/ingest_markdown_chunks.py --input-dir /tmp/aletheia_layout_output --file chapter_1_page_1_scaling_playbook.md
```

## 4) Smoke tests
```bash
curl -sS http://<api-domain>/health

curl -sS -X POST http://<api-domain>/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"WordPress scaling performance","top_k":3}'

curl -sS -X POST http://<api-domain>/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Why WordPress was not enough?","top_k":3,"mode":"grounded"}'
```

## 5) OpenClaw bridge test
```bash
curl -sS -X POST http://<bridge-domain>/tool/search_knowledge \
  -H 'content-type: application/json' \
  -d '{"token":"<ALETHEIA_BRIDGE_TOKEN>","query":"retrieval quality","top_k":3}'
```

## 6) Ops notes
- Do **not** split core/apps into separate compose projects in Dokploy for this stack.
- Keep one compose to avoid orphan/ordering issues.
- Rotate `ALETHEIA_BRIDGE_TOKEN` and DB credentials before production use.
- Add domain-level auth/IP allowlist for bridge endpoint.
