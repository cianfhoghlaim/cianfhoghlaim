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

The system SHALL ingest curriculum documents from multiple Irish and
UK sources with caching fallback.

#### Scenario: Integrates with the 4 quadrants

- **WHEN** a developer reads the `oideachais-pipeline` spec
- **THEN** the spec references the 7 oideachais-* openspec specs
  (oideachais-pipeline, oideachais-leabharlann, oideachais-baml-schemas,
  oideachais-cognify-knowledge-graph, oideachais-semantic-search,
  oideachais-marimo-dashboards, ireland-primary-jc-dlt-baml) AND
  the 3 meaisinfhoghlaim-* specs (meaisinfhoghlaim-platform,
  meaisinfhoghlaim-agent-frameworks, meaisinfhoghlaim-ocr-htr) AND
  the 1 tuatha-platform spec AND the 3 croilar-* specs
  (croilar-portfolio, croilar-data-engineering, croilar-cv-extraction)
- **AND** the 4 quadrant AGENTS.md files (oideachais/AGENTS.md,
  meaisinfhoghlaim/AGENTS.md, tuatha/AGENTS.md, croilar/AGENTS.md)
  are linked from the spec's Cross-references section

#### Scenario: References the right AGENTS.md / README / STATUS

- **GIVEN** the openspec change `openspec-consolidation-and-readme-refresh`
  is archived
- **WHEN** a developer navigates to the pipeline
- **THEN** the canonical `oideachais/AGENTS.md`,
  `oideachais/STATUS.md`, `oideachais/REFACTORING.md`, and the 4
  quadrant READMEs are linked from the spec

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

### Requirement: Dagster DuckLake resource (canonical KCG lakehouse sink)

The system SHALL use the upstream `dagster-ducklake` integration
(`DuckLakeResource` from `docs/dagster/integrations/dagster-ducklake/`)
as the canonical KCG lakehouse sink, with the resource config:

- **Postgres catalog** at `oideachais/storage/ducklake_client.py`
- **Garage S3 object store** at the `ducklake` bucket
- **`dg.EnvVar`** for all secrets (no hardcoded values)

#### Scenario: DuckLake resource config

- **GIVEN** the `dagster-ducklake` package is installed
- **WHEN** the `DuckLakeResource` is configured with
  `catalog="postgres://..."`, `storage_url="s3://ducklake/..."`
  (and `aws_access_key_id` / `aws_secret_access_key` via `dg.EnvVar`)
- **THEN** the resource SHALL be available to every Dagster asset
  that calls `context.resources.ducklake.read_sql(...)` /
  `.write_table(...)`
- **AND** `USE_DUCKLAKE=true` is the single env-var gate

### Requirement: Self-hosted Docker Dagster deploy (canonical KCG pattern)

The system SHALL use the upstream self-hosted Docker pattern
(`docs/dagster/integrations/deploy/`) as the canonical Dagster
deploy topology, with 4 services:

1. `dagster-postgres` — `PostgresRunStorage` + `PostgresScheduleStorage` +
   `PostgresEventLogStorage`
2. `dagster-user-code` — gRPC user-code container (the `definitions.py`
   module)
3. `dagster-webserver` — UI on port 3000
4. `dagster-daemon` — schedules + sensors + run coordinator

The compose file uses healthchecks, a named network, and
`/var/run/docker.sock` mount for `DockerRunLauncher`.

#### Scenario: Self-hosted stack runs

- **GIVEN** `docker compose -f infrastructure/stacks/engineering/dagster/compose.yaml up -d`
- **WHEN** all 4 services are healthy
- **THEN** the Dagster UI SHALL be reachable at `http://localhost:3000`
- **AND** the daemon SHALL poll the schedules/sensors
- **AND** user-code SHALL register via gRPC

### Requirement: DLT parallel-asset factory (DLT + Dagster integration)

The system SHALL use the upstream `dlt_github` reference
(`docs/dagster/integrations/dlt_github/`) as the template for
DLT → Dagster parallel-asset factories, with:

- A `make_resource_asset(resource_fn, endpoint_name)` factory that
  yields one `@asset` per REST endpoint
- `apply_hints` for incremental loading (`write_disposition="merge"`,
  `primary_key=[...]`)
- `multiprocess_executor` configured for N parallel resources
- A daily `@schedule` that fires the affected partitions
- `DagsterDltResource` as the resource

#### Scenario: Ireland curriculum DLT asset factory

- **GIVEN** the 4+ `oideachais/dlt_sources/ireland/curriculum/*` REST
  endpoints
- **WHEN** the SourceFactory emits the corresponding Dagster assets
- **THEN** 4+ parallel `@asset`s SHALL be registered in the
  `ireland/curriculum/` group
- **AND** each asset SHALL be independently re-materialisable
- **AND** the partition key SHALL be `language + subject` (the
  `MultiPartitionsDefinition` already in `oideachais/dagster_defs/`)

### Requirement: SQLMesh ↔ Dagster translator pattern

The system SHALL use the upstream `dagster-sqlmesh` reference
(`docs/dagster/integrations/dagster-sqlmesh/`) as the template for
`@sqlmesh_assets`, `SQLMeshResource`, and a central
`SQLMeshDagsterTranslator` shared between the resource and the
assets to prevent key drift.

#### Scenario: SQLMesh assets register

- **GIVEN** a `SQLMeshResource` configured with the project at
  `oideachais/dbt_project/` (or its SQLMesh equivalent)
- **WHEN** the `@sqlmesh_assets` decorator is applied with the
  shared translator
- **THEN** the SQLMesh models SHALL appear as Dagster assets
- **AND** the asset keys SHALL match the translator's output
  (no drift between resource and asset views)

### Requirement: KCG CocoIndex + Graphiti asset graph

The system SHALL implement the asset graph
`raw_pdf → extracted_markdown → semantic_chunks → vector_embeddings → knowledge_graph_episodes`
with `DynamicPartitionsDefinition(name="exam_papers")` per file, and
a sensor-driven `context.instance.add_dynamic_partitions(...)` flow.

The graph uses CocoIndex `SplitRecursively` for chunking and Graphiti
bi-temporal ingestion for the knowledge-graph episodes.

#### Scenario: Exam-paper partition registered

- **GIVEN** a new PDF lands in
  `stedding/ingest_queue/leaving_cert/2027/`
- **WHEN** the `leaving_cert_sensor` polls
- **THEN** `add_dynamic_partitions("exam_papers", ["2027|english_p1"])`
  SHALL register the partition
- **AND** a `RunRequest(run_key="2027|english_p1")` SHALL be emitted
  for the affected assets

### Requirement: Tripartite Data Landscape

The system SHALL model the Irish education data through
**three evidential sources** with distinct governance:

- **Pedagogical intent** — the NCCA curriculum (the "what
  should be taught")
- **Evidentiary truth** — SEC examination papers + marking
  schemes (the "what was actually assessed")
- **Temporal governance** — NCCA circulars (the "what changed
  and when")

#### Scenario: Cross-source query returns all three lenses

- **GIVEN** a Dagster asset materialises the
  `oideachais.education.ie.curriculum` table
- **WHEN** a marimo dashboard queries for the Junior Cycle
  Mathematics syllabus
- **THEN** the dashboard SHALL display the NCCA syllabus
  (pedagogical intent), the last 3 years of SEC exam papers
  (evidentiary truth), and any 2024-2025 NCCA circulars
  (temporal governance) side-by-side

### Requirement: Bilingual data strategy

The system SHALL support bilingual (English + Irish) data
through a **unified concept node** with separate
language-specific `HAS_FORM` edges. The concept node is the
canonical entity; the language-specific forms are edges
to the language-specific text.

#### Scenario: English query returns the canonical concept

- **GIVEN** a user queries "handwriting recognition for Irish"
- **WHEN** the RAG pipeline resolves the query to a
  `HandwritingRecognition` concept node
- **THEN** the result includes the English form
  ("handwriting recognition for Irish") + the Irish form
  ("aithint scribhneoireachta") + 1+ synonym layer (e.g.
  "OCR for Irish handwriting" → "OCR do scribhneoireacht
  Ghaeilge")

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
