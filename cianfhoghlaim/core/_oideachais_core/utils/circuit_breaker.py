"""
Circuit Breaker Pattern for API Resilience.

Prevents cascading failures by tracking service health and
temporarily blocking requests to failing services.

Based on patterns from sruth/browser/core/llm_router.py
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""

    def __init__(self, service: str, retry_after: float):
        self.service = service
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker open for '{service}'. "
            f"Retry after {retry_after:.1f} seconds."
        )


@dataclass
class ServiceState:
    """State tracking for a single service."""
    failures: int = 0
    successes: int = 0
    last_failure: float = 0.0
    state: CircuitState = CircuitState.CLOSED


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for preventing cascading failures.

    When a service fails repeatedly, the circuit "opens" and blocks
    further requests for a recovery period. After recovery, the circuit
    enters "half-open" state to test if the service has recovered.

    Usage:
        breaker = CircuitBreaker(failure_threshold=3, recovery_time=60)

        try:
            result = breaker.call("api_name", lambda: fetch_api())
        except CircuitBreakerOpen as e:
            print(f"Service unavailable, retry after {e.retry_after}s")

    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_time: Seconds to wait before testing recovery
        success_threshold: Successes needed to close half-open circuit
    """
    failure_threshold: int = 3
    recovery_time: float = 60.0
    success_threshold: int = 2

    _services: dict[str, ServiceState] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        self._services = {}
        self._lock = threading.Lock()

    def _get_state(self, service: str) -> ServiceState:
        """Get or create state for a service."""
        if service not in self._services:
            self._services[service] = ServiceState()
        return self._services[service]

    def is_open(self, service: str) -> bool:
        """Check if circuit is open for a service."""
        with self._lock:
            state = self._get_state(service)

            if state.state == CircuitState.CLOSED:
                return False

            if state.state == CircuitState.OPEN:
                # Check if recovery period has elapsed
                if time.time() - state.last_failure >= self.recovery_time:
                    state.state = CircuitState.HALF_OPEN
                    state.successes = 0
                    logger.info(f"Circuit for '{service}' entering half-open state")
                    return False
                return True

            # HALF_OPEN state allows requests through
            return False

    def record_success(self, service: str) -> None:
        """Record a successful call."""
        with self._lock:
            state = self._get_state(service)

            if state.state == CircuitState.HALF_OPEN:
                state.successes += 1
                if state.successes >= self.success_threshold:
                    state.state = CircuitState.CLOSED
                    state.failures = 0
                    logger.info(f"Circuit for '{service}' closed after recovery")
            elif state.state == CircuitState.CLOSED:
                # Reset failure count on success
                state.failures = 0

    def record_failure(self, service: str) -> None:
        """Record a failed call."""
        with self._lock:
            state = self._get_state(service)
            state.failures += 1
            state.last_failure = time.time()

            if state.state == CircuitState.HALF_OPEN:
                # Single failure in half-open reopens circuit
                state.state = CircuitState.OPEN
                logger.warning(f"Circuit for '{service}' reopened after failure in half-open")
            elif state.failures >= self.failure_threshold:
                state.state = CircuitState.OPEN
                logger.warning(
                    f"Circuit for '{service}' opened after "
                    f"{state.failures} failures"
                )

    def call(
        self,
        service: str,
        fn: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Execute a function with circuit breaker protection.

        Args:
            service: Service identifier for tracking
            fn: Function to execute
            *args: Arguments to pass to fn
            **kwargs: Keyword arguments to pass to fn

        Returns:
            Result of fn execution

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: Any exception from fn (after recording failure)
        """
        if self.is_open(service):
            state = self._get_state(service)
            retry_after = (
                state.last_failure + self.recovery_time - time.time()
            )
            raise CircuitBreakerOpen(service, retry_after)

        try:
            result = fn(*args, **kwargs)
            self.record_success(service)
            return result
        except Exception:
            self.record_failure(service)
            raise

    async def call_async(
        self,
        service: str,
        fn: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Execute an async function with circuit breaker protection.

        Same as call() but for async functions.
        """
        if self.is_open(service):
            state = self._get_state(service)
            retry_after = (
                state.last_failure + self.recovery_time - time.time()
            )
            raise CircuitBreakerOpen(service, retry_after)

        try:
            result = await fn(*args, **kwargs)
            self.record_success(service)
            return result
        except Exception:
            self.record_failure(service)
            raise

    def get_status(self, service: str) -> dict[str, Any]:
        """Get current status for a service."""
        with self._lock:
            state = self._get_state(service)
            return {
                "service": service,
                "state": state.state.value,
                "failures": state.failures,
                "successes": state.successes,
                "last_failure": state.last_failure,
            }

    def reset(self, service: str) -> None:
        """Manually reset circuit for a service."""
        with self._lock:
            if service in self._services:
                del self._services[service]
                logger.info(f"Circuit for '{service}' manually reset")
