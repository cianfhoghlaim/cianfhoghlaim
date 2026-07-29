# Spec delta: `infrastructure-stacks`

This delta is part of the openspec change
`2026-08-01-lakehouse-and-reproducible-deploy-v1`. It modifies 2
requirements and adds 3 new requirements that ship the lakehouse
external-network fix + the `deploy:full` orchestrator + the
3 dead-stack deletions.

## MODIFIED Requirements

### Requirement: Cross-Sruth Lakehouse Wiring Contract

MUST declare the lakehouse external network with matching identifiers.
Every active srutha in the Cianfhoghlaim monorepo MUST wire into the
canonical dev lakehouse via two contracts:

1. **`LANCEDB_URI=rest://lakehouse-lance-namespace:8182`** for
   LanceDB vector RAG (set via `.env` or compose.yaml default).
2. **A dedicated `ducklake_{namespace}` PostgreSQL database** created
   in `bonneagar/stacks/lakehouse/init-db.sql` for DuckLake
   write-ahead-log storage.

The canonical factory for both contracts is
`cianfhoghlaim/dlt_utils/destinations.py:with_namespace()` (the
`with_namespace()` method at line 289 of the file). The 6 active
srutha DBs are: `ducklake_oideachais`, `ducklake_crypteolas`,
`ducklake_croilar`, `ducklake_tuath`, `ducklake_meaisinfhoghlaim`,
`ducklake_aleyum` (legacy — superseded by croilar).

The lakehouse stack MUST declare this same network as
`external: true, name: lakehouse_lakehouse` in its own
`compose.yaml`. Without this declaration, the local bridge has no
endpoint for the external name and every downstream stack fails
to resolve `lakehouse-postgres`, `lakehouse-garage`,
`lakehouse-redis`, etc.

#### Scenario: An active srutha needs LanceDB vector RAG

- **GIVEN** an active srutha stack (e.g. `croilar-dagster`,
  `croilar-marimo`, `oideachais`)
- **WHEN** the stack boots
- **THEN** its `LANCEDB_URI` env var MUST default to
  `rest://lakehouse-lance-namespace:8182`
- **AND** the default MUST be overridable via `.env` for legacy
  file-path deployments
- **AND** the stack MUST be on the `lakehouse` external network
  (declared `external: true, name: lakehouse_lakehouse` by BOTH the
  lakehouse stack AND the srutha stack) so it can reach the Lance
  sidecar at `:8182`

#### Scenario: An active srutha needs DuckLake storage

- **GIVEN** an active srutha (e.g. `oideachais`, `croilar`,
  `crypteolas`, `tuath`, `meaisinfhoghlaim`)
- **WHEN** its Dagster code-location runs `with_namespace()` to
  materialise a DuckLake destination
- **THEN** the factory MUST produce a connection string referencing
  `ducklake_{namespace}` on the shared `lakehouse-postgres`
- **AND** the database MUST exist in
  `bonneagar/stacks/lakehouse/init-db.sql` with `OWNER lakehouse`
- **AND** if the database is missing, the `with_namespace()` factory
  MUST raise an actionable error pointing at the lakehouse
  `init-db.sql` file

#### Scenario: meaisinfhoghlaim is wired into the lakehouse

- **GIVEN** the `meaisinfhoghlaim` srutha has a Dagster code-location
  but historically had no `ducklake_*` database
- **WHEN** the lakehouse `init-db.sql` runs on a fresh
  `docker compose up`
- **THEN** the `ducklake_meaisinfhoghlaim` database MUST be created
  with `OWNER lakehouse` and `GRANT ALL PRIVILEGES`
- **AND** the `meaisinfhoghlaim` Dagster assets MUST be able to
  materialise to `with_namespace("meaisinfhoghlaim")` on the shared
  Postgres without manual DB creation

### Requirement: Lakehouse Stack Versions 2026-07

MUST pin the 8 canonical lakehouse stack versions, including the
renamed `DUCKLAKE_BUCKET`. The lakehouse stack pins 8 versions:

- **`dxflrs/garage:v2.3.0`** (the centralised S3 storage)
- **`postgres:16-alpine`** (the lakehouse-postgres instance)
- **`clickhouse/clickhouse-server:25.8`** (the lakehouse-clickhouse)
- **`redis:7-alpine`** (the lakehouse-redis cache)
- **`quay.io/lakekeeper/catalog:v0.13.1`** (the Iceberg REST catalog)
- **`lakehouse-lance-namespace:latest`** (built from local Dockerfile;
  Lance Namespace sidecar at `:8182`)
- **`nimtable/nimtable:latest`** (the Iceberg catalog UI; documented
  exception to the 5-file GOLD_STANDARD contract)
- **`ghcr.io/olake-io/olake:v0.8.0`** (the CDC ingestion engine)

Additionally MUST pin `DUCKLAKE_BUCKET=ducklake-cianfhoghlaim` (renamed
from `ducklake` per the 2026-08-01 change; the canonical bucket
name now matches `dlt_sources/common/destinations_cianfhoghlaim.py:109`
default).

#### Scenario: garage-init creates the renamed bucket

```
# On lakehouse bring-up, the garage-init 1-shot service runs and
# creates the bucket:
$ curl -X GET http://lakehouse-garage:3900/v2/bucket
[{"name":"ducklake-cianfhoghlaim","creationDate":"2026-08-01T...","globalAliases":[]}]
# the dlt destinations_cianfhoghlaim.py factory can now write to this
# bucket at the canonical name (no name-mismatch risk)
```

> The stack MUST be on the `lakehouse` external network so it can
> reach the Lance sidecar at `:8182`. **The lakehouse stack MUST
> declare this same network as `external: true, name: lakehouse_lakehouse`
> in its own `compose.yaml`** (per the
> `2026-08-01-lakehouse-and-reproducible-deploy-v1` change — without
> this, the local bridge has no endpoint for the external name).

#### Scenario: the lakehouse external network has an endpoint

- **GIVEN** the lakehouse stack is up via `docker compose -f lakehouse/compose.yaml -f lakehouse/sidecar.yaml up -d`
- **AND** langfuse is up via `docker compose -f langfuse/compose.yaml -f langfuse/sidecar.yaml up -d`
- **WHEN** langfuse resolves `http://lakehouse-postgres:5432/langfuse` (its `DATABASE_URL`)
- **THEN** the DNS resolves successfully to a container on the lakehouse stack
- **AND** the connection succeeds (PG password matches via Locket-resolved env)

## ADDED Requirements

### Requirement: Lakehouse network externalisation

The lakehouse stack MUST declare its internal bridge network as
`external: true, name: lakehouse_lakehouse` in its own `compose.yaml`.
This MUST match the network declaration that every downstream stack
(langfuse, mlflow, litellm, cognee, dagster, marimo, oideachais,
graphiti, agent-os) declares against `lakehouse: name: lakehouse_lakehouse,
external: true`.

#### Scenario: lakehouse stack network matches downstream declarations

```
# Lakehouse declares (correct):
networks:
  lakehouse:
    name: lakehouse_lakehouse
    external: true

# Langfuse declares (correct):
networks:
  lakehouse:
    name: lakehouse_lakehouse
    external: true
```

#### Scenario: pre-change lakehouse network declaration is rejected

```
# Pre-change (rejected — was the #1 critical gap):
networks:
  lakehouse:
    driver: bridge      # WRONG: local bridge with no external endpoint
```

### Requirement: MotherDuck hosting-mode env contract

MUST export 4 MotherDuck env vars via `secrets.env`. Every data-plane
stack (`lakehouse`, `oideachais`, `dagster`, `motherduck`, `marimo`)
MUST set the following:

- `MOTHERDUCK_MODE` (default `byob`)
- `MOTHERDUCK_DATABASE` (default `cianfhoghlaim`)
- `MOTHERDUCK_S3_BUCKET` (default `ducklake-cianfhoghlaim`)
- `MOTHERDUCK_S3_ENDPOINT` (default `http://lakehouse-garage:3900`)

The canonical MotherDuck token path is `dev-baile/motherduck/token`
(single canonical path; duplicates in other paths are forbidden).

#### Scenario: a stack operator switches to `managed` mode

```
# Operator overrides in .env.local:
MOTHERDUCK_MODE=managed
MOTHERDUCK_DATABASE=cianfhoghlaim-prod
# leaves MOTHERDUCK_TOKEN to Locket resolution
# the dlt destinations_cianfhoghlaim.py factory routes via the managed
# path on next pipeline run
```

#### Scenario: MotherDuck token is single-canonical

```
# lakehouse/secrets.env:
MOTHERDUCK_TOKEN=infisical://dev-baile/motherduck/token   # canonical

# oideachais/secrets.env:
MOTHERDUCK_TOKEN=infisical://dev-baile/motherduck/token   # same canonical path
# NOT: infisical://dev-baile/lakehouse/token              # forbidden duplicate
```

### Requirement: deploy:full orchestrator

The system MUST provide a `mise run deploy:full` command that brings
up the entire 91-stack platform in 7 phases with healthchecks + a
resumable checkpoint state file at `~/.cianfhoghlaim/deploy-state.json`.

The 7 phases MUST be (in this order):

1. `preflight-arm-oci` — the 4-check safety gate
2. `control-plane-up` — infisical + pangolin + komodo + pocket-id + tinyauth
3. `lakehouse-up` — postgres + garage + clickhouse + redis + lakekeeper + lance-namespace
4. `data-stacks-up` — litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb
5. `agent-surfaces-up` — openclaw + openchamber + hermes + ocr-router
6. `dagster-materialize` — BIEP v3 upstream + downstream assets
7. `dagster-sensor-health-gate` — `ocr_completion_sensor` + the 5
   other active sensors report `ACTIVE` state

Each phase MUST verify healthchecks before proceeding to the next.
Re-running after a partial failure MUST resume from the failed phase
(checkpoint read from `deploy-state.json`).

#### Scenario: full deploy succeeds

```
$ mise run deploy:full
[phase 1] preflight-arm-oci: ✓ (4/4 checks passed)
[phase 2] control-plane-up:  ✓ (5/5 services healthy)
[phase 3] lakehouse-up:      ✓ (6/6 services healthy)
[phase 4] data-stacks-up:    ✓ (7/7 services healthy)
[phase 5] agent-surfaces-up: ✓ (4/4 services healthy)
[phase 6] dagster-materialize: ✓ (199 assets materialized)
[phase 7] dagster-sensor-health-gate: ✓ (6/6 sensors active)
deploy-state.json: 7/7 phases complete
```

#### Scenario: deploy fails at phase 4, re-run resumes

```
$ mise run deploy:full
[phase 1] preflight-arm-oci: ✓ (cached)
[phase 2] control-plane-up:  ✓ (cached)
[phase 3] lakehouse-up:      ✓ (cached)
[phase 4] data-stacks-up:    ✗ langfuse healthcheck FAILED
deploy-state.json: 3/7 phases complete (resumable)
# operator fixes langfuse, re-runs:
$ mise run deploy:full
[phase 1-3] skipped (cached)
[phase 4] data-stacks-up:    ✓ (7/7 services healthy, langfuse now healthy)
[phase 5-7] ... continues
```

### Requirement: supersede the 3 standalone data stacks

MUST be removed from the repo. The 3 standalone stacks
`bonneagar/stacks/garage/`, `bonneagar/stacks/lakekeeper/`,
`bonneagar/stacks/lakefs/` MUST NOT exist (per the 2026-08-01
change). They are superseded by the centralised `lakehouse` stack
(Garage v2.3.0 + Lakekeeper v0.13.1 + Lance Namespace).

#### Scenario: stack-doctor no longer references the dead stacks

```
$ ls bonneagar/stacks/garage/ 2>&1
ls: bonneagar/stacks/garage/: No such file or directory

$ ls bonneagar/stacks/lakekeeper/ 2>&1
ls: bonneagar/stacks/lakekeeper/: No such file or directory

$ ls bonneagar/stacks/lakefs/ 2>&1
ls: bonneagar/stacks/lakefs/: No such file or directory
```

#### Scenario: the central `lakehouse` stack covers all 3 use cases

```
# Storage: lakehouse-garage (Garage v2.3.0)
$ curl http://lakehouse-garage:3900/health
{"status":"Server available"}

# Catalog: lakehouse-lakekeeper (Lakekeeper v0.13.1)
$ curl http://lakehouse-lakekeeper:8181/health
{"status":"ok"}

# Vector: lakehouse-lance-namespace (Lance Namespace sidecar)
$ curl http://lakehouse-lance-namespace:8182/health
{"status":"ok"}
```

## Why this matters

The 4 fixes bundled here are the data plane + the full-platform
orchestrator that make the platform reproducible from a fresh host.
The external network rename is the single biggest silent-integration
break in the IaC surface today.