# Lance-Ray Distributed Indexing

`lance-ray` is the distributed companion to LanceDB. It uses Ray
actors to parallelise index builds, re-embeddings, and bulk inserts
across a cluster (or a single multi-core machine).

## Use case

You have a Lance table with > 1M rows and need to:
- Re-embed with a new model
- Build a new HNSW index
- Run a one-time batch transformation (e.g. translation, OCR)

`lance-ray` parallelises the work across N workers.

## Install

```bash
pip install lance-ray ray
```

## Re-embed with a new model (distributed)

```python
import lance
import lance_ray as lr
from sentence_transformers import SentenceTransformer

# Read the existing table
ds = lance.dataset("s3://lance/leabharlann_books")

# Read all rows
rows = ds.to_pandas()  # or ds.to_batches() for memory-efficient streaming

# Define the transform (runs on each Ray worker)
def reembed(row):
    model = SentenceTransformer("BAAI/bge-m3")
    new_vec = model.encode(row["text"])
    return {**row, "text_embedding_v2": new_vec.tolist()}

# Run distributed
result = lr.map_batches(
    reembed,
    data=rows,
    batch_size=1000,
    num_workers=8,  # Ray actors
    compute="actors",
)

# Write back to a new table
new_table = lance.write_dataset(
    result,
    "s3://lance/leabharlann_books_v2",
    schema=...,
    mode="overwrite",
)
```

## Distributed index build

```python
import lance_ray as lr

# Create an HNSW index in parallel
lr.create_hnsw_index(
    "s3://lance/leabharlann_books",
    vector_column="text_embedding",
    index_type="HNSW",
    m=20,
    ef_construction=150,
    num_workers=8,
)
```

## Distributed scalar index

```python
lr.create_scalar_index(
    "s3://lance/leabharlann_books",
    column="subject",
    index_type="BTREE",
    num_workers=4,
)
```

## When to use lance-ray

- **> 1M rows** and a one-time transformation (re-embed, re-index)
- **Multi-machine cluster** (KCG uses `bunchloch` M4 Mac for
  in-house, `arm1-oci` ARM for cluster)
- **ML inference workloads** (embedding, OCR, translation) where
  the bottleneck is GPU/CPU, not I/O

## When NOT to use lance-ray

- **< 100K rows** — the Ray actor startup overhead dominates
- **Real-time search** — use `lancedb` Python API directly
- **Single-machine CPU-bound work** — use `concurrent.futures` or
  `asyncio` instead

## KCG integration

The KCG stack runs Ray on the `bunchloch` M4 Mac (local) for
leabharlann re-indexing. The Dagster asset
`orchestration/defs/leabharlann_assets.py` includes a
`leabharlann_reindex` asset that uses `lance-ray` under the hood.

## Reference

- The `lance-ray` docs: <https://github.com/lancedb/lance-ray>
- The 1,000+ line `lancedb-reference.md` section on `lance-ray`
  (lines 1160-1546) was in `docs/lance/lancedb-reference.md`
  (deleted with the docs subdirectory).
