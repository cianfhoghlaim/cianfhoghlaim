# `workflow-automation` capability spec (NEW)

Self-hosted workflow automation built on n8n. Provides a visual pipeline builder for the team. Six seeded workflows demonstrate the canonical team patterns: daily briefing, email triage, booking-to-task sync, follow-up drafting, weekly summary, and stale-task nudging. All LLM-backed workflow steps use the OpenCode Go API (`https://opencode.ai/zen/go/v1`) as a unified OpenAI-compatible endpoint — one bill, one rate-limit pool, one model catalogue across the whole monorepo.

## ADDED Requirements

### Requirement: n8n Deployment
The system SHALL deploy n8n as a private Pangolin resource in community-edition + queue mode.

#### Scenario: Image and queue mode
- **WHEN** the n8n stack deploys and the `n8n` service starts
- **THEN** the image SHALL be `docker.n8n.io/n8nio/n8n:1.94.1`
- **AND** `EXECUTIONS_MODE=queue` SHALL be set
- **AND** `QUEUE_BULL_REDIS_HOST=n8n-redis` SHALL point at the queue-mode Redis sidecar

#### Scenario: Postgres backing store
- **WHEN** n8n is in queue mode and workflow executions and credentials are persisted
- **THEN** they SHALL be stored in the dedicated `n8n-postgres` container (`postgres:16-alpine`)

#### Scenario: Encryption + JWT
- **WHEN** n8n stores API credentials in its DB
- **THEN** they SHALL be encrypted with `N8N_ENCRYPTION_KEY` from Infisical
- **AND** session JWTs SHALL be signed with `N8N_USER_MANAGEMENT_JWT_SECRET` from Infisical

### Requirement: OpenCode Go LLM Integration
The system SHALL allow n8n's HTTP Request node to call any OpenCode Go model without per-workflow credential configuration.

#### Scenario: Default OpenAI-compatible endpoint
- **WHEN** any n8n workflow contains an "OpenAI" or "HTTP Request" node and the node makes a chat-completions call
- **THEN** it SHALL target `${OPENAI_BASE_URL}/chat/completions` (= `https://opencode.ai/zen/go/v1/chat/completions`)
- **AND** authenticate with `Authorization: Bearer ${OPENAI_API_KEY}` (resolved from Infisical via Locket)

#### Scenario: Six available models
- **WHEN** a workflow needs an LLM step and the operator configures the `model` field
- **THEN** the following models SHALL be available without extra setup: `kimi-k2.6`, `glm-5.1`, `minimax-m2.5`, `mimo-v2.5`, `deepseek-v4-flash` (chat-completions endpoint) and `qwen3.6-plus`, `qwen3.7-max`, `minimax-m2.5`, `minimax-m2.7`, `minimax-m3` (messages endpoint)

### Requirement: Seeded Workflows
The system SHALL auto-import six baseline workflows on first boot via the `n8n-init` one-shot container.

#### Scenario: First-boot import
- **WHEN** the n8n stack deploys for the first time and the `n8n-init` container runs
- **THEN** it SHALL POST each `team-*.json` file from the mounted `/workflows` directory to the n8n REST API
- **AND** activate each imported workflow
- **AND** skip any workflow whose name already exists (idempotent re-import)

#### Scenario: Six baseline workflows
- **WHEN** the workflow files have been imported and the n8n dashboard is opened
- **THEN** the following six workflows SHALL be present and active: `team-daily-briefing`, `team-email-triage`, `team-booking-to-vikunja`, `team-followup-drafter`, `team-weekly-summary`, `team-stale-task-nudger`

### Requirement: Cross-Stack Integration
The system SHALL let n8n workflows read and write to Vikunja and receive webhooks from cal-diy.

#### Scenario: Vikunja REST writes
- **WHEN** a workflow needs to create or update a Vikunja task and makes a REST call to `http://vikunja:3456/api/v1/...`
- **THEN** the call SHALL be authenticated with `Authorization: Bearer jwt(${VIKUNJA_SERVICE_JWT_SECRET})` (resolved by Locket)

#### Scenario: cal-diy webhook ingress
- **WHEN** cal-diy fires a webhook for a booking event and the webhook arrives at the n8n URL configured in cal-diy
- **THEN** the `team-booking-to-vikunja` workflow SHALL receive the payload and create a Vikunja task with start/end dates

### Requirement: Backup
The system SHALL back up the n8n Postgres database nightly to Garage S3.

#### Scenario: Nightly backup
- **WHEN** the `team-backup.toml` Komodo procedure runs at 02:00
- **THEN** `pg_dump` of the n8n database SHALL be compressed and uploaded to `s3://team-backups/n8n/n8n-<timestamp>.sql.gz`

### Requirement: Private Routing
The system SHALL route n8n only through the Pangolin private resource pattern.

#### Scenario: No public exposure
- **WHEN** an unauthenticated client attempts to reach `n8n.cianfhoghlaim.ie` over the public internet
- **THEN** the request SHALL be rejected at Traefik
- **AND WHEN** an authenticated team member connects via the Olm VPN client
- **THEN** the request SHALL succeed
