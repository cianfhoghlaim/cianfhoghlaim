# Tasks: CopilotKit Action Wiring + Agent Chat Routes

## Phase 1 — Real handlers (5 tasks, ~3 hours)

- [ ] **T1.1** Read existing `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts` to identify the 13 stub actions
- [ ] **T1.2** Create `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/handlers/syllabus.ts` (handles getSyllabusTopics, lookupExamQuestion)
- [ ] **T1.3** Create `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/handlers/marking.ts` (handles getMarkingSchemeSummary, recommendNextTopic)
- [ ] **T1.4** Create `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/handlers/ocr.ts` (handles lookupOcrResult, compareOcrEngines)
- [ ] **T1.5** Create `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/handlers/learning_outcome.ts` (handles lookupLearningOutcome, searchBilingualLOPair, getStrandGraph)
- [ ] **T1.6** Create `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/handlers/student_progress.ts` (handles getStudentProgress, compareSubjects, summarizeCircular, recommendNextTopic)

## Phase 2 — Wire all actions (2 tasks, ~1 hour)

- [ ] **T2.1** Refactor `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts` to import + call the 5 handler modules
- [ ] **T2.2** Add `recommendNextTopic` (FalkorDB prerequisite graph lookup) — new action not in the original 14

## Phase 3 — Agent chat route (2 tasks, ~1 hour)

- [ ] **T3.1** Read `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/agents/$agent.tsx` (current metadata-only display)
- [ ] **T3.2** Replace metadata with `<CopilotKit agent={$agent}>` inline chat using existing AG-UI SSE runtime

## Phase 4 — Knowledge Graph Health tab (3 tasks, ~1 hour)

- [ ] **T4.1** Create `notebooks/28_knowledge_graph_health.py` (5-tab marimo notebook: aistear/primary/jc/sc/cross_stage ingestion timestamps)
- [ ] **T4.2** Add "Knowledge Graph Health" tab to `notebooks/00_control_panel.py`
- [ ] **T4.3** Wire Cognify sensors (from C2) to update the KG Health tab on file change

## Phase 5 — Validate (3 tasks, ~15 minutes)

- [ ] **T5.1** `openspec validate 2026-08-10-copilotkit-action-wiring-v1 --strict`
- [ ] **T5.2** `bun install && bun run typecheck` (LC web app)
- [ ] **T5.3** `mise run lint:registry && mise run lint:skills`

## Total

- **17 tasks** across **5 phases**
- **~6 hours of focused work**
- **5 new handler files** + **2 modified TSX files** + **2 new notebooks**
- **13 stub actions → real handlers**
