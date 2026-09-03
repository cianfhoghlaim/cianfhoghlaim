"""Circuit breaker pattern for A2A resilience.

Prevents cascading failures when downstream agents are unavailable.
After a threshold of failures, the circuit opens and fails fast,
then periodically attempts to close.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Failing fast, no requests sent
- HALF_OPEN: Testing if service recovered
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional, TypeVar

import structlog

logger = structlog.get_logger()

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpen(Exception):
    """Raised when circuit is open and request is rejected."""

    def __init__(self, name: str, retry_after: float):
        self.name = name
        self.retry_after = retry_after
        super().__init__(f"Circuit breaker '{name}' is open. Retry after {retry_after:.1f}s")


@dataclass
class CircuitBreaker:
    """Circuit breaker for protecting A2A calls.

    Usage:
        cb = CircuitBreaker("crypteolas")

        async def call_agent():
            async with cb:
                return await make_a2a_call()

        try:
            result = await call_agent()
        except CircuitBreakerOpen as e:
            # Handle fast failure
            return fallback_response()
    """

    name: str
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes in half-open to close
    timeout_seconds: float = 60.0  # Time before trying half-open
    half_open_max_calls: int = 3  # Max concurrent calls in half-open

    # Internal state
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _half_open_calls: int = field(default=0, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    @property
    def state(self) -> CircuitState:
        """Current circuit state."""
        return self._state

    @property
    def is_closed(self) -> bool:
        """True if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """True if circuit is open (failing fast)."""
        return self._state == CircuitState.OPEN

    @property
    def time_until_retry(self) -> float:
        """Seconds until circuit will attempt half-open."""
        if self._state != CircuitState.OPEN:
            return 0.0
        elapsed = time.time() - self._last_failure_time
        return max(0.0, self.timeout_seconds - elapsed)

    async def __aenter__(self):
        """Context manager entry - check if call allowed."""
        await self._before_call()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - record result."""
        if exc_type is None:
            await self._on_success()
        else:
            await self._on_failure(exc_val)
        # Don't suppress exceptions
        return False

    async def _before_call(self) -> None:
        """Check if call is allowed."""
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                return

            if self._state == CircuitState.OPEN:
                # Check if timeout elapsed
                if time.time() - self._last_failure_time >= self.timeout_seconds:
                    self._transition_to_half_open()
                else:
                    raise CircuitBreakerOpen(self.name, self.time_until_retry)

            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    raise CircuitBreakerOpen(self.name, 1.0)
                self._half_open_calls += 1

    async def _on_success(self) -> None:
        """Record successful call."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                self._half_open_calls -= 1

                if self._success_count >= self.success_threshold:
                    self._transition_to_closed()

            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0

    async def _on_failure(self, error: Optional[Exception]) -> None:
        """Record failed call."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            logger.warning(
                "Circuit breaker failure",
                name=self.name,
                state=self._state.value,
                failure_count=self._failure_count,
                error=str(error) if error else None,
            )

            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls -= 1
                self._transition_to_open()

            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    self._transition_to_open()

    def _transition_to_open(self) -> None:
        """Transition to open state."""
        self._state = CircuitState.OPEN
        self._success_count = 0
        logger.warning(
            "Circuit breaker opened",
            name=self.name,
            failure_count=self._failure_count,
            timeout_seconds=self.timeout_seconds,
        )

    def _transition_to_half_open(self) -> None:
        """Transition to half-open state."""
        self._state = CircuitState.HALF_OPEN
        self._success_count = 0
        self._half_open_calls = 0
        logger.info(
            "Circuit breaker half-open",
            name=self.name,
        )

    def _transition_to_closed(self) -> None:
        """Transition to closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        logger.info(
            "Circuit breaker closed",
            name=self.name,
        )

    def reset(self) -> None:
        """Manually reset circuit to closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
        logger.info(
            "Circuit breaker manually reset",
            name=self.name,
        )

    async def call(
        self,
        func: Callable[..., T],
        *args,
        fallback: Optional[Callable[..., T]] = None,
        **kwargs,
    ) -> T:
        """Execute function with circuit breaker protection.

        Args:
            func: Async function to call
            *args: Positional arguments for func
            fallback: Optional fallback function if circuit is open
            **kwargs: Keyword arguments for func

        Returns:
            Result from func or fallback

        Raises:
            CircuitBreakerOpen: If circuit is open and no fallback provided
        """
        try:
            async with self:
                return await func(*args, **kwargs)
        except CircuitBreakerOpen:
            if fallback:
                logger.info(
                    "Using fallback due to open circuit",
                    name=self.name,
                )
                return await fallback(*args, **kwargs)
            raise


class CircuitBreakerRegistry:
    """Registry of circuit breakers for different services."""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

    async def get(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout_seconds: float = 60.0,
    ) -> CircuitBreaker:
        """Get or create circuit breaker for a service.

        Args:
            name: Service name
            failure_threshold: Failures before opening
            timeout_seconds: Time before attempting recovery

        Returns:
            CircuitBreaker for the service
        """
        async with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    timeout_seconds=timeout_seconds,
                )
            return self._breakers[name]

    def status(self) -> dict[str, dict]:
        """Get status of all circuit breakers.

        Returns:
            Dict mapping service name to status info
        """
        return {
            name: {
                "state": cb.state.value,
                "failure_count": cb._failure_count,
                "time_until_retry": cb.time_until_retry,
            }
            for name, cb in self._breakers.items()
        }


# Global registry
_cb_registry: Optional[CircuitBreakerRegistry] = None


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get the global circuit breaker registry."""
    global _cb_registry
    if _cb_registry is None:
        _cb_registry = CircuitBreakerRegistry()
    return _cb_registry
