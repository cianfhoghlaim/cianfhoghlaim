## ADDED Requirements

### Requirement: DLT Sources Use Canonical Declarative APIs
The oideachais data platform SHALL use the canonical `dlt.sources.rest_api`
declarative API for all `api_table` kind sources and the canonical
`dlt.sources.filesystem` declarative API for all `filesystem_csv` and
`filesystem_parquet` kind sources. Hand-rolled `@dlt.source` wrappers that
re-implement the `urllib.request` or `boto3` request flows are forbidden.

#### Scenario: A new api_table source is added to sources.yaml
- **WHEN** a contributor adds a new entry with `kind: api_table` to
  `oideachais/sources.yaml`
- **THEN** the `SourceFactory._build_api_table_source` method
  resolves the YAML to a `rest_api_source(config)` call where `config`
  is built from the YAML's `pagination` + `urls` fields
- **AND** the source is materialisable through the `dlt.pipeline(...)` +
  `safe_dlt_run(pipeline, source)` pattern

#### Scenario: A new filesystem_parquet source is added
- **WHEN** a contributor adds a new entry with
  `kind: filesystem_parquet` to `oideachais/sources.yaml`
- **THEN** the `SourceFactory._build_filesystem_parquet_source` method
  resolves the YAML to a `filesystem(bucket_url, file_glob) | read_parquet()`
  pipeline

### Requirement: DLT 1.0 Safety Helpers
The `oideachais/dlt_utils/safety.py` module SHALL export two
helper functions in addition to `safe_dlt_run`:
- `safe_dlt_run_with_progress(pipeline, source)` that streams
  package progress.
- `validate_source_kwargs(source, **kwargs)` that catches the
  4 common dlt 1.0 mistakes: missing `name`, missing
  `primary_key` on incremental, no `write_disposition`,
  `merge` without `primary_key`.

#### Scenario: A pipeline uses merge without a primary key
- **WHEN** a `safe_dlt_run_with_progress` call runs a source
  with `write_disposition="merge"` and no `primary_key`
- **THEN** the function raises a `ValueError` with a clear
  message identifying the missing `primary_key` field

### Requirement: Dagster dg CLI Components
The oideachais data platform SHALL expose its Dagster assets through
the `dg` CLI Components pattern. The 3 KCG-specific components
(`CelticDltSourceComponent`, `CelticLancedbHnswComponent`,
`CelticCocoindexV1Component`) SHALL be importable from
`oideachais.dagster_defs.components` and SHALL be discoverable via
`dg list components`.

#### Scenario: A developer runs `dg list components`
- **WHEN** a developer runs `uv run --package oideachais dg list components`
  from the repo root
- **THEN** the output includes `CelticDltSourceComponent`,
  `CelticLancedbHnswComponent`, and `CelticCocoindexV1Component`

#### Scenario: A developer runs `dg list defs`
- **WHEN** a developer runs `uv run --package oideachais dg list defs`
- **THEN** the output includes all 120+ assets registered
  through the new `defs.yaml` mount point

### Requirement: DuckLake 1.0 Features
The oideachais DuckLake destination SHALL be created with the
DuckLake 1.0 spec. Every new table SHALL be created with
`data_inlining_row_limit=100` (the 1.0 default). The 4
highest-volume tables (the marimo `weekly_downloads`,
`language_distribution`, `ocr_confidence_by_model`, and the
leabharlann `*_raw` tables) SHALL be `SORTED BY (id)`. The 3
largest fact tables (leabharlann zotero, takeout, cocoindex)
SHALL be `PARTITIONED BY (bucket(1000, id))`.

#### Scenario: A new dlt pipeline writes to DuckLake
- **WHEN** `dlt.pipeline(destination=get_dlt_destination()).run(source)`
  is called
- **THEN** the destination uses the DuckLake 1.0 spec with
  `data_inlining_row_limit=100` set on every created table

#### Scenario: The weekly_downloads table is materialised
- **WHEN** the `weekly_downloads` dbt model materialises
- **THEN** the underlying DuckLake table has `SORTED BY (id)`
  set (verified by querying the `ducklake_sort_orders` table)

### Requirement: MotherDuck Hosting Options
The `oideachais/dlt_utils/destinations.py` module SHALL support the
3 MotherDuck hosting options (managed / BYOB / BYOC) via the
`MOTHERDUCK_MODE` env var. The default SHALL be `byob` (the
"bring-your-own-bucket" sweet spot per the MotherDuck 2026-04-13
launch post).

#### Scenario: A pipeline runs with MOTHERDUCK_MODE=managed
- **WHEN** `MOTHERDUCK_MODE=managed` is set
- **THEN** `get_dlt_destination()` returns a destination backed
  by the MotherDuck catalog + MotherDuck storage + MotherDuck
  compute

#### Scenario: A pipeline runs with MOTHERDUCK_MODE=byob
- **WHEN** `MOTHERDUCK_MODE=byob` is set
- **THEN** `get_dlt_destination()` returns a destination backed
  by the MotherDuck catalog + self-hosted S3 (the lakehouse
  Garage stack) + MotherDuck compute

### Requirement: LanceDB HNSW Indexes
The system SHALL build an HNSW index on the `vector` column of
every LanceDB table created by the leabharlann full-stack demo
at materialisation time. The 3 helper functions in
`oideachais.lancedb.indexing` (`build_hnsw_index`,
`build_ivf_pq_index`, `optimize_index`) MUST be importable
and MUST follow the canonical 2026-06 LanceDB 0.15 API.

#### Scenario: The leabharlann_books table is materialised
- **WHEN** the `leabharlann_books_app` v1 CocoIndex App
  materialises
- **THEN** `build_hnsw_index(table, column="vector")` is called
  on the resulting LanceDB table
- **AND** the HNSW index has `ef_construction=100` and `M=16`
  (the defaults recommended by the LanceDB 10B-scale blog)

### Requirement: Graphiti 0.5 + FalkorDB 1.0
The system SHALL use the real `graphiti_core` 0.5 client
backed by the FalkorDB compose stack in
`oideachais/cognee_integration/cross_stage_cognify.py`. The
hand-rolled `oideachais/graph/temporal.py` implementation
MUST be deleted.

#### Scenario: The cross_stage_cognify pipeline runs
- **WHEN** the `cross_stage_cognify` Dagster asset materialises
- **THEN** it calls `graphiti_client.add_episode()` to persist
  the 8 cross-stage edges to the FalkorDB graph
- **AND** the edges are queryable via a Cypher query against
  the `falkordb.cianfhoghlaim.ie:6379` endpoint

#### Scenario: A developer runs locally without the FalkorDB stack
- **WHEN** the `falkordb.cianfhoghlaim.ie` compose stack is
  unreachable
- **THEN** the `graphiti_client` falls back to the
  `FalkorDBLite` embedded mode (the `falkordb_lite` Python
  package introduced in 2026-05)

### Requirement: CocoIndex v1 Apps Only
Every CocoIndex flow in `oideachais/cocoindex_flows/` SHALL be
a v1 App using the canonical `@coco.fn` + `@coco.lifespan` +
`lancedb.mount_table_target()` pattern. The shared
`oideachais/cocoindex_flows/_lifespan.py` module SHALL export
the shared `@coco.lifespan` and the 3 ContextKeys
(RESOLVED_FILE_REGISTRY, EMBEDDER, LANCE_DB).

#### Scenario: A new CocoIndex flow is added
- **WHEN** a contributor adds a new file to
  `oideachais/cocoindex_flows/`
- **THEN** the file imports the shared `@coco.lifespan` and
  3 ContextKeys from `oideachais.cocoindex_flows._lifespan`
  rather than re-declaring them
- **AND** the file uses `@coco.fn` and
  `lancedb.mount_table_target()` (no v0 `FlowBuilder` API)

## MODIFIED Requirements

### Requirement: Celtic Education Lakehouse Pipeline
The oideachais data platform SHALL be organised as a Celtic
education lakehouse with dlt ingestion, Dagster orchestration,
BAML extraction, CocoIndex v1 embedding, and Cognee cognify.
The directory structure SHALL follow the
`cross-domain-registry` contract: dlt sources for the
education domain live in
`oideachais/dlt_sources/domains/education/{nation}/{source}.py`.

#### Scenario: A contributor adds a new education source for a UK nation
- **WHEN** a contributor adds a new education source for England
- **THEN** the file is created at
  `oideachais/dlt_sources/domains/education/en/{source}.py`
- **AND** the legacy `oideachais/dlt_sources/uk/england/{source}.py`
  is NOT used

#### Scenario: A contributor adds a Dagster asset
- **WHEN** a contributor adds a new Dagster asset
- **THEN** the asset is registered through a `dg.Component`
  (the new `dg` CLI pattern) or through a `.py` file in
  `oideachais/dagster_defs/assets/`
- **AND** the asset is discoverable via `dg list defs`

### Requirement: Source Factory
The oideachais data platform SHALL expose a `SourceFactory`
class in `oideachais/dlt_utils/source_factory.py` that reads
`oideachais/sources.yaml` and produces 7 contract methods:
`source(id)`, `dlt_asset(id)`, `dagster_asset(id)`,
`lance_table(id)`, `cognee_dataset(id)`, `marimo_path(id)`,
`tests_path(id)`.

#### Scenario: A developer wants to materialise a single source
- **WHEN** a developer calls
  `SourceFactory.from_yaml('oideachais/sources.yaml').dlt_asset('ie.education.ncca')`
- **THEN** the returned asset runs the canonical DLT source
  and materialises it to the configured DuckLake destination
- **AND** the asset is registered in the Dagster definitions
  (via `dg.load_from_defs_folder()` or the legacy
  `Definitions(assets=...)`)

### Requirement: Destination Factory
The oideachais data platform SHALL expose a
`get_dlt_destination()` function in
`oideachais/dlt_utils/destinations.py` that returns a
DuckLake destination configured for the local development
environment (Garage S3 + Lakekeeper Postgres catalog).

#### Scenario: A pipeline runs locally with the lakehouse stack
- **WHEN** `get_dlt_destination()` is called with no arguments
  and the lakehouse stack is reachable at
  `http://localhost:3900` (Garage) and `localhost:5433`
  (Postgres)
- **THEN** the destination uses the DuckLake 1.0 spec with
  `data_inlining_row_limit=100`
- **AND** the catalog is the Lakekeeper Postgres database
- **AND** the storage is the Garage S3 bucket

## REMOVED Requirements

### Requirement: Hand-Rolled Temporal Knowledge Graph
**Reason**: Replaced by the real `graphiti_core` 0.5 client
backed by the FalkorDB compose stack.
**Migration**: Delete `oideachais/graph/temporal.py`. Update
`oideachais/cognee_integration/cross_stage_cognify.py` to use
`oideachais.graph.graphiti_client`.

### Requirement: CocoIndex v0 DSL
**Reason**: CocoIndex 1.0.9 (the v1 API) is on the venv; the
v0 DSL (`@cocoindex.flow_def`, `FlowBuilder`, `DataScope`)
is removed. All v0 flows MUST be migrated to v1.
**Migration**: Use the canonical v1 pattern in
`oideachais/cocoindex_flows/leabharlann_embedding.py`. The
shared `@coco.lifespan` is in
`oideachais/cocoindex_flows/_lifespan.py`.
