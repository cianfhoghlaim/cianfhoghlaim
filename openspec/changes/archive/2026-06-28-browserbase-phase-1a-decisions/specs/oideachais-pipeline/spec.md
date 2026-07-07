# oideachais-pipeline (delta: Phase 1A research findings)

> Filled by Phase 1A research agent (5/5 prompts complete).
> See `openspec/research/2026-06-28-browserbase-credit-program/phase-1a/`.

## ADDED Requirements

### Requirement: minimax alias is the canonical LiteLLM default

The system SHALL route every default-model LiteLLM request through the
`minimax` alias, which contains a 7-tier fallback chain
(`opencode-go/minimax-m3-slot0`, `slot1`, `slot2`,
`opencode-go/qwen3.7-max`, `opencode-go/kimi-k2.6`,
`openai/glm-4.6`, `local/math/qwen25-math`).

#### Scenario: minimax alias fallback chain

- **GIVEN** the LiteLLM gateway is running with the canonical config
- **WHEN** a request hits `minimax` and the first slot returns 429
- **THEN** LiteLLM's `num_retries: 3` cycles to the next entry in the
  fallback chain
- **AND** the original 429 is recorded in Langfuse with
  `metadata.fallback_triggered = true`

### Requirement: Lakehouse uses Iceberg format on Garage S3 via Lakekeeper catalog

The system SHALL store all lakehouse tabular data as Iceberg tables on
Garage S3 (`s3://lakehouse-bucket/iceberg/`) with Lakekeeper (port 8181)
as the Iceberg REST catalog, backed by PlanetScale Postgres
(`lakehouse_catalog` database).

#### Scenario: Iceberg ACID writes

- **GIVEN** the dlt pipeline writes to a lakehouse dataset
- **WHEN** a write completes
- **THEN** the Iceberg catalog creates a new snapshot
- **AND** subsequent reads can time-travel to the snapshot via
  `lakehouse.dataset TIMESTAMP AS OF ...`

### Requirement: DuckLake 1.0 is the canonical SQL interface (Wave 2 verified)

The system SHALL use **DuckLake 1.0** (stable 2026-04-13) as the
canonical SQL interface, available as a DuckDB **core extension**
(`INSTALL ducklake; LOAD ducklake;`). The
`ATTACH 'ducklake:postgres:dbname=lakehouse_catalog ...'` (Postgres
catalog) pattern is canonical for KCG.

#### Scenario: DuckLake 1.0 attach + Iceberg storage

- **GIVEN** a DuckDB Python client with the `ducklake` core extension
- **WHEN** the client runs
  `ATTACH 'ducklake:postgres:dbname=lakehouse_catalog host=lakehouse-postgres' AS lakehouse (DATA_PATH 's3://lakehouse-bucket/ducklake/')`
- **THEN** the query reads from Iceberg Parquet on Garage S3 via the
  DuckLake catalog
- **AND** time-travel queries
  (`SELECT * FROM lakehouse.curriculum AT (TIMESTAMP => ...)`) work
  natively

### Requirement: MotherDuck is the canonical cross-host query layer

The system SHALL use MotherDuck as the canonical cross-host query layer
for Dives (live dashboards) + cross-org data sharing.

#### Scenario: MotherDuck Dive

- **GIVEN** a MotherDuck Dive definition
- **WHEN** the Dive is opened in a browser
- **THEN** the query runs on MotherDuck compute
- **AND** reads from the same Iceberg catalog as local DuckDB

### Requirement: Dagster is the canonical orchestration layer with MultiPartitionsDefinition for exams

The system SHALL use Dagster as the canonical orchestration layer with
`MultiPartitionsDefinition(subject, material_type)` for the examinations
asset (96 partitions = 24 subjects × 4 material types).

#### Scenario: Exam partition materialization

- **GIVEN** a Dagster `@asset` with `MultiPartitionsDefinition`
- **WHEN** the asset materializes a single (subject, material_type) partition
- **THEN** it runs the dlt pipeline scoped to that partition
- **AND** the result is materialized as Iceberg Parquet in the lakehouse

### Requirement: CocoIndex v1 App is the canonical code search index

The system SHALL use CocoIndex v1 `coco.App` + `@coco.fn` + `ContextKey` +
`mount_table_target` pattern for all code/document embeddings,
mounted to LanceDB HNSW tables.

#### Scenario: CocoIndex v1 App mount

- **GIVEN** a `coco.App` class with `@coco.fn` decorators
- **WHEN** `cocoindex update <module>:<AppClass>` runs
- **THEN** the App indexes files into LanceDB via `mount_table_target`
- **AND** the resulting HNSW table is queryable via the `cocoindex-code` MCP

### Requirement: dlt 1.28.1 with `[hub]` extra is the canonical install (Wave 2 drift fix)

The system SHALL pin `dlt[hub]>=1.27.0,<2.0.0` in
`cianfhoghlaim/pyproject.toml` (the 1.27 `workspace` split moved
`dlt dashboard` / `dlt pipeline show` out of the base wheel on
2026-05-19) and SHALL upgrade the lock to **dlt 1.28.1** (2026-06-19)
to pick up the `replace` snapshot fix and Lance destination write
optimisations. dlt sources SHALL yield native Polars `LazyFrame` from
`@dlt.resource` to enable lazy column-projection + filter pushdown.

#### Scenario: dlt[hub] is required for `dlt pipeline show`

- **GIVEN** `pyproject.toml` currently pins plain `dlt>=1.0.0`
  (missing `[hub]`)
- **WHEN** a developer runs `dlt pipeline curriculum show` on a laptop
- **THEN** the CLI raises `ModuleNotFoundError: dlthub` (per release
  notes 1.27.0 §Breaking Changes)
- **AND** the fix is to change the pin to `dlt[hub]>=1.27.0,<2.0.0`
- **AND** re-running `dlt pipeline curriculum show` then opens the
  Marimo dashboard at `localhost`

### Requirement: Dagster @dlt_assets + asset_check is the canonical ingestion wrapper (Wave 2)

The system SHALL wrap every dlt source in a Dagster `@dlt_assets`
definition (per `dagster-dlt`'s `build_dlt_asset_specs` +
`DagsterDltTranslator`), expose its 6 resource tables as 6 Dagster
asset keys, and attach `asset_check` (row-count ≥ 1) and
`asset_observation` (schema-drift) to every asset so freshness and
quality are first-class Dagster objects.

#### Scenario: dlt_assets + asset_check

- **GIVEN** the `curriculumonline_primary` dlt source declares 6
  resources (curriculum_area, subject, learning_outcome,
  content_objective, assessment, glossary)
- **WHEN** the `@dlt_assets(dlt_source=curriculumonline_primary())` def
  materialises
- **THEN** Dagster emits 6 asset keys
  `lakehouse.curriculumonline_primary.{curriculum_area,…,glossary}`
- **AND** each gets a row-count `asset_check` that fails the asset if
  0 rows are produced

### Requirement: LanceDB IVF_HNSW_SQ is the canonical vector index (Wave 2 drift fix)

The system SHALL use **`IVF_HNSW_SQ`** as the default vector index for
all LanceDB tables created via the `mount_table_target` path
(supersedes the P1B-06 standalone HNSW config — HNSW is a **sub-index**
inside IVF partitions in LanceDB v0.33+, not a top-level type). For
large tables (>1 M rows) the system SHALL use `IVF_PQ` (or `IVF_RQ`
when `dim <= 256`).

#### Scenario: IVF_HNSW_SQ build

- **GIVEN** a LanceDB `codebase_chunks` table with 50,000 rows and
  1024-dim BGE-M3 embeddings
- **WHEN** `table.create_index("vector", config=IvfHnswSq(
  num_partitions=4, metric="cosine", ef_construction=150))` runs
- **THEN** LanceDB builds an IVF_HNSW_SQ index (HNSW sub-graph inside
  4 IVF partitions + scalar quantisation)
- **AND** recall@10 ≥ 0.95 at p50 latency ≤ 200 ms

### Requirement: Lakekeeper v0.12.4 is the canonical Iceberg REST catalog (Wave 2 verified)

The system SHALL pin **Lakekeeper v0.12.4** (released 2026-06-17) as
the canonical Iceberg REST catalog on port 8181, picking up the
v0.12.0 Idempotency Keys + V3 Variant datatype + OPA batch
optimisation features. The canonical GitHub org is
`lakekeeper/lakekeeper` (the historical `treeverse/lakekeeper` URL
now 404s).

#### Scenario: DuckDB `iceberg` core extension reads Iceberg via Lakekeeper

- **GIVEN** Lakekeeper is running at `http://lakekeeper:8181` v0.12.4
- **WHEN** a dlt pipeline writes to
  `s3://lakehouse-bucket/iceberg/curriculum/`
- **THEN** Lakekeeper creates a new Iceberg snapshot
- **AND** a DuckDB client can read it via the `iceberg` core
  extension: `SELECT * FROM iceberg_scan(
  's3://lakehouse-bucket/iceberg/curriculum/', snapshot_version => 42)`

### Requirement: MotherDuck mcp-server-motherduck is the canonical agent-side SQL surface

The system SHALL expose the `mcp-server-motherduck` MCP server
(`uvx mcp-server-motherduck --db-path :memory: --read-write
--allow-switch-databases`) as the canonical SQL tool surface for every
OpenCode / Claude Code / Cursor / Copilot Studio agent that needs to
query the lakehouse, registered in `opencode.json` under the
`motherduck` MCP key.

#### Scenario: Agent queries MotherDuck via MCP

- **GIVEN** an OpenCode subagent has the `motherduck` MCP enabled
- **WHEN** the agent calls `mcp__motherduck__query("SELECT count(*) FROM
  oideachais.curriculum")`
- **THEN** the MCP server routes the query to MotherDuck cloud
- **AND** returns a DuckDB `RecordBatchReader` the agent can consume
  as Arrow / Polars / pandas
