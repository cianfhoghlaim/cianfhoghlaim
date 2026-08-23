# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: Substrate boundary — agent-platform-cluster covers the 8-stack substrate + 3 agent surfaces

The system SHALL recognize that `agent-platform-cluster` covers:

- The 8-stack substrate: lakehouse + litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb
- The 3 agent surfaces: openclaw + openchamber + hermes
- LiteLLM as the M3 chokepoint (the unified LLM router)
- The iac:bootstrap + iac:sync:* orchestration that brings the 8 stacks up

The system SHALL NOT duplicate the concerns of `agent-observability`, which covers the observability LAYER (Langfuse @observe + MLflow tracking + RAGAS evaluation + structlog + Logfire fan-out).

Where `agent-platform-cluster` and `agent-observability` BOTH reference Langfuse:
- `agent-platform-cluster` covers the deployment topology (the Langfuse stack at `bonneagar/stacks/langfuse/`)
- `agent-observability` covers the LLM tracing API + the @observe integration

Where `agent-platform-cluster` and `agent-memory-systems` BOTH reference Cognee + Graphiti + LanceDB:
- `agent-platform-cluster` covers the deployment topology (the Cognee stack at `bonneagar/stacks/cognee/` + the Graphiti stack at `bonneagar/stacks/graphiti/` + the LanceDB sidecar)
- `agent-memory-systems` covers the memory cascade pattern (which backend wins per query) + the 5-backend `MemoryLayer` Protocol

This boundary clarification is added by the 2026-08-22-openspec-audit-and-merge-v1 audit.

#### Scenario: Agent looks up Cognee deployment topology

- **WHEN** an agent reads `openspec/list --specs` to find the spec for "Cognee stack deployment"
- **THEN** the agent SHOULD load `agent-platform-cluster` (not `agent-memory-systems`)
- **AND** find the Cognee requirements under the "8-stack cluster deployed together" Requirement

#### Scenario: Agent looks up the memory cascade pattern

- **WHEN** an agent reads `openspec/list --specs` to find the spec for "memory cascade"
- **THEN** the agent SHOULD load `agent-memory-systems` (not `agent-platform-cluster`)
- **AND** find the cascade requirements under "Multi-backend agent memory"