# Agent Platform Cluster Capability

## Purpose

`agent-platform-cluster` is the 8-stack observability + memory +
LLM-routing substrate that backs every agent in the 12-agent fleet of
the Cianfhoghlaim platform. The 8 stacks are: lakehouse (MotherDuck +
DuckLake), litellm (LLM gateway), langfuse (LLM observability), mlflow
(experiment tracking), logfire (Python tracing), cognee (knowledge
graph), graphiti (temporal KG), lancedb (vector search).

The corresponding source code lives at:

- `bonneagar/stacks/lakehouse/`, `bonneagar/stacks/litellm/`,
  `bonneagar/stacks/langfuse/`, `bonneagar/stacks/mlflow/`,
  `bonneagar/stacks/logfire/`, `bonneagar/stacks/cognee/`,
  `bonneagar/stacks/graphiti/`, `bonneagar/stacks/lancedb/` (the 8
  stack directories)
- `bonneagar/komodo/procedures/deploy-agent-platform-cluster-bunchloch.toml`
  (the omnibus procedure)
- `bonneagar/iac/commands/deploy.ts` (the `iac:deploy` step that
  registers the 8 stacks)

## Background

Before this cluster, each agent (12 agents in
`cianfhoghlaim/agents/meaisinfhoghlaim/`) hit its own ad-hoc
observability + memory + LLM stack. The 8-stack cluster unifies the 6
infrastructure layers + the 2 memory layers into one composable
substrate. The cluster is the canonical home for every agent in the
fleet; the user contract is "if it touches an LLM, it goes through
LiteLLM; if it remembers, it goes through Cognee + Graphiti; if it
observes, it goes through Langfuse + Logfire + MLflow".
## Requirements
### Requirement: 8-stack cluster deployed together

The system SHALL provide 8 Docker Compose stacks that deploy as a
single cluster: lakehouse + litellm + langfuse + mlflow + logfire +
cognee + graphiti + lancedb. Each stack SHALL follow the 6-file
GOLD_STANDARD pattern (`compose.yaml` + `sidecar.yaml` + `secrets.env`
+ `pangolin.yaml` + `blueprint.yaml` + `.env.example`). The 8 stacks
SHALL be deployed by the omnibus Komodo procedure
`deploy-agent-platform-cluster-bunchloch`.

#### Scenario: Cluster bootstrap

- **WHEN** `bun run komodo:deploy-agent-platform-cluster-bunchloch` runs with no `--skip` flags
- **THEN** all 8 stacks are up within 5 minutes
- **AND** LiteLLM is reachable at `litellm.cianfhoghlaim.ie:4000`
- **AND** Lakehouse (MotherDuck) is reachable at `motherduck.cianfhoghlaim.ie:5433` (Postgres endpoint)

#### Scenario: Partial deploy with `--skip` flag

- **WHEN** `bun run komodo:deploy-agent-platform-cluster-bunchloch --skip=cognee,graphiti` runs
- **THEN** cognee + graphiti stacks SHALL be skipped (others deployed)
- **AND** the skipped stacks SHALL appear in the output with `SKIPPED: <reason>` markers

### Requirement: 3 agent-facing surfaces

The system SHALL provide 3 agent-facing surfaces that sit in front of
the 8-stack cluster: openclaw (channel-fanout gateway at
`openclaw.cianfhoghlaim.ie`), openchamber (OpenCode web/desktop at
`openchamber.cianfhoghlaim.ie`), hermes (NousResearch/hermes-agent
v0.17.0 — a 3rd vertex alongside OpenClaw + OpenChamber).

#### Scenario: Agent routes through LiteLLM

- **WHEN** any of the 12 agents in the fleet calls an LLM
- **THEN** the call SHALL be routed through LiteLLM (port 4000)
- **AND** Langfuse SHALL record the trace
- **AND** MLflow SHALL log the model + prompt version

#### Scenario: Agent recalls memory

- **WHEN** any agent in the fleet needs to recall a fact from prior conversation
- **THEN** the recall SHALL go through Cognee (semantic knowledge graph)
- **AND/OR** through Graphiti (temporal KG, bi-temporal model)
- **AND** if vector-only recall is needed, it SHALL go through LanceDB

### Requirement: LiteLLM is the M3 chokepoint

The system SHALL route every agent LLM call through LiteLLM (port 4000)
so the routing keyword maps apply uniformly. The 5 routing keywords are:
`kimi / k2` → kimi-k2.6; `glm / 5.1` → glm-5.1; `minimax / m2.5` →
minimax-m2.5; `mimo / 2.5` → mimo-v2.5; `deepseek / flash` →
deepseek-v4-flash.

#### Scenario: Routing keyword dispatch

- **WHEN** an agent invokes a model with the keyword "kimi" or "k2"
- **THEN** LiteLLM SHALL route to the `kimi-k2.6` model
- **AND** the trace SHALL identify the model in Langfuse

### Requirement: Letta memory layer

The system SHALL optionally provide a Letta memory layer for the 3
surfaces (OpenClaw + OpenChamber + Hermes) so user-level memory
persists across sessions.

#### Scenario: User-level memory persistence

- **WHEN** a user chats via OpenClaw and dismisses a topic
- **THEN** the next session opens with the prior context loaded from Letta
- **AND** Letta stores the conversation summary in the per-user namespace

### Requirement: Bootstrap procedure composes 7 stages into one km invocation

The system SHALL provide an `agent-platform-cluster-arm1-oci-bootstrap`
Komodo procedure that brings up the agent platform on arm1-oci via a
single `km run procedure` invocation. The procedure SHALL compose 7
stages:

1. **pre-reqs** — Check 9 environment variables exist
   (INFISICAL_CLIENT_ID, INFISICAL_CLIENT_SECRET, INFISICAL_PROJECT_ID,
   DOCKER_REGISTRY_TOKEN, OPENCODE_AUTH_TOKEN, MCP_CURATOR_AUTH_TOKEN,
   LANE_POOL_STORAGE_S3_BUCKET, LANE_POOL_STORAGE_S3_ACCESS_KEY,
   LANE_POOL_STORAGE_S3_SECRET_KEY) AND check the arm1-oci resource
   ceiling (CPU ≤ 85%, MEM ≤ 90%).
2. **parallel-image-builds** — Run 3 Komodo `Build` resources in
   parallel (`openchamber-arm1-oci` + `openclaw-arm1-oci` +
   `hermes-arm1-oci`).
3. **iac-bootstrap** — Invoke `pnpm tsx bonneagar/iac/commands/bootstrap.ts arm1-oci`.
4. **omnibus-deploy** — Invoke `deploy-agent-platform-cluster-arm1-oci`
   (the preflight-gated omnibus from Improvement 3).
5. **health-checks** — Curl `https://{hermes,openclaw,openchamber}.cianfhoghlaim.ie/api/health`
   (all 3 MUST return 200).
6. **emit-artifact** — Write
   `/tmp/agent-platform-cluster/arm-oci-<utc-ts>.json` containing the
   resolved cluster fingerprint (URLs + image tags).
7. **validate** — Run `bun run validate-stacks`.

#### Scenario: All 3 builds succeed in parallel

- **WHEN** all 3 image builds (`openchamber-arm1-oci` + `openclaw-arm1-oci` + `hermes-arm1-oci`) complete with exit 0
- **THEN** `iac-bootstrap` proceeds
- **AND** the omnibus runs (with preflight gating Stage 4)
- **AND** the 3 health endpoints are probed
- **AND** the JSON artifact is written

#### Scenario: 1 build fails

- **WHEN** at least 1 of the 3 builds returns non-zero
- **THEN** `iac-bootstrap` is skipped
- **AND** the omnibus is skipped
- **AND** no curl probes run
- **AND** the JSON artifact is NOT emitted

#### Scenario: Omnibus preflight fails

- **WHEN** the omnibus preflight (Stage 0 of `deploy-agent-platform-cluster-arm1-oci`) returns non-zero
- **THEN** the 3 health checks are skipped
- **AND** the JSON artifact is NOT emitted
- **AND** the procedure reports the preflight failure reason (the captured `/tmp/preflight-reports/arm-oci/<ts>.md` path)

### Requirement: Auto-archive procedure gates on 3 health endpoints returning 200

The system SHALL provide an `archive-agent-platform-cluster-arm1-oci`
Komodo procedure that archives the 5 openspec changes closing the
agent-platform-cluster deployment — but ONLY WHEN all 3 health
endpoints return 200:

- `https://hermes.cianfhoghlaim.ie/api/health` (must return 200)
- `https://openclaw.cianfhoghlaim.ie/api/health` (must return 200)
- `https://openchamber.cianfhoghlaim.ie/api/health` (must return 200)

The 5 changes to archive (in any order, all idempotent):

1. `2026-07-13-backfill-server-id-on-12-procedures`
2. `2026-07-13-arm-oci-deploy-preflight-hard-gate-v1`
3. `2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1`
4. `2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1` (self)
5. `2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow`

The procedure SHALL emit a JSON artifact at
`/tmp/agent-platform-cluster/archived-on-<utc-ts>.json` containing the
timestamp + the 5 archived change IDs.

#### Scenario: all 3 endpoints return 200

- **WHEN** `curl https://hermes.cianfhoghlaim.ie/api/health` returns 200
- **AND** `curl https://openclaw.cianfhoghlaim.ie/api/health` returns 200
- **AND** `curl https://openchamber.cianfhoghlaim.ie/api/health` returns 200
- **THEN** the procedure runs `openspec archive --yes` on the 5 changes
  (idempotent — `|| true` so already-archived is treated as success)
- **AND** the JSON artifact is written to `/tmp/agent-platform-cluster/archived-on-<ts>.json`

#### Scenario: any endpoint returns non-200

- **WHEN** ANY of the 3 endpoints returns non-200
- **THEN** the procedure aborts at Stage 1
- **AND** no archive commands run
- **AND** the JSON artifact is NOT emitted

#### Scenario: archive commands are idempotent

- **WHEN** an already-archived change is re-archived
- **THEN** `openspec archive` exits 0 (not an error)
- **AND** the procedure reports success
- **AND** the JSON artifact IS emitted (with the timestamp of the current run)

### Requirement: 3 agent surfaces on arm1-oci (control plane)

The system SHALL provide the 3 agent-platform surfaces on `arm1-oci` (the control-plane host on Oracle Cloud Free Tier, Frankfurt): **hermes** + **openclaw** + **openchamber**. Each surface SHALL follow the 6-file `GOLD_STANDARD` pattern (`compose.yaml` + `sidecar.yaml` + `pangolin.yaml` + `blueprint.yaml` + `.env.example` + a `secrets.env` compatible with Locket) PLUS a Komodo `[[stack]]` registration PLUS a deploy procedure, all wired into the `arm1-oci` resource-sync.

The 3 surfaces SHALL share the existing `langfuse` observability sink (which itself depends on the `lakehouse` data plane on bunchloch). They SHALL be reachable at `https://<service>.cianfhoghlaim.ie/api/health` via the Pangolin mesh on `arm1-oci`, gated by Pocket ID OIDC + TinyAuth. Access from this Mac (bunchloch) to the arm1-oci surfaces SHALL be mediated by the `newt` (Pangolin client) stack running on bunchloch.

The upstream GHCR images for `openchamber` (`:1.0.0`) and `openclaw` (`:2026.2.6`) are private (401 on GHCR HEAD). The arm1-oci stacks SHALL reference code-owned images built from local Dockerfiles: `ghcr.io/cianfhoghlaim/openchamber:1.14.1-arm1` and `ghcr.io/cianfhoghlaim/openclaw:2026.6-arm1`. The `hermes` stack SHALL reference the **public** Docker Hub image `nousresearch/hermes-agent:v2026.7.1` (the upstream `0.17.0` tag is also private).

The omnibus procedure `deploy-agent-platform-cluster-arm1-oci` brings all 3 surfaces up in dependency order and includes a `preflight:arm-oci` safety check (Pangolin + Komodo + Infisical health + process namespace isolation) as the first stage. The omnibus accepts `--skip=<stage>` flags for partial re-deploys.

#### Scenario: openclaw.cianfhoghlaim.ie is reachable

- **WHEN** `km run procedure deploy-openclaw-arm1-oci` completes
- **THEN** `https://openclaw.cianfhoghlaim.ie/api/health` returns 200
- **AND** the `openclaw` container joins the `cianfhoghlaim` bridge network
- **AND** Locket injects the `dev-baile/openclaw/*` Infisical secrets
- **AND** the WS protocol v3 handshake (challenge + auth + connect) returns 200 at `ws://openclaw.cianfhoghlaim.ie:18789`

#### Scenario: openchamber.cianfhoghlaim.ie is reachable

- **WHEN** `km run procedure deploy-openchamber-arm1-oci` completes
- **THEN** `https://openchamber.cianfhoghlaim.ie/api/health` returns 200
- **AND** the openchamber UI serves its bundled React frontend at `https://openchamber.cianfhoghlaim.ie/`
- **AND** the `openchamber` container joins the `cianfhoghlaim` bridge network
- **AND** Locket injects the `dev-baile/openchamber/*` Infisical secrets

#### Scenario: hermes.cianfhoghlaim.ie is reachable

- **WHEN** `km run procedure deploy-hermes-arm1-oci` completes
- **THEN** `https://hermes.cianfhoghlaim.ie/api/health` returns 200
- **AND** `https://hermes.cianfhoghlaim.ie/api/status` returns `version: 0.18.0` (or newer)
- **AND** the hermes `users.allowlist` is populated with the operator's Pocket ID subject (via the `init-allowlist.sh` one-shot container)
- **AND** Locket injects the `dev-baile/hermes/*` Infisical secrets

#### Scenario: Omnibus brings all 3 surfaces up in dependency order

- **WHEN** `km run procedure deploy-agent-platform-cluster-arm1-oci` runs
- **THEN** the `preflight:arm-oci` stage passes all 4 checks
- **AND** the 3 Komodo `Build` resources complete (openchamber + openclaw + hermes)
- **AND** Stage 1 (control-plane foundation) brings up `pangolin-core-arm1` + `langfuse` + `observability`
- **AND** Stage 2 (the 3 surfaces) brings up `hermes` + `openclaw` + `openchamber` in that order
- **AND** Stage 3 (Pangolin routes) applies the 3 blueprints via the Pangolin Integration API
- **AND** Stage 4 (health checks) returns 200 for all 3 endpoints
- **AND** Stage 5 (validate) reports 0 hard failures
- **AND** the omnibus completes within 15 minutes on the arm1-oci host

#### Scenario: Operator skips a stage

- **WHEN** `km run procedure deploy-agent-platform-cluster-arm1-oci -- --skip=foundation,observability` runs
- **THEN** Stage 1 (foundation) and Stage 1b (observability) SHALL be skipped
- **AND** the skipped stages SHALL appear in the output with `SKIPPED: <reason>` markers
- **AND** the remaining stages (agent surfaces + Pangolin routes + health + validate) SHALL run as normal

#### Scenario: Remote dev workflow from this Mac

- **WHEN** the `newt` (Pangolin client) stack is up on `bunchloch` (via `km run procedure deploy-newt-bunchloch`)
- **AND** the WireGuard tunnel is established (verified via `docker exec bunchloch-newt -- newt --version` showing 1.14.0)
- **THEN** from this Mac, `curl https://hermes.cianfhoghlaim.ie/api/health` returns 200 (proves the newt → Pangolin → arm1-oci → hermes path works end-to-end)
- **AND** the same path works for `openclaw.cianfhoghlaim.ie` and `openchamber.cianfhoghlaim.ie`

### Requirement: iac:sync:sites provisions newt sites via the Pangolin Integrations API

The system SHALL provide a `bun run iac:sync:sites` command that walks
`stacks/*/site.yaml` and provisions each newt site via the Pangolin
Integrations API (`POST /org/{orgId}/site`). The returned `newtId` +
`newtSecret` SHALL be written to local `~/.env` (under
`PANGOLIN_NEWT_<NAME>_ID` + `PANGOLIN_NEWT_<NAME>_SECRET`) AND to the
Infisical `dev-baile` vault (so other hosts can fetch via Locket).

The command SHALL be idempotent: re-running skips sites that already
exist (via `GET /org/{orgId}/site/{niceId}`) and does not re-issue
credentials.

The command SHALL be wired into `iac:bootstrap` Phase 6 (the missing
"newt deploy" step that was previously a TODO).

#### Scenario: new site is provisioned

- **GIVEN** `stacks/newt/site.yaml` declares `niceId: bunchloch-newt`
- **AND** the site does NOT exist in Pangolin
- **WHEN** `bun run iac:sync:sites` runs
- **THEN** the command POSTs to `/org/{orgId}/site` → gets back `{ id, newtId, newtSecret }`
- **AND** writes `PANGOLIN_NEWT_BUNCHLOCH_ID` + `PANGOLIN_NEWT_BUNCHLOCH_SECRET` to `~/.env`
- **AND** writes the same to Infisical `/pangolin/` (if Infisical auth is configured)
- **AND** the `deploy-newt-bunchloch-v2` procedure can now read the credentials via Locket

#### Scenario: existing site is skipped (idempotent)

- **GIVEN** the bunchloch-newt site already exists in Pangolin
- **WHEN** `bun run iac:sync:sites` runs
- **THEN** the command GETs `/org/{orgId}/site/bunchloch-newt` → finds the existing site
- **AND** does NOT POST a new site
- **AND** does NOT overwrite the existing credentials in `~/.env`
- **AND** logs `bunchloch-newt (already exists, id=<n>)`

#### Scenario: credentials are written to local .env

- **WHEN** `bun run iac:sync:sites` runs with a valid Pangolin API key
- **AND** Infisical auth is NOT configured
- **THEN** the command writes newtId + newtSecret ONLY to local `~/.env`
- **AND** logs a warning: `infisical: not configured — credentials will be written to local .env only`
- **AND** the procedure still succeeds (exit 0)

#### Scenario: iac:bootstrap Phase 6 calls iac:sync:sites

- **WHEN** `bun run iac:bootstrap` runs
- **THEN** Phase 6 (the "Newt (Pangolin tunnel client)" step) calls `await syncSites()`
- **AND** the bootstrap is no longer stuck at a TODO for the Newt step

### Requirement: deploy-newt-bunchloch-v2 integrates with iac:sync:sites + asserts newt v1.14.0

The system SHALL provide a `deploy-newt-bunchloch-v2` Komodo procedure
that supersedes the legacy `deploy-newt-bunchloch` (v1). The v2
procedure SHALL integrate with the `iac:sync:sites` command (which
auto-provisions the bunchloch-newt site via the Pangolin Integrations
API) AND SHALL assert that the running newt container is at v1.14.0
(the canonical pin from `stacks/newt/IMAGE`).

The v2 procedure SHALL have 5 stages:
1. **preflight** — verify docker is present, env vars hydrated, locket healthy
2. **iac-provision** — `bun run iac:sync:sites` (provisions the site if not already)
3. **stackup** — `mkdir -p ~/.local/newt && docker compose up -d` (creates run-directory on first use)
4. **wireguard-tunnel** — wait up to 60s for the "tunnel established" log line + dump `wg show`
5. **health-checks** — all 4 services Up, locket secrets resolved, newt version = 1.14.0, WireGuard handshake present, komodo-core reachable

The v2 procedure is wired into the cross-cutting prereq order (runs
AFTER `locket-deploy`, BEFORE the per-host syncs).

#### Scenario: iac-provision runs as Stage 2

- **WHEN** `km run procedure deploy-newt-bunchloch-v2` runs
- **THEN** Stage 2 calls `bun run iac:sync:sites`
- **AND** the site is auto-provisioned via the Pangolin Integrations API
- **AND** the newtId + newtSecret are written to local `~/.env` + Infisical

#### Scenario: newt version mismatch detected

- **WHEN** the bunchloch-newt container is at v1.13.0 (or any version ≠ 1.14.0)
- **THEN** Stage 4 health-checks emits `newt version MISMATCH (expected 1.14.0)`
- **AND** the procedure exits non-zero
- **AND** the operator must re-deploy with the pinned IMAGE

#### Scenario: all 5 health-checks pass

- **WHEN** `km run procedure deploy-newt-bunchloch-v2` runs after `iac:sync:sites` has succeeded
- **THEN** Stage 5 verifies:
  1. 4 services Up (bunchloch-locket, bunchloch-newt, bunchloch-periphery, bunchloch-beszel-agent)
  2. Locket has resolved 3 secrets (NEWT_ID, NEWT_SECRET, PERIPHERY_ONBOARDING_KEY)
  3. newt version = 1.14.0
  4. WireGuard handshake present (`wg show` returns a "latest handshake" line)
  5. komodo-core on arm1-oci is reachable via the Pangolin mesh
- **AND** the procedure exits 0

### Requirement: deploy-pangolin-newt-arm1-oci brings the arm1-oci-side newt client online

The system SHALL provide a `deploy-pangolin-newt-arm1-oci` Komodo
procedure that brings the secondary newt client online on the
`arm1-oci` control plane. This secondary newt is required so that
arm1-oci-hosted services (hermes, openclaw, openchamber, langfuse)
can route through the local gerbil WireGuard server without going
back to bunchloch first.

The procedure SHALL have 5 stages (mirrors `deploy-newt-bunchloch-v2`):
1. **preflight** — verify Pangolin + Infisical are reachable + healthy
2. **iac-provision** — `bun run iac:sync:sites` (auto-provisions the arm1-oci newt site)
3. **stackup** — extend the pangolin compose with the newt service (`docker compose -f compose.yaml -f newt.yaml -f newt.sidecar.yaml up -d newt`)
4. **wireguard-tunnel** — wait up to 60s + dump `wg show`
5. **health-checks** — 5 verifications including newt v1.14.0 assertion + pangolin-core reachability

The v2 procedure is wired into the cross-cutting prereq order (runs
AFTER `locket-deploy`, BEFORE `deploy-newt-bunchloch-v2`).

#### Scenario: iac-provision runs as Stage 2

- **WHEN** `km run procedure deploy-pangolin-newt-arm1-oci` runs
- **THEN** Stage 2 calls `bun run iac:sync:sites`
- **AND** the arm1-oci newt site is auto-provisioned via the Pangolin Integrations API
- **AND** the newtId + newtSecret are written to local `~/.env` + Infisical (under `PANGOLIN_NEWT_ARM1_*`)

#### Scenario: newt version mismatch detected

- **WHEN** the pangolin-newt container is at v1.13.0 (or any version ≠ 1.14.0)
- **THEN** Stage 5 health-checks emits `newt version MISMATCH (expected 1.14.0)`
- **AND** the procedure exits non-zero

#### Scenario: all 5 health-checks pass

- **WHEN** `km run procedure deploy-pangolin-newt-arm1-oci` runs after `iac:sync:sites` has succeeded
- **THEN** Stage 5 verifies:
  1. pangolin-newt container is Up
  2. newt-sidecar Locket has resolved 2 secrets (NEWT_ARM1_ID, NEWT_ARM1_SECRET)
  3. newt version = 1.14.0
  4. WireGuard handshake present
  5. pangolin-core on arm1-oci remains reachable (the newt shouldn't break the control plane)
- **AND** the procedure exits 0
- **AND** the arm1-oci-hosted services (hermes, openclaw, openchamber) are now reachable via the Pangolin mesh without going through bunchloch

### Requirement: iac:bootstrap orchestrates all 5 auth components as a single tightly-integrated system

The system SHALL provide a `bun run iac:bootstrap` command that
orchestrates all 5 auth components (Pulumi → Infisical → Pocket ID →
Pangolin → Komodo → Tinyauth → Newt → sync) as a single, idempotent
end-to-end flow. Each phase checks the current state and (re)deploys as
needed.

Pocket ID + Tinyauth SHALL be first-class systems in the IaC (not
manually configured outside the bons). The bootstrap SHALL include a
new `iac:bootstrap-pocketid-admin` subcommand that creates the first
admin user + the bons-iac OIDC client via the Pocket ID admin API
(only the operator's browser-passkey-registration is manual).

The system SHALL also provide `iac:health` that does a 6-way check
(added Pocket ID + Tinyauth on top of the previous 4-way check of
Komodo + Pangolin + Infisical + Newt). Each check SHALL report a clear
actionable error message.

#### Scenario: iac:bootstrap runs end-to-end on cold-boot

- **WHEN** the bons host has no Pocket ID, no Tinyauth, no newt containers
- **THEN** `iac:bootstrap` orchestrates all 9 phases in order:
  1. Pulumi (TODO)
  2. Infisical secrets
  3. Pocket ID deploy + health check (via `km run procedure deploy-pocket-id-bunchloch`)
  4. Auth wiring (creates bons-iac OIDC client via admin API; mints Pangolin API key via OIDC client_credentials)
  5. Pangolin private resources
  6. Komodo Core + Periphery
  7. Tinyauth deploy + health check (via `km run procedure deploy-tinyauth-bunchloch`)
  8. Newt (sync-sites)
  9. All sync commands
- **AND** the bootstrap is idempotent: re-running on a warm cluster skips
  the already-done phases.

#### Scenario: iac:bootstrap-pocketid-admin is run after a DB wipe

- **GIVEN** the Pocket ID DB has 0 users (e.g. after a wipe)
- **AND** `POCKETID_ADMIN_PASSWORD` is in env
- **WHEN** `bun run iac:bootstrap-pocketid-admin` runs
- **THEN** the command:
  1. Logs in to Pocket ID as admin (uses `POCKETID_ADMIN_PASSWORD`)
  2. Enables signup
  3. Creates a signup token (1-hour expiry)
  4. Prints the signup URL to stdout (operator opens in browser)
  5. Waits for operator to press ENTER
  6. Verifies the user was created (via the admin API)
  7. Disables signup (security)
  8. Creates the bons-iac OIDC client (with `client_credentials` grant)
  9. Writes `POCKETID_CLIENT_ID` + `POCKETID_CLIENT_SECRET` to `~/.env`
  10. Emits a JSON audit record to `/tmp/pocketid-bootstrap-{ts}.json`
- **AND** the operator's next `bun run iac:health` exits 0 for the
  Pocket ID + tinyauth checks.

#### Scenario: iac:health returns 6-way actionable errors

- **WHEN** the user runs `bun run iac:health` with a broken auth state
- **THEN** the command reports the state of each of the 6 surfaces:
  - `komodo`: count of servers + stacks (or auth error)
  - `pangolin`: `{"healthy": true|false, "detail": "..."}`
  - `infisical`: `{"healthy": true|false, "detail": "..."}`
  - `newt (bunchloch)`: container status + version + WireGuard handshake
  - `pocket-id`: v{version}, {dbUsers} users, {dbOidcClients} OIDC clients, signup=on|off
  - `tinyauth`: HTTP status of `/api/health`
- **AND** if Pocket ID DB is empty, the message is actionable:
  `pocket-id: v2.9.0 but DB is empty (run: bun run iac:bootstrap-pocketid-admin)`
- **AND** if Tinyauth container is NOT Up:
  `tinyauth: http://tinyauth.cianfhoghlaim.ie returned {status_code}`

#### Scenario: Pocket ID + Tinyauth are part of the cross-cutting prereq order

- **GIVEN** the bons cross-cutting prereq order
- **WHEN** Komodo pulls the resource-sync
- **THEN** the order is:
  1. `pangolin-first`
  2. `komodo-core`
  3. `infisical-first`
  4. `locket-deploy`
  5. `deploy-pocket-id-bunchloch` (NEW in this change)
  6. `deploy-tinyauth-bunchloch` (NEW in this change)
  7. `deploy-pocket-id-arm1-oci` (NEW in this change; migration target)
  8. `deploy-pangolin-newt-arm1-oci`
  9. `deploy-newt-bunchloch-v2`
- **AND** the operator can run any one of them in any order (each is
  idempotent and health-checks its own state)

### Requirement: OpenChamber uses the existing Bunchloch OpenCode server

The agent-platform cluster SHALL support OpenChamber as a Bunchloch development
surface backed by the existing host OpenCode `1.17.9` server. OpenChamber MUST
use an explicit external-server configuration with `OPENCODE_HOST`,
`OPENCODE_PORT=4096`, and `OPENCODE_SKIP_START=true`, and MUST NOT create a
parallel bundled OpenCode runtime for this surface.

#### Scenario: The external host is the sole OpenCode runtime

- **WHEN** OpenChamber is started for Bunchloch development
- **THEN** requests are sent to the host OpenCode server at port `4096`
- **AND** no in-container OpenCode process is started or used as a fallback

### Requirement: Host OpenCode sessions and MCP configuration remain authoritative

The cluster SHALL preserve the host OpenCode server as the owner of OpenCode
sessions, project metadata, enabled MCP configuration, and related credentials.
OpenChamber MUST consume those resources through the external server rather than
copying, rehydrating, or shadowing them in its own config volume.

#### Scenario: Existing sessions are visible through OpenChamber

- **WHEN** the host OpenCode server has an existing session for
  `/Users/cianmacandeisigh/dev/kings_college_galway`
- **THEN** OpenChamber can list and reopen that session through the external
  server
- **AND** the session resolves to the identical absolute repository path

#### Scenario: Enabled MCP list is preserved

- **WHEN** the host OpenCode server exposes its enabled MCP list
- **THEN** OpenChamber displays or can query the same enabled MCP names and
  statuses through the external server
- **AND** no MCP credential or configuration is duplicated into the
  OpenChamber-owned persistent volume

### Requirement: Agent-surface parity verification

The agent-platform cluster SHALL provide a verification procedure for the
Bunchloch OpenChamber surface that checks OpenChamber `/health`, host OpenCode
`/global/health`, session visibility, the enabled MCP list, the identical
repository mount, git availability, and loopback-only binding. The procedure
MUST fail if any parity check fails or if plaintext secrets are detected.

#### Scenario: Full parity verification passes

- **WHEN** the verification procedure runs after both services start
- **THEN** OpenChamber `/health` and OpenCode `/global/health` return HTTP 200
- **AND** an existing host session opens at the canonical repository path with
  the expected enabled MCP list
- **AND** git, secret, mount, and loopback checks all pass

#### Scenario: A parity check fails

- **WHEN** the external server is unavailable, a session is missing, an MCP
  list differs, or a security check fails
- **THEN** the verification procedure exits non-zero
- **AND** it reports the failed check without printing secret values

### Requirement: Bundling procedure `deploy-agent-fleet-bunchloch`

The system SHALL provide a Komodo procedure
`deploy-agent-fleet-bunchloch.toml` at
`bonneagar/komodo/procedures/` that bundles the 12 main
agents + the 8 NCCA subject agents + the 3 educational agents
into a single 4-stage omnibus:

- **Stage 1**: pre-reqs (cross-cutting prerequisites)
- **Stage 2**: DeployStack 8 supporting stacks (lakehouse + litellm + langfuse + mlflow + cognee + graphiti + lancedb + falkordb)
- **Stage 3**: DeployStack 3 agent surfaces (hermes + openclaw + openchamber)
- **Stage 4**: health verify (12 agents reachable, 8 NCCA agents reachable, 3 educational agents reachable)

The procedure SHALL accept `--skip=<stage>` flags like the
existing `deploy-agent-platform-cluster-bunchloch` omnibus.

#### Scenario: `deploy-agent-fleet-bunchloch` completes all 4 stages

- **GIVEN** the 8 supporting stacks are deployed (lakehouse + litellm + langfuse + mlflow + cognee + graphiti + lancedb + falkordb)
- **WHEN** `km run procedure deploy-agent-fleet-bunchloch`
- **THEN** the 3 agent surfaces SHALL be deployed (hermes + openclaw + openchamber)
- **AND** the 12 main agents SHALL be reachable via `AGENT_REGISTRY`
- **AND** the 8 NCCA subject agents SHALL be reachable via `agents.tuatha.<slug>_agent`
- **AND** the 3 educational agents SHALL be reachable via `agents.meaisinfhoghlaim.educational.<slug>_agent`

#### Scenario: `--skip=` flag accepts per-stage names

- **GIVEN** the operator wants to skip the agent surfaces (already deployed)
- **WHEN** `km run procedure deploy-agent-fleet-bunchloch --skip=stage3`
- **THEN** Stages 1, 2, 4 SHALL run
- **AND** Stage 3 SHALL be skipped
- **AND** the procedure SHALL exit 0

### Requirement: Bundling procedure `deploy-agent-fleet-arm1-oci`

The system SHALL provide a Komodo procedure
`deploy-agent-fleet-arm1-oci.toml` at
`bonneagar/komodo/procedures/` that mirrors the bunchloch
procedure but adapted for `arm1-oci` (the 6-stage omnibus with
`preflight:arm-oci`):

- **Stage 1**: pre-reqs (`preflight:arm-oci` + cross-cutting prerequisites)
- **Stage 2**: control-plane foundation (pangolin + langfuse + observability)
- **Stage 3**: 8 supporting stacks (lakehouse + litellm + mlflow + cognee + graphiti + lancedb + falkordb + mlflow)
- **Stage 4**: 3 agent surfaces (hermes + openclaw + openchamber)
- **Stage 5**: Pangolin routes (12 agents + 8 NCCA + 3 educational)
- **Stage 6**: health verify

The procedure SHALL have `server_id = "arm1-oci"` at the top
of the file (the cross-host dispatch convention from the
`2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow`
change).

#### Scenario: `deploy-agent-fleet-arm1-oci` runs `preflight:arm-oci` as Stage 1

- **GIVEN** the arm1-oci host is reachable
- **WHEN** `km run procedure deploy-agent-fleet-arm1-oci`
- **THEN** Stage 1 SHALL run `preflight:arm-oci` first
- **AND** if `preflight:arm-oci` returns ALL CHECKS PASSED,
  Stages 2-6 SHALL proceed
- **AND** if `preflight:arm-oci` reports any failure, the
  procedure SHALL exit with a non-zero status

#### Scenario: `deploy-agent-fleet-arm1-oci` has `server_id = "arm1-oci"`

- **GIVEN** `bonneagar/komodo/procedures/deploy-agent-fleet-arm1-oci.toml`
- **WHEN** `head -1 deploy-agent-fleet-arm1-oci.toml`
- **THEN** the output SHALL be `server_id = "arm1-oci"`

### Requirement: Operator runbooks `agent-fleet-*-2026-08.md`

The system SHALL provide 2 operator runbooks at
`bonneagar/deploy-runbooks/`:

- `agent-fleet-bunchloch-2026-08.md` — the operator's
  quick-start for bunchloch (the `bun run deploy-agent-fleet-bunchloch`
  5-command sequence)
- `agent-fleet-arm1-oci-2026-08.md` — the operator's
  quick-start for arm1-oci (the `bun run deploy-agent-fleet-arm1-oci`
  6-command sequence with WARP + Locket)

Each runbook SHALL include:

- Pre-flight checks (the 4 outputs the operator must verify)
- Bundled procedure invocation (the 1 `km run` command)
- Post-archive verification (the 3 health endpoints)
- Rollback (the 1 `km run procedure rollback` command)

#### Scenario: `agent-fleet-bunchloch-2026-08.md` runbook exists

- **GIVEN** `bonneagar/deploy-runbooks/agent-fleet-bunchloch-2026-08.md`
- **WHEN** tested against the current bunchloch state
- **THEN** the runbook's 5-command sequence SHALL result in
  all 12 + 8 + 3 agents being reachable within 10 min

#### Scenario: `agent-fleet-arm1-oci-2026-08.md` runbook exists

- **GIVEN** `bonneagar/deploy-runbooks/agent-fleet-arm1-oci-2026-08.md`
- **WHEN** tested against the current arm1-oci state
- **THEN** the runbook's 6-command sequence SHALL result in
  all 12 + 8 + 3 agents being reachable via `*.cianfhoghlaim.ie`
  within 15 min
- **AND** the 3 health endpoints SHALL return 200:
  - `https://hermes.cianfhoghlaim.ie/api/health`
  - `https://openclaw.cianfhoghlaim.ie/api/health`
  - `https://openchamber.cianfhoghlaim.ie/api/health`

### Requirement: iac:rotate-auth mints fresh Pangolin + Komodo + Infisical credentials via Pocket ID OIDC

The system SHALL provide a `bun run iac:rotate-auth` command that
auto-rotates the 3 critical IaC credentials via the Pocket ID OIDC
`client_credentials` flow. The rotation is idempotent and emits a JSON
audit record.

The command:
1. Discovers Pocket ID's `.well-known/openid-configuration`
2. POSTs to Pocket ID's `/oidc/token` with `grant_type=client_credentials`
3. Receives an `access_token` (JWT)
4. POSTs to Pangolin's form-login endpoint to exchange the JWT for a Pangolin session cookie
5. Mints a fresh Pangolin API key via `PUT /org/{orgId}/api-key` → writes to `PANGOLIN_API_KEY` in `~/.env`
6. Reads `KOMODO_PASSWORD` from Infisical (using the universal auth client) → writes to `~/.env`
7. Reads the `INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET` from the Infisical vault → writes to `~/.env`
8. Emits a JSON audit record to `/tmp/auth-rotation-{ts}.json`

The command SHALL be wired into `iac:auth.ts` to replace the existing
`// TODO: Pocket ID OIDC client_credentials flow` placeholder.

#### Scenario: rotation succeeds

- **GIVEN** the Pocket ID OIDC client is configured (client_id + client_secret in `~/.env`)
- **AND** the Infisical universal auth client is functional
- **WHEN** `bun run iac:rotate-auth` runs
- **THEN** all 3 credentials are written to `~/.env` (PANGOLIN_API_KEY, KOMODO_PASSWORD, INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET)
- **AND** a JSON audit record is emitted to `/tmp/auth-rotation-{ts}.json`
- **AND** the procedure exits 0

#### Scenario: rotation fails (Pocket ID unreachable)

- **WHEN** the Pocket ID endpoint returns 503 (unreachable)
- **THEN** the command exits 1
- **AND** the existing credentials in `~/.env` are NOT modified
- **AND** a JSON audit record is emitted to `/tmp/auth-rotation-failed-{ts}.json` with the failure reason

#### Scenario: rotated credentials are used by iac:sync:sites

- **WHEN** `bun run iac:rotate-auth` has just succeeded
- **AND** `bun run iac:sync:sites` runs immediately afterward
- **THEN** the `iac:sync:sites` command uses the freshly-minted `PANGOLIN_API_KEY`
- **AND** the Pangolin Integrations API call succeeds (no 401)
- **AND** the bunchloch-newt site is provisioned + credentials written

### Requirement: Cross-agent context envelope protocol

The system MUST provide a typed context-envelope protocol that any of
the 3 agent surfaces (openclaw + openchamber + hermes) MUST use to hand
context to any other agent surface. The protocol MUST be backed by the
Pydantic v2 model `agents/contracts/context-envelope.py`
(`ContextEnvelope`).

The system MUST provide 3 handler modules — one per surface —
`agents/contracts/openclaw_handler.py`,
`agents/contracts/openchamber_handler.py`,
`agents/contracts/hermes_handler.py`. Each handler MUST implement a
function `receive_envelope(envelope: ContextEnvelope) -> dict[str, Any]`
that unpacks the envelope into the surface's local context.

The protocol MUST be the canonical cross-surface handoff mechanism. No
surface MUST hand context to another via raw HTTP `POST` of an
untyped JSON body.

#### Scenario: openclaw routes a webhook event into hermes

```
# On openclaw (channel fanout):
envelope = ContextEnvelope(
    sender="openclaw",
    recipient="hermes",
    agent_run_id="run_abc123",
    parent_trace_id="trace_def456",
    context_payload={"event": "telegram_message", "from": "@alice",
                     "text": "what's the BIEP v3 status?"},
    mtls_subject="openclaw-telegram-bridge",
)
result = hermes_handler.receive_envelope(envelope)
assert result["status"] == "received"
# hermes now has a RunScope tied to parent_trace_id="trace_def456"
# so any downstream LLM call is correlated to the openclaw webhook
```

#### Scenario: hermes returns a result envelope back to openchamber

```
envelope = ContextEnvelope(
    sender="hermes",
    recipient="openchamber",
    agent_run_id="run_abc123",
    parent_trace_id="trace_def456",
    context_payload={"response": "5 jurisdictions live, 3 deferred",
                     "evidence": ["dagster://asset/biiep_v3_jurisdiction_status"]},
    expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
)
result = openchamber_handler.receive_envelope(envelope)
# openchamber IDE/CLI session now shows the result inline + traces to langfuse
```

### Requirement: OCR / VLM routing layer

The system MUST provide a single OCR / VLM routing layer at
`bonneagar/stacks/ocr-router/` that maps a `requested capability` to
the best-fit backend. The router MUST consult this dispatch matrix:

| Capability | Backend | URL |
|:--|:--|:--|
| `forms` (handwritten + printed forms) | paddleocr | `http://paddleocr:8000/v1` |
| `layout` (dense + sparse layout, tables, sections) | mlx-omni | `http://mlx-omni:10240/v1` |
| `tables+latex` (math, table extraction) | olmocr | `http://olmocr:8003/v1` |
| `doctags` (IBM DocTags format) | docling-serve | `http://docling-serve:5001/v1` |
| `gaelic` / `english` vision (gemma-4 + qwen3-vl) | llama-swap | `http://llama-swap:8080/v1` |
| `tesseract-fallback` (legacy) | dots-ocr | `http://dots-ocr:8001/v1` |

The system MUST keep the router as a separate stack (NOT embed the
routing logic in litellm) so that:

1. litellm's role stays "OpenAI-compatible API gateway"; the OCR router
   is the "OCR / VLM capability gateway".
2. The router is the only place that knows the backend ↔ capability
   mapping, so a new backend (e.g. paddleocr-vl-2) can be added without
   touching litellm.
3. The router exposes the OCR_WEBHOOK_URL convention (see BIEP v3 spec
   delta Requirement "OCR completion webhook").

#### Scenario: a Dagster asset asks for table extraction

```
$ curl -X POST http://ocr-router.cianfhoghlaim.ie/ocr \
    -H "Authorization: Bearer $OCR_ROUTER_API_KEY" \
    -d '{"capability": "tables+latex", "image_url": "s3://lakehouse/lc_chem_2024.pdf"}'
{
  "result_url": "s3://lakehouse/ocr/tables_latex_lc_chem_2024.json",
  "backend_used": "olmocr",
  "model": "olmocr-2-7b-1025",
  "duration_ms": 4128,
  "webhook_delivered": true
}
```

#### Scenario: capability `forms` routes to paddleocr

```
$ curl -X POST http://ocr-router.cianfhoghlaim.ie/ocr \
    -d '{"capability": "forms"}'
[ocr-router] → paddleocr:8000/v1/ocr  (capability match: forms)
[ocr-router] response received in 217ms
{"backend_used": "paddleocr", "model": "pp-ocrv4-multilingual", ...}
```

### Requirement: Skills + MCP server use canonical post-BIEP-v3 paths

The system SHALL require:

1. All `.agents/skills/**/*.md` files to use the canonical
   post-BIEP-v3 namespace (no `sruth/<quadrant>/` legacy paths
   appear as path references — `sruth-subagents` and
   `sruth_browser` historical mentions in skill History sections
   are explicitly exempt).
2. The `croilar-devtools` MCP server to live at the canonical path
   `agents/api/_croilar_convex/devtools.ts` (the legacy
   `agents/_croilar/_croilar_convex/devtools.ts` path MUST be
   absent).
3. A CI gate at `.github/workflows/skill-refs-check.yaml` AND
   `.forgejo/workflows/skill-refs-check.yaml` that fails on any
   remaining `sruth/(cianfhoghlaim|meaisinfhoghlaim|tuatha|croilar|oideachais)/`
   PATH reference (with explicit excludes for the 3 documents that
   intentionally quote legacy paths:
   `docs/audits/2026-07-06-drift-audit.md`,
   `docs/p3-skill-mcp-migration-status.md`, and
   `docs/biiep-v3/post-iac-namespace-rename-secrets.md`).

#### Scenario: No sruth/ PATH references in skills or in the un-excluded docs

- **WHEN** the CI gate runs against `grep -rE "sruth/(cianfhoghlaim|meaisinfhoghlaim|tuatha|croilar|oideachais)/" .agents/skills/ docs/`
- **THEN** zero matches SHALL be present in `.agents/skills/` or in any un-excluded `docs/` file
- **AND** the 3 excluded docs (`docs/audits/2026-07-06-drift-audit.md`,
  `docs/p3-skill-mcp-migration-status.md`,
  `docs/biiep-v3/post-iac-namespace-rename-secrets.md`) MAY contain
  intentional `sruth/` mentions that document the migration itself

#### Scenario: croilar-devtools lives at the canonical path

- **WHEN** `ls agents/api/_croilar_convex/devtools.ts` runs
- **THEN** the file SHALL exist
- **AND** `ls agents/_croilar/` SHALL return "No such file or directory"
  (the old path is gone)

#### Scenario: MCP test passes after migration

- **WHEN** `bun run mcp:test` runs
- **THEN** the suite SHALL pass with the migrated file at the new path

#### Scenario: CI gate present at both GitHub + Forgejo

- **WHEN** `.github/workflows/skill-refs-check.yaml` is inspected
- **THEN** it SHALL contain the strict regex check for `sruth/` PATH
  references AND the `croilar-devtools` canonical-path check
- **AND** `.forgejo/workflows/skill-refs-check.yaml` SHALL exist
  with the same checks (so both CI systems enforce the gate)

### Requirement: PlanetScale Postgres Centralisation (agent-platform-cluster)

The system SHALL migrate the 8-stack agent-platform-cluster (`lakehouse` + `litellm` + `langfuse` + `mlflow` + `logfire` + `cognee` + `graphiti` + `lancedb` + 3 agent surfaces) per the canonical 28-row matrix in `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7.

#### Scenario: A consumer reads the cluster spec

- **GIVEN** the cluster spec is opened alongside the planetscale-postgres-data-strategy umbrella
- **WHEN** they look up `langfuse` / `mlflow` / `cognee` / `logfire`
- **THEN** they see the PlanetScale PG row in the matrix
- **AND** the cluster member row is annotated with "target: PlanetScale PG"

#### Scenario: Cognee moves to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/cognee/compose.yaml` is inspected
- **THEN** `cognee-postgres` SHALL be removed
- **AND** `DATABASE_URL` SHALL point at PlanetScale PG
- **AND** the `pgvector` extension SHALL be enabled on the PlanetScale branch

### Requirement: LiteLLM config is regenerated from MODEL_REGISTRY

The system SHALL regenerate
`bonneagar/stacks/litellm/config/config.yaml` from `MODEL_REGISTRY`
on every `mise run cic:meaisin:litellm-regenerate`. The 5 M3
chokepoint aliases (`kimi/k2`, `glm/5.1`, `minimax/m2.5`, `mimo/2.5`,
`deepseek/flash`) + the 24 `local/vision/*` entries SHALL all be
derived from `MODEL_REGISTRY`.

#### Scenario: LiteLLM config is generated from MODEL_REGISTRY

- **GIVEN** the `MODEL_REGISTRY` populated
- **WHEN** the operator runs
  `mise run cic:meaisin:litellm-regenerate`
- **THEN** `bonneagar/stacks/litellm/config/config.yaml` is regenerated
  from `MODEL_REGISTRY`
- **AND** the file contains no hand-edited model_list entries
- **AND** the 5 ghost-model references (`qwen3-vl-235b-a22b`,
  `glm-4.6v-full`, `qwen3.6-35b-a3b-mtp`, `gemma-4-31B`,
  `gemma-3-27b-it`) are removed

### Requirement: Deployment control panel consumes sync reports

The system SHALL provide a marimo notebook
`notebooks/24_deployment_control_panel.py` that reads the latest
sync report from `stedding/sync-reports/all-{date}.md` and surfaces
the per-layer status + the model registry + the MCP server health.

This requirement was added in the
`2026-08-15-knowledge-sync-loop-v1` change (Change B — the
model-registry change consumes the sync reports as the canonical
"operator's eye" on the repo's knowledge state).

#### Scenario: Deployment control panel shows 5 layer statuses

- **GIVEN** the latest `stedding/sync-reports/all-{date}.md` exists
- **WHEN** a user opens `notebooks/24_deployment_control_panel.py` in marimo
- **THEN** the notebook SHALL display the 5 sync layer statuses
  (paths / ccc / cognee / skills / mcp) at the top with
  pass/fail/info indicators
- **AND** the notebook SHALL list the 14 MCP servers (from
  `opencode.json`)
- **AND** the notebook SHALL list the 54+ agent skills
- **AND** the notebook SHALL have an expander that shows the full
  sync report

### Requirement: sync_health Dagster asset emits sync metadata

The system SHALL provide a Dagster asset `sync_health` at
`orchestration/defs/sync_assets.py` that reads the latest
`stedding/sync-reports/all-{date}.md` and emits metadata for the
5 sync layers.

This requirement was added in the
`2026-08-15-knowledge-sync-loop-v1` change (Change B — the sync
metadata is consumed by the deployment control panel + the
`stale_skill_alert` Dagster job).

#### Scenario: sync_health materializes on cron

- **GIVEN** the `0 */4 * * *` cron fires (every 4 hours)
- **WHEN** the `sync_health` asset materializes
- **THEN** it SHALL emit the following Dagster metadata:
  `paths_sync_time`, `ccc_chunk_count`, `cognee_cluster_count`,
  `skill_pass_rate`, `mcp_server_count_healthy`,
  `layer_statuses` (per-layer pass/fail), `path_pattern_counts`
  (per-pattern count from the paths report)
- **AND** it SHALL trigger a downstream Dagster job
  `stale_skill_alert` if `skill_pass_rate < 0.95`

### Requirement: sync_report_sensor fires on new reports

The system SHALL provide a Dagster sensor `sync_report_sensor` that
fires when a new `stedding/sync-reports/all-{date}.md` file is
created (i.e. after `mise run sync:all`).

#### Scenario: sync_report_sensor fires on new file

- **GIVEN** the sensor is running with `minimum_interval_seconds=3600`
- **WHEN** a new `stedding/sync-reports/all-{date}.md` file is created
  (e.g. after `mise run sync:all`)
- **THEN** the sensor SHALL enqueue a `RunRequest` for the
  `sync_health` asset
- **AND** the `sync_health` asset SHALL re-materialize
- **AND** the `sync_health_refresh` job SHALL complete within 60 seconds

### Requirement: deployment-choice.yaml is the canonical enablement file

The system SHALL provide a `deployment-choice.yaml` file at the
repo root that records which families in `MODEL_REGISTRY` are
enabled for production (default: all). The file SHALL have the
shape:

```yaml
enabled_families:
  - ocr_vision
  - text_llm
  - embedder
  - image_gen
  - voice
  - translation
enabled_jurisdictions:
  - ireland
  - england
disabled_families: []
disabled_models: []
```

#### Scenario: deployment-choice.yaml is read at startup

- **WHEN** the agent runtime (hermes / openclaw / openchamber) starts
- **THEN** it SHALL read `deployment-choice.yaml`
- **AND** the runtime SHALL only call `MODEL_REGISTRY.model_for(...)`
  for families in `enabled_families`
- **AND** if `deployment-choice.yaml` is missing, the runtime SHALL
  default to all-families-enabled + log a warning

### Requirement: All hardcoded model strings across the platform route through MODEL_REGISTRY

The system SHALL route every model invocation through `MODEL_REGISTRY.model_for(family, role, language=None)` or `MODEL_REGISTRY.filter(family=...)`. No hardcoded model strings (e.g., `gpt-4o-mini`, `minimax-m3`, `chatterbox`, `gemini-2.5-pro`) SHALL remain outside the registry whitelist. The `mise run lint:registry` CI gate SHALL fail any commit that introduces a hardcoded model string.

This requirement was added in the
`2026-07-29-complete-remaining-model-registry-migrations-v1` change
(per issue #141 follow-up to the deferred Phase 1.3-1.10 + 1.12-1.19
from `2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`).

#### Scenario: New model added via registry, not code

- **GIVEN** a new `text_llm` model is added to `MODEL_REGISTRY`
- **WHEN** the operator runs `mise run lint:registry`
- **THEN** the audit SHALL pass (no hardcoded strings)
- **AND** every agent that calls `model_for("text_llm", "default")`
  SHALL pick up the new model automatically (no code changes)

#### Scenario: Operator disables a model via deployment-choice.yaml

- **GIVEN** `deployment-choice.yaml` has `disabled_models: ["minimax-m3"]`
- **WHEN** the agent runtime starts
- **THEN** `model_for("text_llm", "default")` SHALL return the next
  enabled model in the family
- **AND** the audit log at `stedding/deployment-control-panel/audit.log`
  SHALL record the disabled model with timestamp

### Requirement: Phase 7 of deploy-full.sh runs the memory-stack doctor

The system SHALL extend `scripts/deploy-full.sh` Phase 7
(`data-stacks-up`) to invoke `bun run scripts/lakehouse-memory-doctor.ts`
after the 8 supporting stacks (litellm + langfuse + mlflow + logfire +
cognee + graphiti + lancedb + falkordb) come up. The probe SHALL fail
the phase if any of the 5 memory backends reports a `not_healthy`
status.

#### Scenario: All 5 memory backends return healthy

- **WHEN** `mise run deploy:full --phase=7` runs
- **THEN** the doctor SHALL probe all 5 memory backends
- **AND** the JSON health report SHALL be emitted at `stedding/memory-health/<utc-ts>.json`
- **AND** the phase SHALL exit 0
- **AND** the deploy-state.json checkpoint SHALL record `phase_7_memory_doctor: success`

#### Scenario: One memory backend reports unhealthy

- **WHEN** the doctor reports `falkordb: not_healthy`
- **THEN** the phase SHALL exit non-zero
- **AND** the deploy-state.json checkpoint SHALL record `phase_7_memory_doctor: failed: falkordb_unhealthy`
- **AND** the operator SHALL see the actionable error in the deploy log

#### Scenario: Re-running deploy:full resumes from the failed Phase 7

- **WHEN** `mise run deploy:full` runs after a Phase 7 failure
- **THEN** Phases 1-6 SHALL be skipped (already `success`)
- **AND** Phase 7 SHALL re-run the doctor
- **AND** if the underlying issue has been resolved, the doctor SHALL report `healthy: 5/5` and the checkpoint SHALL be updated

### Requirement: CopilotKit actions-stubbed lint invariant

The system SHALL fail `mise run lint:copilotkit-actions-stubbed` if
any action function in `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts`
returns the literal string `"TBD"` (the 12-of-14 stub class per the
`agentic-frontend-frameworks` spec).

The reason: per the `2026-08-10-copilotkit-action-wiring-v1` change
proposal, 12 of 14 CopilotKit actions return placeholder data. The
`leaving-cert.cianfhoghlaim.ie` chat UX is degraded. Closing this
gap requires (a) wiring real handlers (5 new files in
`apps/api/src/copilotkit/handlers/{syllabus,marking,ocr,learning_outcome,student_progress}.ts`)
and (b) a lint gate that prevents re-introduction of the stub
pattern.

This requirement adds the lint gate (the action wiring itself is
archived as part of Mega-1 Phase 4).

#### Scenario: Developer adds a new stub action

- **WHEN** a developer adds:
  ```typescript
  appRuntimeClient.actions.lookupFoo = async (): Promise<FooResult> => {
    return { result: "TBD", };  // placeholder
  };
  ```
- **THEN** `mise run lint:copilotkit-actions-stubbed` exits 1 with
  `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts:<line>: stub action detected — wire to a real handler`

#### Scenario: Real action passes the lint

- **WHEN** the action returns real data from a BAML call, DuckLake
  query, or Convex lookup
- **THEN** the lint exits 0

#### Scenario: Test fixture with stub action is exempt

- **GIVEN** `actions.test.ts` contains stub actions for unit tests
- **WHEN** the lint runs
- **THEN** it exits 0 (the `.test.ts` filename matches the test
  exemption pattern)

## Cross-references

- [`agent-memory-systems`](../agent-memory-systems/spec.md) — the 5 memory backends (Cognee + Graphiti + LanceDB + FalkorDB + Memgraph)
- [`agent-observability`](../agent-observability/spec.md) — the observability stack (Langfuse + MLflow + RAGAS + Logfire)
- [`agent-registry`](../agent-registry/spec.md) — the 12-agent + 9-MCP registry
- [`agent-fleet-orchestration`](../../.agents/skills/agent-fleet-orchestration/SKILL.md) — the orchestration skill
- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) — the 88 stacks at `bonneagar/stacks/`
- [`motherduck-architecture`](../../.agents/skills/motherduck/motherduck-architecture/SKILL.md) — the MotherDuck storage pattern (BYOB + DuckLake)

## Migrated from: *(none)*
