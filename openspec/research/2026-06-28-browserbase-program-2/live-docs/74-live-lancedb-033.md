# Agent 74 — Live lancedb-033 Doc Verifier

**Date:** 2026-06-29
**Source live URLs visited:**
`https://pypi.org/project/lancedb/` · `https://lancedb.github.io/lancedb/` ·
`https://lancedb.github.io/lancedb/python/python/` · `https://docs.lancedb.com/llms.txt` ·
`https://docs.lancedb.com/indexing/vector-index.md` · `https://docs.lancedb.com/namespaces/usage.md` ·
`https://docs.lancedb.com/embedding/quickstart.md` ·
`https://github.com/lancedb/lancedb/releases` · `https://github.com/lancedb/lancedb/releases/tag/python-v0.33.0`

## 1. TL;DR

- LanceDB Python `0.33.0` released **2026-05-28**, next beta `python-v0.34.0-beta.3` shipped 2026-06-25.
- **HNSW is NOT a top-level Python vector index** — the docs state it is "available as a sub-index inside IVF partitions" via `IVF_HNSW_FLAT` / `IVF_HNSW_SQ` / `IVF_HNSW_PQ`. The current `.agents/skills/lancedb/SKILL.md` still uses `index_type="HNSW"`, which is a hard drift.
- The `LanceNamespace` API is now first-class Python (`lancedb.connect_namespace("dir", {...})`) and supports multi-level `namespace_path=["prod","search"]` table ops; REST index endpoints (Enterprise) expose `IVF_HNSW_SQ` directly.

## 2. Current Version (PyPI)

| Field | Value |
|:--|:--|
| Latest stable | **`lancedb 0.33.0`** |
| Released | **May 28, 2026** |
| Python | `>=3.10` |
| Wheel abi | `cp39-abi3` (Windows x86-64, manylinux glibc 2.17/2.28, macOS 11+ ARM64) |
| Source dist | none (binary-only) |
| Commit | `c0a9a4d48a384096dbfd928fbbf808f6527dba9c` (`refs/tags/python-v0.33.0`) |
| Extras | `azure, clip, dev, docs, embeddings, pylance, siglip, tests` |
| License | Apache-2.0 |
| Status classifier | `3 - Alpha` |
| Recent pre-releases | `python-v0.34.0-beta.3` (25 Jun), `python-v0.33.1-beta.2` (04 Jun) |

Verbatim PyPI description:

> "Stable releases are created about every 2 weeks. For the latest features and bug fixes, you can install the preview release."

## 3. Verbatim Code Examples (5–10)

### 3.1 Basic connect / open / search (PyPI README)

```python
import lancedb
db = lancedb.connect('<PATH_TO_LANCEDB_DATASET>')
table = db.open_table('my_table')
results = table.search([0.1, 0.3]).limit(20).to_list()
print(results)
```

### 3.2 `create_index` config union (Python SDK ref, current)

> "config: `Optional[Union[IvfFlat, IvfPq, IvfRq, HnswPq, HnswSq, HnswFlat, BTree, Bitmap, LabelList, Fm, FTS]] = None`"

### 3.3 IVF_HNSW_SQ via Python config (docs.lancedb.com/indexing/vector-index.md)

> "Use these Python config classes for the index types shown on this page:
> `IVF_FLAT` → `IvfFlat`; `IVF_PQ` → `IvfPq`; `IVF_RQ` → `IvfRq`;
> `IVF_SQ` → `IvfSq`; `IVF_HNSW_FLAT` → `IvfHnswFlat`;
> `IVF_HNSW_PQ` → `IvfHnswPq`; `IVF_HNSW_SQ` → `IvfHnswSq`."

```python
# Indexing nested vector field
table.create_index(
    vector_column_name="image.embedding",
    num_partitions=1,
    num_sub_vectors=1,
    name="image_embedding_idx",
)
results = (
    table.search([0.0, 1.0], vector_column_name="image.embedding")
    .limit(1)
    .to_list()
)
```

```python
# Async config-object form
import lancedb, numpy as np
from lancedb.index import IvfPq

async def main():
    data = [{"id": i, "vector": np.random.random(8).astype(np.float32).tolist()}
            for i in range(512)]
    db = await lancedb.connect_async("ex_lancedb")
    table = await db.create_table("vector_index_async", data=data, mode="overwrite")
    await table.create_index("vector", config=IvfPq(
        distance_type="cosine", num_partitions=16, num_sub_vectors=4,
    ))
```

### 3.4 IVF_HNSW_SQ via sync `index_type` (vector-index.md)

```python
# HNSW-backed IVF (the actual canonical HNSW form)
table.create_index(index_type="IVF_HNSW_SQ")
# For unquantized: change index_type to "IVF_HNSW_FLAT"
```

```python
# IVF_PQ with cosine + 1536-d
table.create_index(
    metric="cosine",
    vector_column_name="keywords_embeddings",
)
```

```python
# Recall measurement: bypass ANN vs. nprobes=20
query = np.random.random(128)
k = 10
truth = set(table.search(query).bypass_vector_index().limit(k).to_pandas()["id"])
ann   = set(table.search(query).nprobes(20).limit(k).to_pandas()["id"])
recall_at_k = len(truth & ann) / k
```

### 3.5 LanceNamespace table ops (namespaces/usage.md)

```python
import lancedb

db = lancedb.connect_namespace("dir", {"root": "./local_lancedb"})
db.create_namespace(["prod"], mode="exist_ok")
db.create_namespace(["prod", "search"], mode="exist_ok")
db.create_namespace(["prod", "recommendations"], mode="exist_ok")

db.create_table(
    "user",
    data=[{"id": 1, "vector": [0.1, 0.2], "name": "alice"}],
    namespace_path=["prod", "search"],
    mode="create",
)
db.create_table(
    "user",
    data=[{"id": 2, "vector": [0.3, 0.4], "name": "bob"}],
    namespace_path=["prod", "recommendations"],
    mode="create",
)
print(db.list_tables(namespace_path=["prod", "search"]))  # ['user']
```

```typescript
const db = await lancedb.connectNamespace("dir", { root: "./local_lancedb" });
await db.createTable(
  "user",
  [{ id: 1, vector: [0.1, 0.2], name: "alice" }],
  ["prod", "search"],
  { mode: "create" },
);
```

### 3.6 Embeddings quickstart (embedding/quickstart.md)

```python
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry

model = get_registry().get("sentence-transformers").create(
    name="BAAI/bge-small-en-v1.5",
)

class Words(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()

db = lancedb.connect(...)
table = db.create_table("words", schema=Words)
table.add([{"text": "hello world"}, {"text": "goodbye world"}])
actual = table.search("greetings").limit(1).to_pydantic(Words)[0]
print(actual.text)
```

## 4. Changelog Since Wave 1 (since `0.29.0` series — pre-Wave 1 anchor)

| Version | Date | Headline |
|:--|:--|:--|
| 0.30.0 | 2026-03-16 | `IVF_RQ` RaBitQ quantization, `IVF_SQ` scalar quantization, table branches (`feat: add table branch support`) |
| 0.30.2 | 2026-03-31 | Bug-fix rollup |
| 0.32.0 | 2026-05-27 | Pre-0.33 hardening |
| **`0.33.0`** | **2026-05-28** | **Breaking: `fix: support nested field paths in native index creation` (#3408)**; nodejs `connectNamespace` + `renameTable` + `order_by`; python `lit()` supports `bytes`; `set_unenforced_primary_key` + `set_lsm_write_spec`; read-freshness headers for remote table consistency |
| 0.33.1-beta.2 | 2026-06-04 | Bug fixes (DataFusion merge-insert predicates, RRFReranker empty vector_results) |
| 0.34.0-beta.0 | 2026-06-18 | **Breaking: `refactor!: drop unused loss field from IndexStatistics` (#3496)**; FM-Index scalar index for substring search; `Expr.isin()`; `IndexConfig` rich per-index metadata; `rename_table` on `LanceNamespaceDatabase`; `approx` mode on vector queries; column-metadata skills |
| 0.34.0-beta.1 | 2026-06-19 | Namespace-connection `k = sys.maxsize` overflow fix |
| 0.34.0-beta.2 | 2026-06-23 | Rust Blob v2 schema + write path; `created_at` RFC 3339 parsing |
| **0.34.0-beta.3** | **2026-06-25** | Bug fixes: `stacklevel=2` on `warnings.warn`; empty `api_key` header suppression; namespace clients with dynamic headers |

Key verbatim from `0.33.0` release notes:

> "feat: support setting unenforced primary key by [@touch-of-grey] in [#3394]"
> "feat: support setting LSM write spec for a table by [@touch-of-grey] in [#3396]"
> "fix: support nested field paths in native index creation by [@Xuanwo] in [#3408]"

## 5. Drift Items (HNSW is NOT top-level)

**The current `.agents/skills/lancedb/SKILL.md` is wrong on the HNSW story.**
Verbatim from `https://docs.lancedb.com/indexing/vector-index.md`:

> "**IVF + HNSW** — In LanceDB, HNSW is not exposed as a top-level vector index.
> Instead, it's available as a sub-index inside IVF partitions. … LanceDB
> supports the unquantized variant `IVF_HNSW_FLAT`, along with quantized
> variants such as `IVF_HNSW_PQ` and `IVF_HNSW_SQ`."

Concrete drift in the existing skill (file: `.agents/skills/lancedb/SKILL.md`):

| Line | Current (DRIFT) | Should be |
|:--|:--|:--|
| L20 | "**HNSW Indexing**: High-performance ANN" | "**HNSW is a sub-index inside IVF** (`IVF_HNSW_FLAT`/`_SQ`/`_PQ`)" |
| L195-202 | `table.create_index(metric="cosine", index_type="HNSW", m=20, ef_construction=150)` | `table.create_index(metric="cosine", index_type="IVF_HNSW_SQ", m=20, ef_construction=150)` — or, async: `IvfHnswSq(m=20, ef_construction=150)` |
| L371 | `Accuracy critical | HNSW | m=20, ef_construction=150` | `Accuracy critical | IVF_HNSW_SQ | m=20, ef_construction=150, num_partitions = num_rows // 1_048_576` |
| L372 | `Large scale | IVF_HNSW_PQ | Combine both` | rename → `IVF_HNSW_SQ` (best recall/latency trade-off); add new row for `IVF_RQ` (max compression) and `IVF_PQ` (small dim) |
| L556 | `table.create_index(metric="cosine", index_type="HNSW", m=20, ef_construction=150)` | Same fix as L195-202 |
| L568 | "Drop indexes before bulk inserts > 50K rows (HNSW rebuild is slow)" | keep, but qualify as "HNSW-backed IVF rebuild is slow" |
| L628 | "Auto-reindexing — re-creates the HNSW index on every 1k writes" | "Auto-reindexing — re-creates the `IVF_PQ` (default) / `IVF_HNSW_*` index on every 1k writes" |

**The `index_type="HNSW"` string** in the sync `Table.create_index` is not
documented in the live vector-index page; the supported `index_type` strings
are the seven shown in the table above (`IVF_FLAT`, `IVF_PQ`, `IVF_RQ`,
`IVF_SQ`, `IVF_HNSW_FLAT`, `IVF_HNSW_PQ`, `IVF_HNSW_SQ`).

## 6. Skill File Update Diffs (proposed)

`File: .agents/skills/lancedb/SKILL.md`

```diff
-**Version:** >=0.26.0 (pylance >= 0.26) | **Last Updated:** 2026-06
+**Version:** >=0.33.0 (pylance >= 0.33) | **Last Updated:** 2026-06-29
```

```diff
-- **HNSW Indexing**: High-performance approximate nearest neighbor search
+- **HNSW-backed IVF Indexing**: HNSW is **not** a top-level Python
+  index in LanceDB — it is exposed only as a sub-index inside IVF
+  partitions: `IVF_HNSW_FLAT` (no quant), `IVF_HNSW_SQ` (scalar quant,
+  best recall/latency trade-off), `IVF_HNSW_PQ` (product quant).
+  Use the `IvfHnswSq` config class in async Python.
```

```diff
-**HNSW Index** (for accuracy):
-table.create_index(
-    metric="cosine",
-    index_type="HNSW",
-    m=20,
-    ef_construction=150
-)
+**HNSW-backed IVF Index** (HNSW is NOT top-level — see vector-index.md):
+table.create_index(
+    metric="cosine",
+    index_type="IVF_HNSW_SQ",   # or "IVF_HNSW_FLAT" for unquantized
+    num_partitions=64,          # num_rows // 1_048_576 starting point
+    m=20,
+    ef_construction=150,
+)
+
+# Async / config-object form (preferred for new code):
+from lancedb.index import IvfHnswSq
+await table.create_index("vector", config=IvfHnswSq(
+    distance_type="cosine", num_partitions=64, m=20, ef_construction=150,
+))
```

```diff
-| Accuracy critical | HNSW | m=20, ef_construction=150 |
-| Large scale | IVF_HNSW_PQ | Combine both |
+| Accuracy critical | IVF_HNSW_SQ | num_partitions = num_rows // 1_048_576, m=20, ef_construction=150 |
+| Best recall/size | IVF_HNSW_FLAT | m=20, ef_construction=150, no quant (raw + HNSW) |
+| Max compression | IVF_RQ | num_partitions = num_rows // 4096, RaBitQ |
+| Small dim (≤256) | IVF_PQ | num_partitions = num_rows // 4096, num_sub_vectors = dim // 8 |
```

```diff
-# .env: LANCEDB_URI=db://my-database, LANCEDB_API_KEY=...
-const cloud = await lancedb.connect(process.env.LANCEDB_URI!, { ...
+# Python: `lancedb.connect_namespace("dir", {"root": "./data"})` —
+# supports `namespace_path=["prod","search"]` for hierarchical
+# catalog. See `references/lance-namespace-and-iceberg.md` and
+# `docs.lancedb.com/namespaces/usage.md`.
+import lancedb
+db = lancedb.connect_namespace("dir", {"root": "./local_lancedb"})
+db.create_namespace(["prod", "search"], mode="exist_ok")
+db.create_table("user", data=[...], namespace_path=["prod", "search"], mode="create")
```

Also update `.agents/skills/lancedb/references/lancedb-reference-index.md`
to drop the HNSW-as-top-level claim and link to
`https://docs.lancedb.com/indexing/vector-index.md`.

## 7. Decision Matrix (index selection for KCG corpora)

| Corpus size / dim | Recommended index | Why |
|:--|:--|:--|
| < 100K rows, any dim | None (brute force) | Recall@1 = exact; build cost wasted |
| 100K–10M, dim ≤ 256 | `IVF_PQ` (`IvfPq`) | Higher accuracy than `IVF_RQ` at small dim |
| 100K–10M, dim > 256 | `IVF_HNSW_SQ` (`IvfHnswSq`) | Best recall/latency trade-off |
| > 10M, dim > 256, memory-bound | `IVF_RQ` (`IvfRq`) | ~1/32 size; small filter variance |
| Max recall, no quant, RAM ok | `IVF_HNSW_FLAT` (`IvfHnswFlat`) | Raw vectors + HNSW graph |
| Heavy `where(...)` filters | `IVF_RQ` or `IVF_PQ` | HNSW-backed IVF has higher latency variance under filters (verbatim warning in vector-index.md) |

**Source URL pattern observed (live):**
`https://docs.lancedb.com/indexing/vector-index.md` — also reachable as
`https://docs.lancedb.com/latest/indexing/vector-index` (Mintlify
versioned redirect).

**Anti-patterns to retire from the skill:**
- `index_type="HNSW"` — not a valid top-level value in the current docs.
- Claiming HNSW is "high-performance ANN" without naming `IVF_HNSW_*`.
- Mapping `m` / `ef_construction` to HNSW without also setting
  `num_partitions` (HNSW is wrapped in IVF and still needs partitioning).
- Confusing `LanceDB Cloud auto-reindexing` (which auto-creates `IVF_PQ`,
  not bare HNSW) with the `create_index(index_type="HNSW")` call.

**Quote (verbatim, from `python-v0.33.0` release page):**
> "feat: support setting unenforced primary key by [@touch-of-grey] in [#3394]"

**Quote (verbatim, from `docs.lancedb.com/indexing/vector-index.md`):**
> "In LanceDB, HNSW is not exposed as a top-level vector index. Instead,
> it's available as a sub-index inside IVF partitions."

**Quote (verbatim, from PyPI project page):**
> "Stable releases are created about every 2 weeks. For the latest
> features and bug fixes, you can install the preview release."
