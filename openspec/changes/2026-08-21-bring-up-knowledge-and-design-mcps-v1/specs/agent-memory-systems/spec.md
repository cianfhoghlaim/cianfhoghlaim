# Delta: agent-memory-systems

## MODIFIED Requirements

### Requirement: 5 MCP-wired memory backends

The system SHALL expose the canonical 5 memory backends as MCP servers
in addition to the existing programmatic Python interfaces:

| Backend | MCP server name | Default port | Status |
|:--|:--|--:|:--|
| **Cognee** (structured KG) | `cognee` | 8100 | ✅ wired (post-this-change) |
| **Graphiti** (temporal KG) | `graphiti` | 8000 (Neo4j on 7687) | ✅ wired (post-this-change) |
| **LanceDB** (vector RAG) | `lancedb` | 8002 | ⏸ deferred to follow-up |
| **FalkorDB** (vector + graph hybrid) | `falkordb` | 8003 | ⏸ deferred to follow-up |
| **Memgraph** (production graph) | `memgraph` | 7687 | ⏸ deferred to follow-up |

The MCP wiring for Cognee + Graphiti is added by this change; the
remaining 3 (LanceDB + FalkorDB + Memgraph) are deferred to follow-up
changes per the priority queue in
`2026-08-21-mcp-server-revival-overview.md`.

#### Scenario: Cognee MCP is reachable from the agent fleet

- **GIVEN** the `bonneagar/stacks/cognee/` stack is running on port 8100
- **AND** the `cognee` entry in `opencode.json` has `enabled: true`
- **WHEN** the agent runtime connects and calls `cognee_search(query)`
- **THEN** the server returns a GraphRAG result with `search_type` =
  `GRAPH_COMPLETION`, `CHUNKS`, `INSIGHTS`, or `SUMMARIES`
- **AND** `bun run mcp:smoke:cognee` confirms the round-trip

#### Scenario: Graphiti MCP round-trips an episode + search

- **GIVEN** the `bonneagar/stacks/graphiti/` stack is running on port 8000
- **AND** Neo4j is reachable at `bolt://localhost:7687`
- **AND** the `graphiti` entry in `opencode.json` has `enabled: true`
- **WHEN** the agent runtime calls `graphiti_add_episode` followed by
  `graphiti_search_`
- **THEN** the server returns the episode + the search result
- **AND** `bun run mcp:smoke:graphiti` confirms the round-trip

#### Scenario: The memory cascade prefers Cognee + Graphiti

- **GIVEN** all 5 memory backends are reachable
- **WHEN** the agent needs to recall a fact
- **THEN** the cascade order per `agent-memory-systems/spec.md`
  applies: Cognee (1st) → Graphiti (2nd) → LanceDB (3rd) →
  FalkorDB (4th) → Memgraph (5th)
- **AND** the agent runtime logs which backend served the recall
  request in the Langfuse trace