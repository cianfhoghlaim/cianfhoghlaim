## MODIFIED Requirements

### Requirement: Multi-backend agent memory

The system SHALL provide persistent agent memory across sessions using
one of the supported backends.

#### Scenario: Cognee memory

- **GIVEN** an agent with Cognee memory enabled
- **WHEN** a user has multiple conversations
- **THEN** the agent recalls previous interactions via `cognee.search()`
  and `cognee.cognify()`

#### Scenario: Graphiti temporal memory

- **GIVEN** an agent with Graphiti memory enabled
- **WHEN** a knowledge graph is built with bi-temporal tracking
- **THEN** the agent can query the graph as of any point in time

#### Scenario: LanceDB semantic memory

- **GIVEN** an agent with LanceDB memory enabled
- **WHEN** a query is embedded with the BGE-M3 or BGE-large-en model
- **THEN** the agent retrieves the top-10 closest chunks from the
  relevant corpus

## ADDED Requirements

### Requirement: NCCA subject agents MUST depend on the MemoryBackend StorageBackend Protocol

The 8 NCCA subject agents MUST depend on the `MemoryBackend`
Protocol via
`from cianfhoghlaim.storage.memf import get_default_backend`
rather than importing `graphiti_client`, `falkordb_client`, or
`memgraph_client` directly.

The wire-up SHALL be exposed as the module-level
`<slug>_agent_wire` attribute holding a `WireSubjectAgent`
instance (from `cianfhoghlaim/agents/tuatha/wiring.py`).

#### Scenario: gaol_agent does not bypass the Protocol

- **GIVEN** `gael_agent.py` at `cianfhoghlaim/agents/tuatha/`
- **WHEN** `grep -n "graphiti_client\|falkordb_client\|memgraph_client" gael_agent.py` runs
- **THEN** the output SHALL be empty (0 matches)
- **AND** the module exposes `gael_agent_wire` after import

#### Scenario: 8 agents each expose a wire with a known backend kind

- **GIVEN** any of the 8 `<slug>_agent.py` modules
- **WHEN** `<slug>_agent_<slug>_agent_wire` is read
- **THEN** `wire.memory_backend_kind` is either `"protocol"`
  (the canonical case where `get_default_backend` resolves the
  `MemoryBackend` Protocol) or `None` (when the StorageBackend
  Protocol could not be imported — a graceful failure mode)
