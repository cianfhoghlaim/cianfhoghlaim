"""Shared observability utilities for all sruth flows.

Provides unified tracing across:
- Datadog LLMObs: Agent traces, token usage
- Langfuse: Prompt management, A/B testing
- Logfire: Pydantic AI tracing
- MLflow: Experiment tracking
"""

from .unified_tracer import (
    # Core classes
    TraceSpan,
    TracingBackend,
    UnifiedTracer,
    # Backends
    DatadogBackend,
    LangfuseBackend,
    LogfireBackend,
    MLflowBackend,
    # Factory
    get_tracer,
    reset_tracer,
    # Convenience functions
    trace_agent_run,
    trace_tool_call,
    trace_llm_call,
)

__all__ = [
    # Core classes
    "TraceSpan",
    "TracingBackend",
    "UnifiedTracer",
    # Backends
    "DatadogBackend",
    "LangfuseBackend",
    "LogfireBackend",
    "MLflowBackend",
    # Factory
    "get_tracer",
    "reset_tracer",
    # Convenience functions
    "trace_agent_run",
    "trace_tool_call",
    "trace_llm_call",
]
