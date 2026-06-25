# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: Dagster DuckLake resource (canonical KCG lakehouse sink)

The system SHALL use the upstream `dagster-ducklake` integration
(`DuckLakeResource` from `docs/dagster/integrations/dagster-ducklake/`)
as the canonical KCG lakehouse sink, with the resource config:

- **Postgres catalog** at `sruth/oideachais/storage/ducklake_client.py`
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

## REMOVED Requirements

(None. The Curriculum Ingestion cross-reference to the 7 oideachais-*
specs + 3 meaisinfhoghlaim-* specs + 1 tuatha spec + 3 croilar-* specs
is preserved; the 5 new requirements above are additive.)
