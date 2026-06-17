# Change: croilar-devtools-hub

## Why

The croilar portal is already 80% of a centralized dev tools hub for the monorepo. It has Convex polling (Komodo, Dagster, MCP, GHCR), TanStack Start pages, a BAML extraction layer, marimo notebook wiring, and a tenant framework. What's missing for the user's stated goal — "efficient pipelines for troubleshooting and testing our extensive typescript, tanstack, convex, cloudflare and other such web features" — is observability of the web stack itself.

Specifically, today the portal has no way to answer questions like:

- "How many TanStack routes does tuatha have, and which ones are public?"
- "Which Convex functions in oideachais are slow (p95 > 500ms)?"
- "Did the last `bun run turbo test` for meaisínfhoghlaim pass?"
- "What BAML schemas does the cv extraction use, and when were they last compiled?"
- "What Cloudflare Workers are deployed, and to which environment?"
- "What marimo notebooks cover the cv stream, and have they been WASM-exported?"

Three concrete gaps block these answers:

1. **No Convex tables for the web stack.** The portal already polls Komodo, Dagster, MCP, and GHCR — but not the user's own code (routes, functions, schemas, tests, deploys).
2. **Three portal pages are still hard-coded mocks.** `/data/pipelines`, `/monitoring/logs`, `/monitoring/metrics` show `mockLogs` / `mockPipelines` arrays from the user's own source rather than live data.
3. **Glance is hand-edited.** `infrastructure/stacks/infrastructure/glance/config/glance.yml` is a 64-line static file; the portal's widgets page has 40+ widgets across 4 categories but they are not surfaced into Glance.

This change adds the data foundation (9 new Convex tables + a Convex-aware analyzer), the portal binding (live data + 2 new pages), and the Glance/MCP integration (auto-generation + a new `croilar-mcp-devtools` MCP server).

Out of scope (deferred to follow-up issues):

- **Test-runs CI ingest.** The `testRuns` table and `ingest` mutation are created; the GitHub Action or Komodo schedule that calls it is a follow-up.
- **`meaisínfhoghlaim` web analyzer.** That project has no `convex/` or `wrangler.toml` yet; the analyzer skips it gracefully. Re-enable when a web app is added.
- **Marimo-as-a-service polish (Phase D).** New marimo notebooks are created; the inline WASM renderer in `/notebooks/$slug` is wired but the full service is deferred.
- **`developer` role + fine-grained access control (Phase E).** The new `/web` and `/notebooks` pages are gated behind `croilar-admin` org owner|admin; finer-grained roles are a follow-up.

## What Changes

### Capabilities

- **ADD** `croilar-devtools-hub` (new capability)
- **MODIFY** `croilar-data-engineering` (9 new Convex tables, 9 new modules, action-call middleware, 6 new cron entries, Bun analyzer)
- **MODIFY** `croilar-portfolio` (3 portal pages rewritten with live data; 2 new pages: `/web`, `/notebooks`; nav updates)

### Code

#### `croilar/convex/schema.ts` (MODIFIED — append 9 tables)
1. `tanstackRoutes` — TanStack route inventory per project
2. `convexFunctions` — Convex query/mutation/action inventory
3. `cloudflareResources` — Workers / Pages / R2 / KV / D1 / DO inventory
4. `bamlSchemas` — BAML schema/class/function counts
5. `testRuns` — CI test result ingest
6. `convexFunctionCalls` — every action call recorded by middleware
7. `convexMetrics` — p50/p95/qps/error_rate per scope
8. `marimoNotebooks` — notebook inventory
9. `glanceConfig` — Glance YAML version history

#### New Convex modules (9 files, all in `croilar/convex/`)
`tanstack_routes.ts`, `convex_functions.ts`, `cloudflare_resources.ts`, `baml_schemas.ts`, `test_runs.ts`, `convex_function_calls.ts`, `convex_metrics.ts`, `marimo_notebooks.ts`, `glance_config.ts`. Each follows the canonical `list` + `getByProject` + `refreshAll` (action) shape used by the existing `pipelines.ts` and `stacks.ts`.

#### `croilar/convex/_middleware.ts` (NEW)
`loggedAction(fn, {function, project})` helper that wraps every action invocation and records to `convexFunctionCalls`. Opt-in per file (one-line wrap).

#### `croilar/convex/crons.ts` (MODIFIED — append 6 entries)
`syncTanstackRoutes (6h)`, `syncConvexFunctions (12h)`, `syncCloudflareResources (6h)`, `syncBamlSchemas (daily)`, `syncMarimoNotebooks (12h)`, `refreshConvexMetrics (5m)`.

#### `croilar/scripts/analyze-web-stack.ts` (NEW — Bun)
Canonical monorepo walker. Walks tuatha, oideachais, croilar, meaisínfhoghlaim routes/convex/wrangler/baml/notebook trees. HTTP-POSTs aggregates to Convex using the Infisical-loaded service token.

#### `croilar/scripts/regenerate-glance-config.ts` (NEW — Bun)
Reads from the 9 new Convex tables + the existing `stacks`/`pipelines`/`registry` tables. Emits a 5-page `glance.yml`. Refuses to clobber a manually-edited file unless `CROILAR_GLANCE_REGEN_FORCE=true`.

#### `croilar/apps/portal/src/routes/_layout/data/pipelines.tsx` (REPLACED)
Live data via `useQuery(api.pipelines.list, {})`. Group by `assetGroupName`. Reactive Convex subscription.

#### `croilar/apps/portal/src/routes/_layout/monitoring/logs.tsx` (REPLACED)
Live data via `useQuery(api.convexFunctionCalls.tail, { limit: 200 })`. Project/function/ok filters.

#### `croilar/apps/portal/src/routes/_layout/monitoring/metrics.tsx` (REPLACED)
Live data via `useQuery(api.convexMetrics.get, { scope: "global" })`. p50/p95/qps/error_rate per scope.

#### `croilar/apps/portal/src/routes/_layout/web/` (NEW)
`index.tsx` — project picker. `$project.tsx` — per-project view (routes, Convex fns, BAML, tests, Cloudflare, marimo). **Troubleshoot drawer** with cross-references.

#### `croilar/apps/portal/src/routes/_layout/notebooks/` (NEW)
`index.tsx` — grid of marimo notebook cards. `$slug.tsx` — inline WASM render.

#### `croilar/mcp/devtools/` (NEW — TypeScript Bun server)
Tools: `list_convex_functions`, `list_tanstack_routes`, `get_test_results`, `get_glance_config`, `tail_logs`, `get_summary`, `regenerate_glance`. Backed by Convex HTTP.

#### `opencode.json` (MODIFIED)
Register `mcp.croilar-devtools`.

#### `.infisical.env` (MODIFIED)
Add `CROILAR_CONVEX_DEPLOY_KEY=infisical://dev-baile/croilar/convex/deploy_key`.

#### `infrastructure/stacks/infrastructure/glance/{pangolin.yaml,blueprint.yaml}` (MODIFIED)
Add 4 sub-paths under the existing private Glance resource: `/tuatha`, `/oideachais`, `/croilar`, `/meaisinfhoghlaim`.

#### `infrastructure/komodo/procedures/croilar-glance-regenerate.toml` (NEW)
Runs the regenerator on a schedule + on-demand.

#### New marimo notebooks (3 files in `croilar/notebooks/streams/teaching/`)
- `web_route_health.py` — `tanstackRoutes` + `testRuns` → pass/fail per route per project
- `convex_function_latency.py` — `convexFunctionCalls` → p50/p95 per function
- `baml_extraction_quality.py` — BAML `langfuse` traces → confidence histograms

#### Auth model
The new `/web` and `/notebooks` pages are gated behind `croilar-admin` org owner|admin. A new `helpers.currentRole` query exposes the current user's role; the pages render an `AccessDenied` component when the user is not in the required role.

### NOT changed

- The 4 existing data-source Convex modules (`pipelines`, `stacks`, `mcp`, `registry`) keep their shape; the new modules follow the same pattern
- The existing 5 portal `_layout` sub-pages (`agents`, `analytics`, `stacks`, `tools`, `widgets`) keep their current behavior; only `data`, `monitoring` are rewritten and `web`, `notebooks` are new
- The Glance stack itself (compose.yaml, sidecar.yaml) is unchanged — only `glance.yml`, `pangolin.yaml`, and `blueprint.yaml`

## Impact

- **Code** — ~25 files modified, ~15 new files
- **Config** — `.infisical.env`, `opencode.json`, two Glance YAML files, one Komodo TOML
- **Data** — additive; existing music/teaching/cv data flows continue unchanged
- **Tests** — 3 new test files in `croilar/tests/`; existing tests stay green
- **CI** — `bun run turbo typecheck` must pass; `openspec validate --strict` must pass
- **Auth** — two new portal pages gated behind `croilar-admin`
- **Out-of-scope, deferred to follow-up issues:**
  - **Phase D** (marimo-as-a-service polish) — deferred
  - **Phase E** (developer role + fine-grained access control) — deferred
  - **`meaisínfhoghlaim` web analyzer** — when that project gets a web app
  - **Test-runs CI ingest** — wire GitHub Action or Komodo schedule
  - **Cross-project BAML test corpus** — when 3+ projects use the same schema
