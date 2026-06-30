"""
Observability Integration for Celtic Education AI Pipeline.

Provides:
- Datadog LLM Observability for Google ADK agents with Gemini
- Datadog APM tracing for FastAPI endpoints
- MLflow experiment tracking for agent evaluation
- Langfuse LLM tracing with cost tracking
- Ragas RAG quality evaluation
- Structured logging with trace correlation
- Custom metrics for education pipeline

Deployed Infrastructure:
- Datadog: Cloud (datadoghq.eu)
- MLflow: mlflow.cianfhoghlaim.ie
- Langfuse: langfuse.cianfhoghlaim.ie
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Lazy initialization flags
_initialized = False
_llmobs_enabled = False

# Export placeholders (populated on init)
tracer = None
LLMObs = None
workflow = None
task = None
agent = None
llm = None


def init_observability() -> bool:
    """
    Initialize Datadog observability.

    Call this early in application startup (before importing instrumented modules).

    Returns:
        bool: True if initialization successful
    """
    global _initialized, _llmobs_enabled, tracer, LLMObs, workflow, task, agent, llm

    if _initialized:
        return True

    # Check if Datadog is configured
    dd_api_key = os.getenv("DD_API_KEY")
    if not dd_api_key:
        logger.warning("DD_API_KEY not set, Datadog observability disabled")
        _initialized = True
        return False

    try:
        # Initialize ddtrace
        from ddtrace import patch_all
        from ddtrace import tracer as _tracer

        patch_all()
        tracer = _tracer

        # Configure service name
        tracer.set_tags(
            {
                "env": os.getenv("DD_ENV", "development"),
                "service": os.getenv("DD_SERVICE", "oideachais-education"),
                "version": os.getenv("DD_VERSION", "0.1.0"),
            }
        )

        logger.info("Datadog APM initialized")

        # Initialize LLM Observability if enabled
        llmobs_enabled = os.getenv("DD_LLMOBS_ENABLED", "false").lower() == "true"
        if llmobs_enabled:
            try:
                from ddtrace.llmobs import LLMObs as _LLMObs
                from ddtrace.llmobs.decorators import agent as _agent
                from ddtrace.llmobs.decorators import llm as _llm
                from ddtrace.llmobs.decorators import task as _task
                from ddtrace.llmobs.decorators import workflow as _workflow

                _LLMObs.enable(
                    ml_app=os.getenv("DD_LLMOBS_ML_APP", "celtic-education-pipeline"),
                    integrations_enabled=True,
                    agentless_enabled=os.getenv("DD_LLMOBS_AGENTLESS_ENABLED", "true").lower()
                    == "true",
                    site=os.getenv("DD_SITE", "datadoghq.eu"),
                    api_key=dd_api_key,
                    env=os.getenv("DD_ENV", "development"),
                    service=os.getenv("DD_SERVICE", "oideachais-education"),
                )

                # Export LLM Obs components
                LLMObs = _LLMObs
                workflow = _workflow
                task = _task
                agent = _agent
                llm = _llm
                _llmobs_enabled = True

                logger.info("Datadog LLM Observability initialized")

            except ImportError as e:
                logger.warning(f"LLM Observability not available: {e}")

        _initialized = True
        return True

    except ImportError as e:
        logger.warning(f"ddtrace not installed: {e}")
        _initialized = True
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Datadog: {e}")
        _initialized = True
        return False


def is_initialized() -> bool:
    """Check if observability is initialized."""
    return _initialized


def is_llmobs_enabled() -> bool:
    """Check if LLM Observability is enabled."""
    return _llmobs_enabled


def get_tracer():
    """Get the Datadog tracer (or None if not initialized)."""
    return tracer


def annotate_span(
    input_data: Any = None,
    output_data: Any = None,
    metadata: dict[str, Any] | None = None,
    metrics: dict[str, float] | None = None,
    tags: dict[str, str] | None = None,
) -> None:
    """
    Annotate the current LLM Observability span.

    Safe to call even if LLMObs is not enabled.
    """
    if LLMObs is not None:
        try:
            LLMObs.annotate(
                input_data=input_data,
                output_data=output_data,
                metadata=metadata,
                metrics=metrics,
                tags=tags,
            )
        except Exception as e:
            logger.debug(f"Failed to annotate span: {e}")


# Re-export for convenience - Datadog
from .agent_tracing import (
    GeminiLLMSpan,
    MLPipelineMetrics,
    ml_metrics,
    trace_adk_agent,
    trace_tool_call,
)
from .fastapi_middleware import (
    DatadogAPMMiddleware,
    MLPipelineMetricsMiddleware,
    add_health_endpoints,
    setup_datadog_apm,
    setup_ml_metrics,
)

# Re-export for convenience - Langfuse
from .langfuse_config import (
    create_generation,
    create_span,
    get_langfuse_client,
    init_langfuse,
    langfuse_trace,
    log_llm_call,
    observe,
    score_trace,
)
from .langfuse_config import (
    flush as langfuse_flush,
)
from .langfuse_config import (
    shutdown as langfuse_shutdown,
)

# Structured Logging (structlog)
from .logging import LogContext, configure_logging, get_logger, log_operation
from .logging_config import DatadogJSONFormatter, setup_logging

# Re-export for convenience - MLflow
from .mlflow_config import (
    EXPERIMENTS,
    get_experiment,
    init_mlflow,
    log_agent_metrics,
    log_evaluation_results,
    log_model_to_registry,
    log_search_metrics,
    mlflow_run,
    setup_experiment,
    track_agent_run,
)

# Re-export for convenience - Ragas
from .ragas_evaluator import (
    EvaluationResult,
    EvaluationSample,
    RagasEvaluator,
    evaluate_curriculum_search,
    evaluate_document_qa,
    evaluate_rag_response,
    run_evaluation_suite,
)

__all__ = [
    "EXPERIMENTS",
    "DatadogAPMMiddleware",
    "DatadogJSONFormatter",
    "EvaluationResult",
    "EvaluationSample",
    "GeminiLLMSpan",
    "LLMObs",
    "LogContext",
    "MLPipelineMetrics",
    "MLPipelineMetricsMiddleware",
    # Ragas
    "RagasEvaluator",
    "add_health_endpoints",
    "agent",
    "annotate_span",
    "configure_logging",
    "create_generation",
    "create_span",
    "evaluate_curriculum_search",
    "evaluate_document_qa",
    "evaluate_rag_response",
    "get_experiment",
    "get_langfuse_client",
    # Structured Logging (structlog)
    "get_logger",
    "get_tracer",
    # Langfuse
    "init_langfuse",
    # MLflow
    "init_mlflow",
    # Datadog Initialization
    "init_observability",
    "is_initialized",
    "is_llmobs_enabled",
    "langfuse_flush",
    "langfuse_shutdown",
    "langfuse_trace",
    "llm",
    "log_agent_metrics",
    "log_evaluation_results",
    "log_llm_call",
    "log_model_to_registry",
    "log_operation",
    "log_search_metrics",
    # ML Pipeline Metrics
    "ml_metrics",
    "mlflow_run",
    "observe",
    "run_evaluation_suite",
    "score_trace",
    # Datadog FastAPI
    "setup_datadog_apm",
    "setup_experiment",
    # Datadog Logging
    "setup_logging",
    "setup_ml_metrics",
    "task",
    # Datadog Agent tracing
    "trace_adk_agent",
    "trace_tool_call",
    # Datadog Tracer and decorators (may be None)
    "tracer",
    "track_agent_run",
    "workflow",
    # ── Added in Phase 4 (2026-06-30): unified init + logfire flat re-exports ──
    "init_all_observability",
    "init_logfire",
    "ensure_initialized",
    "logfire_span",
    "log_llm_call",
    "log_embedding_call",
    "instrument",
    "instrument_pydantic",
    "instrument_httpx",
    "instrument_fastapi",
    "log_info",
    "log_warning",
    "log_error",
    "shutdown_logfire",
]


def init_all_observability() -> dict[str, bool]:
    """Convenience: call init_observability + init_mlflow + init_langfuse + init_logfire.

    Replaces the per-backend lifespan boilerplate that FastAPI apps used
    previously (see `agents/api/_oideachais_api/main.py:54-73` for the
    original 3-line pattern).

    Returns:
        dict mapping backend name → success flag.
        Example: {"datadog": True, "mlflow": True, "langfuse": True, "logfire": False}
    """
    results: dict[str, bool] = {}

    # 1. Datadog APM + LLMObs
    try:
        results["datadog"] = bool(init_observability())
    except Exception as exc:  # noqa: BLE001
        logger.warning("init_all_observability: Datadog init failed: %s", exc)
        results["datadog"] = False

    # 2. MLflow
    try:
        from cianfhoghlaim.observability.mlflow_config import init_mlflow

        results["mlflow"] = bool(init_mlflow())
    except Exception as exc:  # noqa: BLE001
        logger.warning("init_all_observability: MLflow init failed: %s", exc)
        results["mlflow"] = False

    # 3. Langfuse
    try:
        from cianfhoghlaim.observability.langfuse_config import init_langfuse

        results["langfuse"] = bool(init_langfuse())
    except Exception as exc:  # noqa: BLE001
        logger.warning("init_all_observability: Langfuse init failed: %s", exc)
        results["langfuse"] = False

    # 4. Logfire (Pydantic)
    try:
        from cianfhoghlaim.observability.logfire_config import init_logfire

        results["logfire"] = bool(init_logfire())
    except Exception as exc:  # noqa: BLE001
        logger.warning("init_all_observability: Logfire init failed: %s", exc)
        results["logfire"] = False

    logger.info("init_all_observability: %s", results)
    return results


# ── Flat re-exports of Logfire symbols (T4.3: was logfire_config.py only) ──
# These are exposed at the package root so callers don't need the
# submodule import path. Backward-compat: `from cianfhoghlaim.observability.logfire_config import X`
# still works (the module still exists).
try:
    from cianfhoghlaim.observability.logfire_config import (  # type: ignore[import-not-found]
        ensure_initialized as _ensure_logfire,
        init_logfire as _init_logfire,
        instrument as _instrument,
        instrument_fastapi as _instrument_fastapi,
        instrument_httpx as _instrument_httpx,
        instrument_pydantic as _instrument_pydantic,
        log_embedding_call as _log_embedding_call,
        log_error as _log_error,
        log_info as _log_info,
        log_llm_call as _log_llm_call,
        log_warning as _log_warning,
        logfire_span as _logfire_span,
        shutdown as _shutdown_logfire,
    )

    ensure_initialized = _ensure_logfire
    init_logfire = _init_logfire
    instrument = _instrument
    instrument_fastapi = _instrument_fastapi
    instrument_httpx = _instrument_httpx
    instrument_pydantic = _instrument_pydantic
    log_embedding_call = _log_embedding_call
    log_error = _log_error
    log_info = _log_info
    log_llm_call = _log_llm_call
    log_warning = _log_warning
    logfire_span = _logfire_span
    shutdown_logfire = _shutdown_logfire
except ImportError:
    # logfire not installed (rare); flat symbols degrade to no-ops.
    ensure_initialized = lambda: False  # type: ignore[assignment]
    init_logfire = lambda *a, **kw: False  # type: ignore[assignment]
    instrument = lambda *a, **kw: None  # type: ignore[assignment]
    instrument_fastapi = lambda *a, **kw: None  # type: ignore[assignment]
    instrument_httpx = lambda *a, **kw: None  # type: ignore[assignment]
    instrument_pydantic = lambda *a, **kw: None  # type: ignore[assignment]
    log_embedding_call = lambda *a, **kw: None  # type: ignore[assignment]
    log_error = lambda *a, **kw: None  # type: ignore[assignment]
    log_info = lambda *a, **kw: None  # type: ignore[assignment]
    log_llm_call = lambda *a, **kw: None  # type: ignore[assignment]
    log_warning = lambda *a, **kw: None  # type: ignore[assignment]
    logfire_span = lambda *a, **kw: None  # type: ignore[assignment]
    shutdown_logfire = lambda: None  # type: ignore[assignment]
