"""
Tests for sruth.shared.observability module.

Tests:
- UnifiedTracer context managers
- TraceSpan dataclass
- Backend initialization
"""

from unittest.mock import patch

import pytest


class TestTraceSpan:
    """Tests for TraceSpan dataclass."""

    def test_trace_span_creation(self):
        """Test TraceSpan creation with defaults."""
        from sruth.shared.observability import TraceSpan

        span = TraceSpan(name="test", span_type="workflow")

        assert span.name == "test"
        assert span.span_type == "workflow"
        assert span.status == "running"
        assert span.error is None

    def test_trace_span_complete(self):
        """Test TraceSpan complete method."""
        from sruth.shared.observability import TraceSpan

        span = TraceSpan(name="test", span_type="workflow")
        span.complete("completed")

        assert span.status == "completed"
        assert span.end_time is not None

    def test_trace_span_duration(self):
        """Test TraceSpan duration_ms property."""
        from datetime import datetime, timedelta

        from sruth.shared.observability import TraceSpan

        span = TraceSpan(name="test", span_type="workflow")
        span.start_time = datetime.now() - timedelta(milliseconds=100)
        span.complete()

        assert span.duration_ms is not None
        assert span.duration_ms >= 100


class TestUnifiedTracer:
    """Tests for UnifiedTracer."""

    def test_tracer_creation(self):
        """Test UnifiedTracer can be created."""
        from sruth.shared.observability import UnifiedTracer

        tracer = UnifiedTracer(
            datadog_enabled=False,
            langfuse_enabled=False,
            logfire_enabled=False,
        )

        assert tracer is not None

    def test_trace_context_manager(self):
        """Test trace context manager."""
        from sruth.shared.observability import UnifiedTracer

        tracer = UnifiedTracer(
            datadog_enabled=False,
            langfuse_enabled=False,
            logfire_enabled=False,
        )

        with tracer.trace("test_span", span_type="workflow") as span:
            assert span.name == "test_span"
            assert span.status == "running"

        assert span.status == "completed"

    def test_trace_agent_context_manager(self):
        """Test trace_agent context manager."""
        from sruth.shared.observability import UnifiedTracer

        tracer = UnifiedTracer(
            datadog_enabled=False,
            langfuse_enabled=False,
            logfire_enabled=False,
        )

        with tracer.trace_agent("my_agent", framework="adk") as span:
            assert span.span_type == "agent"
            assert span.metadata["framework"] == "adk"

    def test_trace_tool_context_manager(self):
        """Test trace_tool context manager."""
        from sruth.shared.observability import UnifiedTracer

        tracer = UnifiedTracer(
            datadog_enabled=False,
            langfuse_enabled=False,
            logfire_enabled=False,
        )

        with tracer.trace_tool("search", arguments={"query": "test"}) as span:
            assert span.span_type == "tool"
            assert span.metadata["arguments"]["query"] == "test"

    def test_trace_captures_error(self):
        """Test trace captures errors."""
        from sruth.shared.observability import UnifiedTracer

        tracer = UnifiedTracer(
            datadog_enabled=False,
            langfuse_enabled=False,
            logfire_enabled=False,
        )

        span_ref = None
        try:
            with tracer.trace("failing_span") as span:
                span_ref = span
                raise ValueError("Test error")
        except ValueError:
            pass

        assert span_ref.status == "error"
        assert span_ref.error == "Test error"


class TestTracingBackends:
    """Tests for tracing backends."""

    def test_datadog_backend_disabled_without_key(self):
        """Test DatadogBackend is disabled without API key."""
        from sruth.shared.observability import DatadogBackend

        with patch.dict("os.environ", {}, clear=True):
            backend = DatadogBackend(api_key=None)
            assert not backend.enabled

    def test_langfuse_backend_disabled_without_keys(self):
        """Test LangfuseBackend is disabled without keys."""
        from sruth.shared.observability import LangfuseBackend

        with patch.dict("os.environ", {}, clear=True):
            backend = LangfuseBackend(public_key=None, secret_key=None)
            assert not backend.enabled

    def test_logfire_backend_disabled_without_token(self):
        """Test LogfireBackend is disabled without token."""
        from sruth.shared.observability import LogfireBackend

        with patch.dict("os.environ", {}, clear=True):
            backend = LogfireBackend(token=None)
            assert not backend.enabled


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_tracer_returns_singleton(self):
        """Test get_tracer returns singleton."""
        from sruth.shared.observability import get_tracer

        tracer1 = get_tracer()
        tracer2 = get_tracer()

        assert tracer1 is tracer2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
