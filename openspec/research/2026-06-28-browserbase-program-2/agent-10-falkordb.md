# Agent 10 — FalkorDB (Vector + Graph Hybrid)

**Date:** 2026-06-28 22:07 UTC
**Agent:** 10 of 25 (BrowserBase Program 2, Wave 1)
**Budget used:** ~9 scrapes (well under 200 credits)
**Stack:** FalkorDB (graph + vector hybrid), Graphiti, Dragonfly, RisingWave

## TL;DR

FalkorDB is a **Redis-module graph database built on GraphBLAS sparse adjacency matrices** that adds native vector similarity search via the `vector.so` loadable. It exposes both **RESP (Redis)** and **Bolt (Neo4j-style)** wire protocols, supports **OpenCypher v9 with proprietary extensions**, and is the KCG-canonical vector+graph hybrid for the cross-archive knowledge graph. Graphiti's `graphiti-core>=0.5` library uses FalkorDB as its primary backend, with the new **FalkorDB Lite** embedded fallback for local dev (no Docker required). The major drift found: `infrastructure/stacks/falkordb/compose.yaml` does **NOT** currently load `vector.so` — vector queries will silently fail on the production stack until `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]` is added.

## Code

### §1. Canonical client usage (from `docs.falkordb.com`)

```python
from falkordb import FalkorDB

db = FalkorDB(host="localhost", port=6379)
g = db.select_graph("MotoGP")
g.delete()
g.query("""CREATE (:Rider {name:'Valentino Rossi'})-[:rides]->(:Team {name:'Yamaha'})""")
res = g.query("MATCH (r:Rider)-[:rides]->(t:Team) WHERE t.name='Yamaha' RETURN r.name")
for row in res.result_set:
    print(row[0])  # "Valentino Rossi"
```

### §2. Vector index — the `vector.so` API surface

```cypher
-- 1) Create index (dimension + similarity function mandatory; M / efConstruction / efRuntime optional)
CREATE VECTOR INDEX FOR (p:Product) ON (p.description)
OPTIONS {
  dimension: 768,
  similarityFunction: 'cosine',  -- or 'euclidean'
  M: 32,                          -- default 16; HNSW max outgoing edges per node
  efConstruction: 200,            -- default 200; HNSW build-time candidates
  efRuntime: 10                   -- default 10; HNSW query-time candidates
}

-- 2) Insert vectors using vecf32()
CREATE (p:Product {name:'Laptop', embedding: vecf32([0.1, 0.2, ...])})

-- 3) k-NN query (the only procedure-call form; no Cypher syntax sugar)
CALL db.idx.vector.queryNodes(
  'Product', 'embedding', 5, vecf32([...])
) YIELD node, score
RETURN node.name, score ORDER BY score DESC

-- 4) Drop the index
DROP VECTOR INDEX FOR (p:Product) ON (p.description)
```

### §3. Three index types — only ONE is vector

| Type | Where used | Algo |
|:--|:--|:--|
| Range index | node label / relationship type properties | B-tree |
| Full-text index | text search with stemming | RediSearch (TF-IDF) |
| **Vector index** | similarity on embeddings | **HNSW** (1–4096 dim) |

### §4. Eleven built-in algorithms (`CALL algo.<name>()`)

| Category | Algorithms |
|:--|:--|
| Pathfinding | BFS, SPpath (single source → single target), SSpath (single source → all), MSF (minimum spanning forest) |
| Centrality | PageRank, Betweenness Centrality, Harmonic Centrality |
| Community | WCC (weakly connected components), CDLP (label propagation) |
| Network flow | MaxFlow |

All algorithms use **matrix-based computation** over GraphBLAS sparse matrices.

### §5. KCG Graphiti client (`cianfhoghlaim/core/cognee/_graph/graphiti_client.py:51`)

```python
DEFAULT_FALKORDB_URI = os.getenv("FALKORDB_URI", "falkordb://falkordb:6379")
DEFAULT_FALKORDB_LITE_PATH = os.getenv("FALKORDB_LITE_PATH", "/tmp/falkordb_lite")

class GraphitiClient:
    """Thin async wrapper around graphiti_core.Graphiti.
    Auto-falls-back to FalkorDB Lite if the production FalkorDB
    compose stack is unreachable."""
    @classmethod
    async def connect(cls, uri=None, *, use_lite_fallback=True):
        try:
            graphiti = Graphiti(uri=uri or DEFAULT_FALKORDB_URI)
            await graphiti.build_indices_and_constraints()
            return cls(graphiti)
        except Exception as exc:
            if not use_lite_fallback:
                raise
            return await cls._connect_lite(DEFAULT_FALKORDB_LITE_PATH)
```

This is the **modern (2026)** pattern — replaces the older direct `FalkorDriver` import from Phase-1B P1B-07. The `Graphiti(uri=...)` constructor handles driver wiring internally.

### §6. KCG Cognee FalkorDB adapter (`cianfhoghlaim/core/cognee/_graph/_shared/falkordb.py:19`)

`FalkorDBClient(GraphClient)` — concrete ABC implementation that wraps the raw `falkordb.FalkorDB` client. 323 lines, implements `create_node`, `create_edge`, `query`, `get_neighbors`, `delete_node/edge`, `create_index`, `get_schema`. NOTE: this adapter does NOT have a vector-query method — vector search is expected to go through `db.idx.vector.queryNodes()` directly via `query()`.

### §7. Docker image — `falkordb/falkordb:latest` (hub.docker.com)

- Pulls: **500K+** on Docker Hub (16 stars shown on the registry metadata; 4-day-old tag updates)
- License: **SSPLv1** (Server Side Public License v1) — MongoDB-style copyleft; **important** for SaaS deployments
- Size: ~134 MB (latest-alpine)
- 500K+ pulls; React2Shell (CVE-2025-55182) fixed from v4.14.9
- Required Redis: **8.0.0 or later** (7.x and earlier **not supported**)

```bash
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest
# 6379 = RESP (Redis) protocol; 3000 = FalkorDB Browser UI
```

## Env

| Env var | Value | Where set |
|:--|:--|:--|
| `FALKORDB_URI` | `falkordb://falkordb:6379` | `graphiti_client.py:51` (Locket / mise) |
| `FALKORDB_LITE_PATH` | `/tmp/falkordb_lite` | `graphiti_client.py:55` (embedded fallback) |
| `FALKORDB_HOST` | `falkordb` | compose env (DNS to falkordb container) |
| `FALKORDB_PORT` | `6379` | compose env |
| `FALKORDB_UI_PORT` | `3000` | compose env (Browser UI) |
| `FALKORDB_PASSWORD` | `devpassword` | compose env (dev only) |
| `BROWSER` | `1` | compose env (enable Browser UI) |
| `REDIS_ARGS` | `--requirepass yourpassword` | compose env (auth mode) |
| `OPENAI_API_KEY` | `infisical://dev-baile/openai/api_key` | Locket (Graphiti embeddings) |
| `DRAGONFLY_URL` | `redis://dragonfly:6379/0` | compose env (Graphiti episode cache) |

**Protocol dual-stack:** FalkorDB speaks **RESP** (port 6379) and **Bolt** (Neo4j wire protocol). This is why `graphiti-core` and `falkordb-py` work with the same `falkordb://` URI.

## CCC anchors

| Path | What lives there |
|:--|:--|
| `infrastructure/stacks/falkordb/{compose,sidecar,pangolin,secrets.env,blueprint,README}.yaml\|md` | 6-file GOLD_STANDARD stack |
| `infrastructure/stacks/graphiti/` | Graphiti Python server (port 8000) |
| `infrastructure/stacks/dragonfly/` | Episode cache for Graphiti |
| `infrastructure/pangolin/private-resources.blueprint.yaml:62-97` | falkordb.cianfhoghlaim.ie route |
| `cianfhoghlaim/core/cognee/_graph/graphiti_client.py` | **Production** Graphiti client (uses `Graphiti(uri=...)`, with FalkorDB Lite fallback) |
| `cianfhoghlaim/core/cognee/_graph/_shared/falkordb.py` | FalkorDB ABC adapter (no vector method) |
| `cianfhoghlaim/core/cognee/_graph/_shared/interface.py` | `GraphClient` ABC base |
| `openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/oideachais-storage/spec.md:21-34` | FalkorDB canonical decision |
| `.agents/skills/falkordb/SKILL.md` | Skill (note: still references port 7687 / Bolt — outdated) |
| `falkordb/falkordb:latest-alpine` (Docker) | The image we actually deploy |

**Search terms that hit:** `FalkorDriver`, `Graphiti(uri=...)`, `vecf32(...)`, `db.idx.vector.queryNodes`, `vector.so`, `HNSW`, `falkordb_lite`, `CYPHER`, `add_episode`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-11 | Initial FalkorDB stack added to `infrastructure/stacks/` |
| 2026-01 | Dragonfly cache layer for Graphiti episodes added |
| 2026-03 | Graphiti episodes wired across 12 leabharlann subdirs |
| 2026-04 | RisingWave CDC source → FalkorDB via Iceberg sink added |
| 2026-05 | (upstream) graphiti-core 0.5 — FalkorDB Lite embedded mode introduced |
| **2026-06-28** | **DRIFT:** Phase-1B P1B-07 spec mandates `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]` on the container, but `infrastructure/stacks/falkordb/compose.yaml:18-37` does NOT have this `command:` field. **Vector queries silently fail in production.** |
| 2026-06-28 | **DRIFT:** `.agents/skills/falkordb/SKILL.md:43-46` references port `7687 (Bolt)` and hostname `falkordb.cianfhoghlaim.ie` — but the compose stack uses **port 6379 (RESP)**. The Neo4j-style Bolt URL is also supported, but the KCG default in `graphiti_client.py:51` is the RESP `falkordb://falkordb:6379` URI. |
| 2026-06-28 | **DRIFT:** Phase-1B P1B-07 snippet (`graphiti_client.py:44`) uses `from graphiti_core.driver.falkordb_driver import FalkorDriver` — but the production code (`cianfhoghlaim/core/cognee/_graph/graphiti_client.py:40,99`) uses `from graphiti_core import Graphiti` and lets `Graphiti(uri="falkordb://...")` instantiate the driver internally. The Phase-1B snippet is **stale**. |
| 2026-06-28 | **DRIFT:** `.agents/skills/falkordb/SKILL.md:92-99` shows vector index syntax `CREATE VECTOR INDEX topic_embedding ON (t:Topic) FOR (t.embedding) OPTIONS {dimension: 1536, similarity_function: 'cosine'}` — but current docs use `CREATE VECTOR INDEX FOR (p:Product) ON (p.description) OPTIONS {dimension:128, similarityFunction:'euclidean'}` (reversed clause order; camelCase `similarityFunction`). The skill is **stale by 1 release cycle**. |

## Anti-patterns

1. **NEVER** use FalkorDB without `vector.so` loaded — the `CREATE VECTOR INDEX` and `db.idx.vector.queryNodes` procedures are not registered otherwise; queries return `unknown procedure` errors.
2. **NEVER** use Redis 7.x with FalkorDB — the Docker image requires Redis 8.0.0+ at runtime (and pulls the right Redis internally). Self-hosting requires explicit Redis 8 upgrade.
3. **NEVER** run graphiti-core 0.5 with both `FalkorDriver` and `Neo4jDriver` in the same process — the Graphiti instance is single-driver; mixing them causes cross-graph query leakage.
4. **NEVER** query vector indexes with property filters in the same Cypher query — the docs explicitly call this out: "Vector queries don't combine well with property filters." Two-step pattern: (a) kNN vector search → (b) graph traversal on the resulting node IDs.
5. **NEVER** embed raw user strings into Cypher (the `FalkorDBClient` in `cognee/_graph/_shared/falkordb.py:170-177` interpolates them — this is a SQL-injection-class vulnerability; use the `params` argument instead).
6. **NEVER** build large vector indexes without tuning `efConstruction` — default 200 is fine for ≤100k vectors, but ≥1M vectors need 400+ for adequate recall.
7. **NEVER** use SSpath (single-source all-targets) for production traffic — it's `O(V*E)` and will exhaust memory on graphs >100k nodes. Use SPpath for point-to-point queries.

## Decision matrix

| Decision | Choice | Rationale (sourced) |
|:--|:--|:--|
| Vector + graph DB | **FalkorDB** | Sparse-matrix GraphBLAS + HNSW vector in one engine; 500K+ Docker pulls |
| Vector index algorithm | **HNSW only** (no FLAT option) | docs.falkordb.com/cypher/indexing/vector-index.html — only HNSW is implemented |
| Vector similarity functions | **`cosine`** for embeddings, `euclidean` for raw data | docs: cosine is best for normalized embeddings (OpenAI, Sentence Transformers) |
| Wire protocol | **RESP** (port 6379) | KCG default; `falkordb://` URI scheme |
| Cypher dialect | **OpenCypher v9 + proprietary** | docs.falkordb.com/cypher — label expressions unsupported |
| Episode cache | **Dragonfly** | 5× faster than Redis (per Phase-1B P1B-07 decision) |
| Local dev fallback | **FalkorDB Lite** (SQLite-backed) | graphiti-core 0.5+; zero-config; `graphiti_client.py:111-131` |
| Cypher encoding | **JSON-form `vecf32([...])`** | docs; `vec.f32` is the only vector constructor |
| License | **SSPLv1** | MongoDB-style copyleft; OK for in-house use, blocking for SaaS redistribution |
| Embedding dim for OpenAI `text-embedding-3-small` | **1536** | OpenAI spec; must match index `dimension:` |
| HNSW `M` (default) | **16** | docs; raise to 32 for higher recall at 2× memory cost |
| Bulk loading | **`falkordb-bulk-loader`** (`pip install falkordb-bulk-loader`) | docs.falkordb.com — 10–100× faster than per-row `graph.query()` |
| MCP exposure | `falkordb.cianfhoghlaim.ie:3000` (Browser UI only — no API) | `pangolin.yaml` — TinyAuth-protected |
| CDC ingestion | **RisingWave → Iceberg → FalkorDB** | per Phase-1B P1B-07 |
| Graphiti URI scheme | `falkordb://host:port` (graphiti-core 0.5+) | docs.falkordb.com/agentic-memory/graphiti.html — `bolt://` also valid |

## §8. Refactor opportunities

The following drift items should be filed as `openspec/changes/<id>/` proposals:

1. **`falkordb-vector-so-loadable` (HIGH)** — Add `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]` (or the upstream `falkordb-server --loadmodule /etc/falkordb/vector.so`) to `infrastructure/stacks/falkordb/compose.yaml:18-37`. Without this, every vector-index call from `oideachais-semantic-search` and `meaisinfhoghlaim-agent-frameworks` fails silently. **Verify with** `docker exec falkordb redis-cli MODULE LIST | grep vector`.

2. **`falkordb-skill-refresh` (MEDIUM)** — Rewrite `.agents/skills/falkordb/SKILL.md:43-46, 92-99` to use the current RESP-port-6379 default and the current `CREATE VECTOR INDEX FOR ... ON ... OPTIONS {...}` syntax. The skill currently teaches the wrong port and wrong clause order.

3. **`phase-1b-p1b07-snippet-stale` (LOW)** — Update `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/P1B-07-falkordb-graphiti-dragonfly-risingwave.md:43-66` to use `Graphiti(uri="falkordb://falkordb:6379")` instead of `FalkorDriver(host="falkordb", port=6379)`. The current snippet reflects pre-0.5 Graphiti and would mislead future agents.

4. **`falkordb-cognee-cypher-injection` (HIGH)** — `cianfhoghlaim/core/cognee/_graph/_shared/falkordb.py:170-177` and `:204-212` interpolate user-controlled values into Cypher strings via f-strings. Refactor to use the `params=` argument of `graph.query(cypher, params)` so values are bound instead of interpolated.

5. **`falkordb-abc-vector-method` (MEDIUM)** — Add a `vector_query(label, attr, k, query_vec) -> list[(GraphNode, score)]` method to the `GraphClient` ABC (`cianfhoghlaim/core/cognee/_graph/_shared/interface.py`) so `FalkorDBClient`, `Neo4jClient`, `MemgraphClient` all expose a uniform vector-query surface. Today only FalkorDB supports it; the abstraction will let the new `oideachais-semantic-search` paths stay backend-agnostic.

6. **`falkordb-bulk-loader-pipeline` (MEDIUM)** — Phase-1B specifies 12 leabharlann subdirs × 216 docs = 2,592 episodes in `graphiti`. Today each `add_episode` is a single round-trip. Replace with `falkordb-bulk-loader` for the bulk re-ingestion path; the existing `graphiti_client.add_episode()` remains the live-write surface.

7. **`falkordb-dragonfly-pangolin-route` (LOW)** — `pangolin/private-resources.blueprint.yaml:62-97` exposes the falkordb Browser UI but **not** the Redis RESP port. Graphiti clients on other hosts can only reach FalkorDB via the docker-compose network. If we ever run the Graphiti server on a different stack host (e.g. a dedicated agent VM), we'll need to add a Pangolin route for `falkordb.cianfhoghlaim.ie:6379`.

8. **`falkordb-license-ssplv1-audit` (LOW)** — SSPLv1 is acceptable for our self-hosted use case, but any future move to offer "FalkorDB-as-a-Service" on `arm1-oci` would force either a source-publication obligation or a license change. Capture the SSPLv1 audit decision in `openspec/specs/agent-memory-systems/spec.md` so it's discoverable.

9. **`falkordb-risingwave-cdc-implementation` (MEDIUM)** — The Phase-1B P1B-07 spec claims "RisingWave → Iceberg → FalkorDB" is wired, but `infrastructure/stacks/risingwave/` has no Dagster asset or Iceberg-sink glue. Build the missing `risingwave_to_falkordb` Dagster asset in `oideachais-pipeline`.

10. **`graphiti-lite-vs-prod-metrics` (LOW)** — `graphiti_client.is_lite` returns a bool but the agent layer never logs/metrics it. Add a Langfuse span tag `falkordb.backend=production|lite` so we can observe fallback rate in production.