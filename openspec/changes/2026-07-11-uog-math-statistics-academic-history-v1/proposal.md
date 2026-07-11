# UoG Math/Statistics Academic History Pipeline

## Why

The existing BIEP notebooks analyse Leaving Certificate syllabi, exam
papers, and marking schemes, but they do not cover the user's University
of Galway (UoG) mathematics / statistics modules — e.g. ST311 / ST312
probability & statistics, numerical analysis, nonlinear systems,
cryptography — nor the user's own assignments, exam papers, worked
solutions, answer scripts, formulas, and progress over time.

The existing UoG / leabharlann DLT sources already discover these
artefacts at
`leabharlann/ollscoil_na_gaillimhe/{mata,past,...}/`, but they only
extract generic artefact metadata (`ExtractUoGArtifact`,
`ExtractLeabharlannDoc`). No math-aware schema exists; no notebook
summarises the user's history; no agent can answer questions about it.

This change adds a typed, math-aware **Academic History Pipeline**:

1. BAML extraction for tertiary math/statistics artefacts
   (formulas, theorems, statistical procedures, numerical methods,
   nonlinear systems, assignment briefs, exam papers, answer scripts,
   worked solutions, validation findings).
2. Dagster assets wrapping the existing UoG filesystem scanner for the
   `mata` and `past` subdirs.
3. A new `oideachais_academic_history` LanceDB table (via a v1
   CocoIndex App) for semantic search across chunks + formulas.
4. 8 new marimo notebooks under `notebooks/14_academic_history/`
   covering corpus overview, syllabus/assessment map, statistics
   methods lab, numerical analysis lab, nonlinear systems lab,
   formula/theorem/worked-solution registry, assignments/exams/answers,
   and academic-history chat.
5. A new `academic_history_agent` (13th routing bucket) that can
   answer questions about modules, notes, assignments, exams, answers,
   formulas, progress, and timeline.
6. A portable, manifest-driven **"bring your own academic history"**
   template that any user can drop into a new folder + manifest and
   reuse the same pipeline.

## What changes

### 1. BAML (`cianfhoghlaim/baml/education/university/mathematics_statistics_extraction.baml`, NEW)

- `TertiaryMathTopic` (40+ values for ST3xx / MA3xx / AP3xx)
- `DistributionFamily` (22 distributions)
- `InferenceProcedure` (24+ tests / estimators)
- `RegressionFamily` (16+ families)
- `NumericalMethod` (40+ methods)
- `ConvergenceRate` (7 values)
- `NonlinearSystemKind`, `BifurcationType`, `MathContentLanguage`,
  `AssignmentKind`, `DocumentKind`, `ValidationSeverity`
- `AcademicModuleDescriptor`, `CourseworkArtifactExtraction`,
  `TertiaryExamPaper`, `AssignmentBrief`, `AssignmentRubric`,
  `StudentAnswerScript`, `WorkedSolution`, `SolutionStep`,
  `FormulaRecord`, `TheoremRecord`, `StatisticalProcedureRecord`,
  `NumericalMethodRecord`, `NonlinearSystemRecord`,
  `ValidationFinding`, `AcademicHistorySnapshot`, `AcademicHistoryManifest`
- Functions:
  `ExtractAcademicModuleSyllabus`, `ExtractCourseworkArtifact`,
  `ExtractTertiaryExamPaper`, `ExtractAssignmentBrief`,
  `ExtractStudentAnswerScript`, `ExtractWorkedSolution`,
  `ExtractFormulaRecords`, `ExtractTheorems`,
  `ExtractStatisticalProcedureRecords`, `ExtractNumericalMethodRecords`,
  `ExtractNonlinearSystemRecords`, `ExtractAcademicHistorySnapshot`

### 2. BAML extension (`author_archive.baml`, MODIFIED)

- `ExtractUoGArtifact` keeps existing behaviour for back-compat
- Adds `extract_uog_math_artifact()` thin wrapper for math/statistics
  specialisation

### 3. DLT / Dagster

- New `author_archive_uog_math_coursework` Dagster asset driven by the
  existing `university_of_galway_source()` (partitioned on
  `domain ∈ {mata, past}`).
- New `academic_history_validation_findings` asset that materialises
  deterministic math/statistics validation findings
  (LaTeX well-formedness, SymPy equivalence, p-value/alpha consistency,
  probability sums, regression diagnostics, residual/convergence
  checks, mark totals).

### 4. CocoIndex v1 (`cianfhoghlaim/cocoindex/academic_history_flow.py`, NEW)

- `AcademicHistoryApp` — embeds chunks + formulas into the
  `oideachais_academic_history` LanceDB table using
  `BAAI/bge-m3` (1024-d) to match the existing leabharlann embedding
  model.
- R1–R4 conforming (`from ._lifespan import shared_lifespan`,
  `coco.App(...)` at module scope, `@coco.fn(memo=True)`).

### 5. Cross-archive edges

- `(:CourseworkArtifact)-[:PART_OF]->(:AcademicModule)`
- `(:CourseworkArtifact)-[:CONTAINS]->(:FormulaRecord)`
- `(:FormulaRecord)-[:USED_IN]->(:SolutionStep)`
- `(:StudentAnswerScript)-[:RESPONDS_TO]->(:ExamQuestion)`
- `(:StudentAnswerScript)-[:COMPARED_TO]->(:WorkedSolution)`
- `(:AcademicModule)-[:BUILDS_ON]->(:LeavingCertTopic)`
- `(:UoGArtifact)-[:MATCHES]->(:ModuleDescriptor)` (existing)

### 6. Marimo notebooks (`cianfhoghlaim/notebooks/14_academic_history/`)

1. `01_uog_maths_corpus_overview.py`
2. `02_module_syllabus_assessment_map.py`
3. `03_statistics_methods_lab.py`
4. `04_numerical_analysis_lab.py`
5. `05_nonlinear_systems_lab.py`
6. `06_formulas_theorems_worked_solutions.py`
7. `07_assignments_exams_answers.py`
8. `08_academic_history_chat.py`

All notebooks ship with PEP 723 inline deps, MotherDuck/DuckLake
connect via `nb_utils.connect_biep_lakehouse()`, Altair 5-panel layout,
health banner, openspec cross-reference footer, and CLI dual-mode.

### 7. Academic-history agent (memory + chat)

- New 13th routing bucket in
  `cianfhoghlaim/agents/routing_keywords.py`
- New module
  `cianfhoghlaim/agents/meaisinfhoghlaim/educational/academic_history_agent.py`
  implementing 10 tools (`list_my_modules`, `list_my_artifacts`,
  `get_my_notes`, `get_my_assignments`, `get_my_exam_history`,
  `get_my_answer_scripts`, `summarise_my_progress`,
  `recommend_next_revision`, `compare_my_answer_to_solution`,
  `search_my_formulas`).
- Wires through the canonical `MemoryBackend` Protocol via
  `get_default_backend()`.
- Per-user Cognee dataset `oideachais_student_<id>_history`.

### 8. Generic bring-your-own-academic-history template

- `AcademicHistoryManifest` Pydantic model + `manifest.yaml` example
  at `openspec/changes/2026-07-11-uog-math-statistics-academic-history-v1/templates/academic_history_manifest.example.yaml`.
- Any user can point this at their own notes/assignments/exam_papers/
  answers/ folder and produce the same pipeline output.

## Dependencies

```markdown
## Dependencies

`Blocked by: none`
`Blocked by (soft): 2026-07-15-oideachais-leabharlann-v1`
`Blocked by (soft): 2026-07-15-oideachais-university-deep-extraction-v1`
`Blocked by (soft): 2026-07-17-consolidate-bi-ep-v1-spec-deltas-v1`
`Affected repos: cianfhoghlaim, leabharlann`
```

## Out of scope

- Live web scraping of private learning platforms (e.g. Blackboard,
  Canvas).
- Writing into the sibling `leabharlann` repo (read-only; only metadata
  is committed in this repo).
- Identity records unless `INCLUDE_IDENTITY_RECORDS=true` is set.
- Replacing the existing Leaving Cert BIEP notebooks.
- UK / Scottish / Welsh curriculum extensions (deferred to v2 of
  `british-isles-education-pipeline`).

## Cross-repo sync

This change is **single-repo** from a build standpoint
(`cianfhoghlaim` repo), but it reads the personal archive in the
sibling `leabharlann` repo. No commits are made to `leabharlann`. A
`cross-repo-sync.md` file documents the read-only contract.

## Acceptance gates

- `openspec validate 2026-07-11-uog-math-statistics-academic-history-v1 --strict` passes
- All BAML functions compile (`baml-cli check` exit 0)
- New Dagster defs YAML files parse (`dg check yaml` exit 0)
- 8 new marimo notebooks render without errors in headless mode
- Test suite (`tests/_oideachais/test_academic_history_pipeline.py`)
  passes (10+ test cases covering BAML extraction, validation,
  asset registration, notebook parse)
- Privacy gate (`INCLUDE_IDENTITY_RECORDS`) verified to default-off
- Per-user pseudonymised ID contract enforced (no PII emitted to
  Langfuse / Letta)