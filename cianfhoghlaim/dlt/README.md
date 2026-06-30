# Dlt_utils

Utilities for dlt data loading

## Canonical Embedding Batcher

The canonical `EmbeddingBatcher` lives in `oideachais.dlt_utils.batching`
and is re-exported via `oideachais.dlt_utils.__init__.EmbeddingBatcher`.

The legacy `sruth/oideachais/embeddings/` package has been **removed**
(see `openspec/changes/consolidate-embedding-batcher/`). Do not
re-introduce it. Import the canonical batcher from `dlt_utils` instead:

```python
from oideachais.dlt_utils import (
    EmbeddingBatcher,
    batch_embeddings,
    batch_items,
    should_drop_hnsw,
    calculate_optimal_batch_size,
    MINIMUM_BATCH_SIZE,
    HNSW_DROP_THRESHOLD,
)
```

The `sruth/oideachais/modal_finetune/embed_batch.py` Modal GPU worker is
**not** a duplicate — it is a serverless GPU `@app.cls` worker that
runs on Modal infrastructure, not a local Python utility. The class
name `EmbeddingService` is shared but the layer is different.

## 2026-06 stack alignment

The 2026-06 package updates added new helpers to `dlt_utils`; see
`openspec/changes/refactor-dlt-dagster-2026-stack-align/`.

### dlt 1.0 safety helpers (`sruth/oideachais/dlt_utils/safety.py`)

- `safe_dlt_run(pipeline, data)` — the canonical serial-executor
  wrapper (no change).
- `safe_dlt_run_with_progress(pipeline, data)` — same but with
  structured per-package progress logging (new 2026-06).
- `validate_source_kwargs(source)` — pre-flight validation
  catching the 4 common dlt 1.0 mistakes (new 2026-06):
  - `missing_name`
  - `incremental_no_primary_key`
  - `missing_write_disposition`
  - `merge_without_primary_key`

```python
from oideachais.dlt_utils import (
    safe_dlt_run_with_progress,
    validate_source_kwargs,
)

# Pre-flight check (raises if any dlt 1.0 mistake is found).
mistakes = validate_source_kwargs(my_source())
if mistakes:
    raise ValueError(f"DLT 1.0 source has mistakes: {mistakes}")

# Run with progress logging.
load_info = safe_dlt_run_with_progress(pipeline, my_source())
```

### DuckLake 1.0 SQL helpers (`sruth/oideachais/dlt_utils/ducklake_options.py`)

The 2026-04-13 DuckLake 1.0 launch introduced 3 new features:

- `set_data_inlining_row_limit(table, limit=100)` — the 1.0
  default. Small inserts go to the catalog database instead of
  creating separate Parquet files.
- `set_sorted_by(table, columns=("id",))` — enables sort-based
  clustering (10x speedup when sort columns align with filter
  columns).
- `set_bucket_partition(table, num_buckets=1000, key="id")` —
  enables bucket partitioning for high-cardinality keys.
- `apply_ducklake_1_0_optimisations(table, ...)` — applies the
  3 features in the canonical order.

The `post_create_ducklake_1_0(dataset_name, table)` helper in
`destinations.py` is the canonical post-create hook.

### MotherDuck hosting options (`sruth/oideachais/dlt_utils/motherduck_options.py`)

The 2026-04-13 MotherDuck launch introduced 3 hosting options:

- `fully_managed_destination()` — MotherDuck catalog + storage
  + compute.
- `byob_destination()` — MotherDuck catalog + self-hosted S3
  (Garage) + MotherDuck compute. **The KCG default.**
- `byoc_destination()` — MotherDuck catalog + self-hosted S3
  + self-hosted compute (Trino / Spark / DataFusion).
- `get_motherduck_destination()` — routes on the
  `MOTHERDUCK_MODE` env var (default `byob`).

### DuckDB + DuckLake schema type helpers (`sruth/oideachais/dlt_utils/schema.py`)

The 2026-04-13 DuckDB core updates added 2 new types:

- `GEOMETRY` / `geometry_column()` — geospatial data with
  predicate-pushdown support.
- `VARIANT` / `variant_column()` — binary JSON type with
  automatic shredding for fast filtering.


## Cross-References

This module integrates with other components of the Oideachais platform:
- See the main [Agent Architecture](../../AGENTS.md) for global orchestration rules.
- View the [Skills Library](../../.skills/) for agent capability instructions.
- Relevant modules: [visualization](../visualization/README.md), [clients](../clients/README.md), [ui](../ui/README.md)
