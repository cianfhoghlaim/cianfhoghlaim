# Infrastructure Stacks — Replace Private Images + Wave 2 Delta

> This file is the change-side delta for
> `2026-07-02-replace-private-images-and-bring-wave2`. It applies on
> top of the canonical `infrastructure-stacks` spec at
> `../../../../specs/infrastructure-stacks/spec.md` and on top of the
> prior 4 changes' deltas (bunchloch-stack-bootstrap,
> add-lancedb-and-logfire-stacks, add-marimo-stack,
> add-agent-surface-stacks).

## ADDED Requirements

### Requirement: Public image registry policy

The system SHALL NOT reference `ghcr.io/cianfhoghlaim/*` images in
any compose.yaml. Images SHALL come from public upstream registries
(Docker Hub, `ghcr.io/<upstream-org>/*`, `quay.io`) OR from
locally-built images via `Dockerfile.<stack>` in the stack dir.

#### Scenario: Image source review
- **WHEN** a developer runs `grep -rE 'ghcr\.io/cianfhoghlaim' bonneagar/stacks/`
- **THEN** the result SHALL be empty (no `ghcr.io/cianfhoghlaim/*` references)

#### Scenario: Image source classification
- **WHEN** a developer reviews any `image:` line in a compose.yaml
- **THEN** the image SHALL be either:
  - A semver-tagged public upstream image (e.g.
    `ghcr.io/mlflow/mlflow:v2.22.4`)
  - A `nousresearch/*` Docker Hub image (per user direction:
    `docker pull nousresearch/hermes-agent` should work)
  - A local-build image (e.g. `dagster-local:latest`) with a matching
    `Dockerfile.<stack>` in the same directory

### Requirement: Dagster local-build image

The system SHALL build the dagster webserver + daemon images
locally from `bonneagar/stacks/dagster/Dockerfile.dagster` (modeled
on `dagster-io/dagster/examples/deploy_docker`, integrated with the
cianfhoghlaim-specific Python deps). The image tag SHALL be
`dagster-local:latest`.

The Dockerfile SHALL install:
- `dagster==1.13.11` (the current public release)
- `dagster-webserver==1.13.11`
- `dagster-postgres==1.13.11` (Postgres-backed run/event storage;
  used for `DAGSTER_HOME=/opt/dagster/home` in dev)
- `dagster-duckdb`, `dagster-aws` (lakehouse integration)
- `baml>=0.222.0` (per `pyproject.toml`)
- `cocoindex>=0.3.9`, `lancedb>=0.24.0`, `duckdb>=1.0.0`
- `psycopg2-binary`, `boto3`, `pyarrow`

#### Scenario: Dagster boots in dev mode
- **WHEN** an operator runs `docker build -f stacks/dagster/Dockerfile.dagster -t dagster-local:latest stacks/dagster/`
  followed by `./scripts/stack.sh dagster up -d` (or the docker compose
  equivalent)
- **THEN** the dagster container SHALL start using
  `dagster-local:latest`
- **AND** the dagster webserver SHALL respond at
  `127.0.0.1:3335/server_info` (per the existing port mapping in
  dagster/compose.yaml)

### Requirement: MLflow image pinned to public upstream

The system SHALL use `ghcr.io/mlflow/mlflow:v2.22.4` as the mlflow
base image. The `Dockerfile.mlflow` `FROM` line MUST match this tag.
The custom dev overlay (mlflow/compose.dev.yaml) MUST reference the
`ghcr.io/mlflow/mlflow` public image (not the org-private
`ghcr.io/cianfhoghlaim/mlflow:v2.19.0`).

#### Scenario: MLflow ping
- **WHEN** the mlflow stack comes up in dev mode
- **THEN** `curl :5000/api/2.0/mlflow/ping` SHALL return HTTP 200
- **AND** the `MLFLOW_BACKEND_STORE_URI` env var SHALL point at the
  lakehouse-postgres `mlflow` database

#### Scenario: MLflow S3 storage
- **WHEN** the mlflow server is started
- **THEN** `MLFLOW_S3_ENDPOINT_URL` SHALL point at
  `http://lakehouse-garage:3900` (the in-cluster Garage endpoint)
- **AND** `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` SHALL be set
  from the dev `.env.dev` (mapped from `GARAGE_*` env vars via the
  `destinations_oideachais.py` translation layer in Change 8)

### Requirement: Hermes + Openclaw + Openchamber image hygiene

The hermes image SHALL be `nousresearch/hermes-agent:v2026.7.1`
(Docker Hub public — verified 200 with the user's local docker
pull). The openclaw image stays
`ghcr.io/openclaw/openclaw:2026.2.6` (verified public 200 on GHCR).
The openchamber image is deferred to a separate follow-up change
(`2026-07-XX-bring-openchamber-stack-to-spec`) because no public
image exists.

#### Scenario: Hermes pulls
- **WHEN** the hermes stack comes up in dev mode
- **THEN** `docker pull nousresearch/hermes-agent:v2026.7.1` SHALL
  succeed (no 401 / 403)
- **AND** the hermes container SHALL use the docker DNS name
  `nousresearch/hermes-agent:v2026.7.1` (no `ghcr.io/` prefix)

#### Scenario: Openclaw pulls
- **WHEN** the openclaw stack comes up in dev mode
- **THEN** `docker pull ghcr.io/openclaw/openclaw:2026.2.6` SHALL
  succeed (verified public)

#### Scenario: Openchamber deferred
- **WHEN** an operator attempts to bring up the openchamber stack
- **THEN** the pull of `ghcr.io/openchamber/openchamber:1.0.0` SHALL
  fail (private image; no public alternative)
- **AND** the operator SHALL file a separate openspec change
  (`2026-07-XX-bring-openchamber-stack-to-spec`) to remediate

### Requirement: Lakehouse integration smoke tests (15-test gate)

After Wave 2 deploys, the system SHALL pass a 15-test smoke gate
that verifies each subsystem (CocoIndex, DLT, Dagster, BAML,
Marimo) is correctly wired to the lakehouse destinations.

The 15 tests are:
1. DLT destination factory returns a DuckLake destination object
2. DLT pipeline dry-run succeeds (no exception)
3. Garage S3 health probe (`/health` returns 200 or 403)
4. LanceDB REST health probe (`:8182/health` returns 200)
5. Postgres dev DBs exist (at least 7: `mlflow`, `langfuse`,
   `litellm`, `cognee_oideachais`, `nimtable`, `olake_state`,
   `ducklake_oideachais`)
6. ClickHouse ping (`:8123/ping` returns 200)
7. Lakehouse Redis (`redis-cli ping` returns PONG)
8. BAML `baml-cli generate` succeeds (no errors)
9. LiteLLM gateway `:4000/health/liveliness` returns 200
10. (Optional) BAML test call via LiteLLM returns 200
11. CocoIndex v1 conformance update (`codebase_indexing:codebase_app`)
    indexes N files with 0 errors
12. Marimo `ducklake_explorer.py` runs end-to-end with live
    `DUCKLAKE_POSTGRES_HOST=lakehouse-postgres`
13. FalkorDB `GRAPH.QUERY` works on `:6379`
14. Dagster webserver `:3335/server_info` returns 200 + JSON
15. Dagster code location loads the 5 KCG Components from
    `cianfhoghlaim.dagster.definitions`

#### Scenario: Smoke gate passes
- **WHEN** an operator runs the 15 tests after Wave 2 deploy
- **THEN** at least 14 of 15 tests SHALL pass (1 optional test may
  be skipped without failing the gate)
- **AND** the HEALTH_REPORT Session 6 entry SHALL record the
  pass/fail count for each test

#### Scenario: Smoke gate fails
- **WHEN** any required test fails
- **THEN** the omnibus is INCOMPLETE and the failure SHALL be
  documented in HEALTH_REPORT
- **AND** a follow-up issue SHALL be filed to remediate
