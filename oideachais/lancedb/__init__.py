"""
oideachais.lancedb — canonical LanceDB helpers.

The 2026-06 package updates added 3 features to LanceDB 0.15+:

1. **HNSW index** — `LanceDB` ships an HNSW implementation
   optimised for 10B-scale workloads per
   `lancedb.com/blog/how-lancedb-accelerates-vector-search-at-10-billion-scale`.
   HNSW gives 10-100x speedup at the cost of ~10% recall loss.
2. **IVF-PQ index** — the low-memory mobile pattern
   (`docs.lancedb.com/indexing`).
3. **Scalar indexes** — `LanceDB` can build B-tree indexes on
   metadata columns (e.g. `subject`, `htr_relevant`).

This package wraps the 3 patterns in 3 simple functions so the
leabharlann full-stack demo (and any other v1 CocoIndex App) can
call them in 1 line.

Usage:
    from oideachais.lancedb.indexing import build_hnsw_index

    table = db.open_table("leabharlann_books")
    build_hnsw_index(table, column="embedding")
"""

from .indexing import (
    DEFAULT_HNSW_EF_CONSTRUCTION,
    DEFAULT_HNSW_M,
    DEFAULT_IVF_NUM_PARTITIONS,
    DEFAULT_IVF_NUM_SUB_VECTORS,
    LANCEDB_AVAILABLE,
    build_hnsw_index,
    build_ivf_pq_index,
    build_scalar_index,
    optimize_index,
)

__all__ = [
    "LANCEDB_AVAILABLE",
    "DEFAULT_HNSW_EF_CONSTRUCTION",
    "DEFAULT_HNSW_M",
    "DEFAULT_IVF_NUM_PARTITIONS",
    "DEFAULT_IVF_NUM_SUB_VECTORS",
    "build_hnsw_index",
    "build_ivf_pq_index",
    "build_scalar_index",
    "optimize_index",
]
