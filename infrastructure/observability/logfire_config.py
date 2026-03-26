"""
Logfire Configuration for Celtic Education Pipeline.

Provides:
- OpenTelemetry-based tracing and observability
- Pydantic model validation tracking
- Automatic instrumentation of HTTP requests
- LLM call tracing with cost attribution
- Integration with existing Datadog APM

Docs: https://logfire.pydantic.dev
Dashboard: https://logfire.pydantic.dev/<project>
"""

import logging
import os
import threading
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)

# Lazy imports for optional dependency
_logfire = None
_logfire_available = None
_logfire_initialized = False
_init_lock = threading.Lock()


def _get_logfire():
    """Lazy load Logfire to handle missing dependency."""
    global _logfire, _logfire_available
    if _logfire_available is None:
        try:
            import logfire

            _logfire = logfire
            _logfire_available = True
        except ImportError:
            _logfire_available = False
            logger.warning("Logfire not installed. Install with: pip install logfire")
    return _logfire if _logfire_available else None


# Default configuration
LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN", "")
LOGFIRE_PROJECT_NAME = os.getenv("LOGFIRE_PROJECT_NAME", "oideachas-celtic-education")
LOGFIRE_SERVICE_NAME = os.getenv("LOGFIRE_SERVICE_NAME", "education-pipeline")
LOGFIRE_ENVIRONMENT = os.getenv("LOGFIRE_ENVIRONMENT", os.getenv("DD_ENV", "development"))


def init_logfire(
    token: str | None = None,
    project_name: str | None = None,
    service_name: str | None = None,
    environment: str | None = None,
) -> bool:
    """
    Initialize Logfire with configuration.

    Args:
        token: Logfire write token
        project_name: Project name in Logfire
        service_name: Service name for tracing
        environment: Environment (development, staging, production)

    Returns:
        True if initialization successful, False otherwise.
    """
    global _logfire_initialized, LOGFIRE_TOKEN, LOGFIRE_PROJECT_NAME
    global LOGFIRE_SERVICE_NAME, LOGFIRE_ENVIRONMENT

    if _logfire_initialized:
        return True

    logfire_module = _get_logfire()
    if logfire_module is None:
        return False

    with _init_lock:
        if _logfire_initialized:
            return True

        # Update configuration
        if token:
            LOGFIRE_TOKEN = token
        if project_name:
            LOGFIRE_PROJECT_NAME = project_name
        if service_name:
            LOGFIRE_SERVICE_NAME = service_name
        if environment:
            LOGFIRE_ENVIRONMENT = environment

        if not LOGFIRE_TOKEN:
            logger.warning("LOGFIRE_TOKEN not set, Logfire disabled")
            return False

        try:
            logfire_module.configure(
                token=LOGFIRE_TOKEN,
                project_name=LOGFIRE_PROJECT_NAME,
                service_name=LOGFIRE_SERVICE_NAME,
                environment=LOGFIRE_ENVIRONMENT,
                send_to_logfire=True,
            )
            _logfire_initialized = True
            logger.info(
                f"Logfire initialized: project={LOGFIRE_PROJECT_NAME}, "
                f"service={LOGFIRE_SERVICE_NAME}, env={LOGFIRE_ENVIRONMENT}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Logfire: {e}")
            return False


def ensure_initialized() -> bool:
    """Ensure Logfire is initialized."""
    if not _logfire_initialized:
        return init_logfire()
    return True


@contextmanager
def logfire_span(
    name: str,
    *,
    user_id: str | None = None,
    session_id: str | None = None,
    attributes: dict[str, Any] | None = None,
):
    """
    Context manager for Logfire span.

    Args:
        name: Name of the span
        user_id: Optional user identifier
        session_id: Optional session identifier
        attributes: Additional span attributes

    Yields:
        Logfire span object if available, None otherwise.

    Example:
        with logfire_span("curriculum_search", user_id="user123"):
            # Operations will be traced
            response = agent.run(query)
    """
    logfire_module = _get_logfire()
    if logfire_module is None or not ensure_initialized():
        yield None
        return

    span_attributes = {
        "service.name": LOGFIRE_SERVICE_NAME,
        "environment": LOGFIRE_ENVIRONMENT,
        "pipeline": "oideachas",
    }

    if user_id:
        span_attributes["user.id"] = user_id
    if session_id:
        span_attributes["session.id"] = session_id
    if attributes:
        span_attributes.update(attributes)

    try:
        with logfire_module.span(name, **span_attributes) as span:
            yield span
    except Exception as e:
        logger.error(f"Logfire span failed: {e}")
        yield None


def log_llm_call(
    model: str,
    messages: list[dict],
    response: str,
    latency_ms: float,
    token_usage: dict[str, int] | None = None,
    cost_usd: float | None = None,
):
    """
    Log an LLM call to Logfire.

    Args:
        model: Model name (e.g., "gemini-2.0-flash", "claude-sonnet")
        messages: Input messages
        response: Model response
        latency_ms: Latency in milliseconds
        token_usage: Token usage dict (prompt_tokens, completion_tokens, total_tokens)
        cost_usd: Cost in USD (if known)
    """
    logfire_module = _get_logfire()
    if logfire_module is None or not ensure_initialized():
        return

    attributes = {
        "llm.model": model,
        "llm.latency_ms": latency_ms,
        "llm.input_length": sum(len(m.get("content", "")) for m in messages),
        "llm.output_length": len(response),
    }

    if token_usage:
        attributes["llm.prompt_tokens"] = token_usage.get("prompt_tokens", 0)
        attributes["llm.completion_tokens"] = token_usage.get("completion_tokens", 0)
        attributes["llm.total_tokens"] = token_usage.get("total_tokens", 0)

    if cost_usd is not None:
        attributes["llm.cost_usd"] = cost_usd

    try:
        logfire_module.info(
            f"LLM call: {model}",
            **attributes,
        )
    except Exception as e:
        logger.warning(f"Failed to log LLM call: {e}")


def log_embedding_call(
    model: str,
    text_count: int,
    latency_ms: float,
    dimensions: int | None = None,
    token_count: int | None = None,
):
    """
    Log an embedding call to Logfire.

    Args:
        model: Embedding model name
        text_count: Number of texts embedded
        latency_ms: Latency in milliseconds
        dimensions: Embedding dimensions
        token_count: Total token count
    """
    logfire_module = _get_logfire()
    if logfire_module is None or not ensure_initialized():
        return

    attributes = {
        "embedding.model": model,
        "embedding.text_count": text_count,
        "embedding.latency_ms": latency_ms,
    }

    if dimensions:
        attributes["embedding.dimensions"] = dimensions
    if token_count:
        attributes["embedding.token_count"] = token_count

    try:
        logfire_module.info(
            f"Embedding: {model} ({text_count} texts)",
            **attributes,
        )
    except Exception as e:
        logger.warning(f"Failed to log embedding call: {e}")


def instrument(
    name: str | None = None,
    *,
    user_id_param: str | None = None,
    session_id_param: str | None = None,
    extract_attributes: Callable[[dict], dict] | None = None,
):
    """
    Decorator to instrument a function with Logfire tracing.

    Args:
        name: Name of the span (defaults to function name)
        user_id_param: Name of parameter containing user_id
        session_id_param: Name of parameter containing session_id
        extract_attributes: Function to extract additional attributes from kwargs

    Example:
        @instrument("curriculum_search", user_id_param="user_id")
        async def search(query: str, user_id: str = None):
            ...
    """

    def decorator(func: Callable) -> Callable:
        span_name = name or func.__name__

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            user_id = kwargs.get(user_id_param) if user_id_param else None
            session_id = kwargs.get(session_id_param) if session_id_param else None

            attributes = {"function": func.__name__}
            if extract_attributes:
                attributes.update(extract_attributes(kwargs))

            with logfire_span(
                span_name,
                user_id=user_id,
                session_id=session_id,
                attributes=attributes,
            ):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            user_id = kwargs.get(user_id_param) if user_id_param else None
            session_id = kwargs.get(session_id_param) if session_id_param else None

            attributes = {"function": func.__name__}
            if extract_attributes:
                attributes.update(extract_attributes(kwargs))

            with logfire_span(
                span_name,
                user_id=user_id,
                session_id=session_id,
                attributes=attributes,
            ):
                return func(*args, **kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def instrument_pydantic():
    """
    Enable Logfire instrumentation for Pydantic models.

    This tracks validation time, errors, and model usage.
    Call this once at startup.
    """
    logfire_module = _get_logfire()
    if logfire_module is None or not ensure_initialized():
        return

    try:
        logfire_module.instrument_pydantic()
        logger.info("Pydantic instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to enable Pydantic instrumentation: {e}")


def instrument_httpx():
    """
    Enable Logfire instrumentation for HTTPX.

    This tracks outgoing HTTP requests.
    Call this once at startup.
    """
    logfire_module = _get_logfire()
    if logfire_module is None or not ensure_initialized():
        return

    try:
        logfire_module.instrument_httpx()
        logger.info("HTTPX instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to enable HTTPX instrumentation: {e}")


def instrument_fastapi(app):
    """
    Enable Logfire instrumentation for FastAPI.

    Args:
        app: FastAPI application instance

    Call this after creating the FastAPI app.
    """
    logfire_module = _get_logfire()
    if logfire_module is None or not ensure_initialized():
        return

    try:
        logfire_module.instrument_fastapi(app)
        logger.info("FastAPI instrumentation enabled")
    except Exception as e:
        logger.warning(f"Failed to enable FastAPI instrumentation: {e}")


def log_info(message: str, **attributes):
    """Log an info message with attributes."""
    logfire_module = _get_logfire()
    if logfire_module is None or not ensure_initialized():
        return

    try:
        logfire_module.info(message, **attributes)
    except Exception as e:
        logger.warning(f"Logfire info log failed: {e}")


def log_warning(message: str, **attributes):
    """Log a warning message with attributes."""
    logfire_module = _get_logfire()
    if logfire_module is None or not ensure_initialized():
        return

    try:
        logfire_module.warn(message, **attributes)
    except Exception as e:
        logger.warning(f"Logfire warning log failed: {e}")


def log_error(message: str, **attributes):
    """Log an error message with attributes."""
    logfire_module = _get_logfire()
    if logfire_module is None or not ensure_initialized():
        return

    try:
        logfire_module.error(message, **attributes)
    except Exception as e:
        logger.warning(f"Logfire error log failed: {e}")


def shutdown():
    """Shutdown Logfire gracefully."""
    global _logfire_initialized

    logfire_module = _get_logfire()
    if logfire_module and _logfire_initialized:
        try:
            logfire_module.shutdown()
            _logfire_initialized = False
            logger.info("Logfire shutdown complete")
        except Exception as e:
            logger.warning(f"Error during Logfire shutdown: {e}")
