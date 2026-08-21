"""
Rate Limiter for API Request Control.

Provides token bucket and sliding window rate limiting to prevent
overwhelming external APIs and getting rate-limited/banned.
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RateLimiter:
    """
    Token bucket rate limiter for controlling request rates.

    Uses a token bucket algorithm with configurable capacity and refill rate.
    Supports both sync and async operations.

    Usage:
        limiter = RateLimiter(max_per_second=10)

        # Sync usage
        limiter.acquire()
        response = requests.get(url)

        # Async usage
        await limiter.acquire_async()
        response = await client.get(url)

    Args:
        max_per_second: Maximum requests per second
        burst_size: Maximum burst capacity (defaults to max_per_second)
    """
    max_per_second: float = 10.0
    burst_size: int | None = None

    _tokens: float = field(init=False)
    _last_refill: float = field(init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _async_lock: asyncio.Lock | None = field(default=None)

    def __post_init__(self) -> None:
        if self.burst_size is None:
            self.burst_size = int(self.max_per_second)
        self._tokens = float(self.burst_size)
        self._last_refill = time.time()
        self._lock = threading.Lock()
        self._async_lock = None

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_refill
        tokens_to_add = elapsed * self.max_per_second
        self._tokens = min(self.burst_size, self._tokens + tokens_to_add)
        self._last_refill = now

    def acquire(self, tokens: int = 1, block: bool = True) -> bool:
        """
        Acquire tokens from the bucket.

        Args:
            tokens: Number of tokens to acquire
            block: If True, wait until tokens available

        Returns:
            True if tokens acquired, False if not blocking and unavailable
        """
        with self._lock:
            while True:
                self._refill()

                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True

                if not block:
                    return False

                # Calculate wait time
                needed = tokens - self._tokens
                wait_time = needed / self.max_per_second

                # Release lock while waiting
                self._lock.release()
                try:
                    time.sleep(wait_time)
                finally:
                    self._lock.acquire()

    async def acquire_async(self, tokens: int = 1) -> None:
        """
        Async version of acquire that yields control while waiting.

        Args:
            tokens: Number of tokens to acquire
        """
        if self._async_lock is None:
            self._async_lock = asyncio.Lock()

        async with self._async_lock:
            while True:
                with self._lock:
                    self._refill()

                    if self._tokens >= tokens:
                        self._tokens -= tokens
                        return

                    needed = tokens - self._tokens
                    wait_time = needed / self.max_per_second

                await asyncio.sleep(wait_time)

    @property
    def available_tokens(self) -> float:
        """Current number of available tokens."""
        with self._lock:
            self._refill()
            return self._tokens


@dataclass
class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter for more precise rate limiting.

    Tracks actual request timestamps within a window for more
    accurate rate limiting than token bucket.

    Usage:
        limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=60)

        if limiter.can_proceed():
            limiter.record_request()
            response = requests.get(url)

    Args:
        max_requests: Maximum requests allowed in window
        window_seconds: Size of sliding window in seconds
    """
    max_requests: int = 100
    window_seconds: float = 60.0

    _timestamps: deque = field(default_factory=deque)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        self._timestamps = deque()
        self._lock = threading.Lock()

    def _cleanup_old(self) -> None:
        """Remove timestamps outside the window."""
        cutoff = time.time() - self.window_seconds
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()

    def can_proceed(self) -> bool:
        """Check if a request can proceed."""
        with self._lock:
            self._cleanup_old()
            return len(self._timestamps) < self.max_requests

    def record_request(self) -> None:
        """Record a request timestamp."""
        with self._lock:
            self._timestamps.append(time.time())

    def wait_time(self) -> float:
        """Calculate time to wait before next request can proceed."""
        with self._lock:
            self._cleanup_old()

            if len(self._timestamps) < self.max_requests:
                return 0.0

            # Wait until oldest request falls outside window
            oldest = self._timestamps[0]
            return oldest + self.window_seconds - time.time()

    def acquire(self, block: bool = True) -> bool:
        """
        Acquire permission to make a request.

        Args:
            block: If True, wait until request can proceed

        Returns:
            True if permission granted
        """
        while True:
            if self.can_proceed():
                self.record_request()
                return True

            if not block:
                return False

            wait = self.wait_time()
            if wait > 0:
                time.sleep(wait)

    async def acquire_async(self) -> None:
        """Async version of acquire."""
        while True:
            if self.can_proceed():
                self.record_request()
                return

            wait = self.wait_time()
            if wait > 0:
                await asyncio.sleep(wait)

    @property
    def current_count(self) -> int:
        """Current number of requests in window."""
        with self._lock:
            self._cleanup_old()
            return len(self._timestamps)
