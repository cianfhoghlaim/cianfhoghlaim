## ADDED Requirements

### Requirement: LC5-subject pipeline for 5 NCCA Leaving Certificate subjects

The system SHALL provide an end-to-end pipeline for the 5 active LC
subjects (chemistry / computer_science / gaeilge / geography /
mathematics) processing 41 PDFs + 2 JPGs across 2 languages (EN + GA
plus the GA-only-at-root gaeilge layout).

The pipeline SHALL be organised into 7 stages:

1. **VLM/OCR routing** — `select_ocr_backend()` selects the v4
   registry model per PDF based on filename pattern + language.
2. **BAML extraction** — 5 BAML functions on 5 BAML files in
   `cianfhoghlaim/baml_src/education/lc_extraction/`.
3. **DuckLake** — 6 tables per subject = 30 tables total, in the
   `curriculum_unified.<subject>_<kind>` schema.
4. **LanceDB** — 5 per-subject embedding tables, 1 HNSW index each.
5. **Cognee cognify** — 5 per-subject datasets (oideachais_<subject>).
6. **Graphiti temporal** — 5 per-subject episode streams.
7. **FalkorDB cross-subject** — Subject → Topic → LO graph shared
   across all 5 subjects.

#### Scenario: The 5 L1 ingestion assets run end-to-end

- **WHEN** `dagster asset materialize --select 'lc5_*_ingested'`
- **THEN** `lc5_chemistry_ingested`, `lc5_computer_science_ingested`,
  `lc5_gaeilge_ingested`, `lc5_geography_ingested`,
  `lc5_mathematics_ingested` SHALL all materialise successfully
- **AND** the DLT source `lc5_documents` SHALL yield 72 rows
  (41 PDFs + 1 JPG + duplicate "_2026-06-30" copies per file)

#### Scenario: The 5 L2 syllabus BAML extraction assets run

- **WHEN** `dagster asset materialize --select 'lc5_*_syllabus_extracted'`
- **THEN** each subject's BAML `ExtractCurriculumSyllabus` SHALL run
- **AND** on failure (BAML unavailable) the asset SHALL return a stub
  `{"rows": 0, "subject": subject, "kind": "syllabus"}` instead of
  raising an error

#### Scenario: The cross-subject Graphiti stream integrates all 5 subjects

- **WHEN** `dagster asset materialize --select 'lc5_cross_subject_graphiti_stream'`
- **THEN** the asset SHALL depend on all 5 per-subject cognify assets
- **AND** the returned dict SHALL contain `"subjects": 5` reflecting
  the 5 per-subject streams

#### Scenario: The diagram extraction uses molmo2-8b pointing

- **GIVEN** the chemistry syllabus PDF
- **WHEN** the `*_diagrams_extracted` asset runs
- **THEN** the BAML `ExtractSyllabusDiagram` function SHALL be called
  with `pointing_model="allenai/Molmo2-8B"` (the v4 registry specialist)

### Requirement: 5 BAML files for LC5 extraction

The system SHALL provide 5 BAML files at
`cianfhoghlaim/baml_src/education/lc_extraction/`:

1. `curriculum_syllabus.baml` — `class SyllabusDocument`, `class ModuleTopic`, `class LearningOutcome`, `class SyllabusLanguage`, `class NCCAStage`, `class ModuleType`
2. `exam_paper_layout.baml` — `class ExamPaper`, `class Question`, `class QuestionSection`, `class QuestionType`
3. `marking_scheme.baml` — `class MarkingScheme`, `class MarkAllocation`, `class GradeDescriptor`, `class MarkingBand`
4. `cross_linguistic.baml` — `class CrossLinguisticConcept`, `class GaelicTopic`, `class EnglishEquivalent`
5. `syllabus_diagram.baml` — `class SyllabusDiagram`, `class DiagramRegion`, `class DiagramKind`, `class RegionRole`

#### Scenario: The BAML project compiles all 5 new files

- **WHEN** `cd cianfhoghlaim && uv run baml-cli generate`
- **THEN** the `baml_client/` directory SHALL contain the new Pydantic
  models for the 5 BAML classes
- **AND** `from cianfhoghlaim.baml_client.types import SyllabusDocument, ExamPaper, MarkingScheme, CrossLinguisticConcept, SyllabusDiagram` SHALL succeed

### Requirement: 16 dev marimo notebooks under `notebooks/dashboards/leaving_cert/`

The system SHALL provide 16 working dev notebooks demonstrating the
LC5 pipeline:

- `01_chemistry_analysis.py`, `02_computer_science_analysis.py`,
  `03_gaeilge_analysis.py`, `04_geography_analysis.py`,
  `05_mathematics_analysis.py` (per-subject; all 7 stages)
- `06_en_vs_ga_comparison.py`, `07_syllabus_topic_overlap.py`,
  `08_exam_paper_difficulty.py`, `09_marking_scheme_complexity.py`,
  `10_curriculum_evolution.py` (cross-subject comparisons)
- `11_ocr_model_comparison.py`, `12_layout_extraction.py`,
  `13_dense_ocr_benchmark.py`, `14_table_extraction.py`,
  `15_diagram_detection.py` (model benchmarks on the LC corpus)
- `16_runtime_comparison_llama_swap_vs_cpp.py` (the side-by-side
  llama-swap vs llama-cpp-python timing notebook)

Each notebook SHALL have working `@app.cell` cells (not skeletons).

#### Scenario: All 16 notebooks parse

- **WHEN** `for f in notebooks/dashboards/leaving_cert/*.py; do python -c "import ast; ast.parse(open('\$f').read())"; done`
- **THEN** all 16 files SHALL parse without syntax errors

#### Scenario: Notebook 01 opens and shows the chemistry file inventory

- **WHEN** `marimo edit notebooks/dashboards/leaving_cert/01_chemistry_analysis.py`
- **THEN** the notebook SHALL open with `mo.md` cells showing 16
  chemistry PDFs (8 en + 8 ga) + their v4 registry model routing
