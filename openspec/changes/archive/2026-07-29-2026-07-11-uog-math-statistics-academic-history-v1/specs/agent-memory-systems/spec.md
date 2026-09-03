# agent-memory-systems — academic-history delta

## ADDED Requirements

### Requirement: academic_history_agent MUST depend on the MemoryBackend Protocol

The system SHALL provide an `academic_history_agent` at
`agents/meaisinfhoghlaim/educational/academic_history_agent.py`
that MUST depend on the `MemoryBackend` StorageBackend Protocol via
`from cianfhoghlaim.storage.memf import get_default_backend` rather
than importing `graphiti_client`, `falkordb_client`, or
`memgraph_client` directly.

The wire-up SHALL be exposed as the module-level
`academic_history_agent_wire` attribute holding a
`WireSubjectAgent` instance — following the same pattern as the
8 NCCA subject agents and the 5 UoG coursework agents documented
elsewhere in this spec.

#### Scenario: academic_history_agent does not bypass the Protocol

- **GIVEN** `academic_history_agent.py`
- **WHEN** `grep -n "graphiti_client\|falkordb_client\|memgraph_client" academic_history_agent.py` runs
- **THEN** the output SHALL be empty (0 matches)
- **AND** the module SHALL expose `academic_history_agent_wire`
  after import

### Requirement: 13th routing keyword bucket

The system SHALL add a 13th `ROUTING_KEYWORDS` bucket
`academic_history_agent` to
`agents/routing_keywords.py` covering:

- "my history", "my notes", "my modules", "my assignments"
- "my exam history", "my answers", "my progress"
- "summarise my degree", "what should I revise"
- "stair acadúil", "mo chuid cuntas", "mo nótaí"

#### Scenario: Query routes to academic_history_agent

- **GIVEN** the user asks "summarise my stats modules"
- **WHEN** the `QueryRouter.route_by_keywords` runs
- **THEN** the `academic_history_agent` bucket SHALL match (priority
  over the generic `statistics_agent` bucket)
- **AND** the agent SHALL retrieve the user's ST311/ST312 modules
  from memory + lakehouse