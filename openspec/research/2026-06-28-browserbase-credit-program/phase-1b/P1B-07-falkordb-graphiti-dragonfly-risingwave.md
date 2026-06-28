# P1B-07 — FalkorDB + Graphiti + Dragonfly + RisingWave (Phase 1B, Vector + Graph + Storage)

**Date:** 2026-06-28
**Phase:** 1B (Vector + Graph + Storage Tier)
**Budget:** ~180 credits
**Subagent:** research

## TL;DR

FalkorDB is the **vector + graph hybrid database** that powers the cross-archive knowledge graph queries (3 edge types: cites, builds-on, contradicts). Graphiti is the **bi-temporal knowledge graph library** that uses FalkorDB for persistence + Neo4j for the open-source fallback + Dragonfly for the episode cache. RisingWave streams CDC events into FalkorDB via Iceberg sink.

The canonical Cianfhoghlaim pattern uses Graphiti's `graphiti-core` library with FalkorDB as the backend (since it has the best vector+graph combination).

## Code

| Path | Purpose |
|:--|:--|
| `stacks/falkordb/compose.yaml` | FalkorDB service (port 6379 with graph protocol) |
| `stacks/graphiti/compose.yaml` | Graphiti Python server (port 8000) |
| `stacks/dragonfly/compose.yaml` | Episode cache for Graphiti (port 6379, separate) |
| `stacks/risingwave/compose.yaml` | CDC source → FalkorDB via Iceberg |
| `oideachais/agents/meaisinfhoghlaim/memory/` | Graphiti client + episode store |
| `cognify/rules/falkordb_edge_types.py` | Lists 3 cross-archive edge types |
| `cognify/rules/graphiti_episodes.py` | Lists 12 active episodes (per Leabharlann subdir) |

**Canonical FalkorDB compose**:

```yaml
falkordb:
  image: falkordb/falkordb:latest
  container_name: falkordb-graph
  restart: unless-stopped
  ports:
    - "6379:6379"
  command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]
  volumes:
    - falkordb-data:/data
```

**Canonical Graphiti init** (`oideachais/agents/meaisinfhoghlaim/memory/graphiti_client.py`):

```python
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver
from datetime import datetime, timezone

async def init_graphiti() -> Graphiti:
    """Initialize Graphiti with FalkorDB + Dragonfly episode cache."""
    falkor_driver = FalkorDriver(host="falkordb", port=6379)
    dragonfly_client = ...  # Redis client pointing at dragonfly:6379
    graphiti = Graphiti(
        graph_driver=falkor_driver,
        cache_client=dragonfly_client,
    )
    await graphiti.build_indices_and_constraints()
    return graphiti

async def add_episode(graphiti: Graphiti, episode_body: str, source: str):
    """Add an episode (e.g., a leabharlann document)."""
    await graphiti.add_episode(
        name=f"episode-{datetime.now(timezone.utc).isoformat()}",
        episode_body=episode_body,
        source_description=source,
        reference_time=datetime.now(timezone.utc),
    )
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `FALKORDB_HOST` | `falkordb` | compose env |
| `FALKORDB_PORT` | `6379` | compose env |
| `DRAGONFLY_URL` | `redis://dragonfly:6379/0` | compose env |
| `NEO4J_URI` (fallback) | `bolt://neo4j:7687` | Locket |
| `OPENAI_API_KEY` (for embeddings) | `infisical://dev-baile/openai/api_key` | Locket |

## CCC anchors

`stacks/falkordb/` · `stacks/graphiti/compose.yaml` · `stacks/dragonfly/` · `stacks/risingwave/` · `oideachais/agents/meaisinfhoghlaim/memory/graphiti_client.py`

Search terms: `"FalkorDriver"`, `"Graphiti("`, `"add_episode"`, `"vector.so"`.

## Drift log

| Date | Event |
|--:|:--|
| 2025-11 | Initial FalkorDB deploy |
| 2026-01 | Added Dragonfly cache layer |
| 2026-03 | Wired Graphiti episodes (12 leabharlann subdirs) |
| 2026-04 | Added RisingWave CDC source → FalkorDB via Iceberg |
| 2026-05 | Cross-archive edge types: cites, builds-on, contradicts |

## Anti-patterns

1. Don't use FalkorDB without the `vector.so` loadable — vector queries won't work
2. Don't bypass the episode cache — without Dragonfly, Graphiti queries are 10x slower
3. Don't use Graphiti with FalkorDB and Neo4j simultaneously — pick one per environment
4. Don't skip `build_indices_and_constraints` — without it, bi-temporal queries are O(N²)

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Vector + graph | FalkorDB | Best combined performance |
| Episode cache | Dragonfly | 5x faster than Redis |
| Embeddings | OpenAI text-embedding-3-small | Multilingual support |
| Edge types | 3 (cites, builds-on, contradicts) | Academic knowledge graph |
| Bi-temporal | Graphiti (built-in) | Time-aware queries |
| CDC source | RisingWave → Iceberg → FalkorDB | Real-time updates |

## Files to read next

`stacks/falkordb/` · `stacks/graphiti/compose.yaml` · `oideachais/agents/meaisinfhoghlaim/memory/graphiti_client.py` · `cognify/rules/falkordb_edge_types.py` · `.agents/skills/graphiti-core/SKILL.md` · `.agents/skills/agent-memory-systems/SKILL.md`
