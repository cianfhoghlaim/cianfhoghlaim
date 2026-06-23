# Spec Delta: agent-observability

## ADDED Requirements

### Requirement: Datadog APM + LLMObs

The system SHALL wire Datadog APM + LLMObs (`@llm`, `@agent`,
`@workflow`, `@task` decorators) into every agent invocation,
with the FastAPI `TraceMiddleware` for HTTP request tracing.

#### Scenario: Agent invocation traced via Datadog

- **GIVEN** a Pydantic AI / Agno / Google ADK agent call
- **WHEN** the agent is invoked
- **THEN** the `ddtrace.llmobs.decorators.agent()` decorator
  SHALL emit a span to Datadog with the model name, prompt,
  completion, token counts, and latency
- **AND** the parent FastAPI request SHALL be linked via
  `TraceMiddleware`

### Requirement: Continuous RAG evaluation as a Dagster asset_check

The system SHALL run the Ragas evaluator as a
`dagster.AssetCheck` on every RAG-asset materialisation, with
the Ragas thresholds (`faithfulness >= 0.8`,
`answer_relevancy >= 0.7`) enforced as quality gates.

#### Scenario: Asset check fails on Ragas regression

- **GIVEN** a RAG asset (e.g. `oideachais-curriculum-search`)
  with Ragas faithfulness baseline 0.92
- **WHEN** a new deployment changes the embedding model
- **THEN** the next asset materialisation's `AssetCheck`
  reports `faithfulness = 0.71` (< 0.8 gate)
- **AND** the asset materialisation is marked as `failed`
- **AND** a Slack notification is sent to the `#kcg-rag` channel
  via the Langfuse webhook

## REMOVED Requirements

(None.)
