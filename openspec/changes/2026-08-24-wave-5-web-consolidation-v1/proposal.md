# 2026-08-24-wave-5-web-consolidation-v1

## Why

The 2026-08-24 master refactor plan identified Wave 5 as the **web apps
consolidation** — collapsing the 12 apps under `web/apps/` down to
5 consolidated apps with shared `web/packages/`.

Three structural problems motivate this change:

1. **Naming sprawl** — 5 inconsistent prefixes (`cianfhoghlaim-*`,
   `oideachais*`, `tuatha*`, `croilar*`, `_oideachais_apps`) where
   `"cianfhoghlaim"` alone refers to 4 different things
   (`cianfhoghlaim/`, `cianfhoghlaim-web/`, `cianfhoghlaim-mmo/`,
   `cianfhoghlaim-leaving-cert/`).

2. **Two massive sub-monorepos** — `cianfhoghlaim-web/` (10 MB) and
   `cianfhoghlaim-leaving-cert/` (2.4 GB) each contain their own
   `apps/web/ + apps/api/ + packages/{auth,config,db,convex,...}/`,
   completely duplicating the root `web/packages/*` workspace. The
   `croilar-web/` (35 MB) and `croilar-portal/` (265 MB) have the same
   problem.

3. **Dead weight** — `web/apps/_oideachais_apps/` (552 KB) is the
   legacy sruth-era workspace that was never cleaned up. It contains
   stale code that no longer compiles against the current root
   `web/packages/*`.

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| App merge mapping | `croilar-portal/ + croilar-web/ → croilar/`<br/>`cianfhoghlaim-web/ + cianfhoghlaim/ → cianfhoghlaim/`<br/>`cianfhoghlaim-leaving-cert/ + oideachais/ + oideachais-dashboard/ → oideachais/`<br/>`tuatha-ui/ → tuatha/`<br/>`_oideachais_apps/ → web/_archive/_oideachais_apps/` |
| Implementation scope | **Wave 5 = structural skeleton + safe moves** (3-5 day PR). The actual 2.4 GB `cianfhoghlaim-leaving-cert/` migration lands in a Wave 5 follow-up PR (the size makes it too risky for one PR). |
| Move strategy | `git mv` (preserves file history) + `_archive/` for dead weight |
| Shared packages | Lift from sub-monorepos into root `web/packages/*` (auth, db, ui-kit, api-client, contracts) |

## Dependencies

`Blocked by: 2026-08-24-wave-4-ducklake-v1-hardening-v1` (✅ landed commit `7bb26496f`)
`Unblocks: 2026-08-24-wave-6-frontend-tanstack-modernisation-v1`
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes

### 1. Archive `_oideachais_apps/` (safe, 552 KB)

```
git mv web/apps/_oideachais_apps/ web/_archive/_oideachais_apps/
```

This is the smallest, safest move. The directory is stale sruth-era
code that no longer compiles.

### 2. Merge `tuatha-ui/` (60 MB) → `tuatha-demo/` (32 KB)

The canonical Tuatha demo app is `tuatha-demo/`. The 60 MB `tuatha-ui/`
is the same app duplicated. Merge by moving `tuatha-ui/src/*` into
`tuatha-demo/src/`, then `git rm -rf web/apps/tuatha-ui`.

(The merge is performed in this PR; the 60 MB is mostly node_modules
which git ignores.)

### 3. Document + skeleton the larger merges (NOT executed in this PR)

These moves are TOO LARGE (2.4 GB) for a single PR. Wave 5 documents
the merge plan in the openspec spec and creates the canonical target
directories with `__init__.py` + minimal `package.json` placeholders.
The actual 2.4 GB migration lands in Wave 5 follow-up PRs.

| Canonical target | Sources to merge |
|:--|:--|
| `web/apps/cianfhoghlaim/` | `cianfhoghlaim-web/`, `cianfhoghlaim-mmo/`, `cianfhoghlaim/` |
| `web/apps/oideachais/` | `cianfhoghlaim-leaving-cert/`, `oideachais/`, `oideachais-dashboard/` |
| `web/apps/croilar/` | `croilar-portal/`, `croilar-web/` |
| `web/apps/tuatha/` | `tuatha-demo/`, `tuatha-ui/` (already merged) |
| `web/apps/game_showcase/` | (kept as-is) |

### 4. Shared packages (lift from sub-monorepos)

The 3 sub-monorepos (`cianfhoghlaim-web/`, `cianfhoghlaim-leaving-cert/`,
`croilar-portal/`) each carry their own `packages/{auth,config,db,convex,...}/`.
Wave 5 documents the canonical layout:

```
web/packages/
├── auth/            # Better Auth (consolidates 3 installs)
├── db/              # Convex (consolidates 3 deployments)
├── ui-kit/          # Radix UI + Tailwind (consolidates 3 installs)
├── api-client/      # TanStack AI/DB/Form + CopilotKit v2 + AG-UI (NEW)
└── contracts/       # Shared TS types (NEW)
```

The actual lift is deferred to Wave 5 follow-up PRs because it
requires updating every `import` statement across the sub-monorepos.

### 5. Documentation

- `web/AGENTS.md` — updated to document the new app layout
- `web/turbo.json` — updated workspaces
- `web/package.json` — updated workspaces

## Out of scope (deferred to Wave 5 follow-up PRs)

- **Actual migration of `cianfhoghlaim-leaving-cert/`** (2.4 GB) into
  `oideachais/` — too large for one PR. Split across 2-3 follow-up PRs.
- **Actual migration of `croilar-portal/`** (265 MB) into `croilar/`
  — split across 1-2 follow-up PRs.
- **Actual migration of `cianfhoghlaim-mmo/`** (55 MB, Babylon.js + SpacetimeDB)
  — split across 1 follow-up PR.
- **Shared packages lift** — deferred until the per-app merges complete.
- **`turbo.json` / `package.json` workspace rewrites** — deferred
  until the apps are merged.
- **TanStack Start / AG-UI / CopilotKit v2 wiring** — that's Wave 6.

## Verification

After Wave 5 lands:

1. `git mv web/apps/_oideachais_apps/ web/_archive/_oideachais_apps/`
   succeeds (the legacy dir is no longer at `web/apps/`)
2. `web/apps/tuatha-ui/` is gone (merged into `tuatha-demo/`)
3. `ls web/apps/` shows the 5 canonical app targets (with placeholders
   for the larger merges)
4. `web/AGENTS.md` documents the new layout
5. `openspec/changes/2026-08-24-wave-5-web-consolidation-v1/specs/web-consolidation/spec.md`
   defines the full merge requirements

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Wave 0: `openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/`
- Wave 1: `openspec/changes/2026-08-24-wave-1-dlt-sources-domain-restructure-v1/`
- Wave 2: `openspec/changes/2026-08-24-wave-2-orchestration-vertical-pipelines-v1/`
- Wave 3: `openspec/changes/2026-08-24-wave-3-cocoindex-v0-stragglers-v1/`
- Wave 4: `openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1/`
