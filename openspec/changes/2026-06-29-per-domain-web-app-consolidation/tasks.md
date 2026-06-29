# Tasks: Per-Domain Web App Consolidation

## Phase 3.1: hono-api backend

- [x] 1.1 Move `web/hono-api/hono-api/` → `web/hono-api/` (17 files)
- [ ] 1.2 Populate `web/packages/packages/auth/` with the BetterAuth client
- [ ] 1.3 Wire croilar-web + croilar-portal to use `@croilar/auth`
- [x] 1.4 Document the 3 OIDC audiences: `convex_backend`, `croilar_web`, `croilar_portal`

### Chrome MCP validation (verified 2026-06-29)

- `chrome_navigate_page https://www.example.com` → 200, snapshot OK
- `chrome_lighthouse_audit` example.com → Accessibility 96, Best Practices 96, SEO 80, Agentic 100
- `chrome_navigate_page http://oideachais.cianfhoghlaim.ie` → 404 (production not deployed; local dev server not running in this sandbox)
- `chrome_navigate_page https://croilar.cianfhoghlaim.ie` → SSL cert error (private domain)

Conclusion: Chrome MCP works correctly. Per-app testing requires a running dev server
which is out of scope for this session; the test plan below documents the
expected commands for the 5 apps when they are deployed.

## Phase 3.2: croilar-web

- [ ] 2.1 Move `web/apps/croilar-web/` → `web/cio-web/croilar/` (NOTE: actual app lives at `web/apps/_croilar_apps/web/`; `web/apps/croilar-web/` is a README-only placeholder)
- [ ] 2.2 Use `@croilar/auth` from Phase 3.1
- [ ] 2.3 Convex schema in `web/cio-web/croilar/convex/`
- [ ] 2.4 TanStack Start routes in `web/cio-web/croilar/src/routes/`
- [ ] 2.5 Test with chrome (a11y ≥ 90, SEO ≥ 90, best practices ≥ 90)
  - `cd web/apps/_croilar_apps/web && bun run dev` (port 3003)
  - `chrome_navigate_page http://localhost:3003`
  - `chrome_take_snapshot` → verify TanStack Start routes render
  - `chrome_lighthouse_audit` → a11y/SEO/best practices
  - `chrome_performance_start_trace` → LCP, CLS, INP

## Phase 3.3: croilar-portal

- [ ] 3.1 Move `web/apps/croilar-portal/` → `web/cio-web/croilar-portal/`
- [ ] 3.2 Use `@croilar/auth` (org-scope checks for croilar-admin)
- [ ] 3.3 Dashboard variant
- [ ] 3.4 Test with chrome
  - `cd web/apps/_croilar_apps/portal && bun run dev` (port 3000)
  - `chrome_navigate_page http://localhost:3000`
  - `chrome_take_snapshot` → verify dashboard renders
  - `chrome_evaluate_script` to verify Convex state
  - `chrome_lighthouse_audit`

## Phase 3.4: tuatha-ui

- [ ] 4.1 Move `web/apps/tuatha-ui/` → `web/cio-web/tuatha/`
- [ ] 4.2 Babylon.js + R3F (3D Celtic MMO)
- [ ] 4.3 Test with chrome (60fps target via chrome_performance_start_trace)
  - `cd web/apps/tuatha-ui && bun run dev`
  - `chrome_navigate_page http://localhost:<port>`
  - `chrome_performance_start_trace` for 5s → check 60fps sustained
  - `chrome_evaluate_script` to inspect Babylon scene state

## Phase 3.5: oideachais-web (last, largest)

- [ ] 5.1 Move `web/apps/oideachais-web/` → `web/cio-web/oideachais/`
- [ ] 5.2 TanStack Start + Convex + CopilotKit + AG-UI
- [ ] 5.3 Agentic frontend (the most complex of the 5)
- [ ] 5.4 Test with chrome (full agent interaction E2E)
  - `cd web/apps/oideachais-web && bun run dev`
  - `chrome_navigate_page http://localhost:<port>`
  - `chrome_evaluate_script` to trigger a CopilotKit chat
  - `chrome_take_snapshot` → verify AG-UI streaming renders

## Phase 3.6: web/packages/ consolidation

- [ ] 6.1 `web/packages/packages/` → `web/packages/` (dedupe path)
- [ ] 6.2 Merge `packages/auth/` + `packages/db/` + `packages/ui/` + `packages/config/` + `packages/i18n/` + `packages/analytics/` into the canonical single-level layout

## Validation gate

- [ ] V.1 `openspec validate 2026-06-29-per-domain-web-app-consolidation --strict` exits 0
- [ ] V.2 `bun install` succeeds at the workspace root
- [ ] V.3 `bun run dev` launches all 5 apps on their canonical ports
