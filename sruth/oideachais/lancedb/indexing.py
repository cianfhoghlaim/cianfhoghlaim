"""
LanceDB 0.15+ vector + scalar index helpers.

The 3 functions in this module wrap the canonical 2026-06 LanceDB
patterns so the leabharlann full-stack demo (and any other v1
CocoIndex App) can call them in 1 line.

Reference:
- `lancedb.com/blog/how-lancedb-accelerates-vector-search-at-10-billion-scale`
  (the HNSW defaults `ef_construction=100, M=16`).
- `docs.lancedb.com/indexing` (the IVF-PQ pattern).
- `docs.lancedb.com/indexing/vector-index` (the multi-index
  pattern that supports HNSW + IVF + binary quantised indexes
  on the same table).
"""
from __future__ import annotations

from typing import Any

# LanceDB is optional — degrade gracefully if not installed.
try:
    import lancedb  # type: ignore[import-not-found]

    LANCEDB_AVAILABLE = True
except ImportError as e:  # pragma: no cover
    lancedb = None  # type: ignore[assignment]
    LANCEDB_AVAILABLE = False
    import logging

    logging.getLogger(__name__).warning("lancedb_not_available: %s", e)


# The default HNSW parameters per the LanceDB 10B-scale blog.
DEFAULT_HNSW_EF_CONSTRUCTION: int = 100
DEFAULT_HNSW_M: int = 16

# The default IVF-PQ parameters per the LanceDB docs.
DEFAULT_IVF_NUM_PARTITIONS: int = 256
DEFAULT_IVF_NUM_SUB_VECTORS: int = 32


def build_hnsw_index(
    table: Any,
    column: str = "embedding",
    *,
    ef_construction: int = DEFAULT_HNSW_EF_CONSTRUCTION,
    M: int = DEFAULT_HNSW_M,
    replace: bool = True,
) -> None:
    """Build an HNSW index on a LanceDB table.

    Per the LanceDB 10B-scale blog, the recommended defaults are
    `ef_construction=100, M=16` (10-100x speedup at ~10% recall
    loss). For higher recall, increase `ef_construction` to
    200-400; for higher speed, decrease to 50.

    Args:
        table: A LanceDB `Table` object.
        column: The vector column name. Default "embedding".
        ef_construction: HNSW `ef_construction` parameter. Default 100.
        M: HNSW `M` parameter (max edges per node). Default 16.
        replace: If True, replace any existing index on the same
                 column. Default True.

    Example:
        >>> from oideachais.lancedb.indexing import build_hnsw_index
        >>> table = db.open_table("leabharlann_books")
        >>> build_hnsw_index(table, column="embedding")
    """
    if not LANCEDB_AVAILABLE:
        return
    table.create_index(
        metric="L2",
        num_partitions=256,  # HNSW uses IVF-PQ params for partitioning
        num_sub_vectors=96,
        vector_column_name=column,
        index_type="HNSW",
        hnsw_params={
            "ef_construction": ef_construction,
            "M": M,
        },
        replace=replace,
    )


def build_ivf_pq_index(
    table: Any,
    column: str = "embedding",
    *,
    num_partitions: int = DEFAULT_IVF_NUM_PARTITIONS,
    num_sub_vectors: int = DEFAULT_IVF_NUM_SUB_VECTORS,
    replace: bool = True,
) -> None:
    """Build an IVF-PQ index on a LanceDB table.

    The low-memory mobile pattern (per `docs.lancedb.com/indexing`).
    IVF-PQ gives the best recall-per-byte tradeoff for low-memory
    devices (iPhone, Apple Watch).

    Args:
        table: A LanceDB `Table` object.
        column: The vector column name. Default "embedding".
        num_partitions: The number of IVF partitions. Default 256.
        num_sub_vectors: The number of PQ sub-vectors. Default 32.
        replace: If True, replace any existing index on the same
                 column. Default True.

    Example:
        >>> from oideachais.lancedb.indexing import build_ivf_pq_index
        >>> table = db.open_table("leabharlann_books")
        >>> build_ivf_pq_index(table, column="embedding")
    """
    if not LANCEDB_AVAILABLE:
        return
    table.create_index(
        metric="L2",
        num_partitions=num_partitions,
        num_sub_vectors=num_sub_vectors,
        vector_column_name=column,
        index_type="IVF_PQ",
        replace=replace,
    )


def build_scalar_index(
    table: Any,
    column: str,
    *,
    replace: bool = True,
) -> None:
    """Build a scalar (B-tree) index on a non-vector column.

    Use for metadata columns that are frequently used in
    `where` clauses (e.g. `subject`, `htr_relevant`, `account`).

    Args:
        table: A LanceDB `Table` object.
        column: The scalar column name.
        replace: If True, replace any existing index on the same
                 column. Default True.

    Example:
        >>> from oideachais.lancedb.indexing import build_scalar_index
        >>> table = db.open_table("leabharlann_books")
        >>> build_scalar_index(table, "subject")
    """
    if not LANCEDB_AVAILABLE:
        return
    table.create_index(
        vector_column_name=None,
        scalar_column_name=column,
        index_type="BTREE",
        replace=replace,
    )


def optimize_index(table: Any) -> None:
    """Run the LanceDB 0.15 index optimisation pass.

    Per the LanceDB lifecycle, every index must be optimised after
    bulk inserts. The optimisation pass:
    - Compacts the index segments (reduces index size by 2-5x).
    - Retrains the IVF centroids.
    - Trims orphaned index entries.

    Args:
        table: A LanceDB `Table` object.

    Example:
        >>> from oideachais.lancedb.indexing import (
        ...     build_hnsw_index, optimize_index,
        ... )
        >>> table = db.open_table("leabharlann_books")
        >>> build_hnsw_index(table, column="embedding")
        >>> # ... insert 10k rows ...
        >>> optimize_index(table)
    """
    if not LANCEDB_AVAILABLE:
        return
    table.optimize()


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
