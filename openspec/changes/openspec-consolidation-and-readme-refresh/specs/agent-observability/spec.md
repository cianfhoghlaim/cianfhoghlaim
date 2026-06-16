## ADDED Requirements

The `agent-observability` capability is renamed from `observability`
and shrunk to a thin capability pointer at the relevant skills. The
full Requirements + Scenarios are in the canonical spec at
`openspec/specs/agent-observability/spec.md`.

### Requirement: LLM call tracing

The system SHALL trace every LLM call with input, output, metadata,
and session information via Langfuse.

#### Scenario: Decorator-based tracing

- **WHEN** a function decorated with `@langfuse.observe()` is called
- **THEN** the call is traced with input, output, and metadata to
  Langfuse

### Requirement: RAG evaluation

The system SHALL evaluate RAG pipelines using RAGAS metrics.

#### Scenario: RAGAS evaluation

- **WHEN** a RAG pipeline produces a result for a query
- **THEN** the RAGAS evaluator computes faithfulness, answer
  relevance, context precision, and context recall
