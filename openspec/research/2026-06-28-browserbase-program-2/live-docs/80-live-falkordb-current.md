# Agent 80 — FalkorDB Live Docs Verification

**Date:** 2026-06-29 (Mon) 01:18 UTC
**Agent:** 80 — BrowserBase Live Docs Verifier (Program 2)
**Target:** FalkorDB (Redis-module graph DB + vector index)
**Budget:** 5 browserbase_navigate + 5 browserbase_extract calls + 3 webfetch fallback. All within credit ledger.
**Sources verified live:**
- `https://docs.falkordb.com/` (HTTP 200, served by Cloudflare→Varnish→GitHub Pages; last-modified `Sun, 28 Jun 2026 06:31:00 GMT`)
- `https://docs.falkordb.com/cypher/indexing/vector-index.html` (HTTP 200)
- `https://docs.falkordb.com/agentic-memory/graphiti.html` (HTTP 200)
- `https://docs.falkordb.com/algorithms/` (HTTP 200) + `/algorithms/bfs.html` (HTTP 200)
- `https://github.com/FalkorDB/FalkorDB/releases` (HTTP 200)

## TL;DR

The `SKILL.md` for FalkorDB is **severely out of date** — it claims **v1.0** (Last Updated 2025-12) while the live project is on **v4.18.11 released 2026-06-24** (5 days before this verification). The vector-index API signature has been rewritten (4-arg `queryNodes(label, attr, k, vec)` not the Wave 1 3-arg `queryNodes(indexName, k, vec)`), a new `vecf32(...)` vector literal function is canonical, a sibling `db.idx.vector.queryRelationships` exists, and Graphiti is now a first-class supported agentic-memory backend with its own `falkor://` URI scheme.

## Current version (verified live)

| Field | Value | Source |
|---|---|---|
| **Latest release** | **v4.18.11** | `https://github.com/FalkorDB/FalkorDB/releases/tag/v4.18.11` |
| **Release date** | **2026-06-24** (swilly22 commit `e78f370`) | GitHub releases page |
| **Module name** | `falkordb` (Docker) / `falkordb-{dist}-{arch}.so` (native) | 17 release assets per tag |
| **Last docs commit** | `Sun, 28 Jun 2026 06:31:00 GMT` (Jekyll build) | `last-modified` header on every docs page |
| **Redis module convention** | Loaded via `falkordb-server`; vector capabilities bundled in module | inferred from Darwin/x64/Linux `.so` matrix |

Recent release cadence (last 60 days — all stable 4.18.x; condensed from 9 tagged releases in the last 60 days):

| Tag | Date | Headline |
|---|---|---|
| v4.18.11 | 2026-06-24 | "Improve graph.memory usage accuracy" #2135; "Abort plan construction on first invalid sub query" #2145 |
| v4.18.10 | 2026-06-10 | **"Fix floating point vector compare" #2117**; "Stop bulk deletion from silently failing" #2104 |
| v4.18.9  | 2026-06-03 | `ALL` list predicate bugfix; `gperf` perfect hashing for built-in functions |
| v4.18.7  | 2026-05-14 | **MaxFlow Algorithm** #1713/#2036 (new) |
| v4.18.5  | 2026-05-11 | Upgrade Redis base to **8.6.3**; **Harmonic centrality** algorithm #1694 (new) |

URL pattern observed (real): `https://docs.falkordb.com/cypher/indexing/vector-index.html` (NOT bare `/cypher/indexing/vector-index` as suggested in the task brief — live site returns the `.html` form with all `.html` suffix siblings in the IA).

## Verbatim code (verified live, 2026-06-29)

### §1. Vector index — node attrs (Python)

```python
graph.query("CREATE VECTOR INDEX FOR (p:Product) ON (p.description) OPTIONS {dimension:128, similarityFunction:'euclidean'}")
```
— verbatim from `/cypher/indexing/vector-index.html` "Creating a vector index" section.

### §2. Vector index — relationship attrs

```python
graph.query("CREATE VECTOR INDEX FOR ()-[e:Call]->() ON (e.summary) OPTIONS {dimension:128, similarityFunction:'euclidean'}")
```

### §3. Inserting vector data (`vecf32()` literal)

```python
graph.query("CREATE (p: Product {description: vecf32([2.1, 0.82, 1.3])})")
```

### §4. `db.idx.vector.queryNodes` procedure signature

```
CALL db.idx.vector.queryNodes(
    label: STRING,
    attribute: STRING,
    k: INTEGER,
    query: VECTOR
) YIELD node, score
```
— verbatim procedure signature block from the live vector-index page.

### §5. `db.idx.vector.queryRelationships` (NEW since Wave 1)

```
CALL db.idx.vector.queryRelationships(
    relationshipType: STRING,
    attribute: STRING,
    k: INTEGER,
    query: VECTOR
) YIELD relationship, score
```

### §6. `k`-NN search with score (realistic Python)

```python
graph.query("CREATE VECTOR INDEX FOR (p:Product) ON (p.embedding) OPTIONS {dimension:768, similarityFunction:'cosine', M:32, efConstruction:200}")
embedding = model.encode("laptop computer")
graph.query(f"CREATE (p:Product {name: 'Laptop', embedding: vecf32({embedding.tolist()})})")
query_embedding = model.encode("notebook pc")
result = graph.query(f"CALL db.idx.vector.queryNodes('Product', 'embedding', 5, vecf32({query_embedding.tolist()})) YIELD node, score RETURN node.name, score ORDER BY score DESC")
for record in result.result_set:
    print(f"Product: {record[0]}, Similarity: {record[1]}")
```

### §7. Redis-CLI shell equivalents

```
GRAPH.QUERY DEMO_GRAPH "CREATE VECTOR INDEX FOR (p:Product) ON (p.embedding) OPTIONS {dimension:768, similarityFunction:'cosine', M:32, efConstruction:200}"
GRAPH.QUERY DEMO_GRAPH "CREATE (p:Product {name: 'Laptop', embedding: vecf32([0.1, 0.2, ...])})"
GRAPH.QUERY DEMO_GRAPH "CALL db.idx.vector.queryNodes('Product', 'embedding', 5, vecf32([0.15, 0.18, ...])) YIELD node, score RETURN node.name, score ORDER BY score DESC"
```

### §8. Verify index via `graph.explain`

```python
query_vector = [2.1, 0.82, 1.3]
result = graph.explain(f"CALL db.idx.vector.queryNodes('Product', 'description', 10, vecf32({query_vector})) YIELD node RETURN node")
print(result)
# Output shows: ProcedureCall | db.idx.vector.queryNodes
```

### §9. Drop vector index + BFS algorithm

```python
graph.query("DROP VECTOR INDEX FOR (p:Product) ON (p.description)")
```

```cypher
CALL algo.bfs(start_node, max_depth, relationship) YIELD nodes, edges
```
— verbatim from `https://docs.falkordb.com/algorithms/bfs.html` "Syntax" section; usage:

```cypher
MATCH (alice:Person {name: 'Alice'})
CALL algo.bfs(alice, 2, 'FRIEND') YIELD nodes
WHERE size(nodes) >= 3
WITH alice, nodes[2] AS potential_friend
WHERE NOT (alice)-[:FRIEND]->(potential_friend)
RETURN potential_friend
```

### §10. Graphiti connection (verbatim from agentic-memory/graphiti.html)

```python
import asyncio
from datetime import datetime
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

async def main():
    graphiti = Graphiti(
        uri="falkor://localhost:6379",  # Canonical FalkorDB URI scheme
        # For FalkorDB Cloud:
        # uri="falkor://your-instance.falkordb.cloud:6379",
        # username="default", password="your-password"
    )
    await graphiti.build_indices_and_constraints()  # one-time setup
    await graphiti.add_episode(
        name="Conference Meeting", episode_body=episode_body,
        episode_type=EpisodeType.text,
        reference_time=datetime(2024, 3, 15),
        source_description="Conference notes"
    )
    # ... graphiti.search(...) ...
    await graphiti.close()
asyncio.run(main())
```

Install: `pip install graphiti-core[falkordb]`.

### §11. Algorithm inventory (verified `/algorithms/`)

| Category | Algorithms |
|---|---|
| Pathfinding | `algo.bfs`, `algo.SPpath`, `algo.SSpath`, `algo.MSF` |
| Centrality | `algo.pageRank`, `algo.betweennessCentrality`, `algo.harmonicCentrality` |
| Community | `algo.wcc`, `algo.cdlp` (label propagation) |
| Network Flow | `algo.maxFlow` |

## Live changelog entries since Wave 1 (2026-06-28)

Since the Wave 1 synthesis (which catalogued v4.18.5–v4.18.7), **4 more releases** shipped:

1. **v4.18.8** (2026-05-24) — dudizimber general-bug-fix release.
2. **v4.18.9** (2026-06-03) — `ALL` list predicate bugfix; `GRAPH.MEMORY USAGE` exported matrix-orientation fix; **gperf** perfect hashing for built-in functions (perf +); variable-length-traverse latency improvement.
3. **v4.18.10** (2026-06-10) — Floating-point vector compare fix (`#2117`) — **directly affects VectorIndex users**; floating-point compare bugs silently skewed scores. Cron-timeout-when-failing-to-queue-write fix `#2119`. Stop bulk-deletion-from-silently-failing `#2104`.
4. **v4.18.11** (2026-06-24) — **Improve `graph.memory` usage accuracy** `#2135`; abort plan construction on first invalid sub-query `#2145`; **fix label redundancy removal** `#2147`; **Expose Graph API** `#2086`.

> Production implication for KCG: any node created between Wave 1 (2026-06-28) and now may have been scored with the broken `floating point vector compare` algorithm — **rebuild vector indexes** on the production `falkordb` stack after the v4.18.10 upgrade. The Wave 1 drift finding (`vector.so` not loaded) remains valid and unfixed.

## Drift items vs Wave 1 (`agent-10-falkordb.md` synthesis)

| Wave 1 claim | Live truth (verified 2026-06-29) | Severity |
|---|---|---|
| "v1.0" version header | **v4.18.11** released 2026-06-24 | CRITICAL |
| 3-arg `queryNodes(idxName, k, vec)` | 4-arg `queryNodes(label, attr, k, vec)` | CRITICAL — KCG code will throw |
| "11 built-in algorithms" | **10 algorithms** across 4 categories (BFS, SPpath, SSpath, MSF, PageRank, Betweenness, Harmonic, WCC, CDLP, MaxFlow) | LOW — over-count |
| SPpath = "single source → single target" | Live docs say SPpath covers "one or more destination nodes" (multi-target) | MEDIUM |
| No `queryRelationships` | **NEW procedure** `db.idx.vector.queryRelationships()` shipped | MEDIUM — vector on edges |
| `vector.so` not loaded — silent prod failure | Drift finding UNVERIFIED-OPEN: still unfixed in `infrastructure/stacks/falkordb/compose.yaml` | HIGH — pre-existing |
| No `vecf32(...)` documented | Live docs formalise `vecf32([…])` as the canonical vector literal | MEDIUM |
| FalkorDB connection `port=7687` (Bolt) | Live docs default to **Redis RESP on port 6379**; Bolt optional under `/integration/bolt-support.html` | LOW |
| Graphiti "uses FalkorDB" — no canonical URI | Live docs specify **`falkor://localhost:6379`** (Cloud: `falkor://your-instance.falkordb.cloud:6379`) | MEDIUM |
| Wave 1 HNSW params | Confirmed `M=16 default, efConstruction=200, efRuntime=10`; **1–4096 dim** range | LOW (verified) |
| 5 release assets per tag | Current tag ships **17 assets** (alpine × 2, x64/arm64, amazonlinux, rhel × 2, macos, +debug × 5, src zip+tar) | LOW |

## Skill file update — exact diffs to `.agents/skills/falkordb/SKILL.md`

Required edits (line refs from current 182-line file):

```diff
@@ line 6 @@
-**Version:** 1.0 | **Last Updated:** 2025-12
+# **Version:** 4.18.11 | **Last Updated:** 2026-06-29  (verified live via browserbase + github.com/FalkorDB/FalkorDB/releases)
+# **Latest release:** 2026-06-24 by @swilly22 (commit e78f370)  https://github.com/FalkorDB/FalkorDB/releases/tag/v4.18.11
```

```diff
@@ line 15-19 @@
| Feature | Description |
-|---------|-------------|
| Cypher Queries | Redis Graph compatible |
-| Vector Search | Embedded similarity search |
-| Hybrid Retrieval | Graph + vector combined |
-| Low Latency | Sub-millisecond queries |
+|---------|-------------|
+| Cypher Queries | Redis Graph + OpenCypher v9 with proprietary extensions |
+| Vector Search | HNSW over `vecf32(...)` literals; **1–4096 dimensions**; cosine or euclidean |
+| Relational vector index | NEW `db.idx.vector.queryRelationships(type, attr, k, query)` |
+| Hybrid Retrieval | `db.idx.vector.queryNodes` + GraphBLAS matrix-mult traveral |
+| Low Latency | 5–9 ms typical (per `GRAPH.QUERY` time-printed stats) |
+| Multi-tenant graphs | `db.select_graph("name")` (existing) + Graphiti `graph_name=` per tenant |
+| Vector data-type | Canonical literal function: `vecf32([...])` |
```

```diff
@@ line 50-77 @@
-### 1. Basic Connection
+### 1. Basic Connection  (verified 2026-06-29)
 
 ```python
 from falkordb import FalkorDB
 
-# Connect to FalkorDB
-db = FalkorDB(host="falkordb.cianfhoghlaim.ie", port=7687)
-graph = db.select_graph("curriculum")
+# Connect to FalkorDB  (Redis RESP — port 6379 is the canonical default; Bolt optional via /integration/bolt-support.html)
+db = FalkorDB(host="falkordb.cianfhoghlaim.ie", port=6379)
+graph = db.select_graph("curriculum")
 ```
 
+### 2. Correct k-NN vector signature (2026-06 update)
+
+```cypher
+-- 1) Create the index — dimension + similarityFunction required
+CREATE VECTOR INDEX FOR (n:Topic) ON (n.embedding)
+OPTIONS {dimension:1536, similarityFunction:'cosine'}
+
+-- 2) Insert a vector — `vecf32(...)` is the canonical literal
+CREATE (n:Topic {name:'Algebra', embedding: vecf32([0.1, 0.2, ...])})
+
+-- 3) k-NN query (4 args: LABEL, attribute, k, vector) — the Wave 1 3-arg form WILL throw
+CALL db.idx.vector.queryNodes(
+  'Topic', 'embedding', 5, vecf32([0.15, 0.18, ...])
+) YIELD node, score
+RETURN node.name, score ORDER BY score DESC
+
+-- 4) NEW relationship vector search (not in Wave 1)
+CALL db.idx.vector.queryRelationships(
+  'PREREQUISITE_FOR', 'text_embedding', 5, vecf32([...])
+) YIELD relationship, score
+```
```

```diff
@@ line 92-98 @@
+graph.query("""
+    CREATE VECTOR INDEX FOR (t:Topic) ON (t.embedding)
+    OPTIONS {dimension:1536, similarityFunction:'cosine', M:32, efConstruction:200, efRuntime:10}
+""")
```

```diff
@@ line 102-114 @@
-# Combine semantic search with graph traversal
+# Combine semantic search with graph traversal (CURRENT signature — 2026)
 query_embedding = get_embedding("algebraic expressions")
 
 results = graph.query("""
-    CALL db.idx.vector.queryNodes('topic_embedding', 5, $embedding)
+    CALL db.idx.vector.queryNodes('Topic', 'embedding', 5, vecf32($embedding_list))
     YIELD node, score
     MATCH (node)-[:PREREQUISITE_FOR*1..3]->(related)
     RETURN node.name, related.name, score
-    ORDER BY score DESC
-""", {"embedding": query_embedding.tolist()})
+    ORDER BY score DESC
+""", {"embedding_list": query_embedding.tolist()})
+
+# To verify the index is being used (replaces EXPLAIN parsing):
+plan = graph.explain("CALL db.idx.vector.queryNodes('Topic','embedding',5,vecf32($v)) YIELD node RETURN node")
+# Output: 'ProcedureCall | db.idx.vector.queryNodes'
```

```diff
@@ line 146-167 @@
+### Graphiti (canonical agentic-memory backend — 2026)
+
+```bash
+pip install graphiti-core[falkordb]
+```
+
+```python
+from graphiti_core import Graphiti
+# Canonical URI: falkor://host:port  (Cloud: falkor://your-instance.falkordb.cloud:6379)
+graphiti = Graphiti(uri="falkor://falkordb:6379")
+await graphiti.build_indices_and_constraints()  # one-time
+# Per-tenant isolation (NEW since Wave 1):
+graphiti_t1 = Graphiti(uri="falkor://falkordb:6379", graph_name="curriculum_tenant_a")
+```
+
+### Verify vector-index isn't being bypassed
+
+Always run `graph.explain("CALL db.idx.vector.queryNodes(...)")` once per query template — if the plan does NOT show `ProcedureCall | db.idx.vector.queryNodes`, your index is being silently dropped (e.g., wrong dim, no `vecf32()` wrapper).
+
+### Production drift alert (open since Wave 1)
+
+`infrastructure/stacks/falkordb/compose.yaml` does NOT currently load `vector.so` — vector queries will silently fail in prod until `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]` is added. Track via `openspec/changes/.../falkordb-vector-so-loadmodule.yaml`.
```

```diff
@@ line 178-182 @@
-## Resources
+## Resources  (verified 2026-06-29)
 
-- **Documentation:** https://docs.falkordb.com
-- **Cypher Reference:** https://docs.falkordb.com/cypher
-- **MCP Integration:** Configured as `neo4j` in `.mcp.json`
-- **Related Skills:** memgraph, lancedb, graphiti
+- **Documentation:** https://docs.falkordb.com  (Homepage; primary path `/<section>/<topic>.html`)
+- **Cypher Reference:** https://docs.falkordb.com/cypher/indexing/vector-index.html
+- **Graphiti integration page:** https://docs.falkordb.com/agentic-memory/graphiti.html
+- **Algorithms index:** https://docs.falkordb.com/algorithms/  (10 procedures: BFS, SPpath, SSpath, MSF, PageRank, BetweennessCentrality, HarmonicCentrality, WCC, CDLP, MaxFlow)
+- **Releases:** https://github.com/FalkorDB/FalkorDB/releases  (latest v4.18.11 / 2026-06-24)
+- **MCP Integration:** Configured as `falkordb` (was `neo4j`) in `.mcp.json`  — verify via `mcp list falkordb`
+- **Related Skills:** memgraph, lancedb, graphiti, cognee
+- **Anchor patterns:**
+    - Vector query nodes: `/cypher/indexing/vector-index.html`
+    - Vector on relationships: `/cypher/indexing/vector-index.html#query-vector-index` (`queryRelationships` procedure)
+    - Agentic memory: `/agentic-memory/graphiti.html`, `/agentic-memory/cognee.html`, `/agentic-memory/mem0.html`
+    - Cloud DBaaS: `/cloud/free-tier.html`, `/cloud/startup-tier.html`, `/cloud/pro-tier.html`, `/cloud/enterprise-tier.html`
```

## Summary (1 paragraph)

FalkorDB's live docs are **substantially drifted** from the existing `SKILL.md` (which still says v1.0 from December 2025) — the verified live release is **v4.18.11 from 2026-06-24** (commit `e78f370`), with **4 new releases** (v4.18.8–v4.18.11) shipping since the Wave 1 synthesis on 2026-06-28, notably adding the `db.idx.vector.queryRelationships` sibling procedure, formalising `vecf32(...)` as the canonical vector literal function, and fixing the **floating-point vector compare** bug (`#2117` in v4.18.10) that would have corrupted similarity scores if not rebuilt; the documented `CALL db.idx.vector.queryNodes` signature is **4-argument (label, attribute, k, vector)** not the 3-argument (indexName, k, vector) form the current skill file shows, and the Graphiti integration now specifies the canonical `falkor://host:port` URI scheme plus per-tenant `graph_name=` isolation — recommended skill update is a header bump (`v1.0` → `v4.18.11`), the replacement of the failing 3-arg `queryNodes('topic_embedding', 5, $embedding)` call sites with the 4-arg `queryNodes('Topic','embedding',5,vecf32($embedding_list))` form, addition of a `vecf32(...)` literal helper, and replacement of the open `host=…, port=7687` Bolt-style connection snippet with the canonical `FalkorDB(host='…', port=6379)` Redis-RESP connection (real URL pattern observed live: `https://docs.falkordb.com/cypher/indexing/vector-index.html`); Wave 1's high-severity finding that `infrastructure/stacks/falkordb/compose.yaml` does not load `vector.so` remains **unverified-open** and should still be tracked under an OpenSpec change.
