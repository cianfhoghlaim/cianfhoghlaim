"""
Shared utilities for resilience and rate control.

Provides:
    - CircuitBreaker: Prevent cascading failures
    - RateLimiter: Control API request rates
    - retry_with_backoff: Exponential backoff retry decorator
"""

from .circuit_breaker import CircuitBreaker, CircuitBreakerOpen
from .rate_limiter import RateLimiter, SlidingWindowRateLimiter
from .retry import (
    retry_with_backoff,
    retry_with_backoff_async,
    RetryableError,
    RateLimitError,
    Retryer,
    RetryConfig,
    calculate_backoff,
)

__all__ = [
    # Circuit breaker
    "CircuitBreaker",
    "CircuitBreakerOpen",
    # Rate limiting
    "RateLimiter",
    "SlidingWindowRateLimiter",
    # Retry utilities
    "retry_with_backoff",
    "retry_with_backoff_async",
    "RetryableError",
    "RateLimitError",
    "Retryer",
    "RetryConfig",
    "calculate_backoff",
]
