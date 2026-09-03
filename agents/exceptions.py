"""Canonical exceptions + retry + graceful degradation for the agent fleet.

Replaces the 4 different error-handling patterns across the 12
main agents with a single canonical hierarchy.

Reference: openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1.
"""
from __future__ import annotations

import asyncio
import functools
import logging
from contextlib import contextmanager
from typing import Any, Awaitable, Callable, ParamSpec, TypeVar

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Canonical exception hierarchy.
# ---------------------------------------------------------------------------


class AgentError(Exception):
    """Base class for all agent-fleet exceptions.

    All agent-level errors SHALL subclass this. The fleet
    contract guarantees that no agent SHALL propagate a
    non-AgentError exception during routine operation —
    all non-AgentError exceptions are converted at the
    wire boundary.
    """

    def __init__(
        self, message: str, *, agent_name: str | None = None
    ) -> None:
        super().__init__(message)
        self.agent_name = agent_name


class AgentConfigError(AgentError):
    """Configuration error (missing dep, invalid path, etc.)."""


class AgentRuntimeError(AgentError):
    """Runtime error during agent execution."""


class AgentTimeoutError(AgentError):
    """Agent execution timed out."""


class AgentMemoryError(AgentError):
    """Memory backend error (Cognee/Graphiti/LanceDB/FalkorDB/Memgraph)."""


class AgentObservabilityError(AgentError):
    """Observability backend error (Langfuse/Logfire/MLflow/RAGAS/structlog)."""


class AgentDependencyMissingError(AgentConfigError):
    """A required dependency is missing (e.g. langfuse not installed).

    This exception is raised by the wire-up layer when a
    dependency is missing but the agent can still be used
    in degraded mode. The wire-up layer catches this and
    returns a no-op wire.
    """


# ---------------------------------------------------------------------------
# with_retry decorator: exponential backoff for transient failures.
# ---------------------------------------------------------------------------


P = ParamSpec("P")
T = TypeVar("T")


def with_retry(
    *,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    exceptions: tuple[type[BaseException], ...] = (AgentRuntimeError,),
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Retry decorator with exponential backoff.

    Re-raises after ``max_attempts`` failed attempts. The delay
    between attempts doubles each time (capped at ``max_delay``).
    Only retries on the specified exception types; other
    exceptions propagate immediately.

    Example::

        @with_retry(max_attempts=3, exceptions=(AgentRuntimeError,))
        async def call_agent(...):
            ...
    """

    def decorator(
        func: Callable[P, Awaitable[T]],
    ) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            delay = base_delay
            last_exc: BaseException | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        logger.warning(
                            "with_retry(%s): exhausted %d attempts: %s",
                            getattr(func, "__name__", "?"),
                            max_attempts,
                            exc,
                        )
                        break
                    logger.debug(
                        "with_retry(%s): attempt %d/%d failed (%s); "
                        "sleeping %.2fs",
                        getattr(func, "__name__", "?"),
                        attempt,
                        max_attempts,
                        exc,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# graceful_degradation context manager: never propagate on missing dep.
# ---------------------------------------------------------------------------


@contextmanager
def graceful_degradation(
    *,
    on_missing: Callable[[Exception], Any] | None = None,
    fallback: Any = None,
):
    """Context manager that swallows dependency-missing exceptions.

    Used by agent modules that wrap optional dependencies
    (Langfuse, Logfire, MLflow, RAGAS, structlog, Cognee, Graphiti,
    LanceDB, FalkorDB, Memgraph, Letta). When the dep is missing,
    the block runs to completion but the ``on_missing`` callback
    (or the default ``fallback`` value) is returned.

    Example::

        with graceful_degradation(fallback=None) as ctx:
            client = get_langfuse_client()
            if client is None:
                ctx.set_missing(ImportError("langfuse not installed"))
            ...
    """
    missing_exc: Exception | None = None

    class _Ctx:
        def set_missing(self, exc: Exception) -> None:
            nonlocal missing_exc
            missing_exc = exc

    ctx = _Ctx()
    try:
        yield ctx
    except (ImportError, ModuleNotFoundError) as exc:
        missing_exc = exc
        logger.debug(
            "graceful_degradation(): swallowed %s: %s",
            type(exc).__name__,
            exc,
        )
    except Exception as exc:  # noqa: BLE001
        if on_missing is not None:
            return on_missing(exc)
        raise

    if missing_exc is not None:
        if on_missing is not None:
            return on_missing(missing_exc)
        return fallback


__all__ = [
    "AgentConfigError",
    "AgentDependencyMissingError",
    "AgentError",
    "AgentMemoryError",
    "AgentObservabilityError",
    "AgentRuntimeError",
    "AgentTimeoutError",
    "graceful_degradation",
    "with_retry",
]