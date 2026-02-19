# OpenClaw Integration Plan

## Option A: MCP-native clients
Run `apps/mcp_server/server.py` and connect any MCP-capable client.

## Option B: OpenClaw bridge (recommended now)
1. Start Aletheia API (`apps/api`).
2. Start bridge (`apps/bridge`) on port `8090`.
3. In OpenClaw, add a custom HTTP tool/plugin that calls:
   - `POST /tool/search_knowledge`
   - `POST /tool/ask_knowledge`
4. Pass `ALETHEIA_BRIDGE_TOKEN` in body or adapter-level secret.

## Security notes
- Restrict bridge to localhost or private network.
- Rotate bridge token.
- Add request logging + rate limits in production.
