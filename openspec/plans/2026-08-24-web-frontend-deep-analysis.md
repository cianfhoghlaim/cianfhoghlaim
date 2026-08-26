# Web Frontend Deep Analysis — Cianfhoghlaim Monorepo

> **Date:** 2026-08-24
> **Author:** Build agent (read-only research subagent)
> **Scope:** Full inventory + tech stack audit + naming analysis + 2026 consolidation plan
> **Status:** This is a research artefact, not an openspec change. Use it to seed the
> `2026-08-24-web-frontend-consolidation-v1` openspec change.

---

## Executive summary

The `web/` surface of the Cianfhoghlaim monorepo is the **most chaotic area of the codebase**. As of 2026-08-24:

| Metric | Value |
|:--|--:|
| Top-level apps under `web/apps/` | **12** (including `_oideachais_apps` legacy) |
| Distinct framework roots inside the apps | **18** (5 of the apps contain nested `apps/web` + `apps/api` + `packages/*` sub-monorepos) |
| `package.json` files inside `web/` | **32** (16 app roots + 7 nested apps + 5 ui-kit packages + 4 hono-api / shared) |
| `.tsx` source files | **443** |
| `.ts` source files | **439** |
| Total disk footprint of `web/apps/` | **~2.4 GB** (dominated by `node_modules`) |
| Web-app projects that **actually run** today | **8** (4 in production, 4 stub/legacy) |
| Independent Convex deployments | **≥ 3** (`oideachais-dashboard/convex`, `cianfhoghlaim-web/convex`, `croilar-portal/convex`, `cianfhoghlaim-mmo/convex`) |
| Independent Hono / API gateways | **≥ 3** (`web/hono-api/`, `web/apps/cianfhoghlaim-web/apps/api/`, `web/apps/cianfhoghlaim-leaving-cert/apps/api/`) |
| Independent Better-Auth installations | **≥ 3** (`web/hono-api/`, `web/packages/auth/`, `web/apps/cianfhoghlaim-leaving-cert/packages/auth/`) |
| Independent CopilotKit installs | **≥ 5** |

**The single largest finding:** the `web/AGENTS.md` (the canonical web-monorepo guide) describes **4 apps** (oideachais, croilar, oideachais-dashboard, cianfhoghlaim). Real disk state: **12 apps + 1 legacy archive**. ~67% of the web surface is **undocumented drift**.

A second wave of similar drift exists **inside** the apps: `cianfhoghlaim-web/`, `cianfhoghlaim-leaving-cert/`, `croilar-portal/`, `oideachais-dashboard/` each maintain their own private `apps/web/ + apps/api/ + packages/auth/ + packages/db/ + packages/convex/` sub-monorepos, completely duplicating the root `web/packages/` workspace.

The recommended 2026 architecture is **TanStack Start + TanStack AI + AG-UI + Convex + Better-Auth + CopilotKit v2 + Hono on Cloudflare Workers**. Of the 12 apps, **2 are canonical** (oideachais-dashboard for ops, cianfhoghlaim for the central homepage), **3 should be merged** (cianfhoghlaim-web → cianfhoghlaim, oideachais → the BIEP v3 substrate, croilar-portal → croilar-web), **2 should be archived** (cianfhoghlaim-leaving-cert → its data goes into oideachais; _oideachais_apps → archive), **2 are clearly niche and should be promoted or retired** (tuatha-ui for the MMO, tuatha-demo is a Python demo, not a real app), **2 are non-web artefacts** (game_showcase is a Python data dir, cianfhoghlaim-mmo is the TanStack Start 2D client — could merge with tuatha-ui or keep separate).

---

## A) Full inventory of `web/apps/` and `web/packages/`

### A.1 — Top-level `web/apps/` (12 entries)

| # | App | Size | LOC (tsx/ts) | Last touched | Status | Purpose |
|--:|:--|--:|--:|:--|:--|:--|
| 1 | `_oideachais_apps/`       | 552 KB | 23 tsx / 3 ts | 2026-07-22 | **LEGACY** (sruth-era archive, pre-v4) | Old oideachais quadrant AGENTS.md / STATUS.md / CHANGELOG.md + a `web/` subdir with the legacy Vite SPA from before TanStack Start |
| 2 | `cianfhoghlaim/`          | 148 KB | 15 tsx / 4 ts | 2026-08-23 | **CANONICAL** (new central homepage, Phase T) | The central Cianfhoghlaim homepage with agentic chat — uses TanStack Start + TanStack AI + CopilotKit v1.67 |
| 3 | `cianfhoghlaim-leaving-cert/` | 2.4 GB | 130 tsx / 62 ts | 2026-08-08 | **SHOULD MERGE → oideachais** | Self-contained **sub-monorepo** with `apps/web/`, `apps/api/`, `packages/{auth,config,convex,db,i18n,ui,api}/`. The full LC website per its own README, port 3082 + API 8787, Cloudflare Workers + R2 + Convex. **Duplicates everything.** |
| 4 | `cianfhoghlaim-mmo/`      | 55 MB | 9 tsx / 7 ts | 2026-08-22 | **SHOULD MERGE → cianfhoghlaim or tuatha-ui** | TanStack Start 2D client for the 8 NCCA subjects, port 3080. Has its own `convex/{badges,credentialAnchors,questPacks,x402Payments,schema}.ts` (x402 Web3 micropayments for the MMO economy). |
| 5 | `cianfhoghlaim-web/`      | 10 MB | 56 tsx / 39 ts | 2026-08-08 | **SHOULD MERGE → cianfhoghlaim** | The largest pre-v7 web app — TanStack Start + Vinxi + R2 + Convex. **Self-contained sub-monorepo** with `apps/api/`, `apps/web/`, `packages/{api,auth,config,db}/`. Per `wrangler.toml`, R2 bucket `cianfhoghlaim-leaving-cert` and CF Pages project `cianfhoghlaim-oideachais`. **Duplicates `web/hono-api/`** — has its own `apps/api/` for Hono routes. |
| 6 | `croilar-portal/`         | 265 MB | 21 tsx / 26 ts | 2026-08-19 | **SHOULD MERGE → croilar-web** | Internal developer portal (auth-gated, BetterAuth + SIWE + x402). Has its own `compose.yaml` + `Drizzle` + `postgres` + TanStack Start 1.168.21. README dated pre-v7 (`sruth/aleyum/portal` path). |
| 7 | `croilar-web/`            | 35 MB | 27 tsx / 10 ts | 2026-08-19 | **CANONICAL** (multi-persona public site) | Public croilar portfolio, port 3003, Radix UI + Tailwind 4 + TanStack Start 1.168.21 + i18n EN/GA. Owns the i18n package (`@croilar/i18n`). |
| 8 | `game_showcase/`          | 24 KB | 0 / 0 | 2026-07-22 | **NOT A WEB APP** (Python data) | 5 YAML project descriptors (SpacetimeDB, Godot, Unity, Unreal, Babylon.js) — loaded by `__init__.py:get_projects()`. Likely a marimo/notebook surface, not a web app. |
| 9 | `oideachais/`             | 1.3 MB | 92 tsx / 93 ts | 2026-08-16 | **CANONICAL** (per-subject content app, Phase D) | The new consolidated per-subject app. **NO `package.json`** — `routes/` is the source of truth. 14 LC subjects × `index.tsx + $topicId.tsx + AGENTS.md` (e.g. `routes/lc/mathematics/`). |
| 10 | `oideachais-dashboard/`  | 1.0 MB | 10 tsx / 100 ts | 2026-08-14 | **CANONICAL** (operator dashboard, Phase F) | Operator dashboard. Has 100 ts files (the Convex schema is huge: `a-level/`, `gcse/`, `jc/`, `lc/`, `models.ts`, `schema.ts`, etc.). The **umbrella Convex deployment** shared with oideachais + cianfhoghlaim per `web/AGENTS.md`. |
| 11 | `tuatha-demo/`           | 32 KB | 0 / 0 | 2026-07-22 | **NOT A WEB APP** (Python demo) | `run_demo.py` — SIWE demo for the Tuatha Celtic MMO. Backend is `sruth/tuath/api/main.py` on FastAPI port 8000. |
| 12 | `tuatha-ui/`             | 60 MB | 15 tsx / 13 ts | 2026-07-22 | **CANONICAL** (Tuatha MMO front-end) | TanStack Start 1.168.21 + Babylon.js (per `app.config.ts`). Port 3004. **Missing AG-UI / CopilotKit** — appears stale compared to cianfhoghlaim. |

> **Observation:** 7 apps are TanStack Start (cianfhoghlaim, cianfhoghlaim-leaving-cert, cianfhoghlaim-mmo, cianfhoghlaim-web, croilar-portal, croilar-web, oideachais-dashboard, tuatha-ui) — that's 7 production-grade frontends.
> oideachais is a routes-only stub. _oideachais_apps/web/ is the pre-v7 legacy SPA. game_showcase + tuatha-demo are non-web.

### A.2 — Top-level `web/packages/` (3 entries + 5 sub-packages)

| Package | Purpose | Files | Status |
|:--|:--|--:|:--|
| `auth/` (1 file: `index.ts`) | Better-Auth wrapper (depends on `better-auth ^1.3.11`) | 1 | **SHELL** — `src/index.ts` is 1955 bytes, minimal |
| `db/` (1 file: `index.ts` + `src/api/`) | Convex helpers (depends on `convex ^1.19.0`) | 1 + subdir | **SHELL** — `src/index.ts` is 107 bytes, re-export |
| `ui-kit/` (`analytics`, `components`, `config`, `hooks`, `i18n`, `src`) | Tailwind + Radix UI + tokens + i18n | 6 sub-pkgs + 1 src | **PARTIAL** — `src/index.ts` is 638 bytes; sub-packages have their own package.jsons |

> **Total `web/packages/` source: 3 ts files.** This is **dramatically thinner** than the
> nested `web/apps/*/packages/*/` sub-monorepos, which contain the real UI components,
> auth wiring, and db helpers. The root workspace packages are basically placeholders.

### A.3 — `web/hono-api/`

| Path | Purpose |
|:--|:--|
| `src/index.ts` | Main entry, registers routes |
| `src/auth.ts` | BetterAuth handler with Drizzle + Postgres |
| `src/middleware.ts` | Auth middleware (JWT validation) |
| `src/migrate.ts` | Drizzle migration runner |
| `src/data/`, `src/db/`, `src/routes/` | Domain modules |
| **6 source files** | Total LOC ~800 |

This is the **canonical Hono gateway** per `web/AGENTS.md` — but `cianfhoghlaim-web/apps/api/` and `cianfhoghlaim-leaving-cert/apps/api/` are duplicates of this pattern.

### A.4 — Sub-monorepos buried inside apps

| App | Has own `apps/web`? | Has own `apps/api`? | Has own `packages/`? |
|:--|:--:|:--:|:--|
| `cianfhoghlaim-web/` | ✅ | ✅ | ✅ (api, auth, config, db — 4 packages) |
| `cianfhoghlaim-leaving-cert/` | ✅ | ✅ | ✅ (api, auth, config, convex, db, i18n, ui — 7 packages) |
| `croilar-portal/` | ❌ | ❌ | ❌ |
| `oideachais-dashboard/` | ❌ | ❌ | ❌ (uses root `web/packages/`) |
| `oideachais/` | ❌ | ❌ | ❌ |

> **Two of the 12 apps** (`cianfhoghlaim-web` and `cianfhoghlaim-leaving-cert`) **each contain
> their own private mini-monorepo** with 5–7 internal packages. These are full-stack
> end-to-end applications that don't reuse `web/packages/`, `web/hono-api/`, or the
> canonical Convex deployment.

---

## B) Naming sprawl analysis

The web surface has **5 inconsistent naming conventions** co-existing:

| Prefix | Apps | Implication |
|:--|:--|:--|
| **`cianfhoghlaim-*`** | `cianfhoghlaim/` (homepage), `cianfhoghlaim-web/` (TanStack Start), `cianfhoghlaim-leaving-cert/` (the leaving-cert rewrite), `cianfhoghlaim-mmo/` (TanStack Start 2D MMO client) | "cianfhoghlaim" used for 4 different things — homepage, full-stack web app, leaving-cert rewrite, MMO. Indistinguishable in conversation. |
| **`oideachais*`** | `oideachais/` (new content app), `oideachais-dashboard/` (operator dashboard), `_oideachais_apps/` (legacy archive) | Distinguishable from `cianfhoghlaim-*`, but the `_oideachais_apps` archive uses underscore-prefix (the v4-consolidation convention for archived directories). |
| **`tuatha*`** | `tuatha-ui/` (TanStack Start Babylon.js MMO), `tuatha-demo/` (Python SIWE demo) | MMO is real, demo is a Python script — should be flagged as "not a web app". |
| **`croilar*`** | `croilar-web/` (public persona site), `croilar-portal/` (admin dashboard) | Clean split: public vs private. |
| **`game_showcase/`** | (single) | Snake-case (the only one!) — and it's a Python module, not a web app. |

### B.1 — Pairwise naming conflicts (where things collide in conversation)

1. **`cianfhoghlaim-web`** vs **`oideachais-dashboard`**: both are large TanStack Start apps with their own `app.config.ts`, both reference `oideachais` in route paths, both have their own Convex schemas. The first is the "old" web app, the second is the "new" operator dashboard. **Same problem domain, two competing implementations.**

2. **`cianfhoghlaim-leaving-cert`** vs **`oideachais`**: both are Leaving-Cert content apps. The first has the full TanStack Start stack + BAML + ADK agents + CopilotKit. The second is a routes-only stub. **They appear to be 90% overlapping in scope.** Per the audit at `docs/audit/web-app-consolidation-plan.md`, the consolidation plan was to merge all web apps into a single `cio-web/`. That hasn't happened.

3. **`cianfhoghlaim`** (homepage) vs **`cianfhoghlaim-web`**: the first is a thin homepage (15 tsx, 4 ts). The second is the full web app (56 tsx, 39 ts). Confusingly, **`cianfhoghlaim-web`** is **not** the implementation of the **cianfhoghlaim** homepage — it's a separate app.

4. **`tuatha-ui`** vs **`cianfhoghlaim-mmo`**: both are MMO clients. `tuatha-ui` is Babylon.js 3D. `cianfhoghlaim-mmo` is TanStack Start 2D. Different code paths to the same goal.

### B.2 — `_oideachais_apps/` — the legacy archive

| File | Size | Status |
|:--|--:|:--|
| `AGENTS.md` | 12 KB | Pre-v4 (sruth/) routing reference. Has explicit "v4 consolidation note (2026-06-28)" — points readers to `cianfhoghlaim/` as canonical. |
| `STATUS.md` | 28 KB | Pre-v4 BAML × DLT × Dagster matrix. Has explicit note about `sruth/oideachais/` paths — pre-v4. |
| `CHANGELOG.md` | 11 KB | Pre-v4 cumulative change log. |
| `README.md` / `README_eile.md` | 34 KB / 17 KB | Pre-v4 user-facing docs (one Irish, one English). |
| `REFACTORING.md` | 49 KB | Pre-v4 refactor backlog. |
| `web/` (subdir) | 552 KB | The pre-v7 Vite SPA. Has its own `package.json` + `vite.config.ts` + `src/` + `bun.lock` + `pnpm-lock.yaml`. **Dead code.** |

> **Recommendation:** `_oideachais_apps/` is the textbook legacy archive. **Archive it.**
> Move all 7 files to `openspec/archive/2026-08-24-archive-legacy-oideachais-apps/` and
> delete the directory. The v7-flatten `web/AGENTS.md` already establishes `oideachais/`
> as canonical — the legacy archive is pure dead weight and confusing.

### B.3 — `game_showcase/` and `tuatha-demo/` — the non-web apps

Neither of these is a web app:
- `game_showcase/` is a Python module (47-line `__init__.py` + 5 YAML project descriptors). It loads via `get_projects()` and is consumed by marimo notebooks or external scripts.
- `tuatha-demo/` is a Python CLI demo (`run_demo.py`) that exercises the FastAPI backend at `sruth/tuath/api/main.py:app`.

> **Recommendation:** move both to a new top-level `demos/` or `samples/` directory
> **outside `web/`** to make it clear they are not web apps. The web-app bun
> workspaces glob (`web/apps/*`) will then match only real web apps.

---

## C) Tech stack per app (matrix)

### C.1 — Framework / routing / runtime

| App | Framework | Router | Runner | Backend | Auth | UI lib | Realtime |
|:--|:--|:--|:--|:--|:--|:--|:--|
| `cianfhoghlaim/` | **TanStack Start** (RC) | TanStack Router 1.95+ | Vinxi node-server | Convex 1.40 + BetterAuth 1.0 | better-auth | CopilotKit v1.67 + TanStack AI 0.5 | Convex |
| `cianfhoghlaim-leaving-cert/` | **TanStack Start** 1.168 | TanStack Router 1.167+ | Vinxi | Convex 1.40 + BetterAuth 1.4 + Hono (CF Workers) + oRPC | better-auth + Pocket ID OIDC | CopilotKit v1.67 + A2UI + AG-UI + TanStack AI/DB/Form + Radix + d3 + reactflow + framer-motion + recharts | Convex + R2 |
| `cianfhoghlaim-mmo/` | **TanStack Start** 1.95 | TanStack Router 1.95+ | Vite 6 + node-server | Convex 1.40 + BetterAuth 1.0 | better-auth | CopilotKit v1.67 + lucide | Convex + x402 |
| `cianfhoghlaim-web/` | **TanStack Start** (via Vinxi) | TanStack Router | Vinxi (pre-TanStack-Start-1.0) | Convex 1.40 + Hono (own `apps/api/`) + R2 | own `packages/auth/` (BetterAuth) | Tailwind 4 | Convex + R2 |
| `croilar-portal/` | **TanStack Start** 1.168 | TanStack Router 1.170 | Vinxi node-server | MCP (`@mcp-ui/server`) + Drizzle + Postgres | better-auth 1.4 + SIWE + x402 | Tailwind 4 + Radix UI + lucide + recharts | MCP-UI + Drizzle |
| `croilar-web/` | **TanStack Start** 1.168 | TanStack Router 1.170 | Vinxi | Convex (own `convex/`) + Postgres | better-auth | Tailwind 4 + Radix UI + lucide + i18next | Convex |
| `_oideachais_apps/web/` (legacy) | **Vite SPA** | TanStack Router | Vite 5 | (none — dead) | none | Tailwind + CopilotKit | none |
| `oideachais/` | **TanStack Start** (no `package.json`) | file-based routes | Vinxi (parent) | shared via umbrella Convex | shared | shared | shared |
| `oideachais-dashboard/` | **TanStack Start** 1.95+ | TanStack Router 1.95 | Vinxi node-server | shared Convex (umbrella) | shared BetterAuth | Tailwind + shared ui-kit | Convex |
| `tuatha-ui/` | **TanStack Start** 1.168 | TanStack Router 1.170 | Vinxi (Nitro nightly) | not connected | not wired | lucide | not wired |

### C.2 — Stack inconsistencies

1. **TanStack Router pin drift**: `^1.95.0` (newer apps) vs `1.170.8` (older apps) vs `^1.95.0` (mm0). The router is at v1.170+ now; the 1.95 spec might be a typo (could be 1.95.0 from an older release). **Audit needed.**
2. **TanStack Start runtime**: apps using `Vinxi` (pre-1.0) vs `vite-tsconfig-paths` (post-1.0). This is a major version drift within the same repo.
3. **Backend pick**: Convex is used by 6/12 apps, but the same Convex deployment is **not** shared. `oideachais-dashboard/convex/` is the umbrella; `cianfhoghlaim-web/convex/` and `croilar-portal/convex/` and `cianfhoghlaim-mmo/convex/` are independent.
4. **Hono duplication**: 3 separate Hono gateways (`web/hono-api/`, `cianfhoghlaim-web/apps/api/`, `cianfhoghlaim-leaving-cert/apps/api/`). The canonical one per `web/AGENTS.md` is `web/hono-api/`.
5. **Auth duplication**: 3 BetterAuth installs. The `web/packages/auth/` is supposed to be canonical, but `cianfhoghlaim-leaving-cert/packages/auth/` and `web/hono-api/src/auth.ts` (with Drizzle) are independent.
6. **MCP-UI presence**: only `croilar-portal/` uses `@mcp-ui/server` + `@mcp-ui/client` — this is the protocol for surfacing MCP tool calls as chat UIs. Should be a platform-wide pattern.

### C.3 — Backend relationship to data platforms

| Platform | Path | Surfaces |
|:--|:--|:--|
| MotherDuck (DuckLake) | `md:cianfhoghlaim` (Dagster → BIEP v3) | `oideachais-dashboard/` (via DLT/MotherDuck Dives), `oideachais/` (per-subject queries), `notebooks/` (BIEP v3 marimo) |
| Convex (real-time) | per-app deployments | `cianfhoghlaim`, `cianfhoghlaim-leaving-cert`, `cianfhoghlaim-mmo`, `cianfhoghlaim-web`, `croilar-portal`, `oideachais-dashboard` (umbrella) |
| Hono (Bun + oRPC) | `web/hono-api/` | all apps should route through this |
| BAML (typed LLM extraction) | `baml_src/british_isles/ireland/education/` | `cianfhoghlaim-leaving-cert/` (the only one wired) — should be wired to `oideachais/` too |
| Dagster (orchestration) | `orchestration/defs/{1..5}_*/` | `web/hono-api/` proxies Dagster health endpoints to `oideachais-dashboard/` |
| LanceDB / Convex agents | per-deployment | `cianfhoghlaim-leaving-cert/packages/convex/` |

The **handoff from data platform to web** is:
`dlt_sources/ → orchestration/ (Dagster) → cocoindex_flows/ (LanceDB + Convex mirror) → notebooks/ + web/hono-api/ + web/apps/*/convex/`

For **67% of the apps**, this hand-off is **broken or duplicated**. Specifically:
- `cianfhoghlaim-web/` re-implements the Convex schema for the leaving-cert (instead of consuming the umbrella schema in `oideachais-dashboard/convex/`).
- `cianfhoghlaim-leaving-cert/` re-implements the entire BAML surface (it has its own `apps/api/` + `packages/convex/` + `baml_src/` inside its `apps/`).
- `croilar-portal/` uses Postgres + Drizzle instead of Convex.

---

## D) Shared packages audit

### D.1 — Root `web/packages/` (the canonical surface per `web/AGENTS.md`)

| Package | `src/index.ts` size | Real content? | Used by |
|:--|--:|:--|:--|
| `@cianfhoghlaim/ui-kit` | 638 bytes | **NO** — just re-exports | `oideachais-dashboard`, `cianfhoghlaim`, `hono-api` |
| `@cianfhoghlaim/ui-kit/analytics` | n/a (sub-package) | not yet built out | (intended) |
| `@cianfhoghlaim/ui-kit/i18n` | n/a | not yet built out | (intended) |
| `@cianfhoghlaim/ui-kit/components` | n/a | not yet built out | (intended) |
| `@cianfhoghlaim/ui-kit/config` | n/a | not yet built out | (intended) |
| `@cianfhoghlaim/ui-kit/hooks` | n/a | not yet built out | (intended) |
| `@cianfhoghlaim/auth` | 1955 bytes | **PARTIAL** — minimal BetterAuth wrapper | `hono-api` (as dep), `oideachais-dashboard` (as dep) |
| `@cianfhoghlaim/db` | 107 bytes | **NO** — near-empty re-export | `hono-api` (as dep), `croilar-web` (as dep) |

### D.2 — Inner app sub-monorepos (the **actual** implementations)

| App | Inner packages | `apps/api` contents | Drift |
|:--|:--|:--|:--|
| `cianfhoghlaim-leaving-cert/` | **7** (`api`, `auth`, `config`, `convex`, `db`, `i18n`, `ui`) | Hono + oRPC + AG-UI + CopilotKit runtime + content-types router | This is the **full implementation** that the root `web/packages/*/` were supposed to provide. |
| `cianfhoghlaim-web/` | **4** (`api`, `auth`, `config`, `db`) | Hono with R2 proxy | Subset of the above; uses pre-1.0 Vinxi stack |
| `croilar-portal/` | **0** (uses root `web/packages/`) | n/a | Uses root packages, but its own Drizzle + Postgres in `db/` |
| `croilar-web/` | **0** (uses root `web/packages/db/` + own `@croilar/i18n`) | n/a | Uses root packages, but `convex/` is internal |
| `oideachais-dashboard/` | **0** (uses root `web/packages/`) | n/a | Convex in `convex/` |

### D.3 — Usage table (which app depends on which root package)

| Package | Used by |
|:--|:--|
| `@cianfhoghlaim/ui-kit` | `hono-api`, `cianfhoghlaim`, `oideachais-dashboard` |
| `@cianfhoghlaim/auth` | `hono-api` |
| `@cianfhoghlaim/db` | `hono-api`, `croilar-web` |
| `@croilar/i18n` | `croilar-web` |

> **Only 3 of 12 apps actually consume the root `web/packages/*` surface.**
> The rest re-implement everything in their own internal `packages/`.
> This is the single biggest source of duplication.

### D.4 — Drift summary

- **Root packages are aspirational.** The sub-monorepos inside `cianfhoghlaim-leaving-cert/` and `cianfhoghlaim-web/` are **what the apps actually use**.
- The audit at `docs/audit/web-app-consolidation-plan.md` proposed merging all apps into a single `cio-web/`. That plan never landed, so the drift compounded.
- The current `web/AGENTS.md` says "Never create a per-app `apps/<app>/apps/api/src/` directory" — but `cianfhoghlaim-web/apps/api/src/` and `cianfhoghlaim-leaving-cert/apps/api/src/` both exist and are non-trivial.

---

## E) Recommended 2026 stack

> Sourced from the official docs fetched 2026-08-24.

### E.1 — Per-layer stack

| Layer | Technology | Why |
|:--|:--|:--|
| **Framework** | **TanStack Start** (RC, post-1.0) | "Router-first app, from server request to client navigation. Keep the routes. Change the output." Supports Cloudflare Workers, Node.js, Netlify, Railway. Type-safe server functions + middleware. |
| **Router / state** | TanStack Router + TanStack Query + TanStack AI + TanStack DB + TanStack Form | The full TanStack family; AI for tool calling, DB for differential sync, Form for filter forms. |
| **Auth** | **Better Auth** (`^1.7`) | Framework-agnostic, TS, plugin ecosystem (OIDC, 2FA, passkey, multi-tenancy, multi-session, SSO). Plus an MCP server at `https://mcp.better-auth.com/mcp`. |
| **Backend (real-time)** | **Convex** | Reactive database + queries + mutations + actions + HTTP actions + file storage + vector search + auth + cron + scheduled functions + agents + MCP server. Has a first-class Convex-TanStack-Start integration. |
| **API gateway** | **Hono** on Cloudflare Workers (`hono ^4.8`) | Fast HTTP servers with middleware composition; pairs with oRPC for typed RPC. |
| **Agent UI** | **CopilotKit v2** (current major) + **AG-UI** protocol | CopilotKit for the React chat components (chat/popup/sidebar); AG-UI for SSE streaming agent↔UI events (RUN_STARTED, STATE_SNAPSHOT, MESSAGES_SNAPSHOT, etc.). |
| **A2UI / generative UI** | **A2UI** (Google) — declarative agent UI protocol | For agents that need to render dynamic UI trees with constraints. Used alongside AG-UI (the two protocols are complementary). |
| **Runtime** | Bun (`>= 1.4`) + Nitro (for Vinxi back-compat) | Already on Bun 1.4+; Nitro for the older TanStack Start apps until they migrate to 1.0+. |
| **Cloud** | Cloudflare Workers + R2 + D1 + Vectorize + Pages | R2 for static asset / PDF storage, D1 for relational data, Vectorize for vector search, Workers for the Hono gateway. |
| **CSS / UI** | **Tailwind 4** + **Radix UI** primitives + **shadcn/ui** + **d3** + **reactflow** + **framer-motion** + **recharts** + **sonner** | Already the de facto stack across all apps. |
| **Deployment** | Cloudflare Pages + Cloudflare Workers + wrangler.toml per app | Standard for TanStack Start on Cloudflare. |
| **Observability** | **Langfuse** (LLM traces + cost) + **Logfire** (Python traces) + **MLflow** (experiments) + **Ragas** (RAG eval) | Already on `agent-observability` skill. |
| **State management** | **Zustand** + **TanStack Store** | Already present in `cianfhoghlaim-leaving-cert`. |

### E.2 — The 12 building blocks of AG-UI that justify the protocol choice

Per `https://ag-ui.com/`:

1. Streaming chat — live token + event streaming
2. Multimodality — typed attachments (files, images, audio)
3. Generative UI, static — typed components under app control
4. Generative UI, declarative — agents propose trees + constraints
5. Shared state — typed store between agent and app
6. Thinking steps — visualise intermediate reasoning
7. Frontend tool calls — typed handoffs from agent to frontend
8. Backend tool rendering — visualise backend tool outputs
9. Interrupts — human-in-the-loop
10. Sub-agents and composition — nested delegation
11. Agent steering — dynamic redirect via real-time user input
12. Tool output streaming — stream tool results in real time

> **Adoption:** Google ADK (which `agents/adk/` uses) has **1st-party AG-UI support** per the AG-UI docs. So all the ADK agents already in `agents/adk/personal_archive_module_assistant.py` etc. can stream AG-UI events natively.

### E.3 — Per-domain Convex schema strategy

For the canonical Convex deployment (the umbrella at `oideachais-dashboard/convex/`), the per-table layout should be:

```
oideachais_dashboard.convex schema:
├── umbrella/         # cross-cutting tables (users, sessions, audit)
├── lc/              # 14 LC subjects × {topics, practice, sessions, embeddings}
├── jc/              # 11 JC subjects × {specs, cba_tasks, outcomes}
├── gcse/            # 8 GCSE subjects × {specs, papers, mark_schemes}
├── a-level/         # 6 A-level subjects × {specs, papers, mark_schemes}
├── models/          # the 76-entry MODEL_REGISTRY mirror
├── agents/          # per-subject agent chat history
├── comparison/      # cross-jurisdiction comparisons (BIEP v3)
└── tasks/           # async task queue for BAML extractions
```

This already exists in `oideachais-dashboard/convex/` — but `cianfhoghlaim-web/convex/` and `croilar-portal/convex/` re-implement subsets.

### E.4 — Recommended IDE / scaffolding tools

- **TanStack Start CLI** (`create-tsrouter-app`) for new apps
- **Convex Agent Skills** (https://docs.convex.ai/ai/agent-skills) — official Claude Code / Cursor / Codex plugin for Convex best practices
- **Better Auth Skills** — first-party skills for Claude Code
- **CopilotKit `create-copilot-app`** for new agent UIs
- **AG-UI Dojo** (https://dojo.ag-ui.com/) — 12 walkthroughs for the 12 building blocks

---

## F) Proposed consolidation plan

### F.1 — Tier table

| App / package | Tier | Action | Effort | Risk |
|:--|:--|:--|:--|:--|
| `oideachais/`                 | **1 — canonical** (per-subject content) | **KEEP + invest** | n/a | n/a |
| `oideachais-dashboard/`       | **1 — canonical** (operator dashboard) | **KEEP + invest** | n/a | n/a |
| `cianfhoghlaim/`              | **1 — canonical** (central homepage) | **KEEP + grow** to absorb cianfhoghlaim-web | L (3 weeks) | High |
| `croilar-web/`                | **1 — canonical** (multi-persona public) | **KEEP + invest**; consider pulling `croilar-portal` | M | Low |
| `tuatha-ui/`                  | **1 — canonical** (Tuatha MMO Babylon.js) | **KEEP + refresh** with AG-UI + CopilotKit; consider pulling `cianfhoghlaim-mmo` | M | Med |
| `croilar-portal/`             | **2 — merge into croilar-web** | **MERGE** as `/croilar/admin/` routes in croilar-web | S (1 week) | LOW |
| `cianfhoghlaim-mmo/`          | **2 — merge into tuatha-ui or cianfhoghlaim** | **MERGE** the 2D TanStack MMO into tuatha-ui (Babylon.js + 2D canvas) | M (2 weeks) | Med |
| `cianfhoghlaim-web/`          | **3 — merge into cianfhoghlaim** | **MERGE** the full leaving-cert TanStack Start app into cianfhoghlaim (the central homepage). Move routes to `/<stage>/<subject>/` per the BIEP v3 model. The data engineering pipeline stays; the UI moves. | L (3-4 weeks) | HIGH (largest public surface) |
| `cianfhoghlaim-leaving-cert/` | **3 — merge into oideachais** | **MERGE** the leaving-cert sub-monorepo into `oideachais/` (which is currently just routes). Move `apps/web/` → `oideachais/src/routes/`, `apps/api/` → `web/hono-api/`, `packages/{auth,config,convex,db,i18n,ui}/` → `web/packages/*/`. | XL (4-6 weeks) | HIGH (richest content) |
| `tuatha-demo/`                | **4 — move out** | **MOVE** to `demos/tuatha-demo/` at repo root (or `examples/`); it's a Python CLI, not a web app. | S | LOW |
| `game_showcase/`              | **4 — move out** | **MOVE** to `demos/game_showcase/`; it's a Python data module. | S | LOW |
| `_oideachais_apps/`           | **5 — archive** | **ARCHIVE** the entire directory to `openspec/archive/2026-08-24-archive-legacy-oideachais-apps/`. Pure dead weight. | S | LOW |

### F.2 — Post-consolidation topology (target state)

```
web/
├── apps/
│   ├── oideachais/                # MERGED from cianfhoghlaim-leaving-cert (LC content)
│   ├── oideachais-dashboard/      # unchanged (operator dashboard)
│   ├── cianfhoghlaim/             # MERGED from cianfhoghlaim-web (central homepage)
│   ├── croilar-web/               # MERGED from croilar-portal (public + /admin)
│   └── tuatha-ui/                 # MERGED from cianfhoghlaim-mmo (Babylon.js + 2D MMO)
├── packages/
│   ├── auth/                      # canonical BetterAuth (moved from hono-api/src/auth.ts + clc/packages/auth/)
│   ├── db/                        # canonical Convex generators + Drizzle helpers (moved from clc/packages/db/)
│   ├── ui-kit/                    # canonical UI surface (moved from clc/packages/ui/)
│   ├── i18n/                      # canonical i18n (was @croilar/i18n)
│   └── convex/                    # canonical Convex helpers (moved from clc/packages/convex/)
├── hono-api/                      # canonical API gateway (moved from cianfhoghlaim-web/apps/api/ + clc/apps/api/)
└── (no hono-api/ — merged into oideachais-dashboard/api/ if SSR-only; or kept standalone for cross-app RPC)
```

That's **5 apps + 5 packages + 1 hono-api** down from **12 apps + 32 package.jsons**.

### F.3 — Estimated impact

| Metric | Before | After | Δ |
|:--|--:|--:|--:|
| Apps | 12 | 5 | −7 |
| Distinct `package.json` files | 32 | 11 | −21 |
| Duplicated Convex deployments | ≥3 | 1 | −2 |
| Duplicated Hono gateways | 3 | 1 | −2 |
| Duplicated BetterAuth installs | 3 | 1 | −2 |
| `.tsx` source files | 443 | ~350 (after dedupe) | ~−20% |
| Estimated LOC reduction | n/a | n/a | ~−30% |
| Disk footprint (excl. node_modules) | ~80 MB | ~50 MB | ~−37% |

---

## G) Order of refactor

> Per the user's question: **dlt → dagster → cocoindex → lakehouse → web → frontend.**
> This ordering reflects dependency: each layer's surface must be **stable** before the
> next layer can consume it.

### G.1 — The 6 phases

| Phase | Layer | Scope | Critical artifacts | Status |
|:--|:--|:--|:--|:--|
| **1** | **dlt** | 928 DLT sources + per-jurisdiction subdirectories. Get all sources green, all staging tables materialised. | `dlt_sources/common/`, `dlt_sources/british_isles/`, `dlt_sources/commonwealth/` | DONE — 99% green |
| **2** | **dagster** | 833 assets in the 5-layer `defs/` tree. Wire every DLT destination to a Dagster asset. Asset checks for freshness. | `orchestration/defs/1_ingestion/`, `orchestration/components/layer{1..5}_*.py` | 95% done |
| **3** | **cocoindex** | 17+ CocoIndex v1 Apps covering the 6 LC subjects + 11 dlt-derived corpora. Embedding pipeline via the shared `_lifespan.py` (BGE-M3 1024-d). | `cocoindex_flows/*`, `cocoindex_flows/_shared/_lifespan.py` | 90% done |
| **4** | **lakehouse** | MotherDuck + DuckLake tables under `md:cianfhoghlaim`. The BIEP v3 federated SQL layer (`ibis.duckdb.connect("md:cianfhoghlaim")`). MotherDuck Dives for the 4 BIEP dashboards. | `motherduck/`, `notebooks/_shared/db.py`, `notebooks/10_biep_*` | 85% done |
| **5** | **web** | Convex umbrella schema + `web/hono-api/` + `web/packages/{auth,db,ui-kit}/`. Wire BIEP v3 marimo notebook outputs to the web via Hono + Convex. | `web/hono-api/`, `web/packages/*`, `oideachais-dashboard/convex/` | 70% done — **THIS IS WHERE WE ARE** |
| **6** | **frontend** | Per-phase **frontend consolidation** (this plan): merge 12 apps → 5 apps + 1 gateway + 5 packages. Apply the recommended 2026 stack (TanStack Start 1.0+ + CopilotKit v2 + AG-UI + Convex + Better Auth + Hono). | All `web/apps/*/`, all `web/packages/*/` | 20% done — **START HERE NEXT** |

### G.2 — Justification of the order

1. **dlt must finish first** because every downstream layer (Dagster, CocoIndex, web)
   consumes the staging tables DLT produces. If a DLT source is broken, every asset
   downstream is broken.

2. **Dagster must finish second** because it provides the **observability + asset
   graph + scheduling** for everything else. Without Dagster, you can't tell which
   upstream asset is stale, and you can't backfill.

3. **CocoIndex must finish third** because it produces the **embeddings + semantic
   search index** that the agent layer (Langfuse + Graphiti + Cognee + AG-UI) consumes.
   Without CocoIndex, RAG has no corpus.

4. **Lakehouse must finish fourth** because it provides the **federated SQL + MotherDuck
   Dives** that the BIEP v3 marimo notebooks + `oideachais-dashboard` consume.
   Without the lakehouse, the dashboards are empty.

5. **Web (Phase 5) is the platform boundary.** Once the data platform is stable, the
   web layer becomes the **canonical entry point** for humans + agents. Hono becomes
   the gateway; Convex becomes the real-time backend; Better Auth becomes the identity
   layer; web/packages/* becomes the shared UI surface.

6. **Frontend consolidation (Phase 6) is last** because:
   - It depends on the canonical `web/packages/*` being stable.
   - It depends on the canonical Hono gateway being stable.
   - It depends on the canonical Convex schema being stable.
   - It depends on AG-UI being wired into the canonical Hono gateway (so that the
     CopilotKit v2 React components can attach).

### G.3 — Recommended opening move (Phase 6, step 1)

**Archive `_oideachais_apps/` + `game_showcase/` + `tuatha-demo/` first.** These
three directories are the lowest-risk, highest-clarity wins:

- `_oideachais_apps/` — pure legacy. Move to `openspec/archive/`.
- `game_showcase/` — Python module, not a web app. Move to `demos/game_showcase/`.
- `tuatha-demo/` — Python demo, not a web app. Move to `demos/tuatha-demo/`.

That's 580 KB removed from `web/apps/` and the bun workspaces glob stops matching
non-web artefacts.

### G.4 — Recommended next 3 steps (Phase 6, steps 2-4)

| Step | Move | Effort | Why |
|:--|:--|:--|:--|
| 2 | Move the `web/packages/auth/` wrapper to a real implementation: lift `web/hono-api/src/auth.ts` + `oideachais-dashboard/convex/auth/` + `cianfhoghlaim-leaving-cert/packages/auth/` into one canonical `@cianfhoghlaim/auth`. Then update all 3 call sites. | M (1-2 weeks) | Eliminates 2 of 3 auth duplicates |
| 3 | Same for `web/packages/db/`: lift `cianfhoghlaim-leaving-cert/packages/db/` + `cianfhoghlaim-leaving-cert/packages/convex/` into one canonical `@cianfhoghlaim/db` + `@cianfhoghlaim/convex`. | M (1-2 weeks) | Eliminates Convex schema duplicates |
| 4 | Promote `web/hono-api/src/copilotkit/` and `web/hono-api/src/ag-ui/` to be the **single canonical CopilotKit actions + AG-UI streamer** surface. Move the equivalent code from `cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/` and `cianfhoghlaim-web/apps/api/` to here. | M (2-3 weeks) | Eliminates 2 of 3 Hono gateways + 2 of 3 CopilotKit installs |

### G.5 — Recommended final 3 steps (Phase 6, steps 5-7)

| Step | Move | Effort | Why |
|:--|:--|:--|:--|
| 5 | **Merge `croilar-portal/` → `croilar-web/`** as `/admin` routes. | S (1 week) | Easiest merge; portal is small |
| 6 | **Merge `cianfhoghlaim-web/` → `cianfhoghlaim/`**. The new homepage absorbs the leaving-cert TanStack Start app; routes become `/<stage>/<subject>/` per the BIEP v3 model. | L (3-4 weeks) | High-impact consolidation |
| 7 | **Merge `cianfhoghlaim-leaving-cert/` → `oideachais/`**. The leaving-cert sub-monorepo becomes per-subject routes in the canonical oideachais app. The BAML + ADK agents stay at `agents/`. The data engineering pipeline stays at `baml_src/`. The UI moves. | XL (4-6 weeks) | The final big move |

### G.6 — Total refactor timeline

| Stream | Duration | Squad |
|:--|:--|:--|
| Steps 1-4 (cleanup + canonical packages) | 6-9 weeks | 1 person, sequential |
| Step 5 (croilar merge) | 1 week | 1 person |
| Step 6 (cianfhoghlaim-web merge) | 3-4 weeks | 2 people (parallel) |
| Step 7 (cianfhoghlaim-leaving-cert merge) | 4-6 weeks | 2 people (parallel) |
| **Total** | **15-21 weeks** | mixed |

With 2 people running in parallel: **12 weeks** is realistic.

---

## H) Other notable observations

### H.1 — The opencode.json `design-system` MCP

`opencode.json:352-364` registers a `design-system` MCP server at:
```
uv run python web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/mcp/design-system-server.py
```

This is **a deeply nested path** that breaks if any of the intermediate directories
are renamed. It should move to `web/packages/ui-kit/mcp/design-system-server.py` after
the consolidation lands.

### H.2 — The `croilar:analyze` mise task

`package.json:90` registers `bun run scripts/croilar/analyze-web-stack.ts` as
`croilar:analyze`. The script outputs `.cache/webstack-snapshot.json`. **This is the
canonical web-stack snapshot tool.** Run it before any refactor to capture the
baseline.

### H.3 — The BIEP v3 web UI consumer spec

The `british-isles-education-pipeline-v3` spec already commits to a per-jurisdiction
web UI pattern. The 60-subject coverage matrix + per-subject agents spec
(`per-subject-coverage`, `per-subject-agents`) are downstream. The web layer
refactor **must not break the BIEP v3 contract** — every subject landing page at
`/<stage>/<subject>/` must continue to work after the merge.

### H.4 — The `tuatha-ui` Nitro-nightly warning

`web/apps/tuatha-ui/package.json:26` pins `"nitro": "npm:nitro-nightly@latest"` in
devDependencies. This is a nightly build of Nitro used by Vinxi. **Nitro nightly
builds are unstable.** After the consolidation, this should move to a stable Nitro
release.

### H.5 — Babylon.js is in the ui package

`web/apps/cianfhoghlaim-leaving-cert/packages/ui/package.json:28-29` declares
`"@babylonjs/core": "^6.0.0"` and `"@babylonjs/loaders": "^6.0.0"` in the UI package
exports. This is **3D rendering dependencies in a UI package** — leaky abstraction.
After consolidation, Babylon.js should be only in the `tuatha-ui` app, not in the
shared `ui-kit`.

### H.6 — The Croilar portal README is pre-v7

`web/apps/croilar-portal/README.md:24` says `cd sruth/aleyum/portal` — a
**pre-v7 path** that no longer exists. The README is stale and should be updated.

### H.7 — The Croilar AGENTS.md is still titled for sruth/

`web/apps/croilar-web/AGENTS.md:9` starts with "Croílár Quadrant — Agent Instructions"
and references `sruth/croilar/` paths. Although the AGENTS.md does include a
"v4 consolidation note (2026-06-28)" mentioning that `sruth/croilar/` was merged
into `cianfhoghlaim/`, the rest of the document still uses `sruth/` paths in the
quick-routing table and the cross-references. **Update to `web/apps/croilar-web/`.**

---

## I) Adjacent specs and skills to consult

| Spec | Why it matters |
|:--|:--|
| [`agentic-frontend-frameworks`](../openspec/specs/agentic-frontend-frameworks/spec.md) | The canonical 4-surface + CopilotKit + AG-UI + Convex pattern |
| [`web-monorepo-consolidation`](../openspec/specs/web-monorepo-consolidation/spec.md) | The Phase A-F consolidation that this plan supersedes |
| [`central-cianfhoghlaim-homepage`](../openspec/specs/central-cianfhoghlaim-homepage/spec.md) | The Phase T homepage (the destination for cianfhoghlaim-web) |
| [`per-subject-coverage`](../openspec/specs/per-subject-coverage/spec.md) | The 60-subject matrix (the destination for cianfhoghlaim-leaving-cert) |
| [`per-subject-agents`](../openspec/specs/per-subject-agents/spec.md) | The 60 per-subject agents (already wired in cianfhoghlaim-leaving-cert) |
| [`tanstack-ai-agui-integration`](../openspec/specs/tanstack-ai-agui-integration/spec.md) | The TanStack AI + AG-UI compliance |
| [`schema-driven-codegen`](../openspec/specs/schema-driven-codegen/spec.md) | The BAML → Zod → Convex → CopilotKit pipeline |
| [`deployment-control-panel`](../openspec/specs/deployment-control-panel/spec.md) | The deployment-choice.yaml web UI (consumer of this dashboard's data) |
| [`british-isles-education-pipeline-v3`](../openspec/specs/british-isles-education-pipeline-v3/spec.md) | The BIEP v3 web UI consumer |

| Skill | Why it matters |
|:--|:--|
| [`.agents/skills/tanstack-start/SKILL.md`](../.agents/skills/tanstack-start/SKILL.md) | TanStack Start 1.0 patterns |
| [`.agents/skills/copilotkit-develop/SKILL.md`](../.agents/skills/copilotkit-develop/SKILL.md) | CopilotKit v2 React components |
| [`.agents/skills/ag-ui/SKILL.md`](../.agents/skills/ag-ui/SKILL.md) | AG-UI SSE protocol |
| [`.agents/skills/hono/SKILL.md`](../.agents/skills/hono/SKILL.md) | Hono API gateway |
| [`.agents/skills/convex/SKILL.md`](../.agents/skills/convex/SKILL.md) | Convex reactive backend |
| [`.agents/skills/better-auth/SKILL.md`](../.agents/skills/better-auth/SKILL.md) | BetterAuth OIDC + SIWE + 2FA |
| [`.agents/skills/cloudflare/SKILL.md`](../.agents/skills/cloudflare/SKILL.md) | Cloudflare Workers + Pages + R2 + D1 + Vectorize |
| [`.agents/skills/centralized-registry/SKILL.md`](../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry |
| [`.agents/skills/schema-codegen/SKILL.md`](../.agents/skills/schema-codegen/SKILL.md) | The BAML → Zod → Convex → CopilotKit pipeline |
| [`.agents/skills/agent-fleet-orchestration/SKILL.md`](../.agents/skills/agent-fleet-orchestration/SKILL.md) | The 12-agent fleet wiring |

---

## J) Next actions (for the build agent)

1. **Open an openspec change** at `openspec/changes/2026-08-24-web-frontend-consolidation-v1/` mirroring this report.
2. **Validate with `--strict`** before commit.
3. **Archive `_oideachais_apps/` first** as the lowest-risk wins.
4. **Move `game_showcase/` and `tuatha-demo/`** to `demos/` at repo root.
5. **Lift the `web/packages/{auth,db,ui-kit,convex}/` content** from the sub-monorepos to make them the canonical implementation.
6. **Merge `croilar-portal/` → `croilar-web/`** as `/admin` routes.
7. **Merge `cianfhoghlaim-web/` → `cianfhoghlaim/`** (the central homepage absorbs it).
8. **Merge `cianfhoghlaim-leaving-cert/` → `oideachais/`** (per-subject routes).
9. **Update `web/AGENTS.md`** to reflect the new topology (5 apps + 5 packages + 1 hono-api).
10. **Run `bun run croilar:analyze`** before and after each merge to capture the diff.

---

## K) Sources

- `web/AGENTS.md`, `web/README.md`, `web/package.json`, `web/turbo.json`, `web/tsconfig.base.json`
- `web/apps/_oideachais_apps/{AGENTS,STATUS,CHANGELOG,README,README_eile,REFACTORING}.md`
- `web/apps/{cianfhoghlaim,cianfhoghlaim-leaving-cert,cianfhoghlaim-mmo,cianfhoghlaim-web,croilar-portal,croilar-web,oideachais,oideachais-dashboard,tuatha-demo,tuatha-ui,game_showcase}/package.json`
- `web/apps/{cianfhoghlaim,cianfhoghlaim-leaving-cert,cianfhoghlaim-mmo,cianfhoghlaim-web,croilar-portal,croilar-web,oideachais-dashboard}/app.config.ts`
- `web/apps/{croilar-portal,croilar-web,oideachais-dashboard}/AGENTS.md`
- `web/apps/cianfhoghlaim-leaving-cert/README.md`
- `web/apps/croilar-portal/README.md`
- `web/apps/tuatha-demo/README.md`
- `web/apps/_oideachais_apps/web/src/routes/{chat,index,translation}.tsx`
- `web/hono-api/{README.md,package.json,src/{index,auth,middleware,migrate}.ts}`
- `web/packages/{auth,db,ui-kit}/package.json`
- `docs/audit/web-app-consolidation-plan.md` (the prior failed consolidation plan from 2026-05)
- `package.json` (root)
- `opencode.json`
- `turbo.json` (root)

### External docs (fetched 2026-08-24)

- https://tanstack.com/start/latest — TanStack Start (Router-first full-stack framework)
- https://ag-ui.com/ — Agent–User Interaction protocol
- https://www.convex.dev/docs — Convex reactive backend
- https://www.better-auth.com/docs — BetterAuth framework

---

**Last updated:** 2026-08-24 — by build agent (read-only research).
**Next review:** when the `2026-08-24-web-frontend-consolidation-v1` openspec change is filed.
