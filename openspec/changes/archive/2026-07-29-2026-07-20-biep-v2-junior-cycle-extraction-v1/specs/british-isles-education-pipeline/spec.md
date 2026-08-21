## ADDED Requirements

### Requirement: Junior Cycle end-to-end

The system SHALL provide a full BIEP-grade Junior Cycle pipeline
(Republic of Ireland), mirroring the existing
"Requirement: 6 Irish LC subjects end-to-end" but for the 18
NCCA JC subjects:

- **52 NCCA Junior Cycle DLT sources** at
  `dlt/british_isles/ireland/education/junior_cycle_subjects/` (18 subjects × 2 languages)
  + `dlt/british_isles/ireland/education/junior_cycle_short_courses/` (16 short courses)
- **4 BAML extraction functions** at
  `baml_src/british_isles/ireland/education/junior_cycle/`
  (ExtractJCCurriculum, ExtractCBADescriptor, ExtractJCShortCourse, ExtractJCExamPaper)
- **1 CocoIndex v1 App** at `cocoindex_flows/subjects/junior_cycle_embedding.py`
  producing 36 LanceDB tables `cianfhoghlaim.jc.<subject>.<year>_<lang>`
  (18 subjects × 2 langs)
- **72+ Dagster assets** at
  `orchestration/defs/2_materials/junior_cycle/` (18 × 4 layers + 16 short-course
  + 36 CBA + 1 cross-subject Graphiti stream + 1 orchestrator composite)
- **1 MotherDuck Dive** `jc_curriculum_dive` + **1 daily Flight** `jc_pdf_sync_flight`

#### Scenario: mise run dagster:oideachais → materialize all 18 JC subjects

- **WHEN** a teacher clicks "Materialize all" in the Dagster UI for the JC pipeline
- **THEN** the 72+ JC assets materialise within minutes
- **AND** the 36 LanceDB tables `cianfhoghlaim.jc.<subject>.<year>_<lang>` are populated
- **AND** the `jc_curriculum_dive` MotherDuck Dive shows topic coverage per JC subject
- **AND** the daily `jc_pdf_sync_flight` re-runs BAML extraction on any new PDFs
  landed in `s3://garage/cianfhoghlaim/junior_cycle/<subject>/<lang>/<year>/`

#### Scenario: JC-to-LC topic progression

- **WHEN** a teacher opens `cianfhoghlaim.jc.<subject>.year_3_en` in the marimo portal
- **AND** joins to `cianfhoghlaim.lc.<subject>.<level>_en` (the LC equivalent table)
- **THEN** the join returns the topic chain from JC Year 3 → LC Year 4 (Ordinary Level)
- **AND** the `jc_curriculum_dive` shows the topic progression alongside the LC Dive
