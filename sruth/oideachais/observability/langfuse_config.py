"""
Langfuse Configuration for Celtic Education Pipeline.

Provides:
- LLM tracing and observability
- User session tracking
- Cost tracking per model/agent
- Prompt management and A/B testing
- Integration with Ragas for evaluation

Deployed at: langfuse.cianfhoghlaim.ie
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
_langfuse = None
_langfuse_available = None
_langfuse_client = None
_client_lock = threading.Lock()


def _get_langfuse():
    """Lazy load Langfuse to handle missing dependency."""
    global _langfuse, _langfuse_available
    if _langfuse_available is None:
        try:
            import langfuse

            _langfuse = langfuse
            _langfuse_available = True
        except ImportError:
            _langfuse_available = False
            logger.warning("Langfuse not installed. Install with: pip install langfuse")
    return _langfuse if _langfuse_available else None


# Default configuration
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")


def get_langfuse_client():
    """
    Get or create singleton Langfuse client.

    Returns:
        Langfuse client if available, None otherwise.
    """
    global _langfuse_client

    langfuse_module = _get_langfuse()
    if langfuse_module is None:
        return None

    if _langfuse_client is None:
        with _client_lock:
            if _langfuse_client is None:
                try:
                    from langfuse import Langfuse

                    _langfuse_client = Langfuse(
                        public_key=LANGFUSE_PUBLIC_KEY,
                        secret_key=LANGFUSE_SECRET_KEY,
                        host=LANGFUSE_HOST,
                    )
                    logger.info(f"Langfuse client initialized: host={LANGFUSE_HOST}")
                except Exception as e:
                    logger.error(f"Failed to initialize Langfuse: {e}")
                    return None

    return _langfuse_client


def init_langfuse(
    public_key: str | None = None,
    secret_key: str | None = None,
    host: str | None = None,
) -> bool:
    """
    Initialize Langfuse with custom configuration.

    Args:
        public_key: Langfuse public key
        secret_key: Langfuse secret key
        host: Langfuse server host

    Returns:
        True if initialization successful, False otherwise.
    """
    global LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST, _langfuse_client

    if public_key:
        LANGFUSE_PUBLIC_KEY = public_key
    if secret_key:
        LANGFUSE_SECRET_KEY = secret_key
    if host:
        LANGFUSE_HOST = host

    # Reset client to force re-initialization
    _langfuse_client = None

    client = get_langfuse_client()
    return client is not None


@contextmanager
def langfuse_trace(
    name: str,
    user_id: str | None = None,
    session_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
):
    """
    Context manager for Langfuse trace.

    Args:
        name: Name of the trace
        user_id: Optional user identifier
        session_id: Optional session identifier
        metadata: Additional metadata
        tags: Tags for filtering

    Yields:
        Langfuse trace object if available, None otherwise.

    Example:
        with langfuse_trace("curriculum_search", user_id="user123"):
            # LLM calls will be traced
            response = agent.run(query)
    """
    client = get_langfuse_client()
    if client is None:
        yield None
        return

    default_tags = ["oideachais", "celtic-education"]
    if tags:
        default_tags.extend(tags)

    default_metadata = {
        "environment": os.getenv("DD_ENV", "development"),
        "pipeline": "oideachais",
    }
    if metadata:
        default_metadata.update(metadata)

    try:
        trace = client.trace(
            name=name,
            user_id=user_id,
            session_id=session_id,
            metadata=default_metadata,
            tags=default_tags,
        )
        yield trace
    except Exception as e:
        logger.error(f"Langfuse trace failed: {e}")
        yield None
    finally:
        try:
            client.flush()
        except Exception:
            pass


def create_generation(
    trace,
    name: str,
    model: str,
    input_messages: list[dict] | str,
    output: str | None = None,
    model_parameters: dict[str, Any] | None = None,
    usage: dict[str, int] | None = None,
    metadata: dict[str, Any] | None = None,
):
    """
    Create a generation (LLM call) within a trace.

    Args:
        trace: Parent trace object
        name: Name of the generation
        model: Model identifier (e.g., "gemini-2.0-flash")
        input_messages: Input to the LLM
        output: LLM output
        model_parameters: Model parameters (temperature, etc.)
        usage: Token usage dict (prompt_tokens, completion_tokens, total_tokens)
        metadata: Additional metadata

    Returns:
        Generation object if successful, None otherwise.
    """
    if trace is None:
        return None

    try:
        generation = trace.generation(
            name=name,
            model=model,
            input=input_messages,
            output=output,
            model_parameters=model_parameters or {},
            usage=usage,
            metadata=metadata or {},
        )
        return generation
    except Exception as e:
        logger.warning(f"Failed to create generation: {e}")
        return None


def create_span(
    trace,
    name: str,
    input_data: Any | None = None,
    output_data: Any | None = None,
    metadata: dict[str, Any] | None = None,
):
    """
    Create a span (non-LLM operation) within a trace.

    Args:
        trace: Parent trace object
        name: Name of the span
        input_data: Input to the operation
        output_data: Output of the operation
        metadata: Additional metadata

    Returns:
        Span object if successful, None otherwise.
    """
    if trace is None:
        return None

    try:
        span = trace.span(
            name=name,
            input=input_data,
            output=output_data,
            metadata=metadata or {},
        )
        return span
    except Exception as e:
        logger.warning(f"Failed to create span: {e}")
        return None


def score_trace(
    trace,
    name: str,
    value: float,
    comment: str | None = None,
):
    """
    Add a score to a trace.

    Args:
        trace: Trace object to score
        name: Name of the score (e.g., "faithfulness", "relevancy")
        value: Score value (typically 0-1)
        comment: Optional comment explaining the score
    """
    if trace is None:
        return

    client = get_langfuse_client()
    if client is None:
        return

    try:
        client.score(
            trace_id=trace.id,
            name=name,
            value=value,
            comment=comment,
        )
    except Exception as e:
        logger.warning(f"Failed to score trace: {e}")


def observe(
    name: str | None = None,
    user_id_param: str | None = None,
    session_id_param: str | None = None,
):
    """
    Decorator to observe a function with Langfuse tracing.

    Args:
        name: Name of the trace (defaults to function name)
        user_id_param: Name of parameter containing user_id
        session_id_param: Name of parameter containing session_id

    Example:
        @observe("curriculum_search", user_id_param="user_id")
        async def search(query: str, user_id: str = None):
            ...
    """

    def decorator(func: Callable) -> Callable:
        trace_name = name or func.__name__

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            user_id = kwargs.get(user_id_param) if user_id_param else None
            session_id = kwargs.get(session_id_param) if session_id_param else None

            with langfuse_trace(
                name=trace_name,
                user_id=user_id,
                session_id=session_id,
                metadata={"function": func.__name__},
            ) as trace:
                # Store trace in thread-local for nested operations
                import contextvars

                trace_var = contextvars.ContextVar("langfuse_trace", default=None)
                token = trace_var.set(trace)
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    trace_var.reset(token)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            user_id = kwargs.get(user_id_param) if user_id_param else None
            session_id = kwargs.get(session_id_param) if session_id_param else None

            with langfuse_trace(
                name=trace_name,
                user_id=user_id,
                session_id=session_id,
                metadata={"function": func.__name__},
            ) as trace:
                import contextvars

                trace_var = contextvars.ContextVar("langfuse_trace", default=None)
                token = trace_var.set(trace)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    trace_var.reset(token)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def log_llm_call(
    model: str,
    messages: list[dict],
    response: str,
    latency_ms: float,
    token_usage: dict[str, int] | None = None,
    trace=None,
):
    """
    Log an LLM call to Langfuse.

    Args:
        model: Model name (e.g., "gemini-2.0-flash")
        messages: Input messages
        response: Model response
        latency_ms: Latency in milliseconds
        token_usage: Token usage dict
        trace: Optional parent trace
    """
    client = get_langfuse_client()
    if client is None:
        return

    if trace is None:
        # Create standalone trace
        with langfuse_trace(f"llm_call_{model}") as trace:
            create_generation(
                trace=trace,
                name="llm_completion",
                model=model,
                input_messages=messages,
                output=response,
                usage=token_usage,
                metadata={"latency_ms": latency_ms},
            )
    else:
        create_generation(
            trace=trace,
            name="llm_completion",
            model=model,
            input_messages=messages,
            output=response,
            usage=token_usage,
            metadata={"latency_ms": latency_ms},
        )


def flush():
    """Flush all pending Langfuse events."""
    client = get_langfuse_client()
    if client:
        try:
            client.flush()
        except Exception as e:
            logger.warning(f"Failed to flush Langfuse: {e}")


def shutdown():
    """Shutdown Langfuse client gracefully."""
    global _langfuse_client

    if _langfuse_client:
        try:
            _langfuse_client.flush()
            _langfuse_client.shutdown()
            _langfuse_client = None
            logger.info("Langfuse client shutdown complete")
        except Exception as e:
            logger.warning(f"Error during Langfuse shutdown: {e}")
