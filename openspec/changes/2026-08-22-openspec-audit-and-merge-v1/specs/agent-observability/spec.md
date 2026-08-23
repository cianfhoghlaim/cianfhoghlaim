# Spec Delta: agent-observability

## ADDED Requirements

### Requirement: Observability boundary — agent-observability covers the observability LAYER only

The system SHALL recognize that `agent-observability` covers the observability layer only:

- Langfuse + Logfire + MLflow + RAGAS + structlog (the observability stack)
- LLM call tracing via `@observe` decorators
- RAG evaluation via RAGAS as Dagster `asset_check`
- Cost + prompt management via Langfuse v4 SDK
- OpenTelemetry fan-out to all observability backends

The system SHALL NOT duplicate the concerns of `agent-platform-cluster`, which covers the substrate (8-stack cluster: lakehouse + litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb) + the 3 agent surfaces (openclaw + openchamber + hermes).

Where `agent-observability` and `agent-platform-cluster` BOTH reference Langfuse:
- `agent-platform-cluster` covers the deployment topology (the Langfuse stack at `bonneagar/stacks/langfuse/`)
- `agent-observability` covers the LLM tracing API + the @observe integration

This boundary clarification is added by the 2026-08-22-openspec-audit-and-merge-v1 audit.

#### Scenario: Agent looks up Langfuse deployment topology

- **WHEN** an agent reads `openspec/list --specs` to find the spec for "Langfuse stack deployment"
- **THEN** the agent SHOULD load `agent-platform-cluster` (not `agent-observability`)
- **AND** find the Langfuse requirements under the "8-stack cluster deployed together" Requirement

#### Scenario: Agent looks up Langfuse @observe tracing API

- **WHEN** an agent reads `openspec/list --specs` to find the spec for "@observe tracing"
- **THEN** the agent SHOULD load `agent-observability` (not `agent-platform-cluster`)
- **AND** find the @observe requirements under "Langfuse v4 server + SDK deployed before 2026-11-16"