# Per-Domain Web App Consolidation

## Why

The v4 consolidation (2026-06-28) merged all 5 former `sruth/<quadrant>/`
quadrants into the single `cianfhoghlaim/` package, but left several
web/ doubled directory paths as residue:

- `cianfhoghlaim/web/hono-api/hono-api/` → `cianfhoghlaim/web/hono-api/`
- `cianfhoghlaim/web/packages/packages/` → `cianfhoghlaim/web/packages/`
- `cianfhoghlaim/web/packages/packages/auth/` → consolidate with
  `cianfhoghlaim/web/apps/oideachais-web/packages/auth/`
- `cianfhoghlaim/web/packages/packages/ui/src/components/ui/` →
  `cianfhoghlaim/web/packages/ui/src/`

Additionally, the 5 web apps (croilar-web, croilar-portal, tuatha-ui,
oideachais-web, game_showcase) have overlapping BetterAuth + Convex +
TanStack Start configurations that should be consolidated into a
shared `web/cio-web/` package (or similar).

## What Changes

### Phase 3.1: hono-api backend (this change)

- Move `web/hono-api/hono-api/` → `web/hono-api/`
- Populate `web/packages/packages/auth/` with the BetterAuth client
  that wraps the hono-api's `auth.ts`
- Wire the croilar-web + croilar-portal to use `@croilar/auth`
- Document the 3 OIDC audiences: `convex_backend`, `croilar_web`,
  `croilar_portal`

### Phase 3.2: croilar-web

- Move to `web/cio-web/croilar/` (or similar shared layout)
- Use `@croilar/auth` from Phase 3.1
- Convex schema in `web/cio-web/croilar/convex/`
- TanStack Start routes in `web/cio-web/croilar/src/routes/`
- Test with `chrome_navigate_page` + `chrome_lighthouse_audit`

### Phase 3.3: croilar-portal

- Move to `web/cio-web/croilar-portal/`
- Use `@croilar/auth` (org-scope checks for croilar-admin)
- Dashboard variant
- Test with chrome

### Phase 3.4: tuatha-ui

- Move to `web/cio-web/tuatha/`
- Babylon.js + R3F (3D Celtic MMO)
- Test with chrome (chrome_performance_start_trace for 60fps target)

### Phase 3.5: oideachais-web (last, largest)

- Move to `web/cio-web/oideachais/`
- TanStack Start + Convex + CopilotKit + AG-UI
- Agentic frontend (the most complex of the 5)
- Test with chrome (full agent interaction E2E)

### Phase 3.6: web/packages/ consolidation

- `web/packages/packages/` → `web/packages/` (dedupe path)
- Merge `packages/auth/` + `packages/db/` + `packages/ui/` + `packages/config/` + `packages/i18n/` + `packages/analytics/` into the canonical single-level layout

## Validation

- `bun install` succeeds at the workspace root
- `bun run dev` launches all 5 apps on their canonical ports
- `chrome_navigate_page http://localhost:3000` shows croilar-web
- `chrome_lighthouse_audit` returns a11y ≥ 90, SEO ≥ 90, best practices ≥ 90
- `openspec validate 2026-06-29-per-domain-web-app-consolidation --strict` passes

## Why per-domain and not big-bang

Each web app has its own deployment timeline, port, and tech stack.
Trying to merge all 5 in one go would require:
- Coordinating 5+ Dockerfile + docker-compose changes
- Touching the live oideachais-web (the largest, most critical)
- Risking 3-4 hours of merge conflicts

The per-domain approach (3.1 → 3.5) lets us:
- Validate the hono-api + auth consolidation before touching the apps
- Test each app independently with chrome
- Roll back one app without breaking the others

## Out of scope

- The legacy `docs/legacy/crypteolas/ui/` (deleted by the v4 merge;
  any stragglers will be cleaned up by a separate "stale-pipelines-cleanup" change).
- The `spaces/` sub-project (separate repos; see #96 follow-up issue).
