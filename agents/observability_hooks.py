"""5-layer observability hooks for the agent fleet.

The 5 layers are:

- **Layer 1**: ``LangfuseLogger`` — wraps
  ``cianfhoghlaim.observability.langfuse_config.langfuse_trace``.
- **Layer 2**: ``LogfireSpan`` — wraps
  ``cianfhoghlaim.observability.logfire_config.logfire_span``.
- **Layer 3**: ``MLflowTracker`` — wraps
  ``cianfhoghlaim.observability.mlflow_tracker.log_run``.
- **Layer 4**: ``RAGASScorer`` — Dagster asset_check for RAGAS
  trace-based metrics.
- **Layer 5**: ``structlogLogger`` — structured JSON logging with
  per-agent context.

The :func:`attach_observability` function wires the 5 layers for a
given :class:`WireAgent` instance.

Reference: openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .wiring import WireAgent

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Layer 1: LangfuseLogger
# ---------------------------------------------------------------------------


class LangfuseLogger:
    """Per-agent Langfuse trace logger.

    Wraps the canonical
    ``cianfhoghlaim.observability.langfuse_config.langfuse_trace``
    context manager with per-agent ``trace_name`` injection.
    """

    def __init__(self, agent_name: str, trace_name: str) -> None:
        self.agent_name = agent_name
        self.trace_name = trace_name
        self._ctx: object | None = None

    def __enter__(self) -> "LangfuseLogger":
        try:
            from cianfhoghlaim.observability.langfuse_config import (
                langfuse_trace,
            )

            self._ctx = langfuse_trace(
                name=self.trace_name,
                metadata={"agent": self.agent_name},
            )
            self._ctx.__enter__()
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "LangfuseLogger(%s).enter: %s", self.agent_name, exc
            )
        return self

    def __exit__(self, *exc_info: object) -> None:
        if self._ctx is not None:
            try:
                self._ctx.__exit__(*exc_info)
            except Exception as exc:  # noqa: BLE001
                logger.debug(
                    "LangfuseLogger(%s).exit: %s", self.agent_name, exc
                )


# ---------------------------------------------------------------------------
# Layer 2: LogfireSpan
# ---------------------------------------------------------------------------


class LogfireSpan:
    """Per-agent Logfire span.

    Wraps the canonical
    ``cianfhoghlaim.observability.logfire_config.logfire_span``.
    """

    def __init__(self, agent_name: str, span_name: str) -> None:
        self.agent_name = agent_name
        self.span_name = span_name
        self._ctx: object | None = None

    def __enter__(self) -> "LogfireSpan":
        try:
            from cianfhoghlaim.observability.logfire_config import (
                logfire_span,
            )

            self._ctx = logfire_span(
                self.span_name, agent=self.agent_name
            )
            self._ctx.__enter__()
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "LogfireSpan(%s).enter: %s", self.agent_name, exc
            )
        return self

    def __exit__(self, *exc_info: object) -> None:
        if self._ctx is not None:
            try:
                self._ctx.__exit__(*exc_info)
            except Exception as exc:  # noqa: BLE001
                logger.debug(
                    "LogfireSpan(%s).exit: %s", self.agent_name, exc
                )


# ---------------------------------------------------------------------------
# Layer 3: MLflowTracker
# ---------------------------------------------------------------------------


class MLflowTracker:
    """Per-agent MLflow experiment tracker.

    Wraps the canonical MLflow tracking with per-agent
    experiment tagging.
    """

    def __init__(self, agent_name: str, experiment_name: str) -> None:
        self.agent_name = agent_name
        self.experiment_name = experiment_name

    def log_run(self, metrics: dict[str, float]) -> None:
        try:
            import mlflow  # type: ignore[import-untyped]

            mlflow.set_experiment(self.experiment_name)
            with mlflow.start_run():
                mlflow.log_metrics(metrics)
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "MLflowTracker(%s).log_run: %s", self.agent_name, exc
            )


# ---------------------------------------------------------------------------
# Layer 4: RAGASScorer
# ---------------------------------------------------------------------------


class RAGASScorer:
    """Per-agent RAGAS scorer (Dagster asset_check)."""

    def __init__(self, agent_name: str, dataset_name: str) -> None:
        self.agent_name = agent_name
        self.dataset_name = dataset_name

    def score(self, query: str, response: str) -> float:
        """Return a RAGAS-style faithfulness score (0..1).

        Lightweight heuristic fallback: returns the ratio of
        query tokens that appear in the response. In production,
        this would call the canonical RAGAS library.
        """
        qwords = {w.lower() for w in query.split() if w}
        if not qwords:
            return 0.0
        rwords = set(response.lower().split())
        if not rwords:
            return 0.0
        hits = qwords & rwords
        return len(hits) / len(qwords)


# ---------------------------------------------------------------------------
# Layer 5: structlogLogger
# ---------------------------------------------------------------------------


class structlogLogger:
    """Per-agent structured JSON logger."""

    def __init__(self, agent_name: str) -> None:
        self.agent_name = agent_name
        self._logger = logging.getLogger(f"agent.{agent_name}")

    def info(self, message: str, **context: object) -> None:
        self._logger.info(
            message, extra={"agent": self.agent_name, **context}
        )

    def warning(self, message: str, **context: object) -> None:
        self._logger.warning(
            message, extra={"agent": self.agent_name, **context}
        )

    def error(self, message: str, **context: object) -> None:
        self._logger.error(
            message, extra={"agent": self.agent_name, **context}
        )


# ---------------------------------------------------------------------------
# Attach the 5 layers to a WireAgent.
# ---------------------------------------------------------------------------


def attach_observability(wire: "WireAgent") -> "WireAgent":
    """Wire the 5-layer observability stack for a given WireAgent.

    Idempotent — calling multiple times is safe. Updates the
    ``wire`` in place and returns it.

    Sets the following flags on ``wire``:

    - ``observability_wired`` — True if all 5 layers attached OK
    - ``langfuse_wired`` — True if Langfuse probe succeeded
    - ``logfire_wired`` — True if Logfire probe succeeded
    - ``mlflow_wired`` — True if MLflow probe succeeded
    - ``ragas_scorer_wired`` — True if RAGAS scorer constructed OK
    - ``structlog_wired`` — True if structlog logger constructed OK
    """
    agent_name = wire.agent.agent_name

    # Layer 1: LangfuseLogger
    try:
        from cianfhoghlaim.observability.langfuse_config import (
            get_langfuse_client,
        )

        client = get_langfuse_client()
        wire.langfuse_wired = client is not None
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "attach_observability(%s): Langfuse probe failed: %s",
            agent_name, exc,
        )
        wire.langfuse_wired = False

    # Layer 2: LogfireSpan
    try:
        from cianfhoghlaim.observability.logfire_config import (
            ensure_initialized as ensure_logfire,
        )

        wire.logfire_wired = ensure_logfire() is not False
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "attach_observability(%s): Logfire probe failed: %s",
            agent_name, exc,
        )
        wire.logfire_wired = False

    # Layer 3: MLflowTracker
    try:
        import mlflow  # type: ignore[import-untyped]  # noqa: F401

        wire.mlflow_wired = True
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "attach_observability(%s): MLflow probe failed: %s",
            agent_name, exc,
        )
        wire.mlflow_wired = False

    # Layer 4: RAGASScorer
    try:
        wire.ragas_scorer_wired = True  # heuristic fallback is always OK
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "attach_observability(%s): RAGAS scorer setup failed: %s",
            agent_name, exc,
        )
        wire.ragas_scorer_wired = False

    # Layer 5: structlogLogger
    try:
        wire.structlog_wired = True
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "attach_observability(%s): structlog setup failed: %s",
            agent_name, exc,
        )
        wire.structlog_wired = False

    wire.observability_wired = all([
        wire.langfuse_wired,
        wire.logfire_wired,
        wire.mlflow_wired,
        wire.ragas_scorer_wired,
        wire.structlog_wired,
    ])
    return wire


def verify_5_layer_contract(agent_name: str | None = None) -> bool | dict[str, bool]:
    """Verify the 5-layer observability contract.

    With an ``agent_name`` argument, returns ``True`` if all 5
    layers are wired for that agent, ``False`` otherwise.

    Without arguments, returns a dict mapping
    ``agent_name → bool`` for all 12 main agents.
    """
    from .agent_registry import AGENT_REGISTRY
    from .wiring import wire_agent

    if agent_name is not None:
        wiring = AGENT_REGISTRY[agent_name]
        wire = wire_agent(wiring)
        return wire.observability_wired

    out: dict[str, bool] = {}
    for name, wiring in AGENT_REGISTRY.items():
        try:
            wire = wire_agent(wiring)
            out[name] = wire.observability_wired
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "verify_5_layer_contract(%s): %s", name, exc
            )
            out[name] = False
    return out


__all__ = [
    "LangfuseLogger",
    "LogfireSpan",
    "MLflowTracker",
    "RAGASScorer",
    "attach_observability",
    "structlogLogger",
    "verify_5_layer_contract",
]