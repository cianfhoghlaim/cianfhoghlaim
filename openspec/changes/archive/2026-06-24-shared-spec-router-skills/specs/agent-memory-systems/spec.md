## ADDED Requirements

### Requirement: Agent memory router skill

The agent memory capability MUST be discoverable via a single router skill at `.agents/skills/agent-memory-systems/SKILL.md`. The router SHALL list the 5 backends (Cognee, Graphiti, LanceDB, FalkorDB, Memgraph) with a decision tree and a "pair this skill with" cross-reference table.

#### Scenario: Agent finds the memory router

- **WHEN** an agent searches for "agent memory", "cognee", "graphiti", "long-term memory", or "knowledge graph for agents"
- **THEN** the loader matches `.agents/skills/agent-memory-systems/SKILL.md`
- **AND** the skill points at the underlying memory skills (cognee, graphiti, lancedb, falkordb, memgraph) without duplicating their content
