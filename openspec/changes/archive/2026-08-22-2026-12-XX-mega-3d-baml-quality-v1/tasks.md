# Mega-3d Tasks

## Phase 1 — Close Mega-3c (DONE)

- [x] **T1.1** Fix `notebooks/29_4_stage_plane_demo.py` to use the canonical
  PEP 723 template import (replaces hand-written PEP 723 block)
- [x] **T1.2** Update `tests/test_agent_registry_smoke.py` (4 tests) for
  the post-v4 `AgentWiring` schema
- [x] **T1.3** Run `openspec validate 2026-11-25-mega-3c-marimo-and-integration-v1 --strict` ✓
- [x] **T1.4** Run `openspec archive 2026-11-25-mega-3c-marimo-and-integration-v1 --yes` ✓
- [x] **T1.5** Commit + push the Phase 1 changes

## Phase 2 — Wire 4 Integration Runtimes (DONE)

- [x] **T2.1** Wire `marimo_integration_runtime.make_baml_chat_for_stage`
  into the 4 stage dashboards:
  - `notebooks/19_ireland_pipeline_dashboard.py` (LC)
  - `notebooks/19_junior_cycle_pipeline_dashboard.py` (JC)
  - `notebooks/20_england_alevel_pipeline_dashboard.py` (A-Level)
  - `notebooks/20_england_gcse_pipeline_dashboard.py` (GCSE)
- [x] **T2.2** Wire `agent_registry_runtime` into the Hono API:
  - `web/hono-api/src/routes/copilotkit/registry.ts` (NEW)
  - `web/hono-api/src/index.ts` (mount the new route)
  - 3 routes: `/config`, `/events`, `/agents`
- [x] **T2.3** `baml_runtime_integration` + `agent_ui_bridge` already
  covered by `tests/test_4_stage_plane_integration.py`
- [x] **T2.4** Add 8 new integration tests in
  `tests/test_phase2_integration_wiring.py`
- [x] **T2.5** Commit + push the Phase 2 changes

## Phase 3 — BAML Bulk-Quality (DONE)

- [x] **T3.1** Create `baml_src/_shared/templates/` (NEW directory)
- [x] **T3.2** Write 18 domain-specific BAML templates
- [x] **T3.3** Build `scripts/baml_generate_templates.py` (NEW CLI)
- [x] **T3.4** Build `scripts/baml_bulk_replace_stubs.py` (NEW CLI)
  - 478 stubs replaced across 261 files ✓
- [x] **T3.5** Build `scripts/baml_bulk_add_catch.py` (NEW CLI)
  - 375 catch blocks added across 254 files ✓
- [x] **T3.6** Update `baml_src/AGENTS.md` with the 18-template section
- [x] **T3.7** Commit + push the Phase 3 changes

## Verification (DONE)

- [x] `python scripts/lint_baml_stub_prompts.py` → OK
- [x] `python scripts/lint_baml_catch_coverage.py` → OK
- [x] `python scripts/lint_cocoindex_baml_coverage.py` → OK
- [x] `python scripts/lint_adk_builtin_planner_coverage.py` → OK
- [x] `python scripts/lint_copilotkit_pin_version.py` → OK
- [x] `python scripts/lint_a2ui_surface_coverage.py` → OK
- [x] `python scripts/lint_marimo_pep723_template.py` → OK
- [x] `python scripts/lint_marimo_tier_dashboard_collapse.py` → OK
- [x] `python -m pytest tests/test_phase2_integration_wiring.py` → 8/8 pass
- [x] `python -m pytest tests/test_agent_registry_smoke.py` → 4/4 pass (post-v4 fields)

## Follow-up (deferred to separate change)

- [ ] Fix `agents/adk/research_agent.py:58` (Pydantic ValidationError:
  `output_schema=list[SearchQuery]` should be `output_schema=SearchQuery`)
- [ ] Re-run `tests/test_4_stage_plane_integration.py::test_4_stage_plane_end_to_end`
  after the research_agent fix
