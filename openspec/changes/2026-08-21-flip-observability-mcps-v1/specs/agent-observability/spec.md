# Delta: agent-observability

## MODIFIED Requirements

### Requirement: 6-layer observability contract (5 programmatic + 1 MCP)

The system SHALL provide the canonical 6-layer observability contract
for the agent fleet:

| Layer | Surface | Transport |
|--:|:--|:--|
| 1 | Langfuse — LLM cost + prompt management | `@observe` decorator (Python) |
| 2 | Logfire — Python tracing | `logfire_span` (Python) |
| 3 | MLflow — Experiment tracking + model registry | `log_run` (Python) |
| 4 | RAGAS — RAG evaluation | `score` (Python, as Dagster `asset_check`) |
| 5 | structlog — Structured logging | `logging.Logger(f"agent.{agent_name}")` |
| 6 | **Langfuse MCP** — Runtime trace + prompt retrieval | MCP server (NEW post-this-change) |

The 6th layer (Langfuse MCP) is added by this change. It exposes
3 tools (`langfuse_get_trace`, `langfuse_get_traces`,
`langfuse_get_prompt`) that enable runtime trace inspection from
MCP clients (e.g. OpenCode, Claude Code).

#### Scenario: An agent runtime retrieves a trace via the Langfuse MCP

- **GIVEN** the `bonneagar/stacks/langfuse/` stack is running on port 3000
- **AND** the `langfuse` entry in `opencode.json` has `enabled: true`
- **WHEN** the agent runtime calls `langfuse_get_trace(trace_id)` with
  a recent trace id from a Langfuse `@observe`-decorated call
- **THEN** the server returns the full trace JSON
- **AND** `bun run mcp:smoke:langfuse` confirms the round-trip

### Requirement: Runtime secret mutation via Infisical MCP

The system SHALL expose the Infisical MCP server as a runtime secret
mutation surface (in addition to the existing `cd`-time hydration via
mise hooks). This enables:
- Adding new secrets without restarting the agent runtime
- Rotating secrets without manual `mise` invocations
- Auditing secret access via the Langfuse trace

The Infisical MCP exposes 3 tools:
`infisical_get_secret(name)`, `infisical_list_secrets()`,
`infisical_create_secret(name, value)`.

#### Scenario: An agent runtime creates a test secret via the Infisical MCP

- **GIVEN** the Infisical stack is running on `:8081`
- **AND** the credentials in `.infisical.env` are populated
  (`INFISICAL_CLIENT_ID`, `INFISICAL_SECRET`, `INFISICAL_PROJECT_ID`)
- **AND** the `infisical` entry in `opencode.json` has `enabled: true`
- **WHEN** the agent runtime calls
  `infisical_create_secret(name="mcp-smoke-test-secret", value="...")`
- **THEN** the server returns success
- **AND** `bun run mcp:smoke:infisical` confirms the round-trip
  (create + read + delete)