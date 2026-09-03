# `infrastructure-stacks` capability spec — hermes + cluster + photos delta

The infrastructure-stacks capability spec governs the 88+
Docker Compose stacks under `bonneagar/stacks/`, the 6-file
GOLD_STANDARD pattern, the Locket sidecar contract, the
Pangolin Traefik routing shape, and the Komodo GitOps
deployment procedure.

This delta adds the Hermes Agent stack as the 89th stack
(bringing the total to 89+), the `agent-platform-cluster`
omnibus Komodo procedure (the 8-stack bring-up), and the
`apple-photos-ingest` Komodo procedure (the Apple Photos
4-stage bring-up).

## ADDED Requirements

### Requirement: hermes Stack Directory

The system SHALL provide a Docker Compose stack at
`bonneagar/stacks/hermes/` that runs the upstream
`NousResearch/hermes-agent` v0.17.0 channel-fanout +
autonomous-agent runtime plus a Locket sidecar for Infisical
secret injection. The Hermes stack SHALL be deployed on
`bunchloch` (MacBook M4 Max), NOT on `arm1-oci` (which is
at 70% utilization).

#### Scenario: 6 GOLD_STANDARD files present

- **WHEN** a developer lists `bonneagar/stacks/hermes/`
- **THEN** the directory SHALL contain all 6 GOLD_STANDARD
  files: `compose.yaml`, `sidecar.yaml`, `secrets.env`,
  `pangolin.yaml`, `blueprint.yaml`, `.env.example`
- **AND** a `README.md` describing the stack
- **AND** a `config/hermes.yaml` runtime config
- **AND** an `init-allowlist.sh` 1-shot init script for
  the day-one allowlist population

#### Scenario: compose.yaml uses pinned image and non-host network

- **WHEN** a developer reads `bonneagar/stacks/hermes/compose.yaml`
- **THEN** the `image:` line SHALL be pinned to
  `ghcr.io/nousresearch/hermes-agent:0.17.0@sha256:<digest>`
  with no `:latest` tag
- **AND** the service SHALL declare the 5 port publishes
  (9119 to Pangolin; 8443/8090/8080/8645 webhook ports to
  127.0.0.1 only)
- **AND** no `network_mode: host` line SHALL appear
- **AND** `networks: [cianfhoghlaim]` SHALL be set
- **AND** the service SHALL declare `restart: unless-stopped`
  and a healthcheck against `/api/health` on port 9119
- **AND** `deploy.resources.limits: { cpus: '2', memory: 2G }`
  SHALL be set

#### Scenario: secrets.env references litellm + langfuse

- **WHEN** a developer reads `bonneagar/stacks/hermes/secrets.env`
- **THEN** the file SHALL contain 9 `infisical://dev-baile/hermes/<key>`
  references:
  `api_server_key` (admin token),
  `openai_api_key` (→ LITELLM_MASTER_KEY),
  `openai_base_url` (http://litellm:4000/v1),
  `langfuse_public_key`,
  `langfuse_secret_key`,
  `langfuse_base_url`,
  `telegram_bot_token`,
  `discord_bot_token`,
  `operator_pocket_id_subject`
- **AND** no plaintext secrets SHALL be present

### Requirement: hermes 3-Layer Auth Contract

The system SHALL enforce 3-layer authentication on
`hermes.cianfhoghlaim.ie`:

1. **Pangolin TinyAuth** (Pocket ID OIDC) at Traefik
2. **`users.allowlist`** in `config/hermes.yaml` (per the
   `meaisinfhoghlaim-agent-frameworks` spec)
3. **`channels.<name>.allow_from`** per channel

The 3 channels enabled in v1 are `telegram`, `discord`,
`webchat` (no overlap with OpenClaw's `telegram` and
`discord` channels — separate bot tokens per the
`meaisinfhoghlaim-agent-frameworks` spec).

#### Scenario: hermes is reachable at hermes.cianfhoghlaim.ie

- **WHEN** the `deploy-agent-platform-cluster-bunchloch`
  Komodo procedure has run to completion
- **THEN** `https://hermes.cianfhoghlaim.ie/api/health`
  SHALL return HTTP 200 within 30s of the procedure's
  Stage 5 health check
- **AND** the `users.allowlist` SHALL contain the operator's
  Pocket ID subject (verified by the
  `curl /api/users/allowlist/test` smoke test)

#### Scenario: hermes channels do not overlap OpenClaw

- **WHEN** a developer lists the enabled channels in
  `bonneagar/stacks/hermes/config/hermes.yaml` and in
  `bonneagar/stacks/openclaw/config/openclaw.json`
- **THEN** Hermes SHALL enable `telegram`, `discord`,
  `webchat` only
- **AND** OpenClaw SHALL keep `telegram`, `slack`,
  `discord`, `whatsapp`, `webchat`, `ms-teams`
- **AND** both stacks SHALL use separate bot tokens
  (different `dev-baile/openclaw/telegram_bot_token` vs
  `dev-baile/hermes/telegram_bot_token`)

### Requirement: agent-platform-cluster deploy procedure brings up the 8 stacks in dependency order

The system SHALL provide a Komodo procedure at
`bonneagar/komodo/procedures/deploy-agent-platform-cluster-bunchloch.toml`
that brings up the 8 agent-platform-cluster stacks in
dependency order, with `--skip=<foundation|observability|memory|surfaces>`
flags for partial re-deploys. The 6 stages are:

- **Stage 0 — pre-reqs:** Pangolin mesh healthy, Pocket ID
  SSO reachable, Infisical `dev-baile` reachable, Bunchloch
  resource ceiling check (< 80% utilized).
- **Stage 1 — `foundation`:** deploy `lakehouse` (Garage S3
  must exist before litellm can store its logs).
- **Stage 2 — `observability`:** deploy `litellm` +
  `langfuse` + `mlflow` + `logfire` (the 3 agent surfaces
  cannot start without litellm; langfuse/mlflow/logfire are
  observability consumers of those 3 surfaces).
- **Stage 3 — `memory`:** deploy `cognee` + `graphiti` +
  `lancedb` (the v1 CocoIndex Apps write to lancedb;
  cognee is the doc knowledge graph; graphiti is the
  temporal knowledge graph).
- **Stage 4 — `surfaces`:** deploy `openclaw` + `openchamber`
  + `hermes` (the 3 agent surfaces).
- **Stage 5 — health checks:** `curl /api/health` on each
  of the 8 stacks + 1 paperless-ngx + 4 OCR stacks.
- **Stage 6 — validate:** the 4 stack-doctor gates
  (`bun run validate-stacks`) all pass.

#### Scenario: Omnibus procedure succeeds end-to-end

- **GIVEN** Bunchloch is at 50% utilization (below 80%)
- **AND** Pangolin + Pocket ID + Infisical are reachable
- **WHEN** the operator runs
  `komodo run procedure deploy-agent-platform-cluster-bunchloch`
- **THEN** the procedure SHALL complete all 6 stages in
  ≤ 15 minutes
- **AND** `curl -fsS https://hermes.cianfhoghlaim.ie/api/health`
  SHALL return HTTP 200
- **AND** `curl -fsS https://openclaw.cianfhoghlaim.ie/api/health`
  SHALL return HTTP 200
- **AND** `curl -fsS https://openchamber.cianfhoghlaim.ie/api/health`
  SHALL return HTTP 200
- **AND** `curl -fsS https://litellm.cianfhoghlaim.ie/health/liveliness`
  SHALL return HTTP 200

#### Scenario: Skip flag re-deploys a subset

- **GIVEN** the omnibus procedure has run to completion
- **AND** the operator wants to re-deploy only the 3 agent
  surfaces (Stage 4) after a code change
- **WHEN** the operator runs
  `komodo run procedure deploy-agent-platform-cluster-bunchloch --skip=foundation,observability,memory`
- **THEN** only `openclaw` + `openchamber` + `hermes` SHALL
  be re-deployed
- **AND** Stages 0, 1, 2, 3 SHALL be no-ops
- **AND** Stage 5 + Stage 6 SHALL run the health checks
  + validation

### Requirement: apple-photos-ingest deploy procedure runs the 4-stage Apple Photos bring-up

The system SHALL provide a Komodo procedure at
`bonneagar/komodo/procedures/deploy-apple-photos-ingest-bunchloch.toml`
that runs the Apple Photos bring-up in 4 stages:

- **Stage 0 — pre-reqs:** the 8-stack cluster is up; the
  `leabharlann/photos/` directory exists from the
  one-shot `osxphotos export`.
- **Stage 1 — `dlt run`:** invokes
  `apple_photos_source()` to populate the `apple_photos`
  DuckLake table from the export.
- **Stage 2 — `mise run cocoindex:update`:** invokes
  `cocoindex:update apple_photos_metadata,
  apple_photos_chunks, apple_photos_geospatial` to
  populate the 3 new v1 Apps in LanceDB.
- **Stage 3 — `smoke route`:** routes 1 sample document
  scan + 1 sample vehicle photo to the 2 destinations
  (`paperless-ngx` + `vehicle_observations` table) as a
  smoke test.
- **Stage 4 — `register + schedule`:** registers the 5 new
  Dagster assets in the `apple_photos` group; schedules
  `apple_photos_vehicle_cross_frame` to run weekly at
  04:00 UTC on `bunchloch`.

#### Scenario: Apple Photos procedure succeeds end-to-end

- **GIVEN** the omnibus procedure has run to completion
- **AND** `leabharlann/photos/` contains at least 1
  document scan + 1 vehicle photo
- **WHEN** the operator runs
  `komodo run procedure deploy-apple-photos-ingest-bunchloch`
- **THEN** the procedure SHALL complete all 4 stages in
  ≤ 30 minutes (the OCR + vision inference is the slow part)
- **AND** 1 paperless-ngx document SHALL be created with
  the OCR'd text + EXIF GPS as tags
- **AND** 1 `vehicle_observations` row SHALL be inserted
  with the plate text + make/model + GPS + timestamp

## Cross-references

- [`openspec/changes/add-openclaw-stack-and-channel-fanout/`](../add-openclaw-stack-and-channel-fanout/)
- [`openspec/changes/add-openchamber-stack-and-opencode-ui/`](../add-openchamber-stack-and-opencode-ui/)
- [`openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/proposal.md`](../proposal.md)
- [`bonneagar/stacks/hermes/`](../../../bonneagar/stacks/hermes/)
- [`bonneagar/komodo/procedures/deploy-agent-platform-cluster-bunchloch.toml`](../../../bonneagar/komodo/procedures/deploy-agent-platform-cluster-bunchloch.toml)
- [`bonneagar/komodo/procedures/deploy-apple-photos-ingest-bunchloch.toml`](../../../bonneagar/komodo/procedures/deploy-apple-photos-ingest-bunchloch.toml)
