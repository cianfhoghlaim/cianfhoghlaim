# Spec Delta: agent-observability

## ADDED Requirements

### Requirement: KCG MCP inventory (5 canonical servers)

The `agent-observability` skill SHALL inventory the 5
canonical KCG Model Context Protocol (MCP) servers
configured in `opencode.json` for agent integration:

| Server | Port | Purpose | Backed by |
|:--|:--|:--|:--|
| `cognee` | 8000 | Knowledge graph (cognify) | `cognee-oss` |
| `ccc` | (local CLI) | Semantic code search | `cocoindex` |
| `graphiti` | 8080 | Bi-temporal knowledge graph | `graphiti-core` |
| `langfuse` | 3000 | LLM observability + traces | `langfuse` |
| `motherduck` | (cloud) | Managed DuckDB query | `motherduck` |
| `firecrawl` | (cloud) | Web scraping | `firecrawl` |
| `browserbase` | (cloud) | Browser automation | `browserbase` |
| `chrome-devtools` | (local) | Chrome DevTools MCP | `chrome-devtools-mcp` |
| `infisical` | (cloud) | Secret management | `infisical` |

The MCP inventory lives at
`.agents/skills/agent-observability/references/mcp-servers.md`
(deep-dive reference) and is summarised in the
`agent-observability/SKILL.md` body under `§KCG MCP
inventory`.

#### Scenario: A new MCP server is added to opencode.json

- **GIVEN** a developer adds a new MCP server (e.g.
  `playwright`) to `opencode.json`
- **WHEN** they look at the KCG MCP inventory in
  `agent-observability/SKILL.md` §KCG MCP inventory
- **THEN** they see the 9 existing canonical servers and
  can decide:
  - Whether the new server fits an existing slot (e.g.
    it replaces one of the 9)
  - Or whether it's a new category
- **AND** the inventory is updated in the skill body +
  the reference file

#### Scenario: An MCP server fails to start

- **GIVEN** the dagster Cognee integration runs a
  `cognee_search` step
- **WHEN** the cognee MCP server is unreachable
- **THEN** the step fails with a clear error pointing
  to the inventory entry for `cognee` MCP server
- **AND** the langfuse trace records the failure
- **AND** the agent can fall back to direct Cognee CLI
  invocation
