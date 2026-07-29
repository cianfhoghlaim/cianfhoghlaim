## ADDED Requirements

### Requirement: `MemoryBackend` Protocol is smoke-tested + the 8 NCCA agents have no direct graphiti/falkordb imports

The system SHALL smoke-test the `MemoryBackend` Protocol +
`get_default_backend()` factory
(at `storage/memf.py`) in a CI-runnable pytest
module that verifies the cascade behaviour
(Graphiti → FalkorDB → InMemoryLanceDB) without requiring
Graphiti or FalkorDB to be reachable in the test environment.

The 8 NCCA subject ADK specialists
(`agents/tuatha/{gael,math,hist,geog,chem,comp,engl,appm}_agent.py`)
SHALL NOT import `graphiti_client`, `falkordb_client`, or
`memgraph_client` directly; they MUST consume the canonical
`MemoryBackend` Protocol via the
`agents/tuatha/wiring.py` module's
`get_default_backend()` binding (or `wire_subject_agent(...)`
which delegates to it).

#### Scenario: `test_memory_backend_smoke.py` exercises the 3-scenario factory contract

- **GIVEN** `tests/test_memory_backend_smoke.py`
- **WHEN** `uv run pytest tests/test_memory_backend_smoke.py`
  runs in a CI environment without Graphiti / FalkorDB reachable
- **THEN** 3 tests SHALL pass:
  - `test_get_default_backend_returns_implementation` —
    `isinstance(backend, MemoryBackend)` AND
    `backend.kind in {"graphiti", "falkordb", "in_memory_lancedb"}`
  - `test_add_episode_round_trips` — adding an `Episode`
    followed by `await backend.search(query, k=1)` returns at
    least 1 hit whose snippet contains the episode body
  - `test_reset_default_backend_returns_fresh_instance` —
    `reset_default_backend()` clears the cached singleton and
    `get_default_backend()` returns a new instance

#### Scenario: 8 NCCA subject agents have zero direct memory-client imports

- **GIVEN** the 8 NCCA subject agent modules at
  `agents/tuatha/{gael,math,hist,geog,chem,comp,engl,appm}_agent.py`
- **WHEN** `grep -n "graphiti_client\|falkordb_client\|memgraph_client"
  agents/tuatha/<slug>_agent.py` runs for each of
  the 8 agents
- **THEN** the output SHALL be empty (0 matches per agent)
- **AND** each agent module SHALL import at least one symbol
  from `agents/tuatha/wiring.py` (the canonical
  wire-up module that depends on `get_default_backend()`)