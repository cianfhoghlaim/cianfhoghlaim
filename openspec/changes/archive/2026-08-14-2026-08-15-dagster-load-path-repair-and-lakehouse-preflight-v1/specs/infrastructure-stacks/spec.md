## ADDED Requirements

### Requirement: `mise run lakehouse:preflight` task exists

The system SHALL provide a `mise run lakehouse:preflight` task that
probes the 5 required lakehouse endpoints + the 12 postgres databases
+ the 8 Garage buckets + the (graceful) cognify stack status.

The 5 required endpoints (all must respond 200):

- Nimtable (Spring Boot Iceberg catalog UI) → `http://localhost:3018/`
- Olake (CDC engine) → `http://localhost:3901/health`
- LanceDB Viewer (Lance table viewer) → `http://localhost:8081/healthz`
- Lance sidecar (Lance namespace) → `http://localhost:8182/health`
- Lakekeeper (REST catalog) → `http://localhost:8181/health`

The 12 postgres databases (created by `init-db.sql`):

- `ducklake_cianfhoghlaim`, `ducklake_crypteolas`, `ducklake_aleyum`, `ducklake_croilar`, `ducklake_tuath`, `ducklake_meaisinfhoghlaim`
- `dagster_local`, `olake_state`, `nimtable`
- `langfuse`, `mlflow`, `litellm`

The 8 Garage buckets (created by `garage-init`):

- `iceberg`, `lance`, `ducklake`, `ducklake-cianfhoghlaim`
- `langfuse-events`, `langfuse-media`, `langfuse-exports`
- `mlflow-artifacts`

The cognify stack (cognee + graphiti + falkordb + lancedb + memgraph)
is OPTIONAL — the preflight probes it but reports `skipped` rather
than failing when the cognify stack is intentionally not deployed.

#### Scenario: The preflight succeeds when the lakehouse is healthy

- **WHEN** `mise run lakehouse:preflight` runs on a fresh `docker compose up -d lakehouse`
- **THEN** the script probes the 5 required endpoints + the 12 databases + the 8 buckets
- **AND** exits 0 with a summary table per probe
- **AND** the cognify stack section reports `skipped` (when not deployed)

#### Scenario: The preflight fails when a required endpoint is down

- **WHEN** the Olake service is down (returns 502)
- **THEN** the preflight exits 1 with an actionable error: "Olake CDC engine unreachable at http://localhost:3901/health — bring up the lakehouse stack via `docker compose -f bonneagar/stacks/lakehouse/compose.yaml -f bonneagar/stacks/lakehouse/sidecar.yaml up -d`"

#### Scenario: The preflight fails when a database is missing

- **WHEN** the `ducklake_<namespace>` database is missing
- **THEN** the preflight exits 1 with an actionable error: "Postgres database `ducklake_meaisinfhoghlaim` is missing — recreate via `init-db.sql`"