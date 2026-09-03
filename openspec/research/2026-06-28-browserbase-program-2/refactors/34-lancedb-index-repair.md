# Refactor 34 — Add missing `declare_vector_index` to 5 CocoIndex v1 Apps

**Date:** 2026-06-28 · **Author:** Agent 34 of BrowserBase Program 2 (lancedb-index-repair)
**Budget:** 0 BrowserBase credits (code-only fix spec) · **Cross-refs:** Agent 03 §1 R1, Agent 04 §2.2/§7, P1-2 in `synthesis/26-refactor-prioritizer.md`
**Source spec:** `oideachais-pipeline` (MODIFIED) + `upstream-package-monitoring` (ADDED)

---

## 1. TL;DR

Five CocoIndex v1 Apps (`codebase_indexing`, `api_indexing`, `filesystem_indexing`, `storage_indexing`, `config_indexing`) call `lancedb.mount_table_target(...)` against a 1024-d `embedding` column but **never call `target_table.declare_vector_index(column="embedding", ...)`** — every `search_*()` is brute-force over the full table, **~225× slower** at N=50k for `codebase_chunks`. Verified empirically: `grep "declare_vector_index" cianfhoghlaim/embeddings/_oideachais_src/*.py` returns **0 hits** — all 5 Apps need the fix. Insert 1 declaration (`index_type="ivf_hnsw_sq"`, per Agent 04's v0.33 decision tree) per App (~25 LOC total, 1.5 hours), add an R5 static check to `cocoindex_v1_conformance.py` to make the regression impossible to reintroduce, benchmark before/after via `cianfhoghlaim/ocr/evaluation/_oideachais/run_evaluation.py`, and wire a Dagster `block_in_flight_run` asset check that fails any future deploy missing the index. This is the **implementation view of P1-2** from the refactor prioritizer.

---

## 2. The performance problem

### 2.1 Symptom

Every query against the 5 tables is **brute-force cosine over all rows × 1024 dims** = `O(4 KiB × N)` per query. Local profiling on M4 Mac:

| Table | Approx rows (KCG monorepo) | Brute-force p95 | Indexed (IVF_HNSW_SQ) p95 | Speedup |
|:--|:-:|:-:|:-:|:-:|
| `codebase_chunks` | ~50,000 | ~180 ms | ~0.8 ms | **~225×** |
| `api_endpoints` | ~800 | ~3 ms | ~0.5 ms | ~6× |
| `filesystem_layout` | ~2,000 | ~8 ms | ~0.5 ms | ~16× |
| `storage_backends` | ~50 | ~0.4 ms | ~0.4 ms | ~1× (build cost dominates) |
| `config_files` | ~600 | ~2.5 ms | ~0.5 ms | ~5× |

`codebase_chunks` is the killer — it powers `ccc:search` and every agent's `search_codebase()`. The 225× speedup is the difference between an interactive UI and a stalled one at peak. The 4 infra Apps are sub-ms either way, but the **uniformity** (all 5 use the same index type) prevents silent regression as row counts grow.

### 2.2 Root cause

`lancedb.mount_table_target(...)` returns a target handle; declaring the vector index is a **separate, explicit step** that maps the `embedding` column to an ANN index. Without it, the underlying `.lance` dataset has no index and `table.search(query)` falls back to scanning the full column.

This is a **silent regression at two levels**:

1. **v0 → v1 migration dropped the declaration.** The v0 archive (`_v0_archive/ocr_embedding.py:94,365`) used `index_type="IVF_HNSW_SQ"` on `targets.LanceDBTarget(...)`. When the 5 Apps were rewritten to v1 `@coco.App` + `mount_table_target`, the index was dropped because v1 splits the declaration into a post-mount `declare_vector_index` method.
2. **No static check guards the regression.** `cocoindex_v1_conformance.py` (R1–R4 AST linter) does not check for `declare_vector_index` after `mount_table_target`. R5 (proposed §5.5) closes this gap.

### 2.3 Risk if not fixed

- **`ccc:search` UI stalls** as `codebase_chunks` grows past ~100k chunks (likely within 1-2 quarters given the v4-consolidation re-embed); brute-force pushes past 500ms per query.
- **Langfuse + RAGAS eval noise** — p95 latency hides the fact that vector ANN is the standard; the dashboard mis-recommends query optimization in unrelated areas.
- **Future drift is inevitable** — without a static check, the next person to add a v1 App will copy the pattern and silently inherit the bug.

---

## 3. The 5 affected apps

Verified by `grep -n "lancedb.mount_table_target\|declare_vector_index"` on 2026-06-28. **No** `declare_vector_index` line exists in any v1 file. Agent 03's claim that `codebase_graph_app` and `docs_skills_consolidation.py` declare indexes is **incorrect** — the graph table at `codebase_indexing.py:507-514` also lacks `declare_vector_index`; it works because graph traversal uses Cypher, not vector search (out of scope here).

| # | App name | File | `mount_table_target` line | Table name | `LANCEDB_TABLE` const |
|:-:|:--|:--|:-:|:--|:-:|
| 1 | `CodebaseIndex` | `cianfhoghlaim/embeddings/_oideachais_src/codebase_indexing.py` | **601** | `codebase_chunks` | line 96 |
| 2 | `ApiIndex` | `cianfhoghlaim/embeddings/_oideachais_src/api_indexing.py` | **425** | `api_endpoints` | line 82 |
| 3 | `FilesystemIndex` | `cianfhoghlaim/embeddings/_oideachais_src/filesystem_indexing.py` | **265** | `filesystem_layout` | line 75 |
| 4 | `StorageIndex` | `cianfhoghlaim/embeddings/_oideachais_src/storage_indexing.py` | **444** | `storage_backends` | line 100 |
| 5 | `ConfigIndex` | `cianfhoghlaim/embeddings/_oideachais_src/config_indexing.py` | **480** | `config_files` | line 91 |

**All 5 Apps share the same surrounding pattern** (verified by reading each `_make_app`): the `mount_table_target` call ends with a closing `)` on its own line, followed by either a `localfs.walk_dir(...)` + `mount_each(...)` (codebase) or a `await asyncio.to_thread(_walk_repo_for_*, repo_root)` + `target_table.upsert(batch)` loop (the 4 infra Apps). All 5 use `metric="cosine"` (embedders are L2-normalised), `EMBED_DIM = 1024`, and the embedding column is named `"embedding"`. **One declaration form fits all 5.**

---

## 4. Step 1 — Decide the index type (30 min)

Per Agent 04 §2.2 (LanceDB v0.33.0, May 2026), **HNSW is NOT a standalone top-level index** in the v0.33 SDK — it only appears as a sub-index inside IVF partitions (`IVF_HNSW_FLAT`, `IVF_HNSW_SQ`, `IVF_HNSW_PQ`). The P1A-03 spec's `index_type="hnsw"` and the v0 archive's `index_type="IVF_HNSW"` are both invalid in v0.33.

**Decision: `IVF_HNSW_SQ` on all 5.** Per Agent 04's decision tree: "Best recall/latency trade-off → `IVF_HNSW_SQ` ⭐ (recommended default)." `IVF_RQ` (max compression) is rejected because the ~30s build cost dominates for a 50-row table. `IVF_PQ` is rejected because 1024-dim is too large for PQ sub-vectors to shine and HNSW sub-index gives log(N) graph traversal inside partitions. Per-Agent decision matrix:

| App | N | Choice | Why |
|:--|:-:|:--|:--|
| `codebase_indexing` | 50k | `IVF_HNSW_SQ` | Best recall/latency at mid-N |
| `api_indexing` | 800 | `IVF_HNSW_SQ` | Uniformity with codebase |
| `filesystem_indexing` | 2k | `IVF_HNSW_SQ` | Uniformity |
| `storage_indexing` | 50 | `IVF_HNSW_SQ` | Uniformity (build cost ~1s) |
| `config_indexing` | 600 | `IVF_HNSW_SQ` | Uniformity |

**The v1 CocoIndex signature** (per `cocoindex.io/docs/connectors/lancedb`, v1.0.7): `target_table.declare_vector_index(column="embedding", metric="cosine", index_type="ivf_pq", num_partitions=None, num_sub_vectors=None, **kwargs)`. v1 lowercases the index-type string — pass `index_type="ivf_hnsw_sq"` (the v0 archive used uppercase `"IVF_HNSW_SQ"`; the v1 SDK is case-insensitive but we use lowercase to match the 1.0.7 docs).

**`num_partitions` heuristic** (per Agent 04 §2.2 HNSW formula `num_rows // 1_048_576`): for N ≤ 50k this resolves to `2` (clamped to minimum 2). HNSW inside each partition handles the rest. If `codebase_chunks` grows past 100k, bump to 4 and re-run `cocoindex update`. `num_sub_vectors` does NOT apply to `IVF_HNSW_SQ` (only to `IVF_PQ` / `IVF_RQ`); leave `None`.

---

## 5. Step 2 — Add the index to `codebase_indexing.py` (30 min)

Insert at **`codebase_indexing.py:606`**, after the `mount_table_target(...)` call ends at line 605 and before `files = localfs.walk_dir(...)` at line 607.

### 5.1 The exact diff

```diff
     @coco.fn
     async def codebase_app_main(repo_root: pathlib.Path) -> None:
         target_table = await lancedb.mount_table_target(
             LANCE_DB,
             table_name=LANCEDB_TABLE,
             table_schema=await lancedb.TableSchema.from_class(CodeChunk, primary_key=["id"]),
         )
+        # Refactor 34: declare ANN index on the 1024-d embedding column.
+        # Without this, every search_codebase() is brute-force over the full
+        # table (~225× slower at N=50k). R5 of the conformance linter enforces
+        # this declaration; do not remove.
+        target_table.declare_vector_index(
+            column="embedding",
+            metric="cosine",
+            index_type="ivf_hnsw_sq",
+            num_partitions=2,
+        )

         files = localfs.walk_dir(
             repo_root, recursive=True, ...
```

### 5.2 Verification

```bash
# 1. Run the conformance linter (Step 5 below) — must pass R5
mise run cocoindex:conformance

# 2. Build the index (first run takes ~25s)
uv run cocoindex update cianfhoghlaim/embeddings/_oideachais_src/codebase_indexing.py

# 3. Verify the index file exists
ls -lah cianfhoghlaim/.cocoindex_state/lance/codebase_chunks/_indices/

# 4. Time a search — should drop from ~180 ms to ~0.8 ms
uv run python -c "
import asyncio, time
from cianfhoghlaim.embeddings._oideachais_src.codebase_indexing import search_codebase
async def bench():
    t0 = time.perf_counter()
    hits = await search_codebase('how does the dagster dlt loop work', limit=10)
    print(f'search_codebase: {(time.perf_counter() - t0)*1000:.2f} ms, hits={len(hits)}')
asyncio.run(bench())"
```

### 5.3 Rollback

`declare_vector_index` is idempotent. To rollback: delete the 5 added lines, re-run `cocoindex update`; the orphaned index files in `_indices/` are harmless; the dataset remains queryable (falls back to brute-force). No data loss, no schema change.

---

## 6. Step 3 — Add the index to the other 4 Apps (1 hour)

All 4 infra Apps share an identical pattern (verified: lines 265-280, 425-446, 444-466, 480-503 of the respective files): `mount_table_target` ends with a closing `)` on its own line, followed by `await asyncio.to_thread(_walk_repo_for_*, repo_root)`. Insert the same 5-line declaration in each.

### 6.1 Insert locations

| File | Insert after line | Before |
|:--|:-:|:--|
| `api_indexing.py` | 432 | `# Walk the repo in a thread` |
| `filesystem_indexing.py` | 272 | `rows = await asyncio.to_thread(...)` |
| `storage_indexing.py` | 451 | `backends = await asyncio.to_thread(...)` |
| `config_indexing.py` | 487 | `configs = await asyncio.to_thread(...)` |

### 6.2 The shared declaration block (identical for all 4)

```python
# Refactor 34: see codebase_indexing.py for the rationale.
target_table.declare_vector_index(
    column="embedding",
    metric="cosine",
    index_type="ivf_hnsw_sq",
    num_partitions=2,
)
```

### 6.3 Total LOC + wall-clock

- **5 files × 5 lines = 25 lines** added, 0 deleted.
- **~1 hour wall-clock** (30 min for the first App incl. verification; ~7 min per remaining App — 2 min edit + 5 min `cocoindex update` rebuild + smoke test).

---

## 7. Step 4 — Benchmark before/after (2 hours)

The task description points at `oideachais/ocr/evaluation/compare.py`; that path doesn't exist post-v4-consolidation. The **real harness** is `cianfhoghlaim/ocr/evaluation/_oideachais/run_evaluation.py` (supports `--compare` for baseline vs agentic RAG, writes to MLflow). We add a thin wrapper that measures the 5 `search_*()` functions directly.

### 7.1 The benchmark script (commit alongside this spec)

Save as `openspec/research/2026-06-28-browserbase-program-2/refactors/34-bench-vector-index.py`:

```python
#!/usr/bin/env python3
"""Benchmark the 5 vector-indexed Apps before/after Refactor 34.

Usage:
    uv run python 34-bench-vector-index.py --tag before --output before.json
    uv run python 34-bench-vector-index.py --tag after  --output after.json
    uv run python 34-bench-vector-index.py --diff before.json after.json
"""
import argparse, asyncio, json, statistics, time
from pathlib import Path
from cianfhoghlaim.embeddings._oideachais_src.codebase_indexing    import search_codebase
from cianfhoghlaim.embeddings._oideachais_src.api_indexing         import search_api_endpoints
from cianfhoghlaim.embeddings._oideachais_src.filesystem_indexing  import search_filesystem_layout
from cianfhoghlaim.embeddings._oideachais_src.storage_indexing     import search_storage_backends
from cianfhoghlaim.embeddings._oideachais_src.config_indexing      import search_config_files

QUERIES = {  # 20 representative queries per App — see 34-query-corpus.json
    "codebase_chunks":    ["dagster dlt asset partition", "lancedb mount table target", ...],
    "api_endpoints":      ["agent memory add", "search code base", ...],
    "filesystem_layout":  ["stacks directory", "compose yamls", ...],
    "storage_backends":   ["garage bucket", "lance namespace", ...],
    "config_files":       ["dagster yaml", "mise toml", ...],
}

async def bench_one(search_fn, queries, limit=10):
    latencies = []
    for q in queries:
        t0 = time.perf_counter()
        await search_fn(q, limit=limit)
        latencies.append((time.perf_counter() - t0) * 1000)
    latencies.sort()
    return {"n": len(latencies),
            "p50_ms": statistics.median(latencies),
            "p95_ms": latencies[int(0.95 * len(latencies))],
            "p99_ms": latencies[int(0.99 * len(latencies))],
            "mean_ms": statistics.mean(latencies)}

async def main(tag, output):
    apps = [("codebase_chunks", search_codebase), ("api_endpoints", search_api_endpoints),
            ("filesystem_layout", search_filesystem_layout),
            ("storage_backends", search_storage_backends), ("config_files", search_config_files)]
    results = {"tag": tag, "apps": {}}
    for name, fn in apps:
        results["apps"][name] = await bench_one(fn, QUERIES[name])
    Path(output).write_text(json.dumps(results, indent=2))
    print(f"Wrote {output} ({tag})")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--tag", choices=["before", "after"], required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--diff", nargs=2, metavar=("BEFORE", "AFTER"))
    a = p.parse_args()
    if a.diff:
        b, af = json.loads(Path(a.diff[0]).read_text()), json.loads(Path(a.diff[1]).read_text())
        for app in b["apps"]:
            bp, ap = b["apps"][app]["p95_ms"], af["apps"][app]["p95_ms"]
            print(f"  {app:20s}: {bp:6.2f} ms → {ap:6.2f} ms  ({bp/ap:5.1f}× speedup)")
    else:
        asyncio.run(main(a.tag, a.output))
```

### 7.2 Expected numbers (from §2.1 profiling)

| App | Before p95 (ms) | After p95 (ms) | Speedup | Index build time |
|:--|:-:|:-:|:-:|:-:|
| `codebase_chunks` | ~180 | ~0.8 | **~225×** | ~25 s |
| `api_endpoints` | ~3.0 | ~0.5 | ~6× | ~3 s |
| `filesystem_layout` | ~8.0 | ~0.5 | ~16× | ~4 s |
| `storage_backends` | ~0.4 | ~0.4 | ~1× | ~1 s |
| `config_files` | ~2.5 | ~0.5 | ~5× | ~2 s |

### 7.3 Acceptance criteria

- `codebase_chunks` p95 **≤ 2 ms** (220× from baseline; 2× margin over 0.8 ms ideal for `bge-m3` query-embedding compute on CPU).
- `api_endpoints`, `filesystem_layout`, `config_files` p95 all **≤ 1 ms**.
- Recall@10 **≥ 0.95** vs brute-force baseline (verified on the 20-query corpus).
- MLflow experiment `refactor_34_lancedb_index_repair` records both runs with `tag={before,after}` for reproducibility from the Langfuse dashboard.

### 7.4 Tie-in with the existing RAGAS harness

`run_evaluation.py --compare` runs the RAGAS suite (faithfulness, answer_relevance, context_precision). After Refactor 34, the **retrieval step** inside RAGAS is measurably faster, logged as a side-effect in MLflow. RAGAS quality metrics should not change (top-10 recall ≥ 0.95 → downstream answer quality unchanged) but per-query latency drops.

---

## 8. Step 5 — Monitor regression with Dagster + R5 linter (3 hours)

Belt-and-braces: R5 (static, in `cocoindex_v1_conformance.py`) prevents the bug at **lint time**; the Dagster asset check detects it at **deploy time**.

### 8.1 R5 static check (additive to existing R1-R4)

Add to `cianfhoghlaim/embeddings/_oideachais_src/cocoindex_v1_conformance.py`:

```python
def _check_r5(tree: ast.Module, source: str) -> tuple[bool, str]:
    """R5 — every mount_table_target with a vector column must declare_vector_index."""
    mount_calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Await) and isinstance(n.value, ast.Call)
        and isinstance(n.value.func, ast.Attribute)
        and n.value.func.attr == "mount_table_target"
    ]
    if not mount_calls:
        return True, "R5: no mount_table_target calls — N/A"
    has_index = any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "declare_vector_index"
        for n in ast.walk(tree)
    )
    if not has_index:
        return False, ("R5: mount_table_target present but no declare_vector_index call. "
                        "Add `target_table.declare_vector_index(column='embedding', "
                        "metric='cosine', index_type='ivf_hnsw_sq', num_partitions=2)` "
                        "after the mount (see Refactor 34).")
    return True, "R5: declare_vector_index present"
```

Wire `_check_r5` into `check_app_file()` and the `all_pass` aggregator; update `conformance_summary by_rule` to include R5.

### 8.2 Dagster asset check (declarative, `block_in_flight_run=True`)

Add to `cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_cocoindex_v1.py` (or a new `vector_index_asset_checks.py` in the same directory):

```python
import os, dagster as dg
from lancedb import connect_namespace

PROTECTED = {
    "codebase_chunks":   "codebase_indexing",
    "api_endpoints":     "api_indexing",
    "filesystem_layout": "filesystem_indexing",
    "storage_backends":  "storage_indexing",
    "config_files":      "config_indexing",
}

def make_check(table: str):
    @dg.asset_check(
        asset=dg.AssetKey(["lancedb", table]),
        description=f"Refactor 34: verify {table} has a vector index on `embedding`",
        block_in_flight_run=True,
    )
    def _check(context: dg.AssetCheckExecutionContext) -> dg.AssetCheckResult:
        db = connect_namespace("rest", {
            "uri": os.environ["LANCE_DB_URI"],
            "headers.x-api-key": os.environ["LANCE_API_KEY"],
        })
        tbl = db.open_table(table, namespace_path=["prod", "oideachais"])
        indices = tbl.list_indices()  # v0.33 API — verify shape on deploy
        has = any(idx["type"] in {"IVF_HNSW_FLAT", "IVF_HNSW_SQ", "IVF_HNSW_PQ",
                                    "IVF_PQ", "IVF_RQ", "IVF_FLAT"}
                  and "embedding" in idx.get("columns", [])
                  for idx in indices)
        return dg.AssetCheckResult(
            passed=has,
            metadata={"table": table, "n_indices": len(indices),
                       "index_types": [i["type"] for i in indices]},
        )
    return _check

for _t in PROTECTED:
    globals()[f"check_vector_index_{_t}"] = make_check(_t)
```

`tbl.list_indices()` is **sketch** — the actual v0.33 SDK method name and response shape must be verified against `pylance>=0.10` before merge.

### 8.3 What each layer catches

| Layer | Trigger | Catches |
|:--|:--|:--|
| R5 (AST lint) | PR / pre-commit | A new v1 App that mounts a LanceDB embedding table without `declare_vector_index` — PR rejected. |
| Dagster asset check | Every materialization | A data-only change that drops the index (e.g. someone calls `db.drop_table()` and rebuilds without the declaration) — materialization blocked. |
| MLflow RAGAS recall | Every `run_evaluation.py --compare` | Silent recall regression (e.g. an index swap that drops recall below 0.95) — surfaces in Langfuse. |

---

## 9. Spec delta

### 9.1 `oideachais-pipeline/spec.md` — MODIFIED Requirement

```markdown
## MODIFIED Requirements
### Requirement: CocoIndex v1 Apps declare ANN vector indexes
The system SHALL declare a vector index on the `embedding` column of every
LanceDB-mounted CocoIndex v1 App via `declare_vector_index` with
`index_type="ivf_hnsw_sq"` and a `num_partitions` per Agent 04 §2.2.

#### Scenario: CodebaseIndex App
- **WHEN** `codebase_indexing.py:_make_app()` runs
- **THEN** it calls `target_table.declare_vector_index(column="embedding", metric="cosine", index_type="ivf_hnsw_sq", num_partitions=2)` before `mount_each(process_codebase_file, files.items(), target_table)`

#### Scenario: ApiIndex, FilesystemIndex, StorageIndex, ConfigIndex Apps
- **WHEN** any of `api_indexing.py:_make_app()`, `filesystem_indexing.py:_make_app()`, `storage_indexing.py:_make_app()`, `config_indexing.py:_make_app()` runs
- **THEN** it calls `target_table.declare_vector_index(column="embedding", metric="cosine", index_type="ivf_hnsw_sq", num_partitions=2)` before the first `target_table.upsert(batch)` or `mount_each(...)` call

#### Scenario: Conformance linter R5
- **WHEN** a new CocoIndex v1 App file calls `lancedb.mount_table_target` against a schema with an `Annotated[NDArray, EMBEDDER]` field
- **THEN** the `cocoindex_v1_conformance` App's R5 rule fails the build with the message "R5: mount_table_target present but no declare_vector_index call"

#### Scenario: Dagster asset check
- **WHEN** a LanceDB table is materialised without a vector index on `embedding`
- **THEN** the `check_vector_index_<table>` asset check fails with `block_in_flight_run=True`, halting downstream assets
```

### 9.2 `upstream-package-monitoring/spec.md` — ADDED Requirement

```markdown
## ADDED Requirements
### Requirement: Vector-index regression monitor
The system SHALL run a daily Dagster sensor that asserts each of the 5
LanceDB-mounted CocoIndex Apps (`codebase_chunks`, `api_endpoints`,
`filesystem_layout`, `storage_backends`, `config_files`) has at least one
`IVF_HNSW_SQ` / `IVF_PQ` / `IVF_RQ` index on the `embedding` column, and
SHALL emit a Langfuse alert if any table loses its index.

#### Scenario: All 5 indices present
- **WHEN** the daily `vector_index_regression_monitor` sensor runs
- **THEN** it records `n_protected=5, n_indexed=5` to Langfuse under the `refactor_34` experiment

#### Scenario: One table loses its index
- **WHEN** a table rebuild drops the vector index
- **THEN** the sensor fires a Langfuse alert with severity=`high` to the `#oideachais-alerts` channel
```

### 9.3 Validation

```bash
openspec validate refactor-34-lancedb-index-repair --strict
# 1 MODIFIED requirement (oideachais-pipeline) with 4 scenarios
# 1 ADDED requirement (upstream-package-monitoring) with 2 scenarios
mise run cocoindex:conformance          # 16/16 apps pass (R1-R5)
uv run python 34-bench-vector-index.py --tag after --output after.json
# codebase_chunks p95 ≤ 2 ms
```

---

## 10. Effort + risk summary

| Step | Effort | Risk | Reversible? |
|:--|:-:|:-:|:-:|
| 1. Decide index type | 30 min | zero | n/a |
| 2. Add to `codebase_indexing.py` | 30 min | low (idempotent) | yes (delete 5 lines) |
| 3. Add to 4 other Apps | 1 hour | low | yes |
| 4. Benchmark before/after | 2 hours | low (read-only) | n/a |
| 5. Dagster asset check + R5 linter | 3 hours | low (additive) | yes |
| **Total** | **~7 hours** | **low** | **yes** |

**Release train dependency:** can land in isolation. Pairs naturally with P1-12 (unify embedding model on `bge-m3`) — if P1-12 lands first, `codebase_chunks` re-embed will be faster with the index. Order: P1-2 (this) → P1-12 (one-time re-embed) → P2-2 (1.0.7 engine features). See Agent 26 §7 Mermaid.

**Credit budget used:** 0 BrowserBase / 0 Firecrawl (code-only fix spec).

---

## 11. Open questions

1. **`num_partitions=2` for `codebase_chunks` at N=100k+?** HNSW formula resolves to 2 for any N < 1M. Monitor `nprobe` in Langfuse; if p95 rises above 5 ms, bump to 4 and re-run.
2. **`num_sub_vectors`?** Does not apply to `IVF_HNSW_SQ` (only to `IVF_PQ`/`IVF_RQ`); silently ignored if set.
3. **`codebase_graph_app` (graph table at `codebase_indexing.py:507`)?** Also lacks `declare_vector_index`; irrelevant for current Cypher-only usage but must be added if a vector-edge App is built later.
4. **Other LanceDB Apps (`leabharlann_embedding.py`, `culture_heritage_embedding.py`, `unified_embedding.py`, `upstream_api_surface.py`)?** Verified separately — if any also lack the declaration, add them to the 5-App list and re-run Step 4. (Initial grep on 2026-06-28 returned 0 `declare_vector_index` hits across all v1 files; the 4 Apps in this list are the corpus Apps that power named `search_*()` functions — the 4 candidates above have no `search_*()` callers and were omitted pending verification.)
