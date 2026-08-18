# Tasks — Mega-3c

## Phase 1: PEP 723 template collapse (Week 1)

### TASK-M3C-1.1 — Build `notebooks/_shared/_pep723_template.py` (canonical template)
- **Status**: pending
- **Files**: `notebooks/_shared/_pep723_template.py` (~50 LOC)
- **What**: The canonical PEP 723 inline metadata block with the 9 canonical
  dependencies (marimo >=0.14.10, ibis-framework[duckdb] >=9.0, pandas >=2.2,
  altair >=5.0, pyarrow >=15, anywidget >=0.9, traitlets >=5.14, duckdb >=1.0,
  python-dotenv >=1.0). Every notebook imports this via `from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES`.

### TASK-M3C-1.2 — Refactor 201 notebooks to use the canonical template
- **Status**: pending
- **Files**: 201 notebooks × ~5 LOC modification each
- **What**: Replace the duplicate `# /// script` blocks with a
  single-line `from notebooks._shared._pep723_template import *` + a comment.

## Phase 2: biiep_v3_dashboard_v2 collapse (Week 2)

### TASK-M3C-2.1 — Build `notebooks/_shared/biiep_v3_dashboard_v2.py` (canonical helper)
- **Status**: pending
- **Files**: `notebooks/_shared/biiep_v3_dashboard_v2.py` (~300 LOC)
- **What**: The 8-cell BIEP v3 operator console hoisted into 1
  parameterised helper `build_biep_v3_dashboard(jurisdiction=..., milestone=...)`.
  Used by all 7 tier dashboards + the 4 stage dashboards.

### TASK-M3C-2.2 — Refactor 7 tier dashboards to use the canonical helper
- **Status**: pending
- **Files**: `notebooks/{19_ireland,20_england,21_sct_wls_ni,22_crown,23_8_jurisdiction,26_aistear,27_primary}_pipeline_dashboard.py`
- **What**: Replace each ~600 LOC dashboard body with a single
  `build_biep_v3_dashboard(jurisdiction=...)` call (~10 LOC per file).

## Phase 3: 4 Stage Marimo Dashboards (Weeks 3-4)

### TASK-M3C-3.1 — Build `19_junior_cycle_pipeline_dashboard.py` (JC stage dashboard)
- **Status**: pending
- **Files**: `notebooks/19_junior_cycle_pipeline_dashboard.py` (~150 LOC, new)
- **What**: Uses `build_biep_v3_dashboard(jurisdiction="ireland_jc", milestone="M3")`.
  Covers the 8 NCCA Junior Cycle subjects at full scope.

### TASK-M3C-3.2 — Build `20_england_alevel_pipeline_dashboard.py` (A-Level stage dashboard)
- **Status**: pending
- **Files**: `notebooks/20_england_alevel_pipeline_dashboard.py` (~150 LOC, new)
- **What**: Uses `build_biep_v3_dashboard(jurisdiction="england_alevel", milestone="M4")`.

### TASK-M3C-3.3 — Build `20_england_gcse_pipeline_dashboard.py` (GCSE stage dashboard)
- **Status**: pending
- **Files**: `notebooks/20_england_gcse_pipeline_dashboard.py` (~150 LOC, new)
- **What**: Uses `build_biep_v3_dashboard(jurisdiction="england_gcse", milestone="M4")`.

### TASK-M3C-3.4 — Wire the existing `19_ireland_pipeline_dashboard.py` to v2 helper
- **Status**: pending
- **Files**: `notebooks/19_ireland_pipeline_dashboard.py`
- **What**: Use `build_biep_v3_dashboard(jurisdiction="ireland_lc", milestone="M1")`.

## Phase 4: Marimo Patterns Tour (Week 5)

### TASK-M3C-4.1 — Enhance `00_marimo_patterns_tour.py` with A2UI surfaces
- **Status**: pending
- **Files**: `notebooks/00_marimo_patterns_tour.py`
- **What**: Add the 8 A2UI surface demos (chart, graph, playback,
  lineage, search, subject_grid, dashboard, translator) using
  `mo.ui.chat` streaming + `mo.ai.llm`.

### TASK-M3C-4.2 — Adopt `mo.ui.chat` streaming across the 6 BIEP v3 jurisdiction dashboards
- **Status**: pending
- **Files**: 6 stage dashboards
- **What**: Each dashboard exposes a `mo.ui.chat(..., streaming=True)`
  cell that allows the operator to ask questions about the pipeline.

## Phase 5: Cross-Package Integration (Weeks 6-10)

### TASK-M3C-5.1 — Wire BAML into the 7 BIEP CocoIndex v1 flows
- **Status**: pending
- **Files**: `cocoindex/biep_parity/4_stage_factory.py` + 7 flows
- **What**: Each CocoIndex flow calls the corresponding BAML function
  via `BAMLFunctionTool`.

### TASK-M3C-5.2 — Wire BAML into the 42 Dagster assets
- **Status**: pending
- **Files**: `orchestration/defs/2_materials/england_education/`
- **What**: Each asset materialization triggers the corresponding BAML extraction.

### TASK-M3C-5.3 — Wire BAML `image` / `pdf` multimodal into the 6-stage PDF pipeline
- **Status**: pending
- **Files**: `dlt/british_isles/ireland/education/pdfs/root_pdf_extraction.py`
- **What**: Replace the embed→string→BAML handoff with direct PDF input.

### TASK-M3C-5.4 — Wire the 5 lc6 functions to the 6 marimo notebooks
- **Status**: pending
- **Files**: 6 stage dashboards
- **What**: Each dashboard has a "Apply BAML" button that calls the
  corresponding BAML function via `marimo_baml`.

### TASK-M3C-5.5 — Wire BAML extractor outputs to the 4 MotherDuck Dives
- **Status**: pending
- **Files**: 4 MotherDuck Dive notebooks
- **What**: Each Dive reads from the BAML extractor output.

### TASK-M3C-5.6 — Wire the SSE streaming endpoint to the BIEP v3 lineage viewer
- **Status**: pending
- **Files**: `web/apps/cianfhoghlaim-web/src/routes/api/lineage/stream.ts`
- **What**: The lineage viewer streams BAML extraction progress in
  real-time.

### TASK-M3C-5.7 — Wire BAML `Collector` into the 7 BIEP CocoIndex flows
- **Status**: pending
- **Files**: 7 CocoIndex flows
- **What**: Each flow emits a Langfuse trace + a BAML Collector record.

### TASK-M3C-5.8 — Wire BAML `image` outputs to the 12-agent fleet
- **Status**: pending
- **Files**: 12 ADK agents
- **What**: Each agent can emit BAML `image` outputs.

## Phase 6: FastAPI + Auth (Week 11)

### TASK-M3C-6.1 — Mount the 6 BIEP notebooks as FastAPI endpoints
- **Status**: pending
- **Files**: 6 stage dashboards + `notebooks/_shared/marimo_to_fastapi.py` (~150 LOC)
- **What**: Each dashboard becomes a FastAPI endpoint.

### TASK-M3C-6.2 — Adopt FastAPI Auth for the 6 BIEP notebooks
- **Status**: pending
- **Files**: 6 stage dashboards
- **What**: Lock down the notebook APIs with the canonical
  `frameworks/fastapi-auth/` pattern.

### TASK-M3C-6.3 — Adopt Fasthtml for the 6 BIEP notebooks (single-page HTML)
- **Status**: pending
- **Files**: 6 stage dashboards
- **What**: Each dashboard becomes a single HTML page.

## Acceptance Criteria

- [ ] All 201 notebooks use the canonical `_pep723_template.py` (Phase 1)
- [ ] All 7 tier dashboards use the canonical `biiep_v3_dashboard_v2.py` (Phase 2)
- [ ] All 4 stage Marimo dashboards land (Phase 3)
- [ ] All 60 integration sub-tasks land (Phase 5)
- [ ] All 6 BIEP notebooks exposed via FastAPI + Auth (Phase 6)
- [ ] `dedup-report.md` shows the -6,066 LOC savings
- [ ] `openspec validate 2026-11-25-mega-3c-marimo-and-integration-v1 --strict` passes
- [ ] All 19/19 existing tests still pass + new ones added
- [ ] No conflict with the 4 Mega-3 predecessors