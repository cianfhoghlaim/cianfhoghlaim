# Agent Observability — Code-side Langfuse + Logfire Defaults Delta

> This file is the change-side delta for
> `2026-07-02-align-cianfhoghlaim-env-with-stacks`. It applies on
> top of the canonical `agent-observability` spec at
> `../../../../specs/agent-observability/spec.md` and on top of the
> prior `2026-07-02-replace-private-images-and-bring-wave2` delta.

## ADDED Requirements

### Requirement: Langfuse /api/public/health endpoint on host port 3001

The cianfhoghlaim code default for `LANGFUSE_HOST` SHALL be
`http://localhost:3001` (the langfuse stack's actual host port per
`langfuse/compose.yaml`), not the previous default of
`http://localhost:3000` (the langfuse container's internal port).

#### Scenario: Langfuse default points to the correct host port
- **WHEN** an agent or Dagster asset initialises the Langfuse
  client (e.g. via
  `from cianfhoghlaim.observability.langfuse_config import LANGFUSE_HOST`)
  without overriding `LANGFUSE_HOST` via env var
- **THEN** the default value is `http://localhost:3001`
  (matching the langfuse stack's host port)
- **AND** the agent traces land in the local langfuse stack
  (not on a non-existent port 3000)

#### Scenario: Container-to-container tracing
- **WHEN** the cianfhoghlaim code runs inside a docker container on
  the cianfhoghlaim network
- **THEN** the operator sets `LANGFUSE_HOST=http://langfuse:3000`
  (the docker DNS resolves to the langfuse container's internal
  port 3000)
- **AND** traces flow through the langfuse-web service

### Requirement: Logfire self-host mode bypasses SaaS token

The cianfhoghlaim code SHALL provide a
`logfire_instrument_local_otlp_only()` function that bypasses the
Logfire SaaS `send_to_logfire=True` path and instead routes all
spans to the local OTel collector at
`OTEL_EXPORTER_OTLP_ENDPOINT` (the `logfire` stack in dev mode).

When `LOGFIRE_TOKEN` is empty (the canonical dev state), the
`init_logfire()` function SHALL automatically call
`logfire_instrument_local_otlp_only()` instead of returning False.

#### Scenario: Logfire dev mode without SaaS
- **WHEN** `LOGFIRE_TOKEN` is empty AND the local OTel collector is
  running on `OTEL_EXPORTER_OTLP_ENDPOINT` (default
  `http://logfire:4317` in-docker or `http://127.0.0.1:4317` on-host)
- **THEN** the cianfhoghlaim code initializes Logfire in self-host
  mode (no SaaS required)
- **AND** all spans are sent to the local OTel collector

#### Scenario: Logfire production with SaaS
- **WHEN** `LOGFIRE_TOKEN` is non-empty
- **THEN** `init_logfire()` uses the SaaS path (sends to Logfire
  cloud)
- **AND** the local OTel collector can ALSO be configured to forward
  to Logfire cloud (handled in the logfire stack's collector config,
  not in the cianfhoghlaim code)
