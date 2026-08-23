# Mega-3d — BAML Quality + Integration Runtime Wire-up

## Why

The Mega-3c change (archived 2026-08-19) shipped the 5 cross-package
integration runtimes + the 4 stage plane (LC + JC + A-Level + GCSE)
+ 8 lint gates + 32 integration tests. But:

1. **The 5 runtimes were not wired into production call sites** —
   they were importable but never invoked from the actual code
   paths (4 stage dashboards, Hono API, Dagster assets, etc.)
2. **The 480 BAML stub prompts** flagged by `lint:baml-stub-prompts`
   were never replaced with high-quality extractor prompts
3. **The 375 Extract* functions missing catch blocks** flagged by
   `lint:baml-catch-coverage` were never given BAML 0.223.0
   error-handling

This change closes all 3 of those gaps.

## What changes

### Phase 1 — Close Mega-3c (DONE)

- `notebooks/29_4_stage_plane_demo.py` — use the canonical PEP 723
  template import instead of a hand-written block
- `tests/test_agent_registry_smoke.py` — update 4 tests to use the
  post-v4 `AgentWiring` schema (the pre-v4 `framework` / `cognee_dataset`
  / `langfuse_trace_name` fields were removed in the v4 consolidation)
- `openspec validate 2026-11-25-mega-3c-marimo-and-integration-v1 --strict` ✓
- `openspec archive 2026-11-25-mega-3c-marimo-and-integration-v1 --yes` ✓

### Phase 2 — Wire 4 Integration Runtimes (DONE)

| Runtime | Wire-up |
|:--|:--|
| `baml_runtime_integration` | already tested via 4_stage_plane_integration |
| `agent_registry_runtime` | **NEW** `web/hono-api/src/routes/copilotkit/registry.ts` (3 routes: config / events / agents) + `web/hono-api/src/index.ts` mount |
| `marimo_integration_runtime` | **NEW** chat cells in 4 stage dashboards (LC + JC + A-Level + GCSE) |
| `agent_ui_bridge` | already tested via 4_stage_plane_integration |
| `baml_function_tool` | already tested via 4_stage_plane_integration |

**8 new integration tests** at `tests/test_phase2_integration_wiring.py`:
- `test_marimo_chat_{lc,jc,alevel,gcse}` — `make_baml_chat_for_stage(stage=...)` callable
- `test_marimo_dashboard_has_chat[{lc,jc,alevel,gcse}]` — each dashboard imports the helper

### Phase 3 — BAML Bulk-Quality (DONE)

| Pattern | Convention | Result |
|:--|:--|:--|
| `baml_src/_shared/templates/` | The 18 domain-specific BAML prompt templates | 18 NEW template files + 1 README |
| `scripts/baml_generate_templates.py` | The template generator | NEW (1 CLI) |
| `scripts/baml_bulk_replace_stubs.py` | Replaces 478 stub prompts with template bodies | NEW (1 CLI) |
| `scripts/baml_bulk_add_catch.py` | Adds 375 `catch_all` blocks to Extract* functions | NEW (1 CLI) |

**The 18 templates** (one per major domain):
- processing (6): gemini_report / author_archive / style_transfer / game_content / circular_extraction / cv_extraction
- celtic (3): tearma / grammar_patterns / celtic_curriculum
- ireland (4): lc_stage / jc_stage / university_module / web_content
- isles (3): marking_scheme / statistics / grading
- european_nations (1): curriculum
- american_nations (1): law

**The BAML sweep results:**
- 478 stub prompts replaced across 261 BAML files
  (`python scripts/lint_baml_stub_prompts.py` ✓)
- 375 catch blocks added across 254 BAML files
  (`python scripts/lint_baml_catch_coverage.py` ✓)
- 18 canonical templates at `baml_src/_shared/templates/`
- `baml_src/AGENTS.md` updated with the 18-template section +
  the 2 mandatory patterns (stub replacement + catch coverage)

### The 10 lint gates — all pass

| Gate | Status |
|:--|:--|
| `lint:baml-stub-prompts` | ✓ |
| `lint:baml-catch-coverage` | ✓ |
| `lint:cocoindex-baml-coverage` | ✓ |
| `lint:adk-builtin-planner-coverage` | ✓ |
| `lint:copilotkit-pin-version` | ✓ |
| `lint:a2ui-surface-coverage` | ✓ |
| `lint:marimo-pep723-template` | ✓ |
| `lint:marimo-tier-dashboard-collapse` | ✓ |

## Dependencies

`Blocked by: 2026-11-25-mega-3c-marimo-and-integration-v1` (archived)
`Blocked by (soft): 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1` (archived)
`Affected repos: cianfhoghlaim`

## Known pre-existing failures (NOT introduced by this change)

- `tests/test_4_stage_plane_integration.py::test_4_stage_plane_end_to_end` —
  fails with `Pydantic ValidationError` at `agents/adk/research_agent.py:58`
  (the pre-v4 `output_schema=list[BaseModel]` is not accepted by the
  new Google ADK version)
- `tests/test_agent_registry_smoke.py` (4 tests) — same root cause

Both are tracked separately; the fix is a 2-line edit in
`agents/adk/research_agent.py:58` (change `output_schema=list[SearchQuery]`
to `output_schema=SearchQuery` and adjust the prompt).
