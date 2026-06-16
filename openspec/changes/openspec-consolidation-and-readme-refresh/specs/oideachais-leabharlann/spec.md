## ADDED Requirements

The `oideachais-leabharlann` capability is consolidated from the old
`leabharlann-ingestion` and `author-archive-baml-extraction` specs.
The full Requirements + Scenarios are in the canonical spec at
`openspec/specs/oideachais-leabharlann/spec.md`.

### Requirement: 4 dlt sources

The system SHALL provide 4 dlt sources for the leabharlann corpora:
`leabharlann_books` (generic, `subject` partition), `leabharlann_zotero`
(arxiv_id detection), `leabharlann_takeout_v1` (Google Takeout v1,
auto-discovers account prefixes), and
`leabharlann_university_of_galway` (UoG artefacts, `domain`
partition).

#### Scenario: All 4 sources construct

- **WHEN** the 4 dlt source factories are imported
- **THEN** each source is a `@dlt.source`-decorated callable that
  yields 6 resources

### Requirement: 3 v1 CocoIndex Apps

The system SHALL provide 3 CocoIndex v1 Apps
(`LeabharlannBooksEmbedding`, `LeabharlannZoteroEmbedding`,
`LeabharlannTakeoutEmbedding`) that embed the leabharlann corpora
into LanceDB with BAAI/bge-large-en-v1.5 (1024-d).

#### Scenario: Apps instantiate on cocoindex==1.0.9

- **WHEN** `from oideachais.cocoindex_flows.leabharlann_embedding import LeabharlannBooksEmbedding`
- **THEN** the App class loads without errors
- **AND** the App uses `IdGenerator()` for stable IDs

### Requirement: Dagster asset group

The system SHALL register 7 Dagster assets in the
`leabharlann_ingestion` group: 3 raw ingest + 1 BAML metadata
extraction + 3 CocoIndex v1 embedding updates.

#### Scenario: 7 assets register

- **WHEN** the Dagster code-location is loaded
- **THEN** 7 assets appear in the `leabharlann_ingestion` group

### Requirement: Full-stack demo asset

The system SHALL provide a `leabharlann_full_stack_demo` Dagster
asset that exercises the entire stack on 2 sample PDFs.

#### Scenario: Full-stack demo runs

- **WHEN** the `leabharlann_full_stack_demo` asset materialises
- **THEN** 4 asset checks pass (extraction OK, BAML OK, CocoIndex OK,
  full pipeline OK)

### Requirement: Directory-watch sensor

The system SHALL provide a `leabharlann_sensors` directory-watch
sensor that polls every 60 seconds.

#### Scenario: Sensor fires on new file

- **WHEN** a new PDF lands in `leabharlann/gaeilge/`
- **THEN** a `RunRequest` is emitted for the affected asset partition
