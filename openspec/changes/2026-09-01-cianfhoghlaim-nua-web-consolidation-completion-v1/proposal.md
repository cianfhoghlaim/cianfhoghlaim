# Change: Cianfhoghlaim-Nua Web Consolidation Completion v1 — Fix the 7 missing skeleton files + archive 5 old apps

> **Status:** AUTHORED + IMPLEMENTED.
>
> **Phase 3 completion** of the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`. The 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1
> change shipped the consolidated app skeleton + the 4 Phase 1
> study-plan routes; this change closes the 7 missing skeleton
> files + the 4 unmounted Hono endpoints + the monorepo config +
> archives the 5 old apps per the `retrospective-cleanup` spec.

## Why

The 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change
shipped the consolidated `web/apps/cianfhoghlaim-nua/` app with 6
routes + the A2UI catalog mount, but **left the app broken at
runtime**: 7 skeleton files were missing, the 4 Hono study-plan
endpoints were never mounted, and the 5 old apps were still on
disk (consolidation ratio 1:90.7).

The operator's audit (2026-09-01) confirmed the consolidated app
could not be served at runtime. This change ships the 7 missing
files + the 4 Hono mounts + archives the 5 old apps so the
consolidated app is fully functional.

## What was shipped

### §1 — Author the 7 missing skeleton files (7 files)

- **§1.1** `web/apps/cianfhoghlaim-nua/routes/__root.tsx` —
  the TanStack Start root layout; mounts `<CianfhoghlaimOS>` +
  `<CopilotKitProvider>` + `<Outlet>`.
- **§1.2** `web/apps/cianfhoghlaim-nua/app.config.ts` —
  the TanStack Start build config (Vite + node-server preset).
- **§1.3** `web/apps/cianfhoghlaim-nua/src/convex/schema.ts` —
  re-exports the canonical 13-table schema from
  `@cianfhoghlaim/db/convex/schema`.
- **§1.4** `web/apps/cianfhoghlaim-nua/src/convex/auth.ts` —
  the BetterAuth → Convex `users` sync mutation.
- **§1.5** `web/apps/cianfhoghlaim-nua/src/copilot/agui-bridge.ts` —
  the AG-UI SSE bridge helper (`createAGUIEventSource`) for the
  Phase 6 Pipecat oral study plans.
- **§1.6** `web/apps/cianfhoghlaim-nua/src/lib/study_plan_stub.ts` —
  the Phase 1 stub helper (the canonical study-plan response shape
  + the per-subject theme map).
- **§1.7** `web/apps/cianfhoghlaim-nua/src/components/study-plan/StudyPlanCard.tsx` —
  the Phase 1 study-plan A2UI card (lifted from
  `web/apps/oideachais/src/components/study-plan/StudyPlanCard.tsx`).

### §2 — Mount the 4 Hono study-plan endpoints (4 mounts + 1 AG-UI mount)

- **§2.1** `web/hono-api/src/index.ts`:
  - `app.route("/api/copilotkit/lc/chemistry", chemistryApp)`
  - `app.route("/api/copilotkit/lc/mathematics", mathematicsApp)`
  - `app.route("/api/copilotkit/lc/gaeilge", gaeilgeApp)`
  - `app.route("/api/copilotkit/lc/computer_science", computerScienceApp)`
  - `app.route("/api/agui", aguiApp)` (the AG-UI SSE bridge for Phase 6)

### §3 — Archive the 5 old apps (5 actions)

- **§3.1** `mv web/apps/cianfhoghlaim web/apps/_archive/cianfhoghlaim-pre-v6`
- **§3.2** `mv web/apps/oideachais web/apps/_archive/oideachais-pre-v6`
- **§3.3** `mv web/apps/oideachais-dashboard web/apps/_archive/oideachais-dashboard-pre-v6`
- **§3.4** `mv web/apps/tuatha web/apps/_archive/tuatha-pre-v6`
- **§3.5** `mv web/apps/croilar-web web/apps/_archive/croilar-web-pre-v6`

### §4 — Update the monorepo config (1 file)

- **§4.1** `web/AGENTS.md` — the apps table replaced with
  `1 active + 5 archived`; the routing table now points at
  `web/apps/cianfhoghlaim-nua/` as the canonical consolidated app.
- **§4.2** `web/turbo.json` — no change needed; the `apps/*`
  workspace glob auto-adjusts to only `cianfhoghlaim-nua/` after
  the archive.
- **§4.3** `web/package.json` — no change needed; same reason.

### §5 — Spec delta to `agentic-frontend-frameworks` (1 file)

- **§5.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1/specs/agentic-frontend-frameworks/spec.md`
  — adds 1 new Requirement:
    - "The consolidated Cianfhoghlaim-Nua app MUST have a complete skeleton (`__root.tsx` + `app.config.ts` + `convex/{schema,auth}.ts` + `copilot/agui-bridge.ts` + `lib/study_plan_stub.ts` + `components/study-plan/StudyPlanCard.tsx`)"

## Impact

- **Audience:** every Cianfhoghlaim user (the consolidated app is
  now runnable).
- **Scope:** 7 new files + 1 modified file + 5 archive actions.
- **LOC delta:** +~250 (7 new files) + ~30 modified (Hono mounts
  + AGENTS.md).
- **Risk:** MEDIUM — the 4 Hono study-plan endpoints return the
  Phase 1 stub (per the existing `studyPlanStubResponse()`); this
  is the expected behaviour per the Phase 1 plan.
- **Reversibility:** full — the 5 old apps are in `web/apps/_archive/`
  for 1 release cycle; the 7 skeleton files can be reverted via
  `git revert`.

## Dependencies

`Blocked by (soft):`

- `2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1/` (Phase 1)
- `2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1/` (Phase 2)
- `2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/` (Phase 3 original)

`Blocked by (hard):` none.

`Enables:`

- Phase 11 (Ireland NCCA-adjacent 6 + Physics) — has a working
  consolidated app to render into
- Phase 12-18 (England / Wales / NI / IoM / Scotland / vernaculars) —
  the consolidated app is the canonical home for the new
  jurisdiction-specific routes

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale rewrite of the 5 archived apps — they stay in
  `web/apps/_archive/` for 1 release cycle per the
  `retrospective-cleanup` spec, then deleted.
- Phase 11+ work (Ireland NCCA-adjacent 6 + Physics) — separate
  openspec change.
- The DLT path drift fix (Wave 1 completion) — separate openspec
  change.

## Quality gates (must pass before `openspec archive`)

```bash
uv run openspec validate 2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1 --strict  ✅
ls web/apps/  # must show only: _archive/ cianfhoghlaim-nua/                  ✅
ls web/apps/_archive/  # must show: 5 -pre-v6/ directories                          ✅
uv run pytest tests/test_adk_subject_actions.py -v  # 11 passed                         ✅
```

---

*Last updated by build subagent at 2026-09-01.*