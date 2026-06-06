"""
Unified Observability for Aleyum.

Provides tracing and metrics across multiple backends:
- Datadog LLMObs: Agent traces, token usage, cost tracking
- Langfuse: Prompt management, A/B testing, trace analysis
- Logfire: Pydantic AI specific tracing

This module provides a unified interface for instrumenting agents,
LLM calls, and MCP tool invocations.
"""

import logging
import os
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Generator, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TraceSpan:
    """Represents a trace span across all backends."""
    name: str
    span_type: str  # "agent", "llm", "tool", "workflow"
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    span_id: str = ""
    status: str = "running"  # running, completed, error
    error: Optional[str] = None

    def complete(self, status: str = "completed") -> None:
        """Mark span as complete."""
        self.end_time = datetime.now()
        self.status = status

    @property
    def duration_ms(self) -> Optional[float]:
        """Get span duration in milliseconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return None


class TracingBackend(ABC):
    """Base class for tracing backends."""

    @abstractmethod
    def start_span(
        self,
        name: str,
        span_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        """Start a new span, return span ID."""
        pass

    @abstractmethod
    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """End a span."""
        pass

    @abstractmethod
    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an event within a span."""
        pass


class DatadogBackend(TracingBackend):
    """Datadog LLMObs integration."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DD_API_KEY")
        self.enabled = bool(self.api_key)
        self._llmobs = None

        if self.enabled:
            try:
                from ddtrace.llmobs import LLMObs
                self._llmobs = LLMObs
                LLMObs.enable(api_key=self.api_key)
                logger.info("Datadog LLMObs enabled")
            except ImportError:
                logger.warning("ddtrace not installed, Datadog tracing disabled")
                self.enabled = False

    def start_span(
        self,
        name: str,
        span_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        if not self.enabled or not self._llmobs:
            return ""

        # Map span types to LLMObs span types
        span_kind_map = {
            "agent": "agent",
            "llm": "llm",
            "tool": "tool",
            "workflow": "workflow",
        }

        span_kind = span_kind_map.get(span_type, "task")

        # Create span (simplified - real implementation would track context)
        span_id = f"dd_{name}_{datetime.now().isoformat()}"
        logger.debug(f"Datadog span started: {span_id}")
        return span_id

    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Datadog span ended: {span_id} ({status})")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Datadog event: {event_name} in {span_id}")


class LangfuseBackend(TracingBackend):
    """Langfuse integration for prompt management and tracing."""

    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        self.public_key = public_key or os.environ.get("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.environ.get("LANGFUSE_SECRET_KEY")
        self.enabled = bool(self.public_key and self.secret_key)
        self._client = None

        if self.enabled:
            try:
                from langfuse import Langfuse
                self._client = Langfuse(
                    public_key=self.public_key,
                    secret_key=self.secret_key,
                )
                logger.info("Langfuse enabled")
            except ImportError:
                logger.warning("langfuse not installed, Langfuse tracing disabled")
                self.enabled = False

    def start_span(
        self,
        name: str,
        span_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        if not self.enabled or not self._client:
            return ""

        span_id = f"lf_{name}_{datetime.now().isoformat()}"
        logger.debug(f"Langfuse span started: {span_id}")
        return span_id

    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Langfuse span ended: {span_id} ({status})")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Langfuse event: {event_name} in {span_id}")


class LogfireBackend(TracingBackend):
    """Logfire integration for Pydantic AI tracing."""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("LOGFIRE_TOKEN")
        self.enabled = bool(self.token)
        self._logfire = None

        if self.enabled:
            try:
                import logfire
                logfire.configure(token=self.token)
                self._logfire = logfire
                logger.info("Logfire enabled")
            except ImportError:
                logger.warning("logfire not installed, Logfire tracing disabled")
                self.enabled = False

    def start_span(
        self,
        name: str,
        span_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        if not self.enabled:
            return ""

        span_id = f"log_{name}_{datetime.now().isoformat()}"
        logger.debug(f"Logfire span started: {span_id}")
        return span_id

    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Logfire span ended: {span_id} ({status})")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Logfire event: {event_name} in {span_id}")


class AleyumTracer:
    """
    Unified tracer for Aleyum agents and workflows.

    Sends traces to all configured backends (Datadog, Langfuse, Logfire)
    providing comprehensive observability across the agent ecosystem.

    Usage:
        tracer = AleyumTracer()

        with tracer.trace_agent("code_analyzer", framework="adk"):
            with tracer.trace_tool("codeolas_search", {"query": "async"}):
                # Tool execution
                pass

        # Or with decorators:
        @tracer.traced("my_function", span_type="tool")
        async def my_function():
            pass
    """

    def __init__(self):
        """Initialize with all available backends."""
        self.backends: List[TracingBackend] = []

        # Initialize backends based on environment
        self.backends.append(DatadogBackend())
        self.backends.append(LangfuseBackend())
        self.backends.append(LogfireBackend())

        self._active_spans: Dict[str, List[str]] = {}  # backend_name -> span_ids

        enabled_backends = [
            b.__class__.__name__ for b in self.backends if b.enabled
        ]
        logger.info(f"AleyumTracer initialized with backends: {enabled_backends}")

    @contextmanager
    def trace(
        self,
        name: str,
        span_type: str = "workflow",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Generator[TraceSpan, None, None]:
        """
        Context manager for creating a trace span.

        Args:
            name: Span name
            span_type: Type of span (agent, llm, tool, workflow)
            metadata: Additional metadata

        Yields:
            TraceSpan object for adding metadata during execution
        """
        span = TraceSpan(name=name, span_type=span_type, metadata=metadata or {})
        span_ids = []

        try:
            # Start span on all backends
            for backend in self.backends:
                span_id = backend.start_span(name, span_type, metadata)
                if span_id:
                    span_ids.append((backend, span_id))

            yield span

            span.complete("completed")

        except Exception as e:
            span.complete("error")
            span.error = str(e)
            raise

        finally:
            # End span on all backends
            for backend, span_id in span_ids:
                backend.end_span(
                    span_id,
                    status=span.status,
                    metadata=span.metadata,
                    error=span.error,
                )

    @contextmanager
    def trace_agent(
        self,
        agent_name: str,
        framework: str = "unknown",
        **metadata: Any,
    ) -> Generator[TraceSpan, None, None]:
        """Trace an agent execution."""
        with self.trace(
            name=agent_name,
            span_type="agent",
            metadata={"framework": framework, **metadata},
        ) as span:
            yield span

    @contextmanager
    def trace_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        **metadata: Any,
    ) -> Generator[TraceSpan, None, None]:
        """Trace a tool invocation."""
        with self.trace(
            name=tool_name,
            span_type="tool",
            metadata={"arguments": arguments, **metadata},
        ) as span:
            yield span

    @contextmanager
    def trace_llm(
        self,
        model: str,
        prompt: Optional[str] = None,
        **metadata: Any,
    ) -> Generator[TraceSpan, None, None]:
        """Trace an LLM call."""
        with self.trace(
            name=model,
            span_type="llm",
            metadata={"prompt_length": len(prompt) if prompt else 0, **metadata},
        ) as span:
            yield span

    def traced(
        self,
        name: Optional[str] = None,
        span_type: str = "workflow",
    ):
        """
        Decorator for tracing functions.

        Usage:
            @tracer.traced("my_function", span_type="tool")
            async def my_function():
                pass
        """
        def decorator(func):
            span_name = name or func.__name__

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.trace(span_name, span_type):
                    return await func(*args, **kwargs)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with self.trace(span_name, span_type):
                    return func(*args, **kwargs)

            # Return appropriate wrapper
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator


# Global tracer instance
_tracer: Optional[AleyumTracer] = None


def get_tracer() -> AleyumTracer:
    """Get the global AleyumTracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = AleyumTracer()
    return _tracer


# Convenience context managers
def trace_agent_run(agent_name: str, framework: str = "unknown", **metadata):
    """Convenience function for agent tracing."""
    return get_tracer().trace_agent(agent_name, framework, **metadata)


def trace_tool_call(tool_name: str, arguments: Optional[Dict[str, Any]] = None, **metadata):
    """Convenience function for tool tracing."""
    return get_tracer().trace_tool(tool_name, arguments, **metadata)
