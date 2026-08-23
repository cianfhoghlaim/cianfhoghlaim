## ADDED Requirements

### Requirement: litellm-v1-97-tasks

The `data:litellm:*` task namespace SHALL expose LiteLLM v1.97+
features via 2 new tasks. Per the
`2026-08-23-integration-litellm-1-97-features-v1` change.

#### Scenario: data:litellm:mcp:gateway boots the gateway daemon

- **WHEN** `mise run data:litellm:mcp:gateway` runs
- **THEN** it MUST boot the MCP Gateway daemon
- **AND** it MUST print the routes for all configured MCP servers
- **AND** the daemon MUST remain alive for the duration of the task

#### Scenario: data:litellm:oauth:v2 enables OAuth 2.0 v2

- **WHEN** `mise run data:litellm:oauth:v2` runs
- **THEN** it MUST enable OAuth 2.0 v2 (DCR)
- **AND** it MUST print the dynamic client registration endpoint