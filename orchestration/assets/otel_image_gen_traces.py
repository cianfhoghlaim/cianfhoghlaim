"""orchestration/assets/otel_image_gen_traces.py — OTel spans for the asset-gen chain.

Per the 2026-10-05-lakehouse-ml-assetgen-wiring-v1 saga change (Plan 5 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Emits OTel spans for the full chain:
  DLT load → BAML extract → CocoIndex embed → image-gen litellm → LanceDB upsert

The chain is traced via the opentelemetry-instrumentation decorators + a
manual span manager. Falls back to a no-op when the OTel SDK isn't
installed (offline dev mode).

Reference: openspec/specs/lakehouse-assetgen-wiring/spec.md (R3: OTel spans)
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


# Lazy OTel import (graceful degradation when SDK isn't installed)
try:
    from opentelemetry import trace  # type: ignore[import-not-found]
    from opentelemetry.trace import Status, StatusCode  # type: ignore[import-not-found]
    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False
    trace = None  # type: ignore[assignment]
    Status = None  # type: ignore[assignment]
    StatusCode = None  # type: ignore[assignment]


# The canonical asset-gen chain tracer name
TRACER_NAME = "cianfhoghlaim.asset_generation"


def _get_tracer():
    """Return the OTel tracer (or a no-op tracer if SDK is missing)."""
    if not _HAS_OTEL:
        return None
    return trace.get_tracer(TRACER_NAME)


def trace_image_gen_chain(
    *,
    asset_id: str,
    subject: str,
    role: str,
    prompt_sha256: str,
    litellm_alias: str,
    lancedb_table: str,
    operation: str = "image_gen_chain",
):
    """Decorator + context manager for the full DLT → BAML → image-gen → LanceDB chain.

    Usage:
        with trace_image_gen_chain(asset_id=..., subject=..., ...) as span:
            dlt.load(...)
            baml.extract(...)
            cocoindex.embed(...)
            litellm.image_gen(...)
            lancedb.upsert(...)

    Or as a decorator:
        @trace_image_gen_chain(asset_id=..., subject=..., ...)
        def my_chain():
            ...

    Args:
        asset_id: The asset UUID
        subject: The NCCA subject (e.g. "chemistry")
        role: The image_gen role (default / fast / bilingual / legacy / diagrams)
        prompt_sha256: SHA-256 of the input prompt
        litellm_alias: The litellm_alias of the called model
        lancedb_table: The target LanceDB table name
        operation: The operation name for the OTel span
    """
    attrs = {
        "asset.asset_id": asset_id,
        "asset.subject": subject,
        "asset.role": role,
        "asset.prompt_sha256": prompt_sha256,
        "asset.litellm_alias": litellm_alias,
        "asset.lancedb_table": lancedb_table,
    }

    if not _HAS_OTEL:
        # Offline dev mode: return a no-op context manager
        class _NoOpCM:
            def __enter__(self):
                return None
            def __exit__(self, *a):
                return False
        return _NoOpCM()

    tracer = _get_tracer()
    return tracer.start_as_current_span(operation, attributes=attrs)


def trace_dlt_load(**attrs):
    """Span for the DLT load step."""
    if not _HAS_OTEL:
        class _NoOp:
            def __enter__(self): return None
            def __exit__(self, *a): return False
        return _NoOp()
    return _get_tracer().start_as_current_span("dlt.load", attributes=attrs)


def trace_baml_extract(**attrs):
    """Span for the BAML extract step."""
    if not _HAS_OTEL:
        class _NoOp:
            def __enter__(self): return None
            def __exit__(self, *a): return False
        return _NoOp()
    return _get_tracer().start_as_current_span("baml.extract", attributes=attrs)


def trace_cocoindex_embed(**attrs):
    """Span for the CocoIndex embed step."""
    if not _HAS_OTEL:
        class _NoOp:
            def __enter__(self): return None
            def __exit__(self, *a): return False
        return _NoOp()
    return _get_tracer().start_as_current_span("cocoindex.embed", attributes=attrs)


def trace_litellm_image_gen(**attrs):
    """Span for the LiteLLM image-gen step."""
    if not _HAS_OTEL:
        class _NoOp:
            def __enter__(self): return None
            def __exit__(self, *a): return False
        return _NoOp()
    return _get_tracer().start_as_current_span("image_gen.litellm", attributes=attrs)


def trace_lancedb_upsert(**attrs):
    """Span for the LanceDB upsert step."""
    if not _HAS_OTEL:
        class _NoOp:
            def __enter__(self): return None
            def __exit__(self, *a): return False
        return _NoOp()
    return _get_tracer().start_as_current_span("lancedb.upsert", attributes=attrs)


# The OTel collector endpoint (the lakehouse otel-collector service)
OTEL_COLLECTOR_ENDPOINT = os.environ.get(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"
)


def configure_otel_sdk() -> None:
    """Configure the OTel SDK to export to the lakehouse OTel collector.

    Idempotent: calling this multiple times is safe. Falls back to a
    no-op when the SDK isn't installed.
    """
    if not _HAS_OTEL:
        logger.debug("opentelemetry SDK not available — skipping configure")
        return

    try:
        from opentelemetry import trace  # noqa: F401
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        resource = Resource.create({"service.name": "cianfhoghlaim-asset-gen"})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=f"{OTEL_COLLECTOR_ENDPOINT}/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        logger.info("OTel SDK configured → %s", OTEL_COLLECTOR_ENDPOINT)
    except Exception as exc:
        logger.warning("configure_otel_sdk failed: %s", exc)


__all__ = [
    "TRACER_NAME",
    "trace_image_gen_chain",
    "trace_dlt_load",
    "trace_baml_extract",
    "trace_cocoindex_embed",
    "trace_litellm_image_gen",
    "trace_lancedb_upsert",
    "configure_otel_sdk",
    "OTEL_COLLECTOR_ENDPOINT",
]
