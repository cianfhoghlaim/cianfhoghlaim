# Tasks — Mega-3a

## Phase 1: BAML 0.223.0 Feature Adoption (Week 1)

### TASK-M3A-1.1 — Adopt `spawn` + `await` for the 4-path OCR ensemble
- **Status**: pending
- **Files**: `baml_src/british_isles/england/education/ensembled_extraction.baml` (~120 LOC)
- **What**: The 4 paths (BAML + Unstract + qwen3-vl-8b + gemma-4) run as `spawn` blocks; the ensemble awaits all 4 results.
- **Reference**: `docs/baml-demos/baml-deep-research-demo/baml_src/research.baml`
- **Impact**: 4× speedup (~350s → ~120s for the ensemble)

### TASK-M3A-1.2 — Adopt concurrent function calls (race qwen3-vl-8b vs gemma-4)
- **Status**: pending
- **Files**: `baml_src/british_isles/england/education/ensembled_extraction.baml`
- **What**: Race `LocalVisionQwen3vl` vs `LocalVisionGemma4`; cancel the slower.

### TASK-M3A-1.3 — Adopt `catch` / `catch_all` for the 6 LC extractors
- **Status**: pending
- **Files**: `baml_src/british_isles/ireland/education/lc_extraction/*.baml`
- **What**: Every `Extract*` function uses `catch_all (_) { <fallback> }` to degrade gracefully on per-call failure.
- **Replaces**: Hard-fail behavior (the 6 LC extractors currently fail hard on any malformed field)

### TASK-M3A-1.4 — Adopt `render_null_as="-1"` for `source_pages`, `year`, `total_marks`
- **Status**: pending
- **Files**: 6 LC extractor return types
- **What**: Replace `null` serialization with `-1` for missing fields (per the 0.223.0 output format option).

### TASK-M3A-1.5 — Adopt intersection bounds `T extends Document + Bilingual + HasMetadata`
- **Status**: pending
- **Files**: `baml_src/british_isles/_cross/multi_nation_curriculum.baml`
- **What**: Replace 4 near-identical extraction functions with 1 generic.

### TASK-M3A-1.6 — Adopt host callables: `run_lct6_query(introspect, execute, render_chart)`
- **Status**: pending
- **Files**: New BAML function for the marimo lineage viewer
- **What**: Python owns the MotherDuck credentials; BAML owns the SQL chart logic.

### TASK-M3A-1.7 — Adopt `image` / `pdf` multimodal inputs
- **Status**: pending
- **Files**: `baml_src/british_isles/ireland/education/pdfs/root_pdf_extraction.baml`
- **What**: Replace the embed→string→BAML handoff with direct PDF input.

### TASK-M3A-1.8 — Adopt `@assert` BAML test blocks in the 8 NCCA qpack generators
- **Status**: pending
- **Files**: `baml_src/british_isles/_shared/qpack_template.baml`
- **What**: Every generated qpack has `assert.baml_lo_code matches /LC-.../-LO-\d+/` validation.

### TASK-M3A-1.9 — Add 5 new lint gates (`lint:baml-stub-prompts`, `lint:baml-catch-coverage`, etc.)
- **Status**: pending
- **Files**: `scripts/lint_baml_*.py` (5 new scripts)
- **What**: E.1-E.5 from the roadmap — 5 new lint gates that prevent regression.

## Phase 2: 4 Stage BAML Templates (Weeks 2-4)

### TASK-M3A-2.1 — Build `lc_extraction_template.baml` (the LC 14-subject template)
- **Status**: pending
- **Files**: `baml_src/british_isles/_shared/lc_extraction_template.baml` (~250 LOC)
- **What**: 1 template that parameterises the 14 LC subjects via `{% if subject == "x" %}` blocks. Replaces the 6 `lc_extraction/*.baml` files.
- **Replaces**: 1,287 LOC
- **Net**: -1,037 LOC

### TASK-M3A-2.2 — Build `junior_cycle_template.baml` (the JC 8-subject template)
- **Status**: pending
- **Files**: `baml_src/british_isles/_shared/junior_cycle_template.baml` (~200 LOC)
- **What**: 1 template for the 8 NCCA Junior Cycle subjects. Replaces the 6 `junior_cycle/*.baml` files.
- **Replaces**: 518 LOC
- **Net**: -318 LOC

### TASK-M3A-2.3 — Build `alevel_extraction_template.baml` (the A-Level 15-subject template)
- **Status**: pending
- **Files**: `baml_src/british_isles/_shared/alevel_extraction_template.baml` (~250 LOC)
- **What**: 1 template for the 15 A-Level subjects × 3 boards (AQA + OCR + Edexcel).
- **Replaces**: ~1,500 LOC (the 15 `a_level_extraction/*.baml` files)
- **Net**: -1,250 LOC

### TASK-M3A-2.4 — Build `gcse_extraction_template.baml` (the GCSE 9-subject template)
- **Status**: pending
- **Files**: `baml_src/british_isles/_shared/gcse_extraction_template.baml` (~250 LOC)
- **What**: 1 template for the 9 GCSE subjects × 3 boards.
- **Replaces**: ~900 LOC (the 9 `gcse_extraction/*.baml` files)
- **Net**: -650 LOC

### TASK-M3A-2.5 — Build `qpack_template.baml` (the cross-stage qpack template)
- **Status**: pending
- **Files**: `baml_src/british_isles/_shared/qpack_template.baml` (~250 LOC)
- **What**: 1 template for ALL 4 stages' qpack generators. Replaces the 8 `qpack_*.baml` files.
- **Replaces**: 2,670 LOC
- **Net**: -2,420 LOC

### TASK-M3A-2.6 — Add the 8 NCCA Junior Cycle subjects at full scope
- **Status**: pending
- **Files**: `baml_src/british_isles/_shared/junior_cycle_template.baml` + 8 BAML functions
- **What**: JC Mathematics + English + Gaeilge + Science + Geography + History + CSPE + SPHE. Each gets:
 - 1 BAML function in the Junior Cycle template
 - 1 CocoIndex App (lands in Mega-3b)
 - 1 ADK agent (`jc_subject_agent`)
 - 1 A2UI surface (lands in Mega-3b)
- **Replaces**: Hand-written per-subject BAML files
- **Net**: -1,200 LOC

## Phase 3: Test Coverage (Week 5)

### TASK-M3A-3.1 — Add 6 test blocks for the 5 canonical lc6 functions
- **Status**: pending
- **Files**: 6 `test "name" { functions [...] }` blocks

### TASK-M3A-3.2 — Add ensemble test blocks for the 4-path OCR
- **Status**: pending
- **Files**: `baml_src/british_isles/england/education/ensembled_extraction.baml`

### TASK-M3A-3.3 — Add host-callable test blocks for `run_lct6_query`
- **Status**: pending
- **Files**: New BAML test fixtures

### TASK-M3A-3.4 — Add regression test blocks for the 7 BIEP CocoIndex v1 flows
- **Status**: pending

### TASK-M3A-3.5 — Wire `baml-cli test` to CI via `mise run baml:test`
- **Status**: pending

## Phase 4: Advanced BAML Features (Week 6)

(M3A-1.5 through M3A-1.8 above)

## Phase 5: Integration Touchpoints (Weeks 7-8)

### TASK-M3A-5.1 — Wire BAML into the 7 BIEP CocoIndex v1 flows
- **Status**: pending
- **Files**: `cocoindex_flows/biep_parity/*.py`

### TASK-M3A-5.2 — Wire BAML into the 42 Dagster assets
- **Status**: pending
- **Files**: `orchestration/defs/2_materials/england_education/`

### TASK-M3A-5.3 — Wire BAML `image` / `pdf` into the 6-stage PDF pipeline
- **Status**: pending

### TASK-M3A-5.4 — Wire the 5 lc6 functions to the 6 marimo notebooks
- **Status**: pending
- **Files**: `notebooks/19_ireland_pipeline_dashboard.py` etc.

### TASK-M3A-5.5 — Wire BAML extractor outputs to the 4 MotherDuck Dives
- **Status**: pending

### TASK-M3A-5.6 — Wire the TypeScript client to the croilar-portal UI
- **Status**: pending

### TASK-M3A-5.7 — Wire the SSE streaming endpoint to the BIEP v3 lineage viewer
- **Status**: pending

### TASK-M3A-5.8 — Wire BAML `Collector` into the 7 BIEP CocoIndex flows
- **Status**: pending

### TASK-M3A-5.9 — Wire BAML `image` outputs to the 12-agent fleet
- **Status**: pending

## Phase 6: Tooling + Observability (Weeks 9-10)

### TASK-M3A-6.1 — Wire `Collector` as the canonical BAML trace surface
- **Status**: pending

### TASK-M3A-6.2 — Add RAGAS-style evaluator BAML test blocks
- **Status**: pending

### TASK-M3A-6.3 — Add `baml:report` — per-extraction Snapshot report
- **Status**: pending

### TASK-M3A-6.4 — Add Langfuse prompt-template versioning
- **Status**: pending

### TASK-M3A-6.5 — Add MLflow trace integration for the BIEP v3 ensemble
- **Status**: pending

## Phase 7: ADK Agent Adoption (Weeks 9-10)

### TASK-M3A-7.1 — Adopt `SequentialAgent` for the 12-agent bootstrap
- **Status**: pending

### TASK-M3A-7.2 — Adopt `ParallelAgent` for the 4-path OCR ensemble
- **Status**: pending

### TASK-M3A-7.3 — Adopt `LongRunningFunctionTool` for the dagster trigger + CocoIndex re-index + MotherDuck DML
- **Status**: pending

### TASK-M3A-7.4 — Adopt the `before_model_callback` + `after_model_callback` pattern
- **Status**: pending

### TASK-M3A-7.5 — Adopt `instruction_provider` (function-form)
- **Status**: pending

### TASK-M3A-7.6 — Adopt `ToolContext.state` for the 5 dashboard control panels
- **Status**: pending

### TASK-M3A-7.7 — Adopt `output_schema` (Pydantic) for all 12 agents
- **Status**: pending — auto-generates from BAML via `BAMLFunctionTool`

### TASK-M3A-7.8 — Adopt `output_key` propagation across the agent chain
- **Status**: pending

### TASK-M3A-7.9 — Adopt the `grounder` pattern (google_search → grounding_metadata)
- **Status**: pending

### TASK-M3A-7.10 — Adopt `VertexAiAgentEngine` deployment for the 12-agent fleet
- **Status**: pending

### TASK-M3A-7.11 — Adopt `MultiAgent` patterns (Sequential + Parallel + Loop)
- **Status**: pending

### TASK-M3A-7.12 — Adopt the `domain-expert planner` (BuiltInPlanner) for the 8 NCCA quest pack generators
- **Status**: pending

## Acceptance Criteria

- [ ] All 6 phase 2 stage templates land (`lc_extraction_template.baml`, `junior_cycle_template.baml`, `alevel_extraction_template.baml`, `gcse_extraction_template.baml`, `qpack_template.baml`)
- [ ] The 8 NCCA Junior Cycle subjects are wired at full scope (per Q4)
- [ ] BAML 0.223.0 features adopted (`spawn`, `host.callable`, `catch`, `render_null_as`)
- [ ] 12 ADK agents updated with the new ADK 1.10.0 patterns
- [ ] `dedup-report.md` shows the -9,700 LOC savings
- [ ] `openspec validate 2026-08-26-mega-3a-baml-and-adk-v1 --strict` passes
- [ ] All 19/19 existing tests still pass + new ones added
- [ ] No conflict with the 2 Mega-3 predecessors
- [ ] No conflict with the 2 archived predecessors