# Agent Observability Capability

## Purpose

`agent-observability` is a capability of the Cianfhoghlaim platform. The
corresponding source code lives at `oideachais/observability/` (the
Langfuse + MLflow + Logfire + Datadog integration) and
`meaisinfhoghlaim/evaluation/ragas_pipeline.py` (the RAGAS evaluation
harness). See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This spec was renamed from `observability` to disambiguate it from
infrastructure-level observability (Prometheus + Grafana + Loki, which is
under `infrastructure-stacks`).

## Background

LLM observability, tracing, prompt management, and evaluation frameworks
for monitoring and optimizing AI systems. The full 441-line description
that was here in the old `observability` spec is in the skills
[`.agents/skills/{langfuse,mlflow,ragas,datadog}/SKILL.md`](../../.agents/skills/).

## Requirements

### Requirement: LLM call tracing

The system SHALL trace every LLM call with input, output, metadata, and
session information.

#### Scenario: Decorator-based tracing

- **GIVEN** a function decorated with `@langfuse.observe()`
- **WHEN** the function is called
- **THEN** the call is traced with input, output, and metadata to
  Langfuse

#### Scenario: Session tracking

- **GIVEN** multiple LLM calls in a session
- **WHEN** tracking session performance
- **THEN** all calls are grouped under the session in Langfuse

### Requirement: RAG evaluation

The system SHALL evaluate RAG pipelines using RAGAS metrics
(faithfulness, answer relevance, context precision, context recall).

#### Scenario: RAGAS evaluation

- **GIVEN** a RAG pipeline (e.g. `oideachais/api/routes/search.py`)
- **WHEN** the pipeline produces a result for a query
- **THEN** the RAGAS evaluator computes the 4 metrics and stores the
  scores in MLflow

## Cross-references

- [`.agents/skills/langfuse/SKILL.md`](../../.agents/skills/langfuse/SKILL.md)
- [`.agents/skills/mlflow/SKILL.md`](../../.agents/skills/mlflow/SKILL.md)
- [`.agents/skills/ragas/SKILL.md`](../../.agents/skills/ragas/SKILL.md)
- [`.agents/skills/datadog/SKILL.md`](../../.agents/skills/datadog/SKILL.md)
- [`oideachais/observability/`](../../oideachais/observability/) (the integration module)
- [`meaisinfhoghlaim/evaluation/`](../../meaisinfhoghlaim/evaluation/) (RAGAS pipeline)
