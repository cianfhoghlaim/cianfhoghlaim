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
- **AND** the 4 quadrant AGENTS.md files (sruth/oideachais/AGENTS.md,
  sruth/meaisinfhoghlaim/AGENTS.md, sruth/tuatha/AGENTS.md, sruth/croilar/AGENTS.md)
  are linked from the spec's Cross-references section

#### Scenario: References the right AGENTS.md / README / STATUS

- **GIVEN** the openspec change `openspec-consolidation-and-readme-refresh`
  is archived
- **WHEN** a developer navigates to the pipeline
- **THEN** the canonical `sruth/oideachais/AGENTS.md`,
  `sruth/oideachais/STATUS.md`, `sruth/oideachais/REFACTORING.md`, and the 4
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
`sruth/oideachais/dagster_defs/definitions.py` mapping legacy asset keys to the
new ones for one (1) release cycle, then the alias table SHALL be removed in
a follow‑on `drop-asset-key-aliases` change.

#### Scenario: Domain‑first key for an Irish education asset
- **GIVEN** the existing `sruth/oideachais/dagster_defs/assets/ireland/curriculum_dlt_assets.py` `create_cycle_asset("senior_cycle")` whose legacy key is `["ireland", "curriculum", "senior_cycle"]`
- **WHEN** the asset is registered with the SourceFactory
- **THEN** the new key is `["ie", "education", "curriculum", "senior_cycle"]`
- **AND** the legacy key is resolvable via the backwards‑compat alias

#### Scenario: Domain‑first key for a Northern Ireland CCEA asset
- **GIVEN** the existing `sruth/oideachais/dlt_sources/uk/northern_ireland/ccea_curriculum.py::ni_curriculum_source`
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
- **GIVEN** the API reader at `sruth/oideachais/api/ducklake_reader.py`
- **WHEN** the SPA requests a Leaving Cert subject
- **THEN** the reader does a single `ATTACH 'oideachais'` (or `ducklake:oideachais`)
- **AND** reads `oideachais.education.ie.leaving_cert WHERE subject = ?`
- **AND** no per‑subject glob() / per‑subject S3 prefix is used

#### Scenario: New domain schema is auto‑created
- **GIVEN** a new DLT run for `sruth/oideachais/dlt_sources/domains/medicine/ie/hse.py`
- **WHEN** the pipeline runs
- **THEN** DuckLake creates the schema `oideachais.medicine.ie` on first write
- **AND** the table is discoverable by `marimo` against `md:oideachais`

### Requirement: Dagster DuckLake resource (canonical KCG lakehouse sink)

The system SHALL use the upstream `dagster-ducklake` integration
(`DuckLakeResource` from `docs/dagster/integrations/dagster-ducklake/`)
as the canonical KCG lakehouse sink, with the resource config:

- **Postgres catalog** at `sruth/oideachais/core/storage/clients/ducklake.py`
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

- **GIVEN** `docker compose -f infrastructure/stacks/dagster/compose.yaml up -d`
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

- **GIVEN** the 4+ `sruth/oideachais/dlt_sources/ireland/curriculum/*` REST
  endpoints
- **WHEN** the SourceFactory emits the corresponding Dagster assets
- **THEN** 4+ parallel `@asset`s SHALL be registered in the
  `ireland/curriculum/` group
- **AND** each asset SHALL be independently re-materialisable
- **AND** the partition key SHALL be `language + subject` (the
  `MultiPartitionsDefinition` already in `sruth/oideachais/dagster_defs/`)

### Requirement: SQLMesh ↔ Dagster translator pattern

The system SHALL use the upstream `dagster-sqlmesh` reference
(`docs/dagster/integrations/dagster-sqlmesh/`) as the template for
`@sqlmesh_assets`, `SQLMeshResource`, and a central
`SQLMeshDagsterTranslator` shared between the resource and the
assets to prevent key drift.

#### Scenario: SQLMesh assets register

- **GIVEN** a `SQLMeshResource` configured with the project at
  `sruth/oideachais/dbt_project/` (or its SQLMesh equivalent)
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

### Requirement: V1 codebase indexer (codebase_chunks + codebase_code_graph)

The system SHALL run a v1-native CocoIndex App for codebase indexing,
producing both an embedded chunk table and a code-graph table. The
App uses:

- 29+ language detection (port from `codeolas/chunking/languages.py`
  to `sruth/oideachais/cocoindex_flows/chunking/languages.py`)
- `localfs.walk_dir(repo_root, live=True, refresh_interval=60s)` for
  the source
- `RecursiveSplitter` with `detect_code_language` for chunking
- `SentenceTransformerEmbedder("BAAI/bge-m3")` for embedding
- `lancedb.mount_table_target(...)` for the chunk + graph outputs

The 3 Dagster assets in `sruth/oideachais/dagster_defs/assets/codebase_assets.py`
(group_name="codebase"):

1. `codebase_chunks` — chunked + embedded source files
   (`codebase_chunks` LanceDB table)
2. `codebase_code_graph` — AST-extracted code graph (7 node types +
   7 edge types in 2 LanceDB tables `codebase_graph` +
   `codebase_graph_edges`)
3. `codebase_architecture_docs` — `.arch.md` generation
   (deferred to a later round)

The 7 node types: `FILE`, `FUNCTION`, `CLASS`, `METHOD`, `MODULE`,
`INTERFACE`, `VARIABLE`. The 7 edge types: `CONTAINS`, `IMPORTS`,
`CALLS`, `EXTENDS`, `IMPLEMENTS`, `USES`, `DEFINES`. 11 languages
have Tree-sitter AST node type mappings: Python, TypeScript,
JavaScript, TSX, JSX, Rust, Go, Java, Kotlin, Ruby, Swift.

#### Scenario: A developer queries the codebase semantically

- **GIVEN** the `codebase_chunks` Dagster asset has materialised
- **WHEN** a developer runs `bun run ccc:v1:search "SpacetimeDB
  table"`
- **THEN** the v1 App runs the BGE-M3 embedding over the query
  string, returns the top-10 chunks from the `codebase_chunks`
  LanceDB table (filtered by `language = "rust"` if requested),
  and the chunks' file paths + line numbers are returned

#### Scenario: A developer queries the code graph (Cypher-like)

- **GIVEN** the `codebase_code_graph` Dagster asset has materialised
- **WHEN** a developer runs `search_code_graph(file_path="sruth/oideachais/dagster_defs/")`
- **THEN** the v1 App reads the `codebase_graph` LanceDB table and
  returns the 10 most relevant CodeNode dicts (file_path matches the
  glob, with optional `node_type` filter)

#### Scenario: A new language is added to the language table

- **GIVEN** a developer adds a new language (e.g. `dart` with `.dart`
  extension) to `sruth/oideachais/cocoindex_flows/chunking/languages.py`
- **WHEN** the `codebase_chunks` Dagster asset re-materialises
- **THEN** `.dart` files are now chunked using the recursive splitter
  with `language="dart"`
- **AND** the `languages` metadata includes `dart`

### Requirement: V1 API endpoint indexer (api_endpoints asset)

The system SHALL run a v1-native CocoIndex App for HTTP route indexing,
producing one row per route handler in the `api_endpoints` LanceDB
table. The App uses:

- Regex catalogue covering 4 frameworks: FastAPI (`@app.get`, `@router.post`),
  Hono (`app.get`, `hono.post`), TanStack Start (`createFileRoute`,
  `createServerFileRoute`), and Convex HTTP actions (`httpAction`).
- 1 `ApiEndpoint` dataclass with BGE-M3 embedding on the `summary` field
  (1024 dims).
- `asyncio.to_thread` to run the CPU-bound regex scan (does not block the
  event loop).
- 100-row upsert batches to respect the HNSW-DROP-THRESHOLD rule.
- `localfs.walk_dir`-style recursive walk with the codebase_indexing.py
  excludes (`.venv/`, `node_modules/`, `__pycache__/`, `target/`,
  `dist/`, `build/`, `.turbo/`, `.cocoindex_code/`, `stedding/`,
  `.git/`, `docs/cocoindex/`).

The Dagster asset `api_endpoints` (group `infrastructure`) lives in
`sruth/oideachais/dagster_defs/assets/infrastructure_assets.py` and kicks the
v1 App via `cocoindex update oideachais.cocoindex_flows.api_indexing:api_app`.

#### Scenario: A developer searches the HTTP surface for an agent-memory route

- **GIVEN** the `api_endpoints` Dagster asset has materialised
- **WHEN** a developer runs `await search_api_endpoints("agent memory add")`
- **THEN** the v1 App returns the top-20 rows from the `api_endpoints`
  LanceDB table, ranked by BGE-M3 cosine similarity to the query,
  with `score = 1.0 - _distance`

#### Scenario: A developer filters by framework

- **GIVEN** the `api_endpoints` Dagster asset has materialised
- **WHEN** a developer runs `await search_api_endpoints("query", framework="hono")`
- **THEN** the v1 App returns only Hono routes (filtered by `framework = 'hono'`)

### Requirement: V1 filesystem layout indexer (filesystem_layout asset)

The system SHALL run a v1-native CocoIndex App for filesystem layout
indexing, producing one row per directory (depth 1-4) in the
`filesystem_layout` LanceDB table. The App uses:

- `os.walk` with excludes matching the codebase_indexing.py set.
- 1 `FsLayoutRow` dataclass with fields: `dir_path`, `file_count`,
  `total_bytes`, `file_types` (JSON-encoded `Counter`), `top_files`
  (JSON-encoded list of `[name, size]`), `largest_descendant`,
  `depth`, `summary`, and a BGE-M3 embedding on `summary` (1024 dims).
- `MAX_DEPTH = 4` to keep the row count bounded (~500 dirs in this
  monorepo at depth 4).
- 100-row upsert batches.

The Dagster asset `filesystem_layout` (group `infrastructure`) lives
in `sruth/oideachais/dagster_defs/assets/infrastructure_assets.py` and kicks
the v1 App via `cocoindex update oideachais.cocoindex_flows.filesystem_indexing:fs_app`.

#### Scenario: A developer searches for a directory by description

- **GIVEN** the `filesystem_layout` Dagster asset has materialised
- **WHEN** a developer runs `await search_filesystem("dagster assets", min_depth=2)`
- **THEN** the v1 App returns the top-10 directories semantically related
  to "dagster assets", filtered to `depth >= 2`, ranked by BGE-M3 cosine similarity

#### Scenario: A developer inspects the largest file in a subtree

- **GIVEN** the `filesystem_layout` Dagster asset has materialised
- **WHEN** a developer reads the `largest_descendant` column for the
  `sruth/oideachais/dagster_defs/` row
- **THEN** the cell value is the relative path of the largest file in
  the subtree (e.g. `sruth/oideachais/dagster_defs/assets/codebase_assets.py`)

### Requirement: V1 storage backend indexer (storage_backends asset)

The system SHALL run a v1-native CocoIndex App for storage backend
indexing, producing one row per backend instance in the
`storage_backends` LanceDB table. The App uses:

- 9 storage kinds: `lancedb`, `duckdb`, `ducklake`, `postgres`,
  `garage`, `r2`, `d1`, `kv`, `iceberg`.
- Regex catalogue for source-file references (lancedb, duckdb,
  ducklake, postgres, garage, s3, r2).
- Wrangler-manifest scanner (both `wrangler.jsonc` and `wrangler.toml`)
  for D1 / KV / R2 bindings.
- 1 `StorageBackend` dataclass with BGE-M3 embedding on `summary`.
- 100-row upsert batches.

The Dagster asset `storage_backends` (group `infrastructure`) lives in
`sruth/oideachais/dagster_defs/assets/infrastructure_assets.py` and kicks the
v1 App via `cocoindex update oideachais.cocoindex_flows.storage_indexing:storage_app`.

#### Scenario: A developer finds where the Irish curriculum data is stored

- **GIVEN** the `storage_backends` Dagster asset has materialised
- **WHEN** a developer runs `await search_storage("Irish curriculum", kind="ducklake")`
- **THEN** the v1 App returns the top-20 DuckLake rows semantically
  related to "Irish curriculum", ranked by BGE-M3 cosine similarity

#### Scenario: A developer lists all D1 bindings

- **GIVEN** the `storage_backends` Dagster asset has materialised
- **WHEN** a developer runs `await search_storage("", kind="d1", limit=100)`
- **THEN** the v1 App returns up to 100 rows where `kind = 'd1'`,
  each carrying `name` (the binding name) and `config_ref = '[[d1_databases]]'`

### Requirement: V1 config file indexer (config_files asset)

The system SHALL run a v1-native CocoIndex App for config file indexing,
producing one row per config file in the `config_files` LanceDB table.
The App uses:

- 12 config kinds: `docker-compose`, `mise`, `package`, `pyproject`,
  `turbo`, `wrangler`, `env`, `k8s`, `pulumi`, `dg`, `github`,
  `justfile`.
- Filename-based classification (first-match wins) + pattern match
  for `docker-compose*.y*ml`, `compose.y*ml`, `*.k8s.yaml`,
  `kustomization.yaml`, `.github/workflows/*.yml`.
- Per-kind parser (JSON / TOML / YAML) producing a structured
  `summary` (e.g. `mise.toml: mise tools python,uv,bun,dagger`)
  and a `package_count` (workspace size for `package.json` and
  `dg.toml`).
- Graceful fallback to a tiny TOML subset parser if `tomllib` is
  unavailable (Python 3.10).
- 1 `ConfigFile` dataclass with BGE-M3 embedding on `summary`.
- 100-row upsert batches.

The Dagster asset `config_files` (group `infrastructure`) lives in
`sruth/oideachais/dagster_defs/assets/infrastructure_assets.py` and kicks
the v1 App via `cocoindex update oideachais.cocoindex_flows.config_indexing:config_app`.

#### Scenario: A developer finds the wrangler manifest for a worker

- **GIVEN** the `config_files` Dagster asset has materialised
- **WHEN** a developer runs `await search_config("cloudflare worker", kind="wrangler")`
- **THEN** the v1 App returns the top-15 wrangler rows semantically
  related to "cloudflare worker", ranked by BGE-M3 cosine similarity

#### Scenario: A developer lists all mise.toml files with their tool set

- **GIVEN** the `config_files` Dagster asset has materialised
- **WHEN** a developer runs `await search_config("", kind="mise", limit=50)`
- **THEN** the v1 App returns up to 50 rows where `kind = 'mise'`,
  each carrying a `summary` like `mise.toml: mise tools python,uv,bun`

### Requirement: V1 unified embedding App (unified_embeddings asset)

The system SHALL run a v1-native CocoIndex App for unified document
embedding, reading from any DuckDB-compatible source and writing to
the `unified_embeddings` LanceDB table. The App uses:

- Configurable DuckDB connection (default:
  `crypteolas_catalog.docs.scraped_documents`).
- `asyncio.to_thread` to read the DuckDB rows (does not block the event loop).
- `RecursiveSplitter` (markdown) for chunking, with a paragraph+char
  fallback when cocoindex is unavailable.
- `get_content_hash` (sha256 prefix) for per-chunk deduplication.
- `classify_content` (v0 parity) to tag each chunk as `documentation` or `code`.
- 1 `UnifiedDocumentRow` dataclass with BGE-M3 embedding on `text`
  (1024 dims) and stable IDs of the form
  `unified:<doc_id>:<chunk_index>:<content_hash>`.

The Dagster asset `unified_embeddings` (group `embedding`) lives in
`sruth/oideachais/dagster_defs/assets/unified_embedding_assets.py` and
kicks the v1 App via
`cocoindex update oideachais.cocoindex_flows.unified_embedding:unified_app`.

#### Scenario: A developer searches unified documents by source type

- **GIVEN** the `unified_embeddings` Dagster asset has materialised
- **WHEN** a developer runs `await unified_search("SpacetimeDB reducer", source_types=["protocol_docs"])`
- **THEN** the v1 App returns the top-10 rows from the `unified_embeddings`
  LanceDB table, filtered by `source_type IN ('protocol_docs')`,
  ranked by BGE-M3 cosine similarity to the query

#### Scenario: A developer filters by protocol

- **GIVEN** the `unified_embeddings` Dagster asset has materialised
- **WHEN** a developer runs `await unified_search("reducer", protocol="spacetimedb")`
- **THEN** the v1 App returns only rows where `protocol = 'spacetimedb'`,
  ranked by BGE-M3 cosine similarity

### Requirement: V1 code embedding App (code_embeddings asset)

The system SHALL run a v1-native CocoIndex App for local code file
embedding, walking a configurable directory and writing to the
`code_embeddings` LanceDB table. The App uses:

- `UNIFIED_CODE_ROOT` env var (default:
  `sruth/crypteolas/storage/data/code/`).
- `localfs.walk_dir(code_root, recursive=True, live=True, refresh_interval=3600s)`
  with the codebase_indexing.py excludes.
- 8 file extensions: `*.py`, `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.rs`,
  `*.go`, `*.sol`.
- `RecursiveSplitter` with `detect_code_language` for chunking
  (the canonical v1 pattern from `codebase_indexing.py`).
- 1 `CodeChunkRow` dataclass with BGE-M3 embedding on `text` and
  stable IDs of the form `code:<filename>:<chunk_index>`.

The Dagster asset `code_embeddings` (group `embedding`) lives in
`sruth/oideachais/dagster_defs/assets/unified_embedding_assets.py` and
kicks the v1 App via
`cocoindex update oideachais.cocoindex_flows.unified_embedding:code_app`.

#### Scenario: A developer searches code embeddings by language

- **GIVEN** the `code_embeddings` Dagster asset has materialised
- **WHEN** a developer runs `await code_search("reducer", language="rust")`
- **THEN** the v1 App returns the top-10 rows from the `code_embeddings`
  LanceDB table, filtered by `language = 'rust'`,
  ranked by BGE-M3 cosine similarity to the query

#### Scenario: A developer filters by chunk type

- **GIVEN** the `code_embeddings` Dagster asset has materialised
- **WHEN** a developer runs `await code_search("function", chunk_type="block")`
- **THEN** the v1 App returns only rows where `chunk_type = 'block'`,
  ranked by BGE-M3 cosine similarity

### Requirement: V1 Celtic tutor agent (celtic_tutor_agent)

The system SHALL provide a Celtic-language tutor agent at
`oideachais.agents.adk.celtic_tutor_agent:celtic_tutor_agent` that
exposes the LlmAgent previously at
`tuatha.agents.adk.celtic_tutor:celtic_tutor_agent`. The agent
uses 4 tools: `search_curriculum_tool`, `get_vocabulary_tool`,
`translate_text_tool`, `get_learning_outcomes_tool`. The
`tuatha.agents.adk.celtic_tutor` file is a thin re-export of the
canonical agent.

#### Scenario: A consumer imports the agent via the oideachais path

- **GIVEN** the `oideachais.agents.adk.celtic_tutor_agent` module
- **WHEN** a consumer does `from oideachais.agents.adk.celtic_tutor_agent import celtic_tutor_agent`
- **THEN** the imported `celtic_tutor_agent` is a fully constructed
  `google.adk.agents.LlmAgent` with name `celtic_tutor_agent`

#### Scenario: A consumer imports the agent via the legacy tuatha path

- **GIVEN** the `tuatha.agents.adk.celtic_tutor` thin wrapper
- **WHEN** a consumer does `from tuatha.agents.adk.celtic_tutor import celtic_tutor_agent`
- **THEN** the imported `celtic_tutor_agent` is the **same object**
  as `oideachais.agents.adk.celtic_tutor_agent.celtic_tutor_agent`

### Requirement: V1 mythology narrator agent (mythology_narrator_agent)

The system SHALL provide a Celtic mythology narrator agent at
`oideachais.agents.adk.mythology_narrator_agent:mythology_narrator_agent`.
Uses 3 tools: `search_mythology_tool`, `get_character_info`,
`get_location_info`. The `tuatha.agents.adk.mythology_narrator`
file is a thin re-export.

#### Scenario: A consumer imports the agent via the oideachais path

- **GIVEN** the `oideachais.agents.adk.mythology_narrator_agent` module
- **WHEN** a consumer does `from oideachais.agents.adk.mythology_narrator_agent import mythology_narrator_agent`
- **THEN** the imported `mythology_narrator_agent` is a fully
  constructed `LlmAgent` with name `mythology_narrator_agent`

#### Scenario: A consumer imports the agent via the legacy tuatha path

- **GIVEN** the `tuatha.agents.adk.mythology_narrator` thin wrapper
- **WHEN** a consumer does `from tuatha.agents.adk.mythology_narrator import mythology_narrator_agent`
- **THEN** the imported `mythology_narrator_agent` is the **same
  object** as `oideachais.agents.adk.mythology_narrator_agent.mythology_narrator_agent`

### Requirement: V1 quest guide agent (quest_guide_agent)

The system SHALL provide a quest guide agent at
`oideachais.agents.adk.quest_guide_agent:quest_guide_agent` that
exposes the LlmAgent previously at
`tuatha.agents.adk.quest_guide:quest_guide_agent`. Uses 4 tools:
`get_quest_hints_tool`, `get_player_progress_tool`,
`search_related_curriculum`, `get_learning_outcomes_for_quest`.

#### Scenario: A consumer imports the agent via the oideachais path

- **GIVEN** the `oideachais.agents.adk.quest_guide_agent` module
- **WHEN** a consumer does `from oideachais.agents.adk.quest_guide_agent import quest_guide_agent`
- **THEN** the imported `quest_guide_agent` is a fully constructed
  `LlmAgent` with name `quest_guide_agent`

#### Scenario: A consumer imports the agent via the legacy tuatha path

- **GIVEN** the `tuatha.agents.adk.quest_guide` thin wrapper
- **WHEN** a consumer does `from tuatha.agents.adk.quest_guide import quest_guide_agent`
- **THEN** the imported `quest_guide_agent` is the **same object**
  as `oideachais.agents.adk.quest_guide_agent.quest_guide_agent`

### Requirement: V1 research assistant agent (research_assistant_agent)

The system SHALL provide a research assistant agent at
`oideachais.agents.adk.research_assistant_agent:research_assistant_agent`.
Uses 3 tools: `research_curriculum`, `research_mythology`,
`compare_languages`.

#### Scenario: A consumer imports the agent via the oideachais path

- **GIVEN** the `oideachais.agents.adk.research_assistant_agent` module
- **WHEN** a consumer does `from oideachais.agents.adk.research_assistant_agent import research_assistant_agent`
- **THEN** the imported `research_assistant_agent` is a fully
  constructed `LlmAgent` with name `research_assistant_agent`

#### Scenario: A consumer imports the agent via the legacy tuatha path

- **GIVEN** the `tuatha.agents.adk.research_assistant` thin wrapper
- **WHEN** a consumer does `from tuatha.agents.adk.research_assistant import research_assistant_agent`
- **THEN** the imported `research_assistant_agent` is the **same
  object** as `oideachais.agents.adk.research_assistant_agent.research_assistant_agent`

### Requirement: V1 Tuatha root agent (tuatha_root_agent)

The system SHALL provide a root orchestrator agent at
`oideachais.agents.adk.tuatha_root_agent:root_agent` that wraps
the 4 specialist agents as `sub_agents`. Also constructs the
`google.adk.apps.app.App(name="tuath")` and exports a
`classify_query(query) -> str` helper for routing
("tutor" / "mythology" / "quest" / "research").

The `tuatha.agents.adk.root_agent` thin wrapper re-exports the
root agent + the 4 specialists + the `app` + the `classify_query`
helper for backwards compatibility with
`tuatha.agents.orchestrator.AgentRegistry.initialize_defaults()`.

#### Scenario: A consumer imports the root agent via the oideachais path

- **GIVEN** the `oideachais.agents.adk.tuatha_root_agent` module
- **WHEN** a consumer does `from oideachais.agents.adk.tuatha_root_agent import root_agent`
- **THEN** the imported `root_agent` is a fully constructed
  `LlmAgent` with name `tuath_agent` and 4 sub_agents
  (`celtic_tutor_agent`, `mythology_narrator_agent`,
  `quest_guide_agent`, `research_assistant_agent`)

#### Scenario: A consumer classifies a query

- **GIVEN** the `tuatha.agents.adk.root_agent` thin wrapper
- **WHEN** a consumer calls `classify_query("translate hello into Irish")`
- **THEN** the function returns `"tutor"` (the first matching
  keyword bucket, per the v0 logic)

### Requirement: ExtractCircularMeta Pydantic mirror

The canonical BAML function `ExtractCircularMeta` (in `sruth/oideachais/baml_src/circular_extraction.baml`) MUST have a Pydantic v2 mirror in `spaces/an_scrudu/extraction.py`. The Pydantic classes (`PCircularReference`, `PTopicDistribution`, `PMarkingSchemeSummary`, `PCircularExtraction`) MUST mirror the BAML class shapes exactly, and `_validate_and_coerce` MUST validate the LLM response against the Pydantic schema before falling back to the flat legacy schema.

#### Scenario: LLM returns the nested BAML shape

- **WHEN** the LiteLLM gateway returns a JSON object with `{circular: {...}, scheme: {topics: [...]}}`
- **THEN** `_validate_and_coerce` validates it against `PCircularExtraction`
- **AND** on success, maps to the flat `CircularExtraction` dataclass
- **AND** on failure, falls back to the flat schema with defaults

#### Scenario: Pydantic not installed

- **WHEN** `pydantic` is not in the requirements
- **THEN** the Space falls back to the flat legacy schema (no Pydantic validation)
- **AND** a warning is logged

### Requirement: oideachais Mission Control Space

The oideachais quadrant MUST provide a Mission Control HuggingFace Space at `spaces/oideachais_mission_control/` that surfaces the 5 educational stages (Aistear / Primary / JC / SC / Tertiary) as marimo notebooks over the canonical MotherDuck lakehouse. The Space MUST be wired to the canonical BAML extraction + Cognee cognify + MotherDuck Dive buttons per stage.

#### Scenario: User opens the Mission Control

- **WHEN** a user navigates to the oideachais_mission_control Space
- **THEN** they see 5 tabs (one per educational stage)
- **AND** each tab shows a marimo notebook backed by MotherDuck
- **AND** each tab has a Cognee cognify button + a BAML extraction button + a MotherDuck Dive button

### Requirement: Round 11 Phase 1 — Confirmed-Dead Code Removed (2026-06-25)

The `oideachais-pipeline` capability spec MUST acknowledge that Round 11 of the
multi-quadrant sprawl audit (executed 2026-06-25) removed 14 confirmed-dead
items from `sruth/oideachais/`. The deletions were verified via pre-flight
grep across `sruth/oideachais/dagster_defs`, `sruth/oideachais/api`,
`sruth/oideachais/dlt_sources`, `sruth/oideachais/scripts`,
`sruth/oideachais/notebooks`, `sruth/oideachais/tests`,
`sruth/oideachais/cocoindex_flows`, `sruth/oideachais/cognee_integration`,
`sruth/oideachais/graph`, `sruth/oideachais/lancedb`, `sruth/oideachais/agents`,
`sruth/oideachais/alignment`, and `sruth/oideachais/ocr` (0 matches found for
each deleted item, excluding `__pycache__`).

#### Scenario: A developer queries the canonical layout

- **GIVEN** the openspec change `oideachais-audit-phase-1-delete-dead-code`
  is archived
- **WHEN** a developer runs `ls sruth/oideachais/`
- **THEN** the directory count is 55 (down from 61)
- **AND** the following paths no longer exist:
  - `sruth/oideachais/oideachais/` (nested legacy shim)
  - `sruth/oideachais/services/` (only contained the deleted embedding_service)
  - `sruth/oideachais/services/embedding_service/` (dead FastAPI)
  - `sruth/oideachais/marimo/` (dead 1-file stub)
  - `sruth/oideachais/exam_scraper/` (dead 2-script)
  - `sruth/oideachais/downloads/` (empty mount)
- **AND** the following root-level files no longer exist:
  - `sruth/oideachais/leaving_cert_timetable.pdf` (270 KB orphan)
  - `sruth/oideachais/PIPELINE_OPERATIONS.md` (orphaned doc)
  - `sruth/oideachais/test_api.py`
  - `sruth/oideachais/test_crawl.py`
  - `sruth/oideachais/test_crawl2.py`
  - `sruth/oideachais/test_full_crawl.py`
  - `sruth/oideachais/test_all_sources.py`

#### Scenario: Embedding service migration path

- **WHEN** any caller needs text embeddings after the deletion
- **THEN** they MUST use `sruth.oideachais.clients.embedding_client.EmbeddingClient`
  (the canonical in-process client with BGE-M3 fallback per the
  `embedding-pipeline` skill)
- **AND** NOT import from `sruth.oideachais.services.embedding_service`
  (the deleted module)

#### Scenario: OCR comparison migration path

- **WHEN** any caller needs OCR comparison outputs after the deletion
- **THEN** they MUST use `sruth/meaisinfhoghlaim/marimo/01_leabharlann_descriptive.py`
  (the canonical descriptive stats notebook)
- **OR** the Dagster asset at
  `sruth/oideachais/dagster_defs/assets/ocr_comparison_assets.py`
  (the canonical programmatic interface)
- **AND** NOT import from `sruth.oideachais.marimo.ocr_comparison_enhanced`
  (the deleted module)

#### Scenario: SEC exam paper ingestion migration path

- **WHEN** any caller needs SEC exam paper ingestion after the deletion
- **THEN** they MUST use the `ireland_examinations` DLT source via
  `sruth.oideachais.dlt_sources.ireland.examinations` and the
  `ireland/education/exam_materials_assets.py` Dagster asset group
- **AND** NOT import from `sruth.oideachais.exam_scraper.{retry_failed,scrape_exam_stats}`
  (the deleted modules)

#### Scenario: Test author path

- **WHEN** any test author writes a new test for the oideachais quadrant
- **THEN** they MUST place it under `sruth/oideachais/tests/` following the
  existing per-test-file or per-test-module pattern with `conftest.py` fixtures
- **AND** NOT place test scripts at the root of `sruth/oideachais/`
  (the 5 deleted root-level test scripts are the canonical example of the
  anti-pattern that has now been removed)

### Requirement: Round 11 Phase 2A — Pure-Duplicate Surface Removal (2026-06-25)

The `oideachais-pipeline` capability spec MUST acknowledge that Round 11
phase 2A (executed 2026-06-25) removed 4 confirmed-pure-duplicate surface
pairs from `sruth/oideachais/`, with a total of 5,527 LOC and 17 files
removed. All deletions were byte-identical to canonical surfaces and verified
to have zero external importers (excluding the deprecated stub's single test
importer, which was updated to use the canonical replacement).

The canonical surfaces that retain all functionality:

| Pair | Duplicate (removed) | Canonical (kept) | LOC removed |
|:--|:--|:--|--:|
| 1 | `sruth/oideachais/routes/` | `sruth/oideachais/api/routes/` | 2,836 |
| 2 | `sruth/oideachais/sensors/` | `sruth/oideachais/dagster_defs/sensors/` | 994 |
| 3 | `sruth/oideachais/middleware/` | `sruth/oideachais/api/middleware/` | 1,668 |
| 4 | `sruth/oideachais/storage/serial_executor.py` (deprecated) | `sruth/oideachais/core/storage/serial_executor.py` | 29 |

#### Scenario: A developer imports from a canonical route

- **WHEN** any caller needs a FastAPI router from the oideachais API
- **THEN** they MUST import from `sruth.oideachais.api.routes.{agent,curriculum,search,geospatial,tts,cross_archive_graph,leaving_cert,official_media}` (8 routers total — 5 from before + 3 added in canonical during the Phase 6 leabharlann cross-archive work)
- **AND** NOT import from `sruth.oideachais.routes.*` (the deleted duplicate)

#### Scenario: A developer imports a Dagster sensor

- **WHEN** any caller needs a Dagster sensor from the oideachais platform
- **THEN** they MUST import from `sruth.oideachais.dagster_defs.sensors.all_sensors` (which aggregates all 5 canonical sensor groups: `domain_sensors`, `curriculum_freshness_sensors`, `author_archive_sensors`, `leabharlann_sensors`, `cognee_cron_sensor`)
- **AND** NOT import from `sruth.oideachais.sensors.*` (the deleted duplicate; its stale `__init__.py` only loaded 2 of 5 sensor groups)

#### Scenario: A developer imports FastAPI middleware

- **WHEN** any caller needs the AG-UI / streaming / auth middleware
- **THEN** they MUST import from `sruth.oideachais.api.middleware.{AuthMiddleware, agui.event_translator, agui.session_manager, agui.streaming}` (4 middleware components)
- **AND** NOT import from `sruth.oideachais.middleware.*` (the deleted duplicate)

#### Scenario: A developer imports the serial database executor

- **WHEN** any caller needs `SerialDatabaseExecutor` or `get_executor`
- **THEN** they MUST import from `sruth.oideachais.core.storage.{SerialDatabaseExecutor, get_executor, run_serial}` (the canonical authoritative implementation)
- **AND** NOT import from `sruth.oideachais.storage.serial_executor` (the deleted deprecated stub)

#### Scenario: The canonical surface contract is preserved

- **GIVEN** `openspec/changes/oideachais-audit-phase-2a-remove-pure-duplicates` is archived
- **WHEN** the Dagster Definitions load (`sruth.oideachais.dagster_defs.definitions`)
- **THEN** `defs.sensors` MUST contain all 5 canonical sensor groups (verified via `from sruth.oideachais.dagster_defs.sensors import all_sensors; assert len(all_sensors) >= 5`)
- **AND** `sruth/oideachais/api/main.py` MUST successfully `include_router` all 6 routers from `api.routes` (verified via FastAPI app construction without ImportError)
- **AND** `sruth/oideachais/api/middleware/AuthMiddleware` MUST be importable from the canonical `api.middleware` package

#### Scenario: No residual references after deletion

- **WHEN** any developer runs `grep -rn "from sruth.oideachais.routes\b\|from sruth.oideachais.sensors\b\|from sruth.oideachais.middleware\b\|from oideachais.storage.serial_executor" --include="*.py" --include="*.md"`
- **THEN** zero matches MUST appear outside `openspec/changes/archive/` (the only residual refs are in archived openspec change metadata, which is intentional)

### Requirement: Round 11 Phase 2B — Legacy Storage + Dagster Asset Migration (2026-06-25)

The `oideachais-pipeline` capability spec MUST acknowledge that Round 11
phase 2B (executed 2026-06-25) migrated 11 unique legacy files (5,646 LOC)
from the deprecated `sruth/oideachais/dagster_assets/` and
`sruth/oideachais/storage/` directories to their canonical homes in
`sruth/oideachais/dagster_defs/assets/` and
`sruth/oideachais/core/storage/{clients,config}/`, while removing 5 dead
files (1,544 LOC).

The canonical surfaces after this change:

| Legacy (removed) | Canonical (target) | LOC |
|:--|:--|--:|
| `sruth/oideachais/dagster_assets/model_conversion.py` | `sruth/oideachais/dagster_defs/assets/model_conversion.py` | 374 |
| `sruth/oideachais/dagster_assets/asset_generation.py` | `sruth/oideachais/dagster_defs/assets/asset_generation.py` | 281 |
| `sruth/oideachais/dagster_assets/{grammar_validation,pdf_benchmark,syntactic_parsing}.py` | (deleted — 0 importers) | 1,433 |
| `sruth/oideachais/storage/config.py` | `sruth/oideachais/core/storage/config.py` | 359 |
| `sruth/oideachais/storage/connections.py` | `sruth/oideachais/core/storage/connections.py` | 691 |
| `sruth/oideachais/storage/ducklake.py` | `sruth/oideachais/core/storage/ducklake.py` | 780 |
| `sruth/oideachais/storage/ducklake_client.py` | `sruth/oideachais/core/storage/clients/ducklake.py` | 882 |
| `sruth/oideachais/storage/ducklake_filesystem.py` | `sruth/oideachais/core/storage/clients/ducklake_filesystem.py` | 623 |
| `sruth/oideachais/storage/init_schemas.py` | `sruth/oideachais/core/storage/init_schemas.py` | 418 |
| `sruth/oideachais/storage/lance_iceberg.py` | `sruth/oideachais/core/storage/lance_iceberg.py` | 603 |
| `sruth/oideachais/storage/lancedb_cloud.py` | `sruth/oideachais/core/storage/clients/lancedb_cloud.py` | 664 |
| `sruth/oideachais/storage/curriculum_vectors.py` | `sruth/oideachais/core/storage/curriculum_vectors.py` | 427 |

#### Scenario: A developer adds a new HF → GGUF conversion asset

- **WHEN** any caller needs to add a new HuggingFace → GGUF model conversion for llama-swap
- **THEN** they MUST add a new `@asset` function to `sruth/oideachais/dagster_defs/assets/model_conversion.py` (which contains `hf_models_downloaded`, `gguf_qwen2_5_math_7b`, `gguf_uccix_13b`, etc.)
- **AND** register it in the `model_conversion_assets` list at the bottom of the file
- **AND** NOT add it to the deleted `sruth/oideachais/dagster_assets/model_conversion.py`

#### Scenario: A developer adds a new study asset generation asset

- **WHEN** any caller needs to add a new BAML-driven image generation asset (fibo_configs_built, study_assets_rendered, study_assets_published)
- **THEN** they MUST add a new `@asset` function to `sruth/oideachais/dagster_defs/assets/asset_generation.py`
- **AND** register it in the `asset_generation_assets` list at the bottom of the file
- **AND** NOT add it to the deleted `sruth/oideachais/dagster_assets/asset_generation.py`

#### Scenario: A developer uses the multi-backend storage config

- **WHEN** any caller needs the multi-backend `StorageConfig` (CogneeConfig, DuckLakeConfig, FalkorDBConfig, GarageConfig, LakehouseConfig, LanceDBConfig, MemgraphConfig, PlanetScaleConfig)
- **THEN** they MUST import from `sruth.oideachais.core.storage.config` (re-exported via `sruth.oideachais.core.storage`)
- **AND** NOT import from `sruth.oideachais.storage.config`

#### Scenario: A developer uses a DuckLake client

- **WHEN** any caller needs the DuckLake postgres-catalog + Garage-S3 client (`DuckLakeClient`)
- **THEN** they MUST import from `sruth.oideachais.core.storage.clients.ducklake`
- **AND** NOT import from `sruth.oideachais.storage.ducklake_client`

#### Scenario: A developer uses the LanceDB Cloud client

- **WHEN** any caller needs the managed LanceDB Cloud integration (`LanceDBCloudClient`, `LanceDBCloudConfig`, `EmbeddingBatch`, `CircuitBreaker`)
- **THEN** they MUST import from `sruth.oideachais.core.storage.clients.lancedb_cloud`
- **AND** NOT import from `sruth.oideachais.storage.lancedb_cloud`

#### Scenario: A developer uses curriculum vector search

- **WHEN** any caller needs the `CurriculumVectorSearch` BGE-M3-powered semantic search over curriculum content
- **THEN** they MUST import from `sruth.oideachais.core.storage.curriculum_vectors`
- **AND** NOT import from `sruth.oideachais.storage.curriculum_vectors`

#### Scenario: The canonical surface contract is preserved

- **GIVEN** `openspec/changes/oideachais-audit-phase-2b-migrate-legacy-storage-and-dagster-assets` is archived
- **WHEN** the Dagster Definitions load (`sruth.oideachais.dagster_defs.definitions`)
- **THEN** `defs.assets` MUST contain `model_conversion_assets` and `asset_generation_assets` (verified via `from sruth.oideachais.dagster_defs.assets.model_conversion import model_conversion_assets; assert len(model_conversion_assets) >= 8`)
- **AND** `defs.assets` MUST contain `asset_generation_assets` with ≥ 4 assets
- **AND** `sruth/oideachais/core/storage/__init__.py` MUST re-export all 25 newly-migrated symbols (verified via `from sruth.oideachais.core.storage import (CogneeConfig, DuckLakeConfig, StorageManager, DuckLakeClient, LanceDBCloudClient, CurriculumVectorSearch)`)
- **AND** the legacy `sruth/oideachais/dagster_assets/` and `sruth/oideachais/storage/` directories MUST NOT exist (verified via `not os.path.exists(...)`)

#### Scenario: No residual references after migration

- **WHEN** any developer runs `grep -rn "from sruth.oideachais.dagster_assets\|from oideachais.dagster_assets\|from sruth.oideachais.storage\.[a-z_]\|from oideachais.storage\.[a-z_]" --include="*.py" --include="*.md"`
- **THEN** zero matches MUST appear outside `openspec/changes/archive/` (the only residual refs are in archived openspec change metadata, which is intentional)

### Requirement: Leabharlann DLT Source Package Naming
The personal-archive DLT source package SHALL be located at `sruth/oideachais/dlt_sources/leabharlann/`.

The package directory SHALL be named `leabharlann` (Irish for "library") to match:
- the source callable names inside the package (`leabharlann_books`, `leabharlann_zotero`, `leabharlann_takeout`),
- the `oideachais-leabharlann` skill documentation, and
- the Irish-first naming convention used across the data platform.

The previous `dlt_sources/author_archive/` directory SHALL NOT exist after this change is applied.

#### Scenario: dlt_sources/leabharlann package exists
- **WHEN** a developer lists the contents of `sruth/oideachais/dlt_sources/`
- **THEN** a `leabharlann/` directory SHALL be present
- **AND** the directory SHALL contain `__init__.py`, `leabharlann_books.py`, `zotero.py`, `takeout_v1.py`, `google_takeout.py`, `gemini_deep_research.py`, `university_of_galway.py`, `previews.py`, `_citation_extractor.py`, `_epub_extractor.py`, `_scanner.py`, `_takeout_paths.py`, and `config.example.yaml`
- **AND** no `author_archive/` directory SHALL be present

#### Scenario: leabharlann sources importable from canonical path
- **WHEN** Python code executes `from dlt_sources.leabharlann import leabharlann_books_source, zotero_source, takeout_v1_source`
- **THEN** the import SHALL succeed without raising `ModuleNotFoundError`
- **AND** the callable names SHALL match the `name=` argument on each `@dlt.source` decorator

#### Scenario: no stale references to author_archive import path
- **WHEN** a developer runs `grep -rn "dlt_sources\.author_archive" --include="*.py" sruth/`
- **THEN** zero matches SHALL be returned
- **AND** the legacy `dlt_sources.author_archive` import path SHALL be fully retired

### Requirement: Country-First DLT Source Layout
The canonical DLT source package SHALL use the country-first layout `sruth/oideachais/dlt_sources/{nation}/{domain}/{entity}.py` where `{nation}` is one of `{ie, ni, en, sct, wls, iom, jey, ggy, pan_celtic, cross}` and `{domain}` is one of `{education, culture, law, medicine, statistics, site_analysis}`.

A `domains/` wrapper directory SHALL NOT exist as an intermediate level in the canonical layout. (The legacy `domains/{domain}/{nation}/` tree, when it existed, has been retired.)

#### Scenario: canonical files live at country-first paths
- **WHEN** a developer lists the contents of `sruth/oideachais/dlt_sources/`
- **THEN** a `ie/` directory SHALL exist with `education/`, `culture/`, `law/`, `medicine/` subdirectories
- **AND** an `en/` directory SHALL exist with `education/`, `law/`, `medicine/` subdirectories
- **AND** a `sct/` directory SHALL exist with `education/`, `statistics/`, `medicine/` subdirectories
- **AND** no `domains/` directory SHALL be present

#### Scenario: no stale imports of dlt_sources.domains.*
- **WHEN** a developer runs `grep -rn "dlt_sources\.domains\." --include="*.py" sruth/oideachais/`
- **THEN** zero matches SHALL be returned (excluding frozen `openspec/changes/archive/*` records)

#### Scenario: shims still re-export from legacy ireland/uk/etc.
- **WHEN** Python code executes `from dlt_sources.ie.education import ncca`
- **THEN** the import SHALL succeed (re-exporting from the legacy `dlt_sources.ireland.ncca` path)
- **AND** calling `ncca()` SHALL produce the same source as before the migration

### Requirement: Country-First Layout — Single-Source Migration

The system SHALL migrate all single-source DLT files from the legacy flat-tree layout
(`dlt_sources/ireland/*.py`, `dlt_sources/uk/{england,northern_ireland,scotland,wales}/*.py`,
`dlt_sources/celtic/*.py`) to the canonical country-first layout
(`dlt_sources/{nation}/{domain}/{entity}.py`).

#### Scenario: Single-source IE education files migrated

- **WHEN** a file in `dlt_sources/ireland/` defines exactly one `@dlt.source` function and is in scope of the education domain
- **THEN** the system SHALL move it to `dlt_sources/ie/education/{filename}.py`
- **AND** the system SHALL update all importers in `dagster_defs/`, `tests/`, `dlt_utils/`, and remaining `dlt_sources/ireland/*.py` files

#### Scenario: Single-source UK education files migrated

- **WHEN** a file in `dlt_sources/uk/{england,northern_ireland,scotland,wales}/` defines exactly one `@dlt.source` function and is in scope of the education domain
- **THEN** the system SHALL move it to `dlt_sources/{en,ni,sct,wls}/education/{filename}.py`
- **AND** the system SHALL update all importers

#### Scenario: Single-source UK statistics files migrated

- **WHEN** a file in `dlt_sources/uk/{england,northern_ireland,scotland,wales}/` defines exactly one `@dlt.source` function and is in scope of the statistics domain
- **THEN** the system SHALL move it to `dlt_sources/{en,ni,sct,wls}/statistics/{filename}.py`
- **AND** the system SHALL update all importers

#### Scenario: Single-source Celtic nation-scoped files migrated

- **WHEN** a file in `dlt_sources/celtic/` defines exactly one `@dlt.source` function and is scope-specific to Ireland
- **THEN** the system SHALL move it to `dlt_sources/ie/{culture,education}/{filename}.py`
- **AND** the system SHALL update all importers

#### Scenario: Shared utility files migrated to dlt_sources/common/

- **WHEN** a file in `dlt_sources/ireland/` defines protocol classes, registries, or deduplication utilities used across multiple DLT sources
- **THEN** the system SHALL move it to `dlt_sources/common/{filename}.py`
- **AND** the system SHALL update all intra-tree and external importers

#### Scenario: Multi-source files NOT touched

- **WHEN** a legacy file defines more than one `@dlt.source` function
- **THEN** the system SHALL NOT move it in Phase 3C
- **AND** the system SHALL defer it to Phase 3D for per-source splitting first

#### Scenario: Legacy trees NOT deleted

- **WHEN** legacy flat trees (`dlt_sources/ireland/`, `dlt_sources/uk/`, `dlt_sources/celtic/`) still contain multi-source files deferred to Phase 3D
- **THEN** the system SHALL NOT delete the legacy trees
- **AND** the system SHALL defer tree deletion to Phase 3E

### Requirement: Country-First Layout — Multi-Source File Splitting

The system SHALL split all multi-source legacy DLT files so that each `@dlt.source` function
lives in its own canonical file at `dlt_sources/{nation}/{domain}/{entity}.py`.

#### Scenario: Each `@dlt.source` function lives in its own file

- **WHEN** a legacy file contains 2+ `@dlt.source` functions
- **THEN** the system SHALL split the file such that each `@dlt.source` function lives in its own file
- **AND** the system SHALL extract shared private helpers (non-`@dlt.source` functions and module constants) to a sibling `_helpers.py` file
- **AND** the system SHALL move the new files to the canonical `dlt_sources/{nation}/{domain}/{entity}.py` paths

#### Scenario: Per-source function blocks preserved with decorators

- **WHEN** a `@dlt.source` function contains nested `@dlt.resource` functions
- **THEN** the system SHALL preserve the source function and all its nested resource functions in the same output file
- **AND** the system SHALL preserve all decorators (`@dlt.source`, `@dlt.resource`, `@dlt.transformer`) and indentation

#### Scenario: Shared helpers extracted to private modules

- **WHEN** multiple split source files reference the same private helper function or module constant
- **THEN** the system SHALL extract the shared helper to a sibling `_helpers.py` file (e.g. `dlt_sources/ie/education/_oide_helpers.py`)
- **AND** the system SHALL rewrite intra-file references to import from the helper module

#### Scenario: Legacy multi-source files deleted after split

- **WHEN** all `@dlt.source` functions from a legacy multi-source file have been split
- **THEN** the system SHALL delete the legacy file
- **AND** the system SHALL update all importers

#### Scenario: Multi-source file mapping table

The following legacy multi-source files SHALL be split per source:

| Legacy | Splits into |
|:--|:--|
| `dlt_sources/ireland/oide.py` | `dlt_sources/ie/education/{oide, oide_subject, oide_gaeilge, oide_all_subjects}.py` |
| `dlt_sources/ireland/examinations.py` | `dlt_sources/ie/education/{examinations, sec_examinations_browser, leaving_certificate, junior_cycle_exams, mathematics_exams, science_subjects_exams}.py` |
| `dlt_sources/ireland/local_documents.py` | `dlt_sources/ie/culture/{local_education_documents, local_documents_by_subject}.py` |
| `dlt_sources/ireland/agentic_discovery.py` | `dlt_sources/ie/education/{agentic_discovery, deep_research}.py` |
| `dlt_sources/ireland/pdf_downloader.py` | `dlt_sources/ie/education/{pdf_downloads, exam_pdf_downloads}.py` |
| `dlt_sources/uk/england/national_curriculum.py` | `dlt_sources/en/education/{national_curriculum, aqa_qualifications, edexcel_qualifications, ocr_qualifications, all_exam_boards}.py` |
| `dlt_sources/uk/northern_ireland/ccea_curriculum.py` | `dlt_sources/ni/education/{ni_curriculum, ccea_qualifications, irish_medium_ni}.py` |
| `dlt_sources/uk/scotland/curriculum_for_excellence.py` | `dlt_sources/sct/education/{curriculum_for_excellence, sqa_qualifications, gaelic_curriculum}.py` |
| `dlt_sources/uk/wales/curriculum_for_wales.py` | `dlt_sources/wls/education/{curriculum_for_wales, wjec_qualifications, welsh_medium}.py` |
| `dlt_sources/celtic/canuint.py` | `dlt_sources/ie/culture/canuint/{pronunciation, search, audio_download, dialect_summary, word_alignment}.py` |
| `dlt_sources/celtic/duchas_images.py` | `dlt_sources/ie/culture/{duchas_images, hidden_heritages}.py` |
| `dlt_sources/celtic/gaois.py` | `dlt_sources/ie/culture/{logainm, tearma, ainm, gaois_combined}.py` |
| `dlt_sources/geospatial/met_office.py` | `dlt_sources/ie/statistics/{met_office, met_office_forecast}.py` |
| `dlt_sources/geospatial/cso_small_areas.py` | `dlt_sources/ie/statistics/{cso_small_areas, cso_education, cso_deprivation}.py` |
| `dlt_sources/geospatial/geohive.py` | `dlt_sources/ie/statistics/{geohive, geohive_deprivation}.py` |
| `dlt_sources/bunchloch/filesystem_source.py` | `dlt_sources/cross/bunchloch/{filesystem, filesystem_by_subject}.py` |

### Requirement: Crown Dependencies Sources Live at Per-Nation Canonical Paths

The system SHALL split the `dlt_sources/crown_dependencies/` umbrella so that
each Crown Dependency's education source lives at `dlt_sources/{nation}/education/{entity}.py`,
matching the country-first layout convention.

#### Scenario: Jersey + Guernsey sources split into per-nation files

- **WHEN** `dlt_sources/crown_dependencies/channel_islands.py` contains both `jersey_source` and `guernsey_source`
- **THEN** the system SHALL move `jersey_source` to `dlt_sources/jey/education/channel_islands.py`
- **AND** the system SHALL move `guernsey_source` to `dlt_sources/ggy/education/channel_islands.py`
- **AND** the system SHALL extract shared private helpers (e.g. `_crawl_jersey_education`, `_crawl_guernsey_education`) to a sibling `_channel_islands_helpers.py`

#### Scenario: Isle of Man source moves to canonical home

- **WHEN** `dlt_sources/crown_dependencies/isle_of_man.py` contains `isle_of_man_source`
- **THEN** the system SHALL move `isle_of_man_source` to `dlt_sources/iom/education/isle_of_man.py`
- **AND** the system SHALL preserve the private `_crawl_iom_education` helper inline within the single-source file

#### Scenario: Per-nation `__init__.py` shims import from canonical paths

- **WHEN** the per-nation education shims (`iom/education/__init__.py`, `jey/education/__init__.py`, `ggy/education/__init__.py`) currently re-export from `crown_dependencies/`
- **THEN** the system SHALL replace each re-export with a direct import from the local canonical file (e.g. `from dlt_sources.iom.education.isle_of_man import isle_of_man_source`)
- **AND** the system SHALL break the circular import between the per-nation shims and the `crown_dependencies/` umbrella

#### Scenario: Crown Dependencies umbrella deleted

- **WHEN** all per-nation canonical files exist + all consumers import from the canonical paths
- **THEN** the system SHALL delete `dlt_sources/crown_dependencies/__init__.py`
- **AND** the system SHALL delete `dlt_sources/crown_dependencies/channel_islands.py`
- **AND** the system SHALL delete `dlt_sources/crown_dependencies/isle_of_man.py`
- **AND** the system SHALL leave no production-code references to `crown_dependencies` after deletion

### Requirement: Legacy flat files consolidated at canonical paths

The `dlt_sources/` package MUST NOT contain flat `.py` files at its root
that define `@dlt.source` functions or shared utility modules. Every
DLT source MUST live at a country-first canonical path
`dlt_sources/{nation}/{domain}/{entity}.py`. Every shared utility
module MUST live at either `dlt_sources/common/{name}.py` (for DLT
helpers) or `dlt_utils/{name}.py` (for pipeline config).

#### Scenario: tearma source split into per-source files

- **WHEN** the `tearma` corpus is queried
- **THEN** the `tearma_source` function MUST be importable from
  `dlt_sources.ie.culture.tearma`
- **AND** the `tearma_search_source` function MUST be importable from
  `dlt_sources.ie.culture.tearma_search`
- **AND** shared private state + module constants + helpers MUST live at
  `dlt_sources.ie.culture._tearma_helpers`
- **AND** the legacy `dlt_sources/tearma.py` flat file MUST NOT exist

#### Scenario: utility modules live at dlt_sources/common/

- **WHEN** a downstream DLT source needs `crawl_utils`, `http_client`, or
  `pagination`
- **THEN** those modules MUST be importable from
  `dlt_sources.common.{crawl_utils,http_client,pagination}`
- **AND** the legacy flat files at `dlt_sources/{crawl_utils,http_client,
  pagination}.py` MUST NOT exist
- **AND** the modules MUST sit alongside the existing
  `dlt_sources/common/` siblings (`_http_factories.py`, `incremental.py`,
  `content_deduplication.py`, `curriculum_registry.py`,
  `firecrawl_source.py`, `source_adapters.py`,
  `_shared_utils_stub.py`)

#### Scenario: pipeline config lives at dlt_utils/

- **WHEN** a DLT source needs `apply_dlthub_wrappers`
- **THEN** it MUST be importable from `dlt_utils.dlthub_projects`
- **AND** the legacy `dlt_sources/dlthub_projects.py` flat file MUST NOT
  exist
- **AND** the `dlt_utils/` package MUST re-export
  `apply_dlthub_wrappers` from its `__init__.py`

#### Scenario: importers rewire to canonical paths

- **WHEN** the 4 importers
  (`dlt_sources/ie/education/curriculum.py`,
  `dlt_sources/ie/education/curriculum_source.py`,
  `dlt_sources/ie/education/exam_source_update.py`,
  `dlt_sources/dagster_defs/factories.py`,
  `dlt_sources/tests/dlt_sources/test_integration.py`)
  reference the moved modules
- **THEN** they MUST import from the canonical paths
  (`dlt_utils.dlthub_projects`,
  `dlt_sources.ie.culture.tearma`,
  `dlt_sources.common.crawl_utils`)
- **AND** the legacy `dlt_sources.{dlthub_projects,tearma,crawl_utils,
  http_client,pagination}` paths MUST NOT be referenced

### Requirement: pyproject.toml + canonical docstrings use oideachais.* namespace

The `sruth/oideachais/pyproject.toml` file MUST NOT reference the legacy
`oideachais/data_platform/*` namespace that was deleted in post-cleanup
commit `8484a6353`. The canonical Python package is `oideachais`
(the uv workspace name), and the canonical Dagster code-location entry
point is `sruth/oideachais/dagster_defs/definitions.py`. The 4 sections
in `pyproject.toml` that historically pointed at
`data_platform.dagster_defs.*` MUST all reference the canonical
`oideachais.dagster_defs.*` namespace. The 3 canonical docstrings at
`sruth/oideachais/dlt_utils/destinations.py`,
`sruth/oideachais/dlt_sources/dg.toml`, and
`sruth/oideachais/dlt_sources/__init__.py` MUST NOT reference the
legacy namespace either.

#### Scenario: pyproject.toml has no data_platform references

- **WHEN** `sruth/oideachais/pyproject.toml` is parsed (TOML)
- **THEN** the 4 sections MUST point at the canonical
  `oideachais.dagster_defs.*` namespace
- **AND** the legacy `"data_platform.dagster_defs"` entry MUST be
  REMOVED from `[tool.hatch.build.targets.wheel] packages` (the
  package does not exist on disk; it was dead weight in the wheel
  build)

#### Scenario: docstrings use canonical import paths

- **WHEN** `dlt_utils/destinations.py` documents its usage example
- **THEN** it MUST reference `from dlt_utils import …` (not
  `from oideachais.data_platform.dlt_utils import …`)
- **AND** `dlt_sources/dg.toml` header comment MUST reference the
  canonical path `sruth/oideachais/dagster_defs/` (not the legacy
  `sruth/oideachais/data_platform/dagster_defs/`)

#### Scenario: shim docstring excludes deleted crown_dependencies

- **WHEN** `dlt_sources/__init__.py` enumerates legacy shim directories
- **THEN** it MUST NOT include `crown_dependencies` (deleted in
  Phase 3E on 2026-06-26)
- **AND** the remaining list MUST reflect the actual on-disk legacy
  trees as of Phase 5 completion (the `crown_dependencies` entry
  MUST be removed from the shim enumeration; the other entries
  MAY stay as documentation of remaining legacy areas)

### Requirement: Ireland Education Asset Location (v4)

The system SHALL store Ireland early-childhood, primary, junior-cycle, senior-cycle, and Leaving-Cert assets under `cianfhoghlaim/assets/` keyed by `ireland.education.{stage}.{language}`, where `stage ∈ {aistear, primary, junior_cycle, senior_cycle, leaving_cert_syllabus, leaving_cert_exam_paper, leaving_cert_marking_scheme}` and `language ∈ {english, gaeilge}`. Dagster asset key prefix changes from `oideachais.*` to `ireland.education.*`.

#### Scenario: Dagster asset resolution

- **WHEN** Dagster materialises an Ireland syllabus asset
- **THEN** the asset key is `ireland_education_leaving_cert_syllabus_english` (snake_case of `ireland.education.leaving_cert_syllabus.english`)
- **AND** the source module is `cianfhoghlaim.sources.nations.ie.education.leaving_cert.english`
- **AND** the BAML function is `cianfhoghlaim.core.baml.curriculum.ExtractLeavingCertSyllabus`
- **AND** the CocoIndex embedding flow is `cianfhoghlaim.core.cocoindex.ocr_aware_flow`

### Requirement: Leabharlann Asset Location (v4)

The system SHALL store leabharlann (personal archive) assets under `cianfhoghlaim/assets/leabharlann.py` keyed by `leabharlann.{corpus}.{document}`, where `corpus ∈ {aigne, gaeilge, gemini_deep_research, mata, ollscoil_na_gaillimhe, zotero}`. The physical corpus directory moves from `/leabharlann/` at repo root to `cianfhoghlaim/leabharlann/`.

#### Scenario: Leabharlann DAG asset resolution

- **WHEN** Dagster materialises a Zotero asset
- **THEN** the asset key is `leabharlann_zotero_paper`
- **AND** the source module is `cianfhoghlaim.pipelines.ingest.leabharlann.zotero`
- **AND** the CocoIndex flow is `cianfhoghlaim.core.cocoindex.leabharlann_flow`
- **AND** the destination is `ducklake://oideachais.leabharlann.zotero`

### Requirement: 16 Core Stack Packages (v4)

The system SHALL organise stack concerns under 16 `cianfhoghlaim/core/` packages: `dlt`, `duckdb`, `ducklake`, `lancedb`, `motherduck`, `cocoindex`, `baml`, `marimo`, `browser`, `cognee`, `obs`, `rag`, `search`, `curriculum`, `config`, `memory`.

#### Scenario: Cross-package import

- **WHEN** a developer imports `from cianfhoghlaim.core.lancedb import HnswConfig`
- **THEN** the import resolves to `cianfhoghlaim/core/lancedb/hnsw.py` (the canonical home, formerly at `sruth/oideachais/lancedb/indexing.py`)

### Requirement: 5-Stage Pipeline Spine (v4)

The system SHALL organise pipeline code under 5 `cianfhoghlaim/pipelines/` stages: `browser`, `ingest`, `distribute`, `process`, `expose`. Each stage is independently runnable from Dagster.

#### Scenario: Stage composition

- **WHEN** Dagster materialises an Ireland Leaving Cert paper
- **THEN** stage `browser` loads the PDF via `core/browser/sruth_browser/`
- **AND** stage `ingest` writes to local DuckDB via `core/duckdb/`
- **AND** stage `distribute` writes to DuckLake via `core/ducklake/`
- **AND** stage `process` runs CocoIndex OCR-aware flow via `core/cocoindex/`
- **AND** stage `expose` queries via `core/motherduck/` + `notebooks/ireland_curriculum_analysis.py`

### Requirement: 5-Layer Component Architecture (L1 Ingestion)

The `oideachais-pipeline` capability SHALL emit every Ingestion-layer
asset through `CelticIngestionComponent` (defined in
`cianfhoghlaim/dagster/components/layer1_ingestion.py`). The
Component SHALL be registered as the canonical L1 factory and SHALL
emit exactly one `@asset` per `@dlt.source`, with:

- `group_name = "1_ingestion/<domain>/<nation>"`
- `compute_kind = "dlt"`
- `automation_condition = AutomationCondition.eager() | AutomationCondition.cron(automation_cron)`
- `deps = [<upstream asset keys>]` derived from the YAML defs
- The 5 high-churn sources (NCCA, SEC, CCEA, SQA, WJEC) SHALL be
  state-backed via `dg.StateBackedComponent` with
  `state_refresh_interval="monthly"` (per user direction; the default
  is monthly to minimise unnecessary refreshes of cached external
  metadata; per-source override is allowed via the Component YAML).

The legacy `celtic_dlt_source.py` Component and the hand-written
`@asset` functions in `cianfhoghlaim/dagster/assets/` SHALL NOT
be used after this change lands.

#### Scenario: A developer scaffolds a new L1 ingestion asset

- **WHEN** `dg scaffold defs CelticIngestionComponent ie_education_geography --source-id ie.education.geography --domain curriculum --nation ie --automation on_cron --automation_cron "0 4 * * *"` runs
- **THEN** a YAML defs file is created at `defs/1_ingestion/curriculum/ie_education_geography/defs.yaml`
- **AND** `dg check yaml` reports the new asset passes
- **AND** `dg list defs` shows `1_ingestion/curriculum/ie_education_geography` with `automation_condition=cron @ 0 4 * * *`

#### Scenario: A L1 ingestion asset fires on upstream cron

- **GIVEN** the `1_ingestion/curriculum/ie_education_geography` asset has `automation_cron="0 4 * * *"`
- **WHEN** 02:00 UTC daily is reached
- **THEN** Dagster triggers the materialisation via `AutomationCondition.cron("0 4 * * *")`
- **AND** the asset key `["1_ingestion", "curriculum", "ie", "education", "geography"]` is recorded
- **AND** the partition (if any) is set per the YAML's `partitions_def`

#### Scenario: A state-backed L1 ingestion source refreshes monthly

- **GIVEN** the `1_ingestion/curriculum/ie/ncca_curriculum` asset has `state_backed=True` and `state_refresh_interval="monthly"`
- **WHEN** the code-location is reloaded at the start of each calendar month
- **THEN** the `CelticIngestionState` cache is refreshed from the canonical `sources.yaml`
- **AND** any new source URLs or removed source URLs are reflected in the asset graph
- **AND** between monthly refreshes, the cached state is used (no external metadata round-trip)

### Requirement: Partition-Aware Asset Checks (L2 Materials)

Every L2 `CelticMaterialsComponent` SHALL emit a partition-aware
`@asset_check` with the same `partitions_def` as the parent asset.

#### Scenario: BAML fidelity check fires on a single partition

- **GIVEN** the `2_materials/baml_extraction/leaving_cert_math` asset is partitioned by `(cycle, language, subject)`
- **WHEN** the partition `(2026, en, mathematics)` is materialised
- **THEN** `2_materials/baml_extraction/leaving_cert_math_baml_fidelity_check(context, ducklake)` evaluates ONLY that partition
- **AND** the `AssetCheckResult.passed` flag is True if the BAML extraction recovered at least 95% of expected learning outcomes

#### Scenario: A failing partition blocks the parent asset

- **GIVEN** the `2_materials/baml_extraction/leaving_cert_math` asset has a partition-aware `@asset_check`
- **WHEN** the `baml_fidelity_check` returns `passed=False` for the partition `(2026, en, mathematics)`
- **THEN** Dagster marks the parent asset as `failed` for that partition
- **AND** downstream assets in L3 / L4 that depend on that partition are blocked via `AutomationCondition.all_deps_blocked()`

### Requirement: Virtual CocoIndex v1 Assets (L3 Model Lifecycle)
Every CocoIndex v1 App wrapped by `CelticModelLifecycleComponent` SHALL
be emitted as a `is_virtual=True` `@asset` so the LanceDB table mirrors
its upstream (the L1 filesystem scan) automatically. The Component
SHALL enforce the R1–R4 conformance contract
(`oideachais-cocoindex-v1` skill) at scaffold time by calling
`cocoindex_v1_conformance.check_module(module)` BEFORE emitting the
asset. On R1–R4 fail, `dg.Failure` is raised with the exact rule + fix
instructions.

#### Scenario: A developer scaffolds a new L3 v1 App asset

- **WHEN** `dg scaffold defs CelticModelLifecycleComponent apple_photos_metadata --app-name ApplePhotosMetadata --module cianfhoghlaim.cocoindex.apple_photos_metadata --embedding-model BAAI/bge-large-en-v1.5 --hnsw-index` runs
- **THEN** a YAML defs file is created at `defs/3_model_lifecycle/cocoindex_v1/apple_photos_metadata/defs.yaml`
- **AND** `cocoindex_v1_conformance.check_module("cianfhoghlaim.cocoindex.apple_photos_metadata")` returns `passed=True`
- **AND** `dg check yaml` reports the new asset passes
- **AND** `dg list defs` shows `3_model_lifecycle/cocoindex_v1/apple_photos_metadata` with `is_virtual=True`

#### Scenario: A developer tries to scaffold a non-conformant v1 App

- **WHEN** `dg scaffold defs CelticModelLifecycleComponent test_app --module cianfhoghlaim.cocoindex.test_app` runs against a module that fails R2 (no shared_lifespan import)
- **THEN** `dg.Failure` is raised with `R2: no from ._lifespan import shared_lifespan line; add the import to delegate to the canonical lifespan`
- **AND** no YAML defs file is created
- **AND** `dg list defs` does NOT show the failed asset

#### Scenario: A virtual L3 asset resolves through to its L1 upstream

- **GIVEN** the `3_model_lifecycle/cocoindex_v1/leabharlann_books` asset is `is_virtual=True` with `deps=["1_ingestion/filesystem/leabharlann_books"]`
- **WHEN** a new file lands in the leabharlann books directory
- **THEN** the L1 asset materialises (or refreshes its state-backed cache)
- **AND** the L3 virtual asset's `AutomationCondition.eager().resolve_through_virtual()` chain sees the L1 update
- **AND** the L3 virtual asset materialises (which is a no-op for the LanceDB table; the table is updated by the v1 App's `@coco.fn` directly)

### Requirement: Hierarchical Asset Groups (Dagster 1.13+)

Every asset emitted by the 5 KCG Components SHALL use a
hierarchical `group_name` of the form
`"<N>_<layer>/<domain>/<slug>"` where `<N>` is the layer number
(1–5) and `<layer>` is one of {`ingestion`, `materials`,
`model_lifecycle`, `asset_generation`, `agent_ops`}.

Wildcard selection (`group:"1_*"`, `group:"3_model_lifecycle/*"`,
`group:"5_agent_ops/adk"`) SHALL work in the Dagster UI search bar
and via `dg list defs --select`.

#### Scenario: The Dagster UI renders 5 nested groups

- **GIVEN** the 5 KCG Components have emitted 260+ assets across 5 layers
- **WHEN** a developer opens the Dagster UI at `http://localhost:3335`
- **THEN** the asset catalog displays 5 top-level groups: `1_ingestion`, `2_materials`, `3_model_lifecycle`, `4_asset_generation`, `5_agent_ops`
- **AND** each top-level group nests its domain sub-groups (e.g. `1_ingestion/curriculum`, `1_ingestion/law`, `1_ingestion/medicine`)
- **AND** the search bar accepts `group:"3_model_lifecycle/*"` and returns the 17+ L3 assets

#### Scenario: `dg list defs --select` filters by hierarchical group

- **WHEN** `dg list defs --select "group:5_agent_ops/adk"` runs
- **THEN** the output includes only the 40 L5 ADK assets (8 agents × 5 emitted assets per agent)
- **AND** the output excludes L5 custom + agno assets

### Requirement: Declarative Automation Replaces @schedule

The system SHALL NOT use `@schedule` after this change lands. Every
asset's automation SHALL be expressed via `AutomationCondition`
operators (`eager()`, `cron(...)`, `in_progress()`,
`any_deps_updated()`, `all_deps_blocked()`, etc.) on the asset
itself, composed with `.resolve_through_virtual()` for L3
CocoIndex v1 assets.

#### Scenario: A legacy `@schedule` is migrated

- **WHEN** `ccc search "@schedule\(" cianfhoghlaim/dagster/` runs
- **THEN** 0 hits SHALL appear (every `@schedule` is replaced by `AutomationCondition.cron(...)` on the asset)
- **AND** `dg list schedules` returns 0 schedules
- **AND** `dg list defs --json | jq '.[] | select(.automation_condition != null) | .key' | wc -l` returns at least 260

### Requirement: DBT Bridge via Upstream DbtProjectComponent
The 3 dbt-duckdb models SHALL be wired through the upstream
`dagster_dbt.DbtProjectComponent` (NOT a hand-written `@dbt_assets`
decorator + `DbtCliResource`). The 3 models are `weekly_downloads`,
`language_distribution`, and `ocr_confidence_by_model`. The Component
SHALL live at `defs/2_materials/dbt/defs.yaml`. The legacy
`oideachais_dbt_assets` function in `definitions.py` and the
hand-written `_parse_dbt_manifest()` helper SHALL be removed.

#### Scenario: The dbt bridge appears as a single Component

- **WHEN** `dg list defs` runs
- **THEN** 3 new assets appear under `2_materials/dbt/`:
  - `2_materials/dbt/weekly_downloads`
  - `2_materials/dbt/language_distribution`
  - `2_materials/dbt/ocr_confidence_by_model`
- **AND** no hand-written `@dbt_assets` decorator remains in `dagster/`
- **AND** the `DbtProjectComponent` reads the manifest from
  `cianfhoghlaim/dbt_project/target/manifest.json` (refreshed by `dbt parse` on the
  `AutomationCondition.cron("0 6 * * *")` schedule)

## Components

| Component | Path | Purpose |
|-----------|------|---------|
| DLT Sources | `sruth/oideachais/data_platform/dlt_sources/` | Ireland, UK, Celtic, geospatial ingestion |
| Dagster Definitions | `sruth/oideachais/data_platform/dagster_defs/` | Asset orchestration, jobs, schedules, sensors |
| DLT Utils | `sruth/oideachais/data_platform/dlt_utils/` | DuckLake destination config, caching |
| DuckLake Client | `sruth/oideachais/core/storage/clients/ducklake.py` | Postgres catalog + Garage S3 connection |
| LanceDB Cloud | `sruth/oideachais/core/storage/clients/lancedb_cloud.py` | Local/Cloud/Iceberg vector store modes |
| Embedding Service | `sruth/oideachais/embeddings/service.py` | Multi-provider batch embedding |
| BAML Schemas | `baml_src/` | Type-safe LLM extraction schemas |
| OCR Models | `meaisínfhoghlaim/ocr/` | Multi-model comparison (Docling, PaddleOCR, ColPali) |
| ML Training | `sruth/oideachais/training/` | LLM, HTR, TTS training as Dagster assets |
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
| Dagster Definitions | `sruth/oideachais/data_platform/dagster_defs/definitions.py` |
| DLT Utils | `sruth/oideachais/data_platform/dlt_utils/` |
| Storage Config | `sruth/oideachais/core/storage/` |
| Pipeline Ops Guide | `sruth/oideachais/PIPELINE_OPERATIONS.md` |
| PyProject | `sruth/oideachais/pyproject.toml` |

## Related Specs

- [curriculum-ingestion](../curriculum-ingestion/spec.md) — Document processing
- [bilingual-content](../bilingual-content/spec.md) — English/Irish management
- [knowledge-graph](../knowledge-graph/spec.md) — Prerequisite mapping
- [semantic-search](../semantic-search/spec.md) — Vector search
- [assessment-extraction](../assessment-extraction/spec.md) — Exam papers
- [data-pipeline](../data-pipeline/spec.md) — Pipeline patterns

---

## Delta: 2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs

> This section mirrors the spec delta at
> `openspec/changes/2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs/specs/oideachais-pipeline/spec.md`.
> Applied when that change is archived.

### ADDED Requirements

#### Requirement: Consolidated cianfhoghlaim package manifest

The system SHALL expose a single `pyproject.toml` at `cianfhoghlaim/pyproject.toml` declaring the wheel packages, runtime dependencies, optional-dependency groups, and CLI entry-points for the consolidated `cianfhoghlaim` Python package.

The wheel package list SHALL contain exactly the 18 directories that have an `__init__.py` on disk: `agents`, `assets`, `baml`, `browser`, `cocoindex`, `cognify`, `dagster`, `dlt`, `embeddings`, `geospatial`, `leabharlann`, `meaisinfhoghlaim`, `notebooks`, `observability`, `ocr`, `pipelines`, `sources`, `storage`, plus the nested `libraries/codeolas` sub-package.

The system SHALL NOT have any `_quadrant_pyproject.toml` file at the `cianfhoghlaim/` package root. The legacy `_oideachais_pyproject.toml`, `_meaisinfhoghlaim_pyproject.toml`, `_tuatha_pyproject.toml` files SHALL be removed.

##### Scenario: All declared wheel packages resolve to directories with `__init__.py`

- **WHEN** `uv sync && uv run python -c "import cianfhoghlaim.agents, cianfhoghlaim.baml, cianfhoghlaim.cocoindex, cianfhoghlaim.dagster, cianfhoghlaim.dlt, cianfhoghlaim.meaisinfhoghlaim, cianfhoghlaim.observability, cianfhoghlaim.ocr, cianfhoghlaim.notebooks, cianfhoghlaim.geospatial, cianfhoghlaim.storage, cianfhoghlaim.leabharlann"` runs
- **THEN** no `ModuleNotFoundError` is raised
- **AND** all 12 declared wheel packages import cleanly

##### Scenario: All `[project.scripts]` entry-points resolve to real modules

- **WHEN** `uv run cianfhoghlaim --help`, `uv run cianfhoghlaim-ocr --help`, `uv run cianfhoghlaim-baml --help`, `uv run cianfhoghlaim-marimo --help`, `uv run cianfhoghlaim-stack-doctor --help`, `uv run cianfhoghlaim-dagster --help`, `uv run cianfhoghlaim-dlt --help`, `uv run cianfhoghlaim-cocoindex --help` run
- **THEN** each command's `--help` is printed without `ModuleNotFoundError`

##### Scenario: No stale `_quadrant_pyproject.toml` files exist

- **WHEN** `ls cianfhoghlaim/_*.toml` runs
- **THEN** no files are listed

### MODIFIED Requirements

#### Requirement: All Python imports inside cianfhoghlaim use the canonical namespace

The system SHALL have zero `from sruth.*` or `from oideachais.*` imports inside `cianfhoghlaim/`, except inside `.archive/` directories (point-in-time snapshots that are not part of the build) or inside `compat.py` build-time helpers.

The legacy `sruth.oideachais.*`, `sruth.meaisinfhoghlaim.*`, `sruth.tuatha.*`, `sruth.shared.*`, `sruth.browser`, and bare `oideachais.*` Python namespaces SHALL NOT be importable at runtime from the consolidated `cianfhoghlaim` package.

##### Scenario: Grep finds zero stale imports in active code

- **WHEN** `grep -rE "from sruth\.|from oideachais\." cianfhoghlaim/ --include='*.py' --exclude-dir=.archive --exclude=compat.py` runs
- **THEN** zero matches are returned

##### Scenario: All Dagster assets resolve

- **WHEN** `mise run dagster:dev` launches and the asset graph is materialised
- **THEN** all 199 assets load successfully (no `ModuleNotFoundError` from `sruth.*` or `oideachais.*` imports inside asset modules)

##### Scenario: All 14 v1 CocoIndex Apps pass the conformance contract

- **WHEN** `mise run upstream:conformance` runs
- **THEN** all 14 v1 CocoIndex Apps (leabharlann_books_embedding, leabharlann_zotero_embedding, leabharlann_takeout_embedding, codebase_indexing, api_indexing, filesystem_indexing, storage_indexing, config_indexing, unified_embedding, code_embeddings, docs_skills_consolidation, culture_heritage_embedding, upstream_blog_monitor, upstream_api_surface) pass the 4-rule conformance contract R1-R4
- **AND** `cocoindex_v1_conformance` reports 14/14 PASS

### REMOVED Requirements

#### Requirement: Standalone sruth-browser import alias at `cianfhoghlaim/browser/`

**Reason**: The standalone browser package was renamed from `infrastructure/stacks/browser/` to `bonneagar/stacks/browser/` during the v4 follow-on (`openspec/changes/archive/2026-06-29-2026-06-29-per-domain-web-app-consolidation/`). The local duplicate at `cianfhoghlaim/browser/` is a stale deprecation stub whose `__init__.py` imports from `cianfhoghlaim.core.browser` — a package that was never created.

**Migration**: All Dagster assets, DLT sources, scripts, and notebooks that previously imported `from cianfhoghlaim.core.browser import BrowserClient` (or similar) MUST update to `from bonneagar.stacks.browser.sruth_browser import BrowserClient` (or via the workspace source alias).
