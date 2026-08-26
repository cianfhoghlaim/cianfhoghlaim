# orchestration-vertical-pipelines Specification

## Purpose

`orchestration-vertical-pipelines` is a capability of the Cianfhoghlaim
platform that codifies the vertical-pipeline organisation of the
Dagster orchestration layer. After this spec is implemented:

- `orchestration/pipelines/<domain>/<jurisdiction>/` is the canonical
  layout for orchestration pipelines
- `PipelineFactoryComponent` is the canonical way to declare a pipeline
  from a single dlt source reference
- 8 `pipeline_kind_handlers/` classes cover the major source kinds
  (syllabus, exam_papers, personal_archive, official_docs, comics,
  crypto, pdf, media)
- The UoG tertiary pipelines (`exam_papers`, `personal_archive`,
  `official_docs`, `students_union`) are real Components, not flat
  files

This spec captures Wave 2 of the 2026-08-24 master refactor plan.

## ADDED Requirements

### Requirement: PipelineFactoryComponent

A `PipelineFactoryComponent` SHALL be available at
`orchestration.components.pipeline_factory.PipelineFactoryComponent`.

- **WHEN** a `defs.yaml` file declares `type: orchestration.components.pipeline_factory.PipelineFactoryComponent`
- **THEN** the Component SHALL load the referenced `dlt_source` (Python
  import path), introspect its `@dlt.source`/`@dlt.resource` decorators
  for `name`, `primary_key`, `write_disposition`, `columns`,
  `schema_contract`, AND construct a `dlt.pipeline(...).dataset()` to
  read the actual column types and row counts
- **AND** the Component SHALL generate a 5-stage asset graph:
  - 1 dlt asset (loads the source)
  - 1 BAML extraction asset (L2 materials)
  - 1 cocoindex flow asset (L3 model lifecycle)
  - 1 marimo dashboard asset (L4 asset generation)
  - Asset checks (NULL constraints, row counts, etc.)

#### Scenario: PipelineFactoryComponent emits assets for a dlt source

- **WHEN** `orchestration/pipelines/education/tertiary/uog/exam_papers/defs.yaml` declares:
  ```yaml
  type: orchestration.components.pipeline_factory.PipelineFactoryComponent
  attributes:
    dlt_source: dlt_sources.education.tertiary.uog.exam_papers
    pipeline_kind: exam_papers
  ```
- **THEN** `dg list defs` SHALL include the new exam_papers assets under
  `pipelines/education/tertiary/uog/exam_papers/`

### Requirement: pipeline_kind_handlers namespace

Eight handler classes SHALL be available at
`orchestration.components.pipeline_kind_handlers.<kind>_handler`:

| Handler | File | Purpose |
|:--|:--|:--|
| `SyllabusHandler` | `syllabus_handler.py` | NCCA / SEC / CCEA / SQA / WJEC syllabuses (chemistry_syllabus → experiments → artifacts) |
| `ExamPapersHandler` | `exam_papers_handler.py` | UoG exam papers + Leaving Cert + GCSE (VLM extraction) |
| `PersonalArchiveHandler` | `personal_archive_handler.py` | Personal notes + assignments + transcripts |
| `OfficialDocsHandler` | `official_docs_handler.py` | University module pages + student union |
| `ComicsHandler` | `comics_handler.py` | Comics (VLM via cognee) |
| `CryptoHandler` | `crypto_handler.py` | Chain indexer for crypteolas sources |
| `PdfHandler` | `pdf_handler.py` | OCR + BAML extraction |
| `MediaHandler` | `media_handler.py` | Codec probe + thumbnail + embeddings |

Each handler SHALL implement a `process_pipeline(defs, ctx) -> list[dg.AssetDefinition]`
method that the `PipelineFactoryComponent` calls to specialise the
generated asset graph.

#### Scenario: ExamPapersHandler emits VLM-extraction assets

- **WHEN** `PipelineFactoryComponent.process_pipeline(dlt_source=exam_papers_source, kind='exam_papers')` runs
- **THEN** the emitted assets SHALL include one @asset that runs VLM
  extraction over the exam paper PDFs

### Requirement: Vertical pipeline layout

The `orchestration/pipelines/` directory SHALL mirror the Wave 1
`dlt_sources/` domain-first layout:

```
orchestration/pipelines/
├── law/<jurisdiction>/<geography>/
├── medicine/<jurisdiction>/<geography>/
├── education/<jurisdiction>/<geography>/
│   └── tertiary/<institution>/<subdir>/
├── lexicographic/
├── cultural_heritage/
├── local_archive/
├── media_text/
├── media_comics/
├── media_games/
├── media_personal/
├── crypteolas_chain/
├── crypteolas_docs/
├── crypteolas_defi/
├── raw_files/
├── cv/
├── artwork/
└── labels/
```

#### Scenario: UoG tertiary pipelines live under education/tertiary/

- **WHEN** `ls orchestration/pipelines/education/tertiary/uog/` runs
- **THEN** the result SHALL include `exam_papers/`, `personal_archive/`,
  `official_docs/`, `students_union/`
- **AND** each SHALL have a `defs.yaml` that declares the
  `PipelineFactoryComponent` with the matching `pipeline_kind`

### Requirement: Backwards compatibility
The system SHALL continue to work via the existing `dg.load_defs()` mechanism..
Wave 2 ADDS the vertical `orchestration/pipelines/` namespace without
removing the horizontal one.

#### Scenario: Both old and new layouts load

- **WHEN** `dg list defs` runs
- **THEN** both `1_ingestion/*` (horizontal) and `pipelines/education/*`
  (vertical) assets SHALL appear

### Requirement: UoG flat-file conversion

The 8 post-2026-08-23 UoG flat files SHALL be converted into proper
Components:

| Old (flat file) | New (vertical pipeline) |
|:--|:--|
| `orchestration/defs/uog_exam.py` | `orchestration/pipelines/education/tertiary/uog/exam_papers/defs.yaml` |
| `orchestration/defs/uog_personal_archive.py` + `uog_personal_archive_figures.py` | `orchestration/pipelines/education/tertiary/uog/personal_archive/defs.yaml` |
| `orchestration/defs/uog_official_docs.py` | `orchestration/pipelines/education/tertiary/uog/official_docs/defs.yaml` |
| `orchestration/defs/uog_students_union.py` | `orchestration/pipelines/education/tertiary/uog/students_union/defs.yaml` |
| `orchestration/defs/nui_federation.py` | `orchestration/pipelines/education/tertiary/nui_federation/defs.yaml` |
| `orchestration/defs/british_isles_tertiary.py` | `orchestration/pipelines/education/tertiary/british_isles/defs.yaml` |
| `orchestration/defs/media_intel.py` | `orchestration/pipelines/media_intel/defs.yaml` |

#### Scenario: All UoG flat files are gone

- **WHEN** `ls orchestration/defs/uog_*.py` runs
- **THEN** the result SHALL be empty (all migrated to vertical pipelines)

### Requirement: definitions.py auto-load

`orchestration/definitions.py` SHALL be updated to load both the
horizontal `defs/` tree AND the vertical `pipelines/` tree.

#### Scenario: definitions.py walks both trees

- **WHEN** `dg list defs` runs
- **THEN** assets from `orchestration/defs/*` AND
  `orchestration/pipelines/*` SHALL appear

### Requirement: Firecrawl-driven docs lookup

`PipelineFactoryComponent.build_defs()` SHALL include a firecrawl mcp
call to fetch the latest Dagster 1.13+ Components docs at scaffold
time. The fetched docs are used to validate that the generated YAML
schema matches the current `dg scaffold defs` patterns.

#### Scenario: Firecrawl docs are fetched on first scaffold

- **WHEN** a new pipeline is scaffolded for the first time
- **THEN** the firecrawl mcp SHALL fetch `https://docs.dagster.io/guides/build/components`
  + `https://docs.dagster.io/integrations/libraries/dlt`
- **AND** the fetched content SHALL be cached in
  `orchestration/components/pipeline_factory/_dg_docs_cache.json`
