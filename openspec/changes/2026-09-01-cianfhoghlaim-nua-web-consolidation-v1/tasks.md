# Tasks — Cianfhoghlaim-Nua Web Consolidation v1

> 7 sections, 30 tasks. All tasks MUST pass before
> `openspec archive 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [ ] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [ ] **A.2** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 --strict` exits 0

## Phase B — Author the consolidated app skeleton (§1, 12 files)

- [ ] **B.1** `web/apps/cianfhoghlaim-nua/package.json`
- [ ] **B.2** `web/apps/cianfhoghlaim-nua/tsconfig.json`
- [ ] **B.3** `web/apps/cianfhoghlaim-nua/src/index.ts` (CIANFHOGLAIM_NUA_VERSION + ROUTE_GROUP_PATHS)
- [ ] **B.4** `web/apps/cianfhoghlaim-nua/app.config.ts` (single TanStack Start config)
- [ ] **B.5** `web/apps/cianfhoghlaim-nua/src/convex/schema.ts` (re-exports `web/packages/db/convex/schema.ts`)
- [ ] **B.6** `web/apps/cianfhoghlaim-nua/src/convex/auth.ts` (single BetterAuth integration)
- [ ] **B.7** `web/apps/cianfhoghlaim-nua/src/components/CianfhoghlaimOS.tsx` (unified app shell)
- [ ] **B.8** `web/apps/cianfhoghlaim-nua/src/copilot/CopilotKitProvider.tsx` (wraps `createCatalog()`)
- [ ] **B.9** `web/apps/cianfhoghlaim-nua/src/copilot/agui-bridge.ts`
- [ ] **B.10** `web/apps/cianfhoghlaim-nua/routes/__root.tsx`
- [ ] **B.11** `web/apps/cianfhoghlaim-nua/routes/(student)/index.tsx`
- [ ] **B.12** `web/apps/cianfhoghlaim-nua/routes/(educator)/index.tsx`

## Phase C — Migrate the 4 Phase 1 study-plan routes (§2, 4 files)

- [ ] **C.1** `web/apps/oideachais/routes/lc/chemistry/study-plan.tsx` → `web/apps/cianfhoghlaim-nua/routes/(student)/lc/chemistry/study-plan.tsx`
- [ ] **C.2** `web/apps/oideachais/routes/lc/mathematics/study-plan.tsx` → `web/apps/cianfhoghlaim-nua/routes/(student)/lc/mathematics/study-plan.tsx`
- [ ] **C.3** `web/apps/oideachais/routes/lc/gaeilge/study-plan.tsx` → `web/apps/cianfhoghlaim-nua/routes/(student)/lc/gaeilge/study-plan.tsx`
- [ ] **C.4** `web/apps/oideachais/routes/lc/computer_science/study-plan.tsx` → `web/apps/cianfhoghlaim-nua/routes/(student)/lc/computer_science/study-plan.tsx`

Each migrated route MUST import the 4 A2UI components from
`@cianfhoghlaim/a2ui` (StudyPlanCard + WeekTimeline +
MilestoneBadge + KCWeightsBar).

## Phase D — Migrate the Phase 1 useStudyPlan hook + Hono stub (§3, 2 files)

- [ ] **D.1** `web/apps/oideachais/src/hooks/useStudyPlan.ts` → `web/apps/cianfhoghlaim-nua/src/hooks/useStudyPlan.ts`
- [ ] **D.2** `web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts` → `web/apps/cianfhoghlaim-nua/src/lib/study_plan_stub.ts`

## Phase E — Mount the A2UI catalog (§4, 1 task)

- [ ] **E.1** `web/apps/cianfhoghlaim-nua/src/copilot/CopilotKitProvider.tsx` wraps `createCatalog()` from `@cianfhoghlaim/a2ui`

## Phase F — Archive the 5 old apps (§5, 5 actions)

- [ ] **F.1** `mv web/apps/cianfhoghlaim web/apps/_archive/cianfhoghlaim-pre-v6`
- [ ] **F.2** `mv web/apps/oideachais web/apps/_archive/oideachais-pre-v6`
- [ ] **F.3** `mv web/apps/oideachais-dashboard web/apps/_archive/oideachais-dashboard-pre-v6`
- [ ] **F.4** `mv web/apps/tuatha web/apps/_archive/tuatha-pre-v6`
- [ ] **F.5** `mv web/apps/croilar-web web/apps/_archive/croilar-web-pre-v6`

## Phase G — Update the web monorepo config (§6, 3 files)

- [ ] **G.1** `web/turbo.json` — drop the 5 old app entries; add `cianfhoghlaim-nua`
- [ ] **G.2** `web/package.json` — drop the 5 old app workspace entries; add `cianfhoghlaim-nua`
- [ ] **G.3** `web/AGENTS.md` — update the routing table

## Phase H — Spec delta (§7, 1 file)

- [ ] **H.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/specs/agentic-frontend-frameworks/spec.md` — 4 ADDED Requirements

## Phase I — Validation + quality gates (§8, 5 tasks)

- [ ] **I.1** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 --strict` exits 0
- [ ] **I.2** `mise run lint:skills` reports 167 skills pass
- [ ] **I.3** `cd web/apps/cianfhoghlaim-nua && bunx tsc --noEmit` reports 0 TypeScript errors
- [ ] **I.4** `cd web && bunx turbo typecheck` reports 0 errors across all packages
- [ ] **I.5** `cd web && bunx turbo build` builds clean

---

*Last updated by build subagent at 2026-09-01.*