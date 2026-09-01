# Change: Cianfhoghlaim-Nua Web Consolidation v1 — 5 apps → 1 consolidated `cianfhoghlaim-nua`

> **Status:** AUTHORED, ready for execution.
>
> **Phase 3 of 10** in the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`. The phase-by-phase authoring strategy (per
> operator direction 2026-09-01) means Phases 1-2 are already
> shipped:
>
> - `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` (Phase 1)
> - `2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1/` (Phase 2)
>
> **Anchor:** the
> [`openspec/specs/agentic-frontend-frameworks/spec.md`](../../specs/agentic-frontend-frameworks/spec.md)
> spec — the canonical home for the agent UI surface (CopilotKit +
> AG-UI + TanStack Start streaming + the 11-component A2UI catalog).

## Why

The Cianfhoghlaim web layer has accumulated 5 fragmented TanStack
Start / Vite apps over the 2026 build cycle:

1. `web/apps/cianfhoghlaim/` (the flagship with 7 subjects + BIEP v2/v3 routes)
2. `web/apps/oideachais/` (the British Isles portal with 14 LC + 8 JC + 9 GCSE + 15 A-Level subjects)
3. `web/apps/oideachais-dashboard/` (Vite + Convex admin dashboard)
4. `web/apps/tuatha/` (Vite + Convex MMO)
5. `web/apps/croilar-web/` (Vite + React public persona site)

Each app has its own `package.json`, `vite.config.ts`, `routes/`,
`components/chat/`, and `convex/`. The fragmentation:

- Triples the per-route shipping effort (a chat-with-syllabus
  route ships in 3 places).
- Prevents the canonical Phase 1 `StudyPlanCard` from being
  consumed by all 4 per-subject surfaces (only oideachais
  imports it).
- Prevents the new Phase 2 `@cianfhoghlaim/a2ui` catalog from
  being mounted once for the whole platform.
- Costs ~30s per `bun install` (5 workspaces) and ~20s per
  `bunx turbo typecheck` (5 typecheck invocations).
- Makes the canonical Hono API from `web/hono-api/` require 5
  different CORS configurations.

This change collapses the 5 apps into ONE consolidated
`web/apps/cianfhoghlaim-nua/` TanStack Start app with 6 route
groups (student + educator + researcher + author + mmo + admin),
backed by a single Convex deployment, a single Hono API
mount, and a single A2UI catalog mount.

The agent's earlier 3 apps (cianfhoghlaim + oideachais +
oideachais-dashboard) had this same fragmentation problem; the
W6 web consolidation (`2026-08-24-wave-6-tanstack-modernisation-v1`)
attempted to address it but only achieved the `agent-platform`
+ `croilar-portal` split, not the full consolidation. Phase 3
completes the W6 work.

## What changes

### §1 — Author the consolidated app skeleton (12 files)

- **§1.1** `web/apps/cianfhoghlaim-nua/package.json` — single
  package, depends on `@cianfhoghlaim/a2ui` (Phase 2) +
  `@cianfhoghlaim/ui-kit` + the 4 Phase 1 Convex tables.
- **§1.2** `web/apps/cianfhoghlaim-nua/tsconfig.json` — extends
  the root `tsconfig.base.json`.
- **§1.3** `web/apps/cianfhoghlaim-nua/src/index.ts` —
  `CIANFHOGLAIM_NUA_VERSION` + `ROUTE_GROUP_PATHS` constants.
- **§1.4** `web/apps/cianfhoghlaim-nua/app.config.ts` — single
  TanStack Start config (was duplicated in 5 places).
- **§1.5** `web/apps/cianfhoghlaim-nua/src/convex/schema.ts` —
  single Convex schema (re-exports the canonical schema from
  `web/packages/db/convex/schema.ts`).
- **§1.6** `web/apps/cianfhoghlaim-nua/src/convex/auth.ts` —
  single BetterAuth integration.
- **§1.7** `web/apps/cianfhoghlaim-nua/src/components/CianfhoghlaimOS.tsx`
  — the unified app shell (combines the 5 existing
  `Header`/`Sidebar`/`BIEPSubjectPage`/`CIANFHOGLAIMOS`/etc.
  components into one).
- **§1.8** `web/apps/cianfhoghlaim-nua/src/copilot/CopilotKitProvider.tsx`
  — single `<CopilotKit>` provider wrapping `createCatalog()`
  from `@cianfhoghlaim/a2ui`.
- **§1.9** `web/apps/cianfhoghlaim-nua/src/copilot/agui-bridge.ts`
  — AG-UI SSE bridge to the canonical Hono
  `/api/agui/sse` endpoint.
- **§1.10** `web/apps/cianfhoghlaim-nua/routes/__root.tsx` —
  single root layout (replaces the 5 duplicate root layouts).
- **§1.11** `web/apps/cianfhoghlaim-nua/routes/(student)/index.tsx`
  — student route group landing page.
- **§1.12** `web/apps/cianfhoghlaim-nua/routes/(educator)/index.tsx`
  — educator route group landing page.

### §2 — Migrate the 4 Phase 1 study-plan routes (4 files)

- **§2.1** `web/apps/oideachais/routes/lc/chemistry/study-plan.tsx`
  → `web/apps/cianfhoghlaim-nua/routes/(student)/lc/chemistry/study-plan.tsx`
- **§2.2** `web/apps/oideachais/routes/lc/mathematics/study-plan.tsx`
  → `web/apps/cianfhoghlaim-nua/routes/(student)/lc/mathematics/study-plan.tsx`
- **§2.3** `web/apps/oideachais/routes/lc/gaeilge/study-plan.tsx`
  → `web/apps/cianfhoghlaim-nua/routes/(student)/lc/gaeilge/study-plan.tsx`
- **§2.4** `web/apps/oideachais/routes/lc/computer_science/study-plan.tsx`
  → `web/apps/cianfhoghlaim-nua/routes/(student)/lc/computer_science/study-plan.tsx`

Each migrated route imports the `<StudyPlanCard>` + `<WeekTimeline>`
+ `<MilestoneBadge>` + `<KCWeightsBar>` A2UI components from
`@cianfhoghlaim/a2ui` (was the Phase 1 standalone
`oideachais/src/components/study-plan/StudyPlanCard.tsx`).

### §3 — Migrate the Phase 1 useStudyPlan hook + Hono stub (2 files)

- **§3.1** `web/apps/oideachais/src/hooks/useStudyPlan.ts`
  → `web/apps/cianfhoghlaim-nua/src/hooks/useStudyPlan.ts`
  (lifted into the consolidated app)
- **§3.2** `web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts`
  → `web/apps/cianfhoghlaim-nua/src/lib/study_plan_stub.ts`
  (lifted into the consolidated app)

### §4 — Mount the A2UI catalog (1 file)

- **§4.1** `web/apps/cianfhoghlaim-nua/src/copilot/CopilotKitProvider.tsx`
  wraps `createCatalog()` from `@cianfhoghlaim/a2ui`.

### §5 — Archive the 5 old apps (5 actions)

- **§5.1** `mv web/apps/cianfhoghlaim web/apps/_archive/cianfhoghlaim-pre-v6`
- **§5.2** `mv web/apps/oideachais web/apps/_archive/oideachais-pre-v6`
- **§5.3** `mv web/apps/oideachais-dashboard web/apps/_archive/oideachais-dashboard-pre-v6`
- **§5.4** `mv web/apps/tuatha web/apps/_archive/tuatha-pre-v6`
- **§5.5** `mv web/apps/croilar-web web/apps/_archive/croilar-web-pre-v6`

(The old apps are preserved in `web/apps/_archive/` for 1 release
cycle per the `retrospective-cleanup` spec, then deleted.)

### §6 — Update the web monorepo config (3 files)

- **§6.1** `web/turbo.json` — drop the 5 old app entries; add
  `cianfhoghlaim-nua`.
- **§6.2** `web/package.json` — drop the 5 old app workspace
  entries; add `cianfhoghlaim-nua`.
- **§6.3** `web/AGENTS.md` — update the routing table to point
  at `cianfhoghlaim-nua`.

### §7 — Spec delta to `agentic-frontend-frameworks` (1 file)

- **§7.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/specs/agentic-frontend-frameworks/spec.md`
  — adds 4 new Requirements:
    - "The Cianfhoghlaim web layer MUST be a single TanStack Start app"
    - "Route groups MUST be organised by audience"
    - "Old apps MUST be archived to `web/apps/_archive/`"
    - "The consolidated app MUST depend on `@cianfhoghlaim/a2ui`"

## Impact

- **Audience:** every Cianfhoghlaim user (students + educators
  + researchers + authors + MMO players + admins).
- **Scope:** 12 new files + 4 migrated routes + 2 migrated
  hooks/stubs + 5 archived apps + 3 updated config files.
- **LOC delta:** +~800 (new app) + ~250 (migrated routes) -
  ~5500 (archived apps).
- **Risk:** MEDIUM — the 5 archived apps must be reachable via
  redirects during the 1-release deprecation window. Phase 3
  ships the redirects via TanStack Start's `notFoundComponent`
  + `loader` mechanism.
- **Reversibility:** full — the archived apps can be restored
  from `web/apps/_archive/` if needed.

## Dependencies

`Blocked by (soft):`

- `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` (Phase 1)
  — the 4 Phase 1 study-plan routes are migrated to the
  consolidated app.
- `2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1/` (Phase 2) —
  the `createCatalog()` factory is consumed by the consolidated
  app's `<CopilotKit>` provider.

`Blocked by (hard):` none.

`Extends:`

- [`openspec/specs/agentic-frontend-frameworks/spec.md`](../../specs/agentic-frontend-frameworks/spec.md)
  — adds 4 Requirements to the canonical agent UI spec.

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale copy of `gemini_hackathon/web/` — lifted selectively
  per the operator's earlier directive (deeply-per-sister-repo
  customisation, NOT wholesale copies).
- NCCE learning-graph showcase — Phase 4.
- BAML/CocoIndex/DLT hardening — Phase 5.
- Voice/TTS oral delivery — Phase 6.
- LC/JC certificate pipeline — Phase 7.
- Sister-side mirrors — Phase 8 (the 5 sister-side umbrella mirrors
  promoted in Phase 0 are the canonical mirrors).
- GCP opt-in completion — Phase 9.
- From-the-ground-up v7 — Phase 10 (deferred).

## Quality gates (must pass before `openspec archive`)

```bash
uv run openspec validate 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 --strict
mise run lint:skills            # 167 skills pass
mise run lint:drift-docs        # no drift
cd web/apps/cianfhoghlaim-nua && bunx tsc --noEmit   # 0 TypeScript errors
cd web && bunx turbo typecheck                       # 0 errors
cd web && bunx turbo build                          # builds clean
```

---

*Last updated by build subagent at 2026-09-01.*