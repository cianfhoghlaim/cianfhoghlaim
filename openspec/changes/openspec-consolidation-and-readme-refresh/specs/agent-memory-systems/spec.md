## ADDED Requirements

The `agent-memory-systems` capability is renamed from `memory-systems`
and shrunk to a thin capability pointer at the relevant skills. The
full Requirements + Scenarios are in the canonical spec at
`openspec/specs/agent-memory-systems/spec.md`.

### Requirement: Multi-backend agent memory

The system SHALL provide persistent agent memory across sessions using
one of the supported backends (Cognee, Graphiti, LanceDB, FalkorDB,
Memgraph).

#### Scenario: Cognee memory

- **WHEN** an agent with Cognee memory is invoked across multiple
  conversations
- **THEN** the agent recalls previous interactions via
  `cognee.search()` and `cognee.cognify()`

#### Scenario: Graphiti temporal memory

- **WHEN** an agent with Graphiti memory queries a bi-temporal
  knowledge graph
- **THEN** the agent can query the graph as of any point in time

#### Scenario: LanceDB semantic memory

- **WHEN** an agent with LanceDB memory is invoked
- **THEN** the agent retrieves the top-10 closest chunks from the
  relevant corpus
