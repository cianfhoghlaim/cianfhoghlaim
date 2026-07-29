# British-Isles Education Pipeline Capability

## Purpose

`british-isles-education-pipeline` (BIEP) is the flagship
ingestion+extraction+embedding+orchestration+analytics capability of the
Cianfhoghlaim platform. v1 covers the 6 priority Irish Leaving
Certificate subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science) plus the cross-cutting `gov.ie` education
circulars stream.

The corresponding source code lives at:

- `cianfhoghlaim/dlt/british_isles/` (NCCA + SEC + gov.ie DLT sources)
- `cianfhoghlaim/baml/education/lc_extraction/*.baml` (the BAML extraction schemas)
- `cianfhoghlaim/cocoindex/chemistry_embedding.py` + 5 sibling per-subject CocoIndex flows
- `cianfhoghlaim/orchestration/defs/2_materials/lc_extraction/` (Dagster lc5/lc6 assets)
- `cianfhoghlaim/notebooks/leaving_cert/` (per-subject marimo notebooks)
- `motherduck:` (`md:oideachais`) as the analytics surface (4 Dives + 1 daily Flight)

## Background

The platform has been ingesting education content from NCCA and SEC
since 2026-03 (the pre-v4 `cianfhoghlaim-pipeline`). v1 brings the
6 priority subjects to fully-runnable end-to-end pipelines and adds
`gov.ie` education circulars as the cross-cutting ingestion stream.
Cross-nation extension (Scotland / Wales / England / NI / Isle of Man
/ Crown Dependencies) is deferred to v2 and explicitly out of scope for
this spec.
## Requirements
### Requirement: 6 Irish LC subjects end-to-end

The system SHALL provide NCCA + SEC + gov.ie DLT sources, BAML
extraction (lc5 + lc6), 6 v1 CocoIndex flows (one per subject), 42+
Dagster assets (`lc5_<subject>_documents` + `lc5_<subject>_extract` +
`lc6_<subject>_marking_schemes` + ... + the 2 gov.ie circular assets),
6 per-subject marimo notebooks + 1 cross-subject competency notebook,
for the 6 priority subjects: Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science.

#### Scenario: mise run dagster:oideachais → materialize all

- **WHEN** a teacher clicks "Materialize all" in the Dagster UI for the 6-subject pipeline
- **THEN** the 42+ lc5/lc6 assets materialise within minutes
- **AND** the 6 marimo notebooks show real data via `mo.sql(engine=md:oideachais)`
- **AND** the per-subject LanceDB `cianfhoghlaim.lc.<subject>.<level>_<lang>` tables are populated

#### Scenario: gaeilge-only syllabuses (no English sibling)

- **GIVEN** Gaeilge is taught through Irish only (no `en/`-sibling per syllabus)
- **WHEN** the BAML extraction runs
- **THEN** the system SHALL extract Ga-classified records only
- **AND** not raise a missing-English error

### Requirement: gov.ie education circulars ingestion

The system SHALL ingest `gov.ie` education circulars via a DLT source at
`cianfhoghlaim/dlt/british_isles/ireland/gov_ie_circulars.py`, extract via
BAML `circular_extraction.baml`, embed via the 7th v1 CocoIndex App
`government_circulars`, and surface via a dedicated MotherDuck Dive.

#### Scenario: New circular arrives

- **WHEN** the gov.ie RSS monitor detects a new circular
- **THEN** the BAML `ClassifyCircular` function is invoked
- **AND** the extracted record lands in `md:cianfhoghlaim.education.ie.circulars`
- **AND** the `governance_circulars` CocoIndex App fires within the 60-second live-update window

### Requirement: Daily MotherDuck Flight for BAML backfill

The system SHALL schedule a daily MotherDuck Flight `lc_pdf_sync_flight`
that re-runs BAML extraction on any new PDFs landed in
`s3://garage/cianfhoghlaim/leaving_cert/<subject>/<lang>/<year>/<file>.pdf`.

#### Scenario: PDF lands in Garage S3

- **WHEN** a new PDF is written to `s3://garage/cianfhoghlaim/leaving_cert/mathematics/en/2026/Q1.pdf`
- **THEN** the daily Flight picks it up within 24h
- **AND** the corresponding lc5/lc6 rows appear in `md:cianfhoghlaim.leaving_cert.mathematics`

### Requirement: Cross-nation extension deferred to v2

The system SHALL NOT (in v1) ingest Scotland (SQA), Wales (WJEC),
England (AQA/OCR/Edexcel), Northern Ireland (CCEA), Isle of Man,
Jersey, or Guernsey curricula. These are scoped for the separate v2
change and are explicitly out of scope for this spec.

#### Scenario: v2 boundary

- **WHEN** a developer queries the v1 BIEP for Scottish curriculum data
- **THEN** the system returns an empty result with the message
  "deferred to v2; cross-nation extension is the next phase"

### Requirement: 4 MotherDuck Dives (analytics layer)

The system SHALL provide 4 live MotherDuck Dives:

1. `lc_syllabus_topics` — topic coverage per subject
2. `lc_exam_paper_difficulty` — Bloom's taxonomy distribution per year
3. `lc_marking_complexity` — mark-allocation patterns per question
4. `gov_circulars_archive` — chronological archive with topic classification

#### Scenario: BIEP Dive analytics

- **WHEN** a teacher opens the `lc_syllabus_topics` Dive
- **THEN** the chart shows topic counts grouped by subject
- **AND** the data updates within 24h of new BAML extractions

### Requirement: BIEP Subject Notebooks — ibis-first wiring to local lakehouse

The system MUST ensure the 6 BIEP subject marimo notebooks (Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) under
`cianfhoghlaim/notebooks/04_biep_motherduck/` MUST default to the
local `bunchloch-infra` lakehouse via the `ibis.duckdb.connect()` +
`ibis.lancedb.connect()` entrypoints, with the per-subject
`ducklake_<subject>` database name. The system SHALL reject any raw
`duckdb.connect()` call in these notebooks per the ibis-first
contract from the `cianfhoghlaim-marimo-dashboards` spec.

#### Scenario: Math notebook reads from local Lakekeeper via ibis

- **GIVEN** the lakehouse stack (Garage + Lakekeeper + Lance) is up
  per the upgrade-4-stacks-with-infisical change
- **WHEN** the operator runs
  `marimo run cianfhoghlaim/notebooks/04_biep_motherduck/01_curriculum_educator.py`
- **THEN** the notebook's first data cell SHALL execute
      `conn = ibis.duckdb.connect("ducklake:postgres:...")`
- **AND** it SHALL resolve
      `lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`
- **AND** every data query SHALL be expressed as an ibis expression
  rather than raw SQL strings
- **AND** the operation SHALL complete within 10 seconds against the
  empty Lakekeeper (returns 0-row DataFrames, not errors)

#### Scenario: ibis is the canonical entrypoint, not raw duckdb

- **WHEN** the 6 BIEP notebooks are grepped
- **THEN** every `import duckdb` is replaced by `import ibis`
- **AND** every `duckdb.connect(uri)` call is replaced by
  `ibis.duckdb.connect(uri)`
- **AND** the `ibis` skill is referenced in the per-notebook
  `## KCG patterns used` docstring

### Requirement: BIEP BAML surface drift fix (5 categories)

The system SHALL compile the full BIEP BAML surface without errors. The
following 5 drift categories SHALL be eliminated:

1. **Default-value class fields** SHALL NOT exist in `baml_src/`. Class
   field declarations SHALL NOT carry `= "<value>"` syntax. Optional
   fields SHALL use the `field type?` syntax instead.
2. **Unterminated strings** SHALL NOT exist in any `@description`,
   `prompt`, or `args { ... }` block.
3. **Test block keyword** SHALL be PascalCase `Test` (not `test`). BAML
   0.222+ requires PascalCase.
4. **Function block `client` field** SHALL be present on every `function`
   block. The `client <Name>` line SHALL appear before `prompt #"..."`.
5. **String-literal type references** SHALL NOT exist in class field
   type annotations. Use bare class references (resolved by the BAML
   type system) instead.

#### Scenario: baml-cli generate succeeds

- **WHEN** the user runs `mise run baml:generate` (or `cic:baml:generate`)
- **THEN** BAML SHALL generate the Python client into `baml_client/` without error
- **AND THEN** exit 0

#### Scenario: baml-cli test passes

- **WHEN** the user runs `mise run baml:test` (or `cic:baml:test`)
- **THEN** all `Test PascalCaseDescription { ... }` blocks SHALL execute
- **AND THEN** all assertions SHALL pass
- **AND THEN** exit 0

#### Scenario: BIEP client declarations

- **WHEN** the BIEP v3 hardening change (`2026-08-07-biep-v3-hardening-v1`) ships
- **THEN** the BIEP canonical 3 clients (`BIEPV3Extract`,
      `BIEPV3ExtractStrong`, `BIEPV3Vision`) SHALL each declare a distinct
      model: `gemma-3-4b-it`, `qwen3-vl-8b-it`,
      `qwen3-vl-8b-it-via-llama-swap` respectively
- **AND THEN** the legacy `ExtractEn` / `ExtractEnStrong` aliases MAY collapse to
      a single model (per the BIEP v3 consolidation rationale)

#### Scenario: No `baml_src` field references latent missing types

- **WHEN** any `.baml` file references a class (e.g., `GradeDescriptor`)
- **THEN** that class SHALL be either declared in the same file or
      imported from `_shared/` (no string-literal type references)

### Requirement: Per-subject marking scheme + exam paper ingestion + interactive grading (6 BIEP v1 LC subjects)

The system SHALL provide per-subject marking scheme ingestion + per-subject
interactive grading for the 6 BIEP v1 LC subjects — Mathematics,
Chemistry, Geography, Gaeilge, English, Computer Science — by extending
the canonical `MarkingScheme` + `ExamPaper` extractors with per-subject
discriminators (subject-specific enums + classes) and by adding
per-subject grading functions (`Grade<Subject>Response` +
`Explain<Subject>MarkingScheme`) that the 6 per-subject tutor agents
(Math, Chem, Geog, Gael, Eng, CS) can call.

The per-subject deliverable surface:

- 6 per-subject marking scheme BAML files at
  `baml/education/marking/<subject>_marking.baml`
- 6 per-subject grading BAML files at
  `baml/education/grading/<subject>_grading.baml`
- 6 L1 ingestion defs YAMLs at
  `orchestration/defs/1_ingestion/marking/<subject>.yaml`
- 6 L2 materials defs YAMLs at
  `orchestration/defs/2_materials/grading/<subject>.yaml`

Each per-subject marking BAML has the `<Subject>MarkingScheme` Pydantic
class (with `<Subject>SubjectDiscriminator`) and an
`Extract<Subject>MarkingScheme` function. Each per-subject grading
BAML has the `<Subject>Grade` + `<Subject>MarkingRationale` classes
and the `Grade<Subject>Response` + `Explain<Subject>MarkingScheme`
functions.

Each L1 ingestion defs YAML is a `CelticIngestionComponent` with
`source_id = filesystem.marking.<subject>`, weekly cron (marking
schemes update rarely), and per-subject partitions (year + paper +
level + language).

Each L2 materials defs YAML is a `CelticMaterialsComponent` with
`baml_function = b.Grade<Subject>Response` and
`baml_explain_function = b.Explain<Subject>MarkingScheme`. Gaeilge
uses the `irish_fada` asset check (the canonical Gaeilge-side
fidelity guard); the other 5 subjects use `baml_fidelity`.

#### Scenario: 12 per-subject BAML files exist for the 6 BIEP v1 LC subjects

- **GIVEN** the BIEP v1 capspec covers the 6 priority Irish LC subjects
- Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science
- **WHEN** the operator checks the per-subject BAML surface under
  `baml/education/marking/` + `baml/education/grading/`
- **THEN** 12 files SHALL exist:
  - `mathematics_marking.baml`, `mathematics_grading.baml`
  - `chemistry_marking.baml`, `chemistry_grading.baml`
  - `geography_marking.baml`, `geography_grading.baml`
  - `gaeilge_marking.baml`, `gaeilge_grading.baml`
  - `english_marking.baml`, `english_grading.baml`
  - `computer_science_marking.baml`, `computer_science_grading.baml`

#### Scenario: 12 per-subject defs YAMLs exist

- **WHEN** the operator checks the L1 + L2 defs surface
- **THEN** 12 YAMLs SHALL exist:
  - `orchestration/defs/1_ingestion/marking/{mathematics,chemistry,geography,gaeilge,english,computer_science}.yaml`
  - `orchestration/defs/2_materials/grading/{mathematics,chemistry,geography,gaeilge,english,computer_science}.yaml`
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

#### Scenario: Mathematics marking extraction yields subject discriminator

- **GIVEN** an NCCA Mathematics marking-scheme PDF for HL 2024
- **WHEN** the operator calls `b.ExtractMathematicsMarkingScheme(pdf_text, year=2024, level="hl")`
- **THEN** the system SHALL return a `MathematicsMarkingScheme` with
  `subject_specific.band_scheme = MathMarkingBand.H1..H7`
- **AND** `subject_specific.has_formula_sheet = true` (always true for LC Maths)
- **AND** `subject_specific.most_common_mistake` SHALL be one of the
  `MathCommonMistake` enum values

### Requirement: Per-subject NCCA syllabus ingestion + BAML extraction (6 BIEP v1 LC subjects)

The system SHALL provide per-subject NCCA syllabus ingestion + per-subject
BAML extraction for the 6 BIEP v1 LC subjects — Mathematics, Chemistry,
Geography, Gaeilge, English, Computer Science — by shipping 6 per-subject
NCCA crawl DLT sources (`ncca_<subject>.py`), verifying 6 per-subject qpack
BAMLs (`qpack_<subject>.baml`), exposing a unified BAML extractor
(`ExtractLC6Syllabus(subject, text, language) -> LCSyllabus`), and wiring
6 per-subject L1 ingestion defs YAMLs (one `CelticIngestionComponent` per
subject, daily 04:00 UTC cron, subject × language partitions = 2
partitions per subject, 12 partitions total).

This is the foundation for the BIEP v1 agent + dashboard + study-tool
work (Picks 2-5): a single call site
(`b.ExtractLC6Syllabus(subject="<subject>", text=..., language="<en|ga>")`)
replaces six different `b.ExtractCurriculumSyllabus(text)` invocations
and gives downstream agents one stable discriminated `LCSyllabus` return
shape.

The per-subject deliverable surface:

- 6 per-subject NCCA crawl DLT sources at
  `dlt/british_isles/ireland/education/ncca_<subject>.py`
- 6 per-subject qpack BAMLs at
  `baml/education/subjects/qpack_<subject>.baml` (EXISTING)
- 1 unified BAML extractor at
  `baml/education/unified_extraction.baml`
- 1 named destinations factory at
  `dlt/common/named_destinations.py`
- 6 per-subject L1 defs YAMLs at
  `orchestration/defs/1_ingestion/curriculum/lc6/<subject>.yaml`

Each per-subject NCCA crawl DLT source carries the canonical BIEP v1 dlt
pattern: `@dlt.resource(name="<subject>_syllabus",
write_disposition="merge", primary_key=["url"])`, the `named_destinations`
factory (the `warehouse` named destination),
`USE_LOCAL_SCRAPES=true` honour to read from
`stedding/ingest_queue/ncca/<subject>/<lang>/`, and the `default` BAML
client (minimax-m3 per `667635dfd`).

The unified BAML extractor `ExtractLC6Syllabus(subject, text, language) -> LCSyllabus`
exposes 6 per-subject thin wrappers
(`ExtractMathSyllabus`, `ExtractChemSyllabus`, `ExtractGeogSyllabus`,
`ExtractGaelSyllabus`, `ExtractEnglSyllabus`, `ExtractCompSyllabus`)
and the `LCSyllabus` discriminated Pydantic class (extends the canonical
`SyllabusDocument` with the per-subject discriminator).

Each L1 defs YAML is a `CelticIngestionComponent` with `source_id =
filesystem.leaving_cert.<subject>`, `automation_cron = "0 4 * * *"`
(daily 04:00 UTC), `state_backed = true`,
`state_refresh_interval = "monthly"`, and per-subject partitions
(subject × language = 2 partitions per subject).

#### Scenario: 6 per-subject DLT sources + 6 qpack BAMLs + 1 unified BAML extractor + 6 defs YAMLs exist

- **GIVEN** the BIEP v1 capspec covers the 6 priority Irish LC subjects
  — Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science
- **WHEN** the operator checks the per-subject surface
- **THEN** 13 files SHALL exist:
  - `dlt/british_isles/ireland/education/ncca_mathematics.py`
  - `dlt/british_isles/ireland/education/ncca_chemistry.py`
  - `dlt/british_isles/ireland/education/ncca_geography.py`
  - `dlt/british_isles/ireland/education/ncca_gaeilge.py`
  - `dlt/british_isles/ireland/education/ncca_english.py`
  - `dlt/british_isles/ireland/education/ncca_computer_science.py`
  - `baml/education/subjects/qpack_mathematics.baml`
  - `baml/education/subjects/qpack_chemistry.baml`
  - `baml/education/subjects/qpack_geography.baml`
  - `baml/education/subjects/qpack_gaeilge.baml`
  - `baml/education/subjects/qpack_english.baml`
  - `baml/education/subjects/qpack_computer_science.baml`
  - `baml/education/unified_extraction.baml`
- **AND** 6 per-subject L1 defs YAMLs SHALL exist at
  `orchestration/defs/1_ingestion/curriculum/lc6/`
  (`mathematics.yaml`, `chemistry.yaml`, `geography.yaml`,
  `gaeilge.yaml`, `english.yaml`, `computer_science.yaml`)

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
- **AND** `partitions` SHALL cover subject × language (2 partitions per subject)

### Requirement: All 7 lc_extraction/*.baml files use v0.212+ canonical `field Type` whitespace syntax

The British-Isles Education Pipeline SHALL enforce that every `.baml` file under `baml/education/lc_extraction/` uses the BAML v0.212+ canonical `field Type` (whitespace-separated) syntax — not the legacy Pydantic-style `field: type` colon-separated syntax. The 7 lc_extraction files (`circular_extraction.baml`, `cross_linguistic.baml`, `curriculum_syllabus.baml`, `exam_paper_layout.baml`, `lc_topic_extraction.baml`, `marking_scheme.baml`, `syllabus_diagram.baml`) define the canonical BIEP v1 contract types (`MarkingScheme`, `BilingualText`, `NCCAKeyCompetency`, `CrossNationLearningOutcome`, `PastPaper`, `SyllabusDocument`, `MarkAllocation`, `GradeDescriptor`, `DiagramPayload`, etc.) and the 7 canonical extraction functions (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`, `ExtractMarkingSchemeGuideline`, `ExtractStrandFromCatalog`, `ExtractMarkingSchemeStrand`, `ExtractCelticCurriculumComparison`, `ExtractSyllabusDiagram`).

#### Scenario: all 7 lc_extraction/*.baml files use canonical syntax

- **GIVEN** the 2026-07-13-fix-baml-50-out-of-scope-errors-v1 change has landed
- **WHEN** `grep -rE '^\s+[a-z_][a-zA-Z0-9_]*:\s+(string|int|float|bool|list|map|class|enum|optional)\b' baml/education/lc_extraction/` is run
- **THEN** the count of Pydantic-style lines is 0 across all 7 files
- **AND** `mise run baml:generate` exits 0 against the BIEP v1 contract types

#### Scenario: BIEP v1 contract types remain unchanged

- **GIVEN** the duplicate-class renames (`MarkingScheme` → `MarkingSchemeShared` in `_shared/content_types.baml`; `BilingualText` → `BilingualTextRootPdf` in `pdfs/root_pdf_extraction.baml`; `NCCAKeyCompetency` → `NCCAKeyCompetencyRootPdf` in `pdfs/root_pdf_extraction.baml`; `CrossNationLearningOutcome` → `CrossNationLearningOutcomeIsles` in `cross_nation/isles_education.baml`)
- **WHEN** the BIEP v1 contract types are enumerated from the regenerated `baml_client/types.py`
- **THEN** the canonical class names `MarkingScheme`, `BilingualText`, `NCCAKeyCompetency`, `CrossNationLearningOutcome`, `PastPaper`, `MarkingSchemeSec`, `MarkingSchemeStrand`, `SyllabusDocument`, `MarkAllocation`, `GradeDescriptor`, `DiagramPayload` are all present
- **AND** no class name collides with the renamed duplicates (the duplicate-rename is forward-compatible with the BIEP v1 contract — the canonical names stay in `lc_extraction/*.baml` and the renamed duplicates live in adjacent files)

#### Scenario: 7 canonical BIEP v1 extraction functions still produce output

- **GIVEN** the BIEP v1 contract types are unchanged
- **WHEN** `mise run baml:test` is invoked
- **THEN** each of the 7 canonical extraction functions (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`, `ExtractMarkingSchemeGuideline`, `ExtractStrandFromCatalog`, `ExtractMarkingSchemeStrand`, `ExtractCelticCurriculumComparison`, `ExtractSyllabusDiagram`) has at least one test block in `lc_extraction/*.baml` or `cross_nation/*.baml` that compiles successfully
- **AND** the `baml_client/` regeneration succeeds against the same input schemas as before this change

### Requirement: All 6 LC subjects have working filesystem DLT source

The system SHALL ingest every PDF (and JPG for the scanned geography exam
page) in `leaving_certificate/{chemistry,computer_science,english,gaeilge,geography,mathematics}/`
through a single filesystem DLT resource
(`cianfhoghlaim.dlt.filesystem.leaving_cert_source.lc5_documents` with
`LC6_SUBJECTS = ("chemistry", "computer_science", "english", "gaeilge",
"geography", "mathematics")`). English is en-only at the root of its
subject directory (mirrors the gaeilge asymmetry but with `language = "en"`).
The `LC_PDF_KIND_REGISTRY` SHALL contain explicit regex patterns for both
the English exam-paper kind (`LC002ALP\d{3}[EI]V\.pdf`) and the English
spec-constitution kind (`SC-English-Spec-ENG-INT.*\.pdf`).

#### Scenario: English contributes 8 PDFs to the filesystem resource

- **GIVEN** the 8 PDFs in `leaving_certificate/english/`
      (`LC002ALP100EV.pdf`, `LC002ALP200EV.pdf`, `LC002GLP100EV.pdf`,
      `LC002GLP200EV.pdf`, `SCSEC14_English_Syllabus.pdf`,
      `SCSEC14_English_Syllabus_2026-06-30.pdf`,
      `SC-English-Spec-ENG-INT.pdf`,
      `SC-English-Spec-ENG-INT_2026-06-30.pdf`)
- **WHEN** `from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents; rows = list(lc5_documents())` runs
- **THEN** exactly 8 rows have `subject == "english"` and `language == "en"`
- **AND** the 4 exam papers route through `model_key = "qwen3-vl-8b"`
- **AND** the 4 syllabi / spec constitutions route through `model_key = "gemma-4-26B-A4B"`
- **AND** the total row count is ≥ 80 (the 6 subjects × 2 languages

  minus the english ga-only and gaeilge en-only subjects)

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

### Requirement: No duplicate DLT source files (curriculum_source.py deleted)

The canonical Irish curriculum DLT source SHALL live exclusively at
`dlt/british_isles/ireland/education/curriculum.py`.
The legacy 972-LOC byte-identical duplicate
`dlt/british_isles/ireland/education/curriculum_source.py`
and the 0-byte stub `exam_source_update.py` SHALL NOT exist. All 11
importers (5 in `dlt/british_isles/ireland/law/` + 5 in
`dlt/british_isles/ireland/education/law/` + the canonical
`curriculum.py`'s own docstring + the `test_curriculum_source_local_cache.py`
test) SHALL import `_crawl_source` from `...education.curriculum` (not
`...education.curriculum_source`).

#### Scenario: The duplicate pair is gone

- **WHEN** a developer runs `ls dlt/british_isles/ireland/education/ | grep -E "curriculum_source|exam_source_update"`
- **THEN** zero matches SHALL be returned
- **AND** `curriculum.py` (972 LOC) remains the sole canonical surface

#### Scenario: The 11 importers resolve against the kept file

- **GIVEN** `curriculum.py` defines `_crawl_source` at line 57
      (verified via `grep -n "^def _crawl_source" dlt/british_isles/ireland/education/curriculum.py`)
- **WHEN** any of the 11 importer modules is loaded
- **THEN** the import `from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import _crawl_source` SHALL succeed
- **AND** zero matches SHALL be returned by
      `grep -rn "from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum_source" cianfhoghlaim/`
- **AND** zero matches SHALL be returned by
      `grep -rn "from cianfhoghlaim.dlt.british_isles.ireland.education.exam_source_update" cianfhoghlaim/`

### Requirement: Filesystem scanner domain (BIEP v3)

The system SHALL provide a canonical `filesystem` domain in the BIEP v3
cross-jurisdiction registry that aggregates the 11 canonical filesystem
DLT sources at `dlt_sources/filesystem/`:

1. `leabharlann_books` — `leabharlann/{gaeilge,aigne}/` (EPUB + preview pairing)
2. `gemini_deep_research` — `leabharlann/gemini_deep_research/`
3. `google_takeout` — `Takeout/<account_label>/` (per-account)
4. `takeout_v1` — `stedding/Takeout/` (multi-account auto-discovery)
5. `email_inbox` — `/srv/mailcow-exports/*.mbox` (4-account email-inbox pipeline)
6. `leaving_cert_source` — filesystem scanner for the Ireland LC PDFs
7. `university_of_galway` — `leabharlann/ollscoil_na_gaillimhe/`
8. `zotero` — `leabharlann/zotero/` (real Zotero storage format)
9. `gemini_corpus_source` — Gemini corpus loader
10. `pdf_download_source` — PDF downloader
11. `previews` — preview pairing

The 3 generic Dagster assets (ingestion + extraction + embedding)
MUST be defined at
`orchestration/defs/2_materials/filesystem_pipelines/generic_filesystem_assets.py`.

The 1 monthly MotherDuck Flight MUST be at
`motherduck/flights/filesystem_monthly_sync_flight.py`.

#### Scenario: Filesystem ingestion produces >= 1 row per run

- **WHEN** the operator runs `mise run filesystem:monthly:sync`
- **THEN** the `filesystem_documents_ingested` asset materialises
- **AND** the 11 filesystem sources emit >= 1 row each
- **AND** the 3 filesystem asset checks pass

### Requirement: Language scanner domain (BIEP v3)

The system SHALL provide a canonical `language` domain in the BIEP v3
cross-jurisdiction registry that aggregates the 19 canonical language
DLT sources at `dlt_sources/language/`:

1. `ainm` — Ainm (Irish place names)
2. `canuint` — Canúint (Irish intonation)
3. `canuint_audio` — Canúint audio samples
4. `canuint_dialect_summary` — Canúint dialect summary
5. `canuint_search` — Canúint lexical search
6. `canuint_word_alignment` — Canúint word alignment
7. `duchas` — Dúchas na hÉireann (Schools' Folklore Collection)
8. `duchas_images` — Dúchas images
9. `gaois` — Gaois (Irish language corpus)
10. `gaois_combined` — Gaois combined
11. `heritage` — Heritage sites
12. `hidden_heritages` — Hidden heritages
13. `local_documents_by_subject` — Local documents by subject
14. `local_education_documents` — Local education documents
15. `logainm` — Logainm (place names database)
16. `tearma` — Téarma (terminology database)
17. `tearma_search` — Téarma search
18. `universal_dependencies` — Universal Dependencies

The 3 generic Dagster assets (ingestion + extraction + embedding)
MUST be defined at
`orchestration/defs/2_materials/language_pipelines/generic_language_assets.py`.

The 1 monthly MotherDuck Flight MUST be at
`motherduck/flights/language_monthly_sync_flight.py`.

#### Scenario: Language ingestion produces >= 1 row per run

- **WHEN** the operator runs `mise run language:monthly:sync`
- **THEN** the `language_documents_ingested` asset materialises
- **AND** the 19 language sources emit >= 1 row each (when the cache is present)
- **AND** the 3 language asset checks pass

### Requirement: Monthly BIEP v3 scheduling for filesystem + language

The system SHALL run the filesystem + language assets on a MONTHLY
cadence (`0 0 1 * *`, 1st of each month 00:00 UTC) per the BIEP v3
scheduling policy. This is more frequent than the yearly education
content cadence because filesystem + language content changes more
often.

#### Scenario: Monthly cron fires for filesystem + language

- **WHEN** the monthly cron fires at 00:00 UTC on the 1st of the month
- **THEN** both the `filesystem_monthly_sync_flight` and
  `language_monthly_sync_flight` MotherDuck Flights run
- **AND** both write status rows to their respective audit tables
- **AND** the BIEP v3 canonical `make_monthly_circulars_automation()`
  AutomationCondition is used

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
- **1 CocoIndex v1 App** at `cocoindex/subjects/junior_cycle_embedding.py`
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

### Requirement: England (AQA + OCR + Edexcel) A-Level + GCSE

The system SHALL provide a full BIEP-grade England pipeline for the
3 main awarding bodies (AQA, OCR, Edexcel Pearson) × 9 priority subjects
(Mathematics, English Language, English Literature, Chemistry, Biology,
Physics, Computer Science, History, Geography) × 2 qualification levels
(GCSE, A-Level):

- **5 new BAML extraction functions** at `baml_src/british_isles/england/education/`:
  `ExtractAQAQualSpec`, `ExtractOCRQualSpec`, `ExtractEdexcelQualSpec`,
  `ExtractAQAExamPaper` (multi-board dispatch), `ExtractAQAMarkingScheme`
  (UMS / 9-1 grading) — plus `ExtractEnglandEnsembleConsensus` for Change 3's
  ensemble pipeline
- **27 per-subject DLT sources** at `dlt/british_isles/england/education/subjects/`
  (3 boards × 9 subjects), tagged with `country_code="england"`,
  `jurisdiction="england"`, `exam_board ∈ {aqa,ocr,edexcel}`,
  `qualification_level ∈ {gcse,a_level}`
- **3 CocoIndex v1 Apps** at `cocoindex/british_isles/england/{aqa,ocr,edexcel}_education_embedding.py`,
  producing 27 LanceDB tables `cianfhoghlaim.england.<board>.<subject>.<level>`
- **81+ Dagster assets** at
  `orchestration/defs/2_materials/england_education/{aqa,ocr,edexcel}/`
  (27 × 3 layers: ingest → BAML extract → embed + 3 cross-board comparator assets)
- **3 MotherDuck Dives** (`eng_aqa_curriculum_dive`, `eng_gcse_difficulty_dive`,
  `eng_a_level_complexity_dive`) + **1 daily Flight** `eng_daily_sync_flight`

#### Scenario: mise run dagster:oideachais → materialize all 3 England boards

- **WHEN** a researcher clicks "Materialize all" in the Dagster UI for the England pipeline
- **THEN** the 81 England assets materialise within minutes
- **AND** the 27 LanceDB tables `cianfhoghlaim.england.<board>.<subject>.<level>` are populated
- **AND** the `eng_aqa_curriculum_dive` MotherDuck Dive shows topic coverage per AQA subject
- **AND** the daily `eng_daily_sync_flight` re-runs BAML extraction on any new PDFs
  landed in `s3://garage/cianfhoghlaim/england/<board>/<subject>/<level>/`

#### Scenario: AQA vs OCR vs Edexcel spec diff

- **WHEN** a researcher opens the `eng_aqa_vs_ocr_diff` Dagster asset
- **AND** selects subject="mathematics", qualification_level="gcse"
- **THEN** the diff asset returns the side-by-side topic + assessment objective comparison
- **AND** it surfaces any spec changes between the 3 awarding bodies since the last sync

#### Scenario: Gaeilge/specialised subjects are deferred

- **GIVEN** the Ireland-only BAML `ExtractGaeilgeCurriculum` exists in the BIEP v1 LC pipeline
- **WHEN** a developer queries the England pipeline for `subject="gaeilge"`
- **THEN** the system returns an empty result with the message
  "Gaeilge not offered by AQA / OCR / Edexcel — see Ireland pipeline"

### Requirement: Phase 1.1 English lc5 wiring verified complete (2026-07-13)

The system SHALL satisfy the four static Phase 1.1 verification
gates on the `pick-4-biep-v1` branch as of 2026-07-13. The
Phase 1.1 sub-batch of the BIEP v1 flagship (the 6-subject LC
filesystem wiring for English) was already code-shipped by the
prior openspec change
`2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1` (commit
`ba234de61`); this delta captures the verification status, NOT
the implementation. The flagship's Phase 1.1 `[ ]` tick-boxes
remain un-ticked in the archived
`openspec/changes/archive/2026-07-09-2026-07-06-british-isles-education-pipeline-v1/tasks.md`
(the archive is frozen — modification would violate the "Do NOT
touch the 50+ archived openspec changes" hard rule), but the
underlying code state SHALL satisfy the four gates below.

#### Scenario: Gate 1 — `LC6_SUBJECTS` includes `english` as the 3rd element

- **GIVEN** the file
      `dlt/filesystem/leaving_cert_source.py`
- **WHEN** an agent runs `grep -A 7 "^LC6_SUBJECTS" dlt/filesystem/leaving_cert_source.py`
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
      `dlt/filesystem/leaving_cert_source.py`
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
      `orchestration/defs/2_materials/lc_extraction/lc5_assets.py`
- **THEN** the asset registry SHALL contain exactly these 6 names:
      - `lc5_english_ingested` (explicit `@asset` decorator, Layer 1)
      - `lc5_english_syllabus_extracted`
      - `lc5_english_papers_extracted`
      - `lc5_english_marking_extracted`
      - `lc5_english_diagrams_extracted`
      - `lc5_english_cognified` (explicit `@asset` decorator, Layer 3)
- **AND** the 4 `*_extracted` assets SHALL be generated at
      module-import time by the factory loop
      `for _subject in LC6_SUBJECTS: for _kind in ("syllabus",
      "papers", "marking", "diagrams"): globals()[f"lc5_{_subject}_{_kind}_extracted"]`
      at lines 199-201 (the loop binds to `LC6_SUBJECTS`, which
      contains `"english"` per Gate 1)

#### Scenario: Gate 4 — `english.yaml` cron asset exists

- **GIVEN** the path
      `orchestration/defs/1_ingestion/curriculum/lc5/english.yaml`
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

### Requirement: MarkingPoint classes are uniquely named per BAML file

The British-Isles Education Pipeline SHALL avoid duplicate BAML class names for marking-scheme point records. The cross-stage shared marking point class in `baml/education/_shared/strand_outcome.baml` SHALL be named `MarkingPointStrand`, and the SEC marking-scheme PDF extraction class in `baml/education/pdfs/leaving_cert_marking_scheme.baml` SHALL be named `MarkingPointSec`.

#### Scenario: no bare MarkingPoint class remains

- **GIVEN** the duplicate-class cleanup has landed
- **WHEN** the BAML tree is searched for exact class declarations matching `^class MarkingPoint\b`
- **THEN** the count is `0`
- **AND** `MarkingCriteria.marking_points` in `_shared/strand_outcome.baml` uses `MarkingPointStrand[]`
- **AND** `MarkingSchemeSec.markingPoints` in `pdfs/leaving_cert_marking_scheme.baml` uses `MarkingPointSec[]`

#### Scenario: remaining BAML diagnostics are scoped separately

- **GIVEN** `mise run baml:generate` is run after this duplicate rename
- **WHEN** BAML still reports parser diagnostics in `lc_extraction/*.baml` or other pre-existing files
- **THEN** those diagnostics remain owned by the BIEP v1 / dedicated BAML syntax cleanup scope decision, not by this MarkingPoint duplicate fix

### Requirement: BIEP v1 Phase 6 — 6 per-subject marimo notebooks

The British-Isles Education Pipeline SHALL provide 6 per-subject marimo
notebooks at `notebooks/leaving_cert/`:

1. `chemistry.py` — 5 visualisations of `cianfhoghlaim.leaving_cert.chemistry_*`
2. `computer_science.py` — 5 visualisations of `cianfhoghlaim.leaving_cert.computer_science_*`
3. `gaeilge.py` — 5 visualisations of `cianfhoghlaim.leaving_cert.gaeilge_*`
   (Irish-only; includes the `irish_fada` asset_check badge)
4. `geography.py` — 5 visualisations of `cianfhoghlaim.leaving_cert.geography_*`
5. `mathematics.py` — 5 visualisations of `cianfhoghlaim.leaving_cert.mathematics_*`
6. `06_en_vs_ga_comparison.py` — cross-subject EN ↔ GA competency
   comparison + bilingual coverage matrix (the 7th BIEP subject
   notebook per the spec's "BIEP Subject Notebooks" requirement)

Each notebook SHALL:

- Be a runnable PEP 723 marimo file (`__generated_with = "0.13.0"`)
- Connect to the `md:oideachais` lakehouse via
  `cianfhoghlaim.notebooks.nb_utils.connect_biep_lakehouse()`
- Render 5 visualisations per notebook: topic frequency per year
  (line chart), exam paper difficulty trend (bar chart), marking
  scheme complexity (heatmap), cross-linguistic mapping (for
  `gaeilge` and `06_en_vs_ga_comparison`), and an asset generator
  via the per-subject `qpack_<subject>.baml` function
- Invoke the canonical BAML extractors
  `ExtractCurriculumSyllabus` + `ExtractExamPaperLayout` +
  `ExtractMarkingSchemeGuideline` + `ExtractSyllabusDiagram`
- Be ~300–400 LOC each (the already-existing thin stubs at
  `notebooks/leaving_cert/` are enhanced up to that size)
- Preserve bilingual EN + GA UI strings (via the i18n helper at
  `web/packages/i18n/src/` or inline `mo.md(...)`
  strings in both English and Irish)

#### Scenario: Teacher opens the chemistry BIEP notebook

- **GIVEN** the `md:oideachais` MotherDuck lakehouse is up and the
  chemistry BAML extraction has produced rows in
  `cianfhoghlaim.leaving_cert.chemistry_topics`
- **WHEN** a teacher runs
  `marimo edit notebooks/leaving_cert/chemistry.py`
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
- **THEN** every Irish-language string in `cianfhoghlaim.leaving_cert.gaeilge_topics.topic_label_ga`
  preserves the fada diacritic (e.g. `Máirt`, `Gaeilge`, `scríbhneoir`,
  `Cian`, `Áireamhán`)
- **AND** the `gaeilge` notebook's "Cross-linguistic mapping" viz
  shows the EN ↔ GA topic pair side-by-side

#### Scenario: 06_en_vs_ga_comparison renders the bilingual coverage matrix

- **GIVEN** the bilingual EN + GA subject assets are loaded
- **WHEN** a teacher opens
  `notebooks/leaving_cert/06_en_vs_ga_comparison.py`
- **THEN** the notebook shows the EN ↔ GA topic coverage matrix
  for the 5 EN/GA subjects (Chemistry, Computer Science, Geography,
  Mathematics, English)
- **AND** the bilingual coverage heatmap shows the per-topic
  EN/GA gap (topics where the GA label is missing or stale)

### Requirement: BIEP v1 Phase 7 — Daily MotherDuck lc_pdf_sync_flight

The British-Isles Education Pipeline SHALL schedule a daily MotherDuck
Flight `lc_pdf_sync_flight` at
`motherduck/flights/lc_pdf_sync_flight.py`
that:

1. Runs `uv run cocoindex update lc_subjects` to re-ingest the
   6 LC subjects' PDF corpus (any new PDFs landed in
   `s3://garage/cianfhoghlaim/leaving_cert/<subject>/<lang>/<year>/<file>.pdf`
   in the last 24h)
2. Runs `uv run dagster asset materialize --select '*lc*'` to
   re-materialise the 6×6+2 = 38 LC assets (6 subjects × 6 stages +
   gov.ie circulars)
3. Writes a status row to
   `md:cianfhoghlaim.lc_ops.daily_sync_status(flight_name,
   started_at, completed_at, status, log)` capturing the
   subprocess exit codes + the full log

The Flight SHALL be registered in
`motherduck/flights/config.yaml` with
`schedule: "0 4 * * *"` (daily at 04:00 UTC). The IaC orchestration
(Docker Compose stack + cron binding) lives in the separate
`bonneagar` repo at `bonneagar/stacks/motherduck/`.

#### Scenario: New PDF lands in Garage S3

- **GIVEN** a teacher (or upstream agent) has uploaded a new
  mathematics syllabus PDF to
  `s3://garage/cianfhoghlaim/leaving_cert/mathematics/en/2026/Q1.pdf`
- **WHEN** 24 hours elapse and the daily `lc_pdf_sync_flight`
  fires at 04:00 UTC
- **THEN** the Flight's `cocoindex update lc_subjects` step
  detects the new PDF and re-ingests it
- **AND** the `dagster asset materialize --select '*lc*'`
  step materialises the corresponding `lc5_mathematics_extract`
  asset
- **AND** the resulting typed rows appear in
  `md:cianfhoghlaim.leaving_cert.mathematics` within minutes
- **AND** a status row with `status='ok'` lands in
  `md:cianfhoghlaim.lc_ops.daily_sync_status`

#### Scenario: Daily flight failure is recorded

- **GIVEN** the `lc_pdf_sync_flight` runs at 04:00 UTC
- **WHEN** either the `cocoindex update` step OR the
  `dagster asset materialize` step exits non-zero
- **THEN** the Flight's status row in
  `md:cianfhoghlaim.lc_ops.daily_sync_status` has `status='failed'`
- **AND** the `log` column contains the captured stderr from
  the failed subprocess
- **AND** the daily BIEP dive
  (`lc_syllabus_topics`) is not marked stale until the next
  successful run

### Requirement: Endpoint health monitoring for the British Isles

The system MUST provide a canonical `endpoint_recovery` helper at
`dlt/common/endpoint_recovery.py` that wraps every British Isles
DLT source's outbound network call. The helper MUST try the
following strategies in order:

1. **Plain HTTP crawl** via `dlt/common/site_crawler.py:crawl_site`
   for endpoints that respond with 200 to a browser User-Agent.
2. **Firecrawl `stealth` proxy** (via the Firecrawl MCP
   `firecrawl_scrape(..., proxy="stealth")`) for endpoints that 403
   to plain HTTP.
3. **Wayback Machine fallback**
   (`https://web.archive.org/web/2024/<url>`) for endpoints that
   403 even with stealth or that time-out.

Every call MUST return a `RecoveredPage` dataclass and emit a
structlog `endpoint_status{status, backend_used}` event.

#### Scenario: NCCA returns 403 to plain HTTP

- **WHEN** `endpoint_recovery.fetch("https://ncca.ie/en/", strategy="auto")`
  returns `status_code=403`
- **THEN** the helper MUST retry with `strategy="stealth"`
- **AND** if stealth returns 200, the helper MUST return that
  result tagged `backend_used="firecrawl_stealth"`
- **AND** if stealth also 403s, the helper MUST retry with the
  Wayback Machine
- **AND** the final returned `RecoveredPage.backend_used` MUST be
  one of `{"direct", "firecrawl_stealth", "wayback", "none"}`

### Requirement: 11 British Isles endpoints recovered

The system MUST recover the following 11 broken endpoints:

| Source | Endpoint | Strategy |
|:--|:--|:--|
| NCCA | `https://ncca.ie` | `stealth` |
| CurriculumOnline | `https://www.curriculumonline.ie` | `stealth` |
| SQA | `https://www.sqa.org.uk/sqa/56983.html` | `firecrawl_map` discovery |
| AQA | `https://www.aqa.org.uk/subjects/gcse` | `firecrawl_map` discovery |
| CCEA | `https://ccea.org.uk` | `stealth` |
| Courts.ie judgements | `https://www.courts.ie/judgements` | URL fix to `/search/judgements` |
| GMC | `https://www.gmc-uk.org` | `stealth` + `wait_for=10s` |
| IoM health | `https://www.gov.im/...` | `stealth` |
| IoM education | `https://www.gov.im/education` | `stealth` |
| Pearson | `https://qualifications.pearson.com/...` | `firecrawl_map` discovery |
| WJEC | `https://www.wjec.co.uk` | `firecrawl_map` discovery |

#### Scenario: All 11 sources are recovered

- **WHEN** `endpoint_recovery.probe_all_39()` runs against the 39
  canonical British Isles endpoints
- **THEN** all 39 endpoints MUST return `status_code ∈ (200, 201, 204)`
- **AND** the 11 previously-broken endpoints MUST report
  `backend_used ∈ {"firecrawl_stealth", "wayback"}`

### Requirement: endpoint_health DuckLake table

The system MUST persist a row per `endpoint_recovery.fetch()` call to
the canonical DuckLake table
`cianfhoghlaim.endpoint_health`. The Dagster L2 asset
`endpoint_health_sink` MUST fire every 6 hours and populate the
table from `endpoint_recovery.probe_all_39()`.

#### Scenario: A new endpoint becomes unhealthy

- **WHEN** one of the 39 canonical endpoints returns a non-200 status
  for 2 consecutive probes
- **THEN** the `endpoint_health_alerts` asset MUST post a Slack alert
  to `#upstream-endpoints` within the next 6-hour window

### Requirement: British Isles per-subject completeness

The system MUST ensure that every British Isles nation (Scotland /
Wales / England / Northern Ireland + the Crown Dependencies) ships
the full 6-subject per-subject depth for the BIEP pattern. The 6
required subjects are:

1. mathematics
2. chemistry
3. biology
4. physics
5. language (native-language + literature)
6. computing_science

#### Scenario: Wales ships physics + biology

- **WHEN** the upgrade change is materialised
- **THEN** `dlt/british_isles/wls/education/subjects/physics/physics.py`
  MUST exist with its corresponding L1 def
- **AND** `dlt/british_isles/wls/education/subjects/biology/biology.py`
  MUST exist with its corresponding L1 def
- **AND** the BIEP language partition for Wales is `("en", "cy")`
  (English primary + Welsh secondary)

### Requirement: 7 British Isles nations reach Ireland parity

The system MUST extend the BIEP end-to-end pipeline (DLT + BAML +
CocoIndex v1 + Dagster + MotherDuck) to all 8 British Isles nations.
Per-nation parity requires:

- ≥1 per-subject DLT source per nation for the 6 priority subjects
  (Mathematics / Chemistry / Biology / Physics / English / Computing
  Science) — with bilingual or trilingual language partitioning
  matching the nation's official languages
- 1 CocoIndex v1 App per nation (L3 layer) embedding every per-subject
  row into a shared LanceDB table
- 1 MotherDuck Dive per nation surfacing the per-nation curriculum
  coverage matrix
- 1 daily MotherDuck Flight (`british_isles_daily_sync_flight`)
  backfilling the per-nation sources

#### Scenario: Scotland ships 6 per-subject DLT sources

- **WHEN** the British Isles parity change is materialised
- **THEN** the system MUST provide 6 DLT sources under
  `dlt/british_isles/scotland/education/subjects/` (one per subject)
- **AND** each source MUST partition on
  `language ∈ ("en", "gd")` (Scots Gaelic)
- **AND** the `scotland_education` CocoIndex v1 App MUST embed every
  per-subject row into
  `cianfhoghlaim.lc.scotland.<subject>.<level>_<language>`
- **AND** the `sct_curriculum_dive` MotherDuck Dive MUST surface the
  per-subject curriculum coverage matrix

### Requirement: 7 CocoIndex v1 Apps conform to R1–R4

Every per-nation CocoIndex v1 App MUST import
`from cianfhoghlaim.cocoindex._lifespan import shared_lifespan` and
declare the canonical ContextKeys (`EMBEDDER`, `LANCE_DB`). Every
App MUST use `BAAI/bge-m3` (1024-d multilingual embedder) + the
LanceDB HNSW index.

#### Scenario: The Wales CocoIndex v1 App materialises

- **WHEN** the `wales_education` CocoIndex v1 App materialises
- **THEN** it MUST embed every Welsh per-subject row into the shared
  LanceDB table `cianfhoghlaim.lc.wales.<subject>.<level>_<language>`
- **AND** it MUST honour the R1–R4 conformance contract (the
  `cocoindex_v1_conformance` App MUST report `passed=True` for it)

### Requirement: Central portal as the single entry point to the BIEP surface

The system SHALL publish the central portal at `portal.cianfhoghlaim.ie`
as the **single entry point** to the 6-subject BIEP surface. The 30
existing per-subject routes
(`apps/.../routes/en/subjects/<subject>/{index,syllabus,exam-papers,marking-schemes,study-plan}.tsx`)
SHALL be reachable from the central portal's Leaving Cycle tab.

This requirement is the canonical link between the BIEP data
pipeline and the new central portal entry described in
`openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
R19.

#### Scenario: A user clicks Mathematics from the central portal

- **GIVEN** the user is on `portal.cianfhoghlaim.ie/en/leaving-cycle`
- **WHEN** they click the Mathematics card
- **THEN** the page navigates to `/en/subjects/mathematics/`
- **AND** the Mathematics landing page renders the 4 sub-route cards
  (syllabus / exam-papers / marking-schemes / study-plan)

### Requirement: BIEP display strings use full nation names

The system MUST use the full British Isles nation name (Scotland /
England / Wales / Northern Ireland / Isle of Man / Jersey /
Guernsey / Ireland) in every BAML class + function name, Python
class name, docstring, Dagster `metadata.country_name`, and MotherDuck
Dive description for the BIEP layer. The short identifiers
(`sct`, `wls`, `en`, `ni`, `isle_of_man`, `jersey`, `guernsey`,
`ireland`) remain in file paths, source_id strings, partition
values, and DuckLake table names.

#### Scenario: Scotland BAML class uses the full name

- **WHEN** the rename change is materialised
- **THEN** the BAML class at `baml/education/sct/education.baml`
  MUST be named `class ScotlandSubjectCurriculum`
- **AND** the function MUST be named
  `function ExtractScotlandSubjectCurriculum`

### Requirement: R1 — Phase 1.1 English lc5 filesystem wiring + duplicate cleanup

The system SHALL ingest every PDF (and JPG for the scanned geography
exam page) in `leaving_certificate/{chemistry,computer_science,english,gaeilge,geography,mathematics}/`
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
exclusively at `dlt/british_isles/ireland/education/curriculum.py`.
The legacy 972-LOC byte-identical duplicate
`dlt/british_isles/ireland/education/curriculum_source.py`
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

- **GIVEN** the 8 PDFs in `leaving_certificate/english/`
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

- **WHEN** a developer runs `ls dlt/british_isles/ireland/education/ | grep -E "curriculum_source|exam_source_update"`
- **THEN** zero matches SHALL be returned
- **AND** `curriculum.py` (972 LOC) remains the sole canonical surface

#### Scenario: The 11 importers resolve against the kept file

- **GIVEN** `curriculum.py` defines `_crawl_source` at line 57
      (verified via `grep -n "^def _crawl_source" dlt/british_isles/ireland/education/curriculum.py`)
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
      `dlt/filesystem/leaving_cert_source.py`
- **WHEN** an agent runs `grep -A 7 "^LC6_SUBJECTS" dlt/filesystem/leaving_cert_source.py`
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
      `dlt/filesystem/leaving_cert_source.py`
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
      `orchestration/defs/2_materials/lc_extraction/lc5_assets.py`
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
      `orchestration/defs/1_ingestion/curriculum/lc5/english.yaml`
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
      `orchestration/defs/1_ingestion/curriculum/lc6/`

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
`baml/education/lc_extraction/` uses the BAML v0.212+
canonical `field Type` (whitespace-separated) syntax — not the legacy
Pydantic-style `field: type` colon-separated syntax.

Specifically: the cross-stage shared marking point class in
`baml/education/_shared/strand_outcome.baml` SHALL be
named `MarkingPointStrand`; the SEC marking-scheme PDF extraction
class in `baml/education/pdfs/leaving_cert_marking_scheme.baml`
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
- **WHEN** `grep -rE '^\s+[a-z_][a-zA-Z0-9_]*:\s+(string|int|float|bool|list|map|class|enum|optional)\b' baml/education/lc_extraction/` is run
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
`notebooks/leaving_cert/`: 1 each for `chemistry.py`,
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
      `cianfhoghlaim.leaving_cert.chemistry_topics`
- **WHEN** a teacher runs
      `marimo edit notebooks/leaving_cert/chemistry.py`
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
      `cianfhoghlaim.leaving_cert.gaeilge_topics.topic_label_ga`
      preserves the fada diacritic (e.g. `Máirt`, `Gaeilge`,
      `scríbhneoir`, `Cian`, `Áireamhán`)
- **AND** the `gaeilge` notebook's "Cross-linguistic mapping" viz
      shows the EN ↔ GA topic pair side-by-side

#### Scenario: 06_en_vs_ga_comparison renders the bilingual coverage matrix

- **GIVEN** the bilingual EN + GA subject assets are loaded
- **WHEN** a teacher opens
      `notebooks/leaving_cert/06_en_vs_ga_comparison.py`
- **THEN** the notebook shows the EN ↔ GA topic coverage matrix
      for the 5 EN/GA subjects (Chemistry, Computer Science, Geography,
      Mathematics, English)
- **AND** the bilingual coverage heatmap shows the per-topic
      EN/GA gap (topics where the GA label is missing or stale)

### Requirement: R6 — Phase 7 (Daily MotherDuck lc_pdf_sync_flight)

The system SHALL schedule a daily MotherDuck Flight
`lc_pdf_sync_flight` at
`motherduck/flights/lc_pdf_sync_flight.py` that:

1. Runs `uv run cocoindex update lc_subjects` to re-ingest the 6 LC
   subjects' PDF corpus (any new PDFs landed in
   `s3://garage/cianfhoghlaim/leaving_cert/<subject>/<lang>/<year>/<file>.pdf`
   in the last 24h)
2. Runs `uv run dagster asset materialize --select '*lc*'` to
   re-materialise the 6×6+2 = 38 LC assets (6 subjects × 6 stages +
   gov.ie circulars)
3. Writes a status row to
   `md:cianfhoghlaim.lc_ops.daily_sync_status(flight_name,
   started_at, completed_at, status, log)` capturing the subprocess
   exit codes + the full log

The Flight SHALL be registered in
`motherduck/flights/config.yaml` with
`schedule: "0 4 * * *"` (daily at 04:00 UTC). The IaC orchestration
(Docker Compose stack + cron binding) lives in the separate
`bonneagar` repo at `bonneagar/stacks/motherduck/`.

*(Consolidates the 1 ADDED Requirement from
`2026-07-13-biep-v1-phases-6-7-unblock-v1` for the Phase 7 part.)*

#### Scenario: New PDF lands in Garage S3

- **GIVEN** a teacher (or upstream agent) has uploaded a new
      mathematics syllabus PDF to
      `s3://garage/cianfhoghlaim/leaving_cert/mathematics/en/2026/Q1.pdf`
- **WHEN** 24 hours elapse and the daily `lc_pdf_sync_flight`
      fires at 04:00 UTC
- **THEN** the Flight's `cocoindex update lc_subjects` step
      detects the new PDF and re-ingests it
- **AND** the `dagster asset materialize --select '*lc*'`
      step materialises the corresponding `lc5_mathematics_extract`
      asset
- **AND** the resulting typed rows appear in
      `md:cianfhoghlaim.leaving_cert.mathematics` within minutes
- **AND** a status row with `status='ok'` lands in
      `md:cianfhoghlaim.lc_ops.daily_sync_status`

#### Scenario: Daily flight failure is recorded

- **GIVEN** the `lc_pdf_sync_flight` runs at 04:00 UTC
- **WHEN** either the `cocoindex update` step OR the
      `dagster asset materialize` step exits non-zero
- **THEN** the Flight's status row in
      `md:cianfhoghlaim.lc_ops.daily_sync_status` has `status='failed'`
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
BAML files at `baml/education/marking/<subject>_marking.baml`
+ 6 per-subject grading BAML files at
`baml/education/grading/<subject>_grading.baml` + 6 L1
ingestion defs YAMLs at
`orchestration/defs/1_ingestion/marking/<subject>.yaml`
+ 6 L2 materials defs YAMLs at
`orchestration/defs/2_materials/grading/<subject>.yaml`.

*(Consolidates the 1 ADDED Requirement from
`2026-07-16-biiep-v1-lc-per-subject-marking-grading-v1`.)*

#### Scenario: 12 per-subject BAML files exist for the 6 BIEP v1 LC subjects

- **GIVEN** the BIEP v1 capspec covers the 6 priority Irish LC
      subjects
- **WHEN** the operator checks the per-subject BAML surface under
      `baml/education/marking/` +
      `baml/education/grading/`
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

