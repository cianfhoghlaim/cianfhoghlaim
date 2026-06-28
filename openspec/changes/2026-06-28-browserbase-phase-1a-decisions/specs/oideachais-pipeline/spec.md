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

### Requirement: DuckLake is the canonical SQL interface for lakehouse tables

The system SHALL use DuckLake as the canonical SQL interface, with the
`ATTACH 'ducklake:postgres://lakehouse-postgres:5432/lakehouse_catalog'`
syntax for attaching the catalog.

#### Scenario: DuckLake attach + query

- **GIVEN** DuckDB Python client with MotherDuck token
- **WHEN** the client attaches DuckLake + runs a query
- **THEN** the query reads from Iceberg Parquet on Garage S3
- **AND** returns a Polars DataFrame via `pl.from_arrow(...)`

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
