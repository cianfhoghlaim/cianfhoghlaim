# Frontend Stack

The 5 TypeScript frontend workspaces in the Cianfhoghlaim monorepo, packaged as
independent services and routed through Pangolin + Traefik.

## Services

| Service | Port | Subdomain | Stack |
|:--|:--|:--|:--|
| `oideachais-web` | 3001 | `oideachais.cianfhoghlaim.ie` | TanStack Start + Hono + Convex + CopilotKit + BAML |
| `oideachais-api` | 8787 | `oideachais-api.cianfhoghlaim.ie` | Hono + oRPC + Better Auth + LiteLLM |
| `tuatha-ui` | 3004 | `tuath.cianfhoghlaim.ie` | TanStack Start + Babylon.js + SIWE + x402 + SpacetimeDB |
| `croilar-web` | 3003 | `croilar.cianfhoghlaim.ie` | Vite SPA + Radix + i18n (en/ga) |
| `croilar-portal` | 3000 | `portal.cianfhoghlaim.ie` | TanStack Start + AI SDK + MCP-UI + Komodo |

## Architecture

```
Browser (https://oideachais.cianfhoghlaim.ie)
   │
   ├─ oideachais-web (TanStack Start SSR, port 3001)
   │     └─ /api, /rpc, /api-reference → oideachais-api
   │
   ├─ oideachais-api (Hono + oRPC, port 8787)
   │     ├─ /api/auth/*        → Better Auth (OIDC issuer)
   │     ├─ /rpc/*             → oRPC contract-first RPC
   │     ├─ /api-reference/*  → OpenAPI / Swagger
   │     └─ /api/copilotkit    → AG-UI streaming runtime
   │
   ├─ tuatha-ui (TanStack Start, port 3004)
   │     └─ /api/*, server fns → Graphiti + LanceDB
   │
   ├─ croilar-web (Vite SPA, port 3003)
   │     └─ CV / GitHub / pipeline data → hono-api
   │
   └─ croilar-portal (TanStack Start, port 3000)
         └─ /api/agent, /api/mcp/* → LiteLLM gateway
```

## Backend Dependencies

| Backend | Port | Purpose |
|:--|:--|:--|
| `litellm` | 4000 | LLM gateway (BAML extraction, agent chat) |
| `convex-backend` | 3210 | Real-time reactive database |
| `hono-api` (croilar) | 4000 | Better Auth issuer + data API + MCP gateway |
| `langfuse-web` | 3000 | LLM observability |
| `graphiti` | 8080 | Temporal knowledge graph (mythology) |
| `lancedb` | 8080 | Vector search (curriculum) |
| `komodo` | 9120 | Stack management API |

## Files

| File | Purpose |
|:--|:--|
| `compose.yaml` | Production deployment (build from local source) |
| `compose.dev.yaml` | Dev override with hot-reload via `docker compose watch` |
| `pangolin.yaml` | Traefik routes + Pocket ID OIDC for `*.cianfhoghlaim.ie` subdomains |
| `sidecar.yaml` | Locket sidecar that hydrates `secrets.env` from Infisical |
| `secrets.env` | Infisical URI references (no plaintext) |
| `.env.example` | Dev-only env vars template |
| `blueprint.yaml` | Komodo resource-sync metadata |

## Local Dev

```bash
# From this directory:
cp .env.example .env
docker compose -f compose.yaml -f compose.dev.yaml up -d
docker compose logs -f
```

## Production

Komodo syncs this stack every 6 hours and on git push:

```bash
# Manual trigger via Komodo API:
curl -X POST https://komodo.cianfhoghlaim.ie/api/stack/frontend/Deploy
```

Pangolin routes `*.cianfhoghlaim.ie` traffic to the right container.

## Verification

```bash
# All 5 services should respond
for port in 3001 8787 3004 3003 3000; do
  curl -sf "http://localhost:$port/" >/dev/null && echo "OK: $port" || echo "FAIL: $port"
done

# Health endpoints
curl http://localhost:8787/         # oideachais-api root
curl http://localhost:3000/         # croilar-portal root
```
