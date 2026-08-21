"""
Tests for shared utilities.

Tests the circuit breaker, rate limiter, and retry utilities.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import MagicMock

import pytest

from sruth.shared.utils import (
    CircuitBreaker,
    CircuitBreakerOpen,
    RateLimiter,
    RetryableError,
    retry_with_backoff,
)
from sruth.shared.storage import SerialDatabaseExecutor, run_serial


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""

    def test_starts_closed(self) -> None:
        """Circuit starts in closed state."""
        breaker = CircuitBreaker(failure_threshold=3)
        assert not breaker.is_open("test_service")

    def test_opens_after_failures(self) -> None:
        """Circuit opens after reaching failure threshold."""
        breaker = CircuitBreaker(failure_threshold=2, recovery_time=60)

        # First failure
        breaker.record_failure("test_service")
        assert not breaker.is_open("test_service")

        # Second failure - should open
        breaker.record_failure("test_service")
        assert breaker.is_open("test_service")

    def test_success_resets_failures(self) -> None:
        """Success resets failure count."""
        breaker = CircuitBreaker(failure_threshold=3)

        breaker.record_failure("test_service")
        breaker.record_failure("test_service")
        breaker.record_success("test_service")

        # Should not be open after success reset
        breaker.record_failure("test_service")
        assert not breaker.is_open("test_service")

    def test_call_with_success(self) -> None:
        """call() returns result on success."""
        breaker = CircuitBreaker()

        result = breaker.call("test_service", lambda: 42)
        assert result == 42

    def test_call_raises_when_open(self) -> None:
        """call() raises CircuitBreakerOpen when circuit is open."""
        breaker = CircuitBreaker(failure_threshold=1, recovery_time=60)

        # Open the circuit
        breaker.record_failure("test_service")

        with pytest.raises(CircuitBreakerOpen) as exc_info:
            breaker.call("test_service", lambda: 42)

        assert exc_info.value.service == "test_service"

    def test_half_open_recovery(self) -> None:
        """Circuit recovers through half-open state."""
        breaker = CircuitBreaker(failure_threshold=1, recovery_time=0.1, success_threshold=1)

        # Open the circuit
        breaker.record_failure("test_service")
        assert breaker.is_open("test_service")

        # Wait for recovery period
        time.sleep(0.15)

        # Should allow request through (half-open)
        assert not breaker.is_open("test_service")

        # Success should close the circuit
        breaker.record_success("test_service")
        status = breaker.get_status("test_service")
        assert status["state"] == "closed"


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_allows_requests_under_limit(self) -> None:
        """Allows requests when under rate limit."""
        limiter = RateLimiter(max_per_second=100)

        # Should allow many requests quickly
        for _ in range(10):
            assert limiter.acquire(block=False)

    def test_blocks_when_exhausted(self) -> None:
        """Blocks when rate limit exhausted."""
        limiter = RateLimiter(max_per_second=1, burst_size=1)

        # First request uses all tokens
        assert limiter.acquire(block=False)

        # Second request should fail without blocking
        assert not limiter.acquire(block=False)

    def test_refills_over_time(self) -> None:
        """Tokens refill over time."""
        limiter = RateLimiter(max_per_second=10, burst_size=1)

        # Exhaust tokens
        limiter.acquire(block=False)

        # Wait for refill
        time.sleep(0.15)

        # Should have tokens again
        assert limiter.acquire(block=False)

    @pytest.mark.asyncio
    async def test_async_acquire(self) -> None:
        """Async acquire works correctly."""
        limiter = RateLimiter(max_per_second=100)

        # Should complete quickly
        await asyncio.wait_for(limiter.acquire_async(), timeout=1.0)


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""

    def test_success_on_first_try(self) -> None:
        """No retry needed on success."""
        call_count = 0

        @retry_with_backoff(max_attempts=3)
        def success_fn() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = success_fn()
        assert result == "success"
        assert call_count == 1

    def test_retries_on_failure(self) -> None:
        """Retries when function fails."""
        call_count = 0

        @retry_with_backoff(max_attempts=3, base_delay=0.01)
        def fail_then_succeed() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Not yet")
            return "success"

        result = fail_then_succeed()
        assert result == "success"
        assert call_count == 3

    def test_raises_after_max_attempts(self) -> None:
        """Raises exception after max attempts."""

        @retry_with_backoff(max_attempts=2, base_delay=0.01)
        def always_fails() -> None:
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_fails()

    def test_only_retries_specified_exceptions(self) -> None:
        """Only retries specified exception types."""

        @retry_with_backoff(
            max_attempts=3,
            base_delay=0.01,
            retryable_exceptions=[ValueError],
        )
        def raises_type_error() -> None:
            raise TypeError("Not retryable")

        with pytest.raises(TypeError):
            raises_type_error()

    def test_on_retry_callback(self) -> None:
        """on_retry callback is called."""
        retry_attempts = []

        def on_retry(attempt: int, exc: Exception) -> None:
            retry_attempts.append((attempt, str(exc)))

        @retry_with_backoff(
            max_attempts=3,
            base_delay=0.01,
            on_retry=on_retry,
        )
        def fail_twice() -> str:
            if len(retry_attempts) < 2:
                raise ValueError("Failing")
            return "success"

        result = fail_twice()
        assert result == "success"
        assert len(retry_attempts) == 2


class TestSerialDatabaseExecutor:
    """Tests for SerialDatabaseExecutor."""

    def test_run_returns_result(self) -> None:
        """run() returns function result."""
        result = run_serial(lambda: 42)
        assert result == 42

    def test_run_propagates_exception(self) -> None:
        """run() propagates exceptions."""

        def raise_error() -> None:
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            run_serial(raise_error)

    def test_singleton_pattern(self) -> None:
        """Executor is a singleton."""
        exec1 = SerialDatabaseExecutor()
        exec2 = SerialDatabaseExecutor()
        assert exec1 is exec2

    def test_operation_count(self) -> None:
        """Operation count increases."""
        executor = SerialDatabaseExecutor()
        initial_count = executor.operation_count

        run_serial(lambda: None)
        run_serial(lambda: None)

        assert executor.operation_count == initial_count + 2
