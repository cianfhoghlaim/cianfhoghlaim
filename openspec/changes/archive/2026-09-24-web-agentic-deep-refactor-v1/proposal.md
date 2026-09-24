# Change: 2026-09-24-web-agentic-deep-refactor-v1

## Why

The web + agentic surface (`web/`) declares TanStack Start + CopilotKit + AG-UI
+ Hono + Convex + oRPC + Cloudflare (per `web/AGENTS.md`), but the current
implementation has 3 gaps that need converging:

1. **Stubbed actions**: The 13 + 14 canonical actions in
   `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts:223`
   + the per-router `actions.ts` stubs in
   `web/apps/cianfhoghlaim-web/apps/api/src/routers/{aistear,primary,...}.ts`
   all return `{topics: [], message: "Stub: ..."}` — no real data.
2. **Agent registry wire-up is stubbed**: The
   `web/hono-api/src/routes/copilotkit/registry.ts:111` shells out to
   `python -c "..."` with no in-process fallback, so dev mode without
   Python breaks.
3. **Naming drift**: `web/apps/_archive/_oideachais_apps/` (the v6
   archive) is ambiguous with the live `oideachais-web/` (the
   active TanStack Start app). Renaming to
   `_archive/cianfhoghlaim-pre-v6/` removes the ambiguity.

The Drizzle schema (`web/hono-api/src/db/schema.ts:82`) also lacks the
K-12 agentic tables — the 5 teacher workflows + 5 student workflows
shipped in the 2026-09-23-k12-teacher-student-pipeline-v1 + the
2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1 changes need a persistence
layer for the per-user state.

## What Changes

### Code — Drizzle schema + migrations (5 files)

- `web/hono-api/src/db/schema.ts` — MODIFY: add `project` + `student` + 6
  agentic workflow tables (agent_lesson_plan, agent_homework_item,
  agent_cba_plan, agent_wellbeing_checkin, agent_exam_timetable,
  agent_sen_record) + `teacher_workload` + `class_registry` + `class_roster`
- `web/hono-api/src/db/client.ts` — MODIFY: add type aliases for the
  new tables (`Student`, `NewStudent`, `AgentLessonPlan`, etc.)
- `web/hono-api/src/db/migrations/2026-09-24-k12-agentic-tables.sql` —
  NEW: the DDL (SQLite-flavor compatible with Cloudflare D1)

### Code — Per-app CopilotKit surface unification (6 files)

- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/_base.ts` —
  NEW: the canonical Tool type + defineTool + callAgentRegistryRuntime
  + devFallbackConfig (in-process mirror)
- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/index.ts` —
  NEW: barrel re-export
- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/actions.ts` —
  NEW: the canonical 18 actions (6 leaving-cert + 4 diagram +
  2 3D-asset + 1 cross-subject + 1 SCR commentary + 4 stage-specific +
  2 misc) with REAL handlers (db.execute on LanceDB / MotherDuck /
  R2)
- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/runtime.ts` —
  MODIFY: add /actions endpoint that returns the canonical ALL_ACTIONS
- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/stage_router.ts` —
  MODIFY: re-export from `web/apps/_shared/copilotkit/stage_router.ts`
- `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts` —
  MODIFY: re-export the canonical 13 actions from the shared base

### Code — Stage router unification (3 files)

- `web/apps/_shared/copilotkit/stage_router.ts` — NEW: the canonical
  shared module
- `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/stage_router.ts` —
  MODIFY: re-export
- `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/stage_router.ts` —
  MODIFY: re-export

### Code — Agent registry end-to-end wire-up (3 files)

- `web/hono-api/src/routes/copilotkit/registry.ts` — MODIFY: add
  in-process dev fallback (uses devFallbackConfig from _base.ts);
  add /schema + /handshake endpoints; respect COPILOTKIT_DEV_MODE
  env var
- `web/hono-api/src/routes/copilotkit/index.ts` — NEW: barrel
  re-export (optional)
- `agents/integrations/agent_registry_runtime.py` — (no change — the
  Python helpers already exist)

### Code — Directory rename (1 file moved)

- `web/apps/_archive/_oideachais_apps/` → `web/apps/_archive/cianfhoghlaim-pre-v6/`

### Code — READMEs + new skill (3 files)

- `web/AGENTS.md` — MODIFY: document the AG-UI wire-up + the shared
  CopilotKit module
- `web/apps/_shared/copilotkit/README.md` — NEW: the shared CopilotKit
  + AG-UI module guide
- `.agents/skills/copilotkit-agui-bridge/SKILL.md` — NEW: the AG-UI
  bridge router skill

### New openspec specs (2 files)

- `openspec/changes/2026-09-24-web-agentic-deep-refactor-v1/specs/copilotkit-agentic-surface/spec.md`
- `openspec/changes/2026-09-24-web-agentic-deep-refactor-v1/specs/drizzle-agentic-schema/spec.md`

## Out of scope (follow-up changes)

1. `openspec/changes/2026-09-25-copilotkit-convex-sse-v1/` — Convex real-time SSE
   wire-up (the canonical @convex/* + CopilotKit SSE pattern)
2. `openspec/changes/2026-09-26-copilotkit-a2ui-tanstack-ai-v1/` — A2UI components
   (concrete visualizers for the 4 diagram actions + the 2 3D-asset actions)
3. `openspec/changes/2026-09-27-bq-warehouse-emit-v1/` — emit agentic outputs to
   BigQuery (per agent-valley chapter 5)

## Dependencies

`Blocked by (soft): 2026-09-23-k12-teacher-student-pipeline-v1/`
(the K-12 agentic workflows that need the schema).
`Blocked by (soft): 2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/`
(the 3 Pillar root orchestrators that produce the agentic outputs).
`Affected repos: cianfhoghlaim (single repo)`.

## Cross-repo sync

Single-repo change. No sister-repo coordination required.

## Verification

1. `cd web && bun install && bun run typecheck && bun run lint` exit 0
2. The Drizzle migration runs cleanly (PGlite local + Cloudflare D1 remote)
3. The 18 actions in `actions.ts` return real data via Drizzle (not stubs)
4. The agent_registry_runtime.py helpers are callable from the Hono route (in-process fallback in dev)
5. The AG-UI handshake endpoint returns the registered agents + events
6. The stage_router.ts resolves to the canonical Python stage_teams
7. The directory rename `_oideachais_apps/` → `cianfhoghlaim-pre-v6/` lands cleanly
8. `openspec validate 2026-09-24-web-agentic-deep-refactor-v1 --strict` exits 0
9. `git commit + push` lands `web-agentic-deep-refactor-v1: ...`
