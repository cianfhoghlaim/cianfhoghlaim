"""Cost-based backend router with circuit breaker pattern."""

import asyncio
import time
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import TypeVar

import structlog

from ..config import BrowserConfig, get_config
from ..exceptions import (
    BackendError,
    CircuitOpenError,
    FallbackExhaustedError,
)
from ..browser_types import (
    BACKEND_COST,
    BACKEND_PRIORITY,
    BackendHealth,
    BackendType,
    BrowserOperation,
    CircuitState,
)
from .base import BrowserBackend

logger = structlog.get_logger()

T = TypeVar("T")


class CircuitBreaker:
    """Circuit breaker for a single backend."""

    def __init__(
        self,
        backend: BackendType,
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
        half_open_requests: int = 1,
    ):
        self.backend = backend
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_requests = half_open_requests

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure: datetime | None = None
        self._last_success: datetime | None = None
        self._last_error: str | None = None
        self._half_open_count = 0
        self._lock = asyncio.Lock()
        self._latencies: list[float] = []

    @property
    def health(self) -> BackendHealth:
        """Get current health status."""
        avg_latency = sum(self._latencies) / len(self._latencies) if self._latencies else None
        return BackendHealth(
            backend=self.backend,
            state=self._state,
            failure_count=self._failure_count,
            success_count=self._success_count,
            last_failure=self._last_failure,
            last_success=self._last_success,
            last_error=self._last_error,
            latency_ms=avg_latency,
        )

    async def can_execute(self) -> bool:
        """Check if requests can be executed."""
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                return True

            if self._state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self._last_failure:
                    elapsed = datetime.utcnow() - self._last_failure
                    if elapsed >= timedelta(seconds=self.recovery_timeout):
                        self._state = CircuitState.HALF_OPEN
                        self._half_open_count = 0
                        logger.info(
                            "circuit_half_open",
                            backend=self.backend.value,
                        )
                        return True
                return False

            if self._state == CircuitState.HALF_OPEN:
                return self._half_open_count < self.half_open_requests

            return False

    async def record_success(self, latency_ms: float) -> None:
        """Record a successful request."""
        async with self._lock:
            self._success_count += 1
            self._last_success = datetime.utcnow()
            self._latencies.append(latency_ms)
            if len(self._latencies) > 100:
                self._latencies = self._latencies[-100:]

            if self._state == CircuitState.HALF_OPEN:
                self._half_open_count += 1
                if self._half_open_count >= self.half_open_requests:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    logger.info(
                        "circuit_closed",
                        backend=self.backend.value,
                    )

    async def record_failure(self, error: str) -> None:
        """Record a failed request."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure = datetime.utcnow()
            self._last_error = error

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning(
                    "circuit_opened_from_half_open",
                    backend=self.backend.value,
                    error=error,
                )
            elif self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    "circuit_opened",
                    backend=self.backend.value,
                    failure_count=self._failure_count,
                    error=error,
                )

    def time_until_recovery(self) -> float:
        """Get seconds until circuit may close."""
        if self._state != CircuitState.OPEN or not self._last_failure:
            return 0.0
        elapsed = (datetime.utcnow() - self._last_failure).total_seconds()
        return max(0.0, self.recovery_timeout - elapsed)


class BackendRouter:
    """Routes operations to backends with cost-based selection and fallback."""

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._backends: dict[BackendType, BrowserBackend] = {}
        self._circuits: dict[BackendType, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

        # Initialize circuit breakers for all backend types
        for backend_type in BackendType:
            self._circuits[backend_type] = CircuitBreaker(
                backend=backend_type,
                failure_threshold=self.config.circuit_failure_threshold,
                recovery_timeout=self.config.circuit_recovery_timeout,
                half_open_requests=self.config.circuit_half_open_requests,
            )

    def register_backend(self, backend: BrowserBackend) -> None:
        """Register a backend implementation."""
        self._backends[backend.backend_type] = backend
        logger.info("backend_registered", backend=backend.backend_type.value)

    def get_backend(self, backend_type: BackendType) -> BrowserBackend | None:
        """Get a registered backend by type."""
        return self._backends.get(backend_type)

    def get_health(self, backend_type: BackendType) -> BackendHealth:
        """Get health status for a backend."""
        return self._circuits[backend_type].health

    def get_all_health(self) -> list[BackendHealth]:
        """Get health status for all backends."""
        return [circuit.health for circuit in self._circuits.values()]

    async def select_backend(
        self,
        operation: BrowserOperation,
        *,
        exclude: list[BackendType] | None = None,
    ) -> BackendType | None:
        """Select the best available backend for an operation.

        Selection is based on:
        1. Operation-specific priority order
        2. Circuit breaker state (only closed/half-open)
        3. Cost (prefer free self-hosted)
        4. Registration (backend must be registered)
        """
        exclude = exclude or []
        priority_order = BACKEND_PRIORITY.get(operation, list(BackendType))

        # Filter by cost if strategy is "cost"
        if self.config.fallback_strategy == "cost":
            priority_order = sorted(priority_order, key=lambda b: BACKEND_COST.get(b, 999))

        for backend_type in priority_order:
            if backend_type in exclude:
                continue

            # Check if backend is registered
            if backend_type not in self._backends:
                continue

            # Check circuit breaker
            circuit = self._circuits[backend_type]
            if await circuit.can_execute():
                return backend_type

        return None

    async def execute_with_fallback(
        self,
        operation: BrowserOperation,
        func: Callable[[BrowserBackend], Awaitable[T]],
        *,
        max_attempts: int = 3,
    ) -> T:
        """Execute an operation with automatic fallback on failure.

        Args:
            operation: The type of browser operation
            func: Async function that takes a backend and returns result
            max_attempts: Maximum number of backends to try

        Returns:
            The result from the first successful backend

        Raises:
            FallbackExhaustedError: If all backends fail
            CircuitOpenError: If the selected backend's circuit is open
        """
        backends_tried: list[BackendType] = []

        for attempt in range(max_attempts):
            backend_type = await self.select_backend(
                operation,
                exclude=backends_tried,
            )

            if backend_type is None:
                if not backends_tried:
                    raise FallbackExhaustedError(
                        operation.value,
                        backends_tried,
                    )
                break

            backends_tried.append(backend_type)
            backend = self._backends[backend_type]
            circuit = self._circuits[backend_type]

            logger.info(
                "executing_operation",
                operation=operation.value,
                backend=backend_type.value,
                attempt=attempt + 1,
            )

            start_time = time.perf_counter()
            try:
                result = await func(backend)
                latency_ms = (time.perf_counter() - start_time) * 1000
                await circuit.record_success(latency_ms)

                logger.info(
                    "operation_success",
                    operation=operation.value,
                    backend=backend_type.value,
                    latency_ms=latency_ms,
                )
                return result

            except BackendError as e:
                latency_ms = (time.perf_counter() - start_time) * 1000
                await circuit.record_failure(str(e))

                logger.warning(
                    "backend_error",
                    operation=operation.value,
                    backend=backend_type.value,
                    error=str(e),
                    retryable=e.retryable,
                    latency_ms=latency_ms,
                )

                if not e.retryable or not self.config.fallback_enabled:
                    raise

            except Exception as e:
                latency_ms = (time.perf_counter() - start_time) * 1000
                await circuit.record_failure(str(e))

                logger.error(
                    "unexpected_error",
                    operation=operation.value,
                    backend=backend_type.value,
                    error=str(e),
                    latency_ms=latency_ms,
                )

                if not self.config.fallback_enabled:
                    raise BackendError(str(e), backend_type) from e

        raise FallbackExhaustedError(operation.value, backends_tried)

    async def execute_on_backend(
        self,
        backend_type: BackendType,
        func: Callable[[BrowserBackend], Awaitable[T]],
    ) -> T:
        """Execute on a specific backend without fallback.

        Args:
            backend_type: The backend to use
            func: Async function that takes a backend and returns result

        Returns:
            The result from the backend

        Raises:
            CircuitOpenError: If the backend's circuit is open
            KeyError: If the backend is not registered
        """
        if backend_type not in self._backends:
            raise KeyError(f"Backend {backend_type.value} not registered")

        circuit = self._circuits[backend_type]
        if not await circuit.can_execute():
            raise CircuitOpenError(
                backend_type,
                circuit.time_until_recovery(),
            )

        backend = self._backends[backend_type]
        start_time = time.perf_counter()

        try:
            result = await func(backend)
            latency_ms = (time.perf_counter() - start_time) * 1000
            await circuit.record_success(latency_ms)
            return result
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            await circuit.record_failure(str(e))
            raise


# Global router instance
_router: BackendRouter | None = None


def get_router() -> BackendRouter:
    """Get or create the global backend router."""
    global _router
    if _router is None:
        _router = BackendRouter()
    return _router
