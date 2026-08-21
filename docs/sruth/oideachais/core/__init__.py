"""
Core utilities for oideachais pipeline.

Contains storage utilities and will contain utils after consolidation.
"""

# Storage (local - authoritative)
from .storage import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
    DuckDBClient,
    LanceDBClient,
    HNSW_DROP_THRESHOLD,
)

# Utils (local - authoritative)
from .utils import (
    CircuitBreaker,
    CircuitBreakerOpen,
    RateLimiter,
    SlidingWindowRateLimiter,
    RetryableError,
    RateLimitError,
    retry_with_backoff,
    retry_with_backoff_async,
    Retryer,
)

__all__ = [
    # Storage
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
    "DuckDBClient",
    "LanceDBClient",
    "HNSW_DROP_THRESHOLD",
    # Utils
    "CircuitBreaker",
    "CircuitBreakerOpen",
    "RateLimiter",
    "SlidingWindowRateLimiter",
    "RetryableError",
    "RateLimitError",
    "retry_with_backoff",
    "retry_with_backoff_async",
    "Retryer",
]
