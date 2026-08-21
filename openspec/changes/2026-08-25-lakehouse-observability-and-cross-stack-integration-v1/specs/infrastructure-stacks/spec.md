# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: The lakehouse stack MUST route OTLP traces through a fan-out collector to both Logfire cloud AND Langfuse

The lakehouse stack SHALL route OpenTelemetry traces emitted by its 16 services
through the `otel-collector` service (which is part of the lakehouse compose
project, optional profile `otel`) OR through the existing `logfire` stack's
`logfire-otel` service (cross-stack fan-out via Docker DNS).

The trace pipeline SHALL:
1. **Receive** OTLP traces on gRPC :4317 + HTTP :4318
2. **Batch** with `memory_limiter` + `batch` processors
3. **Fan out** to BOTH:
   - **Logfire cloud** (SaaS) via the `logfire` exporter + `LOGFIRE_TOKEN` env var
   - **Langfuse** (self-hosted) via the `otlphttp/langfuse` exporter + `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY`
4. **Health check** on :8888 (otelcol health extension)

The `lakehouse:stack-doctor` SHALL fail any PR that removes `OTEL_EXPORTER_OTLP_ENDPOINT` from any of the 16 lakehouse services.

#### Scenario: Operator brings up the lakehouse + observability stack

- **WHEN** the operator runs `docker compose --profile otel up -d` from `bonneagar/stacks/lakehouse/`
- **THEN** all 16 lakehouse services emit OTLP traces to `otel-collector:4317`
- **AND** the otel-collector fans out to BOTH Logfire cloud + Langfuse
- **AND** `mise run lakehouse:preflight` reports all 9 endpoints healthy + the 3 observability exports working

#### Scenario: Operator brings up the lakehouse without the observability profile

- **GIVEN** the operator only runs `docker compose -f compose.yaml -f sidecar.yaml up -d` (without `--profile otel`)
- **WHEN** a lakehouse service emits an OTLP trace
- **THEN** the trace goes to `http://otel-collector:4317`
- **AND** the otel-collector service is NOT running (skipped because no `--profile otel`)
- **AND** the trace is dropped silently (otelcol SDK retries with backoff)
- **AND** the service continues to operate normally (degraded observability, not degraded functionality)

#### Scenario: Cross-stack fan-out via the existing logfire stack

- **GIVEN** the lakehouse stack is deployed (via Komodo)
- **AND** the `logfire-bunchloch` stack is also deployed (via Komodo)
- **WHEN** the operator sets `LAKEHOUSE_OTLP_ENDPOINT=http://logfire-otel:4317` in the lakehouse `.env.local`
- **THEN** all 16 lakehouse services route traces to `logfire-otel:4317`
- **AND** the logfire stack's collector (per its own `config/otelcol.yaml`) fans out to Logfire cloud + Langfuse
- **AND** the trace is visible in BOTH backends

### Requirement: The `mise run lakehouse:all:up` task MUST bring up the complete data plane

The `data:all:up` mise task SHALL bring up the **complete data plane** in dependency order:
1. `lakehouse` (16 services + 14 databases + 8 buckets)
2. `logfire` (otel-collector + Langfuse + Logfire fan-out)
3. `langfuse` (LLM observability web + worker)
4. `mlflow` (experiment tracking)
5. `dagster` (orchestration)

The task SHALL use Komodo's stack-depends_on contract (not docker-compose cross-project depends_on which doesn't work). Operators SHALL see the full data plane come up in sequence via a single `mise run lakehouse:all:up` command.

#### Scenario: Operator brings up the complete data plane

- **WHEN** the operator runs `mise run lakehouse:all:up` on bunchloch
- **THEN** lakehouse comes up first (16 services healthy)
- **AND** logfire comes up second (otel-collector + Langfuse fan-out wired)
- **AND** langfuse comes up third (uses lakehouse-postgres + lakehouse-garage)
- **AND** mlflow comes up fourth (uses lakehouse-postgres + lakehouse-garage)
- **AND** dagster comes up last (uses lakehouse-postgres + langfuse for tracing)
- **AND** `mise run lakehouse:preflight` reports 9/9 endpoints healthy

#### Scenario: Operator tears down the complete data plane

- **WHEN** the operator runs `mise run lakehouse:all:down`
- **THEN** dagster comes down first (the highest-level orchestration)
- **AND** mlflow comes down second
- **AND** langfuse comes down third
- **AND** logfire comes down fourth
- **AND** lakehouse comes down last (the foundation)

## REMOVED Requirements

(None — no requirement removed in this change.)