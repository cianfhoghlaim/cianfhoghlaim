# Spec Delta — agent-memory-systems

This delta adds 2 new requirements to the existing
`agent-memory-systems` capability. Existing requirements are
preserved unchanged.

## ADDED Requirements

### Requirement: 5-backend `MemoryLayer` Protocol via `agents/memory_layer.py`

The system SHALL provide a `MemoryLayer` Protocol in
`agents/memory_layer.py` that exposes 5 concrete backends:

- **Cognee** — structured knowledge (entities + relationships)
- **Graphiti** — temporal knowledge graph (bi-temporal)
- **LanceDB** — vector RAG (HNSW)
- **FalkorDB** — vector + graph hybrid (Redis-compatible)
- **Memgraph** — production graph (Cypher + MAGE)

The `get_default_memory_layer()` cached factory SHALL resolve
to one of the 5 backends in the canonical order:
Cognee → Graphiti → LanceDB → FalkorDB → Memgraph.

Each `MemoryLayer` instance SHALL expose a `kind` attribute
(one of `{"cognee", "graphiti", "lancedb", "falkordb", "memgraph"}`)
and an `is_available()` method that returns `True` if the
backend is reachable in the current environment.

#### Scenario: `get_default_memory_layer` returns an implementation

- **GIVEN** `agents/memory_layer.py`
- **WHEN** `layer = get_default_memory_layer()`
- **THEN** `isinstance(layer, MemoryLayer)` SHALL be `True`
- **AND** `layer.kind` SHALL be one of
  `{"cognee", "graphiti", "lancedb", "falkordb", "memgraph"}`
- **AND** the returned layer SHALL be cached (subsequent calls
  return the same instance)

#### Scenario: 5 backends are available in the registry

- **GIVEN** `agents/memory_layer.py`
- **WHEN** `python -c "from cianfhoghlaim.agents.memory_layer import MEMORY_LAYERS; print(len(MEMORY_LAYERS))"`
- **THEN** the output SHALL be 5
- **AND** the keys SHALL be `{"cognee", "graphiti", "lancedb", "falkordb", "memgraph"}`

### Requirement: Graceful degradation when memory backend unavailable

The system SHALL NOT propagate `ConnectionError` or
`RuntimeError` when any of the 5 memory backends are
unreachable in the current environment. The cached
`get_default_memory_layer()` factory SHALL fall through to
the next available backend in the cascade order.

Each agent SHALL attach a `memory_layer_kind` field that
reports which backend was successfully resolved.

#### Scenario: factory falls through to the next available backend

- **GIVEN** Cognee is unreachable (e.g. port 8000 not listening)
- **WHEN** `layer = get_default_memory_layer()`
- **THEN** the factory SHALL fall through to Graphiti
- **AND** if Graphiti is also unreachable, the factory SHALL
  fall through to LanceDB
- **AND** the cascade SHALL continue until a backend is found
- **AND** the returned `layer.kind` SHALL be the first
  available backend in the cascade order

#### Scenario: 12 agents have a `memory_layer_kind` field populated

- **GIVEN** the 12 agents are wired via `agents/wiring.py`
- **WHEN** `python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; [print(k, v.memory_layer_kind) for k, v in AGENT_REGISTRY.items()]"`
- **THEN** the command exits 0
- **AND** each agent SHALL have a `memory_layer_kind` field
  set to one of the 5 backend kinds
- **AND** no `ConnectionError` or `RuntimeError` SHALL be raised