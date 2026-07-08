# Agent Observability — Logfire Stack Bring-up Delta

> This file is the change-side delta for
> `2026-07-02-add-lancedb-and-logfire-stacks`. It applies on top
> of the canonical `agent-observability` spec at
> `../../../../specs/agent-observability/spec.md`.

## ADDED Requirements

### Requirement: LLM Observability Tri-Split satisfied on bunchloch

The system SHALL satisfy the LLM Observability Tri-Split rule
(Langfuse + MLflow + Logfire) by deploying the `logfire` stack
on `bunchloch` (the workload host) and wiring the OTel
collector as a secondary OTLP exporter for both `langfuse`
and any Python service that uses the `unified_tracer` decorator
or the `@logfire` instrumentor.

The local `logfire` stack SHALL be the OpenTelemetry Collector
variant described in `agent-observability` §"Logfire Stack
Self-Hosted Compose" (since Pydantic Logfire is SaaS-only and
does not publish a self-hostable Docker image). The collector
SHALL forward traces to `logfire.pydantic.dev` when
`LOGFIRE_TOKEN` is set.

#### Scenario: Three destinations populated per call
- **GIVEN** an LLM call wrapped in the `unified_tracer` decorator
  (or any Pydantic Logfire-instrumented call) on bunchloch
- **WHEN** the call completes
- **THEN** a Langfuse trace SHALL be written (via the langfuse
  stack on `:3001`) AND an MLflow experiment metric SHALL be
  logged (via the mlflow stack on `:5000`) AND a Logfire span
  SHALL be written (via the OTel collector on `:4317` /
  `:4318`, forwarding to `logfire.pydantic.dev`)
- **AND** no Datadog dependency SHALL be imported (per the
  LLM Observability Tri-Split rule, which explicitly removes
  Datadog in favour of this 3-way split)

#### Scenario: Logfire stack is identifiable from any service
- **WHEN** any Python service on bunchloch wants to forward
  OTLP traces to the local collector
- **THEN** it SHALL set
  `OTEL_EXPORTER_OTLP_ENDPOINT=http://logfire:4317` (gRPC) or
  `OTEL_EXPORTER_OTLP_ENDPOINT=http://logfire:4318` (HTTP) in
  its environment
- **AND** the collector SHALL be reachable on the
  `cianfhoghlaim` docker network at the host name `logfire`
  (the Compose service name)