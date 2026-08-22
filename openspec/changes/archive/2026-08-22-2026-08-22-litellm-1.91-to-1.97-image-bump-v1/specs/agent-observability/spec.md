## ADDED Requirements

### Requirement: LiteLLM v1.97.0 image bump — ghcr.io/berriai/litellm-database:v1.97.0

The system SHALL run `ghcr.io/berriai/litellm-database:v1.97.0` (or any 1.97.x stable patch) in the self-hosted `litellm` container, replacing the legacy `v1.91.0`. The bump brings:

- **1.85.0** — MCP Gateway GA (replaces Hermes's hand-rolled MCP code)
- **1.91.0** — OAuth 2.0 v2 resolver + DCR
- **1.95.0** — Rust `/v1/messages` endpoint
- **1.97.0** — Tool-result guardrails + SAML 2.0 SSO

#### Scenario: A new agent connects via the v1.97 MCP Gateway

- **GIVEN** the platform is on LiteLLM v1.97
- **WHEN** the operator runs `curl -s http://localhost:4000/v1/mcp/servers` to list the configured MCP servers
- **THEN** the response MUST be 200 OK with the MCP registry payload
- **AND** the v1.97 `tool-result guardrails` are applied per the agent's ACL

#### Scenario: The Rust /v1/messages endpoint is reachable

- **GIVEN** `pangolin.yaml` has the `/v1/messages` path exposed
- **WHEN** `curl -s -X POST http://litellm.cianfhoghlaim.ie/v1/messages -d '{"messages": [...]}' -H 'content-type: application/json'`
- **THEN** the request routes through the Pangolin reverse proxy → LiteLLM Rust `/v1/messages` endpoint
- **AND** the response latency is < 200ms for a single-message payload

#### Scenario: The 12-agent fleet still connects

- **WHEN** any `@observe`-decorated BAML function in `agents/meaisinfhoghlaim/agents/*.py` calls a model
- **THEN** the request goes through the v1.97 gateway successfully
- **AND** the trace lands in Langfuse v4 (the v3→v4 migration we just shipped)

### Requirement: LiteLLM v1.97 /v1/messages path exposed via Pangolin

The system SHALL expose LiteLLM's Rust `/v1/messages` endpoint (v1.95+) via the Pangolin reverse proxy. The path MUST be added to `bonnegar/stacks/litellm/pangolin.yaml` under the LITELLM private resource.

#### Scenario: The v1/messages path is reachable

- **GIVEN** the platform is on LiteLLM v1.97 + Pangolin v3
- **WHEN** the operator runs `curl -X POST https://litellm.cianfhoghlaim.ie/v1/messages`
- **THEN** the response MUST be 200 OK or 4xx (NOT 404)
- **AND** the response MUST come from the Rust endpoint (latency < 200ms for a small payload)

### Requirement: litellm config.yaml regenerated from MODEL_REGISTRY

The system SHALL regenerate `bonnegar/stacks/litellm/config/config.yaml` from the centralized `MODEL_REGISTRY` (per the 2026-08-15 centralized-model-registry openspec change) via `mise run ml:litellm:regenerate`. The regeneration MUST be idempotent + auto-runnable in CI.

#### Scenario: The config.yaml matches the current MODEL_REGISTRY

- **GIVEN** the operator has updated `MODEL_REGISTRY` with a new model entry
- **WHEN** they run `mise run ml:litellm:regenerate`
- **THEN** `config.yaml` is regenerated with the new model entry
- **AND** a re-run of the same task produces no further changes (idempotent)
