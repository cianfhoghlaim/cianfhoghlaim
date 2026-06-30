"""
FastAPI middleware for Datadog APM integration.

Provides:
- Request/response tracing with custom tags
- Education-specific metadata tagging
- Custom metrics for API endpoints
"""

import logging
import time
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Lazy imports
_tracer = None
_statsd = None


def _get_tracer():
    """Lazy load tracer."""
    global _tracer
    if _tracer is None:
        try:
            from ddtrace import tracer

            _tracer = tracer
        except ImportError:
            pass
    return _tracer


def _get_statsd():
    """Lazy load statsd."""
    global _statsd
    if _statsd is None:
        try:
            from datadog import statsd

            _statsd = statsd
        except ImportError:
            pass
    return _statsd


class DatadogAPMMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add custom APM tags and metrics to all requests.

    Adds education-specific context:
    - Subject area
    - Education level
    - Language (en/ga)
    - Nation (ireland, scotland, wales, etc.)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        tracer = _get_tracer()
        statsd = _get_statsd()

        # Get current span and add custom tags
        if tracer:
            span = tracer.current_span()
            if span:
                span.set_tag("education.pipeline", "oideachais")
                span.set_tag("http.route", request.url.path)

                # Add query parameters as tags for filtering
                if "subject" in request.query_params:
                    span.set_tag("education.subject", request.query_params["subject"])
                if "level" in request.query_params:
                    span.set_tag("education.level", request.query_params["level"])
                if "language" in request.query_params:
                    span.set_tag("education.language", request.query_params["language"])
                if "nation" in request.query_params:
                    span.set_tag("education.nation", request.query_params["nation"])

        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Record metrics
            if statsd:
                statsd.histogram(
                    "oideachais.api.latency",
                    duration_ms,
                    tags=[
                        f"endpoint:{request.url.path}",
                        f"method:{request.method}",
                        f"status:{response.status_code}",
                    ],
                )

                statsd.increment(
                    "oideachais.api.requests",
                    tags=[
                        f"endpoint:{request.url.path}",
                        f"status:{response.status_code}",
                    ],
                )

            return response

        except Exception as e:
            if statsd:
                statsd.increment(
                    "oideachais.api.errors",
                    tags=[
                        f"endpoint:{request.url.path}",
                        f"error_type:{type(e).__name__}",
                    ],
                )
            raise


def setup_datadog_apm(app: FastAPI) -> None:
    """
    Configure Datadog APM for FastAPI application.

    Call this after creating the FastAPI app:
        app = FastAPI()
        setup_datadog_apm(app)
    """
    try:
        from ddtrace.contrib.fastapi import patch as patch_fastapi

        # Patch FastAPI for automatic instrumentation
        patch_fastapi()
        logger.info("FastAPI patched for Datadog APM")
    except ImportError:
        logger.warning("ddtrace not available, skipping FastAPI patch")

    # Add custom middleware
    app.add_middleware(DatadogAPMMiddleware)
    logger.info("Datadog APM middleware configured for FastAPI")


# =============================================================================
# ML Pipeline Metrics Middleware
# =============================================================================

class MLPipelineMetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for ML pipeline-specific metrics.

    Tracks endpoints for:
    - HTR transcription requests
    - TTS synthesis requests
    - Curriculum search/generation
    - Embedding operations
    """

    # Endpoint patterns for ML services
    ML_ENDPOINTS = {
        "/htr": "htr",
        "/tts": "tts",
        "/curriculum": "curriculum",
        "/search": "search",
        "/embed": "embedding",
        "/duchas": "duchas",
        "/sec": "sec_exams",
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        statsd = _get_statsd()
        tracer = _get_tracer()

        # Identify ML service type
        ml_service = None
        for pattern, service in self.ML_ENDPOINTS.items():
            if pattern in request.url.path:
                ml_service = service
                break

        # Add ML-specific span tags
        if tracer and ml_service:
            span = tracer.current_span()
            if span:
                span.set_tag("ml.service", ml_service)
                span.set_tag("ml.pipeline", "oideachais")

                # Extract ML-specific parameters
                if "dialect" in request.query_params:
                    span.set_tag("ml.dialect", request.query_params["dialect"])
                if "model" in request.query_params:
                    span.set_tag("ml.model", request.query_params["model"])
                if "batch_size" in request.query_params:
                    span.set_tag("ml.batch_size", request.query_params["batch_size"])

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # Record ML-specific metrics
            if statsd and ml_service:
                tags = [
                    f"service:{ml_service}",
                    f"method:{request.method}",
                    f"status:{response.status_code}",
                ]

                # Add optional tags
                if "dialect" in request.query_params:
                    tags.append(f"dialect:{request.query_params['dialect']}")

                statsd.histogram(f"ml.{ml_service}.latency_ms", duration_ms, tags=tags)
                statsd.increment(f"ml.{ml_service}.requests", tags=tags)

                # Track by endpoint for granular monitoring
                statsd.histogram(
                    "oideachais.ml.endpoint.latency",
                    duration_ms,
                    tags=[f"endpoint:{request.url.path}", f"service:{ml_service}"],
                )

            return response

        except Exception as e:
            if statsd and ml_service:
                statsd.increment(
                    f"ml.{ml_service}.errors",
                    tags=[f"error_type:{type(e).__name__}"],
                )
            raise


def setup_ml_metrics(app: FastAPI) -> None:
    """
    Configure ML pipeline metrics middleware.

    Call after setup_datadog_apm for layered instrumentation:
        app = FastAPI()
        setup_datadog_apm(app)
        setup_ml_metrics(app)
    """
    app.add_middleware(MLPipelineMetricsMiddleware)
    logger.info("ML Pipeline metrics middleware configured")


# =============================================================================
# Health Check Endpoints
# =============================================================================

def add_health_endpoints(app: FastAPI) -> None:
    """Add health check endpoints for monitoring."""

    @app.get("/health")
    async def health_check():
        """Basic health check."""
        return {"status": "healthy", "service": "oideachais"}

    @app.get("/health/ready")
    async def readiness_check():
        """Readiness check with dependency status."""
        from datadog import statsd

        checks = {
            "api": True,
            "datadog": statsd is not None,
        }

        # Check optional dependencies
        try:
            import mlflow
            checks["mlflow"] = True
        except ImportError:
            checks["mlflow"] = False

        try:
            import lancedb
            checks["lancedb"] = True
        except ImportError:
            checks["lancedb"] = False

        all_ready = all(checks.values())

        return {
            "status": "ready" if all_ready else "degraded",
            "checks": checks,
        }

    @app.get("/health/live")
    async def liveness_check():
        """Liveness check for container orchestration."""
        return {"status": "alive"}

    logger.info("Health check endpoints configured")
