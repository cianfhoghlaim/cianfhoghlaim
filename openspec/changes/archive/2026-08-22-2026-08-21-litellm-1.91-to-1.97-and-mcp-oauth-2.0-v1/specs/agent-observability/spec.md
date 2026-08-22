## MODIFIED Requirements

### Requirement: LiteLLM v1.91 → v1.97 router updates

The system SHALL upgrade LiteLLM from `v1.91.0` to `v1.97.0` and adopt:

- **MCP Gateway GA** (v1.85.0) — single endpoint with per-key ACL.
- **OAuth 2.0 v2 resolver** (v1.91.0) — replaces Hermes's custom auth code.
- **MCP DCR (Dynamic Client Registration)** (v1.95.0) — new agents self-register without manual secret minting.
- **Rust `/v1/messages` endpoint** (v1.95.0) — high-throughput message bus, exposed via Pangolin reverse proxy under the LITELLM private resource.

#### Scenario: A new agent connects via MCP-OAuth 2.0 v2 + DCR

- **GIVEN** the platform is on LiteLLM v1.97 with MCP Gateway GA + OAuth 2.0 v2 + DCR enabled
- **WHEN** a 12-agent fleet agent connects to `http://litellm.cianfhoghlaim.ie/v1/mcp` for the first time
- **THEN** the DCR flow auto-registers the agent client (no manual operator step)
- **AND** the OAuth 2.0 v2 token flows back to the agent
- **AND** subsequent requests succeed with the v2 token

#### Scenario: The Pangolin reverse-proxy exposes /v1/messages

- **WHEN** `curl -s http://litellm.cianfhoghlaim.ie/v1/messages -X POST -d '{"messages": [...]}' -H 'content-type: application/json'` is called
- **THEN** the request routes through the Pangolin reverse proxy → LiteLLM Rust `/v1/messages` endpoint → response < 200ms
