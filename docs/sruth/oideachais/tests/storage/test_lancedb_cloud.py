"""
Unit tests for LanceDB Cloud client with circuit breaker.

Tests the circuit breaker pattern, retry logic, and resilient operations.

Run with: pytest tests/storage/test_lancedb_cloud.py
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


# ===========================================================================
# Circuit Breaker Unit Tests
# ===========================================================================


class TestCircuitBreaker:
    """Unit tests for CircuitBreaker class."""

    @pytest.fixture
    def breaker(self) -> Any:
        """Create a circuit breaker for testing."""
        from sruth.shared.utils import CircuitBreaker

        return CircuitBreaker(
            failure_threshold=3,
            recovery_time=2,
            half_open_max_calls=1,
        )

    def test_initial_state_is_closed(self, breaker: Any) -> None:
        """Circuit starts in closed state."""
        assert breaker.get_state("service1") == "closed"
        assert not breaker.is_open("service1")
        assert not breaker.is_half_open("service1")

    def test_failures_below_threshold_stay_closed(self, breaker: Any) -> None:
        """Failures below threshold keep circuit closed."""
        breaker.record_failure("service1")
        breaker.record_failure("service1")

        assert breaker.get_state("service1") == "closed"
        assert breaker._failures["service1"] == 2

    def test_failures_at_threshold_opens_circuit(self, breaker: Any) -> None:
        """Failures at threshold open the circuit."""
        for _ in range(3):
            breaker.record_failure("service1")

        assert breaker.get_state("service1") == "open"
        assert breaker.is_open("service1")

    def test_success_resets_failure_count(self, breaker: Any) -> None:
        """Success resets the failure count."""
        breaker.record_failure("service1")
        breaker.record_failure("service1")
        assert breaker._failures["service1"] == 2

        breaker.record_success("service1")
        assert breaker._failures["service1"] == 0

    def test_open_circuit_blocks_calls(self, breaker: Any) -> None:
        """Open circuit blocks further calls."""
        for _ in range(3):
            breaker.record_failure("service1")

        assert breaker.is_open("service1")
        assert breaker.time_until_recovery("service1") > 0

    def test_circuit_transitions_to_half_open(self, breaker: Any) -> None:
        """Circuit transitions to half-open after recovery time."""
        for _ in range(3):
            breaker.record_failure("service1")

        assert breaker.is_open("service1")

        # Wait for recovery
        time.sleep(2.1)

        # Should transition to half-open
        assert not breaker.is_open("service1")
        assert breaker.is_half_open("service1")

    def test_half_open_success_closes_circuit(self, breaker: Any) -> None:
        """Success in half-open state closes the circuit."""
        for _ in range(3):
            breaker.record_failure("service1")
        time.sleep(2.1)

        # Now in half-open
        assert breaker.is_half_open("service1")

        # Success closes it
        breaker.record_success("service1")
        assert breaker.get_state("service1") == "closed"
        assert breaker._failures["service1"] == 0

    def test_half_open_failure_reopens_circuit(self, breaker: Any) -> None:
        """Failure in half-open state reopens the circuit."""
        for _ in range(3):
            breaker.record_failure("service1")
        time.sleep(2.1)

        # Now in half-open
        assert breaker.is_half_open("service1")

        # Failure reopens it
        breaker.record_failure("service1")
        assert breaker.get_state("service1") == "open"

    def test_independent_services(self, breaker: Any) -> None:
        """Different services have independent states."""
        for _ in range(3):
            breaker.record_failure("service1")

        assert breaker.is_open("service1")
        assert breaker.get_state("service2") == "closed"

        breaker.record_failure("service2")
        assert breaker._failures["service2"] == 1


# ===========================================================================
# Retry Logic Tests
# ===========================================================================


class TestRetryWithBackoff:
    """Tests for the retry_with_backoff function."""

    @pytest.mark.asyncio
    async def test_successful_first_attempt(self) -> None:
        """Successful first attempt returns immediately."""
        from sruth.shared.utils import retry_with_backoff

        call_count = 0

        def success_func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = await retry_with_backoff(success_func, max_attempts=3)

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_retryable_exception(self) -> None:
        """Retries on retryable exceptions."""
        from sruth.shared.utils import retry_with_backoff

        call_count = 0

        def fail_then_succeed() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise OSError("Temporary failure")
            return "success"

        result = await retry_with_backoff(
            fail_then_succeed,
            max_attempts=3,
            base_delay=0.1,
            retryable_exceptions=(OSError,),
        )

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_raises_after_max_attempts(self) -> None:
        """Raises exception after max attempts exhausted."""
        from sruth.shared.utils import retry_with_backoff

        def always_fail() -> str:
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError):
            await retry_with_backoff(
                always_fail,
                max_attempts=2,
                base_delay=0.1,
                retryable_exceptions=(ConnectionError,),
            )

    @pytest.mark.asyncio
    async def test_non_retryable_exception_propagates(self) -> None:
        """Non-retryable exceptions propagate immediately."""
        from sruth.shared.utils import retry_with_backoff

        call_count = 0

        def fail_with_value_error() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("Not retryable")

        with pytest.raises(ValueError):
            await retry_with_backoff(
                fail_with_value_error,
                max_attempts=3,
                base_delay=0.1,
                retryable_exceptions=(OSError,),
            )

        assert call_count == 1  # Only called once


# ===========================================================================
# LanceDB Client Resilience Tests
# ===========================================================================


class TestLanceDBClientResilience:
    """Tests for LanceDB client resilience patterns."""

    @pytest.fixture
    def client(self, temp_dir: Path) -> Any:
        """Create a test LanceDB client."""
        from sruth.shared.utils import CircuitBreaker
        from sruth.oideachais.storage.lancedb_cloud import (
            LanceDBCloudClient,
            LanceDBCloudConfig,
            LanceDBEnvironment,
        )

        config = LanceDBCloudConfig(
            local_path=str(temp_dir / "lancedb"),
            api_key="",
        )
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_time=1,
        )
        return LanceDBCloudClient(
            config=config,
            environment=LanceDBEnvironment.LOCAL,
            circuit_breaker=breaker,
        )

    def test_circuit_breaker_status_initial(self, client: Any) -> None:
        """Circuit breaker starts in closed state."""
        status = client.get_circuit_breaker_status()

        assert status["service"] == "lancedb"
        assert status["state"] == "closed"
        assert status["failures"] == 0
        assert not status["is_open"]
        assert status["time_until_recovery"] == 0.0

    def test_reset_circuit_breaker(self, client: Any) -> None:
        """Circuit breaker can be reset."""
        # Simulate failures
        client._circuit_breaker.record_failure("lancedb")
        client._circuit_breaker.record_failure("lancedb")

        status = client.get_circuit_breaker_status()
        assert status["state"] == "open"

        # Reset
        client.reset_circuit_breaker()

        status = client.get_circuit_breaker_status()
        assert status["state"] == "closed"
        assert status["failures"] == 0

    @pytest.mark.asyncio
    async def test_run_with_resilience_success(self, client: Any) -> None:
        """Successful operations record success."""

        def success_op() -> str:
            return "result"

        result = await client._run_with_resilience(
            success_op,
            operation="test_op",
        )

        assert result == "result"
        assert client._circuit_breaker._failures.get("lancedb", 0) == 0

    @pytest.mark.asyncio
    async def test_run_with_resilience_circuit_open_raises(self, client: Any) -> None:
        """Open circuit raises CircuitBreakerOpen."""
        from sruth.shared.utils import CircuitBreakerOpen

        # Open the circuit
        client._circuit_breaker.record_failure("lancedb")
        client._circuit_breaker.record_failure("lancedb")

        def any_op() -> str:
            return "result"

        with pytest.raises(CircuitBreakerOpen) as exc_info:
            await client._run_with_resilience(any_op, operation="test_op")

        assert exc_info.value.service == "lancedb"
        assert exc_info.value.retry_after > 0

    @pytest.mark.asyncio
    async def test_create_and_list_tables(self, client: Any) -> None:
        """Test table creation through resilient client."""
        import pyarrow as pa

        schema = pa.schema(
            [
                ("id", pa.string()),
                ("data", pa.string()),
            ]
        )

        await client.create_table("resilience_test", schema=schema, mode="overwrite")

        tables = await client.list_tables()
        assert "resilience_test" in tables


# ===========================================================================
# EmbeddingBatch Tests
# ===========================================================================


class TestEmbeddingBatch:
    """Tests for EmbeddingBatch class."""

    def test_embedding_batch_len(self) -> None:
        """Test EmbeddingBatch length."""
        from sruth.oideachais.storage.lancedb_cloud import EmbeddingBatch

        batch = EmbeddingBatch(
            vectors=[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]],
            metadata=[{"a": 1}, {"a": 2}, {"a": 3}],
            ids=["1", "2", "3"],
        )

        assert len(batch) == 3

    def test_embedding_batch_to_arrow(self) -> None:
        """Test EmbeddingBatch conversion to Arrow."""
        from sruth.oideachais.storage.lancedb_cloud import EmbeddingBatch

        batch = EmbeddingBatch(
            vectors=[[0.1, 0.2], [0.3, 0.4]],
            metadata=[{"key": "value1"}, {"key": "value2"}],
            ids=["id1", "id2"],
        )

        arrow_table = batch.to_arrow()

        assert arrow_table.num_rows == 2
        assert "id" in arrow_table.column_names
        assert "vector" in arrow_table.column_names
        assert "metadata" in arrow_table.column_names


# ===========================================================================
# Configuration Tests
# ===========================================================================


class TestLanceDBConfig:
    """Tests for LanceDB configuration."""

    def test_config_defaults(self) -> None:
        """Test default configuration values."""
        from sruth.oideachais.storage.lancedb_cloud import LanceDBCloudConfig

        config = LanceDBCloudConfig()

        assert config.batch_size == 100
        assert config.max_batch_size == 10000

    def test_is_cloud_configured_without_key(self) -> None:
        """Test cloud detection without API key."""
        from sruth.oideachais.storage.lancedb_cloud import LanceDBCloudConfig

        config = LanceDBCloudConfig(api_key="", uri="db://test")

        assert not config.is_cloud_configured()

    def test_is_cloud_configured_with_key(self) -> None:
        """Test cloud detection with API key."""
        from sruth.oideachais.storage.lancedb_cloud import LanceDBCloudConfig

        config = LanceDBCloudConfig(api_key="test_key", uri="db://test")

        assert config.is_cloud_configured()

    def test_is_cloud_configured_local_uri(self) -> None:
        """Test cloud detection with local URI."""
        from sruth.oideachais.storage.lancedb_cloud import LanceDBCloudConfig

        config = LanceDBCloudConfig(api_key="test_key", uri="/tmp/lancedb")

        assert not config.is_cloud_configured()
