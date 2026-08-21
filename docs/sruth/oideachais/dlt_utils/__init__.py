"""
DLT (Data Load Tool) utilities for oideachais pipeline.

Provides:
- Source mixins for common patterns (pagination, rate limiting, caching)
- DuckLake destination factory (local/production switching)
- SerialDatabaseExecutor integration for DuckDB safety
- Embedding batching utilities for 100x performance improvement
"""

# Source mixins
from .mixins import (
    PaginatedSourceMixin,
    RateLimitedSourceMixin,
    CachedSourceMixin,
    AuthenticatedSourceMixin,
    IncrementalSourceMixin,
)

# Destination factory
from .destinations import (
    get_dlt_destination,
    get_duckdb_fallback_destination,
    create_pipeline,
)

# Safety wrappers
from .safety import (
    safe_dlt_run,
    safe_dlt_normalize,
    safe_dlt_load,
    safe_dataset_query,
)

# Batching utilities
from .batching import (
    MINIMUM_BATCH_SIZE,
    HNSW_DROP_THRESHOLD,
    batch_embeddings,
    batch_items,
    EmbeddingBatcher,
    should_drop_hnsw,
    calculate_optimal_batch_size,
)

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
    # Safety
    "safe_dlt_run",
    "safe_dlt_normalize",
    "safe_dlt_load",
    "safe_dataset_query",
    # Batching
    "MINIMUM_BATCH_SIZE",
    "HNSW_DROP_THRESHOLD",
    "batch_embeddings",
    "batch_items",
    "EmbeddingBatcher",
    "should_drop_hnsw",
    "calculate_optimal_batch_size",
]
