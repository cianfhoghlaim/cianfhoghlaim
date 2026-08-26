# web-consolidation Specification

## Purpose

`web-consolidation` is a capability of the Cianfhoghlaim platform
that codifies the canonical web apps layout. After this spec is
implemented:

- 5 consolidated apps (`cianfhoghlaim`, `oideachais`, `croilar`,
  `tuatha`, `game_showcase`) — was 12 (plus 2 demo apps)
- 3 shared packages (auth, db, ui-kit) at root `web/packages/`
- Single `hono-api/` gateway (consolidates 3 gateways)
- Single Better Auth + Convex deployment
- Legacy `_oideachais_apps/` archived to `web/_archive/`

This spec captures Wave 5 of the 2026-08-24 master refactor plan.

## Requirements

### Requirement: Legacy archive

`web/apps/_oideachais_apps/` SHALL be moved to `web/_archive/_oideachais_apps/`.

#### Scenario: _oideachais_apps is archived

- **WHEN** `ls web/apps/_oideachais_apps` runs
- **THEN** the result is "No such file or directory"
- **AND** `ls web/_archive/_oideachais_apps/` succeeds

### Requirement: tuatha-ui renamed to tuatha

`web/apps/tuatha-ui/` SHALL be renamed to `web/apps/tuatha/`.

#### Scenario: tuatha-ui is gone

- **WHEN** `ls web/apps/tuatha-ui` runs
- **THEN** the result is "No such file or directory"
- **AND** `ls web/apps/tuatha/` shows the React + TanStack Start files

### Requirement: Canonical app layout

After all Wave 5 follow-up PRs land, the web/apps/ directory SHALL
contain exactly 7 directories:

| Path | Purpose |
|:--|:--|
| `web/apps/cianfhoghlaim/` | Central homepage (merged from `cianfhoghlaim-web/` + `cianfhoghlaim-mmo/` + `cianfhoghlaim/`) |
| `web/apps/oideachais/` | Content app (merged from `cianfhoghlaim-leaving-cert/` + `oideachais/` + `oideachais-dashboard/`) |
| `web/apps/croilar/` | Portfolio app (merged from `croilar-portal/` + `croilar-web/`) |
| `web/apps/tuatha/` | Celtic MMO (was `tuatha-ui/`, renamed in Wave 5) |
| `web/apps/game_showcase/` | Game showcase (kept as-is) |
| `web/apps/cianfhoghlaim-mmo/` | Standalone Babylon.js + SpacetimeDB client (kept until Wave 5 follow-up PR) |
| `web/apps/tuatha-demo/` | Python Túatha demo (separate concern, kept as-is) |

#### Scenario: 5 + 2 canonical apps

- **WHEN** Wave 5 is complete (all follow-up PRs landed)
- **THEN** `ls web/apps/` shows exactly 7 directories
- **AND** each canonical app has a `package.json` + `src/` + `tsconfig.json`

### Requirement: Single shared packages

The 3 shared packages (auth, db, ui-kit) SHALL live at
`web/packages/{auth,db,ui-kit}/`. Each sub-monorepo's `packages/{auth,db,convex,...}/`
SHALL be lifted into the root `web/packages/`.

#### Scenario: 3 shared packages at root

- **WHEN** `ls web/packages/` runs
- **THEN** the result includes `auth/`, `db/`, `ui-kit/`
- **AND** the Wave 6 follow-up adds `api-client/` + `contracts/`

### Requirement: Single hono-api gateway

The 3 sub-monorepos (cianfhoghlaim-web, cianfhoghlaim-leaving-cert, croilar-portal)
each carry their own `apps/api/` directory. Wave 5 follow-up PRs
SHALL consolidate all per-app `apps/api/` directories into the
single root `web/hono-api/`.

#### Scenario: 1 hono-api at root

- **WHEN** `find web -maxdepth 5 -name "apps" -type d` runs
- **THEN** exactly 1 directory named `apps` exists (or 0 if apps are flattened)

### Requirement: Single Better Auth install

The 3 sub-monorepos each install better-auth independently. Wave 5
follow-up PRs SHALL consolidate to 1 install at `web/packages/auth/`.

#### Scenario: 1 Better Auth install

- **WHEN** `grep -r '"better-auth":' web/apps web/packages 2>/dev/null | wc -l` runs
- **THEN** the count is 1 (after Wave 5 follow-up PRs)

### Requirement: Single Convex deployment

The 3 sub-monorepos each have their own `convex/` directory. Wave 5
follow-up PRs SHALL consolidate to 1 deployment at
`web/packages/db/convex/`.

#### Scenario: 1 Convex deployment

- **WHEN** `find web -maxdepth 5 -name "convex.json" | wc -l` runs (after Wave 5 follow-up PRs)
- **THEN** the count is 1

### Requirement: Documentation

The `web/AGENTS.md` SHALL be updated to document:
- The 5 consolidated apps (canonical targets)
- The 3 shared packages at root `web/packages/`
- The single `hono-api/` gateway
- The archived `_oideachais_apps/` at `web/_archive/`

#### Scenario: AGENTS.md reflects new layout

- **WHEN** `grep -E "apps/(oideachais|croilar|cianfhoghlaim|tuatha|game_showcase)" web/AGENTS.md` runs
- **THEN** the canonical 5 apps are mentioned

### Requirement: Migration tooling

The Wave 5 PR SHALL include `scripts/wave_5_consolidate_web.py`
that automates the per-app merges. The script is run manually
per merge (NOT in this PR — too large for one PR).

### Requirement: Migration verification

For each per-app merge (Wave 5 follow-up PRs), the migration SHALL
verify:
- All imports still resolve
- `bun install` succeeds
- `bun run typecheck` succeeds (no type errors)
- `bun run build` succeeds
- The shared `web/packages/*` are reachable from the merged app

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Existing consolidation spec (pre-Wave 5): `openspec/specs/web-monorepo-consolidation/spec.md`
