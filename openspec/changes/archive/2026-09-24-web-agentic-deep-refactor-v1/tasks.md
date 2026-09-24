# Tasks: 2026-09-24-web-agentic-deep-refactor-v1

## 1. Stage A — Drizzle schema extension (3 files)

- [ ] **A1** `web/hono-api/src/db/schema.ts` — add `project` + `student` + 6 agentic tables + `teacher_workload` + `class_registry` + `class_roster`
- [ ] **A2** `web/hono-api/src/db/client.ts` — add type aliases for the new tables
- [ ] **A3** `web/hono-api/src/db/migrations/2026-09-24-k12-agentic-tables.sql` — DDL (SQLite-flavor compatible)

## 2. Stage B — Per-app CopilotKit surface unification (4 files)

- [ ] **B1** `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/_base.ts` — the canonical Tool type + defineTool + callAgentRegistryRuntime + devFallbackConfig
- [ ] **B2** `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/index.ts` — barrel re-export
- [ ] **B3** `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/actions.ts` — the 18 canonical actions (6 leaving-cert + 4 diagram + 2 3D-asset + 1 cross-subject + 1 SCR commentary + 4 stage-specific + 2 misc) with REAL handlers
- [ ] **B4** `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/runtime.ts` — add /actions endpoint
- [ ] **B5** `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts` — re-export the canonical 13 actions + add 14th
- [ ] **B6** `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/_base.ts` — NEW: the shared base

## 3. Stage C — Stage router unification (3 files)

- [ ] **C1** `web/apps/_shared/copilotkit/stage_router.ts` — NEW: canonical shared module
- [ ] **C2** `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/stage_router.ts` — MODIFY: re-export
- [ ] **C3** `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/stage_router.ts` — MODIFY: re-export

## 4. Stage D — Agent registry end-to-end wire-up (2 files)

- [ ] **D1** `web/hono-api/src/routes/copilotkit/registry.ts` — MODIFY: add dev fallback + /schema + /handshake endpoints
- [ ] **D2** `web/hono-api/src/routes/copilotkit/index.ts` — NEW: barrel re-export

## 5. Stage E — Directory rename (1 file moved)

- [ ] **E1** `git mv web/apps/_archive/_oideachais_apps web/apps/_archive/cianfhoghlaim-pre-v6`

## 6. Stage F — READMEs + skill (3 files)

- [ ] **F1** `web/AGENTS.md` — MODIFY: document AG-UI wire-up + shared module
- [ ] **F2** `web/apps/_shared/copilotkit/README.md` — NEW: the shared module guide
- [ ] **F3** `.agents/skills/copilotkit-agui-bridge/SKILL.md` — NEW: the AG-UI bridge router skill

## 7. Stage G — Openspec change + verification (5 files)

- [ ] **G1** `openspec/changes/2026-09-24-web-agentic-deep-refactor-v1/proposal.md`
- [ ] **G2** `openspec/changes/2026-09-24-web-agentic-deep-refactor-v1/tasks.md`
- [ ] **G3** `openspec/changes/2026-09-24-web-agentic-deep-refactor-v1/specs/copilotkit-agentic-surface/spec.md`
- [ ] **G4** `openspec/changes/2026-09-24-web-agentic-deep-refactor-v1/specs/drizzle-agentic-schema/spec.md`
- [ ] **G5** `openspec/changes/2026-09-24-web-agentic-deep-refactor-v1/cross-repo-sync.md`
- [ ] **G6** `openspec validate --strict` exits 0
- [ ] **G7** `openspec archive --yes`
- [ ] **G8** `git commit + git push`
