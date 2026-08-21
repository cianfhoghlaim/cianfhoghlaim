"""Tests for backend router and circuit breaker pattern."""

import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Skip all async tests if pytest-asyncio not installed
try:
    import pytest_asyncio

    HAS_PYTEST_ASYNCIO = True
except ImportError:
    HAS_PYTEST_ASYNCIO = False

requires_async = pytest.mark.skipif(
    not HAS_PYTEST_ASYNCIO, reason="pytest-asyncio not installed"
)


@requires_async
class TestCircuitBreakerInit:
    """Test CircuitBreaker initialization."""

    @pytest.mark.asyncio
    async def test_initial_state_is_closed(self):
        """Circuit breaker should start in CLOSED state."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType, CircuitState

        breaker = CircuitBreaker(BackendType.CDP_LOCAL)
        assert breaker._state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_initial_failure_count_is_zero(self):
        """Circuit breaker should start with zero failure count."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType

        breaker = CircuitBreaker(BackendType.CDP_LOCAL)
        assert breaker._failure_count == 0
        assert breaker._success_count == 0

    @pytest.mark.asyncio
    async def test_custom_threshold_values(self):
        """Circuit breaker should accept custom threshold values."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType

        breaker = CircuitBreaker(
            BackendType.CDP_LOCAL,
            failure_threshold=5,
            recovery_timeout=60.0,
            half_open_requests=2,
        )
        assert breaker.failure_threshold == 5
        assert breaker.recovery_timeout == 60.0
        assert breaker.half_open_requests == 2

    @pytest.mark.asyncio
    async def test_health_property_initial(self):
        """Health property should return correct initial state."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType, CircuitState

        breaker = CircuitBreaker(BackendType.CDP_LOCAL)
        health = breaker.health

        assert health.backend == BackendType.CDP_LOCAL
        assert health.state == CircuitState.CLOSED
        assert health.failure_count == 0
        assert health.success_count == 0
        assert health.latency_ms is None


@requires_async
class TestCircuitBreakerStateTransitions:
    """Test circuit breaker state transitions."""

    @pytest.mark.asyncio
    async def test_stays_closed_below_threshold(self):
        """Circuit should stay closed if failures are below threshold."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType, CircuitState

        breaker = CircuitBreaker(BackendType.CDP_LOCAL, failure_threshold=3)

        # Record 2 failures (below threshold of 3)
        await breaker.record_failure("error 1")
        await breaker.record_failure("error 2")

        assert breaker._state == CircuitState.CLOSED
        assert breaker._failure_count == 2

    @pytest.mark.asyncio
    async def test_opens_at_threshold(self):
        """Circuit should open when failures reach threshold."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType, CircuitState

        breaker = CircuitBreaker(BackendType.CDP_LOCAL, failure_threshold=3)

        # Record exactly threshold failures
        await breaker.record_failure("error 1")
        await breaker.record_failure("error 2")
        await breaker.record_failure("error 3")

        assert breaker._state == CircuitState.OPEN
        assert breaker._failure_count == 3

    @pytest.mark.asyncio
    async def test_cannot_execute_when_open(self):
        """Circuit should not allow execution when open."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType, CircuitState

        breaker = CircuitBreaker(
            BackendType.CDP_LOCAL, failure_threshold=3, recovery_timeout=30.0
        )

        # Force to OPEN state
        for _ in range(3):
            await breaker.record_failure("error")

        assert breaker._state == CircuitState.OPEN
        assert await breaker.can_execute() is False

    @pytest.mark.asyncio
    async def test_transitions_to_half_open_after_timeout(self):
        """Circuit should transition to HALF_OPEN after recovery timeout."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType, CircuitState

        breaker = CircuitBreaker(
            BackendType.CDP_LOCAL, failure_threshold=3, recovery_timeout=0.1
        )

        # Open the circuit
        for _ in range(3):
            await breaker.record_failure("error")

        assert breaker._state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(0.15)

        # Should transition to HALF_OPEN on can_execute check
        can_exec = await breaker.can_execute()
        assert can_exec is True
        assert breaker._state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_closes_after_success_in_half_open(self):
        """Circuit should close after successful request in HALF_OPEN state."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType, CircuitState

        breaker = CircuitBreaker(
            BackendType.CDP_LOCAL,
            failure_threshold=3,
            recovery_timeout=0.1,
            half_open_requests=1,
        )

        # Open the circuit
        for _ in range(3):
            await breaker.record_failure("error")

        # Wait for recovery timeout
        await asyncio.sleep(0.15)
        await breaker.can_execute()  # Transition to HALF_OPEN

        assert breaker._state == CircuitState.HALF_OPEN

        # Record success
        await breaker.record_success(100.0)

        assert breaker._state == CircuitState.CLOSED
        assert breaker._failure_count == 0

    @pytest.mark.asyncio
    async def test_reopens_on_failure_in_half_open(self):
        """Circuit should reopen on failure in HALF_OPEN state."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType, CircuitState

        breaker = CircuitBreaker(
            BackendType.CDP_LOCAL, failure_threshold=3, recovery_timeout=0.1
        )

        # Open the circuit
        for _ in range(3):
            await breaker.record_failure("error")

        # Wait for recovery timeout
        await asyncio.sleep(0.15)
        await breaker.can_execute()  # Transition to HALF_OPEN

        assert breaker._state == CircuitState.HALF_OPEN

        # Record failure - should reopen immediately
        await breaker.record_failure("half_open_error")

        assert breaker._state == CircuitState.OPEN


@requires_async
class TestCircuitBreakerExecution:
    """Test circuit breaker execution control."""

    @pytest.mark.asyncio
    async def test_can_execute_when_closed(self):
        """Should allow execution when circuit is closed."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType

        breaker = CircuitBreaker(BackendType.CDP_LOCAL)
        assert await breaker.can_execute() is True

    @pytest.mark.asyncio
    async def test_success_records_latency(self):
        """Success should record latency."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType

        breaker = CircuitBreaker(BackendType.CDP_LOCAL)

        await breaker.record_success(150.0)
        await breaker.record_success(250.0)

        health = breaker.health
        assert health.latency_ms == 200.0  # Average of 150 and 250

    @pytest.mark.asyncio
    async def test_latency_buffer_limited_to_100(self):
        """Latency buffer should be limited to 100 entries."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType

        breaker = CircuitBreaker(BackendType.CDP_LOCAL)

        # Record 150 successes
        for i in range(150):
            await breaker.record_success(float(i))

        # Should only keep last 100
        assert len(breaker._latencies) == 100

    @pytest.mark.asyncio
    async def test_time_until_recovery_when_closed(self):
        """Time until recovery should be 0 when closed."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType

        breaker = CircuitBreaker(BackendType.CDP_LOCAL)
        assert breaker.time_until_recovery() == 0.0

    @pytest.mark.asyncio
    async def test_time_until_recovery_when_open(self):
        """Time until recovery should be positive when open."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType

        breaker = CircuitBreaker(
            BackendType.CDP_LOCAL, failure_threshold=3, recovery_timeout=30.0
        )

        for _ in range(3):
            await breaker.record_failure("error")

        recovery_time = breaker.time_until_recovery()
        assert recovery_time > 0
        assert recovery_time <= 30.0


@requires_async
class TestBackendRouterInit:
    """Test BackendRouter initialization."""

    @pytest.mark.asyncio
    async def test_initializes_with_config(self):
        """Router should initialize with provided config."""
        from browser.backends.router import BackendRouter
        from browser.core.config import BrowserConfig

        config = BrowserConfig()
        router = BackendRouter(config=config)

        assert router.config is config

    @pytest.mark.asyncio
    async def test_initializes_circuit_breakers_for_all_backends(self):
        """Router should initialize circuit breakers for all backend types."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType

        router = BackendRouter()

        for backend_type in BackendType:
            assert backend_type in router._circuits


@requires_async
class TestBackendRouterRegistration:
    """Test backend registration."""

    @pytest.mark.asyncio
    async def test_register_backend(self):
        """Should be able to register a backend."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType

        router = BackendRouter()

        mock_backend = MagicMock()
        mock_backend.backend_type = BackendType.CDP_LOCAL

        router.register_backend(mock_backend)

        assert router.get_backend(BackendType.CDP_LOCAL) is mock_backend

    @pytest.mark.asyncio
    async def test_get_unregistered_backend_returns_none(self):
        """Getting unregistered backend should return None."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType

        router = BackendRouter()
        assert router.get_backend(BackendType.CDP_LOCAL) is None


@requires_async
class TestBackendRouterSelection:
    """Test backend selection logic."""

    @pytest.mark.asyncio
    async def test_select_backend_prefers_registered(self):
        """Should only select registered backends."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType, BrowserOperation

        router = BackendRouter()

        # Register CRAWL4AI_LOCAL which is in SCRAPE priority
        mock_backend = MagicMock()
        mock_backend.backend_type = BackendType.CRAWL4AI_LOCAL
        router.register_backend(mock_backend)

        selected = await router.select_backend(BrowserOperation.SCRAPE)
        assert selected == BackendType.CRAWL4AI_LOCAL

    @pytest.mark.asyncio
    async def test_select_backend_excludes_specified(self):
        """Should not select excluded backends."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType, BrowserOperation

        router = BackendRouter()

        # Register two backends that are in SCRAPE priority
        mock_crawl4ai = MagicMock()
        mock_crawl4ai.backend_type = BackendType.CRAWL4AI_LOCAL
        router.register_backend(mock_crawl4ai)

        mock_firecrawl = MagicMock()
        mock_firecrawl.backend_type = BackendType.FIRECRAWL_MCP
        router.register_backend(mock_firecrawl)

        # Exclude CRAWL4AI_LOCAL - should fallback to FIRECRAWL_MCP
        selected = await router.select_backend(
            BrowserOperation.SCRAPE, exclude=[BackendType.CRAWL4AI_LOCAL]
        )
        assert selected == BackendType.FIRECRAWL_MCP

    @pytest.mark.asyncio
    async def test_select_backend_returns_none_when_all_excluded(self):
        """Should return None when all backends excluded."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType, BrowserOperation

        router = BackendRouter()

        # Register only CRAWL4AI_LOCAL which is in SCRAPE priority
        mock_backend = MagicMock()
        mock_backend.backend_type = BackendType.CRAWL4AI_LOCAL
        router.register_backend(mock_backend)

        # Exclude the only registered backend
        selected = await router.select_backend(
            BrowserOperation.SCRAPE, exclude=[BackendType.CRAWL4AI_LOCAL]
        )
        assert selected is None

    @pytest.mark.asyncio
    async def test_select_backend_skips_open_circuits(self):
        """Should not select backends with open circuits."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType, BrowserOperation

        router = BackendRouter()

        # Register backend that's in SCRAPE priority
        mock_backend = MagicMock()
        mock_backend.backend_type = BackendType.CRAWL4AI_LOCAL
        router.register_backend(mock_backend)

        # Open its circuit
        circuit = router._circuits[BackendType.CRAWL4AI_LOCAL]
        for _ in range(5):
            await circuit.record_failure("error")

        selected = await router.select_backend(BrowserOperation.SCRAPE)
        assert selected is None


@requires_async
class TestBackendRouterExecution:
    """Test execute_with_fallback functionality."""

    @pytest.mark.asyncio
    async def test_execute_with_fallback_success(self):
        """Should execute successfully with first backend."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType, BrowserOperation

        router = BackendRouter()

        # Use CRAWL4AI_LOCAL which is in SCRAPE priority
        mock_backend = MagicMock()
        mock_backend.backend_type = BackendType.CRAWL4AI_LOCAL
        router.register_backend(mock_backend)

        async def mock_func(backend):
            return {"result": "success"}

        result = await router.execute_with_fallback(BrowserOperation.SCRAPE, mock_func)
        assert result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_execute_with_fallback_tries_next_on_failure(self):
        """Should try next backend on failure."""
        from browser.backends.router import BackendRouter
        from browser.core.exceptions import BackendError
        from browser.core.types import BackendType, BrowserOperation

        router = BackendRouter()

        # Register two backends that are in SCRAPE priority
        mock_crawl4ai = MagicMock()
        mock_crawl4ai.backend_type = BackendType.CRAWL4AI_LOCAL
        router.register_backend(mock_crawl4ai)

        mock_firecrawl = MagicMock()
        mock_firecrawl.backend_type = BackendType.FIRECRAWL_MCP
        router.register_backend(mock_firecrawl)

        call_count = 0

        async def mock_func(backend):
            nonlocal call_count
            call_count += 1
            if backend.backend_type == BackendType.CRAWL4AI_LOCAL:
                raise BackendError("Crawl4AI failed", BackendType.CRAWL4AI_LOCAL, retryable=True)
            return {"result": "success"}

        result = await router.execute_with_fallback(BrowserOperation.SCRAPE, mock_func)
        assert result == {"result": "success"}
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_execute_with_fallback_exhausted(self):
        """Should raise FallbackExhaustedError when all backends fail."""
        from browser.backends.router import BackendRouter
        from browser.core.exceptions import BackendError, FallbackExhaustedError
        from browser.core.types import BackendType, BrowserOperation

        router = BackendRouter()

        # Use CRAWL4AI_LOCAL which is in SCRAPE priority
        mock_backend = MagicMock()
        mock_backend.backend_type = BackendType.CRAWL4AI_LOCAL
        router.register_backend(mock_backend)

        async def mock_func(backend):
            raise BackendError("Always fails", BackendType.CRAWL4AI_LOCAL, retryable=True)

        with pytest.raises(FallbackExhaustedError):
            await router.execute_with_fallback(BrowserOperation.SCRAPE, mock_func)

    @pytest.mark.asyncio
    async def test_execute_with_fallback_no_backends(self):
        """Should raise FallbackExhaustedError when no backends registered."""
        from browser.backends.router import BackendRouter
        from browser.core.exceptions import FallbackExhaustedError
        from browser.core.types import BrowserOperation

        router = BackendRouter()

        async def mock_func(backend):
            return {"result": "success"}

        with pytest.raises(FallbackExhaustedError):
            await router.execute_with_fallback(BrowserOperation.SCRAPE, mock_func)

    @pytest.mark.asyncio
    async def test_execute_with_fallback_records_success_latency(self):
        """Should record success latency on circuit breaker."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType, BrowserOperation

        router = BackendRouter()

        # Use CRAWL4AI_LOCAL which is in SCRAPE priority
        mock_backend = MagicMock()
        mock_backend.backend_type = BackendType.CRAWL4AI_LOCAL
        router.register_backend(mock_backend)

        async def mock_func(backend):
            return {"result": "success"}

        await router.execute_with_fallback(BrowserOperation.SCRAPE, mock_func)

        circuit = router._circuits[BackendType.CRAWL4AI_LOCAL]
        assert circuit._success_count == 1
        assert len(circuit._latencies) == 1

    @pytest.mark.asyncio
    async def test_execute_with_fallback_records_failure(self):
        """Should record failure on circuit breaker."""
        from browser.backends.router import BackendRouter
        from browser.core.exceptions import BackendError, FallbackExhaustedError
        from browser.core.types import BackendType, BrowserOperation

        router = BackendRouter()

        # Use CRAWL4AI_LOCAL which is in SCRAPE priority
        mock_backend = MagicMock()
        mock_backend.backend_type = BackendType.CRAWL4AI_LOCAL
        router.register_backend(mock_backend)

        async def mock_func(backend):
            raise BackendError("Failed", BackendType.CRAWL4AI_LOCAL, retryable=True)

        with pytest.raises(FallbackExhaustedError):
            await router.execute_with_fallback(BrowserOperation.SCRAPE, mock_func)

        circuit = router._circuits[BackendType.CRAWL4AI_LOCAL]
        assert circuit._failure_count == 1


@requires_async
class TestBackendRouterExecuteOnBackend:
    """Test execute_on_backend functionality."""

    @pytest.mark.asyncio
    async def test_execute_on_specific_backend_success(self):
        """Should execute on specific backend successfully."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType

        router = BackendRouter()

        mock_backend = MagicMock()
        mock_backend.backend_type = BackendType.CDP_LOCAL
        router.register_backend(mock_backend)

        async def mock_func(backend):
            return {"backend": backend.backend_type.value}

        result = await router.execute_on_backend(BackendType.CDP_LOCAL, mock_func)
        assert result == {"backend": "cdp_local"}

    @pytest.mark.asyncio
    async def test_execute_on_unregistered_backend_raises(self):
        """Should raise KeyError for unregistered backend."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType

        router = BackendRouter()

        async def mock_func(backend):
            return {"result": "success"}

        with pytest.raises(KeyError):
            await router.execute_on_backend(BackendType.CDP_LOCAL, mock_func)

    @pytest.mark.asyncio
    async def test_execute_on_backend_with_open_circuit_raises(self):
        """Should raise CircuitOpenError when circuit is open."""
        from browser.backends.router import BackendRouter
        from browser.core.exceptions import CircuitOpenError
        from browser.core.types import BackendType

        router = BackendRouter()

        mock_backend = MagicMock()
        mock_backend.backend_type = BackendType.CDP_LOCAL
        router.register_backend(mock_backend)

        # Open the circuit
        circuit = router._circuits[BackendType.CDP_LOCAL]
        for _ in range(5):
            await circuit.record_failure("error")

        async def mock_func(backend):
            return {"result": "success"}

        with pytest.raises(CircuitOpenError):
            await router.execute_on_backend(BackendType.CDP_LOCAL, mock_func)


@requires_async
class TestBackendRouterHealth:
    """Test health reporting functionality."""

    @pytest.mark.asyncio
    async def test_get_health_single_backend(self):
        """Should get health for single backend."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType, CircuitState

        router = BackendRouter()

        health = router.get_health(BackendType.CDP_LOCAL)
        assert health.backend == BackendType.CDP_LOCAL
        assert health.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_get_all_health(self):
        """Should get health for all backends."""
        from browser.backends.router import BackendRouter
        from browser.core.types import BackendType

        router = BackendRouter()

        all_health = router.get_all_health()
        assert len(all_health) == len(BackendType)

        backends_in_health = {h.backend for h in all_health}
        assert backends_in_health == set(BackendType)


@requires_async
class TestGlobalRouter:
    """Test global router instance."""

    @pytest.mark.asyncio
    async def test_get_router_creates_instance(self):
        """get_router should create instance on first call."""
        from browser.backends import router as router_module
        from browser.backends.router import BackendRouter, get_router

        # Reset global
        router_module._router = None

        r = get_router()
        assert isinstance(r, BackendRouter)

    @pytest.mark.asyncio
    async def test_get_router_returns_same_instance(self):
        """get_router should return same instance on subsequent calls."""
        from browser.backends import router as router_module
        from browser.backends.router import get_router

        # Reset global
        router_module._router = None

        r1 = get_router()
        r2 = get_router()

        assert r1 is r2


class TestCircuitBreakerConcurrency:
    """Test circuit breaker thread safety."""

    @pytest.mark.asyncio
    @requires_async
    async def test_concurrent_failures(self):
        """Circuit breaker should handle concurrent failures correctly."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType, CircuitState

        breaker = CircuitBreaker(BackendType.CDP_LOCAL, failure_threshold=10)

        # Record 10 failures concurrently
        async def record_one():
            await breaker.record_failure("concurrent error")

        await asyncio.gather(*[record_one() for _ in range(10)])

        assert breaker._failure_count == 10
        assert breaker._state == CircuitState.OPEN

    @pytest.mark.asyncio
    @requires_async
    async def test_concurrent_successes(self):
        """Circuit breaker should handle concurrent successes correctly."""
        from browser.backends.router import CircuitBreaker
        from browser.core.types import BackendType

        breaker = CircuitBreaker(BackendType.CDP_LOCAL)

        # Record 50 successes concurrently
        async def record_one():
            await breaker.record_success(100.0)

        await asyncio.gather(*[record_one() for _ in range(50)])

        assert breaker._success_count == 50
