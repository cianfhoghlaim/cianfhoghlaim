## ADDED Requirements

### Requirement: Langfuse v3 → v4 migration contract

The system SHALL migrate from `langfuse>=3.x` to `langfuse>=4.0,<5.0` by 2026-11-16 (the v3-Cloud deprecation date). The migration MUST land before that date because v3 will stop receiving security updates + the Python SDK v4 ships Observations-first data model.

The v4 migration contract covers:

1. **SDK v4 surface change**: Removed methods — `start_span`, `start_as_current_span`, `start_generation`, `start_as_current_generation`, `update_current_trace` (decomposed into `propagate_attributes()`, `set_current_trace_io()`, `set_current_trace_as_public()`), `DatasetItemClient` (replaced by `dataset.run_experiment()`).
2. **Env-var rename**: `LANGFUSE_BASEURL` → `LANGFUSE_BASE_URL`.
3. **OpenTelemetry-first**: Default OTel export filters via `is_default_export_span()`; opt-out via `Langfuse(should_export_span=lambda s: True)`.
4. **Pydantic v2 only**: Dropped Pydantic v1 support.
5. **Removed types**: `TraceMetadata`, `ObservationParams`.

#### Scenario: A new agent uses Langfuse tracing

- **GIVEN** the platform is on Langfuse v4
- **WHEN** an agent in `agents/meaisinfhoghlaim/agents/*.py` calls `langfuse.openai().chat.completions.create(...)` (or any framework wrapper)
- **THEN** the call MUST land in the Langfuse UI under "Observations" (not "Traces")
- **AND** the call MUST be visible to `@observe`-decorated BAML functions in the call chain

#### Scenario: A new env var pattern is added to Langfuse

- **WHEN** a new `langfuse-web` sidecar declares `LANGFUSE_BASE_URL`
- **THEN** the v4 server reads it correctly (was `LANGFUSE_BASEURL` in v3)
- **AND** the Locket sidecar MUST inject `LANGFUSE_BASE_URL=https://langfuse.cianfhoghlaim.ie` (not `LANGFUSE_BASEURL`)

### Requirement: LiteLLM v1.91 → v1.97 router updates

The system SHALL upgrade LiteLLM from `>=1.91,<1.98` to `>=1.97,<1.98`. The v1.97 release introduces:

1. **MCP Gateway GA** (v1.85.0) — single endpoint with per-key ACL.
2. **MCP OAuth 2.0 v2 resolver** (v1.91.0) — Hermes can drop its custom auth code.
3. **MCP DCR (Dynamic Client Registration)** (v1.95.0) — agents can self-register as MCP clients.
4. **Tool-result guardrails** (v1.97.0) — output-side safety filters.
5. **SAML 2.0 SSO** (v1.95.0) — operator-driven SSO login for the `litellm` web UI.

The running bunchloch image bumps from `ghcr.io/berriai/litellm-database:v1.91.0` to `:v1.97.0`. The Pangolin reverse proxy MUST expose `/v1/messages` (the Rust-based v1.95.0 endpoint) on the LITELLM subdomain.

#### Scenario: A new LiteLLM model routes through the upgraded gateway

- **GIVEN** the platform is on LiteLLM v1.97 with the MCP Gateway GA
- **WHEN** a 12-agent fleet agent connects to `http://litellm.cianfhoghlaim.ie/v1/mcp`
- **THEN** the gateway authenticates the agent via OAuth 2.0 v2 (or DCR for first-time agents)
- **AND** the model's tool-result guardrails are applied per the agent's ACL
