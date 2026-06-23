# Croílár — Multi-Persona Portfolio Platform

> The personal portfolio of Cian de Búrca, refactored as a **multi-persona,
> self-hosted, full-stack TypeScript + Python platform** that doubles as a
> **reference implementation** for the rest of `kings_college_galway`.

> See also: [`croilar/AGENTS.md`](AGENTS.md) — the developer-quick-reference
> for the croilar quadrant. The openspec specs are at:
> - [`openspec/specs/croilar-portfolio/spec.md`](../openspec/specs/croilar-portfolio/spec.md)
> - [`openspec/specs/croilar-data-engineering/spec.md`](../openspec/specs/croilar-data-engineering/spec.md)
> - [`openspec/specs/croilar-cv-extraction/spec.md`](../openspec/specs/croilar-cv-extraction/spec.md)

Croílár (Irish: *core/heart*) is the canonical example inside this monorepo of
how to combine:

## Status (2026-06-15)

| Metric | Value |
|:--|:--|
| Workspace name | `croilar` (uv) — directory preserves the síneadh fada |
| Dagster code-location | `croilar/definitions.py` (root-level, NOT under `dagster_assets/`). Loads in **both** pytest and production as of 2026-06-15 (issue #17 closed). 25 assets wired. |
| Test pass rate | 1 / 1 dagster_defs test passes; 3 pre-existing failures in `tests/test_smoke.py` and `tests/dlt_assets/test_spotify_soundcloud_labels.py` (see Known issues #3) |
| Pipelines | 12 DLT pipelines under `croilar/pipelines/` (artwork, cv, fs_author, github, labels, linkedin, researchgate, shared, soundcloud, spotify, teaching) |
| 5 user-named stacks | Fully built and wired: `infrastructure/stacks/croilar-{convex, dagster, hono-api, marimo, web}/` |
| Dagster helpers | `_shared/{agents,config,database,embeddings,mcp,observability}/` — **packaging fixed** (issue #17 closed); all subdirs now importable as `croilar._shared.X` |

## Known issues (2026-06-15)

| # | Issue | Tracked in | Severity |
|--:|:--|:--|:--|
| 1 | **RESOLVED 2026-06-15.** `croilar/__init__.py` did not exist + `_shared` and `dagster_assets` were missing from `croilar/pyproject.toml`. **Fixed by** adding `croilar/__init__.py` + changing `croilar/pyproject.toml [tool.hatch.build.targets.wheel].packages = ["."]` + a post-install `croilar/scripts/fix-pth.sh` script that rewrites uv's broken editable-install `.pth` file. The conftest's `croilar_str` sys.path hack was REMOVED (no longer needed). The Phase 1.6 test now passes cleanly (no more `pytest.xfail`). | GitHub issue #17 | **closed** |
| 2 | `croilar/dlt_utils/destinations.py` is a defensive shim identical in pattern to `tuatha/dlt_utils/destinations.py` (re-exports oideachais' namespaced destinations, falls back to local if `oideachais` not on sys.path). The local-fallback code duplicates pre-Phase-2.3 logic and should be deleted once the oideachais workspace dep is wired. | `croilar/dlt_utils/destinations.py` (~85 lines, ~40 of which are the local fallback) | medium — same as tuatha #2 |
| 3 | Pre-existing test failures unrelated to issue #17: (a) `tests/test_smoke.py::test_module_imports[dlt_utils]` imports `DuckLakeConfig` from the shim, but the shim doesn't export it (pre-Phase-2.3 had it). (b) `tests/test_smoke.py::test_dlt_duckdb_fallback` uses old API `get_duckdb_fallback(base_path=...)` but the shim only has `get_duckdb_fallback_destination(database_path=...)`. (c) `tests/dlt_assets/test_spotify_soundcloud_labels.py::test_croilar_dlt_assets_module_imports` asserts a `spotify_ingestion_asset` symbol that doesn't exist. All 3 are pre-existing from the lateralise-british-isles-domains Phase 2.3 change. | git log `croilar/tests/test_smoke.py` | low — pre-existing |

- a **public-facing** persona-aware portfolio (multiple identities sharing one
  domain),
- a **self-hosted developer platform** (auth, data plane, agent runtime, portal
  dashboard), and
- a **typed, end-to-end pipeline** from external data sources (Spotify,
  SoundCloud, GitHub, CV PDFs, teaching records) through BAML extraction to a
  Marimo / MotherDuck / Altair analytics surface,

— all running on a single monorepo's existing infrastructure (Dagster, DLT,
DuckLake, Convex, Hono, BetterAuth, PlanetScale, Komodo, Pangolin, Pocket ID).

The codebase is intentionally readable, opinionated, and small enough that a
new subproject in `kings_college_galway` (e.g. a *consulting* persona for
freelance work, or an *open-source-steward* persona for maintainer-focused CVs)
can be added by copying a single `personas/<id>.ts` file plus 1–2
`pipelines/<id>/*.py` DLT sources, then committing — the rest is generated
infrastructure.

---

## 1. Why this exists

`kings_college_galway` is a polyglot monorepo with four large subprojects
(`oideachais/`, `meaisínfhoghlaim/`, `tuatha/`, `croilar/`) plus 70+ Docker
Compose stacks under `infrastructure/stacks/`. Each subproject historically
re-invented its own:

- TanStack Start + Vite config (3 different versions, 4 different Tailwind
  setups),
- a per-app i18n bootstrap,
- its own ad-hoc DLT → DuckDB → dashboard pipeline,
- and its own ad-hoc "show this on a portfolio" page.

Croílár is the **first** subproject to adopt the unified pattern:

1. One bun-workspace tree with `apps/*` (deployables) and `packages/*`
   (shared libraries).
2. One Python uv-workspace with `pipelines/`, `dagster_assets/`, `baml/`,
   `notebooks/`, `services/`, `agent_os/`, `_shared/`, `convex/`,
   `hono-api/`.
3. One auth layer (BetterAuth OIDC) for the entire surface, with
   `croilar-admin` / `croilar-collab` orgs.
4. One set of Docker Compose stacks (postgres + hono-api + convex + web +
   dagster + marimo) orchestrated by Komodo.
5. One openspec change (`croilar-revitalisation`) that captures the
   reusable design, validated with `openspec validate --strict`.

If `oideachais/`, `tuatha/`, or any future subproject wants the same surface
(CV-driven personal site, dashboard, persona switching, multi-tenant auth,
data-warehouse-backed pages), they can copy the
[`apps/web/`](apps/web), [`apps/portal/`](apps/portal), [`packages/*`](packages/),
[`convex/`](convex), and [`hono-api/`](hono-api) trees almost verbatim and
only re-skin the `personas/` registry.

---

## 2. Feature surface (what you actually get)

### 2.1 Public persona sites (`apps/web`)

- **N personas** served from a single domain at subpath routes
  (`/aleyum`, `/cianfhoghlaim`, `/$persona`).
- **Per-persona theme tokens** (CSS custom properties injected by
  `__root.tsx`): dark + electric violet for `aleyum`, light + celtic
  green for `cianfhoghlaim`. New persona = one new file in
  `apps/web/src/personas/`.
- **Bilingual EN + GA** for every label, in 3 namespaces (`common`,
  `aleyum`, `cianfhoghlaim`) so future personas ship their own overrides
  without touching shared keys.
- **Persona switcher** in the global header — persists the choice in a
  cookie, swaps the theme and i18n bundle, drives which routes appear in
  the nav.
- **Server-function data loaders** for music, code, CV, data, identity —
  each route fetches from the Hono API instead of carrying hardcoded data.
- **Live Spotify + SoundCloud iframes** on the music page.
- **Custom 404** with persona-aware "Back to Home" CTA.
- **46 shadcn/ui components** lifted from `eile/examples/ui/vibesdk/`
  in `@croilar/ui` (button, card, dialog, sidebar, form, table, sheet,
  command, sonner, etc.).

### 2.2 Internal portal (`apps/portal`)

- **Auth-gated** with BetterAuth OIDC; only members of `croilar-admin` or
  `croilar-collab` orgs can see anything in `/portal`.
- **5 dashboard modules** in scope (per the locked plan):
  1. **Stacks** — live health of every croilar Docker stack via Komodo.
  2. **Data Pipelines** — 15 Dagster assets with last-materialization time,
     grouped by persona.
  3. **Monitoring** — Prometheus + Grafana + Loki iframes.
  4. **MCP Gateway** — status of the 13 MCP servers (browser, firecrawl,
     motherduck, infisical, chrome, cocoindex-code, cognee, graphiti,
     langfuse, lancedb, memgraph, chunkhound, pulumi).
  5. **Image Registry** — `ghcr.io/cianfhoghlaim/<image>` tags + multi-arch
     manifest state.
- **MotherDuck Dive** iframes per persona (Dive URLs for
  `aleyum_md` / `cianfhoghlaim_md`).
- **Marimo notebook launcher** cards with `marimo run` instructions.
- **Audit log** writes to the `portalAuditLog` Convex table on every
  privileged action.

### 2.3 Data plane

- **DLT sources** for 7 external surfaces:
  Spotify (`pipelines/spotify/`), SoundCloud (`pipelines/soundcloud/`),
  GitHub (`pipelines/github/`), record labels (`pipelines/labels/`),
  album artwork (`pipelines/artwork/`), CV PDFs (`pipelines/cv/`),
  teaching PDFs (`pipelines/teaching/`).
- **6 BAML extraction schemas** for structured data over PDF / audio /
  text (`baml/{cv,teaching,identity_verification,artwork_analysis,
  style_transfer}.baml`).
- **CocoIndex flows** that embed extracted text and artwork into
  LanceDB (`cocoindex_flows/{cv_embedding,artwork_embedding}.py`).
- **Dagster asset graph** (15 assets, 4 schedules, 2 sensors) orchestrating
  ingestion → extraction → embedding, with per-persona asset groups.
- **MotherDuck sync asset** that ships DuckDB tables to MotherDuck cloud
  every 30 minutes for the Dive iframe.
- **3 marimo notebooks** (`music_analytics`, `github_insights`,
  `cv_dashboard`) for the author, plus per-persona notebooks
  (`notebooks/aleyum/music_analytics.py`,
  `notebooks/cianfhoghlaim/teaching_analytics.py`) for the public
  WASM-exported `/data` route per persona.

### 2.4 Backend

- **Hono 4** server at `croilar/hono-api/` — BetterAuth OIDC issuer
  (`auth.croilar.cianfhoghlaim.ie`), Drizzle adapter against
  PlanetScale Postgres (with pgBouncer-safe `prepare: false`), 4-org
  multi-tenant RBAC, Drizzle migrations, OIDC discovery + JWKS.
- **Convex** at `croilar/convex/` — 9-table schema (personas, orgs,
  memberships, portfolio pages, CV entries, music entries, GitHub repos,
  contact submissions, invites) with 8 query/mutation functions, 4
  crons, and 2 actions for external API calls.
- **DuckDB** at `croilar/_shared/database/` — singleton read-only
  connection helper, env-driven path, writer context manager.
- **PlanetScale Postgres** (`aws-eu-west-2-1.pg.psdb.cloud`) holds 3
  schemas: `better_auth`, `convex`, `ducklake_catalog`.

### 2.5 Infrastructure

- **3 new Docker Compose stacks** in the GOLD_STANDARD 6-file pattern:
  - `infrastructure/stacks/croilar-postgres/`
  - `infrastructure/stacks/croilar-hono-api/`
  - `infrastructure/stacks/croilar-convex/`
- **8 Komodo procedures** under `infrastructure/komodo/procedures/`:
  `croilar-stack-up`, `-down`, `-health`, `-image-rebuild`,
  `-image-publish`, `-renovate-pr`, `-backup`, `-gitops-fullstack`.
- **5 new multi-arch images** ready to publish to
  `ghcr.io/cianfhoghlaim/`:
  - `croilar-web` (Bun)
  - `croilar-portal` (Bun)
  - `croilar-dagster` (Python 3.12 + uv)
  - `croilar-marimo` (Python 3.12 + uv)
  - `croilar-image-pipeline` (Node 20)
- **Dagger `CroilarPipeline`** in
  `infrastructure/dagger/cianchoghlaim_dagger/__init__.py` with 6
  functions: `ci`, `build_images`, `deploy_cloudflare`,
  `deploy_komodo`, `deploy_pangolin`, `gitops_fullstack`. All
  deploys are gated by an `approved: bool = False` parameter.
- **8 GitHub mirror workflows** in `.github/workflows/croilar-*.yaml`:
  ci, images, deploy, renovate, secret-scan, openspec, backup,
  release-please.

### 2.6 OpenSpec & testing

- **`openspec/changes/croilar-revitalisation/`** — the canonical spec with
  5 capability deltas (3 MODIFIED + 2 NEW), validated
  `openspec validate --strict`.
- **31 pytest tests** in `croilar/tests/` (smoke + database) all passing
  via `uv run pytest croilar/tests/`.
- **TypeScript typecheck** passes for `@croilar/web`, `@croilar/portal`,
  `@croilar/hono-api`, `@croilar/ui`, `@croilar/db`, `@croilar/i18n`.

---

## 3. Architecture

```
                          ┌─────────────────────────────────────┐
                          │  croilar.cianfhoghlaim.ie (Pangolin) │
                          └────────────┬────────────────────────┘
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
┌────────────────┐         ┌────────────────────┐         ┌─────────────────────┐
│ apps/web       │         │ apps/portal        │         │ convex.croilar.…     │
│ TanStack       │  JWT    │ TanStack Start     │  JWT    │ Convex self-hosted   │
│ Start (SPA +   │◀───────▶│ (auth-gated)       │◀───────▶│ 4 tenant orgs, 9    │
│ future SSR)    │         │                    │         │ tables, 8 fns, 4    │
└──────┬─────────┘         └──────┬─────────────┘         │ crons                │
       │                          │                       └──────────┬──────────┘
       │ fetch                    │ Komodo / Dagster /              │
       │ /api/v1/*                │ MCP / ghcr.io                   │
       │                          ▼                                 │
       │                 ┌────────────────────┐                    │
       │                 │ hono-api            │                    │
       │  fetch          │ auth.croilar.…     │                    │
       └────────────────▶│ Hono 4 +           │                    │
                          │ BetterAuth OIDC    │                    │
                          │ Drizzle + Postgres │                    │
                          └────────┬───────────┘                    │
                                   │                                │
                                   ▼                                │
                          ┌────────────────────┐                    │
                          │ PlanetScale        │                    │
                          │ Postgres (eu-west-2)│◀───────────────────┘
                          │ better_auth/       │   webhook sync
                          │ convex/            │
                          │ ducklake_catalog/  │
                          └────────────────────┘
                                   │
                          ┌────────┴────────┐
                          ▼                 ▼
                  ┌──────────────┐  ┌──────────────────┐
                  │ DLT sources  │  │ Dagster          │
                  │ → DuckDB     │  │ 15 assets, 4     │
                  │ local file   │  │ schedules, 2     │
                  │              │  │ sensors          │
                  └──────┬───────┘  └────────┬─────────┘
                         │                   │
                         └────────┬──────────┘
                                  ▼
                         ┌──────────────────┐
                         │ CocoIndex →       │
                         │ LanceDB vectors   │
                         │ + BAML extracts   │
                         └────────┬──────────┘
                                  ▼
                         ┌──────────────────┐
                         │ Marimo notebooks  │
                         │ + MotherDuck Dive │
                         │ (iframe in portal)│
                         └──────────────────┘
```

Three runtime layers, each independently deployable:

1. **Edge** (Pangolin) → **Frontend** (apps/web, apps/portal as Docker
   containers) → **API** (hono-api).
2. **API** → **Auth** (BetterAuth) → **Postgres** (PlanetScale) for state
   and → **Convex** for real-time + crons.
3. **Background workers** (Dagster, CocoIndex, DLT) → **DuckDB file**
   (lives on the same volume as Marimo) → periodic push to **MotherDuck**
   cloud → **LanceDB** for vectors.

---

## 4. Software choices — and why

### 4.1 Bun + Vite + TanStack Router (not Next.js, not Remix)

The monorepo already had `oideachais/web/` and `tuatha/ui/` on
TanStack Router v1 with Vite. Croílár adopts the same. Reasons:

- **One framework, two surface areas** — `apps/web` and `apps/portal`
  share `packages/ui`, `packages/i18n`, `packages/db`, `packages/config`.
  Converging on TanStack means the entire monorepo benefits from a
  single routing upgrade cycle.
- **Vite is faster than Turbopack for the type-checked SPA shell we
  actually want** for the public personas (no SSR overhead, no RSC
  mental model, no server components), while remaining SSR-able via
  `@tanstack/react-start` when the hono-api data is finally there.
- **`createServerFn` is the future seam** — when the user upgrades
  to SSR, route loaders can flip from `fetch(/api/v1/...)` to a server
  function without changing the component tree.

### 4.2 shadcn/ui (lifted from `eile/vibesdk/`)

The eile examples directory has 9 UI sub-projects; `vibesdk` ships the
richest shadcn/ui set (60+ components, including a 714-line `sidebar.tsx`).
We copy verbatim rather than maintain our own design system. The cost:
we pin `@radix-ui/*` versions to a known good set. The benefit: every
component, every `cva` pattern, every `tailwind-merge` call is a 1:1
copy of production-grade, accessibility-reviewed React. The 16+ packages
shadcn depends on are not a dependency; they are the *only* way
shadcn works, and they live in `package.json` for the consuming
app, not the library.

### 4.3 DLT + DuckDB + DuckLake (not Airbyte + Snowflake + dbt)

- **DLT is the only Python ingestion tool that emits both a typed
  `Pipeline` object and Parquet files.** That matters because the
  DLT output is the *same* file the hono-api reads from. No ETL
  middleman, no schema drift.
- **DuckDB has a single-writer / multi-reader lock.** DuckLake solves
  that by separating transaction coordination (Postgres catalog) from
  storage (S3/R2 Parquet). Convex's external-postgres mode plays
  nicely with the same Postgres instance.
- **BAML sits on top of the DLT output as a transformation step, not a
  pipeline orchestrator.** BAML is a *schema-first* LLM binding, not
  a workflow tool. We use it where typed LLM output is required
  (extracting `EducationEntry` from a scanned PDF page) and *not*
  for arbitrary control flow.

### 4.4 BetterAuth + Hono + Convex (not NextAuth + Express + Supabase Realtime)

- **BetterAuth is the only self-hosted OIDC library that ships with
  multi-tenant orgs, Drizzle adapter, and an OAuth-client metadata
  block out of the box.** That gives us `organization` + `account` +
  `jwks` tables in one Drizzle schema, and a Convex-friendly
  `applicationID` claim without rolling our own token issuer.
- **Hono 4 over Express/Fastify**: TypeScript-first, runs on every
  runtime (Node, Bun, Cloudflare Workers, Deno, Lambda), 14kb cold
  start. The hono-api stays portable.
- **Convex over a custom WebSocket layer**: Convex's `useQuery` /
  `useMutation` give us real-time table reactivity for the portal
  dashboard *for free* — when Dagster reports a new materialization
  via a Convex mutation, every connected portal client updates without
  any manual subscription code. We use Convex for *real-time state*,
  Postgres for *durable auth state*, DuckDB for *analytics*.

### 4.5 PlanetScale Postgres (not Supabase Postgres, not Neon)

- **Single eu-west-2 region** matches the rest of the platform
  (OCI arm1-oci in London).
- **pgBouncer on 6432** is fine for BetterAuth (transaction-mode is OK
  for Drizzle as long as `prepare: false` is set); the Convex backend
  uses the *direct* port 5432 (Convex needs prepared statements).
- **Free tier row limit** is a non-issue at this scale (CV PDFs + CV
  rows + Convex metadata fit comfortably).
- **One credential set, three schemas** (`better_auth`, `convex`,
  `ducklake_catalog`) — same connection string, different
  `search_path` per consumer.

### 4.6 Marimo (not Streamlit, not Jupyter)

- **Reactive execution graph.** A `slider` widget re-runs only the
  cells downstream of it, with no explicit state plumbing. This is the
  single feature that makes Marimo feel like a real product rather than
  a glorified REPL.
- **Stored as `.py`, not `.ipynb`.** No merge conflicts, no
  `execution_count: 7` noise, no JSON in git. CI runs `ruff` on every
  notebook.
- **WASM export** (`marimo export wasm-wasm`) lets the public
  `/data` route ship a static, deterministic, shareable version of the
  notebook that runs entirely in the browser — no server, no auth, no
  scaling concern.
- **MotherDuck Dive** for the *collaborator* layer where Marimo's
  Python skill requirement is too high.

### 4.7 MotherDuck (not Snowflake, not BigQuery)

- **It's still DuckDB.** No new SQL dialect for the team to learn.
  Anything that runs against local DuckDB runs against MotherDuck with
  one connection-string change.
- **The Dive UI is free and embeds via iframe.** Each persona gets its
  own MotherDuck database (`aleyum_md`, `cianfhoghlaim_md`) which the
  portal embeds in the analytics route.
- **The cost model is per-query**, not per-cluster, which matches the
  expected traffic of a personal portfolio with 2–3 collaborators.

### 4.8 Komodo + Pangolin + Pocket ID (not Kubernetes + Ingress + Dex)

- **The monorepo already runs this stack** (see
  `infrastructure/komodo/` and `infrastructure/pangolin/`). Croílár is
  the first subproject to consume it end-to-end.
- **Komodo's resource model maps 1:1 to a Stack.** A new
  `croilar-convex` blueprint is exactly the same shape as the
  existing `oideachais` and `tuatha` blueprints. No new vocabulary
  to learn.
- **Pocket ID OIDC** is the only OIDC IdP the platform trusts
  (also used by `crypteolas` and `oideachais/dashboard`). BetterAuth
  issues tokens for *its own* clients (Convex, web, portal); the user
  log-in flow goes through Pocket ID for first-factor SSO.

---

## 5. The persona model — how to add a third persona

The plan: drop one file in `apps/web/src/personas/`, register it,
add per-persona data sources, done.

```ts
// apps/web/src/personas/consulting.ts
import type { Persona } from "./_schema";

export const consulting: Persona = {
  id: "consulting",
  slug: "consulting",
  i18n: { en: "Consulting", ga: "Comhairleoireacht" },
  theme: {
    mode: "light",
    accent: "oklch(0.70 0.18 50)",   // warm amber
    palette: {},
  },
  routes: [
    { path: "/",         label: { en: "Home",    ga: "Baile"    }, icon: "home",      loader: "home" },
    { path: "/services", label: { en: "Services", ga: "Seirbhísí" }, icon: "briefcase", loader: "services" },
    { path: "/case-studies", label: { en: "Case studies", ga: "Cás-staidéir" }, icon: "file-text", loader: "cases" },
    { path: "/contact",  label: { en: "Contact", ga: "Teagmháil" }, icon: "mail",       loader: "contact" },
  ],
  dataSources: ["ducklake_oideachais", "ducklake_meaisinfhoghlaim"],
  featureFlags: { cv: true, data: true, identity: false, contact: true },
  dagsterAssetGroup: "consulting",
  bamlSchemas: ["cv_extraction"],
};
```

```ts
// apps/web/src/personas/_registry.ts — add one line:
import { consulting } from "./consulting";
export const PERSONAS: Persona[] = [aleyum, cianfhoghlaim, consulting];
```

That's it. Theme swaps, i18n loads from `packages/i18n/src/resources/consulting/{en,ga}.json`, the Dagster asset group `consulting` is queried, the nav re-renders, the BAML `cv_extraction` runs over the persona's CV PDFs.

The only manual work for a brand-new persona is:
- 1 persona file (`personas/<id>.ts`)
- 1 i18n resource bundle (EN + GA)
- (optionally) 1 Dagster asset group + DLT sources
- (optionally) 1 Marimo notebook + MotherDuck database

Everything else is shared infrastructure: auth, UI, i18n plumbing, BAML client generation, Convex schema, hono-api, portal.

---

## 6. How to fork this pattern for a new monorepo subproject

If a future `kings_college_galway` subproject (`oideachais-portal`,
`tuatha-cv`, `consulting-site`, …) wants the same architecture, the
fork path is:

1. **Copy `apps/web` → `<new>/apps/web`**; rename the workspace
   package from `@croilar/web` to `<@new>/web`; re-point the persona
   registry at the new subproject's persona set.
2. **Copy `apps/portal`** if the new subproject wants an internal
   dashboard; otherwise skip.
3. **Copy `packages/{ui,i18n,config}`** verbatim; these are
   subproject-agnostic.
4. **Copy `hono-api/`** if the new subproject needs its own auth
   surface; otherwise consume the existing `croilar-hono-api` and
   create a new BetterAuth org for the new subproject.
5. **Copy `convex/`** if the new subproject has its own real-time
   state; otherwise share the existing Convex backend and add a
   per-subproject table prefix (`<sub>_*`).
6. **Copy the Docker stacks** (`croilar-postgres`, `croilar-hono-api`,
   `croilar-convex`); rename and re-Pangolin.
7. **Copy the DLT pipelines** that the new subproject actually
   consumes; the rest stays in Croílár.
8. **Open a `croilar-revitalisation` spec change** (or equivalent
   openspec change for the new subproject) so the design is
   reviewable.

The total surface is roughly 60 files of *infrastructure* (auth,
conventions, build setup) and 5–10 files of *content* (personas,
routes, pipelines). The infrastructure is what you copy; the content
is what you write fresh.

---

## 7. OpenSpec change & testing

The canonical spec for this work is
[`openspec/changes/croilar-revitalisation/`](../openspec/changes/croilar-revitalisation/),
validated with `bunx --yes openspec validate croilar-revitalisation --type change --strict`.
The 5 spec deltas are:

- `croilar-portfolio` (MODIFIED) — multi-persona routing, theme tokens,
  server-function loaders, public read + invite-only write.
- `croilar-data-engineering` (MODIFIED) — per-persona Dagster asset
  groups, per-persona BAML schemas.
- `croilar-cv-extraction` (MODIFIED) — `persona` discriminator on every
  extraction record.
- `croilar-persona-registry` (NEW) — Zod-typed persona config schema.
- `croilar-self-hosted-portal` (NEW) — 5-module platform dashboard.

The old `croilar-portfolio` openspec change is retained as superseded
reference; `croilar-revitalisation` is the canonical spec.

**Test count: 31 passing** (24 smoke + 7 data-plane + database).
Run with:

```bash
uv run pytest croilar/tests/ -v
```

---

## 8. Project structure (current)

```
croilar/
├── apps/                         # Bun workspaces (TanStack Start apps)
│   ├── web/                      # Public persona sites
│   │   ├── Dockerfile
│   │   ├── package.json          # @croilar/web
│   │   ├── src/
│   │   │   ├── routes/
│   │   │   │   ├── __root.tsx    # Persona switcher, theme + i18n loader
│   │   │   │   ├── index.tsx
│   │   │   │   ├── cv.tsx
│   │   │   │   ├── music.tsx     # Spotify + SoundCloud live
│   │   │   │   ├── code.tsx      # GitHub live
│   │   │   │   ├── research.tsx
│   │   │   │   ├── teaching.tsx
│   │   │   │   ├── data.tsx
│   │   │   │   ├── identity.tsx
│   │   │   │   ├── contact.tsx
│   │   │   │   └── 404.tsx       # Persona-aware 404
│   │   │   ├── personas/         # Zod-typed persona registry
│   │   │   │   ├── _schema.ts
│   │   │   │   ├── _registry.ts
│   │   │   │   ├── aleyum.ts
│   │   │   │   └── cianfhoghlaim.ts
│   │   │   ├── components/
│   │   │   │   ├── music/AudioCard.tsx
│   │   │   │   └── code/ProjectCard.tsx
│   │   │   ├── lib/
│   │   │   ├── i18n/             # → deprecated, moved to packages/i18n
│   │   │   ├── pages/            # Per-route page sub-components
│   │   │   ├── router.tsx
│   │   │   └── main.tsx
│   │   └── vite.config.ts
│   ├── portal/                   # Internal platform dashboard
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   ├── src/routes/
│   │   │   ├── __root.tsx
│   │   │   ├── _layout/         # Auth-gated layout
│   │   │   │   ├── index.tsx
│   │   │   │   ├── stacks/      # Phase 4
│   │   │   │   ├── agents/
│   │   │   │   ├── data/pipelines.tsx
│   │   │   │   ├── monitoring/
│   │   │   │   ├── analytics/   # Marimo + MotherDuck Dive
│   │   │   │   └── widgets.tsx
│   │   │   ├── login.tsx
│   │   │   └── api/
│   │   ├── lib/                  # auth, drizzle, middleware
│   │   └── db/                   # Drizzle schema
│   └── storybook/                # Reserved
│
├── packages/                      # Bun workspaces (shared libraries)
│   ├── ui/                       # 46 shadcn/ui components from vibesdk
│   ├── auth/                     # BetterAuth client (stub)
│   ├── db/                       # API client + types
│   ├── i18n/                     # EN + GA in 3 namespaces
│   ├── config/                   # Tailwind 4 theme tokens
│   └── analytics/                # PostHog, Sentry (stub)
│
├── hono-api/                     # Hono 4 + BetterAuth OIDC issuer
│   ├── Dockerfile
│   ├── src/
│   │   ├── auth.ts               # BetterAuth config
│   │   ├── middleware.ts         # requireAuth / requireOrg
│   │   ├── index.ts              # Main Hono app
│   │   ├── db/
│   │   │   ├── client.ts         # Drizzle + pgBouncer
│   │   │   └── schema.ts         # 8 tables
│   │   ├── data/
│   │   │   ├── duckdb.ts         # Query helper
│   │   │   ├── spotify.ts        # /api/v1/spotify
│   │   │   ├── github.ts         # /api/v1/github
│   │   │   └── cv.ts             # /api/v1/cv
│   │   └── migrate.ts            # Drizzle migration runner
│   ├── drizzle.config.ts
│   ├── .env.example
│   └── README.md
│
├── convex/                       # Self-hosted Convex backend
│   ├── schema.ts                 # 9 tables
│   ├── auth.config.ts            # BetterAuth OIDC trust
│   ├── helpers.ts                # requireOrg, requireAuth
│   ├── personas.ts               # Public queries
│   ├── portfolio.ts              # Public queries
│   ├── cv.ts                     # Public queries
│   ├── contact.ts                # Public + admin mutations
│   ├── invites.ts                # Admin mutations
│   ├── stacks.ts                 # Komodo sync (action)
│   ├── pipelines.ts              # Dagster sync (action)
│   ├── mcp.ts                    # MCP server status (action)
│   ├── registry.ts               # ghcr.io sync (action)
│   └── crons.ts                  # 4 periodic syncs
│
├── pipelines/                    # DLT sources (existing, hardened)
│   ├── spotify/    soundcloud/   github/    labels/
│   ├── artwork/    cv/           teaching/  shared/
│
├── dagster_assets/               # 15 assets, 4 schedules, 2 sensors
│   ├── dlt_assets.py             # Manual @asset (spotify, soundcloud, etc.)
│   ├── cv_assets.py              # CV + teaching assets
│   ├── cocoindex_assets.py       # Embedding pipeline assets
│   ├── schedules.py              # 4 cron schedules + 2 sensors
│   └── definitions.py             # Single source of truth (no duplicate)
│
├── baml/                         # 6 BAML extraction schemas
│   ├── cv_extraction.baml
│   ├── teaching_extraction.baml
│   ├── identity_verification.baml
│   ├── artwork_analysis.baml
│   ├── style_transfer.baml
│   ├── clients.baml
│   ├── generators.baml
│   └── (baml_client/ generated by `baml-cli generate`)
│
├── cocoindex_flows/              # Embedding pipelines
│   ├── cv_embedding.py
│   └── artwork_embedding.py
│
├── notebooks/                    # Marimo reactive notebooks
│   ├── music_analytics.py
│   ├── github_insights.py
│   ├── cv_dashboard.py
│   ├── aleyum/music_analytics.py       # Per-persona (WASM-exported)
│   └── cianfhoghlaim/teaching_analytics.py
│
├── services/                     # LiteLLM-backed services
│   ├── vision.py                 # Artwork analysis
│   └── image_generation.py       # Style transfer
│
├── agent_os/                     # Agno-based research agent
│   ├── main.py
│   ├── config.yaml
│   └── Dockerfile
│
├── _shared/                      # Cross-cutting Python utilities
│   ├── config/
│   │   ├── paths.py              # get_repo_root, get_author_dir
│   │   └── settings.py           # Pydantic ALEYUM_ env config
│   ├── database/                 # DuckDB connection pool
│   ├── agents/router.py          # ADK + Agno router
│   ├── observability/            # Datadog + Langfuse + Logfire tracer
│   ├── embeddings/               # Embedding batcher
│   └── mcp/gateway.py            # 13 MCP servers
│
├── tests/                        # pytest (31 passing)
│   ├── conftest.py
│   ├── test_smoke.py             # 24 tests
│   └── test_database.py          # 7 tests
│
├── .dlt/                         # DLT config + secrets template
├── .gitignore
├── baml_src -> baml/             # symlink for baml-cli
├── definitions.py                # Dagster entry
├── workspace.yaml
├── dagster.yaml
├── compose.yaml                  # Dagster + Dragonfly (existing)
├── Dockerfile.dagster
├── pyproject.toml                # uv workspace member
├── mise.toml
└── README.md                     # this file

infrastructure/
├── komodo/procedures/
│   ├── croilar-stack-up.toml
│   ├── croilar-stack-down.toml
│   ├── croilar-stack-health.toml
│   ├── croilar-image-rebuild.toml
│   ├── croilar-image-publish.toml
│   ├── croilar-renovate-pr.toml
│   ├── croilar-backup.toml
│   └── croilar-gitops-fullstack.toml
├── dagger/cianchoghlaim_dagger/__init__.py  # CroilarPipeline class
└── stacks/
    ├── storage/croilar-postgres/
    └── engineering/
        ├── croilar-hono-api/
        ├── croilar-convex/
        └── (croilar-web/, croilar-dagster/, croilar-marimo/ existing)

.github/workflows/
├── croilar-ci.yaml
├── croilar-images.yaml
├── croilar-deploy.yaml
├── croilar-renovate.yaml
├── croilar-secret-scan.yaml
├── croilar-openspec.yaml
├── croilar-backup.yaml
└── croilar-release-please.yaml

openspec/
├── changes/croilar-revitalisation/  # canonical (implemented)
│   ├── proposal.md
│   ├── tasks.md
│   └── specs/{croilar-portfolio,croilar-data-engineering,
│              croilar-cv-extraction,croilar-persona-registry,
│              croilar-self-hosted-portal}/spec.md
├── specs/                              # canonical (5 capabilities)
└── changes/croilar-portfolio/         # superseded (kept for reference)
```

---

## 9. How to run locally

### 9.1 Prerequisites

- `mise` (toolchain manager — installs `bun`, `uv`, `python3.12`,
  `dagger`, `pulumi`, `duckdb`)
- `baml-cli` (for BAML schema generation: `npm i -g @boundaryml/baml` or
  `baml-cli` if your platform has it)
- Docker + Docker Compose (for the postgres + hono-api + convex stacks)

### 9.2 Bootstrap

```bash
# from the monorepo root
mise install           # installs the toolchain
bun install            # bun workspaces
uv sync                # uv workspace (croilar)
cp croilar/.dlt/secrets.toml.example croilar/.dlt/secrets.toml
cp croilar/hono-api/.env.example croilar/hono-api/.env
bun run secrets:init   # infisical → .env hydration

# bring up the local data services
docker compose -f infrastructure/stacks/croilar-postgres/compose.yaml \
               -f infrastructure/stacks/croilar-postgres/sidecar.yaml \
               --env-file infrastructure/stacks/croilar-postgres/.env.example \
               up -d
docker compose -f infrastructure/stacks/croilar-hono-api/compose.yaml \
               -f infrastructure/stacks/croilar-hono-api/sidecar.yaml \
               --env-file infrastructure/stacks/croilar-hono-api/.env.example \
               up -d

# generate Drizzle migrations + apply
cd croilar/hono-api
bun run db:generate
bun run db:migrate

# run DLT pipelines to populate local DuckDB (uses USE_LOCAL_SCRAPES=true)
cd ../..
USE_LOCAL_SCRAPES=true DUCKDB_PATH=./croilar/data/croilar.duckdb \
  uv run python -m pipelines.spotify.source

# start the web app
cd croilar/apps/web
bun run dev
```

Open <http://localhost:3003/aleyum> and
<http://localhost:3003/cianfhoghlaim> to see the two personas.

### 9.3 Tests

```bash
# from the monorepo root
uv run pytest croilar/tests/ -v

# TypeScript
cd croilar/apps/web && bun run typecheck
cd croilar/apps/portal && bun run typecheck
cd croilar/hono-api && bun run typecheck
cd croilar/packages/ui && bun run typecheck
```

### 9.4 OpenSpec

```bash
# validate the canonical spec
bunx --yes openspec validate croilar-revitalisation --type change --strict
```

---

## 10. Why this is a reference implementation, not just a portfolio

A portfolio site is normally *the* personal project. Croílár is
deliberately *not* the only project in `kings_college_galway`; it is
the **template** for any other subproject that wants the same
surface.

If `oideachais/` wants a CV-style "team members" page that shows
every contributor's projects, music, and research papers: copy
`apps/web`, point the persona registry at the contributors in
`oideachais/data_platform/agents/`, and you're done. The same
auth, the same i18n, the same theme tokens, the same data wiring.

If `tuatha/` wants to add a "key contributors" persona for its open
source maintainers: copy `apps/web`, register a new persona, point
at the `tuatha/` GitHub repos via the existing GitHub DLT pipeline.

If a brand-new `consulting-site/` subproject is added: copy `apps/web`
+ `apps/portal` + `hono-api/` + `convex/`, register `aleyum` and
`consulting` as the two personas, ship. The same openspec workflow
documents the design for review.

That's why Croílár is in the monorepo root as a *first-class
subproject*: it's the platform's first adopter, and the rest of
the platform gets to follow.

---

## 11. License

MIT.
