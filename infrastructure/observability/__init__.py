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
    # Datadog Initialization
    "init_observability",
    "is_initialized",
    "is_llmobs_enabled",
    "get_tracer",
    "annotate_span",
    # Datadog Tracer and decorators (may be None)
    "tracer",
    "LLMObs",
    "workflow",
    "task",
    "agent",
    "llm",
    # Datadog Agent tracing
    "trace_adk_agent",
    "trace_tool_call",
    "GeminiLLMSpan",
    # ML Pipeline Metrics
    "ml_metrics",
    "MLPipelineMetrics",
    # Datadog FastAPI
    "setup_datadog_apm",
    "setup_ml_metrics",
    "DatadogAPMMiddleware",
    "MLPipelineMetricsMiddleware",
    "add_health_endpoints",
    # Datadog Logging
    "setup_logging",
    "DatadogJSONFormatter",
    # Structured Logging (structlog)
    "get_logger",
    "configure_logging",
    "LogContext",
    "log_operation",
    # MLflow
    "init_mlflow",
    "mlflow_run",
    "log_agent_metrics",
    "log_search_metrics",
    "log_evaluation_results",
    "track_agent_run",
    "get_experiment",
    "setup_experiment",
    "log_model_to_registry",
    "EXPERIMENTS",
    # Langfuse
    "init_langfuse",
    "get_langfuse_client",
    "langfuse_trace",
    "create_generation",
    "create_span",
    "score_trace",
    "observe",
    "log_llm_call",
    "langfuse_flush",
    "langfuse_shutdown",
    # Ragas
    "RagasEvaluator",
    "EvaluationSample",
    "EvaluationResult",
    "evaluate_rag_response",
    "run_evaluation_suite",
    "evaluate_curriculum_search",
    "evaluate_document_qa",
]
