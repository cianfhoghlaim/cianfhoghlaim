# Storage Memory Facade Capability

## Purpose

`storage-memory-facade` is a new capability of the Cianfhoghlaim
platform introduced by the
`2026-07-09-agent-fleet-and-observability-facade-v1` change (T4 of
the 5-tangent modernization). The corresponding source code lives
at `cianfhoghlaim/storage/memf.py`. The facade unifies the 5
post-v4 memory backends (Cognee, Graphiti, LanceDB, FalkorDB,
Memgraph) behind a single narrow `MemoryBackend` Protocol and a
`get_default_backend()` factory that cascades Graphiti →
FalkorDB → InMemoryLanceDB when each upstream backend is down.

The previous `agent-memory-systems` spec continues to govern the
Cognee / Graphiti / Letta cross-cutting layer; this spec covers
the new lightweight `MemoryBackend` Protocol that is the
canonical entry point for any new agent code.

## Background

The 5 memory backends (`agent-memory-systems` spec) are surfaced
to agent code via concrete classes
(`cianfhoghlaim.storage.graphiti_client.GraphitiClient`,
`cianfhoghlaim.storage.falkordb_client.FalkorDBClient`,
`cianfhoghlaim.storage.cognee_service.CogneeService`,
`cianfhoghlaim.storage.lancedb.LanceDBClient`,
`cianfhoghlaim.storage.memgraph_client.MemgraphClient`).
Each has a different API surface, different blocking semantics,
and different async-runtime quirks. Agent code that depends on
two or more backends ends up with a tangle of conditional paths.

The `MemoryBackend` Protocol + `get_default_backend()` factory
collapses all 3 most-common backends (Graphiti, FalkorDB,
InMemoryLanceDB) behind a single 4-method surface
(`add_episode`, `search`, `get_node`, `close`), making it
straightforward to write a cross-backend portable agent.

## Requirements

### Requirement: MemoryBackend Protocol

The system SHALL provide a `MemoryBackend` Protocol at
`cianfhoghlaim/storage/memf.py` with the following surface:

- `kind: ClassVar[str]` — backend identifier
- `async def add_episode(episode: Episode) -> str`
- `async def search(query: str, *, k: int = 10, **filters) -> list[SearchResult]`
- `async def get_node(node_id: str) -> Node | None`
- `async def close() -> None`

#### Scenario: GraphitiBackend satisfies the Protocol

- **GIVEN** `from cianfhoghlaim.storage.memf import GraphitiBackend,
  MemoryBackend`
- **WHEN** `isinstance(GraphitiBackend(), MemoryBackend)` is evaluated
- **THEN** it returns `True`

#### Scenario: InMemoryLanceDBBackend is the read-only fallback

- **GIVEN** an `InMemoryLanceDBBackend()` instance
- **WHEN** `await backend.add_episode(Episode(body="Tá mé ag imirt"))`
  runs
- **THEN** the returned `episode_id` is a `UUID4` string
- **AND** `await backend.search("fichille")` returns a list
  containing the matching episode

### Requirement: get_default_backend() cascade (Graphiti → FalkorDB → InMemory)

The system SHALL provide
`async def get_default_backend() -> MemoryBackend`. The factory
SHALL be the canonical entry point for any agent that needs a
memory backend.

The cascade SHALL be:

1. **GraphitiBackend** — when `GRAPHITI_HOST` is reachable.
2. **FalkorDBBackend** — when Graphiti is unreachable / 5xx.
3. **InMemoryLanceDBBackend** — last-resort read-only fallback.

The cascade SHALL be cached for 30 seconds.

#### Scenario: get_default_backend returns Graphiti when up

- **GIVEN** the Graphiti backend is reachable
- **WHEN** `await get_default_backend()` runs
- **THEN** the result is a `GraphitiBackend`

#### Scenario: get_default_backend returns FalkorDB on Graphiti 5xx

- **GIVEN** Graphiti's TCP probe fails
- **AND** FalkorDB is reachable
- **WHEN** `await get_default_backend()` runs
- **THEN** the result is a `FalkorDBBackend`

#### Scenario: get_default_backend returns InMemoryLanceDB when both are down

- **GIVEN** neither Graphiti nor FalkorDB is reachable
- **WHEN** `await get_default_backend()` runs
- **THEN** the result is an `InMemoryLanceDBBackend`

### Requirement: Backend health probe is cached

The system SHALL cache backend health for 30s.

#### Scenario: probe_backends caches the result for 30s

- **GIVEN** the Graphiti TCP probe returns False
- **WHEN** `probe_backends()` is called twice within 30s
- **THEN** the second call returns the cached False

### Requirement: Episode / Node / SearchResult dataclasses

The system SHALL provide 3 dataclasses:

- `Episode(body, source, source_id, timestamp, metadata, episode_id)`
- `Node(node_id, labels, properties)`
- `SearchResult(node_id, score, snippet, labels, metadata)`

#### Scenario: Episode has auto-generated episode_id

- **GIVEN** `Episode(body="...")` with no `episode_id`
- **WHEN** the dataclass is constructed
- **THEN** `episode_id` is a fresh `uuid.UUID4()`

### Requirement: All backends close gracefully

Every `MemoryBackend` implementation SHALL provide `close()`.

#### Scenario: GraphitiBackend.close releases the driver

- **GIVEN** a `GraphitiBackend` instance
- **WHEN** `await backend.close()` runs
- **THEN** the underlying Graphiti client's `close()` is called

### Requirement: Module-level singleton caches the resolved backend

The system SHALL cache the resolved backend in `_DEFAULT_BACKEND`.

#### Scenario: reset_default_backend() drops the cache

- **GIVEN** `_DEFAULT_BACKEND` is non-None
- **WHEN** `reset_default_backend()` runs
- **THEN** the next `get_default_backend()` returns a fresh instance

## Cross-references

- [`cianfhoghlaim/storage/memf.py`](../../cianfhoghlaim/storage/memf.py) (the facade)
- [`cianfhoghlaim/storage/graphiti_client.py`](../../cianfhoghlaim/storage/graphiti_client.py) (primary backend)
- [`cianfhoghlaim/storage/falkordb_client.py`](../../cianfhoghlaim/storage/falkordb_client.py) (cascade fallback)
- [`openspec/specs/agent-memory-systems/spec.md`](../agent-memory-systems/spec.md) (the parent capability — Cognee + Graphiti + Letta cross-cutting)
- [`.agents/skills/agent-memory-systems/SKILL.md`](../../.agents/skills/agent-memory-systems/SKILL.md)
