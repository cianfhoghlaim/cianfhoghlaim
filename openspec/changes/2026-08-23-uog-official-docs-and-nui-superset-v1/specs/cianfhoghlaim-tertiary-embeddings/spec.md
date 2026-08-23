# cianfhoghlaim-tertiary-embeddings Specification

## Purpose

Add 3 new CocoIndex v1 Apps to take the v1 App count from 14 to 17:
- `UoGOfficialDocsApp` (BGE-M3 1024-d on
  `title + body + source_kind` of every UoG official document).
- `NuiFederationApp` (BGE-M3 on every NUI archive row).
- `UoGStudentsUnionApp` (BGE-M3 on every SU policy).

Plus a `bitertiary_universities_app_factory(config)` that emits
**one** v1 App per `BITertiaryDeepExtractionConfig`. Off by
default — the block must be added to `pyproject.toml`.

## Requirements

### Requirement: 3 new v1 Apps (one per DLT source)

The system SHALL provide the 3 CocoIndex Apps at
`cocoindex_flows/british_isles/ireland/education/university/{uog_official_docs,nui_federation,uog_students_union}_embedding.py`.

Each App SHALL follow the canonical v1 pattern from
`openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md`:
- `from .._shared._lifespan import shared_lifespan, EMBEDDER,
  LANCE_DB`
- `@coco.fn(memo=True)` for the processor
- `@coco.fn` for the entry point that mounts the LanceDB target
- `coco.App(coco.AppConfig(name=...))` at module scope
- BGE-M3 1024-d embeddings

#### Scenario: `UoGOfficialDocsApp` materialises

- **GIVEN** the DuckLake `uog_official_documents` table contains
  ≥ 50 rows
- **WHEN** `cocoindex update UoGOfficialDocsApp` runs
- **THEN** the App emits ≥ 50 LanceDB rows into the
  `uog_official_documents` table (BGE-M3 1024-d)
- **AND** the manifest reports `documents_embedded=50, hnsw_built=true`

### Requirement: `bitertiary_universities_app_factory`

The system SHALL provide the factory at
`cocoindex_flows/british_isles/university/app_factory.py`. The
factory generates **one** CocoIndex v1 App per
`BITertiaryDeepExtractionConfig` so a 6-resource DLT scrape can
become a 6-table LanceDB search surface.

#### Scenario: 2 universities × 1 App each

- **GIVEN** `[tool.dlt.sources.bitertiary_universities.entries]`
  has 2 entries (QUB + Ulster)
- **WHEN** `bitertiary_universities_app_factory().run_all()`
  runs
- **THEN** 2 v1 Apps materialise (one per university)
- **AND** each App's LanceDB table has the expected schema
