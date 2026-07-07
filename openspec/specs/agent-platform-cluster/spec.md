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

## Cross-references

- [`agent-memory-systems`](../agent-memory-systems/spec.md) — the 5 memory backends (Cognee + Graphiti + LanceDB + FalkorDB + Memgraph)
- [`agent-observability`](../agent-observability/spec.md) — the observability stack (Langfuse + MLflow + RAGAS + Logfire)
- [`agent-registry`](../agent-registry/spec.md) — the 12-agent + 9-MCP registry
- [`agent-fleet-orchestration`](../../.agents/skills/agent-fleet-orchestration/SKILL.md) — the orchestration skill
- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) — the 88 stacks at `bonneagar/stacks/`
- [`motherduck-architecture`](../../.agents/skills/motherduck/motherduck-architecture/SKILL.md) — the MotherDuck storage pattern (BYOB + DuckLake)

## Migrated from: *(none)*
