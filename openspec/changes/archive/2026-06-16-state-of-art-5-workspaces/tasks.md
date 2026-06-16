# Tasks: State-of-the-Art 5 Workspaces

## Phase 1 — Restructure (no feature changes)

- [ ] 1.1 Delete `oideachais/web/src/` (empty Vinxi relic)
- [ ] 1.2 Fix `oideachais/web/app.config.ts` — replace stale Vinxi config with TanStack Start vite plugin
- [ ] 1.3 Run `bunx convex dev --once` in `oideachais/web/convex/` to populate `_generated/`
- [ ] 1.4 Run `bunx baml-cli generate` to regenerate BAML client types
- [ ] 1.5 Run `bunx @tanstack/router-cli generate` in oideachais/web to regen `routeTree.gen.ts`
- [ ] 1.6 Add root `README.md` to oideachais/web with architecture diagram, env map, dev commands
- [ ] 1.7 Add per-route READMEs under `oideachais/web/apps/web/src/app/routes/{en,ga}/`
- [ ] 1.8 Add `oideachais/web/convex/README.md` (5 tables, RLS)
- [ ] 1.9 Add `oideachais/web/packages/api/README.md` (oRPC routers, auth flow)
- [ ] 1.10 Delete `tuatha/ui/app.config.ts` (replaced by native TanStack Start in vite.config.ts)
- [ ] 1.11 Fix `tuatha/ui/src/routes/game.tsx` import from `../../game/client/src` to workspace ref
- [ ] 1.12 Add root `README.md` to tuatha/ui
- [ ] 1.13 Add per-route READMEs in tuatha/ui/src/routes/
- [ ] 1.14 Add `tuatha/ui/src/server/README.md` (curriculum, mythology server functions)
- [ ] 1.15 Add root `README.md` to croilar/apps/web
- [ ] 1.16 Add per-route READMEs in croilar/apps/web/src/routes/
- [ ] 1.17 Add `croilar/apps/portal/src/routes/_layout/README.md` summarizing portal sections
- [ ] 1.18 Add `croilar/apps/portal/src/lib/tenant/README.md` (tenant config loader)
- [ ] 1.19 Add per-folder READMEs to croilar/hono-api (auth, db, data)
- [ ] 1.20 Add `croilar/hono-api/ORGANIZATIONS.md`
- [ ] 1.21 Add `croilar/hono-api/ARCHITECTURE.md` with sequence diagrams

## Phase 2 — croilar/hono-api real wiring

- [ ] 2.1 Add SIWE plugin to Better Auth config
- [ ] 2.2 Add Convex auth provider (JWT validation via JWKS)
- [ ] 2.3 Wire `src/data/duckdb.ts` with real DuckDB connection
- [ ] 2.4 Add `/mcp/*` route registering 5 MCP servers
- [ ] 2.5 Add x402 paywall middleware on MCP servers
- [ ] 2.6 Expand `src/db/schema.ts` with orgs, members, invitations, jwks, passkey, oauth tables
- [ ] 2.7 Run `bun db:generate && bun db:migrate` — initial migration
- [ ] 2.8 Add seed script creating 4 orgs + test user per org

## Phase 3 — oideachais/web: AG-UI + auth + DB

- [ ] 3.1 Replace CopilotKit runtime stub with real AG-UI streaming pipeline
- [ ] 3.2 Wire `subject_sessions` Convex table to CopilotKit session persistence
- [ ] 3.3 Add `@tanstack/db` collection for `practice_attempts` client-side cache
- [ ] 3.4 Wire `packages/auth/src/index.ts` to real Better Auth with Drizzle adapter
- [ ] 3.5 Fix `protectedProcedure` to actually validate sessions (currently throws UNAUTHORIZED)
- [ ] 3.6 Wire `baml_src/curriculum_extraction.baml` into new `packages/api/routers/baml.ts` oRPC procedure
- [ ] 3.7 Add Langfuse tracing to BAML extraction (extraction_budget enforcement)

## Phase 4 — oideachais/web: observability + bilingual

- [ ] 4.1 Wire `packages/api/routers/motherduck.ts` to real `<MotherDuckDive>` React component
- [ ] 4.2 Replace ConvexReactClient with Effect-TS layer in `apps/web/src/app/router.tsx`
- [ ] 4.3 Add `loader()` server functions to each bilingual route (`en/` + `ga/`)
- [ ] 4.4 Add `withLangfuse` middleware on the `o` builder for all oRPC procedures
- [ ] 4.5 Verify `bun run typecheck` passes in oideachais/web

## Phase 5 — tuatha/ui: backend wiring

- [ ] 5.1 Wire `routes/game.tsx` to SpacetimeDB subscription (real multiplayer)
- [ ] 5.2 Replace `useAuth.ts` stub with real `useSiweAuth()` hook
- [ ] 5.3 Wire `X402Paywall.tsx` to real x402 middleware on Hono API
- [ ] 5.4 Wire `server/mythology.ts` to Graphiti + LanceDB backend
- [ ] 5.5 Wire `server/curriculum.ts` to Graphiti + LanceDB backend

## Phase 6 — tuatha/ui: front-end

- [ ] 6.1 Wire `routes/map.tsx` to real MapLibre instance with Celtic GeoJSON
- [ ] 6.2 Add mythology A2UI cards (using existing A2UIComponents.tsx)
- [ ] 6.3 Wire `routes/learn/irish.tsx` to crypteolas demo server function
- [ ] 6.4 Grep-and-remove any remaining Vinxi references
- [ ] 6.5 Verify `bun run typecheck` passes in tuatha/ui

## Phase 7 — croilar/apps/web: real data

- [ ] 7.1 Replace PLACEHOLDER_AWARDS with createServerFn → hono-api `/api/v1/cv`
- [ ] 7.2 Replace PLACEHOLDER_EDUCATION with createServerFn → hono-api
- [ ] 7.3 Replace PLACEHOLDER_PUBLICATIONS with createServerFn → Zotero API
- [ ] 7.4 Replace PLACEHOLDER_REFERENCES with createServerFn → hono-api
- [ ] 7.5 Wire `routes/music.tsx` to Marimo WASM notebook
- [ ] 7.6 Wire `routes/research.tsx` to BAML ResearchQuery server function
- [ ] 7.7 Wire `pages/data/pipeline-status.tsx` to hono-api `/api/v1/pipelines`
- [ ] 7.8 Wire `pages/identity/verification-card.tsx` to SIWE auth + ENS resolution
- [ ] 7.9 Wire `pages/contact/form.tsx` to MCP contact submit
- [ ] 7.10 Add `ga.json` Irish translations bundle
- [ ] 7.11 Verify `bun run typecheck` passes

## Phase 8 — croilar/apps/portal: core

- [ ] 8.1 Implement `useAgentChat` hook using ai-sdk v5 `useChat` with AG-UI protocol
- [ ] 8.2 Wire `mcp.gateway.ts` to real LiteLLM MCP proxy
- [ ] 8.3 Add MCP-UI component rendering in agent chat responses
- [ ] 8.4 Replace `stacks/index.tsx` mock array with real Komodo API calls
- [ ] 8.5 Add start/stop/restart actions on Komodo-managed stacks

## Phase 9 — croilar/apps/portal: monitoring + analytics

- [ ] 9.1 Wire `monitoring/logs.tsx` to real Docker container logs
- [ ] 9.2 Wire `monitoring/metrics.tsx` to real Prometheus scrape
- [ ] 9.3 Wire `data/pipelines.tsx` to Dagster GraphQL endpoint
- [ ] 9.4 Wire `analytics/index.tsx` to Langfuse traces + MotherDuck Dive
- [ ] 9.5 Inject tenant CSS variables in `__root.tsx` from `useTenant()`
- [ ] 9.6 Add `config/tenants/*.yaml` schema validator
- [ ] 9.7 Verify `bun run typecheck` passes

## Phase 10 — Cross-cutting

- [ ] 10.1 Update root `README.md` with 5-project mono-graph section
- [ ] 10.2 Add `infrastructure/stacks/frontend/compose.yaml` with 5 containers
- [ ] 10.3 Verify each project's `wrangler.toml`/`wrangler.json` is correct
- [ ] 10.4 Add `bun run smoke` script (Docker compose boot → curl health → teardown)
- [ ] 10.5 Add `mise turbo typecheck` alias
- [ ] 10.6 Grep `TODO|FIXME|XXX` across all 5 projects → audit disposition
- [ ] 10.7 Final `bun run turbo typecheck` (all 5 projects)
- [ ] 10.8 Push to remote
