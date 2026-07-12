# Tasks — UoG Math/Statistics Academic History Pipeline

## Phase 1 — Planning (DONE — five parallel agents)

- [x] Inspect existing UoG / leabharlann DLT sources and Dagster assets
- [x] Audit BAML schemas for math/statistics gaps
- [x] Design marimo notebook surface (8 notebooks)
- [x] Design academic-history agent + memory wiring
- [x] Draft OpenSpec change skeleton

## Phase 2 — Build the data + extraction plane

### 2.1 OpenSpec change skeleton (DONE)

- [x] `openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/proposal.md`
- [x] `tasks.md` (this file)
- [x] Spec deltas:
  - `specs/oideachais-academic-history-pipeline/spec.md` (new capability)
  - `specs/oideachais-leabharlann/spec.md` (MODIFIED)
  - `specs/oideachais-baml-schemas/spec.md` (MODIFIED)
  - `specs/oideachais-marimo-dashboards/spec.md` (MODIFIED)
  - `specs/oideachais-university-deep-extraction/spec.md` (MODIFIED)
  - `specs/agent-memory-systems/spec.md` (MODIFIED)

### 2.2 BAML schemas

- [ ] `baml/education/university/mathematics_statistics_extraction.baml` (NEW)
- [ ] Extend `baml/processing/author_archive.baml` with a math-aware wrapper
- [ ] Run `baml-cli check` — must exit 0

### 2.3 Validation helpers

- [ ] `baml/education/university/math_validation.py` (NEW)
  - LaTeX well-formedness (balanced braces, balanced `\left`/`\right`,
    balanced `\begin{env}`/`\end{env}`, command whitelist)
  - SymPy symbolic equivalence
  - Probability / parameter sanity (variance > 0, α ∈ (0, 1), p-value ∈
    [0, 1], probabilities sum to 1, R² ∈ [0, 1], Durbin–Watson ∈ (0, 4))
  - Iteration / ODE checks (residual < tol, conditioning finite,
    convergence rate)
  - Mark totals / step indices contiguous

### 2.4 DLT / Dagster wiring

- [ ] `orchestration/defs/1_ingestion/filesystem/uog_math_coursework/defs.yaml`
- [ ] `orchestration/defs/2_materials/baml_extraction/uog_math_coursework/defs.yaml`
- [ ] `orchestration/defs/2_materials/academic_history_validation/defs.yaml`
- [ ] `orchestration/defs/3_model_lifecycle/cocoindex_v1/academic_history_flow/defs.yaml`
- [ ] `orchestration/defs/4_asset_generation/marimo_dashboards/uog_math_coursework/defs.yaml`

### 2.5 CocoIndex v1 App

- [ ] `cocoindex/academic_history_flow.py` (R1–R4 conforming)

## Phase 3 — Notebooks + agent + generic template

### 3.1 Marimo notebooks (`notebooks/14_academic_history/`)

- [ ] `01_uog_maths_corpus_overview.py`
- [ ] `02_module_syllabus_assessment_map.py`
- [ ] `03_statistics_methods_lab.py`
- [ ] `04_numerical_analysis_lab.py`
- [ ] `05_nonlinear_systems_lab.py`
- [ ] `06_formulas_theorems_worked_solutions.py`
- [ ] `07_assignments_exams_answers.py`
- [ ] `08_academic_history_chat.py`
- [ ] Register the new group in `notebooks/cli.py::GROUPS`
- [ ] Verify all 8 notebooks parse with `marimo run --headless`

### 3.2 Academic-history agent

- [ ] `agents/routing_keywords.py` — add 13th bucket
  `academic_history_agent`
- [ ] `agents/meaisinfhoghlaim/educational/academic_history_agent.py`
- [ ] Wire to `MemoryBackend` Protocol via `get_default_backend()`

### 3.3 Generic bring-your-own-academic-history template

- [ ] `agents/meaisinfhoghlaim/educational/academic_history_manifest.py`
  (Pydantic model)
- [ ] `openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/templates/academic_history_manifest.example.yaml`

### 3.4 Tests

- [ ] `tests/_oideachais/test_academic_history_pipeline.py`
  - BAML function shape tests
  - Validation helper tests
  - Asset registration tests
  - Notebook parse tests
  - Privacy gate tests
  - Per-user pseudonymisation tests

## Phase 4 — Validation

- [ ] `openspec validate 2026-07-11-uog-math-statistics-academic-history-v1 --strict`
- [ ] `baml-cli check`
- [ ] `baml-cli test` (golden samples for each new function)
- [ ] `mise run turbo dev` (Dagster UI shows new assets)
- [ ] `uv run pytest tests/_oideachais/test_academic_history_pipeline.py`
- [ ] `mise run lint` + `mise run py:typecheck` + `mise run turbo typecheck`