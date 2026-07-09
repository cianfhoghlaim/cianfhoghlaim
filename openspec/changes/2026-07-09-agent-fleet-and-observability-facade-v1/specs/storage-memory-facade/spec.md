# Spec Delta: storage-memory-facade (NEW)

This change creates a new capability `storage-memory-facade` at
`openspec/specs/storage-memory-facade/spec.md`. The capability
defines the `MemoryBackend` Protocol + `get_default_backend()`
factory contract. The full new spec lives at
`openspec/specs/storage-memory-facade/spec.md`.

## ADDED Requirements

### Requirement: MemoryBackend Protocol

The system SHALL provide a `MemoryBackend` Protocol at
`cianfhoghlaim/storage/memf.py` with the following surface:

- `kind: ClassVar[str]` — backend identifier (e.g.
  `"graphiti"`, `"falkordb"`, `"in_memory_lancedb"`)
- `async def add_episode(episode: Episode) -> str`
- `async def search(query: str, *, k: int = 10, **filters) -> list[SearchResult]`
- `async def get_node(node_id: str) -> Node | None`
- `async def close() -> None`

The Protocol SHALL be `@runtime_checkable` so `isinstance(b,
MemoryBackend)` works. The 3 dataclasses — `Episode`, `Node`,
`SearchResult` — SHALL be defined alongside the Protocol.

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
- **AND** `await backend.search("fichille")` returns a
  `list[SearchResult]` containing the matching episode

### Requirement: get_default_backend() cascade (Graphiti → FalkorDB → InMemory)

The system SHALL provide
`async def get_default_backend() -> MemoryBackend` at
`cianfhoghlaim/storage/memf.py`. The factory SHALL be the
canonical entry point for any agent that needs a memory backend;
direct imports of `GraphitiClient`, `FalkorDBClient`, or
`InMemoryLanceDBBackend` SHALL be reserved for backends that
need backend-specific features.

The cascade SHALL be (in order):

1. **GraphitiBackend** — when `GRAPHITI_HOST` is reachable on
   `GRAPHITI_PORT` (default `8080`).
2. **FalkorDBBackend** — when Graphiti is unreachable / 5xx / not
   configured.
3. **InMemoryLanceDBBackend** — last-resort read-only fallback
   when both Graphiti and FalkorDB are unreachable.

The cascade SHALL be cached for 30 seconds (`_HEALTH_TTL_SECONDS`)
to avoid re-probing on every call.

#### Scenario: get_default_backend returns Graphiti when up

- **GIVEN** the Graphiti backend is reachable
- **WHEN** `await get_default_backend()` runs
- **THEN** the result is a `GraphitiBackend`
- **AND** `backend.kind == "graphiti"`
- **AND** subsequent calls within 30s return the same instance

#### Scenario: get_default_backend returns FalkorDB on Graphiti 5xx

- **GIVEN** Graphiti's TCP probe fails (e.g. host unreachable)
- **AND** FalkorDB is reachable on `FALKORDB_HOST:FALKORDB_PORT`
- **WHEN** `await get_default_backend()` runs
- **THEN** the result is a `FalkorDBBackend`
- **AND** a warning is logged: `"Graphiti 5xx, falling back to
  FalkorDBBackend"`

#### Scenario: get_default_backend returns InMemoryLanceDB when both are down

- **GIVEN** neither Graphiti nor FalkorDB is reachable
- **WHEN** `await get_default_backend()` runs
- **THEN** the result is an `InMemoryLanceDBBackend`
- **AND** a warning is logged

### Requirement: Backend health probe is cached

The system SHALL cache backend health for 30 seconds per the
`_HEALTH_TTL_SECONDS` constant. The `_probe()` helper SHALL be a
TCP connect (not full HTTP) so CI without secrets doesn't fire
up network traffic.

#### Scenario: probe_backends caches the result for 30s

- **GIVEN** the Graphiti TCP probe returns False
- **WHEN** `probe_backends()` is called twice within 30s
- **THEN** the second call returns the cached False without
  re-running the TCP probe

### Requirement: Episode / Node / SearchResult dataclasses

The system SHALL provide 3 dataclasses alongside the Protocol:

- `Episode(body: str, source: str = "user", source_id: str | None
  = None, timestamp: datetime = ..., metadata: dict = ...,
  episode_id: UUID = ...)`
- `Node(node_id: str, labels: list[str] = ..., properties:
  dict = ...)`
- `SearchResult(node_id: str, score: float, snippet: str = "",
  labels: list[str] = ..., metadata: dict = ...)`

#### Scenario: Episode has auto-generated episode_id

- **GIVEN** `Episode(body="...")` with no `episode_id`
- **WHEN** the dataclass is constructed
- **THEN** `episode_id` is a fresh `uuid.UUID4()`

### Requirement: All backends close gracefully

Every `MemoryBackend` implementation SHALL provide a `close()`
async method that releases the underlying client handle. Callers
that obtain a backend via `get_default_backend()` SHALL
`await backend.close()` when they are done.

#### Scenario: GraphitiBackend.close releases the driver

- **GIVEN** a `GraphitiBackend` instance
- **WHEN** `await backend.close()` runs
- **THEN** the underlying Graphiti client's `close()` (if
  available) is called
- **AND** no exception escapes (best-effort shutdown)

### Requirement: Module-level singleton caches the resolved backend

The system SHALL cache the resolved backend in the module-level
`_DEFAULT_BACKEND` variable so repeated calls within the same
process share a single instance. The `reset_default_backend()`
test-only helper SHALL drop the cached singleton.

#### Scenario: reset_default_backend() drops the cache

- **GIVEN** `_DEFAULT_BACKEND` is non-None
- **WHEN** `reset_default_backend()` runs
- **THEN** the next `get_default_backend()` call returns a
  fresh instance (and re-probes the cascade)
