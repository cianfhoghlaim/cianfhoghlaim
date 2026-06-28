"""
Structured logging with Datadog trace correlation.

Provides:
- JSON formatted logs for Datadog ingestion
- Automatic trace/span ID injection
- Education-specific log fields
"""

import json
import logging
import sys
from datetime import datetime

logger = logging.getLogger(__name__)


class DatadogJSONFormatter(logging.Formatter):
    """
    JSON formatter with Datadog trace/span IDs for log correlation.

    Output format is compatible with Datadog log ingestion.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "oideachais-celtic-education",
            "source": "python",
        }

        # Add trace context for log correlation
        try:
            from ddtrace import tracer

            span = tracer.current_span()
            if span:
                log_data["dd.trace_id"] = str(span.trace_id)
                log_data["dd.span_id"] = str(span.span_id)
                log_data["dd.service"] = span.service or "oideachais-celtic-education"
        except ImportError:
            pass

        # Add custom fields if present on the record
        custom_fields = [
            "education_level",
            "subject",
            "agent",
            "tool",
            "document_id",
            "query",
            "nation",
            "language",
        ]
        for field in custom_fields:
            if hasattr(record, field):
                log_data[f"education.{field}"] = getattr(record, field)

        # Add exception info if present
        if record.exc_info:
            log_data["error.type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
            log_data["error.message"] = str(record.exc_info[1]) if record.exc_info[1] else None
            log_data["error.stack"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(
    level: int = logging.INFO,
    json_format: bool = True,
) -> None:
    """
    Configure structured logging for Datadog.

    Args:
        level: Log level (default: INFO)
        json_format: Use JSON formatting for Datadog (default: True)
    """
    handler = logging.StreamHandler(sys.stdout)

    if json_format:
        handler.setFormatter(DatadogJSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    # Configure specific loggers
    for logger_name in ["oideachais", "uvicorn", "fastapi", "ddtrace", "dagster"]:
        log = logging.getLogger(logger_name)
        log.handlers = [handler]
        log.setLevel(level)

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logger.info("Structured logging configured for Datadog")
