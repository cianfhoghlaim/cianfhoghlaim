# Oideachais Leabharlann — ADDED Requirements from `ingest-culture-heritage`

This delta adds 2 new requirements to the existing `oideachais-leabharlann` spec. It does NOT modify any existing requirement.

## ADDED Requirements

### Requirement: Culture heritage dataset

The leabharlann full-stack infrastructure SHALL expose a sixth Cognee dataset named `culture_heritage` with cross-dataset edge rules enabled to the existing `oideachais` and `leabharlann` datasets.

The dataset name is registered in `oideachais/cognee_integration/culture_cognify.py` as a module-level constant `DATASET_CULTURE_HERITAGE = "culture_heritage"`, mirroring the existing `DATASET_BOOKS = "leabharlann_books"`, `DATASET_ZOTERO = "leabharlann_zotero"`, `DATASET_TAKEOUT = "leabharlann_takeout"` constants.

#### Scenario: When culture_heritage claims are cognified

- **WHEN** the `culture_heritage_cognify` Dagster asset runs
- **THEN** quintuple entities (person, family-relationship, place, date-range, claim) are persisted to the `culture_heritage` dataset
- **AND** cross-dataset edges linking a `culture_heritage:person:<name>` node to an existing `oideachais:place:galway` node are emitted to the unified graph

#### Scenario: When the culture_heritage LanceDB table is rebuilt

- **WHEN** a PDF in `leabharlann/gemini_deep_research/culture/` changes SHA-256
- **THEN** only the delta chunks are re-embedded; untouched chunks keep their HNSW index

#### Scenario: When a culture_heritage claim has confidence below 0.6

- **WHEN** the BAML extraction emits a `CultureHeritageClaim` with `confidence < 0.6`
- **THEN** the claim is routed to the `low_confidence_review` asset check (severity=WARN)
- **AND** the claim is excluded from the production `culture_heritage_chunks` LanceDB table

### Requirement: Culture heritage sources under domain `culture`

`oideachais/sources.yaml` SHALL register exactly 6 new entries under `domain: culture, nation: ie`, one per PDF in `leabharlann/gemini_deep_research/culture/` that is a personal-heritage document.

#### Scenario: When sources.yaml is parsed

- **WHEN** `SourceFactory` loads `oideachais/sources.yaml`
- **THEN** exactly 6 entries are present under `domain: culture, nation: ie`
- **AND** each entry's `id` matches the pattern `ie.culture.<slug>` where `<slug>` is the kebab-case PDF basename with `.pdf` stripped
- **AND** each entry's `kind` is `filesystem_pdf`
- **AND** each entry's `schema` references the BAML function `ExtractCultureClaims`

#### Scenario: When a culture source entry has a key collision

- **WHEN** two entries in `oideachais/sources.yaml` share the same `id`
- **THEN** `SourceFactory` MUST raise `DuplicateSourceError` at load time
- **AND** the cross-domain-registry spec SHALL report both entries in its validation output