# P1B-06 — LanceDB + Lance Blob + Lance Namespace (Phase 1B, Vector + Graph + Storage)

**Date:** 2026-06-28
**Phase:** 1B (Vector + Graph + Storage Tier)
**Budget:** ~180 credits
**Subagent:** research

## TL;DR

LanceDB is the **columnar vector database** that powers every Cianfhoghlaim embedding search (codebase_chunks, leabharlann_books, leabharlann_zotero, leabharlann_takeout). Lance Blob is the **large object storage** for PDFs/audio/video alongside vectors. Lance Namespace is the **REST Catalog** that bridges LanceDB to the lakehouse (Iceberg) + Garage S3.

The canonical Cianfhoghlaim pattern uses LanceDB 0.10+ with the v2 `.lance` format, mounted via `LanceNamespace` for cross-tool compatibility.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/lakehouse/lance-namespace/` | Lance REST Catalog service (port 8182) |
| `cognify/rules/lance_tables.py` | Lists 8 Lance tables maintained |
| `cianfhoghlaim/core/cocoindex/mount_lance.py` | CocoIndex v1 → Lance mount helper |
| `oideachais/notebooks/lancedb_search.py` | Vector search demo (codebase + leabharlann) |

**Canonical Lance Namespace config** (`stacks/lakehouse/lance-namespace/config.yaml`):

```yaml
namespace:
  name: lance
  type: lance
  storage:
    type: s3
    endpoint: http://lakehouse-garage:3900
    access_key: ${GARAGE_ACCESS_KEY}
    secret_key: ${GARAGE_SECRET_KEY}
    region: garage
    bucket: lance-bucket
tables:
  - name: codebase_chunks
    schema:
      - file_path: string
      - chunk_id: int
      - text: string
      - vector: fixed_size_list<float32>[1024]
    index:
      type: ivf_pq
      metric: cosine
      num_partitions: 256
      num_sub_vectors: 64
  - name: leabharlann_books
    schema:
      - book_id: string
      - chunk_id: int
      - text: string
      - vector: fixed_size_list<float32>[1024]
    index: { type: hnsw, metric: cosine, m: 16, ef_construction: 200 }
```

**Python client** (`cianfhoghlaim/core/cocoindex/mount_lance.py`):

```python
import lancedb

db = lancedb.connect("http://lakehouse-lance:8182")  # via REST Catalog
table = db.open_table("codebase_chunks")
results = table.search([0.1, 0.2, ...]).limit(10).to_pandas()
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `LANCE_DB_URI` | `http://lakehouse-lance:8182` | Locket |
| `GARAGE_ACCESS_KEY` | `infisical://dev-baile/garage/access_key` | Locket |
| `GARAGE_SECRET_KEY` | `infisical://dev-baile/garage/secret_key` | Locket |
| `LANCE_BUCKET` | `lance-bucket` | compose env |

## CCC anchors

`stacks/lakehouse/lance-namespace/` · `cognify/rules/lance_tables.py` · `cianfhoghlaim/core/cocoindex/mount_lance.py`

Search terms: `"LanceNamespace"`, `"ivf_pq"`, `"fixed_size_list<float32>"`, `"HNSW"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-12 | Initial LanceDB 0.5 deploy (local only) |
| 2026-02 | Migrated to `.lance` v2 format (5x smaller files) |
| 2026-03 | Added Lance Namespace (REST Catalog) |
| 2026-04 | Added HNSW index (in addition to IVF_PQ) |
| 2026-05 | Wired to CocoIndex v1 mount_table_target |

## Anti-patterns

1. Don't store vectors outside LanceDB — it's optimized for columnar access
2. Don't use HNSW for <1M vectors — IVF_PQ is faster + smaller
3. Don't use float64 — float32 is sufficient for most embeddings
4. Don't bypass Lance Namespace for direct S3 access — namespace provides schema validation
5. Don't store raw embeddings in Postgres — use LanceDB's columnar storage

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Format | Lance v2 (.lance) | 5x smaller + faster than parquet |
| Index | HNSW (small tables) + IVF_PQ (large) | Per-table tuning |
| Metric | Cosine (for normalized embeddings) | Industry standard |
| Bridge | Lance Namespace (REST Catalog) | Cross-tool (CocoIndex + MotherDuck + marimo) |
| Storage | Garage S3 via Lance Blob | Same as Iceberg |
| Version | LanceDB 0.10+ | Stable v2 format |

## Files to read next

`stacks/lakehouse/lance-namespace/` · `cognify/rules/lance_tables.py` · `cianfhoghlaim/core/cocoindex/mount_lance.py` · `.agents/skills/lancedb/SKILL.md`
