# Delta: agent-platform-cluster

## MODIFIED Requirements

### Requirement: MCP server inventory

The 8-stack agent platform cluster SHALL expose the following MCP
servers in addition to the 3 agent-facing surfaces (openclaw +
openchamber + hermes):

| MCP server | Backend | Default | Purpose |
|:--|:--|:--|:--|
| `crawl4ai` | v0.9.x native MCP on port 11235 | ✅ ON | Open-source bulk scraping (replaces browserbase) |
| `firecrawl` | Firecrawl MCP service | ✅ ON | Paid anti-bot + agent research |
| `chrome-devtools-mcp` | Local Chrome | ✅ ON | Local Chrome debugging |
| `dlt-workspace-mcp` | dlt workspace | ✅ ON | DLT pipeline workspace |
| `motherduck` | MotherDuck MCP (in-memory mode) | ✅ ON | SQL analytics |
| `cognee` | Cognee on :8100 | ✅ ON | Knowledge graph memory |
| `graphiti` | Graphiti on :8000 + Neo4j on :7687 | ✅ ON | Temporal knowledge graph memory |
| `design-system-server` | In-house FastMCP at `web/apps/.../packages/mcp/` | ✅ ON | AG-UI self-heal |
| `langfuse` | Langfuse on :3000 | ✅ ON | LLM trace observability |
| `infisical` | Infisical MCP | ✅ ON | Runtime secret mutation |
| `cocoindex-code` (ccc) | ccc mcp | ✅ ON | Semantic code search |
| `huggingface` | Remote `https://huggingface.co/mcp?login` | ✅ ON | Model + dataset hub |

The `browserbase` MCP server SHALL be removed from this inventory
(per the `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`
change). The `Bonneagar/stacks/browser/` stack SHALL remain as an
optional fallback stack with browserbase integrations explicitly
marked as opt-in.

#### Scenario: The MCP inventory is consistent across docs

- **GIVEN** this change has been archived
- **WHEN** the developer runs `git grep -nE '"browserbase"' openspec/specs/ openspec/changes/active/ opencode.json .mcp.json`
- **THEN** zero active references to `browserbase` MCP are returned
- **AND** the 12 active MCPs above are listed consistently in
  `agent-platform-cluster/spec.md`, the central
  `centralized-registry` skill, and the `.agents/skills/INDEXING_AND_COGNITION.md`
  guide