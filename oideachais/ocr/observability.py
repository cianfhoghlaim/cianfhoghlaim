"""
OCR Observability Module.

Provides Langfuse and Datadog instrumentation for OCR operations:
- Per-extraction cost tracking
- Latency monitoring
- Error rate tracking
- Model comparison metrics

Usage:
    from oideachais.data_platform.ocr.observability import OCRObservability, traced_ocr

    obs = OCRObservability()

    @traced_ocr(obs)
    async def my_ocr_function(...):
        ...

    # Or use directly
    with obs.trace_extraction("paddleocr", "image.png"):
        result = await adapter.process_image(image)
"""

from __future__ import annotations

import functools
import logging
import os
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Lazy imports
_langfuse_client = None
_datadog_tracer = None


def _get_langfuse():
    """Lazy load Langfuse client."""
    global _langfuse_client
    if _langfuse_client is None:
        try:
            from langfuse import Langfuse

            _langfuse_client = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
                host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
            )
        except ImportError:
            logger.debug("Langfuse not installed")
            return None
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse: {e}")
            return None
    return _langfuse_client


def _get_datadog_tracer():
    """Lazy load Datadog tracer."""
    global _datadog_tracer
    if _datadog_tracer is None:
        try:
            from ddtrace import tracer

            _datadog_tracer = tracer
        except ImportError:
            logger.debug("Datadog not installed")
            return None
    return _datadog_tracer


# Cost estimates per extraction (approximate)
OCR_MODEL_COSTS = {
    "paddleocr-v4": {"per_page": 0.0, "per_1k_chars": 0.0},  # Self-hosted
    "docling-v2": {"per_page": 0.0, "per_1k_chars": 0.0},  # Self-hosted
    "dots-ocr": {"per_page": 0.001, "per_1k_chars": 0.0001},  # API-based
    "unstract-v1": {"per_page": 0.002, "per_1k_chars": 0.0},  # API-based
    "olmocr2-7b": {"per_page": 0.0, "per_1k_chars": 0.0},  # Local MLX
    "gemini-vision": {"per_page": 0.0025, "per_1k_chars": 0.0},  # Cloud API
    "claude-vision": {"per_page": 0.01, "per_1k_chars": 0.0},  # Cloud API
}


@dataclass
class OCRExtractionMetrics:
    """Metrics for an OCR extraction."""

    model_id: str
    backend: str
    latency_ms: float
    char_count: int
    page_count: int
    confidence: float
    estimated_cost: float = 0.0
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "backend": self.backend,
            "latency_ms": self.latency_ms,
            "char_count": self.char_count,
            "page_count": self.page_count,
            "confidence": self.confidence,
            "estimated_cost": round(self.estimated_cost, 6),
            "success": self.success,
            "error": self.error,
        }


class OCRObservability:
    """
    Observability wrapper for OCR operations.

    Provides:
    - Langfuse cost tracking
    - Datadog APM tracing
    - Aggregated metrics
    """

    def __init__(
        self,
        project_name: str = "oideachas-ocr",
        service_name: str = "ocr-pipeline",
    ):
        self.project_name = project_name
        self.service_name = service_name
        self._session_id = f"ocr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._metrics: list[OCRExtractionMetrics] = []

    @contextmanager
    def trace_extraction(
        self,
        model_id: str,
        source_name: str,
        page_count: int = 1,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Context manager for tracing an OCR extraction.

        Args:
            model_id: OCR model identifier
            source_name: Name of source document/image
            page_count: Number of pages
            metadata: Additional metadata

        Yields:
            Trace context that can be updated with results

        Example:
            with obs.trace_extraction("paddleocr-v4", "image.png") as ctx:
                result = await adapter.process_image(image)
                ctx.set_result(result.text, result.confidence)
        """
        start_time = time.time()
        trace_ctx = _TraceContext(model_id, source_name, page_count, metadata or {})

        # Start Datadog span
        dd_tracer = _get_datadog_tracer()
        dd_span = None
        if dd_tracer:
            dd_span = dd_tracer.trace(
                "ocr.extraction",
                service=self.service_name,
                resource=model_id,
            )
            dd_span.set_tag("ocr.model_id", model_id)
            dd_span.set_tag("ocr.source", source_name)
            dd_span.set_tag("ocr.page_count", page_count)

        try:
            yield trace_ctx

        finally:
            latency_ms = (time.time() - start_time) * 1000

            # Calculate cost
            model_costs = OCR_MODEL_COSTS.get(model_id, {"per_page": 0.0, "per_1k_chars": 0.0})
            estimated_cost = (
                page_count * model_costs["per_page"] +
                (trace_ctx.char_count / 1000) * model_costs["per_1k_chars"]
            )

            # Create metrics
            metrics = OCRExtractionMetrics(
                model_id=model_id,
                backend=trace_ctx.metadata.get("backend", "unknown"),
                latency_ms=latency_ms,
                char_count=trace_ctx.char_count,
                page_count=page_count,
                confidence=trace_ctx.confidence,
                estimated_cost=estimated_cost,
                success=trace_ctx.success,
                error=trace_ctx.error,
            )
            self._metrics.append(metrics)

            # Log to Langfuse
            self._log_to_langfuse(metrics, source_name, trace_ctx.metadata)

            # Complete Datadog span
            if dd_span:
                dd_span.set_tag("ocr.char_count", trace_ctx.char_count)
                dd_span.set_tag("ocr.confidence", trace_ctx.confidence)
                dd_span.set_tag("ocr.latency_ms", latency_ms)
                dd_span.set_tag("ocr.estimated_cost", estimated_cost)
                if trace_ctx.error:
                    dd_span.set_tag("error", True)
                    dd_span.set_tag("error.message", trace_ctx.error)
                dd_span.finish()

    def _log_to_langfuse(
        self,
        metrics: OCRExtractionMetrics,
        source_name: str,
        metadata: dict[str, Any],
    ) -> None:
        """Log extraction to Langfuse."""
        langfuse = _get_langfuse()
        if langfuse is None:
            return

        try:
            trace = langfuse.trace(
                name=f"ocr_{metrics.model_id}",
                session_id=self._session_id,
                metadata={
                    "project": self.project_name,
                    "source": source_name,
                    **metadata,
                },
                tags=["ocr", "celtic-education", metrics.model_id],
            )

            # Create span for the extraction
            span = trace.span(
                name="extraction",
                metadata=metrics.to_dict(),
            )
            span.end()

            # Add scores
            langfuse.score(
                trace_id=trace.id,
                name="confidence",
                value=metrics.confidence,
            )

            langfuse.score(
                trace_id=trace.id,
                name="latency_ms",
                value=metrics.latency_ms,
            )

            langfuse.score(
                trace_id=trace.id,
                name="cost_usd",
                value=metrics.estimated_cost,
            )

            langfuse.flush()

        except Exception as e:
            logger.warning(f"Failed to log to Langfuse: {e}")

    def log_comparison(
        self,
        results: dict[str, Any],
        source_name: str,
    ) -> None:
        """
        Log a multi-model comparison to observability.

        Args:
            results: Dict mapping model_id to OCRResult
            source_name: Name of source document
        """
        langfuse = _get_langfuse()
        dd_tracer = _get_datadog_tracer()

        if langfuse:
            try:
                trace = langfuse.trace(
                    name="ocr_comparison",
                    session_id=self._session_id,
                    metadata={
                        "project": self.project_name,
                        "source": source_name,
                        "models": list(results.keys()),
                    },
                    tags=["ocr", "comparison", "celtic-education"],
                )

                for model_id, result in results.items():
                    if hasattr(result, "to_dict"):
                        result_dict = result.to_dict()
                    else:
                        result_dict = {"text": str(result)}

                    span = trace.span(
                        name=f"model_{model_id}",
                        metadata=result_dict,
                    )
                    span.end()

                langfuse.flush()

            except Exception as e:
                logger.warning(f"Failed to log comparison to Langfuse: {e}")

        if dd_tracer:
            with dd_tracer.trace("ocr.comparison", service=self.service_name) as span:
                span.set_tag("ocr.model_count", len(results))
                span.set_tag("ocr.source", source_name)
                for model_id in results.keys():
                    span.set_tag(f"ocr.models.{model_id}", True)

    def get_session_summary(self) -> dict[str, Any]:
        """Get summary of all extractions in this session."""
        if not self._metrics:
            return {
                "count": 0,
                "total_cost": 0,
                "avg_latency_ms": 0,
                "success_rate": 0,
            }

        total_cost = sum(m.estimated_cost for m in self._metrics)
        total_latency = sum(m.latency_ms for m in self._metrics)
        success_count = sum(1 for m in self._metrics if m.success)

        # Group by model
        by_model: dict[str, list[OCRExtractionMetrics]] = {}
        for m in self._metrics:
            by_model.setdefault(m.model_id, []).append(m)

        model_summaries = {}
        for model_id, metrics in by_model.items():
            model_summaries[model_id] = {
                "count": len(metrics),
                "total_cost": sum(m.estimated_cost for m in metrics),
                "avg_latency_ms": sum(m.latency_ms for m in metrics) / len(metrics),
                "avg_confidence": sum(m.confidence for m in metrics) / len(metrics),
            }

        return {
            "count": len(self._metrics),
            "total_cost": round(total_cost, 6),
            "avg_latency_ms": total_latency / len(self._metrics),
            "success_rate": success_count / len(self._metrics),
            "by_model": model_summaries,
        }


class _TraceContext:
    """Internal context for tracking extraction results."""

    def __init__(
        self,
        model_id: str,
        source_name: str,
        page_count: int,
        metadata: dict[str, Any],
    ):
        self.model_id = model_id
        self.source_name = source_name
        self.page_count = page_count
        self.metadata = metadata
        self.char_count = 0
        self.confidence = 0.0
        self.success = True
        self.error: str | None = None

    def set_result(
        self,
        text: str,
        confidence: float,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Set successful result."""
        self.char_count = len(text)
        self.confidence = confidence
        self.success = True
        if metadata:
            self.metadata.update(metadata)

    def set_error(self, error: str) -> None:
        """Set error result."""
        self.success = False
        self.error = error
        self.confidence = 0.0


def traced_ocr(obs: OCRObservability):
    """
    Decorator to trace OCR functions.

    The decorated function should return an OCRResult-like object
    with text, confidence, and model_id attributes.

    Usage:
        obs = OCRObservability()

        @traced_ocr(obs)
        async def process_document(image_path: str):
            adapter = get_adapter("paddleocr")
            return await adapter.process_image(image_path)
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Try to extract source name from args
            source_name = "unknown"
            if args:
                first_arg = args[0]
                if hasattr(first_arg, "name"):
                    source_name = first_arg.name
                elif isinstance(first_arg, str):
                    source_name = first_arg

            with obs.trace_extraction("auto", source_name) as ctx:
                result = await func(*args, **kwargs)

                if hasattr(result, "text") and hasattr(result, "confidence"):
                    ctx.model_id = getattr(result, "model_id", "unknown")
                    ctx.set_result(result.text, result.confidence)
                    if hasattr(result, "metadata"):
                        ctx.metadata.update(result.metadata)

                return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            source_name = "unknown"
            if args:
                first_arg = args[0]
                if hasattr(first_arg, "name"):
                    source_name = first_arg.name
                elif isinstance(first_arg, str):
                    source_name = first_arg

            with obs.trace_extraction("auto", source_name) as ctx:
                result = func(*args, **kwargs)

                if hasattr(result, "text") and hasattr(result, "confidence"):
                    ctx.model_id = getattr(result, "model_id", "unknown")
                    ctx.set_result(result.text, result.confidence)

                return result

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Global instance for convenience
_default_obs: OCRObservability | None = None


def get_ocr_observability() -> OCRObservability:
    """Get or create the default OCR observability instance."""
    global _default_obs
    if _default_obs is None:
        _default_obs = OCRObservability()
    return _default_obs
