"""Unified observability tracer for all sruth flows.

Provides tracing and metrics across multiple backends:
- Datadog LLMObs: Agent traces, token usage, cost tracking
- Langfuse: Prompt management, A/B testing, trace analysis
- Logfire: Pydantic AI specific tracing
- MLflow: Experiment tracking, model registry

This module provides a unified interface for instrumenting agents,
LLM calls, and Dagster assets across all sruth flows.

Usage:
    from sruth.shared.observability import get_tracer

    tracer = get_tracer()

    # Trace agent execution
    with tracer.trace_agent("curriculum_scraper"):
        results = scrape_curriculum()

    # Trace LLM calls
    with tracer.trace_llm("gpt-4", prompt=prompt):
        response = llm.complete(prompt)

    # Decorator for functions
    @tracer.traced("extract_metadata")
    def extract_metadata(doc):
        return extract(doc)
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Generator, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class TraceSpan:
    """Represents a trace span across all backends."""

    name: str
    span_type: str  # "agent", "llm", "tool", "workflow", "asset"
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)
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


# ============================================================================
# Abstract Backend Interface
# ============================================================================


class TracingBackend(ABC):
    """Base class for tracing backends."""

    backend_name: str = "base"
    enabled: bool = True

    @abstractmethod
    def start_span(
        self,
        name: str,
        span_type: str,
        metadata: Optional[dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        """Start a new span, return span ID."""
        pass

    @abstractmethod
    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        """End a span."""
        pass

    @abstractmethod
    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        """Log an event within a span."""
        pass


# ============================================================================
# Datadog Backend
# ============================================================================


class DatadogBackend(TracingBackend):
    """Datadog LLMObs integration."""

    backend_name = "datadog"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("DD_API_KEY")
        self.enabled = bool(self.api_key)
        self._llmobs = None
        self._tracer = None

        if self.enabled:
            try:
                from ddtrace import tracer
                from ddtrace.llmobs import LLMObs

                self._tracer = tracer
                self._llmobs = LLMObs

                # Enable LLMObs
                LLMObs.enable(
                    ml_app=os.getenv("DD_LLMOBS_ML_APP", "sruth-pipelines"),
                    integrations_enabled=True,
                    agentless_enabled=True,
                    site=os.getenv("DD_SITE", "datadoghq.eu"),
                    api_key=self.api_key,
                    env=os.getenv("DD_ENV", "development"),
                    service=os.getenv("DD_SERVICE", "sruth"),
                )

                logger.info("Datadog LLMObs enabled")
            except ImportError:
                logger.warning("ddtrace not installed, Datadog tracing disabled")
                self.enabled = False

    def start_span(
        self,
        name: str,
        span_type: str,
        metadata: Optional[dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        if not self.enabled:
            return ""

        span_id = f"dd_{name}_{datetime.now().isoformat()}"
        logger.debug(f"Datadog span started: {span_id}")
        return span_id

    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Datadog span ended: {span_id} ({status})")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Datadog event: {event_name} in {span_id}")


# ============================================================================
# Langfuse Backend
# ============================================================================


class LangfuseBackend(TracingBackend):
    """Langfuse integration for prompt management and tracing."""

    backend_name = "langfuse"

    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        self.public_key = public_key or os.environ.get("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.environ.get("LANGFUSE_SECRET_KEY")
        self.enabled = bool(self.public_key and self.secret_key)
        self._client = None
        self._active_trace = None

        if self.enabled:
            try:
                from langfuse import Langfuse

                self._client = Langfuse(
                    public_key=self.public_key,
                    secret_key=self.secret_key,
                    host=os.getenv("LANGFUSE_HOST", "https://langfuse.cianfhoghlaim.ie"),
                )
                logger.info("Langfuse enabled")
            except ImportError:
                logger.warning("langfuse not installed, Langfuse tracing disabled")
                self.enabled = False

    def start_span(
        self,
        name: str,
        span_type: str,
        metadata: Optional[dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        if not self.enabled or not self._client:
            return ""

        # Create a new trace or span
        if self._active_trace is None:
            self._active_trace = self._client.trace(
                name=name,
                metadata=metadata or {},
            )
            span_id = self._active_trace.id
        else:
            span = self._active_trace.span(
                name=name,
                metadata=metadata or {},
            )
            span_id = span.id

        logger.debug(f"Langfuse span started: {span_id}")
        return span_id

    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        if not self.enabled or not self._active_trace:
            return

        # Update span metadata
        if metadata:
            if hasattr(self._active_trace, "update"):
                self._active_trace.update(metadata=metadata)

        # Mark as complete
        if status == "error" and error:
            if hasattr(self._active_trace, "end"):
                self._active_trace.end(level="ERROR", status_message=error)
        else:
            if hasattr(self._active_trace, "end"):
                self._active_trace.end()

        logger.debug(f"Langfuse span ended: {span_id} ({status})")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Langfuse event: {event_name} in {span_id}")


# ============================================================================
# Logfire Backend
# ============================================================================


class LogfireBackend(TracingBackend):
    """Logfire integration for Pydantic AI tracing."""

    backend_name = "logfire"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("LOGFIRE_TOKEN")
        self.enabled = bool(self.token)
        self._logfire = None

        if self.enabled:
            try:
                import logfire

                logfire.configure(
                    token=self.token,
                    project_name=os.getenv("LOGFIRE_PROJECT", "sruth"),
                )
                self._logfire = logfire
                logger.info("Logfire enabled")
            except ImportError:
                logger.warning("logfire not installed, Logfire tracing disabled")
                self.enabled = False

    def start_span(
        self,
        name: str,
        span_type: str,
        metadata: Optional[dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        if not self.enabled or not self._logfire:
            return ""

        span_id = f"log_{name}_{datetime.now().isoformat()}"
        logger.debug(f"Logfire span started: {span_id}")
        return span_id

    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Logfire span ended: {span_id} ({status})")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Logfire event: {event_name} in {span_id}")


# ============================================================================
# MLflow Backend
# ============================================================================


class MLflowBackend(TracingBackend):
    """MLflow integration for experiment tracking."""

    backend_name = "mlflow"

    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: str = "sruth",
    ):
        self.tracking_uri = tracking_uri or os.getenv(
            "MLFLOW_TRACKING_URI",
            "https://mlflow.cianfhoghlaim.ie",
        )
        self.experiment_name = experiment_name
        self.enabled = bool(self.tracking_uri)
        self._client = None
        self._active_run = None

        if self.enabled:
            try:
                import mlflow

                mlflow.set_tracking_uri(self.tracking_uri)
                mlflow.set_experiment(experiment_name)
                self._client = mlflow
                logger.info("MLflow enabled")
            except ImportError:
                logger.warning("mlflow not installed, MLflow tracking disabled")
                self.enabled = False

    def start_span(
        self,
        name: str,
        span_type: str,
        metadata: Optional[dict[str, Any]] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        if not self.enabled or not self._client:
            return ""

        # Start MLflow run
        self._active_run = self._client.start_run(
            run_name=name,
            nested=True,
        )
        span_id = self._active_run.info.run_id
        logger.debug(f"MLflow run started: {span_id}")
        return span_id

    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        if not self.enabled or not self._client:
            return

        # Log metrics and params
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (int, float)):
                    self._client.log_metric(key, value)
                elif isinstance(value, str):
                    self._client.log_param(key, value)

        # End run
        self._client.end_run()
        logger.debug(f"MLflow run ended: {span_id} ({status})")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"MLflow event: {event_name} in {span_id}")


# ============================================================================
# Unified Tracer
# ============================================================================


class UnifiedTracer:
    """
    Unified tracer for sruth pipelines.

    Sends traces to all configured backends (Datadog, Langfuse, Logfire, MLflow)
    providing comprehensive observability across the sruth ecosystem.

    Usage:
        tracer = UnifiedTracer()

        with tracer.trace_agent("curriculum_scraper"):
            results = scrape_curriculum()

        @tracer.traced("extract_metadata")
        def extract_metadata(doc):
            return extract(doc)
    """

    def __init__(
        self,
        datadog_enabled: bool = True,
        langfuse_enabled: bool = True,
        logfire_enabled: bool = True,
        mlflow_enabled: bool = False,
    ):
        """Initialize with selected backends."""
        self.backends: list[TracingBackend] = []

        if datadog_enabled:
            self.backends.append(DatadogBackend())
        if langfuse_enabled:
            self.backends.append(LangfuseBackend())
        if logfire_enabled:
            self.backends.append(LogfireBackend())
        if mlflow_enabled:
            self.backends.append(MLflowBackend())

        self._active_spans: dict[str, list[tuple[TracingBackend, str]]] = {}

        enabled_backends = [b.backend_name for b in self.backends if b.enabled]
        logger.info(f"UnifiedTracer initialized with backends: {enabled_backends}")

    @contextmanager
    def trace(
        self,
        name: str,
        span_type: str = "workflow",
        metadata: Optional[dict[str, Any]] = None,
    ) -> Generator[TraceSpan, None, None]:
        """
        Context manager for creating a trace span.

        Args:
            name: Span name
            span_type: Type of span (agent, llm, tool, workflow, asset)
            metadata: Additional metadata

        Yields:
            TraceSpan object for adding metadata during execution
        """
        span = TraceSpan(name=name, span_type=span_type, metadata=metadata or {})
        span_ids = []

        try:
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
        arguments: Optional[dict[str, Any]] = None,
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

    @contextmanager
    def trace_asset(
        self,
        asset_name: str,
        partition_key: Optional[str] = None,
        **metadata: Any,
    ) -> Generator[TraceSpan, None, None]:
        """Trace a Dagster asset execution."""
        with self.trace(
            name=asset_name,
            span_type="asset",
            metadata={"partition_key": partition_key, **metadata},
        ) as span:
            yield span

    def traced(
        self,
        name: Optional[str] = None,
        span_type: str = "workflow",
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """
        Decorator for tracing functions.

        Usage:
            @tracer.traced("my_function", span_type="tool")
            async def my_function():
                pass
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            span_name = name or func.__name__

            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                with self.trace(span_name, span_type):
                    return await func(*args, **kwargs)

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> T:
                with self.trace(span_name, span_type):
                    return func(*args, **kwargs)

            import asyncio

            if asyncio.iscoroutinefunction(func):
                return async_wrapper  # type: ignore
            return sync_wrapper  # type: ignore

        return decorator


# ============================================================================
# Factory Functions
# ============================================================================

_tracer: Optional[UnifiedTracer] = None


def get_tracer(
    datadog_enabled: bool = True,
    langfuse_enabled: bool = True,
    logfire_enabled: bool = True,
    mlflow_enabled: bool = False,
) -> UnifiedTracer:
    """Get the global UnifiedTracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = UnifiedTracer(
            datadog_enabled=datadog_enabled,
            langfuse_enabled=langfuse_enabled,
            logfire_enabled=logfire_enabled,
            mlflow_enabled=mlflow_enabled,
        )
    return _tracer


def reset_tracer() -> None:
    """Reset the global tracer (useful for testing)."""
    global _tracer
    _tracer = None


# ============================================================================
# Convenience Functions
# ============================================================================


def trace_agent_run(
    agent_name: str,
    framework: str = "unknown",
    **metadata: Any,
) -> Generator[TraceSpan, None, None]:
    """Convenience function for agent tracing."""
    return get_tracer().trace_agent(agent_name, framework, **metadata)


def trace_tool_call(
    tool_name: str,
    arguments: Optional[dict[str, Any]] = None,
    **metadata: Any,
) -> Generator[TraceSpan, None, None]:
    """Convenience function for tool tracing."""
    return get_tracer().trace_tool(tool_name, arguments, **metadata)


def trace_llm_call(
    model: str,
    prompt: Optional[str] = None,
    **metadata: Any,
) -> Generator[TraceSpan, None, None]:
    """Convenience function for LLM tracing."""
    return get_tracer().trace_llm(model, prompt, **metadata)
