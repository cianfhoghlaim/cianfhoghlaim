# Per-Domain Web App Consolidation Plan

> **Per user request ("4 per domain")** — consolidate 5 web apps (oideachais-web, tuatha-ui, croilar-web, croilar-portal, hono-api) per domain, not all at once.
> **Related:** Plan v6 Phase F8 (merge web), this is the per-domain subplan.

## 1. Current web apps

1. **oideachais-web** (`cianfhoghlaim/web/apps/oideachais-web/`) - TanStack Start + React public web app (the LARGEST)
2. **tuatha-ui** (`cianfhoghlaim/web/apps/tuatha-ui/`) - Tuatha educational MMO front-end
3. **croilar-web** (`cianfhoghlaim/web/apps/croilar-web/`) - Croílár multi-persona portfolio (public site)
4. **croilar-portal** (`cianfhoghlaim/web/apps/croilar-portal/`) - Croílár portfolio dashboard (admin)
5. **hono-api** (`cianfhoghlaim/web/hono-api/`) - Hono API gateway (backend)

## 2. Consolidated target

**Single web app:** `cianfhoghlaim/web/cio-web/` (a unified web app)
- TanStack Start + React (the oideachais-web stack)
- Hono API gateway embedded
- Multi-route:
  - `/` (oideachais public)
  - `/tuatha` (Tuatha MMO)
  - `/croilar` (Croílár portfolio)
  - `/croilar/admin` (Croílár admin)
  - `/api` (Hono API gateway routes)

## 3. Per-domain migration order (per user "4 per domain")

The user said "4 per domain" which I interpret as: do one domain at a time, in order.

### Domain 1: hono-api (backend first, smallest surface)
- Reason: 1st to migrate the API gateway which serves the others
- Effort: S (1 week)
- Files: `cianfhoghlaim/web/hono-api/**`
- Migration:
  1. Copy hono-api into `web/cio-web/api/`
  2. Wire hono-api routes into the TanStack Start server
  3. Test that all consumers (oideachais-web, tuatha-ui, croilar-web) can switch endpoints
  4. Cutover: delete old hono-api directory
- Risk: LOW (backend-only, mostly hidden from users)

### Domain 2: croilar-web (smallest public surface)
- Reason: 2nd smallest, single domain, low risk
- Effort: M (1-2 weeks)
- Files: `cianfhoghlaim/web/apps/croilar-web/**`
- Migration:
  1. Copy croilar-web into `web/cio-web/croilar/`
  2. Move routes from `/` to `/croilar/`
  3. Test cross-app links
  4. Cutover: delete old croilar-web
- Risk: LOW (small public site)

### Domain 3: croilar-portal (admin)
- Reason: continues croilar pattern, admin-only
- Effort: S (1 week)
- Files: `cianfhoghlaim/web/apps/croilar-portal/**`
- Migration:
  1. Copy croilar-portal into `web/cio-web/croilar/admin/`
  2. Add auth layer
  3. Test
  4. Cutover
- Risk: LOW (admin-only)

### Domain 4: tuatha-ui (medium surface, MMO complexity)
- Reason: MMO has specific game state requirements
- Effort: M (2 weeks)
- Files: `cianfhoghlaim/web/apps/tuatha-ui/**`
- Migration:
  1. Copy tuatha-ui into `web/cio-web/tuatha/`
  2. Move Babylon.js scene loader, MMO state, asset references
  3. Cross-link with oideachais data
  4. Cutover
- Risk: MED (Babylon.js + game state)

### Domain 5: oideachais-web (largest, most critical)
- Reason: Last because it has the most surface + critical features
- Effort: L (3-4 weeks)
- Files: `cianfhoghlaim/web/apps/oideachais-web/**`
- Migration:
  1. The existing oideachais-web BECOMES the core of `web/cio-web/`
  2. Update routes: existing routes stay at `/`, add multi-app routing
  3. Migrate remaining content
  4. Cutover: oideachais-web directory becomes legacy
- Risk: HIGH (largest public surface)

## 4. Total timeline

- 5 domains × average 1.5 weeks = 7.5 weeks
- With 1-person squad: 7-8 weeks
- With 2-person squad on parallel safe migrations: 5 weeks
- Per user: do sequentially (safer)

## 5. Per-domain validation criteria

For each domain cutover:
1. ✅ All existing routes still work (smoke test)
2. ✅ All API endpoints still work (smoke test)
3. ✅ Visual regression test (screenshot compare)
4. ✅ Performance baseline (within 5% of old)
5. ✅ No 404s in production logs
6. ✅ Old directory removed from git

## 6. Dependencies

- Requires Plan v5 Phase A (deploy foundations) DONE
- Requires Plan v5 Phase B (P0 + P1) DONE
- Per-domain: hono-api needs to come AFTER all 4 web apps are migrated to use the unified API patterns

## 7. Decisions needed before execution

1. **Reverse domain order** (start with largest, oideachais-web)? I recommend NO - my order (hono-api → croilar-web → croilar-portal → tuatha-ui → oideachais-web) is safest.
2. **Hono API gateway embedded or separate** in the unified app? I recommend embedded (single deploy).
3. **Cross-app navigation** - share a layout or each app has its own? I recommend shared layout with per-app routes.
4. **Auth** - single sign-on or per-app? I recommend SSO via Pocket ID (already deployed).
5. **Build system** - keep 5 separate Vite configs or 1 monorepo config? I recommend 1 monorepo config.
6. **Convex migration** - migrate all 3 Convex schemas at once or per-app? I recommend per-app.

## 8. Risk mitigation

- **Big-bang vs incremental**: Incremental (per user "4 per domain")
- **Staging environment**: Use `web-staging.cianfhoghlaim.ie` for 1 week per domain before production
- **Rollback plan**: Each domain has its own `git revert` capability
- **Monitoring**: Langfuse v3 traces per request to detect regressions

## 9. Post-cutover benefits

- Single `web/cio-web/` repo = single deployment pipeline
- Shared component library
- Unified auth
- Easier to add new domains (just add a route)
- Reduced dev time for new features
- Better performance (single bundle optimization)

## 10. Risks of NOT doing this

- 5 separate deployments to manage
- 5 separate auth systems
- 5 separate component libraries
- Duplicated code (likely 30-40% overlap between apps)
- Slower feature development (changes touch multiple codebases)
