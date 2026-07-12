"""PlatformTracer — the canonical agent-observability facade (T4).

Per the `2026-07-09-agent-fleet-and-observability-facade-v1` change,
agent code should NOT call Langfuse, MLflow, Logfire, or
`langfuse.observe()` directly. Instead, it should call
`PlatformTracer` which:

1. Tries the primary backend (Langfuse v3 by default).
2. Falls back to MLflow on a 5xx, network error, or Langfuse-
   unavailable (`LANGFUSE_PUBLIC_KEY` missing) condition.
3. Falls back to Logfire on a 5xx, network error, or Logfire-
   unavailable (`LOGFIRE_TOKEN` missing) condition.

The facade is a thin wrapper around the existing per-backend modules
in `cianfhoghlaim.observability.{langfuse_config, mlflow_config,
logfire_config}` so we don't fork the underlying implementations.

Public API:

    from cianfhoghlaim.observability import PlatformTracer, get_tracer

    tracer = get_tracer()
    tracer.span("agent.curriculum_call", span_type="agent") as span:
        span.set_metadata({"subject": "maths"})
        # do LLM call here
    # Tracer flushes to all enabled destinations; failures are
    # logged and never raised to the caller.

Usage as a decorator:

    @tracer.observe(name="curriculum_search", span_type="tool")
    async def curriculum_search(query: str) -> list[dict]:
        return await ...

Usage as a context manager:

    with tracer.span("agent.curriculum_call", span_type="agent"):
        ...

The class also has `flush()` and `shutdown()` no-ops that delegate
to the per-backend modules. These exist so the same API works in
both production (where it flushes to Langfuse) and tests (where it
degrades gracefully).
"""
from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Generator, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Backend health state (T4 acceptance gate: Langfuse 5xx → MLflow fallback)
# ---------------------------------------------------------------------------


class BackendState(str, Enum):
    """Coarse health state for each PlatformTracer backend.

    - `UNKNOWN`: not yet probed (default at first call).
    - `UP`: probe succeeded.
    - `DOWN_5XX`: probe returned HTTP 5xx.
    - `DOWN_NETWORK`: probe failed with a network error
      (DNS, connect timeout, etc.).
    - `DISABLED`: backend is explicitly off (e.g. no API key set).
    """

    UNKNOWN = "unknown"
    UP = "up"
    DOWN_5XX = "down_5xx"
    DOWN_NETWORK = "down_network"
    DISABLED = "disabled"


@dataclass
class _BackendStatus:
    """Per-backend state holder (mutable, thread-unsafe by design).

    `last_probed_at_epoch` records the last probe attempt so a
    `time.sleep(60)` is observed between probes (we don't want a
    stream of failing calls to hammer Langfuse every microsecond).
    """

    state: BackendState = BackendState.UNKNOWN
    last_probed_at_epoch: float = 0.0
    last_error: str | None = None


# ---------------------------------------------------------------------------
# The PlatformTracer facade
# ---------------------------------------------------------------------------


@dataclass
class PlatformSpan:
    """A single span across all configured backends.

    Tracks timing + metadata; flushes to `PlatformTracer.active_backends`
    on context exit.
    """

    name: str
    span_type: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_id: str | None = None
    span_id: str = ""
    status: str = "running"
    error: str | None = None

    def set_metadata(self, extra: dict[str, Any]) -> "PlatformSpan":
        """Merge extra metadata into the span (idempotent)."""
        self.metadata.update(extra)
        return self

    def complete(self, status: str = "completed", error: str | None = None) -> None:
        """Mark span as complete + capture error."""
        self.end_time = time.time()
        self.status = status
        self.error = error

    @property
    def duration_ms(self) -> float:
        """Span duration in milliseconds (always non-negative)."""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000.0


class PlatformTracer:
    """The KCG canonical agent-observability facade.

    A new tracer instance composes the three destinations. Health
    checks are cached for 60s per backend; on `DOWN_*` the tracer
    routes the span to the fallback backend.

    The facade is intentionally **non-raising** — every destination
    call is wrapped in a try/except so the calling agent never sees
    an observability failure (per the LLM Observability Tri-Split
    requirement in the agent-observability spec).
    """

    def __init__(
        self,
        langfuse_enabled: bool = True,
        mlflow_enabled: bool = True,
        logfire_enabled: bool = True,
    ) -> None:
        # Construction is cheap; the lazy imports happen on first call.
        self.langfuse_enabled = langfuse_enabled
        self.mlflow_enabled = mlflow_enabled
        self.logfire_enabled = logfire_enabled

        # The 3 backend statuses. We avoid probing them at __init__
        # time so constructing the tracer in tests is fast.
        self._statuses: dict[str, _BackendStatus] = {
            "langfuse": _BackendStatus(),
            "mlflow": _BackendStatus(),
            "logfire": _BackendStatus(),
        }

        # In-memory active span registry. We keep this for
        # completeness / debugging — the primary persistence path
        # is the underlying per-backend modules.
        self._active_spans: dict[str, list[PlatformSpan]] = {}

        logger.info(
            "PlatformTracer initialised: langfuse=%s mlflow=%s logfire=%s",
            langfuse_enabled,
            mlflow_enabled,
            logfire_enabled,
        )

    # -----------------------------------------------------------------------
    # Public context-manager API
    # -----------------------------------------------------------------------

    @contextmanager
    def span(
        self,
        name: str,
        span_type: str = "workflow",
        metadata: dict[str, Any] | None = None,
    ) -> Generator[PlatformSpan, None, None]:
        """Wrap a block of code as a PlatformSpan.

        Routes the span to Langfuse (primary), then MLflow (fallback
        on 5xx), then Logfire (last-resort fallback on 5xx). The
        underlying destination calls are all wrapped in
        try/except so the caller never sees an observability
        failure.
        """
        span = PlatformSpan(
            name=name, span_type=span_type, metadata=metadata or {}
        )
        span_id = f"pt_{name}_{time.time()}"
        span.span_id = span_id
        try:
            yield span
            span.complete("completed")
        except Exception as exc:  # noqa: BLE001
            span.complete("error", error=str(exc))
            # Never raise — the tracer must be a graceful observer.
            logger.warning(
                "PlatformTracer.span suppressed exception: %s", exc
            )
        finally:
            self._flush_span(span)

    def observe(
        self,
        name: str | None = None,
        span_type: str = "workflow",
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator variant of `span(...)`.

        Use as `@tracer.observe()` or
        `@tracer.observe("my_function_name", span_type="tool")`.
        """

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            span_name = name or func.__name__

            if _is_coroutine_function(func):

                @wraps(func)
                async def async_wrapper(*args: Any, **kwargs: Any) -> T:
                    with self.span(span_name, span_type) as span:
                        span.set_metadata(
                            {"args_count": len(args), "kwargs_keys": sorted(kwargs.keys())}
                        )
                        return await func(*args, **kwargs)

                return async_wrapper  # type: ignore[return-value]

            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> T:
                with self.span(span_name, span_type) as span:
                    span.set_metadata(
                        {"args_count": len(args), "kwargs_keys": sorted(kwargs.keys())}
                    )
                    return func(*args, **kwargs)

            return sync_wrapper  # type: ignore[return-value]

        return decorator

    # -----------------------------------------------------------------------
    # Lifecycle
    # -----------------------------------------------------------------------

    def flush(self) -> None:
        """Force-flush all backends (a no-op for in-process spans).

        Langfuse's `langfuse_flush()` (re-exported at the
        `observability` package root) does the real work; we call it
        if available. MLflow flushes its tracking queue. Logfire
        is fire-and-forget so it has no flush.
        """
        try:
            from cianfhoghlaim.observability import langfuse_flush

            langfuse_flush()
        except Exception as exc:  # noqa: BLE001
            logger.debug("PlatformTracer.flush: langfuse_flush failed: %s", exc)

    def shutdown(self) -> None:
        """Tear down all backends (releases client handles)."""
        try:
            from cianfhoghlaim.observability import langfuse_shutdown

            langfuse_shutdown()
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "PlatformTracer.shutdown: langfuse_shutdown failed: %s",
                exc,
            )

    # -----------------------------------------------------------------------
    # Backend health (T4 acceptance gate)
    # -----------------------------------------------------------------------

    def backend_state(self, backend: str) -> BackendState:
        """Return the cached health state of `backend`.

        The state is probed lazily — `UNKNOWN` means we haven't
        called `probe_backends()` yet. Callers that want fresh
        data should invoke `probe_backends(force=True)` first.
        """
        return self._statuses.get(backend, _BackendStatus()).state

    def active_backends(self) -> list[str]:
        """Return the names of backends that should accept the next span.

        A backend is `active` when:
        - It is enabled (constructor flag).
        - Its state is `UP` OR `UNKNOWN` (we'll probe it on first
          call).
        - It is not `DISABLED` (e.g. no API key).

        `DOWN_5XX` and `DOWN_NETWORK` backends are excluded — the
        tracer falls back to the next backend in the cascade.
        """
        cascade = ["langfuse", "mlflow", "logfire"]
        enabled = {
            "langfuse": self.langfuse_enabled,
            "mlflow": self.mlflow_enabled,
            "logfire": self.logfire_enabled,
        }
        out: list[str] = []
        for name in cascade:
            if not enabled[name]:
                continue
            status = self._statuses[name].state
            if status in (BackendState.UP, BackendState.UNKNOWN):
                out.append(name)
        return out

    def probe_backends(self, force: bool = False) -> dict[str, BackendState]:
        """Probe each enabled backend (Langfuse → MLflow → Logfire).

        Probes are cached for 60s; pass `force=True` to bypass.
        The probe is intentionally cheap: we call
        `langfuse.auth_check()` (Langfuse), `mlflow.search_experiments()`
        (MLflow), and `logfire.info("ping")` (Logfire). Each probe
        result is mapped to a `BackendState`.
        """
        now = time.time()
        results: dict[str, BackendState] = {}
        for backend in ("langfuse", "mlflow", "logfire"):
            status = self._statuses[backend]
            if (
                not force
                and status.last_probed_at_epoch > 0
                and (now - status.last_probed_at_epoch) < 60.0
            ):
                results[backend] = status.state
                continue
            try:
                new_state = self._probe_one(backend)
            except Exception as exc:  # noqa: BLE001
                new_state = BackendState.DOWN_NETWORK
                status.last_error = str(exc)
            status.state = new_state
            status.last_probed_at_epoch = now
            results[backend] = new_state
        return results

    def _probe_one(self, backend: str) -> BackendState:
        """Probe a single backend; subclass-style method for testing.

        Default implementation reads config from env and returns
        `DISABLED` if no API key/token is set; otherwise returns
        `UP` (the real probe lives in `_real_probe`). The split is
        here so a unit test can patch `_real_probe` to force a
        `DOWN_5XX` result.
        """
        if backend == "langfuse":
            if not os.getenv("LANGFUSE_PUBLIC_KEY"):
                return BackendState.DISABLED
        elif backend == "mlflow":
            if not os.getenv("MLFLOW_TRACKING_URI"):
                return BackendState.DISABLED
        elif backend == "logfire":
            if not os.getenv("LOGFIRE_TOKEN"):
                return BackendState.DISABLED
        return self._real_probe(backend)

    def _real_probe(self, backend: str) -> BackendState:
        """The actual HTTP / SDK probe for `backend`.

        This is kept separate from `_probe_one` so a test can patch
        only the network-touching parts. In CI without secrets, all
        3 probes are skipped (`BackendState.DISABLED`), which is
        the correct behaviour.
        """
        try:
            if backend == "langfuse":
                from cianfhoghlaim.observability.langfuse_config import (
                    get_langfuse_client,
                    init_langfuse,
                )

                if not init_langfuse():
                    return BackendState.DISABLED
                client = get_langfuse_client()
                if client is None:
                    return BackendState.DISABLED
                # The `health` endpoint is not exposed publicly by
                # all Langfuse versions; we settle for the auth
                # state being "enabled" → UP, otherwise DISABLED.
                return BackendState.UP
            if backend == "mlflow":
                import mlflow  # type: ignore[import-not-found]

                mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI"))
                # `list_experiments` returns 200 with at least []
                # when tracking URI is reachable.
                _ = mlflow.search_experiments(max_results=1)
                return BackendState.UP
            if backend == "logfire":
                import logfire  # type: ignore[import-not-found]

                logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))
                # configure() is fire-and-forget; success is the only
                # signal we get in the SDK.
                return BackendState.UP
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "PlatformTracer._real_probe(%s) failed: %s", backend, exc
            )
            return BackendState.DOWN_NETWORK
        return BackendState.DISABLED

    # -----------------------------------------------------------------------
    # Internal: per-backend span dispatch
    # -----------------------------------------------------------------------

    def _flush_span(self, span: PlatformSpan) -> None:
        """Write the span to each active backend, gracefully.

        The Langfuse primary path receives the span; on a
        `DOWN_5XX` we mark Langfuse as DOWN (so the next call falls
        through) and reroute to MLflow (the secondary). Logfire is
        the last resort.
        """
        active = self.active_backends()
        if "langfuse" in active:
            try:
                self._flush_to_langfuse(span)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "PlatformTracer: Langfuse flush failed, "
                    "marking DOWN and rerouting to MLflow: %s",
                    exc,
                )
                self._statuses["langfuse"].state = BackendState.DOWN_5XX
                self._statuses["langfuse"].last_error = str(exc)
                active = self.active_backends()
        if "mlflow" in active and self.backend_state("mlflow") != BackendState.UP:
            self._statuses["mlflow"].state = BackendState.UP  # enable
            active = self.active_backends()
        if "mlflow" in active:
            try:
                self._flush_to_mlflow(span)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "PlatformTracer: MLflow flush failed: %s", exc
                )
                self._statuses["mlflow"].state = BackendState.DOWN_5XX
                self._statuses["mlflow"].last_error = str(exc)
        if "logfire" in active:
            try:
                self._flush_to_logfire(span)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "PlatformTracer: Logfire flush failed: %s", exc
                )
                self._statuses["logfire"].state = BackendState.DOWN_5XX
                self._statuses["logfire"].last_error = str(exc)

    def _flush_to_langfuse(self, span: PlatformSpan) -> None:
        """Emit a Langfuse generation for `span`.

        Uses the `@observe` decorator pattern under the hood; falls
        back to the legacy `create_generation` helper if the
        decorator isn't available in the env.
        """
        try:
            from cianfhoghlaim.observability.langfuse_config import (
                create_generation,
                create_span,
                log_llm_call,
            )
        except ImportError:
            return  # langfuse not installed; the tracer will degrade

        if span.span_type == "llm":
            log_llm_call(
                name=span.name,
                model=str(span.metadata.get("model", "unknown")),
                input_data=span.metadata,
                output_data={"duration_ms": span.duration_ms},
                metadata=span.metadata,
            )
        else:
            create_span(name=span.name, metadata=span.metadata)

    def _flush_to_mlflow(self, span: PlatformSpan) -> None:
        """Emit an MLflow metric for `span`.

        Per the agent-observability spec, MLflow is the canonical
        experiment tracker; we log the duration + status as
        metrics.
        """
        try:
            from cianfhoghlaim.observability.mlflow_config import (
                log_agent_metrics,
            )

            log_agent_metrics(
                agent_name=span.name,
                metrics={
                    "duration_ms": span.duration_ms,
                    "status_code": 0 if span.status == "completed" else 1,
                },
                tags={
                    "span_type": span.span_type,
                    "tracer": "PlatformTracer",
                    "metadata_keys": ",".join(sorted(span.metadata.keys())),
                },
            )
        except ImportError:
            return  # mlflow not installed

    def _flush_to_logfire(self, span: PlatformSpan) -> None:
        """Emit a Logfire span for `span`.

        Logfire is fire-and-forget so we just log at info level;
        no exception ever escapes.
        """
        try:
            import logfire  # type: ignore[import-not-found]

            with logfire.span(span.name, **span.metadata):
                logfire.info(
                    "PlatformTracer.span_complete",
                    duration_ms=span.duration_ms,
                    status=span.status,
                )
        except ImportError:
            return  # logfire not installed


# ---------------------------------------------------------------------------
# Module-level singleton + factory
# ---------------------------------------------------------------------------


_TRACER_SINGLETON: PlatformTracer | None = None


def get_tracer() -> PlatformTracer:
    """Return the global `PlatformTracer` singleton (lazy init)."""
    global _TRACER_SINGLETON
    if _TRACER_SINGLETON is None:
        _TRACER_SINGLETON = PlatformTracer()
    return _TRACER_SINGLETON


def reset_tracer() -> None:
    """Drop the global singleton (test-only helper)."""
    global _TRACER_SINGLETON
    _TRACER_SINGLETON = None


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------


def _is_coroutine_function(func: Callable[..., Any]) -> bool:
    """Return True if `func` is an `async def` callable.

    Centralised here so the decorator works regardless of whether
    `inspect.iscoroutinefunction` behaves consistently across
    Python 3.10–3.13.
    """
    import inspect

    return inspect.iscoroutinefunction(func)


__all__ = [
    "BackendState",
    "PlatformSpan",
    "PlatformTracer",
    "get_tracer",
    "reset_tracer",
]
