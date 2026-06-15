# Oideachais Pipeline Capability

## Purpose

`oideachais-pipeline` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

## Background
Celtic education curriculum pipeline processing Irish, UK, and pan-Celtic educational content with AI-enhanced learning experiences. Orchestrated via Dagster on a DuckLake destination backed by Garage S3.

| Feature | Description |
|---------|-------------|
| DLT Ingestion | NCCA, SEC, UK curriculum sources via Firecrawl + local cache |
| DuckLake Destination | Parquet on Garage S3 with Postgres catalog |
| Vector Embeddings | LanceDB via Lance Namespace sidecar (Iceberg catalog) |
| Knowledge Graph | Prerequisite mapping in Memgraph (staged for implementation) |
| Multi-Agent AI | Google ADK and Agno education agents via LiteLLM routing |
## Requirements
### Requirement: Curriculum Ingestion

The system SHALL ingest curriculum documents from multiple Irish and UK sources with caching fallback.

#### Scenario: Irish Curriculum
- **GIVEN** NCCA curriculum documents at `curriculumonline.ie`
- **WHEN** DLT pipeline runs with `USE_LOCAL_SCRAPES=false`
- **THEN** documents are scraped via Firecrawl and loaded to DuckLake

#### Scenario: Local Cache Fallback
- **GIVEN** `USE_LOCAL_SCRAPES=true` environment variable
- **WHEN** DLT pipeline runs
- **THEN** documents are read from `/stedding/ingest_queue/` cache instead of live scraping

#### Scenario: Three-Source Unified Crawling
- **GIVEN** curriculumonline.ie, ncca.ie, and examinations.ie sources
- **WHEN** the unified curriculum DLT source runs
- **THEN** content is deduplicated via content hashing with source provenance tracking

#### Scenario: UK Curriculum
- **GIVEN** England, Scotland, Wales, and Northern Ireland curriculum sources
- **WHEN** respective nation-specific DLT pipelines run
- **THEN** data is normalized and stored with per-nation partitions

#### Scenario: Exam Papers
- **GIVEN** SEC exam papers and marking schemes
- **WHEN** extraction pipeline runs with BAML schemas
- **THEN** questions and marking scheme answers are aligned

#### Scenario: Curriculum Index Registry
- **GIVEN** curriculum sources defined in `curriculum_index.json` registry
- **WHEN** pipeline initializes
- **THEN** URLs and subjects are resolved from the registry rather than hardcoded

### Requirement: Partition Strategy (v2)

The system SHALL use a 4-cycle partition scheme with runtime subject selection.

#### Scenario: Cycle-Based Partitions
- **GIVEN** partition definitions for early_childhood, primary, junior_cycle, senior_cycle
- **WHEN** Dagster job is triggered
- **THEN** each cycle partition materializes independently

#### Scenario: Runtime Subject Config
- **GIVEN** `CURRICULUM_CONFIG_SCHEMA` with subject selection
- **WHEN** a partition is materialized with subject override
- **THEN** only specified subjects are processed instead of all 33+

### Requirement: Vector Embeddings

The system SHALL generate embeddings for semantic search via LanceDB.

#### Scenario: Document Embeddings
- **GIVEN** curriculum documents extracted via Docling OCR
- **WHEN** embedding assets materialize
- **THEN** embeddings are generated using `paraphrase-multilingual-MiniLM-L12-v2` (384 dims) and stored in LanceDB with HNSW index

#### Scenario: Bilingual Embeddings
- **GIVEN** English and Irish content
- **WHEN** embedding flow runs
- **THEN** both languages are indexed with language tags in the same vector space

#### Scenario: Batch Constraint Enforcement
- **GIVEN** fewer than 100 texts to embed
- **WHEN** embedding function is called
- **THEN** texts are batched to meet the 100-minimum constraint before API call

### Requirement: Knowledge Graph

The system SHALL maintain curriculum knowledge graph for prerequisites.

#### Scenario: Prerequisite Mapping
- **GIVEN** curriculum topics extracted from NCCA documents
- **WHEN** graph enrichment assets run
- **THEN** prerequisite relationships are captured in Memgraph using Cypher schemas

#### Scenario: Topic Hierarchy
- **GIVEN** subject areas with strand and level metadata
- **WHEN** hierarchy is built
- **THEN** topics are organized by strand and education level

### Requirement: Agent Integration

The system SHALL support Google ADK and Agno education agents with LiteLLM routing.

#### Scenario: Curriculum Query
- **GIVEN** student query about a curriculum topic
- **WHEN** agent processes via LiteLLM router
- **THEN** curriculum-aware response is generated using LanceDB semantic search

#### Scenario: Assessment Help
- **GIVEN** exam question extracted via BAML
- **WHEN** agent analyzes the question
- **THEN** marking scheme guidance and prerequisite mapping are provided

#### Scenario: Agent Routing
- **GIVEN** a domain-specific education question
- **WHEN** Root Agent receives the request
- **THEN** the appropriate Domain Agent (Curriculum, Translation, Corpus, Geospatial, Statistics, Research) is invoked

### Requirement: Asset Key Convention (renamed)

The system SHALL identify every asset by a domain‑first key tuple
`["{nation_code}", "{domain}", "{entity_slug}"]` where:

- `nation_code` is one of `ie | ni | en | sct | wls | iom | jey | ggy`.
- `domain` is one of `education | medicine | law | statistics | site_analysis`.
- `entity_slug` is the YAML `id` suffix (e.g. `ccea`, `irish_statute_book`).

The system SHALL maintain a backwards‑compatibility alias table in
`oideachais/dagster_defs/definitions.py` mapping legacy asset keys to the
new ones for one (1) release cycle, then the alias table SHALL be removed in
a follow‑on `drop-asset-key-aliases` change.

#### Scenario: Domain‑first key for an Irish education asset
- **GIVEN** the existing `oideachais/dagster_defs/assets/ireland/curriculum_dlt_assets.py` `create_cycle_asset("senior_cycle")` whose legacy key is `["ireland", "curriculum", "senior_cycle"]`
- **WHEN** the asset is registered with the SourceFactory
- **THEN** the new key is `["ie", "education", "curriculum", "senior_cycle"]`
- **AND** the legacy key is resolvable via the backwards‑compat alias

#### Scenario: Domain‑first key for a Northern Ireland CCEA asset
- **GIVEN** the existing `oideachais/dlt_sources/uk/northern_ireland/ccea_curriculum.py::ni_curriculum_source`
- **WHEN** the SourceFactory emits the corresponding Dagster asset
- **THEN** the new key is `["ni", "education", "ccea", "pages"]`
- **AND** the legacy key `["uk", "education", "northern_ireland", "ccea_pages"]` is resolvable

### Requirement: Single `oideachais` DB with per‑domain schemas

The system SHALL register a single `md:oideachais` (MotherDuck) database and a
single `ducklake:oideachais` (Garage S3) catalog, with schemas of the form
`oideachais.{domain}.{nation}`. DLT `dataset_name` MAY remain per‑source for
fine‑grained state, but the underlying DuckLake schema SHALL be the
dotted‑triple.

#### Scenario: One attach, one query
- **GIVEN** the API reader at `oideachais/api/ducklake_reader.py`
- **WHEN** the SPA requests a Leaving Cert subject
- **THEN** the reader does a single `ATTACH 'oideachais'` (or `ducklake:oideachais`)
- **AND** reads `oideachais.education.ie.leaving_cert WHERE subject = ?`
- **AND** no per‑subject glob() / per‑subject S3 prefix is used

#### Scenario: New domain schema is auto‑created
- **GIVEN** a new DLT run for `oideachais/dlt_sources/domains/medicine/ie/hse.py`
- **WHEN** the pipeline runs
- **THEN** DuckLake creates the schema `oideachais.medicine.ie` on first write
- **AND** the table is discoverable by `marimo` against `md:oideachais`

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| DLT Sources | `oideachais/data_platform/dlt_sources/` | Ireland, UK, Celtic, geospatial ingestion |
| Dagster Definitions | `oideachais/data_platform/dagster_defs/` | Asset orchestration, jobs, schedules, sensors |
| DLT Utils | `oideachais/data_platform/dlt_utils/` | DuckLake destination config, caching |
| DuckLake Client | `oideachais/storage/ducklake_client.py` | Postgres catalog + Garage S3 connection |
| LanceDB Cloud | `oideachais/storage/lancedb_cloud.py` | Local/Cloud/Iceberg vector store modes |
| Embedding Service | `oideachais/embeddings/service.py` | Multi-provider batch embedding |
| BAML Schemas | `baml_src/` | Type-safe LLM extraction schemas |
| OCR Models | `meaisínfhoghlaim/ocr/` | Multi-model comparison (Docling, PaddleOCR, ColPali) |
| ML Training | `oideachais/training/` | LLM, HTR, TTS training as Dagster assets |
| Agents | `meaisínfhoghlaim/agents/` | Root Agent + 6 domain agents |

## Storage Architecture

```
Firecrawl/LocalScrape → DLT Pipeline → DuckLake (Parquet + Postgres catalog)
                                            │
                                    Garage S3 (ducklake bucket)
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                      DuckDB Query    Lance Namespace   MotherDuck
                      (direct)        Sidecar (8182)   (optional)
                                            │
                                      ├─ Lakekeeper Iceberg Catalog (8181)
                                      │   └─ Postgres metadata (5433)
                                      └─ LanceDB tables on S3 (lance bucket)
                                            │
                                      Vector Search API
```

## Constraints

- **DuckDB:** SINGLE_THREADED_ONLY (concurrent access causes corruption)
- **LanceDB:** MVCC-safe with SerialDatabaseExecutor and circuit breaker (3-failure threshold)
- **Embeddings:** Batch minimum 100 texts per API call; model: `paraphrase-multilingual-MiniLM-L12-v2`
- **HNSW:** Drop indexes before bulk inserts >50 rows
- **Irish Language:** Use UCCIX or GaBERT models
- **Zero Absolute Namespaces:** NEVER import `oideachais.data_platform...` from within the data platform (use relative imports)
- **Ingestion Cache:** Test with `USE_LOCAL_SCRAPES=true` before live web scraping to avoid API rate limits

## Implementation References

| Component | Path |
|-----------|------|
| Dagster Definitions | `oideachais/data_platform/dagster_defs/definitions.py` |
| DLT Utils | `oideachais/data_platform/dlt_utils/` |
| Storage Config | `oideachais/storage/` |
| Pipeline Ops Guide | `oideachais/PIPELINE_OPERATIONS.md` |
| PyProject | `oideachais/pyproject.toml` |

## Related Specs

- [curriculum-ingestion](../curriculum-ingestion/spec.md) — Document processing
- [bilingual-content](../bilingual-content/spec.md) — English/Irish management
- [knowledge-graph](../knowledge-graph/spec.md) — Prerequisite mapping
- [semantic-search](../semantic-search/spec.md) — Vector search
- [assessment-extraction](../assessment-extraction/spec.md) — Exam papers
- [data-pipeline](../data-pipeline/spec.md) — Pipeline patterns
