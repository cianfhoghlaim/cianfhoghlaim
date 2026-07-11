## ADDED Requirements

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
  `cianfhoghlaim/dlt/british_isles/ireland/education/ncca_<subject>.py`
- 6 per-subject qpack BAMLs at
  `cianfhoghlaim/baml/education/subjects/qpack_<subject>.baml` (EXISTING)
- 1 unified BAML extractor at
  `cianfhoghlaim/baml/education/unified_extraction.baml`
- 1 named destinations factory at
  `cianfhoghlaim/dlt/common/named_destinations.py`
- 6 per-subject L1 defs YAMLs at
  `cianfhoghlaim/orchestration/defs/1_ingestion/curriculum/lc6/<subject>.yaml`

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
  - `cianfhoghlaim/dlt/british_isles/ireland/education/ncca_mathematics.py`
  - `cianfhoghlaim/dlt/british_isles/ireland/education/ncca_chemistry.py`
  - `cianfhoghlaim/dlt/british_isles/ireland/education/ncca_geography.py`
  - `cianfhoghlaim/dlt/british_isles/ireland/education/ncca_gaeilge.py`
  - `cianfhoghlaim/dlt/british_isles/ireland/education/ncca_english.py`
  - `cianfhoghlaim/dlt/british_isles/ireland/education/ncca_computer_science.py`
  - `cianfhoghlaim/baml/education/subjects/qpack_mathematics.baml`
  - `cianfhoghlaim/baml/education/subjects/qpack_chemistry.baml`
  - `cianfhoghlaim/baml/education/subjects/qpack_geography.baml`
  - `cianfhoghlaim/baml/education/subjects/qpack_gaeilge.baml`
  - `cianfhoghlaim/baml/education/subjects/qpack_english.baml`
  - `cianfhoghlaim/baml/education/subjects/qpack_computer_science.baml`
  - `cianfhoghlaim/baml/education/unified_extraction.baml`
- **AND** 6 per-subject L1 defs YAMLs SHALL exist at
  `cianfhoghlaim/orchestration/defs/1_ingestion/curriculum/lc6/`
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