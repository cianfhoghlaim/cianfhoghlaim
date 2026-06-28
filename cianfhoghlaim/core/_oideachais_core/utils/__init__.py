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
    RateLimitError,
    RetryableError,
    RetryConfig,
    Retryer,
    calculate_backoff,
    retry_with_backoff,
    retry_with_backoff_async,
)

__all__ = [
    # Circuit breaker
    "CircuitBreaker",
    "CircuitBreakerOpen",
    "RateLimitError",
    # Rate limiting
    "RateLimiter",
    "RetryConfig",
    "RetryableError",
    "Retryer",
    "SlidingWindowRateLimiter",
    "calculate_backoff",
    # Retry utilities
    "retry_with_backoff",
    "retry_with_backoff_async",
]
