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
- **AND** the `openclaw` container joins the `cianchoghlaim` bridge network
- **AND** Locket injects the `dev-baile/openclaw/*` Infisical secrets
- **AND** the WS protocol v3 handshake (challenge + auth + connect) returns 200 at `ws://openclaw.cianfhoghlaim.ie:18789`

#### Scenario: openchamber.cianfhoghlaim.ie is reachable

- **WHEN** `km run procedure deploy-openchamber-arm1-oci` completes
- **THEN** `https://openchamber.cianfhoghlaim.ie/api/health` returns 200
- **AND** the openchamber UI serves its bundled React frontend at `https://openchamber.cianfhoghlaim.ie/`
- **AND** the `openchamber` container joins the `cianchoghlaim` bridge network
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

## Cross-references

- [`agent-memory-systems`](../agent-memory-systems/spec.md) — the 5 memory backends (Cognee + Graphiti + LanceDB + FalkorDB + Memgraph)
- [`agent-observability`](../agent-observability/spec.md) — the observability stack (Langfuse + MLflow + RAGAS + Logfire)
- [`agent-registry`](../agent-registry/spec.md) — the 12-agent + 9-MCP registry
- [`agent-fleet-orchestration`](../../.agents/skills/agent-fleet-orchestration/SKILL.md) — the orchestration skill
- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) — the 88 stacks at `bonneagar/stacks/`
- [`motherduck-architecture`](../../.agents/skills/motherduck/motherduck-architecture/SKILL.md) — the MotherDuck storage pattern (BYOB + DuckLake)

## Migrated from: *(none)*
