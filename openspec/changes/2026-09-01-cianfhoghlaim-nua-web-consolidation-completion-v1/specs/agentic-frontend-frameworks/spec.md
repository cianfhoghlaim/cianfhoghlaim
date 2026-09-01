## ADDED Requirements

### Requirement: The consolidated Cianfhoghlaim-Nua app MUST have a complete skeleton

The Cianfhoghlaim agentic-frontend-frameworks capability MUST
expose a fully-runnable consolidated web app at
`web/apps/cianfhoghlaim-nua/` with all 7 canonical skeleton files:

1. `routes/__root.tsx` — the TanStack Start root layout
2. `app.config.ts` — the TanStack Start build config
3. `src/convex/schema.ts` — re-exports the canonical 13-table schema from `@cianfhoghlaim/db/convex/schema`
4. `src/convex/auth.ts` — the BetterAuth → Convex `users` sync mutation
5. `src/copilot/agui-bridge.ts` — the AG-UI SSE bridge helper
6. `src/lib/study_plan_stub.ts` — the Phase 1 stub helper
7. `src/components/study-plan/StudyPlanCard.tsx` — the Phase 1 study-plan A2UI card

Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1
change (Phase 3 completion).

The 4 Hono study-plan endpoints (`/api/copilotkit/lc/{chemistry,mathematics,gaeilge,computer_science}`)
MUST be mounted in `web/hono-api/src/index.ts` so that
`useStudyPlan` (the Phase 1 React hook) does not 404.

The 5 old apps (`cianfhoghlaim` + `oideachais` + `oideachais-dashboard` +
`tuatha` + `croilar-web`) MUST be archived to
`web/apps/_archive/<app>-pre-v6/` for 1 release cycle per the
`retrospective-cleanup` spec.

#### Scenario: The consolidated app serves a study-plan request

- **WHEN** a user visits `oideachais.ie/lc/chemistry/study-plan`
- **THEN** the TanStack Start app boots successfully (no
  `__root.tsx` missing error)
- **AND** the `useStudyPlan` hook POSTs to
  `/api/copilotkit/lc/chemistry/get_study_plan`
- **AND** the Hono endpoint returns the Phase 1 stub response
  (the canonical `studyPlanStubResponse("chemistry", params)`)
- **AND** the `<StudyPlanCard>` A2UI surface renders the stub