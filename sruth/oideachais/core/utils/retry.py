"""
Retry utilities with exponential backoff.

Provides decorators and utilities for retrying failed operations
with configurable backoff strategies.
"""

from __future__ import annotations

import asyncio
import functools
import logging
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Sequence, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryableError(Exception):
    """Base class for errors that should trigger retry."""
    pass


class RateLimitError(RetryableError):
    """Raised when rate limited by an API."""

    def __init__(self, message: str = "", retry_after: float | None = None):
        self.retry_after = retry_after
        super().__init__(message)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: float = 0.1
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,)


def calculate_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: float = 0.1,
) -> float:
    """
    Calculate delay with exponential backoff and jitter.

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Random jitter factor (0-1)

    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (exponential_base ** attempt), max_delay)

    # Add random jitter to prevent thundering herd
    if jitter > 0:
        jitter_amount = delay * jitter * random.random()
        delay = delay + jitter_amount

    return delay


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: float = 0.1,
    retryable_exceptions: Sequence[type[Exception]] = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator for retrying functions with exponential backoff.

    Usage:
        @retry_with_backoff(max_attempts=3, base_delay=1.0)
        def fetch_data():
            response = requests.get(url)
            response.raise_for_status()
            return response.json()

    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        jitter: Random jitter factor (0-1)
        retryable_exceptions: Exception types to retry
        on_retry: Callback called before each retry (attempt, exception)

    Returns:
        Decorated function
    """
    retryable = tuple(retryable_exceptions)

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except retryable as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        logger.error(
                            f"{fn.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    # Check for rate limit with explicit retry-after
                    if isinstance(e, RateLimitError) and e.retry_after:
                        delay = e.retry_after
                    else:
                        delay = calculate_backoff(
                            attempt, base_delay, max_delay,
                            exponential_base, jitter
                        )

                    logger.warning(
                        f"{fn.__name__} attempt {attempt + 1}/{max_attempts} "
                        f"failed: {e}. Retrying in {delay:.2f}s"
                    )

                    if on_retry:
                        on_retry(attempt, e)

                    time.sleep(delay)

            # Should never reach here, but satisfy type checker
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry loop exit")

        return wrapper

    return decorator


def retry_with_backoff_async(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: float = 0.1,
    retryable_exceptions: Sequence[type[Exception]] = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Async version of retry_with_backoff decorator.

    Usage:
        @retry_with_backoff_async(max_attempts=3)
        async def fetch_data():
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
    """
    retryable = tuple(retryable_exceptions)

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_attempts):
                try:
                    return await fn(*args, **kwargs)
                except retryable as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        logger.error(
                            f"{fn.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    if isinstance(e, RateLimitError) and e.retry_after:
                        delay = e.retry_after
                    else:
                        delay = calculate_backoff(
                            attempt, base_delay, max_delay,
                            exponential_base, jitter
                        )

                    logger.warning(
                        f"{fn.__name__} attempt {attempt + 1}/{max_attempts} "
                        f"failed: {e}. Retrying in {delay:.2f}s"
                    )

                    if on_retry:
                        on_retry(attempt, e)

                    await asyncio.sleep(delay)

            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry loop exit")

        return wrapper

    return decorator


class Retryer:
    """
    Class-based retryer for more control over retry behavior.

    Usage:
        retryer = Retryer(max_attempts=3)
        result = retryer.run(fetch_data, url=url)
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: float = 0.1,
        retryable_exceptions: Sequence[type[Exception]] = (Exception,),
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = tuple(retryable_exceptions)

        self.attempt_count = 0
        self.last_exception: Exception | None = None

    def run(self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Run a function with retry."""
        self.attempt_count = 0
        self.last_exception = None

        for attempt in range(self.max_attempts):
            self.attempt_count = attempt + 1

            try:
                return fn(*args, **kwargs)
            except self.retryable_exceptions as e:
                self.last_exception = e

                if attempt == self.max_attempts - 1:
                    raise

                delay = calculate_backoff(
                    attempt,
                    self.base_delay,
                    self.max_delay,
                    self.exponential_base,
                    self.jitter,
                )

                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_attempts} failed: {e}. "
                    f"Retrying in {delay:.2f}s"
                )

                time.sleep(delay)

        if self.last_exception:
            raise self.last_exception
        raise RuntimeError("Unexpected retry loop exit")

    async def run_async(
        self, fn: Callable[..., T], *args: Any, **kwargs: Any
    ) -> T:
        """Async version of run."""
        self.attempt_count = 0
        self.last_exception = None

        for attempt in range(self.max_attempts):
            self.attempt_count = attempt + 1

            try:
                return await fn(*args, **kwargs)
            except self.retryable_exceptions as e:
                self.last_exception = e

                if attempt == self.max_attempts - 1:
                    raise

                delay = calculate_backoff(
                    attempt,
                    self.base_delay,
                    self.max_delay,
                    self.exponential_base,
                    self.jitter,
                )

                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_attempts} failed: {e}. "
                    f"Retrying in {delay:.2f}s"
                )

                await asyncio.sleep(delay)

        if self.last_exception:
            raise self.last_exception
        raise RuntimeError("Unexpected retry loop exit")
