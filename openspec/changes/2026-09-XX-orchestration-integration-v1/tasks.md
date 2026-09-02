# Tasks — Cianfhoghlaim-Nua Orchestration Integration v1

> 5 sections, 19 tasks. All tasks MUST pass before
> `openspec archive 2026-09-XX-orchestration-integration-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [ ] **A.1** Author `proposal.md` + `tasks.md` + `specs/british-isles-education-pipeline/spec.md` delta (1 new Requirement)
- [ ] **A.2** `uv run openspec validate 2026-09-XX-orchestration-integration-v1 --strict` → exits 0

## Phase B — Hono planner service wire-up (§1, 3 tasks)

- [ ] **B.1** Replace
  `web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts` with
  the subprocess bridge `buildStudyPlanHandler(subject, defaultDurationWeeks, defaultLanguage)`
  + the `studyPlanStubResponse(subject, params)` fallback helper
- [ ] **B.2** Update the 4 LC route handlers (`chemistry.ts`,
  `mathematics.ts`, `gaeilge.ts`, `computer_science.ts`) to call
  `buildStudyPlanHandler(...)` instead of inlining the stub
  response. Route mounts in `web/hono-api/src/index.ts` stay
  unchanged
- [ ] **B.3** Verify the Hono bundle still type-checks:
  `cd web/hono-api && bun run typecheck` exits 0

## Phase C — Per-jurisdiction BAML extractor wire-up (§2, 3 tasks)

- [ ] **C.1** Author
  `orchestration/defs/2_materials/_base/jurisdiction_baml_extractor.py`
  with the 5 helpers: `JURISDICTION_BAML_FUNCTIONS`,
  `JURISDICTION_CONVEX_TABLES`, `read_pdf_text`,
  `get_jurisdiction_baml_fn`, `serialise_spec`,
  `materialise_subject_spec_to_convex`,
  `invoke_jurisdiction_extractor`
- [ ] **C.2** Update the 5 jurisdiction orchestrators
  ({england,wales,scotland,northern_ireland,isle_of_man}_assets.py)
  to use `invoke_jurisdiction_extractor(...)` instead of the
  `getattr(b, fn_name, None)` fallback. Each extraction asset's
  return value now includes `baml_extractions`,
  `extracted_count`, `convex_written_count`
- [ ] **C.3** Verify the 5 orchestrators no longer contain
  `getattr(b, baml_fn_name, None)` patterns

## Phase D — Convex deployment prep (§3, 4 tasks)

- [ ] **D.1** Author `web/apps/cianfhoghlaim-nua/convex.json` with
  the canonical Convex codegen + `convex/` functions path
- [ ] **D.2** Author the 5 jurisdiction Convex tables
  ({england,wales,scotland,northern_ireland,isle_of_man}_subject_specs)
  + their `create` mutations under
  `web/apps/cianfhoghlaim-nua/convex/jurisdictions/`
- [ ] **D.3** Extend `web/apps/cianfhoghlaim-nua/convex/schema.ts`
  with the 5 new tables (canonical 18-table schema: 4 root + 8
  per-subject + 5 jurisdiction subject_spec + 1 NCSE learning graph
  — wait, `ncce_learning_graphs` is the 5th root, so 5+8+5+1 = ... ;
  the actual count is **18 tables**: 4 root + 1 NCSE + 8 per-subject
  + 5 jurisdiction = 18)
- [ ] **D.4** Re-export the 5 new tables from
  `web/apps/cianfhoghlaim-nua/convex/jurisdictions/index.ts`

## Phase E — Test coverage (§4, 2 tasks)

- [ ] **E.1** Author `tests/test_phase11_orchestration_integration.py`
  with the canonical 8 tests:
  - `test_phase11_hono_planner_subprocess_handler_called`
  - `test_phase11_4_lc_routes_use_build_study_plan_handler`
  - `test_phase11_5_jurisdiction_orchestrators_use_canonical_baml`
  - `test_phase11_no_getattr_baml_fallback_remains`
  - `test_phase11_5_jurisdiction_convex_tables_wired`
  - `test_phase11_canonical_18_table_schema`
  - `test_phase11_convex_json_exists`
  - `test_phase11_5_jurisdiction_baml_functions_in_baml_client`
- [ ] **E.2** Run the canonical test suite:
  `pytest tests/test_phase11_orchestration_integration.py -v`
  → exits 0 with 8 passing tests

## Phase F — Validation + quality gates (§5, 4 tasks)

- [ ] **F.1** `uv run openspec validate 2026-09-XX-orchestration-integration-v1 --strict` exits 0
- [ ] **F.2** `pytest tests/test_phase11_orchestration_integration.py -v` runs 8 tests green
- [ ] **F.3** `pytest tests/test_adk_subject_actions.py -v` runs the 7 Phase 1 regression tests green
- [ ] **F.4** `dg list assets 2>&1 | grep -E "england|wales|scotland|northern_ireland|isle_of_man" | head -20` shows the 5 jurisdictions' assets

---

*Last updated by build subagent at 2026-09-01.*
