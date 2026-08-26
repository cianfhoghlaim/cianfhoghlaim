# 2026-08-25-post-cascade-followups

## Why

The 2026-08-24 master refactor 8-wave cascade is complete
(tagged `v2026.08.24-wave8-cascade-complete`). Wave 8 documented the
**out-of-scope follow-up work**:

- Per-app migrations (cianfhoghlaim-leaving-cert, croilar-portal, etc.)
- **Real Convex schema** (users, agents, threads, runs, messages,
  knowledge_graph_nodes, per-subject caches)
- **Real AG-UI event streaming** (the Wave 6 stub emits hello events)
- MotherDuck token wire-up
- Lakekeeper Iceberg REST catalog deployment
- DuckLake data migration (6 legacy namespaces → consolidated)
- Cloudflare Pages deployment

This openspec change delivers **3 of the 7 follow-up items** that are
atomic, well-scoped, and unblock downstream work:

1. **Real Convex schema** — replaces the Wave 6 1-table stub with the
   canonical 7-table schema
2. **Real AG-UI SSE handler** — replaces the Wave 6 hello-event stub
   with the streaming implementation that subscribes to the Convex
   `messages` table
3. **.env.example wire-up** — adds the 4 missing env vars
   (`CIANFHOGHLAIM_MOTHERDUCK_TOKEN`, `CONVEX_URL`,
   `CIANFHOGHLAIM_RUNTIME_URL`, `MLFLOW_TRACKING_URI`)

## What changes

### 1. Real Convex schema

`web/packages/db/convex/schema.ts` (replaces the Wave 6 stub).

The new schema has 7 tables with full indexes:

- `users` — Better Auth + Convex integration (3 OIDC audiences per Wave 6)
- `agents` — the 12-agent Cianfhoghlaim fleet (with `pipeline_kind` from
  Wave 2 + `dlt_source` path)
- `threads` — CopilotKit thread storage (with `agent_id` link)
- `runs` — CocoIndex App execution history (with OTel semantic
  convention tags from Wave 7 + DuckLake time-travel snapshot
  reference from Wave 4)
- `messages` — the 12 AG-UI event types from `@cianfhoghlaim/contracts`
  (with OTel semantic convention tags)
- `knowledge_graph_nodes` — Cognee cognify outputs (4 node types)
- `subject_caches` — per-subject BIEP caches (the 15 subjects × 9 boards
  × N years × 2 languages materialised from DuckLake)

### 2. Real AG-UI SSE handler

`web/hono-api/src/routes/agui/index.ts` (replaces the Wave 6 stub).

The new handler:

- 4 endpoints: `GET /agui/sse`, `POST /agui/run`, `GET /agui/threads`,
  `GET /agui/health`
- Streams events from the Convex `messages` table (via the Convex
  streaming query API)
- Heartbeat pattern (every 30s) so the client knows the connection is alive
- Tagged with OTel semantic conventions per Wave 7
- Graceful error handling: emits a `TEXT_MESSAGE_END` event with the
  error info if the Convex subscription fails

### 3. .env.example wire-up

`.env.example` (appended at the bottom).

The 4 new env vars are:
- `CIANFHOGHLAIM_MOTHERDUCK_TOKEN` — MotherDuck auth token (raises
  `RuntimeError` from `get_motherduck_destination()` if missing)
- `CONVEX_URL` — Convex backend URL (default: `http://localhost:8000`)
- `CIANFHOGHLAIM_RUNTIME_URL` — the hono-api gateway URL (default:
  `http://localhost:4000` in dev)
- `MLFLOW_TRACKING_URI` — MLflow tracking URI (default:
  `sqlite:///stedding/mlflow.db` for local dev)

## Out of scope (deferred to subsequent post-cascade PRs)

- **Per-app migrations** (`cianfhoghlaim-leaving-cert` → `oideachais/`,
  `croilar-portal` → `croilar/`, etc.) — too large for one PR
- **Real Convex REST client** at `web/packages/db/convex/client.ts` —
  connects to the live Convex backend (deferred to a Convex SDK upgrade PR)
- **Lakekeeper Iceberg REST catalog deployment** at
  `http://lakekeeper:8181/catalog` — separate IaC PR
- **DuckLake data migration** (the 6 legacy namespaces → consolidated)
- **Cloudflare Pages deployment** for the 5 web apps

## Verification

After this change lands:

1. `web/packages/db/convex/schema.ts` has 7 tables (was 1)
2. `web/hono-api/src/routes/agui/index.ts` has 4 endpoints (was 1)
3. `.env.example` has the 4 new env vars at the bottom
4. `bun install` + `bun run typecheck` succeed for all 5 packages
5. `npx convex dev` accepts the new schema

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Wave 0-8: see prior openspec changes
- Cascade tag: `v2026.08.24-wave8-cascade-complete`
- Convex docs: https://docs.convex.dev/database/schemas
- AG-UI spec: https://docs.ag-ui.com/
