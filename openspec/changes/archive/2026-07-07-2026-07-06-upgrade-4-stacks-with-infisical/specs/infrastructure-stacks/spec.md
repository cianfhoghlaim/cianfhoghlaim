## ADDED Requirements

### Requirement: Consumer Stack Locket Pointing at Local Vault

The system SHALL route every consumer stack's Locket sidecar
(`stack-shared locket container`) at `http://infisical-backend:8080` on the
shared `bunchloch-infra` external network. The Locket sidecar SHALL read
machine identity `INFISICAL_CLIENT_ID`, `INFISICAL_CLIENT_SECRET`,
`INFISICAL_PROJECT_ID` from a file-mounted secret at
`/run/secrets/infisical_secret` (matching the production secret mount path).

#### Scenario: A consumer stack's Locket sidecar successfully syncs

- **GIVEN** the local Infisical vault from Change 1 is up at
  `http://infisical-backend:8080`
- **AND** the `dev-baile/dev/<stack>/<key>` paths are seeded via the bootstrap script
- **AND** the consumer stack is brought up via
  `docker compose -f compose.yaml -f sidecar.yaml up -d`
- **WHEN** `docker logs <stack>-locket` is observed
- **THEN** the output SHALL contain `secrets synced` within 10 seconds of boot
- **AND** `${VAR}` interpolation in the consumer's `compose.yaml` SHALL
  resolve to the Infisical-stored value (NOT the developer's local `.env`)

### Requirement: Lakehouse Stack Versions 2026-07

The system SHALL pin every container in `bonneagar/stacks/lakehouse/` to
the versions verified via Firecrawl on 2026-07-06.

#### Scenario: All lakehouse containers are semver-pinned

- **WHEN** `bun run validate-stacks` runs against the lakehouse stack
- **THEN** every `image:` line SHALL be a `<major>.<minor>.<patch>` semver
  tag (NOT `:latest`)
- **AND** the canonical versions SHALL be:
  - `quay.io/lakekeeper/catalog:v0.13.1`
  - `dxflrs/garage:v2.3.0`
  - `clickhouse/clickhouse-server:25.8.28.1-lts`
  - `nimtable/nimtable:v0.1.0`
  - `ghcr.io/olake-io/olake:v0.8.0`

### Requirement: LiteLLM Production Memory Formula

The `bonneagar/stacks/litellm/compose.yaml` SHALL declare
`memory: 16G` for the litellm service when `--num_workers=4` is used,
per the upstream `4Gi × num_workers` formula documented at
<https://docs.litellm.ai/docs/proxy/prod>.

#### Scenario: Stack honours the memory formula

- **WHEN** `bun run validate-stacks` runs against litellm
- **THEN** the `litellm` service declaration SHALL contain
  `deploy.resources.limits.memory: 16G` when `command` includes
  `--num_workers=4`
- **AND** the runbook SHALL document the `1×=4G / 2×=8G / 4×=16G` matrix

### Requirement: MLflow v3 Security Middleware

The `bonneagar/stacks/mlflow/` stack SHALL declare the v3-mandatory
`--allowed-hosts="localhost,mlflow.cianfhoghlaim.ie"` and
`--cors-allowed-origins="https://oideachais.cianfhoghlaim.ie"` flags on
the `mlflow server` command, per the upstream v3.5.0+ security
middleware requirement documented at
<https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/>.

#### Scenario: Stack uses the v3 semver + middleware flags

- **WHEN** `compose.yaml` is read
- **THEN** the image SHALL be `ghcr.io/mlflow/mlflow:v3.12.0` (NOT
  `v2.22.4` and NOT `:latest`)
- **AND** the `command:` list SHALL include
  `--allowed-hosts="localhost,mlflow.cianfhoghlaim.ie"`

### Requirement: Unstract OSS Self-Host at v0.177.7

The `bonneagar/stacks/unstract/` stack SHALL match the upstream
`Zipstack/unstract:v0.177.7` (released 2026-07-06) 15-service
docker-compose layout. The stack SHALL NOT pin to `unstract/unstract:latest`
(which does not exist as a single image).

#### Scenario: Unstract compose is a true 15-service fleet

- **WHEN** `compose.yaml` is read
- **THEN** it SHALL declare ALL 8 upstream images pinned to `:v0.177.7`:
  `unstract/{backend,frontend,platform-service,x2text-service,runner,
  worker-unified,tool-sidecar,llm-whisperer}:v0.177.7`
- **AND** it SHALL declare the 6 Celery worker services
  (`worker-metrics`, `worker-ide-callback`, `worker-api-deployment`,
  `worker-callback`, `worker-file-processing`,
  `worker-general`)
- **AND** the `db` image SHALL be `pgvector/pgvector:pg15` (NOT
  `postgres:16` — per upstream dev essentials)
- **AND** the `backend` healthcheck SHALL target port `:8000/health` (NOT
  `:8002`)
- **AND** the stack SHALL NOT declare `UNSTRACT_API_KEY` (OSS does not
  require it)
- **AND** every container SHALL be named with the bare KCG pattern
  (`unstract-backend`, `unstract-celery-worker-general`, etc.) — NOT the
  upstream's `*-1` numeric suffixes