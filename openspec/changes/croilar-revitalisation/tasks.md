# Tasks — croilar-revitalisation

## Phase 0: Pre-flight cleanup (DONE — PR-0 merged)
- [x] PR-0. Delete duplicate `croilar/dagster_assets/definitions.py`
- [x] PR-0. Create missing `pipelines/cv/__init__.py` re-exports
- [x] PR-0. Create `.dlt/config.toml` + `.dlt/secrets.toml.example`
- [x] PR-0. Create `croilar/.gitignore`
- [x] PR-0. Refactor 5-level parent traversal → `_shared.config.paths`
- [x] PR-0. Create `tests/conftest.py` + `tests/test_smoke.py` (27 tests)
- [x] PR-0. Make `_shared/__init__.py` sruth import optional
- [x] PR-0. Fix `dlt.destinations.Destination` type hints
- [x] PR-0. Add `pydantic-settings` to pyproject.toml
- [x] PR-0. Update `.forgejo/workflows/croilar-ci.yaml` with pytest step
- [x] PR-0. Validate: 27/27 tests pass, typecheck passes, openspec validate passes

## Phase 1: Persona registry + monorepo restructure (3 PRs)
- [ ] PR-1a. Write `openspec/changes/croilar-revitalisation/` (this file + proposal + 5 spec deltas)
- [ ] PR-1b. Move `croilar/src/` → `croilar/apps/web/`; add `croilar/apps/{portal,storybook}/`; add `croilar/packages/{ui,auth,db,i18n,config,analytics}/`
- [ ] PR-1c. Update root `package.json` workspaces + `pyproject.toml` uv sources
- [ ] PR-1d. Persona registry: `_schema.ts`, `_registry.ts`, `aleyum.ts`, `cianfhoghlaim.ts`
- [ ] PR-1e. Multi-persona routing: `_persona/$persona.tsx` + `__root.tsx` theme + i18n swap + persona switcher
- [ ] PR-1f. UI package: lift 60+ shadcn/ui components from `stedding/dev/eile/examples/examples/ui/vibesdk/`
- [ ] PR-1g. i18n package: `packages/i18n/resources/{aleyum,cianfhoghlaim,common}.json`
- [ ] PR-1h. Storybook scaffold (optional, deferrable)
- [ ] Validate: `bun install`, `bun run typecheck`, `bun run build` all pass for all new workspaces

## Phase 2: Data layer — Convex + Hono + BetterAuth + DuckDB (4 PRs)
- [ ] PR-2a. 4-service Docker Compose: `croilar-postgres` (dev), `croilar-hono-api`, `croilar-convex`, `croilar-web` — 4 GOLD_STANDARD 6-file stacks
- [ ] PR-2b. Pangolin blueprint for `convex.croilar.cianfhoghlaim.ie`
- [ ] PR-2c. BetterAuth + Hono integration: `/api/auth/*` route, Drizzle schema for `better_auth_*` tables, OIDC client config, `pgBouncer: true`
- [ ] PR-2d. Convex schema + functions: `convex/schema.ts` with 4 tenant orgs + per-persona tables; `auth.config.ts` trusting BetterAuth JWKS; 8+ queries/mutations/actions
- [ ] PR-2e. DuckDB SSR loaders: `packages/db/duckdb/` server-fn wrappers; replace all `PLACEHOLDER_*` arrays with `createServerFn` that queries DuckDB
- [ ] PR-2f. PlanetScale Postgres verification: confirm both ports (6432 + 5432) work for all 3 schemas
- [ ] Validate: `openspec validate croilar-revitalisation --strict`, all 4 compose configs validate, Convex functions deploy locally

## Phase 3: Statistical analysis — Marimo + MotherDuck Dive + curated dashboards (2 PRs)
- [ ] PR-3a. `marimo run` server compose service per persona; MotherDuck sync Dagster asset; portal iframes; WASM-export for public `/data` route
- [ ] PR-3b. Per-persona `/data` route with WASM-exported Marimo + curated Altair/Plotly components in `packages/ui/charts/`
- [ ] PR-3c. Chart-spec extraction build step (marimo export → JSON → Zod-validated chart configs)
- [ ] Validate: WASM exports build in CI; Altair/Plotly components render with mock data; MotherDuck Dive iframe loads

## Phase 4: Self-hosted portal dashboard (3 PRs)
- [ ] PR-4a. Stacks module — Komodo API → 4+ stacks health cards
- [ ] PR-4b. Data Pipelines module — Dagster GraphQL → 15 assets per persona, 4 schedules, 2 sensors
- [ ] PR-4c. Monitoring module — Prometheus + Grafana + Loki iframes
- [ ] PR-4d. MCP Gateway module — 13 MCP servers status + metrics
- [ ] PR-4e. Image Registry module — ghcr.io API → tags, last build, multi-arch manifest
- [ ] PR-4f. Multi-tenant auth UI: login modal (from vibesdk), org switcher, role badges
- [ ] PR-4g. Invite-only collaborator flow
- [ ] Validate: portal/auth-gated; all 5 modules render live data

## Phase 5: Production wiring + BAML (1 PR)
- [ ] PR-5a. BAML compile: `bun run baml-cli generate` → `baml_client/` checked in or CI-generated
- [ ] PR-5b. Wire `cv_extraction_asset` to BAML client (replace `status: ready` with actual extraction)
- [ ] PR-5c. Replace `_shared/observability/tracing.py` stubs with Datadog/Langfuse/Logfire SDKs
- [ ] PR-5d. Replace `_shared/agents/router.py` stubs with real ADK + Agno executors
- [ ] PR-5e. Implement `_shared/database/` — DuckDB connection pool + typed query helpers
- [ ] PR-5f. Update `_shared/__init__.py` to expose the database module
- [ ] Validate: BAML extraction runs end-to-end; all stubs replaced with real SDK calls

## Phase 6: GitOps + CI/CD (Phase 4 from croilar-portfolio, 1 PR)
- [ ] PR-6a. 7 `.forgejo/workflows/` + 7 `.github/workflows/` mirror
- [ ] PR-6b. 8 Komodo procedures (`croilar-stack-up/down/health`, `croilar-image-rebuild/publish`, `croilar-renovate-pr`, `croilar-backup`, `croilar-gitops-fullstack`)
- [ ] PR-6c. 5 new multi-arch images: `croilar-web`, `croilar-portal`, `croilar-dagster`, `croilar-marimo`, `croilar-image-pipeline`
- [ ] PR-6d. 5 existing image multi-arch rebuilds: `browser-grid`, `cal-diy`, `stagehand-local`, `n8n-init`, `vikunja-seed`
- [ ] PR-6e. SOPS setup for long-lived credentials
- [ ] PR-6f. 20 new Infisical items in `dev-baile/croilar/`
- [ ] PR-6g. Dagger module: `infrastructure/dagger/` with 6 functions
- [ ] PR-6h. R2 bucket `croilar-assets` + sharp 3-size WebP image pipeline
- [ ] Validate: all 14 workflows pass CI; 8 Komodo procedures are callable; 10 images publishable

## Phase 7: Polish + Landing the Plane (1 PR)
- [ ] PR-7a. Bilingual proofreading of all `packages/i18n/*` (per-persona EN + GA)
- [ ] PR-7b. Per-persona custom homepage hero (aleyum = music visualizer, cianfhoghlaim = curriculum map)
- [ ] PR-7c. Custom 404 per persona
- [ ] PR-7d. Lighthouse + a11y audit (navigation, snapshot modes)
- [ ] PR-7e. `bun run sync_agent_docs.sh`
- [ ] PR-7f. Archive `croilar-portfolio` openspec change, keep `croilar-revitalisation` as the canonical spec
- [ ] PR-7g. Landing the Plane: `git pull --rebase && git push && git status` clean

## Validation gates (every PR)

- [ ] `uv sync` exits 0
- [ ] `bun install` exits 0
- [ ] `bun run typecheck` exits 0 (all croilar workspaces)
- [ ] `uv run pytest croilar/tests/` exits 0
- [ ] `bunx --yes openspec validate croilar-revitalisation --strict` exits 0
- [ ] `docker compose -f <stack>/compose.yaml config --quiet` exits 0 for all 4 croilar stacks
- [ ] `ruff check croilar/ --select E,F,I,W` exits 0 (0 errors on new code)
