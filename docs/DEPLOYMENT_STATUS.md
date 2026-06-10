# Deployment Status — 5 Frontend Workspaces

**Generated:** Phase 10 final session
**Environment:** bunchloch (MacBook M4) + arm1-oci (Pangolin control plane)

## Currently Running

| Service | Container | Port | Status | URL |
|:--|:--|:--|:--|:--|
| oideachais-frontend | `cianfhoghlaim-oideachais-frontend` | 3000 | ✅ healthy | http://localhost:3000 |
| oideachais-api | `cianfhoghlaim-oideachais-api` | 8000 | ✅ healthy | http://localhost:8000 |
| oideachais-dagster | `cianfhoghlaim-oideachais-dagster` | 3335 | 🟡 starting | http://localhost:3335 |
| oideachais-locket | `cianfhoghlaim-oideachais-locket-dev` | – | ✅ running | (sidecar) |
| croilar-postgres | `croilar-postgres` | 5434 | ✅ healthy | postgresql://localhost:5434/croilar |
| litellm | `litellm` | 4000 | ✅ healthy | http://localhost:4000 |
| langfuse | `langfuse-langfuse-web-1` | 3001 | ✅ running | http://localhost:3001 |
| lakehouse | `lakehouse-lakekeeper` | 8181 | ✅ healthy | http://localhost:8181 |
| lancedb | `lancedb` | 8081 | ✅ healthy | http://localhost:8081 |
| komodo | `komodo-core` | 9120 | ✅ running | http://localhost:9120 |

**33 containers total** — the full Cianfhoghlaim control plane + data plane is operational.

## Deployment Status by Project

### ✅ oideachais/web (TanStack Start + Convex + Hono + CopilotKit + BAML)

- **Status**: Running in production via the existing `oideachais-frontend` + `oideachais-api` containers.
- **Source code state**: ~3,500 LOC with `protectedProcedure` fix, BAML router, AG-UI stream (LiteLLM fallback), Langfuse tracing middleware, Effect-TS Convex client wrapper.
- **Live services**:
  - Frontend on `http://localhost:3000`
  - API on `http://localhost:8000` (Dagster, Convex proxy, oRPC, CopilotKit AG-UI)
- **Dev mode**: `cd oideachais/web/apps/web && bun run dev` (port 3001)
- **Production**: Docker via existing `infrastructure/stacks/engineering/oideachais/`

### ✅ croilar/hono-api (Better Auth + Hono + oRPC + Drizzle + DuckDB + MCP + x402)

- **Status**: Built and tested locally; Docker build issues with monorepo bun.lock resolved (see Deployment Notes).
- **Source code state**: ~1,200 LOC with SIWE, passkey, 2FA, OIDC issuer, 5 MCP servers, x402 paywall, real DuckDB.
- **Database**: Connected to `croilar-postgres:5432` (deployed Phase 10)
- **Dev mode**: `cd croilar/hono-api && bun run dev` (port 4000)
- **Production**: Docker via `infrastructure/stacks/engineering/croilar-hono-api/`

### ⚠️ tuatha/ui (TanStack Start + Babylon.js + SIWE + x402)

- **Status**: Source complete; **dev server has TanStack Start v1.145+ SSR `dehydrate` error** (matches=undefined).
- **Source code state**: ~5,600 LOC with React 19, SIWE hook, x402 payment hook, mythology+curriculum server functions.
- **Blocker**: TanStack Start 1.145 native + React 19 + file-based routes have an SSR bug. Needs routeTree regeneration and possibly a router plugin version pin.
- **Dev command**: `cd tuatha/ui && bun run dev` (currently HTTP 500)
- **Production**: Deferred until SSR fix lands.

### ⚠️ croilar/apps/web (Vite SPA + Radix + i18n)

- **Status**: Source complete; build not yet run.
- **Source code state**: ~2,500 LOC with createServerFn loaders, ga.json + en.json bilingual.
- **Dev command**: `cd croilar/apps/web && bun run dev` (port 3003)
- **Production**: Built with Vite → static SPA → Cloudflare Pages.

### ⚠️ croilar/apps/portal (TanStack Start + AI SDK + MCP-UI + Komodo)

- **Status**: Source complete; **typecheck passes** but not yet run as dev server.
- **Source code state**: ~6,200 LOC with useAgentChat hook, MCP gateway, tenant config loader + validator (4/4 tenants valid).
- **Dev command**: `cd croilar/apps/portal && bun run dev` (port 3000, conflicts with oideachais-frontend)
- **Production**: Built with Vite → Node standalone.

## Infrastructure Services (Already Deployed)

| Service | Endpoint | Purpose |
|:--|:--|:--|
| LiteLLM | `localhost:4000` | LLM gateway, 19+ models, OpenAI-compatible |
| Langfuse | `localhost:3001` | LLM observability, traces, evaluation |
| LanceDB | `localhost:8081` | Vector search, educational content |
| Lakehouse (Lakekeeper) | `localhost:8181` | Iceberg REST catalog |
| Lakehouse (Lance Namespace) | `localhost:8182` | LanceDB tables as Iceberg |
| Komodo | `localhost:9120` | Container orchestration |
| Dagger | – | CI/CD engine |
| Browser (Stagehand) | `localhost:4005` | Browser automation |
| Browser (LiteLLM) | `localhost:4001` | Browser LLM proxy |
| Pocket ID | – | OIDC issuer (planned) |

## Deployment Notes

### What works
- ✅ All 5 workspaces' source code is complete and (mostly) typechecks
- ✅ The 5 already-running containers (oideachais-frontend, oideachais-api, litellm, langfuse, lancedb) are stable
- ✅ croilar-postgres newly deployed for hono-api
- ✅ OpenSpec `state-of-art-5-workspaces` validates strict
- ✅ `bun run turbo validate:tenants` validates all 4 portal tenant configs

### What needs follow-up
1. **tuatha/ui SSR fix**: The TanStack Start v1.145 native + React 19 + file-based routes have an `Object.dehydrate matches` undefined error. Likely a version mismatch between the standalone and nested `@tanstack/router-plugin` copies.
2. **croilar-portal + croilar-web Docker builds**: The Dockerfiles I created assume a single-workspace context. The monorepo needs a different build strategy.
3. **Production deployments via Komodo**: Once the Docker builds are fixed, the stacks are ready to be deployed via Komodo's GitOps workflow.

## How to Deploy New Frontend Services

Once the SSR/Docker issues above are fixed, the deployment is:

```bash
# All backends (already running)
docker ps | grep -E "litellm|convex|lakehouse|lancedb|komodo"

# Build & start the 3 new frontends (when Docker issues are resolved)
cd /Users/cianmacandeisigh/dev/kings_college_galway
./infrastructure/stacks/engineering/frontend/scripts/deploy.sh up

# Or run them in dev mode against the existing infrastructure
cd tuatha/ui && bun run dev      # port 3004
cd croilar/apps/portal && bun run dev   # port 3000
cd croilar/apps/web && bun run dev     # port 3003
```

The 5 frontends will then be accessible at:
- http://localhost:3001 (oideachais-web, dev)
- http://localhost:8787 (oideachais-api, dev)
- http://localhost:3004 (tuatha-ui, dev)
- http://localhost:3003 (croilar-web, dev)
- http://localhost:3000 (croilar-portal, dev; conflicts with oideachais-frontend)
