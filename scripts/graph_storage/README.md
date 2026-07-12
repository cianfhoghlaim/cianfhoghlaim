# `storage/` — Graph Database + Cache + Cognee Integration

## Multi-graph architecture

The `storage/` package provides a layered graph database architecture
where each layer serves a different purpose. These are **complementary
layers**, not duplicates.

### Layers

| Layer | File | Purpose | Used by |
|:--|:--|:--|:--|
| **1. Multi-graph abstraction** | `storage/_shared/{falkordb,memgraph,neo4j,interface}.py` | Generic multi-database client interface | All other layers |
| **2. Data model** | `storage/temporal.py` | Bi-temporal dataclasses (Episode, TemporalEdge, EdgeStatus) | The client layer |
| **3. Graph clients** | `storage/falkordb_client.py` | FalkorDB cache wrapper (Redis-based hot path) | `storage/cache.py` |
| | `storage/memgraph_client.py` | Memgraph curriculum-graph wrapper (Bolt protocol) | `dagster/resources.py` |
| | `storage/temporal_client.py` | `graphiti_core`-backed bi-temporal client (FalkorDB) | The 12-agent fleet |
| | `storage/graphiti_client.py` | LightGraphRAG + Cognee for bunchloch documents | `storage/cognify/` |
| **4. Cognee + cache** | `storage/cache.py` | Unified hot-path cache | Dagster @assets |
| | `storage/cognify/` | Cognee cognify + cross-corpus rules | The 5 cognify asset files |
| | `storage/cognify/cognee_integration/` | The 7 cognify asset wrappers | `dagster/assets/leabharlann_cognify_assets.py` |
| | `storage/cognify/rules/` | The 4 cross-corpus edge rules | The 7 cognify asset wrappers |

### Why both `_shared/falkordb.py` AND `falkordb_client.py`?

The two are different layers:
- `storage/_shared/falkordb.py` — generic `GraphClient` interface used by
  the abstraction layer (Bolt-style graph operations: `create_node`,
  `create_edge`, `get_node`, `get_neighbors`, etc.)
- `storage/falkordb_client.py` — concrete FalkorDB cache wrapper with
  hot-path optimization (uses Redis caching; serial query execution;
  cache TTL). Used by `storage/cache.py` for the Dagster hot path.

### Why both `temporal.py` AND `temporal_client.py`?

The two are different layers:
- `storage/temporal.py` — pure-Python data model: `EdgeStatus` enum,
  `Episode` dataclass, `TemporalEdge` dataclass, `TemporalQuery` class,
  `CurriculumChange` dataclass. These are the bi-temporal types.
- `storage/temporal_client.py` — `graphiti_core`-backed implementation
  that uses the data model from `temporal.py`. This is the runtime
  client that connects to FalkorDB.

**`temporal.py` is NOT superseded by `temporal_client.py`.** The data
model is needed by the client (and by all consumers of the temporal
types).

## Migration status

The legacy `dlt_sources.*` namespace (used pre-v4) has been migrated
to `cianfhoghlaim.dlt.*` paths. See
`openspec/changes/consolidate-cianfhoghlaim-subdirs/proposal.md` for
the full mapping table.

The legacy `oideachais.dagster_defs.*` and `oideachais.dlt_sources.*`
imports have been migrated to `cianfhoghlaim.dagster.*` and
`cianfhoghlaim.dlt.*` respectively (per the 7-phase
`consolidate-cianfhoghlaim-pyproject-and-8-dirs` change).
