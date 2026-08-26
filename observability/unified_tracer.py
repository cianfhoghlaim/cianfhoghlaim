"""
Unified Tracer for sruth data pipelines.

Provides tracing and metrics across multiple backends:
- Datadog LLMObs: Agent traces, token usage, cost tracking
- Langfuse: Prompt management, A/B testing, trace analysis
- Logfire: Pydantic AI specific tracing

This module provides a unified interface for instrumenting agents,
LLM calls, and MCP tool invocations.

Note: Migrated from sruth/aleyum/_shared/observability/tracing.py
"""

import logging
import os
from abc import ABC, abstractmethod
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class TraceSpan:
    """Represents a trace span across all backends."""

    name: str
    span_type: str  # "agent", "llm", "tool", "workflow"
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_id: str | None = None
    span_id: str = ""
    status: str = "running"  # running, completed, error
    error: str | None = None

    def complete(self, status: str = "completed") -> None:
        """Mark span as complete."""
        self.end_time = datetime.now()
        self.status = status

    @property
    def duration_ms(self) -> float | None:
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
        metadata: dict[str, Any] | None = None,
        parent_id: str | None = None,
    ) -> str:
        """Start a new span, return span ID."""
        pass

    @abstractmethod
    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        """End a span."""
        pass

    @abstractmethod
    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Log an event within a span."""
        pass


class DatadogBackend(TracingBackend):
    """Datadog LLMObs integration."""

    def __init__(self, api_key: str | None = None):
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
        metadata: dict[str, Any] | None = None,
        parent_id: str | None = None,
    ) -> str:
        if not self.enabled or not self._llmobs:
            return ""

        span_kind_map = {
            "agent": "agent",
            "llm": "llm",
            "tool": "tool",
            "workflow": "workflow",
        }

        span_kind_map.get(span_type, "task")
        span_id = f"dd_{name}_{datetime.now().isoformat()}"
        logger.debug(f"Datadog span started: {span_id}")
        return span_id

    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Datadog span ended: {span_id} ({status})")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Datadog event: {event_name} in {span_id}")


class LangfuseBackend(TracingBackend):
    """Langfuse integration for prompt management and tracing."""

    def __init__(
        self,
        public_key: str | None = None,
        secret_key: str | None = None,
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
        metadata: dict[str, Any] | None = None,
        parent_id: str | None = None,
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
        metadata: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Langfuse span ended: {span_id} ({status})")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Langfuse event: {event_name} in {span_id}")


class LogfireBackend(TracingBackend):
    """Logfire integration for Pydantic AI tracing."""

    def __init__(self, token: str | None = None):
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
        metadata: dict[str, Any] | None = None,
        parent_id: str | None = None,
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
        metadata: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Logfire span ended: {span_id} ({status})")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        if not self.enabled:
            return
        logger.debug(f"Logfire event: {event_name} in {span_id}")


# ─── OpenTelemetry semantic-convention helpers (Wave 7) ──────────────────────

def apply_otel_semantic_conventions(
    span: "TraceSpan",
    kind: str,
) -> None:
    """Tag a `TraceSpan` with the canonical OpenTelemetry semantic
    conventions per `https://opentelemetry.io/docs/specs/semconv/`.

    Per Wave 7 of the 2026-08-24 master refactor plan. Three families
    are applied based on the `kind` of span:

    - `db.system: duckdb`            — for spans that touch the
      dlt + Convex + DuckLake stack (any database operation)
    - `gen_ai.system: baml`           — for spans that invoke the BAML
      extraction runtime
    - `object_store.system: s3`       — for spans that read/write
      Garage S3 or MinIO S3-compatible storage

    Args:
        span: The `TraceSpan` to tag (mutated in place).
        kind: The span kind — one of `db`, `gen_ai`, `object_store`.
    """
    if kind == "db":
        span.metadata["db.system"] = "duckdb"
    elif kind == "gen_ai":
        span.metadata["gen_ai.system"] = "baml"
    elif kind == "object_store":
        span.metadata["object_store.system"] = "s3"
    else:
        # Unknown kind — don't tag (per OTel spec, only valid values
        # should be used)
        logger.debug(f"apply_otel_semantic_conventions: unknown kind={kind!r}")


class MlflowBackend(TracingBackend):
    """MLflow integration for local tracing (the Wave 7 v0 straggler).

    Per the `docs/lakehouse-otel-fanout.md` stack spec, MLflow v3.15.1
    is the canonical local-tracing sink. MLflow supports OpenTelemetry
    natively via `mlflow.tracing`.

    Args:
        tracking_uri: MLflow tracking URI (e.g. `http://mlflow:5000`
            or `sqlite:///stedding/mlflow.db` for local dev).
        experiment_name: MLflow experiment name. Default: `cianfhoghlaim`.
    """

    def __init__(
        self,
        tracking_uri: str | None = None,
        experiment_name: str = "cianfhoghlaim",
    ):
        self.tracking_uri = tracking_uri or os.environ.get(
            "MLFLOW_TRACKING_URI", "sqlite:///stedding/mlflow.db",
        )
        self.experiment_name = experiment_name
        self.enabled = bool(self.tracking_uri)
        self._client = None

        if self.enabled:
            try:
                import mlflow

                mlflow.set_tracking_uri(self.tracking_uri)
                mlflow.set_experiment(self.experiment_name)
                self._client = mlflow
                logger.info(
                    f"Mlflow enabled: tracking_uri={self.tracking_uri} "
                    f"experiment={self.experiment_name}",
                )
            except ImportError:
                logger.warning("mlflow not installed, Mlflow tracing disabled")
                self.enabled = False

    def start_span(
        self,
        name: str,
        span_type: str,
        metadata: dict[str, Any] | None = None,
        parent_id: str | None = None,
    ) -> str:
        if not self.enabled or not self._client:
            return ""

        try:
            span = self._client.start_span(name=name)
            span.set_tag("span_type", span_type)
            if metadata:
                for k, v in metadata.items():
                    span.set_tag(k, str(v))
            span_id = f"mlf_{name}_{span.span_id}"
            logger.debug(f"Mlflow span started: {span_id}")
            return span_id
        except Exception as exc:
            logger.warning(f"Mlflow start_span failed: {exc}")
            return ""

    def end_span(
        self,
        span_id: str,
        status: str = "completed",
        metadata: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> None:
        if not self.enabled or not self._client:
            return

        try:
            # Mlflow tracks the active span internally; end it via the
            # mlflow.tracing context manager (per the mlflow 3.x API).
            self._client.end_span(status=status)
        except Exception as exc:
            logger.warning(f"Mlflow end_span failed: {exc}")

    def log_event(
        self,
        span_id: str,
        event_name: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        if not self.enabled:
            return

        try:
            self._client.log_metric(
                run_id=span_id,
                key=f"event.{event_name}",
                value=1.0,
            )
            logger.debug(f"Mlflow event: {event_name} in {span_id}")
        except Exception as exc:
            logger.warning(f"Mlflow log_event failed: {exc}")


class UnifiedTracer:
    """
    Unified tracer for sruth agents and workflows.

    Sends traces to all configured backends (Datadog, Langfuse, Logfire)
    providing comprehensive observability across the pipeline ecosystem.

    Usage:
        tracer = UnifiedTracer()

        with tracer.trace_agent("code_analyzer", framework="adk"):
            with tracer.trace_tool("codeolas_search", {"query": "async"}):
                # Tool execution
                pass

        # Or with decorators:
        @tracer.traced("my_function", span_type="tool")
        async def my_function():
            pass
    """

    def __init__(
        self,
        datadog_enabled: bool = False,
        langfuse_enabled: bool = True,
        logfire_enabled: bool = True,
        mlflow_enabled: bool = True,
    ):
        """Initialize with selected backends.

        Args:
            datadog_enabled: Enable Datadog LLMObs backend (Wave 0).
            langfuse_enabled: Enable Langfuse backend (Wave 0).
            logfire_enabled: Enable Logfire backend (Wave 0).
            mlflow_enabled: Enable MLflow backend (Wave 7 — NEW).
        """
        self.backends: list[TracingBackend] = []

        if datadog_enabled:
            self.backends.append(DatadogBackend())
        if langfuse_enabled:
            self.backends.append(LangfuseBackend())
        if logfire_enabled:
            self.backends.append(LogfireBackend())
        if mlflow_enabled:
            self.backends.append(MlflowBackend())

        self._active_spans: dict[str, list[str]] = {}

        enabled_backends = [b.__class__.__name__ for b in self.backends if b.enabled]
        logger.info(f"UnifiedTracer initialized with backends: {enabled_backends}")

    @contextmanager
    def trace(
        self,
        name: str,
        span_type: str = "workflow",
        metadata: dict[str, Any] | None = None,
    ) -> Generator[TraceSpan]:
        """
        Context manager for creating a trace span.

        Args:
            name: Span name
            span_type: Type of span (agent, llm, tool, workflow)
            metadata: Additional metadata

        Yields:
            TraceSpan object for adding metadata during execution
        """
        # Wave 7: apply OpenTelemetry semantic conventions based on
        # the span_type (db → db.system:duckdb; llm → gen_ai.system:baml;
        # tool/workflow that touches s3 → object_store.system:s3).
        otel_kind_map = {
            "db": "db",
            "llm": "gen_ai",
            "tool": "object_store",  # tools often touch S3 for documents
        }
        otel_kind = otel_kind_map.get(span_type)

        span = TraceSpan(name=name, span_type=span_type, metadata=metadata or {})
        if otel_kind is not None:
            apply_otel_semantic_conventions(span, otel_kind)
        span_ids = []

        try:
            for backend in self.backends:
                span_id = backend.start_span(name, span_type, span.metadata)
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
    ) -> Generator[TraceSpan]:
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
        arguments: dict[str, Any] | None = None,
        **metadata: Any,
    ) -> Generator[TraceSpan]:
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
        prompt: str | None = None,
        **metadata: Any,
    ) -> Generator[TraceSpan]:
        """Trace an LLM call."""
        with self.trace(
            name=model,
            span_type="llm",
            metadata={"prompt_length": len(prompt) if prompt else 0, **metadata},
        ) as span:
            yield span

    def traced(
        self,
        name: str | None = None,
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


# Global tracer instance
_tracer: UnifiedTracer | None = None


def get_tracer() -> UnifiedTracer:
    """Get the global UnifiedTracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = UnifiedTracer()
    return _tracer


# Convenience context managers
def trace_agent_run(
    agent_name: str, framework: str = "unknown", **metadata: Any
) -> Generator[TraceSpan]:
    """Convenience function for agent tracing."""
    return get_tracer().trace_agent(agent_name, framework, **metadata)


def trace_tool_call(
    tool_name: str, arguments: dict[str, Any] | None = None, **metadata: Any
) -> Generator[TraceSpan]:
    """Convenience function for tool tracing."""
    return get_tracer().trace_tool(tool_name, arguments, **metadata)
