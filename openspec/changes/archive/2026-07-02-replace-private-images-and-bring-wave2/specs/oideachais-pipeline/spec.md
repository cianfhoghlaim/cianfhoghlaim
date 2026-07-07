# Oideachais Pipeline — Wave 2 Lakehouse Integration Delta

> This file is the change-side delta for
> `2026-07-02-replace-private-images-and-bring-wave2`. It applies on
> top of the canonical `oideachais-pipeline` spec at
> `../../../../specs/oideachais-pipeline/spec.md` and on top of the
> prior `2026-07-02-bunchloch-stack-bootstrap` delta.

## ADDED Requirements

### Requirement: CocoIndex v1 Apps use lakehouse LANCEDB_URI

The system SHALL configure the 14 CocoIndex v1 Apps to use the
lakehouse-lance-namespace as the LANCEDB target, not the production
endpoint `rest://lance-api.cianfhoghlaim.ie`. The
`LANCEDB_URI` env var default in `cocoindex/_lifespan.py` SHALL be
changed to `rest://lakehouse-lance-namespace:8182` (in-cluster DNS)
or `rest://127.0.0.1:8182` (on-host dagster dev).

#### Scenario: CocoIndex lifespan connects to lakehouse
- **WHEN** any of the 14 v1 Apps starts (e.g. `codebase_indexing:codebase_app`)
- **THEN** the `coco_lancedb.connect_async(LANCEDB_URI)` call SHALL
  connect to `rest://lakehouse-lance-namespace:8182` (in-cluster) or
  `rest://127.0.0.1:8182` (on-host)
- **AND** the embedder SHALL use the shared `BAAI/bge-large-en-v1.5`
  model with 1024 dims (per the existing canonical config in
  `cocoindex/_lifespan.py:92`)

#### Scenario: LanceDB namespace is the lakehouse one
- **WHEN** CocoIndex writes tables to LanceDB
- **THEN** the tables SHALL land in the lakehouse-managed
  LanceDB instance (Garage-backed, lakekeeper-coordinated via
  the lance-namespace REST adapter)
- **AND** the `lakehouse-lancedb-viewer` UI on `:8082` SHALL be
  able to discover and display the new tables

### Requirement: DLT DuckLake destination uses lakehouse Garage + Postgres

The system SHALL configure DLT DuckLake destinations to use the
lakehouse infrastructure (Garage S3 + lakehouse-postgres catalog)
for dev mode. The `_build_local_destination(namespace)` function
in `dlt/common/destinations_oideachais.py` SHALL use:
- Postgres: `lakehouse-postgres:5432` (in-cluster) or
  `localhost:5433` (on-host)
- S3: Garage at `localhost:3900` (on-host) or `lakehouse-garage:3900`
  (in-cluster)
- Credentials: from `.env.dev` via the
  `_resolve_aws_credentials()` helper in Change 8 (which maps
  `GARGE_*` → `AWS_*`)

#### Scenario: DLT writes to lakehouse
- **WHEN** a DLT pipeline materialises (e.g.
  `oideachais/notebooks/analysis_plan/aistear.md` triggers an NCCA
  ingestion via `create_pipeline('ncca_aistear', 'aistear')`)
- **THEN** the Parquet files SHALL land in
  `s3://ducklake/oideachais/<table_name>/` (Garage-backed)
- **AND** the catalog metadata SHALL be stored in
  `postgresql://lakekeeper:devpassword@lakehouse-postgres:5432/ducklake_oideachais`
- **AND** the 8 high-volume tables (per `ducklake_options.SORTED_BY_TABLES`)
  SHALL be `SORTED BY (id)` and the 3 largest fact tables
  (per `BUCKET_PARTITIONED_TABLES`) SHALL be
  `PARTITIONED BY (bucket(1000, id))`

#### Scenario: DLT fallback to plain DuckDB
- **WHEN** `USE_DUCKLAKE=false` (or the lakehouse is not running)
- **THEN** DLT SHALL use the plain DuckDB fallback at
  `./data/oideachais.duckdb` (per `get_duckdb_fallback_destination`)

### Requirement: Marimo notebooks connect to lakehouse destinations

The system SHALL configure the 11 marimo notebooks in
`cianfhoghlaim/notebooks/dashboards/` to connect to the lakehouse
destinations (not the local file system defaults). The
`bonneagar/stacks/marimo/.env.dev` SHALL provide:
- `DUCKLAKE_POSTGRES_HOST=lakehouse-postgres`
- `AWS_ENDPOINT_URL=http://lakehouse-garage:3900`
- `LANCEDB_URI=rest://lakehouse-lance-namespace:8182`
- `OTEL_EXPORTER_OTLP_ENDPOINT=http://logfire:4317`

#### Scenario: Static notebooks (8) wired to live data
- **WHEN** the user opens any of the 8 stage/cross-domain notebooks
  (`aistear.py`, `primary.py`, `junior_cycle.py`, `senior_cycle.py`,
  `tertiary.py`, `cross_domain.py`, `leabharlann_full_stack_demo.py`,
  `email_inbox_triage.py`)
- **THEN** the notebook SHALL query the corresponding Cognee dataset
  (e.g. `oideachais.aistear` for `aistear.py`) or LanceDB table
  (e.g. `aistear_knowledge_graph`) or lakehouse-postgres table
  (e.g. `oideachais_inbox_messages` for `email_inbox_triage.py`)
- **AND** the query SHALL return real data (not the hardcoded
  dataframe defaults)

#### Scenario: 4 lakehouse notebooks (already in `duckdb/` subdir)
- **WHEN** the user opens `cocoindex_embedding_coverage.py`,
  `dlt_pipeline_overview.py`, `ducklake_explorer.py`, or
  `lakehouse_inspector.py`
- **THEN** the notebook SHALL query the lakehouse DuckLake
  catalog via DuckDB-ATTACH (or a direct PG connection) and
  return live DLT-pipeline metadata
- **AND** the marimo container SHALL reach the lakehouse services
  via the `cianfhoghlaim` external docker network

### Requirement: Dagster code location loads 5 KCG Components

The system SHALL configure the dagster image so that
`DAGSTER_HOME=/opt/dagster/home` is set, with the
`dagster-webserver` (port 3000 inside container, 3335 on host) and
`dagster-daemon` (background) services both running. The
`DAGSTER_HOME` directory SHALL be persisted as a named volume so
the run history survives restarts.

#### Scenario: Dagster dev server boots
- **WHEN** an operator runs `./scripts/stack.sh dagster up -d` (or
  the docker compose equivalent) using the `dagster-local:latest`
  image
- **THEN** the `dagster` container SHALL start on `:3335` (host)
  → `:3000` (container)
- **AND** the `dagster-daemon` container SHALL start in the
  background, polling for schedules + sensors
- **AND** `curl :3335/server_info` SHALL return HTTP 200 + JSON

#### Scenario: Dagster code location loads 5 KCG Components
- **WHEN** `dagster dev -m cianfhoghlaim.dagster.definitions` is
  invoked (either in the container or on host with the
  `DAGSTER_HOME=./` env var)
- **THEN** the Definitions object SHALL load the 5 KCG Components
  (L1 CelticIngestionComponent, L2 CelticMaterialsComponent,
  L3 CelticModelLifecycleComponent, L4 CelticAssetGenerationComponent,
  L5 CelticAgentOpsComponent) per the 5-layer Component architecture
- **AND** the assets from the legacy 6-sub-folder shape
  (`defs/{oideachais_pipeline, celtic_asset_generation, cognify,
  croilar, meaisinfhoghlaim_platform, tuatha}`) SHALL be merged in
  via the `dg.load_from_defs_folder()` legacy merge

### Requirement: BAML clients use litellm + llama-swap gateways

The system SHALL configure the 11 BAML clients (7 in
`baml/clients.baml` + 4 in `baml/clients_llama_swap.baml`) to use
the litellm gateway and llama-swap as their `base_url`. The
hardcoded `http://localhost:4000/v1` and `http://llama-swap:8080/v1`
references SHALL be replaced with `env.LITELLM_BASE_URL` and
`env.LLAMASWAP_BASE_URL` respectively (the code-side env var
substitution happens in Change 8).

#### Scenario: BAML LLM call routes through litellm
- **WHEN** a BAML function (e.g. `ExtractMarkingScheme`) is invoked
- **THEN** the BAML client SHALL POST to
  `env.LITELLM_BASE_URL/v1/chat/completions` (default:
  `http://localhost:4000/v1`)
- **AND** the `OPENAI_API_KEY` env var SHALL be the litellm master
  key (`sk-1234` per the litellm compose `LITELLM_MASTER_KEY`)

#### Scenario: BAML LlamaSwap call routes to local GGUFs
- **WHEN** a BAML function uses the `LlamaSwapClient` (or one of
  the 4 LlamaSwap* aliases)
- **THEN** the BAML client SHALL POST to
  `env.LLAMASWAP_BASE_URL/v1/chat/completions` (default:
  `http://llama-swap:8080/v1` inside docker network)
- **AND** the `LLAMASWAP_API_KEY` env var SHALL be the llama-swap
  master key (per the llama-swap compose)

### Requirement: GARAGE_* → AWS_* credential translation

The system SHALL translate `GARAGE_*` env vars (the lakehouse's
canonical naming for S3 credentials) to `AWS_*` env vars (the
naming expected by DLT, MLflow, BAML) at the application layer
via a `_resolve_aws_credentials()` helper in
`dlt/common/destinations_oideachais.py`. The translation maps:
- `GARAGE_ACCESS_KEY_ID` → `AWS_ACCESS_KEY_ID`
- `GARAGE_SECRET_ACCESS_KEY` → `AWS_SECRET_ACCESS_KEY`

#### Scenario: DLT reads GARAGE_* env and uses AWS_* internally
- **WHEN** a DLT pipeline starts
- **THEN** the `_resolve_aws_credentials()` helper SHALL set
  `AWS_ACCESS_KEY_ID` from `GARAGE_ACCESS_KEY_ID` (if not already set)
- **AND** `AWS_SECRET_ACCESS_KEY` SHALL be set from
  `GARAGE_SECRET_ACCESS_KEY`
- **AND** DLT's internal S3 client (boto3) SHALL use the resolved
  `AWS_*` values to authenticate with Garage
