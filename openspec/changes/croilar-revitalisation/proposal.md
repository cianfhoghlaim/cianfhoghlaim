# croilar-revitalisation — Multi-persona portfolio platform

## Why

The current `croilar-portfolio` change scoped a **single-persona** portfolio site with 9 hardcoded routes and disconnected data pipelines. Since its Phase 1–3 implementation, the project vision has expanded to a **multi-persona platform** capable of hosting N distinct public identities (aleyum, cianfhoghlaim, and future personas) sharing essential infrastructure — data pipelines, BAML extraction, CocoIndex embeddings, Dagster orchestration, bilingual i18n, multi-tenant auth, and a self-hosted developer dashboard — while remaining the canonical showcase of the cianfhoghlaim monorepo's self-hosted developer experience.

The pivot is from "9 routes, one person" → "platform with N personas, shared infrastructure, extensible by design."

## What Changes

### 1. Multi-persona model

The subproject restructures from a flat 9-route TanStack Start app to a bun-workspace tree:

```
sruth/croilar/
├── apps/
│   ├── web/          ← TanStack Start (public persona router)
│   ├── portal/       ← Self-hosted platform dashboard (auth-gated)
│   └── storybook/    ← Optional UI explorer
├── packages/
│   ├── ui/           ← 60+ shadcn/ui components (lifted from eile/vibesdk)
│   ├── auth/         ← BetterAuth client + multi-tenant helpers
│   ├── db/           ← Convex + Hono + DuckDB + MotherDuck clients
│   ├── i18n/         ← EN/GA resource bundles per persona
│   ├── config/       ← Tailwind 4 theme tokens per persona
│   └── analytics/    ← PostHog, Sentry, Axiom wiring
├── hono-api/         ← Hono + BetterAuth server (oRPC routes)
├── convex/           ← Convex schema + 4-tenant org functions
├── pipelines/        ← Existing DLT sources (extended for personas)
├── dagster_assets/   ← Existing Dagster assets (extended per persona)
├── baml/             ← Existing BAML schemas (extended per persona)
├── notebooks/        ← Marimo notebooks (per-persona analytics)
...
```

### 2. Persona registry

A Zod-typed `personas/{_schema,_registry,aleyum,cianfhoghlaim}.ts` defines each persona as: id, slug, i18n labels, theme (mode + accent + palette), route list (with per-route loaders + icons), data sources (spotify, soundcloud, github, cv_pdfs, teaching_pdfs, ducklake_*), feature flags, Dagster asset group, and BAML schemas.

New personas are addable by creating one new file + registering in `_registry.ts`.

### 3. Full Convex + Hono + BetterAuth stack (per the consolidated docs)

- 4 self-hosted Docker services: `croilar-postgres` (dev), `croilar-hono-api`, `croilar-convex` (at `convex.croilar.cianfhoghlaim.ie`), `croilar-web`
- BetterAuth OIDC issuer hosted in Hono → JWT validated by Convex's `auth.config.ts`
- Multi-tenant orgs: `aleyum`, `cianfhoghlaim`, `croilar-admin`, `croilar-collab`
- Auth model: public pages are anonymous read. Portal is auth-gated. Collaborators are invited by email.
- All 3 schemas (better_auth_*, convex_*, ducklake_catalog_*) go to PlanetScale Postgres (aws-eu-west-2-1.pg.psdb.cloud:6432 for pgbouncer, :5432 direct for Convex)

### 4. Statistical analysis layer

- **DuckDB SSR loaders**: `createServerFn` wires every route to typed DuckDB queries (replacing all hardcoded `PLACEHOLDER_*` arrays)
- **Marimo notebooks**: new per-persona notebooks; embedded in portal via iframe to authenticated `marimo run` server; WASM-exported for the public `/data` route
- **MotherDuck Dive**: embedded iframe for collaborators; Dagster `motherduck_sync` asset copies tables on schedule
- **Curated dashboards**: Vega-Altair + Plotly components in `packages/ui/charts/` driven by Zod-validated chart specs from Marimo notebook extraction

### 5. Self-hosted developer portal (5 of 12 modules)

The existing `sruth/croilar/portal/` grows into the Croílár platform dashboard:
1. **Stacks** — Komodo API → 4+ croilar stacks health
2. **Data Pipelines** — Dagster GraphQL → 15 assets per persona
3. **Monitoring** — Prometheus + Grafana + Loki iframes
4. **MCP Gateway** — 13 MCP servers status
5. **Image Registry** — ghcr.io tags + multi-arch manifest

### 6. GitOps + CI/CD (Phase 4 from the original proposal)

- 7 Forgejo + 7 GitHub mirror workflows
- 8 Komodo procedures (stack-up/down/health, image-rebuild/publish, backup, gitops-fullstack)
- 5 new multi-arch images (croilar-web, -portal, -dagster, -marimo, -image-pipeline)
- 5 existing image multi-arch rebuilds
- SOPS encryption setup
- 20 new Infisical items in `dev-baile/sruth/croilar/`
- Dagger module with 6 functions

### 7. Games deferred to v2

The `/games` route for aleyum is omitted from v1.

## New Capabilities

| Capability | Type | Purpose |
|:--|:--|:--|
| `croilar-portfolio` | MODIFIED | Multi-persona model, theme tokens, server-function loaders |
| `croilar-data-engineering` | MODIFIED | Per-persona Dagster asset groups, per-persona BAML schemas |
| `croilar-cv-extraction` | MODIFIED | Add persona field to extraction records |
| `croilar-persona-registry` | NEW | Zod-typed persona config schema + lookup table |
| `croilar-self-hosted-portal` | NEW | 5-module platform dashboard (stacks, pipelines, monitoring, MCP, registry) |

## Impact

| Surface | Before | After |
|:--|:--|:--|
| Top-level subprojects | 4 | 4 |
| Bun workspaces (croilar) | 2 (root + portal) | 10 (apps/web, apps/portal, apps/storybook, packages/{ui,auth,db,i18n,config,analytics}, hono-api) |
| Python packages (croilar) | 1 (pipelines + notebooks) | 1 (unchanged — uv workspace member) |
| Personas | 1 (implicit "Cian") | 2 registered + N future |
| Routes per persona | 9 (flat) | 6–8 (per-persona config) |
| Auth model | None | Full multi-tenant BetterAuth OIDC |
| Portal modules | 0 (bare scaffold) | 5 (stacks, pipelines, monitoring, MCP, registry) |
| Docker Compose services | 2 (Dragonfly + Dagster) | 6 (+ supabase-db, hono-api, convex, web) |
| Statistical dashboards | 0 | 3 layers (SSR loaders, Marimo notebooks, MotherDuck Dive) |
| Convex tables | 0 | 4 tenant orgs + per-persona data |
| DLT pipelines per persona | 1 shared set | 2 persona-specific Dagster asset groups |
