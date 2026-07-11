# `british-isles-education-pipeline` MODIFIED — Consolidate 9 ADDED Requirements from 7 changes into R0–R7 sequential R-group history

> Consolidates the 9 ADDED Requirements shipped across the 7 source
> changes (2 + 1 + 1 + 2 + 1 + 1 + 1) into a single R0–R7 sequential
> R-group history. The R-group labels correspond to the BIEP v1
> delivery phases (Phase 0 foundation / Phase 1.1 English wiring /
> Phase 1.1 verification / Phase 1.4 BIEP-foundation / Phase 4-5
> BAML fix / Phase 6 per-subject marimo / Phase 7 daily flight /
> Phase 8 BIEP-marking).

## ADDED Requirements

### Requirement: R1 — Phase 1.1 English lc5 filesystem wiring + duplicate cleanup

The system SHALL ingest every PDF (and JPG for the scanned geography
exam page) in `cianfhoghlaim/leaving_certificate/{chemistry,computer_science,english,gaeilge,geography,mathematics}/`
through a single filesystem DLT resource
(`cianfhoghlaim.dlt.filesystem.leaving_cert_source.lc5_documents` with
`LC6_SUBJECTS = ("chemistry", "computer_science", "english", "gaeilge",
"geography", "mathematics")`). English is en-only at the root of its
subject directory (mirrors the gaeilge asymmetry but with
`language = "en"`). The `LC_PDF_KIND_REGISTRY` SHALL contain explicit
regex patterns for both the English exam-paper kind
(`LC002ALP\d{3}[EI]V\.pdf`) and the English spec-constitution kind
(`SC-English-Spec-ENG-INT.*\.pdf`).

Additionally, the canonical Irish curriculum DLT source SHALL live
exclusively at `cianfhoghlaim/dlt/british_isles/ireland/education/curriculum.py`.
The legacy 972-LOC byte-identical duplicate
`cianfhoghlaim/dlt/british_isles/ireland/education/curriculum_source.py`
and the 0-byte stub `exam_source_update.py` SHALL NOT exist. All 11
importers (5 in `dlt/british_isles/ireland/law/` + 5 in
`dlt/british_isles/ireland/education/law/` + the canonical
`curriculum.py`'s own docstring + the
`test_curriculum_source_local_cache.py` test) SHALL import
`_crawl_source` from `...education.curriculum` (not
`...education.curriculum_source`).

*(Consolidates the 2 ADDED Requirements from
`2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1`.)*

#### Scenario: English contributes 8 PDFs to the filesystem resource

- **GIVEN** the 8 PDFs in `cianfhoghlaim/leaving_certificate/english/`
      (`LC002ALP100EV.pdf`, `LC002ALP200EV.pdf`, `LC002GLP100EV.pdf`,
      `LC002GLP200EV.pdf`, `SCSEC14_English_Syllabus.pdf`,
      `SCSEC14_English_Syllabus_2026-06-30.pdf`,
      `SC-English-Spec-ENG-INT.pdf`,
      `SC-English-Spec-ENG-INT_2026-06-30.pdf`)
- **WHEN** `from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents; rows = list(lc5_documents())` runs
- **THEN** exactly 8 rows have `subject == "english"` and `language == "en"`
- **AND** the 4 exam papers route through `model_key = "qwen3-vl-8b"`
- **AND** the 4 syllabi / spec constitutions route through `model_key = "gemma-4-26B-A4B"`
- **AND** the total row count is ≥ 80 (the 6 subjects × 2 languages minus
      the english ga-only and gaeilge en-only subjects)

#### Scenario: 36 lc5-group Dagster assets register per subject × asset group

- **GIVEN** `LC6_SUBJECTS` has 6 elements
- **WHEN** the `_make_subject_extraction_asset` factory loop + the 6
      explicit ingestion + 6 explicit cognify `@asset` decorators execute
- **THEN** exactly 36 assets register under the `lc5` group_name subtree
      (6 subjects × 6 asset groups: 1 ingestion + 4 BAML extraction +
      1 cognify)
- **AND** the English asset set is `{lc5_english_ingested,
  lc5_english_syllabus_extracted, lc5_english_papers_extracted,
  lc5_english_marking_extracted, lc5_english_diagrams_extracted,
  lc5_english_cognified}` (6 assets, one per asset group)

#### Scenario: lc6 cross-subject Graphiti fan-out reports 6 subjects

- **WHEN** `lc5_cross_subject_graphiti_stream` materialises
- **THEN** its return payload reports `subjects = len(LC6_SUBJECTS) = 6`
- **AND** the Graphiti episode stream merges all 6 subjects into the
      FalkorDB cross-subject graph (nodes: Subject, Topic,
      LearningOutcome, Question, Year, ModuleKind;
      edges: HAS_TOPIC, ASSESSED_BY, EVOLVED_TO, EN_CORRESPONDS_TO_GA)

#### Scenario: The duplicate pair is gone

- **WHEN** a developer runs `ls cianfhoghlaim/dlt/british_isles/ireland/education/ | grep -E "curriculum_source|exam_source_update"`
- **THEN** zero matches SHALL be returned
- **AND** `curriculum.py` (972 LOC) remains the sole canonical surface

#### Scenario: The 11 importers resolve against the kept file

- **GIVEN** `curriculum.py` defines `_crawl_source` at line 57
      (verified via `grep -n "^def _crawl_source" cianfhoghlaim/dlt/british_isles/ireland/education/curriculum.py`)
- **WHEN** any of the 11 importer modules is loaded
- **THEN** the import `from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import _crawl_source` SHALL succeed
- **AND** zero matches SHALL be returned by
      `grep -rn "from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum_source" cianfhoghlaim/`
- **AND** zero matches SHALL be returned by
      `grep -rn "from cianfhoghlaim.dlt.british_isles.ireland.education.exam_source_update" cianfhoghlaim/`

### Requirement: R2 — Phase 1.1 verification gates (English lc5 wiring complete)

The system SHALL satisfy the four static Phase 1.1 verification
gates on the `pick-4-biep-v1` branch as of 2026-07-13. The Phase 1.1
sub-batch of the BIEP v1 flagship (the 6-subject LC filesystem wiring
for English) was already code-shipped by the prior openspec change
`2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1`; this R2
requirement captures the verification status, NOT the
implementation. The underlying code state SHALL satisfy the four
gates below (Gates 1–4: `LC6_SUBJECTS` includes `english` as the 3rd
element; `LC_PDF_KIND_REGISTRY` has 2 English regex patterns; 6
`lc5_english_*` assets exist in `lc5_assets.py`; `english.yaml` cron
asset exists at `orchestration/defs/1_ingestion/curriculum/lc5/english.yaml`
with `CelticIngestionComponent` + `automation_cron: "0 5 * * *"` +
`state_backed: true`).

*(Consolidates the 1 ADDED Requirement from
`2026-07-13-biep-v1-phase-1-1-english-wiring-v1`.)*

#### Scenario: Gate 1 — `LC6_SUBJECTS` includes `english` as the 3rd element

- **GIVEN** the file
      `cianfhoghlaim/dlt/filesystem/leaving_cert_source.py`
- **WHEN** an agent runs `grep -A 7 "^LC6_SUBJECTS" cianfhoghlaim/dlt/filesystem/leaving_cert_source.py`
- **THEN** the output SHALL be exactly:
      ```python
      LC6_SUBJECTS: tuple[str, ...] = (
          "chemistry",
          "computer_science",
          "english",
          "gaeilge",
          "geography",
          "mathematics",
      )
      ```
- **AND** `grep -rn "LC5_SUBJECTS" cianfhoghlaim/` SHALL return
      zero matches (the rename is complete — no stale references
      in the source tree)

#### Scenario: Gate 2 — `LC_PDF_KIND_REGISTRY` has 2 English regex patterns

- **GIVEN** the `LC_PDF_KIND_REGISTRY` dict in
      `cianfhoghlaim/dlt/filesystem/leaving_cert_source.py`
- **THEN** the dict SHALL contain both of these patterns:
      - `r"^LC002ALP\d{3}[EI]V\.pdf$"` mapped to `qwen3-vl-8b`
        (the LC English ALP/GLP exam-paper kind)
      - `r"^SC-English-Spec-ENG-INT.*\.pdf$"` mapped to
        `gemma-4-26B-A4B` (the English spec-constitution kind)
- **AND** `_scan_subject` SHALL have an
      `elif subject_dir.name == "english"` branch that emits files
      at the root with `language = "en"` (the English LC syllabus
      is monolingual — no `en/` subdir needed, mirrors the gaeilge
      asymmetry)

#### Scenario: Gate 3 — 6 `lc5_english_*` assets exist in `lc5_assets.py`

- **GIVEN** the file
      `cianfhoghlaim/orchestration/defs/2_materials/lc_extraction/lc5_assets.py`
- **THEN** the asset registry SHALL contain exactly these 6 names:
      - `lc5_english_ingested` (explicit `@asset` decorator, Layer 1)
      - `lc5_english_syllabus_extracted`
      - `lc5_english_papers_extracted`
      - `lc5_english_marking_extracted`
      - `lc5_english_diagrams_extracted`
      - `lc5_english_cognified` (explicit `@asset` decorator, Layer 3)
- **AND** the 4 `*_extracted` assets SHALL be generated at
      module-import time by the factory loop

#### Scenario: Gate 4 — `english.yaml` cron asset exists

- **GIVEN** the path
      `cianfhoghlaim/orchestration/defs/1_ingestion/curriculum/lc5/english.yaml`
- **THEN** the file SHALL exist (≥ 1 KB)
- **AND** its top-level `type` SHALL be
      `cianfhoghlaim.orchestration.components.CelticIngestionComponent`
- **AND** its `attributes` SHALL include:
      - `source_id: cianfhoghlaim.filesystem.leaving_cert.english`
      - `subject: english`
      - `automation_cron: "0 5 * * *"` (UTC, mirrors
        `lc5/defs.yaml`)
      - `state_backed: true`
      - `tags: [biep, lc6, english, ingestion]`

### Requirement: R3 — Phase 1.4 BIEP 6-subject foundation (per-subject NCCA syllabus ingestion)

The system SHALL provide per-subject NCCA syllabus ingestion +
per-subject BAML extraction for the 6 BIEP v1 LC subjects —
Mathematics, Chemistry, Geography, Gaeilge, English, Computer
Science — by shipping 6 per-subject NCCA crawl DLT sources
(`ncca_<subject>.py`), verifying 6 per-subject qpack BAMLs
(`qpack_<subject>.baml`), exposing a unified BAML extractor
(`ExtractLC6Syllabus(subject, text, language) -> LCSyllabus`), and
wiring 6 per-subject L1 ingestion defs YAMLs (one
`CelticIngestionComponent` per subject, daily 04:00 UTC cron,
subject × language partitions = 2 partitions per subject, 12
partitions total).

This R3 requirement is the foundation for the BIEP v1 agent +
dashboard + study-tool work (the per-subject downstream): a single
call site
(`b.ExtractLC6Syllabus(subject="<subject>", text=..., language="<en|ga>")`)
replaces six different `b.ExtractCurriculumSyllabus(text)` invocations
and gives downstream agents one stable discriminated `LCSyllabus`
return shape.

*(Consolidates the 1 ADDED Requirement from
`2026-07-16-biiep-v1-lc-per-subject-syllabus-ingestion-v1`.)*

#### Scenario: 6 per-subject DLT sources + 6 qpack BAMLs + 1 unified BAML extractor + 6 defs YAMLs exist

- **GIVEN** the BIEP v1 capspec covers the 6 priority Irish LC
      subjects — Mathematics, Chemistry, Geography, Gaeilge, English,
      Computer Science
- **WHEN** the operator checks the per-subject surface
- **THEN** 13 files SHALL exist (6 DLT + 6 qpack BAMLs + 1 unified
      extractor) AND 6 L1 defs YAMLs SHALL exist at
      `cianfhoghlaim/orchestration/defs/1_ingestion/curriculum/lc6/`

#### Scenario: Per-subject DLT sources honour the canonical BIEP v1 dlt pattern

- **WHEN** the operator checks the 6 per-subject DLT sources
- **THEN** each SHALL have:
      - `@dlt.resource(name="<subject>_syllabus", write_disposition="merge", primary_key=["url"])`
      - `destination=named_destination("warehouse")`
      - `USE_LOCAL_SCRAPES=true` reading from
        `stedding/ingest_queue/ncca/<subject>/<lang>/`

#### Scenario: Unified BAML extractor returns LCSyllabus

- **WHEN** the operator calls
      `b.ExtractLC6Syllabus(subject="mathematics", text=<pdf_text>, language="en")`
- **THEN** the system SHALL return an `LCSyllabus` with
      `subject = LC6Subject.MATHEMATICS` and `language = LC6Language.EN`
- **AND** the `document` field SHALL be the canonical `SyllabusDocument`
      Pydantic class (from `baml/education/lc_extraction/curriculum_syllabus.baml`)

#### Scenario: Per-subject L1 defs YAMLs use CelticIngestionComponent with daily cron

- **WHEN** the operator checks the 6 L1 defs YAMLs at
      `orchestration/defs/1_ingestion/curriculum/lc6/`
- **THEN** each SHALL be a `CelticIngestionComponent` with
      `source_id = filesystem.leaving_cert.<subject>`
- **AND** `automation_cron = "0 4 * * *"` (daily 04:00 UTC)
- **AND** `state_backed = true` + `state_refresh_interval = "monthly"`
- **AND** `partitions` SHALL cover subject × language (2 partitions
      per subject)

### Requirement: R4 — Phase 4-5 BAML fix (MarkingPoint classes + v0.212+ canonical syntax in lc_extraction)

The system SHALL avoid duplicate BAML class names for marking-scheme
point records AND enforce that every `.baml` file under
`cianfhoghlaim/baml/education/lc_extraction/` uses the BAML v0.212+
canonical `field Type` (whitespace-separated) syntax — not the legacy
Pydantic-style `field: type` colon-separated syntax.

Specifically: the cross-stage shared marking point class in
`cianfhoghlaim/baml/education/_shared/strand_outcome.baml` SHALL be
named `MarkingPointStrand`; the SEC marking-scheme PDF extraction
class in `cianfhoghlaim/baml/education/pdfs/leaving_cert_marking_scheme.baml`
SHALL be named `MarkingPointSec`. The 7 lc_extraction files
(`circular_extraction.baml`, `cross_linguistic.baml`,
`curriculum_syllabus.baml`, `exam_paper_layout.baml`,
`lc_topic_extraction.baml`, `marking_scheme.baml`,
`syllabus_diagram.baml`) define the canonical BIEP v1 contract types
(`MarkingScheme`, `BilingualText`, `NCCAKeyCompetency`,
`CrossNationLearningOutcome`, `PastPaper`, `SyllabusDocument`,
`MarkAllocation`, `GradeDescriptor`, `DiagramPayload`, etc.) and the
7 canonical extraction functions (`ExtractCurriculumSyllabus`,
`ExtractExamPaperLayout`, `ExtractMarkingSchemeGuideline`,
`ExtractStrandFromCatalog`, `ExtractMarkingSchemeStrand`,
`ExtractCelticCurriculumComparison`, `ExtractSyllabusDiagram`).

*(Consolidates the 2 ADDED Requirements from
`2026-07-13-baml-final-cleanup-v1` +
`2026-07-13-fix-baml-50-out-of-scope-errors-v1`.)*

#### Scenario: no bare MarkingPoint class remains

- **GIVEN** the duplicate-class cleanup has landed
- **WHEN** the BAML tree is searched for exact class declarations matching `^class MarkingPoint\b`
- **THEN** the count is `0`
- **AND** `MarkingCriteria.marking_points` in
      `_shared/strand_outcome.baml` uses `MarkingPointStrand[]`
- **AND** `MarkingSchemeSec.markingPoints` in
      `pdfs/leaving_cert_marking_scheme.baml` uses `MarkingPointSec[]`

#### Scenario: all 7 lc_extraction/*.baml files use canonical syntax

- **GIVEN** the 2026-07-13-fix-baml-50-out-of-scope-errors-v1 change has landed
- **WHEN** `grep -rE '^\s+[a-z_][a-zA-Z0-9_]*:\s+(string|int|float|bool|list|map|class|enum|optional)\b' cianfhoghlaim/baml/education/lc_extraction/` is run
- **THEN** the count of Pydantic-style lines is 0 across all 7 files
- **AND** `mise run baml:generate` exits 0 against the BIEP v1
      contract types

#### Scenario: BIEP v1 contract types remain unchanged

- **GIVEN** the duplicate-class renames (`MarkingScheme` →
      `MarkingSchemeShared` in `_shared/content_types.baml`;
      `BilingualText` → `BilingualTextRootPdf` in
      `pdfs/root_pdf_extraction.baml`; `NCCAKeyCompetency` →
      `NCCAKeyCompetencyRootPdf` in `pdfs/root_pdf_extraction.baml`;
      `CrossNationLearningOutcome` → `CrossNationLearningOutcomeIsles`
      in `cross_nation/isles_education.baml`)
- **WHEN** the BIEP v1 contract types are enumerated from the
      regenerated `baml_client/types.py`
- **THEN** the canonical class names `MarkingScheme`, `BilingualText`,
      `NCCAKeyCompetency`, `CrossNationLearningOutcome`, `PastPaper`,
      `MarkingSchemeSec`, `MarkingSchemeStrand`, `SyllabusDocument`,
      `MarkAllocation`, `GradeDescriptor`, `DiagramPayload` are all
      present
- **AND** no class name collides with the renamed duplicates

#### Scenario: 7 canonical BIEP v1 extraction functions still produce output

- **GIVEN** the BIEP v1 contract types are unchanged
- **WHEN** `mise run baml:test` is invoked
- **THEN** each of the 7 canonical extraction functions
      (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
      `ExtractMarkingSchemeGuideline`, `ExtractStrandFromCatalog`,
      `ExtractMarkingSchemeStrand`,
      `ExtractCelticCurriculumComparison`, `ExtractSyllabusDiagram`)
      has at least one test block that compiles successfully
- **AND** the `baml_client/` regeneration succeeds against the same
      input schemas as before this change

### Requirement: R5 — Phase 6 (6 per-subject marimo notebooks)

The system SHALL provide 6 per-subject marimo notebooks at
`cianfhoghlaim/notebooks/leaving_cert/`: 1 each for `chemistry.py`,
`computer_science.py`, `gaeilge.py` (Irish-only; includes the
`irish_fada` asset_check badge), `geography.py`, `mathematics.py`,
plus the 7th `06_en_vs_ga_comparison.py` cross-subject EN ↔ GA
competency comparison + bilingual coverage matrix.

Each notebook SHALL be a runnable PEP 723 marimo file
(`__generated_with = "0.13.0"`), connect to the `md:oideachais`
lakehouse via
`cianfhoghlaim.notebooks.nb_utils.connect_biep_lakehouse()`, render
5 visualisations per notebook (topic frequency per year, exam paper
difficulty trend, marking scheme complexity, cross-linguistic mapping
for gaeilge + 06_en_vs_ga_comparison, asset generator via the
per-subject `qpack_<subject>.baml` function), invoke the canonical
BAML extractors (`ExtractCurriculumSyllabus` + `ExtractExamPaperLayout` +
`ExtractMarkingSchemeGuideline` + `ExtractSyllabusDiagram`), be
~300–400 LOC, and preserve bilingual EN + GA UI strings.

*(Consolidates the 1 ADDED Requirement from
`2026-07-13-biep-v1-phases-6-7-unblock-v1` for the Phase 6 part.)*

#### Scenario: Teacher opens the chemistry BIEP notebook

- **GIVEN** the `md:oideachais` MotherDuck lakehouse is up and the
      chemistry BAML extraction has produced rows in
      `oideachais.leaving_cert.chemistry_topics`
- **WHEN** a teacher runs
      `marimo edit cianfhoghlaim/notebooks/leaving_cert/chemistry.py`
- **THEN** the notebook renders 5 altair visualisations (topic
      frequency line chart, exam paper difficulty bar chart, marking
      scheme complexity heatmap, experiment ↔ learning outcome
      coverage, and the chemistry qpack asset generator) against
      live lakehouse data
- **AND** the BAML extractor cells show typed Pydantic records
      (not raw exceptions) for at least the chemistry syllabus PDF

#### Scenario: Gaeilge notebook preserves Irish fada

- **GIVEN** the gaeilge notebook renders
- **WHEN** the `irish_fada` asset_check fires on the loaded topic strings
- **THEN** every Irish-language string in
      `oideachais.leaving_cert.gaeilge_topics.topic_label_ga`
      preserves the fada diacritic (e.g. `Máirt`, `Gaeilge`,
      `scríbhneoir`, `Cian`, `Áireamhán`)
- **AND** the `gaeilge` notebook's "Cross-linguistic mapping" viz
      shows the EN ↔ GA topic pair side-by-side

#### Scenario: 06_en_vs_ga_comparison renders the bilingual coverage matrix

- **GIVEN** the bilingual EN + GA subject assets are loaded
- **WHEN** a teacher opens
      `cianfhoghlaim/notebooks/leaving_cert/06_en_vs_ga_comparison.py`
- **THEN** the notebook shows the EN ↔ GA topic coverage matrix
      for the 5 EN/GA subjects (Chemistry, Computer Science, Geography,
      Mathematics, English)
- **AND** the bilingual coverage heatmap shows the per-topic
      EN/GA gap (topics where the GA label is missing or stale)

### Requirement: R6 — Phase 7 (Daily MotherDuck lc_pdf_sync_flight)

The system SHALL schedule a daily MotherDuck Flight
`lc_pdf_sync_flight` at
`cianfhoghlaim/motherduck/flights/lc_pdf_sync_flight.py` that:

1. Runs `uv run cocoindex update lc_subjects` to re-ingest the 6 LC
   subjects' PDF corpus (any new PDFs landed in
   `s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<file>.pdf`
   in the last 24h)
2. Runs `uv run dagster asset materialize --select '*lc*'` to
   re-materialise the 6×6+2 = 38 LC assets (6 subjects × 6 stages +
   gov.ie circulars)
3. Writes a status row to
   `md:oideachais.lc_ops.daily_sync_status(flight_name,
   started_at, completed_at, status, log)` capturing the subprocess
   exit codes + the full log

The Flight SHALL be registered in
`cianfhoghlaim/motherduck/flights/config.yaml` with
`schedule: "0 4 * * *"` (daily at 04:00 UTC). The IaC orchestration
(Docker Compose stack + cron binding) lives in the separate
`bonneagar` repo at `bonneagar/stacks/motherduck/`.

*(Consolidates the 1 ADDED Requirement from
`2026-07-13-biep-v1-phases-6-7-unblock-v1` for the Phase 7 part.)*

#### Scenario: New PDF lands in Garage S3

- **GIVEN** a teacher (or upstream agent) has uploaded a new
      mathematics syllabus PDF to
      `s3://garage/oideachais/leaving_cert/mathematics/en/2026/Q1.pdf`
- **WHEN** 24 hours elapse and the daily `lc_pdf_sync_flight`
      fires at 04:00 UTC
- **THEN** the Flight's `cocoindex update lc_subjects` step
      detects the new PDF and re-ingests it
- **AND** the `dagster asset materialize --select '*lc*'`
      step materialises the corresponding `lc5_mathematics_extract`
      asset
- **AND** the resulting typed rows appear in
      `md:oideachais.leaving_cert.mathematics` within minutes
- **AND** a status row with `status='ok'` lands in
      `md:oideachais.lc_ops.daily_sync_status`

#### Scenario: Daily flight failure is recorded

- **GIVEN** the `lc_pdf_sync_flight` runs at 04:00 UTC
- **WHEN** either the `cocoindex update` step OR the
      `dagster asset materialize` step exits non-zero
- **THEN** the Flight's status row in
      `md:oideachais.lc_ops.daily_sync_status` has `status='failed'`
- **AND** the `log` column contains the captured stderr from
      the failed subprocess
- **AND** the daily BIEP dive
      (`lc_syllabus_topics`) is not marked stale until the next
      successful run

### Requirement: R7 — BIEP 6-subject marking + interactive grading

The system SHALL provide per-subject marking scheme ingestion +
per-subject interactive grading for the 6 BIEP v1 LC subjects —
Mathematics, Chemistry, Geography, Gaeilge, English, Computer
Science — by extending the canonical `MarkingScheme` + `ExamPaper`
extractors with per-subject discriminators (subject-specific enums +
classes) and by adding per-subject grading functions
(`Grade<Subject>Response` + `Explain<Subject>MarkingScheme`) that the
6 per-subject tutor agents (Math, Chem, Geog, Gael, Eng, CS) can
call.

The per-subject deliverable surface: 6 per-subject marking scheme
BAML files at `cianfhoghlaim/baml/education/marking/<subject>_marking.baml`
+ 6 per-subject grading BAML files at
`cianfhoghlaim/baml/education/grading/<subject>_grading.baml` + 6 L1
ingestion defs YAMLs at
`cianfhoghlaim/orchestration/defs/1_ingestion/marking/<subject>.yaml`
+ 6 L2 materials defs YAMLs at
`cianfhoghlaim/orchestration/defs/2_materials/grading/<subject>.yaml`.

*(Consolidates the 1 ADDED Requirement from
`2026-07-16-biiep-v1-lc-per-subject-marking-grading-v1`.)*

#### Scenario: 12 per-subject BAML files exist for the 6 BIEP v1 LC subjects

- **GIVEN** the BIEP v1 capspec covers the 6 priority Irish LC
      subjects
- **WHEN** the operator checks the per-subject BAML surface under
      `cianfhoghlaim/baml/education/marking/` +
      `cianfhoghlaim/baml/education/grading/`
- **THEN** 12 files SHALL exist (6 marking + 6 grading, one per
      subject per surface)

#### Scenario: 12 per-subject defs YAMLs exist

- **WHEN** the operator checks the L1 + L2 defs surface
- **THEN** 12 YAMLs SHALL exist (6 L1 at
      `orchestration/defs/1_ingestion/marking/` + 6 L2 at
      `orchestration/defs/2_materials/grading/`)
- **AND** each L1 YAML SHALL be a `CelticIngestionComponent` with
      `source_id = filesystem.marking.<subject>`
- **AND** each L2 YAML SHALL be a `CelticMaterialsComponent` with
      `baml_function = b.Grade<Subject>Response`

#### Scenario: per-subject grading uses per-subject discriminators (Mathematics)

- **GIVEN** a Mathematics question with `q_id = "q3a"`, `level = HL`
- **WHEN** the math tutor agent calls
      `b.GradeMathematicsResponse(student_answer, question, marking_scheme, is_higher_level=True)`
- **THEN** the system SHALL return a `MathematicsGrade` with
      `step_marks[].step_label` referring to Mathematics-specific
      step labels (e.g. "Set up chain rule", "Apply dy/dx")
- **AND** the `most_common_mistake_made` SHALL pick from the
      `MathCommonMistake` enum (e.g. `SIGN_ERROR`)
- **AND** the per-step `feedback` SHALL reference concrete
      calculus steps, not generic feedback

#### Scenario: Gaeilge grading is GA-primary

- **GIVEN** a Gaeilge question (taught in Irish)
- **WHEN** the gael tutor agent calls
      `b.GradeGaeilgeResponse(student_answer, question, marking_scheme, is_higher_level=True)`
- **THEN** the system SHALL return a `GaeilgeGrade` with
      `overall_feedback_ga` in Irish (canonical)
- **AND** `overall_feedback_en` SHALL be a translation helper (optional)
- **AND** the asset check on the L2 defs SHALL be `irish_fada`
      (asserts Irish text preserves the síneadh fada)

## Cross-references *(unchanged — pre-existing)*

- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) — the parent capability (5 education stages + leabharlann corpus)
- [`agent-platform-cluster`](../agent-platform-cluster/spec.md) — the 8-stack substrate (MotherDuck + Dagster + LiteLLM + Langfuse)
- [`ncca-leaving-cert-root-pdfs`](../ncca-leaving-cert-root-pdfs/spec.md) *(merged into oideachais-pipeline)* — the 5 NCCA root-level programme PDFs
- [`apple-photos-ingestion`](../apple-photos-ingestion/spec.md) — the 5th leabharlann corpus, sharing the same CocoIndex v1 pattern
- [`motherduck-dives`](../../.agents/skills/motherduck-create-dive/SKILL.md) — the 4 Dive authoring model

## R-group history *(added by this consolidation change)*

| R-group | Source change(s) | Logical feature |
|:--|:--|:--|
| **R0** | *(pre-existing)* | Phase 0 foundation — 6 Irish LC subjects end-to-end |
| **R1** | `2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1` | Phase 1.1 English lc5 filesystem wiring + duplicate cleanup (2 ADDEDs combined) |
| **R2** | `2026-07-13-biep-v1-phase-1-1-english-wiring-v1` | Phase 1.1 verification gates (4 gates: LC6_SUBJECTS, LC_PDF_KIND_REGISTRY, lc5_english_* assets, english.yaml) |
| **R3** | `2026-07-16-biiep-v1-lc-per-subject-syllabus-ingestion-v1` | Phase 1.4 BIEP 6-subject foundation (per-subject NCCA syllabus ingestion + unified BAML extractor) |
| **R4** | `2026-07-13-baml-final-cleanup-v1` + `2026-07-13-fix-baml-50-out-of-scope-errors-v1` | Phase 4-5 BAML fix (MarkingPoint classes + v0.212+ canonical syntax in lc_extraction; 2 ADDEDs combined) |
| **R5** | `2026-07-13-biep-v1-phases-6-7-unblock-v1` (Phase 6 part) | Phase 6 — 6 per-subject marimo notebooks |
| **R6** | `2026-07-13-biep-v1-phases-6-7-unblock-v1` (Phase 7 part) | Phase 7 — Daily MotherDuck lc_pdf_sync_flight |
| **R7** | `2026-07-16-biiep-v1-lc-per-subject-marking-grading-v1` | BIEP 6-subject marking + interactive grading |

**Summary**: 9 ADDED Requirements from 7 source changes consolidated
into 8 R-groups (R0–R7).

## Migrated from: *(none)*