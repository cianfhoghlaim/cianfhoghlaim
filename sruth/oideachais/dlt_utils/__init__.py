"""
DLT (Data Load Tool) utilities for oideachais pipeline.

Provides:
- Source mixins for common patterns (pagination, rate limiting, caching)
- DuckLake destination factory (local/production switching)
- SerialDatabaseExecutor integration for DuckDB safety
- Embedding batching utilities for 100x performance improvement
"""

# Source mixins
# Batching utilities
from .batching import (
    HNSW_DROP_THRESHOLD,
    MINIMUM_BATCH_SIZE,
    EmbeddingBatcher,
    batch_embeddings,
    batch_items,
    calculate_optimal_batch_size,
    should_drop_hnsw,
)

# Destination factory
from .destinations import (
    create_pipeline,
    get_dlt_destination,
    get_duckdb_fallback_destination,
    post_create_ducklake_1_0,
)

# DuckLake 1.0 SQL helpers (the 2026-04-13 launch features)
from .ducklake_options import (
    BUCKET_PARTITIONED_TABLES,
    DEFAULT_DATA_INLINING_ROW_LIMIT,
    SORTED_BY_TABLES,
    apply_ducklake_1_0_optimisations,
    is_bucket_partitioned_table,
    is_sorted_by_table,
    set_bucket_partition,
    set_data_inlining_row_limit,
    set_sorted_by,
)

# MotherDuck managed / BYOB / BYOC hosting options
from .motherduck_options import (
    byob_destination,
    byoc_destination,
    fully_managed_destination,
    get_motherduck_destination,
)

# DuckDB + DuckLake schema type helpers (GEOMETRY + VARIANT)
from .schema import (
    GEOMETRY,
    VARIANT,
    geometry_column,
    variant_column,
)
from .mixins import (
    AuthenticatedSourceMixin,
    CachedSourceMixin,
    IncrementalSourceMixin,
    PaginatedSourceMixin,
    RateLimitedSourceMixin,
)

# Safety wrappers
from .safety import (
    DLT_1_0_MISTAKES,
    safe_dataset_query,
    safe_dlt_load,
    safe_dlt_normalize,
    safe_dlt_run,
    safe_dlt_run_with_progress,
    validate_source_kwargs,
)

# dlt+ project wrappers (added 2026-06-26, Phase 4)
from .dlthub_projects import apply_dlthub_wrappers

__all__ = [
    # Mixins
    "PaginatedSourceMixin",
    "RateLimitedSourceMixin",
    "CachedSourceMixin",
    "AuthenticatedSourceMixin",
    "IncrementalSourceMixin",
    # Destinations
    "get_dlt_destination",
    "get_duckdb_fallback_destination",
    "create_pipeline",
    "post_create_ducklake_1_0",
    # DuckLake 1.0 SQL helpers
    "SORTED_BY_TABLES",
    "BUCKET_PARTITIONED_TABLES",
    "DEFAULT_DATA_INLINING_ROW_LIMIT",
    "set_data_inlining_row_limit",
    "set_sorted_by",
    "set_bucket_partition",
    "apply_ducklake_1_0_optimisations",
    "is_sorted_by_table",
    "is_bucket_partitioned_table",
    # MotherDuck hosting options
    "fully_managed_destination",
    "byob_destination",
    "byoc_destination",
    "get_motherduck_destination",
    # DuckDB + DuckLake schema type helpers
    "GEOMETRY",
    "VARIANT",
    "geometry_column",
    "variant_column",
    # Safety
    "safe_dlt_run",
    "safe_dlt_run_with_progress",
    "safe_dlt_normalize",
    "safe_dlt_load",
    "safe_dataset_query",
    # dlt 1.0 alignment (added 2026-06)
    "validate_source_kwargs",
    "DLT_1_0_MISTAKES",
    # Batching
    "MINIMUM_BATCH_SIZE",
    "HNSW_DROP_THRESHOLD",
    "batch_embeddings",
    "batch_items",
    "EmbeddingBatcher",
    "should_drop_hnsw",
    "calculate_optimal_batch_size",
    # dlt+ project wrappers (added 2026-06-26, Phase 4)
    "apply_dlthub_wrappers",
] 
