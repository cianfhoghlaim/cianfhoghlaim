# Tasks — Cianfhoghlaim-Nua End-to-End Showcase v1

> 5 sections, 34 tasks. All tasks MUST pass before
> `openspec archive 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [ ] **A.1** Author `proposal.md` + `tasks.md` + `specs/oideachais-pipeline/spec.md` delta
- [ ] **A.2** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 --strict` → exits 0

## Phase B — Canonical study-plan surface (§1, 3 tasks)

- [ ] **B.1** Author `baml_src/british_isles/_shared/study_plan.baml`
  with `StudyPlan + ExtractStudyPlan + GenerateStudyPlanAssets`
  classes — porting the 6 legacy
  `baml_src/british_isles/ireland/education/_legacy/web/<subject>_web.baml`
  into a single canonical schema
- [ ] **B.2** Author `agents/adk/subjects/lc/planner.py` with
  `generate_study_plan(parameters) -> StudyPlanResponse` callable
  that wraps `b.GenerateStudyPlanAssets(...)` and rehydrates the
  Convex `study_plans` row
- [ ] **B.3** Author `baml_src/british_isles/_shared/oral_study_plan.baml`
  with `GenerateOralStudyPlan(text_plan, dialect) -> OralStudyPlan`
  for Phase 6 (oral delivery); stubbed callable in Phase 1

## Phase C — Fix the broken stubs (§2, 6 tasks)

- [ ] **C.1** Fix `orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py:326`
  to call consolidated `b.GenerateSubjectQuestPack(...)` instead of
  per-subject `Generate{prefix}QuestPack`
- [ ] **C.2** Replace the broken `from agents.knowledge_graph import
  HybridSearchConfig` import in `agents/api/routes/routes/search.py`
  with `from agents.meaisinfhoghlaim.firecrawl_mcp.memory.router
  import MemoryRouter`
- [ ] **C.3** Replace the broken `from cianfhoghlaim.storage.cognify.rules
  import semantic_search as ss` import in
  `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py` with
  the same `MemoryRouter` re-export
- [ ] **C.4** Replace the `pass # TODO` body of
  `agents/adk/voice_agent.py::process_audio()` with a wired Pipecat
  client + ChatterboxTTS dispatch stub (logs the round-trip;
  Phase 6 wires the real TTS)
- [ ] **C.5** Replace the stub body of
  `agents/_workflow_handlers.py::dispatch_study_plan` with a real
  call to `agents.adk.subjects.lc.planner.generate_study_plan`
- [ ] **C.6** Add FTS indexes to the LanceDB `ireland_lc_*_chunks`
  tables

## Phase D — Convex schema + per-subject wire-ups (§3, 5 tasks)

- [ ] **D.1** Extend `web/packages/db/convex/schema.ts` with
  `study_plans + quest_packs + oral_study_plans` tables (Phase 1
  scope; the remaining 3 tables come in Phase 4/6)
- [ ] **D.2** Wire
  `web/hono-api/src/routes/copilotkit/lc/{chemistry, mathematics,
  gaeilge, computer_science}.ts` `POST /get_study_plan` to
  `agents.adk.subjects.lc.planner`
- [ ] **D.3** Wire `web/apps/oideachais/src/lib/copilotkit/lc/{chemistry,
  mathematics, gaeilge, computer_science}.ts` `useCopilotAction({name:
  "get_study_plan", ...})` handler to the same planner
- [ ] **D.4** Replace placeholder content of
  `web/apps/oideachais/routes/lc/{chemistry, mathematics, gaeilge,
  computer_science}/study-plan.tsx` with a real `<StudyPlanCard>`
  A2UI surface (Phase 1 ships a basic placeholder; Phase 2 fills
  in the full 11-component catalog)
- [ ] **D.5** Verify end-to-end via `pytest tests/test_adk_subject_actions.py`

## Phase E — Subject end-to-end showcases (§4, 16 tasks = 4 subjects × 4 tasks)

### Chemistry (showcase default; matches `JOURNEY_DEFAULT_SUBJECT=chemistry_lc`)

- [ ] **E.1.1** `baml_src/british_isles/ireland/education/marking/chemistry_marking.baml`
  reuses the canonical `StudyPlan` schema
- [ ] **E.1.2** `agents/adk/subjects/lc/chemistry.py` registers
  13 actions
- [ ] **E.1.3** `web/apps/oideachais/routes/lc/chemistry/index.tsx`
  mounts per-subject chat + marimo + PDF library
- [ ] **E.1.4** `notebooks/lc/chemistry.py` adds a "study-plan
  demo" cell calling `planner.generate_study_plan(...)`

### Mathematics (broadest student audience)

- [ ] **E.2.1** `baml_src/british_isles/ireland/education/marking/mathematics_marking.baml`
  reuses the canonical `StudyPlan` schema
- [ ] **E.2.2** `agents/adk/subjects/lc/mathematics.py` registers
  13 actions
- [ ] **E.2.3** `web/apps/oideachais/routes/lc/mathematics/index.tsx`
  mounts per-subject chat + marimo + PDF library
- [ ] **E.2.4** `notebooks/lc/mathematics.py` adds a "study-plan
  demo" cell

### Gaeilge (oral-first subject; ships the dialect dispatch stub)

- [ ] **E.3.1** `baml_src/british_isles/ireland/education/marking/gaeilge_marking.baml`
  reuses the canonical `StudyPlan` schema + `dialect` field
- [ ] **E.3.2** `agents/adk/subjects/lc/gaeilge.py` registers
  13 actions + `process_oral_dialect` (Phase 6 fills the TTS)
- [ ] **E.3.3** `web/apps/oideachais/routes/lc/gaeilge/index.tsx`
  mounts per-subject chat + marimo + PDF library + oral-player
  placeholder
- [ ] **E.3.4** `notebooks/lc/gaeilge.py` adds a "study-plan demo"
  cell + an "oral plan preview" cell (Phase 6 fills audio)

### Computer Science (the newest NCCA LC subject)

- [ ] **E.4.1** `baml_src/british_isles/ireland/education/marking/computer_science_marking.baml`
  reuses the canonical `StudyPlan` schema
- [ ] **E.4.2** `agents/adk/subjects/lc/computer_science.py` registers
  13 actions
- [ ] **E.4.3** `web/apps/oideachais/routes/lc/computer_science/index.tsx`
  mounts per-subject chat + marimo + PDF library
- [ ] **E.4.4** `notebooks/lc/computer_science.py` adds a
  "study-plan demo" cell

## Phase F — Validation + quality gates (§5, 5 tasks)

- [ ] **F.1** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 --strict` exits 0
- [ ] **F.2** `mise run lint:registry` reports 0 drift
- [ ] **F.3** `mise run lint:skills` reports 167 skills pass
- [ ] **F.4** `pytest tests/test_adk_subject_actions.py -v` runs
  4 per-subject integration tests green
- [ ] **F.5** `dg list assets 2>&1 | grep -E "lc_extraction|study_plan"`
  shows the fixed materialisations succeed

## Phase G — BAML Primary alias confirmation (§6, 1 task)

- [ ] **G.1** Confirm `baml_src/clients.baml` +
  `baml_src/clients_biep_v3.py` use the `Primary` BAML alias;
  the new `study_plan.baml` + `oral_study_plan.baml` reuse the
  alias with `unavailable-to-provide` retry policy

---

*Last updated by build subagent at 2026-09-01.*