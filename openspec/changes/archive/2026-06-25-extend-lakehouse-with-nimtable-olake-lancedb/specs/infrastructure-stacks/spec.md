## MODIFIED Requirements

### Requirement: Storage Stacks

The system SHALL deploy database and data infrastructure for the lakehouse architecture. The dev lakehouse stack MUST extend the canonical Garage + Postgres + Lakekeeper + Lance Namespace sidecar foundation with an Iceberg catalog UI, a CDC ingestion engine, and a LanceDB table viewer. Every active srutha MUST be wired into the lakehouse via the canonical cross-sruth contract documented in the `Cross-Sruth Lakehouse Wiring Contract` requirement below.

#### Scenario: Lakehouse Stack

- **GIVEN** lakehouse stack with Garage S3, Postgres, Lakekeeper, and Lance Namespace sidecar
- **WHEN** stack deploys via Komodo
- **THEN** S3 API (3900), Postgres (5433), Iceberg REST catalog (8181), and Lance sidecar (8182) are accessible

#### Scenario: Lakehouse Iceberg Catalog UI

- **GIVEN** the Nimtable service appended to `infrastructure/stacks/lakehouse/compose.yaml`
- **WHEN** the lakehouse stack deploys
- **THEN** Nimtable is accessible at `http://localhost:3018` and `https://nimtable.cianfhoghlaim.ie` (via Pangolin)
- **AND** Nimtable connects to the shared Postgres at `jdbc:postgresql://postgres:5432/nimtable` and surfaces all Iceberg tables registered in Lakekeeper
- **AND** the `nimtable` service resource usage is capped at `cpus: '1'`, `memory: 512M` per service

#### Scenario: Lakehouse CDC Engine (Olake)

- **GIVEN** the Olake service appended to `infrastructure/stacks/lakehouse/compose.yaml`
- **WHEN** the lakehouse stack deploys
- **THEN** Olake is reachable via `https://olake.cianfhoghlaim.ie` (admin via `docker exec`) for CDC jobs
- **AND** Olake reads its source/catalog/writer config from `infrastructure/stacks/lakehouse/olake/{config,catalog,writer}.json`
- **AND** Olake persists checkpoint + offset state to the named volume `olake_state` and the Postgres DB `olake_state`
- **AND** the `olake` service resource usage is capped at `cpus: '1'`, `memory: 512M` per service

#### Scenario: Lakehouse LanceDB Viewer

- **GIVEN** the lancedb-viewer service appended to `infrastructure/stacks/lakehouse/compose.yaml`
- **WHEN** the lakehouse stack deploys
- **THEN** the LanceDB viewer is accessible at `http://localhost:8081` and `https://lance-viewer.cianfhoghlaim.ie` (via Pangolin)
- **AND** the viewer connects to the Lance namespace at `rest://lakehouse-lance-namespace:8182`
- **AND** the `lancedb-viewer` service resource usage is capped at `cpus: '0.5'`, `memory: 256M` per service

#### Scenario: AI Memory Stacks

- **GIVEN** Cognee and Graphiti stacks
- **WHEN** stacks deploy
- **THEN** knowledge graph and temporal memory services are available

#### Scenario: Vector Database Stacks

- **GIVEN** LanceDB, Qdrant, and FalkorDB stacks
- **WHEN** stacks deploy
- **THEN** vector search infrastructure is accessible

## ADDED Requirements

### Requirement: Cross-Sruth Lakehouse Wiring Contract

Every active srutha in the Cianfhoghlaim monorepo MUST wire into the canonical dev lakehouse via two contracts: (1) `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` for LanceDB vector RAG (set via `.env` or compose.yaml default), and (2) a dedicated `ducklake_{namespace}` PostgreSQL database created in `infrastructure/stacks/lakehouse/init-db.sql` for DuckLake write-ahead-log storage. The canonical factory for both contracts is `sruth/oideachais/dlt_utils/destinations.py:with_namespace()` (the `with_namespace()` method at line 289 of the file). The 6 active srutha DBs are: `ducklake_oideachais`, `ducklake_crypteolas`, `ducklake_croilar`, `ducklake_tuath`, `ducklake_meaisinfhoghlaim`, `ducklake_aleyum` (legacy — superseded by croilar).

#### Scenario: An active srutha needs LanceDB vector RAG

- **GIVEN** an active srutha stack (e.g. `croilar-dagster`, `croilar-marimo`, `oideachais`)
- **WHEN** the stack boots
- **THEN** its `LANCEDB_URI` env var MUST default to `rest://lakehouse-lance-namespace:8182`
- **AND** the default MUST be overridable via `.env` for legacy file-path deployments
- **AND** the stack MUST be on the `lakehouse` external network so it can reach the Lance sidecar at `:8182`

#### Scenario: An active srutha needs DuckLake storage

- **GIVEN** an active srutha (e.g. `oideachais`, `croilar`, `crypteolas`, `tuath`, `meaisinfhoghlaim`)
- **WHEN** its Dagster code-location runs `with_namespace()` to materialise a DuckLake destination
- **THEN** the factory MUST produce a connection string referencing `ducklake_{namespace}` on the shared `lakehouse-postgres`
- **AND** the database MUST exist in `infrastructure/stacks/lakehouse/init-db.sql` with `OWNER lakehouse`
- **AND** if the database is missing, the `with_namespace()` factory MUST raise an actionable error pointing at the lakehouse `init-db.sql` file

#### Scenario: meaisinfhoghlaim is wired into the lakehouse

- **GIVEN** the `meaisinfhoghlaim` srutha has a Dagster code-location but historically had no `ducklake_*` database
- **WHEN** the lakehouse `init-db.sql` runs on a fresh `docker compose up`
- **THEN** the `ducklake_meaisinfhoghlaim` database MUST be created with `OWNER lakehouse` and `GRANT ALL PRIVILEGES`
- **AND** the `meaisinfhoghlaim` Dagster assets MUST be able to materialise to `with_namespace("meaisinfhoghlaim")` on the shared Postgres without manual DB creation

#### Scenario: The standalone olake/ and nimtable/ stacks are deprecated

- **GIVEN** the standalone `infrastructure/stacks/olake/` and `infrastructure/stacks/nimtable/` Compose stacks predate this change
- **WHEN** a contributor searches for the canonical Olake or Nimtable location
- **THEN** each stack directory MUST contain a `DEPRECATED.md` file pointing at the canonical location (`infrastructure/stacks/lakehouse/olake/` and the `nimtable` service inside `infrastructure/stacks/lakehouse/compose.yaml`)
- **AND** the `compose.yaml` files MUST remain on disk (not deleted) to avoid breaking any automated tests that import from them; deletion is left to a follow-up change after one release cycle
