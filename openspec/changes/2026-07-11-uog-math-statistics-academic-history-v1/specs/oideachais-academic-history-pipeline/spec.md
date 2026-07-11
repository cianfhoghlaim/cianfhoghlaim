# oideachais-academic-history-pipeline Specification

## Purpose

`oideachais-academic-history-pipeline` is a capability of the Cianfhoghlaim
platform that ingests a student's personal academic archive (notes,
assignments, exam papers, answer scripts, worked solutions) and produces:

1. Typed math/statistics artefacts (formulas, theorems, statistical
   procedures, numerical methods, nonlinear systems).
2. A semantic search index over the corpus + formulas.
3. Marimo notebooks for analysis (corpus overview, syllabus/assessment
   map, statistics lab, numerical analysis lab, nonlinear systems lab,
   formula/theorem registry, assignments/exams/answers, chat).
4. An `academic_history_agent` that can answer questions about the
   student's modules, notes, assignments, exams, answers, formulas,
   progress, and timeline.
5. A portable manifest format so any user can drop their own
   `notes/`, `assignments/`, `exam_papers/`, `answers/` folder into the
   pipeline and get the same surface.

The University of Galway (UoG) Mathematics + Statistics corpus at
`leabharlann/ollscoil_na_gaillimhe/{mata,past}/` is the case study
(ST311 / ST312, numerical analysis, nonlinear systems, cryptography,
discrete maths). The pipeline is generic — any user with a
`manifest.yaml` can reuse it.

## ADDED Requirements

### Requirement: Academic-history corpus manifest

The system SHALL provide an `AcademicHistoryManifest` schema that maps
local folders to typed academic artefacts.

The system SHALL provide an `AcademicHistoryManifest` schema that maps
local folders to typed academic artefacts.

#### Scenario: UoG maths corpus is discovered

- **GIVEN** a manifest with
  `module_roots: [{path: "leabharlann/ollscoil_na_gaillimhe/mata",
  module_code: "ST311"}]`
- **WHEN** the academic-history ingestion runs
- **THEN** it SHALL emit rows for every supported file in that subtree
- **AND** each row SHALL include `module_code`, `document_kind`,
  `file_hash`, `requires_ocr`, and `privacy_classification`

### Requirement: Math/statistics artefact extraction

The system SHALL extract tertiary mathematics and statistics artefacts
into typed schemas covering formulas, theorems, statistical procedures,
numerical methods, nonlinear systems, assignment briefs, exam papers,
worked solutions, answer scripts, and validation findings.

#### Scenario: ST311 statistics assignment extraction

- **GIVEN** an ST311 assignment PDF containing a hypothesis test and
  regression output
- **WHEN** `b.ExtractCourseworkArtifact(pdf_text, "st311_hypothesis_test.pdf", "assignment")` runs
- **THEN** the returned record SHALL include at least one
  `StatisticalProcedureRecord` and one `ValidationFinding`
- **AND** the validation findings SHALL include a
  `p_value_alpha_consistency` check

### Requirement: Numerical analysis + nonlinear systems records

The system SHALL extract `NumericalMethodRecord` and
`NonlinearSystemRecord` typed rows when the artefact contains
relevant mathematical content.

#### Scenario: Newton's method worked solution

- **GIVEN** an MA335 / numerical-analysis artefact describing a
  Newton-Raphson iteration
- **WHEN** `b.ExtractNumericalMethodRecords(pdf_text)` runs
- **THEN** the returned record SHALL include
  `method: NEWTON`, `convergence_rate: QUADRATIC`,
  `iterates: [...]` with the iteration trace
- **AND** the validation finding SHALL include
  `residual_within_tolerance` and `monotonic_descent` checks

### Requirement: Deterministic validation findings

The system SHALL validate every extracted math/statistics record with
deterministic checks (no LLM-as-judge). Findings SHALL be persisted to
`oideachais_academic_history.validation_findings`.

#### Scenario: LaTeX well-formedness

- **GIVEN** a `FormulaRecord` with `latex: "E = mc^2"`
- **WHEN** the LaTeX well-formedness validator runs
- **THEN** all 4 sub-checks SHALL pass (balanced braces, balanced
  `\left`/`\right`, balanced `\begin{env}`/`\end{env}`, command
  whitelist)

#### Scenario: p-value / alpha consistency

- **GIVEN** a `TestRecord` with `p_value: 0.04` and `alpha: 0.05`
- **WHEN** the p-value/alpha consistency check runs
- **THEN** `decision: REJECT` SHALL be consistent with `p_value < alpha`
- **AND** the finding SHALL be severity `INFO` (consistent) or
  `ERROR` (inconsistent)

### Requirement: Academic-history notebooks

The system SHALL provide a new marimo notebook group at
`cianfhoghlaim/notebooks/14_academic_history/` with 8 notebooks:

1. `01_uog_maths_corpus_overview.py` — corpus manifest + ingestion status
2. `02_module_syllabus_assessment_map.py` — joins personal notes + official
   module descriptors
3. `03_statistics_methods_lab.py` — ST311/ST312-style interactive analysis
4. `04_numerical_analysis_lab.py` — interactive root-finding, interpolation,
   quadrature, ODE methods
5. `05_nonlinear_systems_lab.py` — interactive phase portraits, fixed
   points, stability, bifurcation, chaos
6. `06_formulas_theorems_worked_solutions.py` — formula/theorem registry
   with LaTeX rendering
7. `07_assignments_exams_answers.py` — assignments, exam papers, student
   answer scripts, worked solutions, mark comparison
8. `08_academic_history_chat.py` — academic-history chat prototype

#### Scenario: Formula registry renders

- **WHEN** the user opens notebook `06_formulas_theorems_worked_solutions.py`
- **THEN** every extracted `FormulaRecord` SHALL render as LaTeX
- **AND** the notebook SHALL show `module_code`, `source_artifact`,
  `validation_status`, and `usage_count_in_assignments_or_exams`

### Requirement: Academic-history agent

The system SHALL provide an `academic_history_agent` that can answer
questions about the user's modules, notes, assignments, exams, answer
scripts, formulas, progress, and timeline.

The agent SHALL implement 10 tools:
`list_my_modules`, `list_my_artifacts`, `get_my_notes`,
`get_my_assignments`, `get_my_exam_history`, `get_my_answer_scripts`,
`summarise_my_progress`, `recommend_next_revision`,
`compare_my_answer_to_solution`, `search_my_formulas`.

The agent SHALL depend on the canonical `MemoryBackend` Protocol via
`get_default_backend()` (per the `agent-memory-systems` spec).

#### Scenario: User asks for a revision plan

- **GIVEN** the user has indexed notes, assignments, exams, and answers
- **WHEN** the user asks "what should I revise next for statistics?"
- **THEN** the agent SHALL retrieve the user's relevant history
- **AND** the response SHALL cite modules, topics, and specific
  artefacts (course code, file hash, validation status)

### Requirement: Privacy gate (defaults to off)

The system SHALL default `INCLUDE_IDENTITY_RECORDS=false` for the
academic-history pipeline. Personal identity folders SHALL be excluded
from ingestion unless the env var is explicitly set to `"true"`.

#### Scenario: Identity folder is gated

- **WHEN** the academic-history ingestion runs with
  `INCLUDE_IDENTITY_RECORDS` unset
- **THEN** rows from `cian_mac_an_déisigh_uí_liatháin/identity/`
  SHALL be excluded
- **AND** the asset run log SHALL record a warning identifying the
  excluded folder

### Requirement: Generic bring-your-own-academic-history pipeline

The system SHALL provide a portable manifest-driven pipeline: any user
can provide a `manifest.yaml` and a folder containing
`notes/`, `assignments/`, `exam_papers/`, `answers/`,
`worked_solutions/`, `feedback/`, and `official_module_descriptors/`,
and the pipeline SHALL produce the same typed artefacts + notebooks +
agent surface.

#### Scenario: External user with custom manifest

- **GIVEN** a user-provided `manifest.yaml` with `institution`,
  `programme`, and `module_roots`
- **WHEN** the academic-history ingestion runs
- **THEN** the pipeline SHALL ingest the user's folder
- **AND** produce the same `oideachais_academic_history.*` tables

## Cross-references

- `oideachais-leabharlann` — the upstream leabharlann corpus capability
- `oideachais-baml-schemas` — the canonical BAML client + clusters
- `oideachais-marimo-dashboards` — the parent notebook spec
- `oideachais-university-deep-extraction` — official module descriptors
- `agent-memory-systems` — the `MemoryBackend` Protocol contract
- `oideachais-cognify-knowledge-graph` — the cross-archive FalkorDB graph