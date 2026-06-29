# Tasks: Per-Domain Web App Consolidation

## Phase 3.1: hono-api backend

- [x] 1.1 Move `web/hono-api/hono-api/` → `web/hono-api/` (17 files)
- [ ] 1.2 Populate `web/packages/packages/auth/` with the BetterAuth client
- [ ] 1.3 Wire croilar-web + croilar-portal to use `@croilar/auth`
- [ ] 1.4 Document the 3 OIDC audiences: `convex_backend`, `croilar_web`, `croilar_portal`

## Phase 3.2: croilar-web

- [ ] 2.1 Move `web/apps/croilar-web/` → `web/cio-web/croilar/`
- [ ] 2.2 Use `@croilar/auth` from Phase 3.1
- [ ] 2.3 Convex schema in `web/cio-web/croilar/convex/`
- [ ] 2.4 TanStack Start routes in `web/cio-web/croilar/src/routes/`
- [ ] 2.5 Test with `chrome_navigate_page` + `chrome_lighthouse_audit` (a11y/SEO/best practices)

## Phase 3.3: croilar-portal

- [ ] 3.1 Move `web/apps/croilar-portal/` → `web/cio-web/croilar-portal/`
- [ ] 3.2 Use `@croilar/auth` (org-scope checks for croilar-admin)
- [ ] 3.3 Dashboard variant
- [ ] 3.4 Test with chrome

## Phase 3.4: tuatha-ui

- [ ] 4.1 Move `web/apps/tuatha-ui/` → `web/cio-web/tuatha/`
- [ ] 4.2 Babylon.js + R3F (3D Celtic MMO)
- [ ] 4.3 Test with chrome (chrome_performance_start_trace for 60fps target)

## Phase 3.5: oideachais-web (last, largest)

- [ ] 5.1 Move `web/apps/oideachais-web/` → `web/cio-web/oideachais/`
- [ ] 5.2 TanStack Start + Convex + CopilotKit + AG-UI
- [ ] 5.3 Agentic frontend (the most complex of the 5)
- [ ] 5.4 Test with chrome (full agent interaction E2E)

## Phase 3.6: web/packages/ consolidation

- [ ] 6.1 `web/packages/packages/` → `web/packages/` (dedupe path)
- [ ] 6.2 Merge `packages/auth/` + `packages/db/` + `packages/ui/` + `packages/config/` + `packages/i18n/` + `packages/analytics/` into the canonical single-level layout

## Validation gate

- [ ] V.1 `openspec validate 2026-06-29-per-domain-web-app-consolidation --strict` exits 0
- [ ] V.2 `bun install` succeeds at the workspace root
- [ ] V.3 `bun run dev` launches all 5 apps on their canonical ports
