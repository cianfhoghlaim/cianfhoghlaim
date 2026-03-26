"""
Structured logging configuration for oideachais.

Provides consistent, structured logging across all modules using structlog.
Integrates with Dagster, Datadog, and other observability tools.

Usage:
    from sruth.oideachais.observability.logging import get_logger

    logger = get_logger(__name__)
    logger.info("processing_started", source="ncca", batch_size=100)
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from sruth.oideachais.settings import settings
from structlog.types import Processor


def add_environment(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Add environment information to log events."""
    event_dict["environment"] = settings.env
    event_dict["service"] = "oideachais"
    return event_dict


def add_caller_info(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Add caller module and function info."""
    # structlog already handles this, but we can customize
    return event_dict


def configure_logging(
    level: str = "INFO",
    json_output: bool | None = None,
    add_timestamp: bool = True,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_output: Force JSON output (default: True in production)
        add_timestamp: Add ISO timestamp to logs
    """
    # Determine output format
    if json_output is None:
        json_output = settings.is_production

    # Build processor chain
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_environment,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if add_timestamp:
        processors.insert(0, structlog.processors.TimeStamper(fmt="iso"))

    # Add format-specific processors
    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.rich_traceback,
            )
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class LogContext:
    """
    Context manager for adding temporary context to logs.

    Usage:
        with LogContext(request_id="abc123", user_id="user1"):
            logger.info("processing_request")
            # All logs within this block will have request_id and user_id
    """

    def __init__(self, **context: Any):
        self.context = context
        self._token: Any = None

    def __enter__(self) -> LogContext:
        self._token = structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, *args: Any) -> None:
        if self._token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


def log_operation(
    operation: str,
    **kwargs: Any,
) -> Any:
    """
    Decorator for logging function entry/exit.

    Usage:
        @log_operation("fetch_curriculum")
        async def fetch_curriculum(url: str):
            ...
    """
    import functools
    import time

    def decorator(fn: Any) -> Any:
        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **fn_kwargs: Any) -> Any:
            logger = get_logger(fn.__module__)
            start_time = time.time()

            logger.info(
                f"{operation}_started",
                function=fn.__name__,
                **kwargs,
            )

            try:
                result = await fn(*args, **fn_kwargs)
                duration = time.time() - start_time

                logger.info(
                    f"{operation}_completed",
                    function=fn.__name__,
                    duration_seconds=round(duration, 3),
                    **kwargs,
                )
                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{operation}_failed",
                    function=fn.__name__,
                    duration_seconds=round(duration, 3),
                    error=str(e),
                    error_type=type(e).__name__,
                    **kwargs,
                )
                raise

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **fn_kwargs: Any) -> Any:
            logger = get_logger(fn.__module__)
            start_time = time.time()

            logger.info(
                f"{operation}_started",
                function=fn.__name__,
                **kwargs,
            )

            try:
                result = fn(*args, **fn_kwargs)
                duration = time.time() - start_time

                logger.info(
                    f"{operation}_completed",
                    function=fn.__name__,
                    duration_seconds=round(duration, 3),
                    **kwargs,
                )
                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"{operation}_failed",
                    function=fn.__name__,
                    duration_seconds=round(duration, 3),
                    error=str(e),
                    error_type=type(e).__name__,
                    **kwargs,
                )
                raise

        import asyncio
        if asyncio.iscoroutinefunction(fn):
            return async_wrapper
        return sync_wrapper

    return decorator


# Initialize logging on import (can be reconfigured later)
configure_logging(
    level="DEBUG" if settings.debug else "INFO",
)
