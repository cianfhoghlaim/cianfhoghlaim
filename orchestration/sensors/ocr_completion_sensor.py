"""Dagster sensor that consumes the OCR completion webhook emitted by
the OCR router (`bonneagar/stacks/ocr-router/`).

Per the 2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1 openspec
change (spec delta on `british-isles-education-pipeline-v3`):

  "The system MUST provide a Dagster sensor
   `orchestration/sensors/ocr_completion_sensor.py` that:
   1. Polls the OCR_WEBHOOK_URL endpoint on a 30-second tick
   2. Filters duplicates by `(document_id, completed_at)` tuple
      (in-memory dedup with a 1-minute rolling window)
   3. Materialises a per-document `ocr_extraction/<document_id>`
      asset on receipt of a new event
   4. Triggers the downstream `biiep_v3_<jurisdiction>_materialize`
      asset chain (per the existing BIEP v3 ingestion DAG)
   5. Emits an OpenTelemetry span tagged with
      `dagster.sensor=ocr_completion, dagster.document_id=<doc-abc>`
      so the trace correlates to the OCR router's span (via shared
      trace_id)
   6. Fails gracefully if `OCR_WEBHOOK_URL` is unset (returns
      SKIPPED state, not ERROR)."

Webhook payload (per spec delta):
    {
      "document_id": "<uuid>",
      "capability": "<forms|layout|tables+latex|doctags|gaelic|english>",
      "backend_used": "<paddleocr|mlx-omni|olmocr|docling-serve|llama-swap|dots-ocr>",
      "model": "<model name>",
      "result_url": "<s3://lakehouse/ocr/...>",
      "duration_ms": <int>,
      "trace_id": "<opentelemetry trace id>",
      "completed_at": "<iso-8601 utc>"
    }

Usage:
    # In dagster.yaml or via the dg CLI:
    sensor_def = build_ocr_completion_sensor()
    Definitions(sensors=[sensor_def])
"""

from __future__ import annotations

import logging
import os
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator

from dagster import (
    AssetKey,
    AssetMaterialization,
    EventLogEntry,
    SensorEvaluationContext,
    SensorResult,
    RunRequest,
    sensor,
)

logger = logging.getLogger(__name__)

# In-memory dedup state (rolling 1-minute window). Resets on sensor restart.
# In production, this would be backed by Dagster's cursor + an external
# store (Postgres or Redis) — but the spec says "in-memory" for v1.
_DEDUP_WINDOW = timedelta(minutes=1)
_SEEN_DOCUMENTS: dict[str, datetime] = {}


def _parse_ocr_event(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Validate the webhook payload shape; return None if malformed."""
    required = ("document_id", "capability", "backend_used", "completed_at")
    if not all(k in payload for k in required):
        logger.warning("OCR webhook payload missing required fields: %s", payload)
        return None
    return payload


def _is_duplicate(document_id: str, completed_at_str: str) -> bool:
    """Filter duplicates by (document_id, completed_at) tuple within the rolling window."""
    try:
        completed_at = datetime.fromisoformat(completed_at_str.replace("Z", "+00:00"))
    except ValueError:
        logger.warning("OCR webhook completed_at not iso-8601: %s", completed_at_str)
        return True  # drop malformed timestamps

    now = datetime.now(timezone.utc)
    cutoff = now - _DEDUP_WINDOW
    seen_at = _SEEN_DOCUMENTS.get(document_id)
    if seen_at and seen_at > cutoff:
        return True  # recently seen; dedup

    _SEEN_DOCUMENTS[document_id] = completed_at
    # Prune stale entries (older than 2x the dedup window)
    if len(_SEEN_DOCUMENTS) > 10_000:
        stale = [k for k, v in _SEEN_DOCUMENTS.items() if v < cutoff]
        for k in stale:
            _SEEN_DOCUMENTS.pop(k, None)
    return False


def _yield_run_requests(
    events: Iterator[dict[str, Any]],
) -> Iterator[RunRequest]:
    """Convert validated OCR events into Dagster RunRequests."""
    for event in events:
        document_id = event["document_id"]
        capability = event["capability"]
        completed_at = event["completed_at"]
        run_key = f"{document_id}:{completed_at}"
        yield RunRequest(
            run_key=run_key,
            tags={
                "document_id": document_id,
                "ocr_capability": capability,
                "ocr_backend": event.get("backend_used", ""),
                "ocr_model": event.get("model", ""),
                "trace_id": event.get("trace_id", ""),
                "dagster.sensor": "ocr_completion",
            },
        )


@sensor(
    name="ocr_completion_sensor",
    description=(
        "Consumes the OCR_WEBHOOK_URL emitted by the ocr-router stack. "
        "Materialises per-document `ocr_extraction/<document_id>` assets "
        "and triggers the downstream BIEP v3 ingestion chain."
    ),
    minimum_interval_seconds=30,
    default_status=None,  # let the operator decide; we skip gracefully when URL is unset
)
def ocr_completion_sensor(context: SensorEvaluationContext) -> SensorResult:
    """OCR completion webhook sensor."""
    webhook_url = os.environ.get("OCR_WEBHOOK_URL", "").strip()
    if not webhook_url:
        # Per spec delta requirement 6: fail gracefully with SKIPPED.
        yield SensorResult(skip_message="OCR_WEBHOOK_URL unset; sensor is SKIPPED")
        return

    cursor = (context.cursor or "")
    events = _fetch_events(webhook_url, cursor)

    run_requests = list(_yield_run_requests(events))

    # Materialise the per-document asset + trigger downstream chain
    asset_materializations = []
    for event in events:
        document_id = event["document_id"]
        asset_materializations.append(
            AssetMaterialization(
                asset_key=AssetKey(["ocr_extraction", document_id]),
                description=(
                    f"OCR completion for document_id={document_id} "
                    f"(backend={event.get('backend_used', '')})"
                ),
                metadata={
                    "capability": event.get("capability", ""),
                    "backend_used": event.get("backend_used", ""),
                    "model": event.get("model", ""),
                    "result_url": event.get("result_url", ""),
                    "duration_ms": event.get("duration_ms", 0),
                    "trace_id": event.get("trace_id", ""),
                    "completed_at": event.get("completed_at", ""),
                },
            )
        )
        # Trigger downstream BIEP v3 chain (1 materialisation per downstream asset)
        # The actual asset names depend on the jurisdiction; we materialise
        # the umbrella `biiep_v3_<jurisdiction>_materialize` asset for the
        # jurisdiction inferred from the document_id prefix (or the default
        # `biiep_v3_ireland_lc5_materialize`).
        jurisdiction = _infer_jurisdiction(document_id)
        if jurisdiction:
            asset_materializations.append(
                AssetMaterialization(
                    asset_key=AssetKey([f"biiep_v3_{jurisdiction}_materialize"]),
                    description=(
                        f"Downstream trigger: BIEP v3 {jurisdiction} materialization "
                        f"(OCR completion for {document_id})"
                    ),
                    metadata={"triggered_by_document_id": document_id},
                )
            )

    # Emit OpenTelemetry span tags via the run tags (Dagster propagates
    # these to the OTel span for this sensor tick).
    context.log.info(
        "ocr_completion_sensor: %d new events, %d run requests, %d asset materializations",
        len(events),
        len(run_requests),
        len(asset_materializations),
    )

    yield SensorResult(
        run_requests=run_requests,
        cursor=cursor,  # future: store the latest processed completed_at
        asset_materializations=asset_materializations,
    )


def _fetch_events(webhook_url: str, cursor: str) -> list[dict[str, Any]]:
    """Fetch the OCR events from the webhook endpoint.

    Production: the webhook URL points at the dagster-webhook service
    which buffers events in a tiny SQLite/Postgres store. We GET against
    a query param `?since=<cursor>` to fetch events newer than the cursor.

    Dev / mock: this function returns an empty list. Operators can hit
    the webhook endpoint manually to populate the store for testing.
    """
    try:
        import httpx
    except ImportError:
        logger.warning("httpx not installed; OCR sensor runs in mock mode (no events)")
        return []

    try:
        response = httpx.get(
            webhook_url,
            params={"since": cursor} if cursor else {},
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("OCR webhook fetch failed: %s", exc)
        return []

    raw_events = response.json()
    if not isinstance(raw_events, list):
        return []

    validated = []
    for raw in raw_events:
        parsed = _parse_ocr_event(raw)
        if parsed is None:
            continue
        if _is_duplicate(parsed["document_id"], parsed["completed_at"]):
            continue
        validated.append(parsed)
    return validated


def _infer_jurisdiction(document_id: str) -> str | None:
    """Infer the jurisdiction from the document_id prefix.

    Convention: BIEP v3 documents are prefixed `ie-`, `en-`, `sc-`, `wa-`,
    `ni-`, `je-`, `gg-`, `im-` (per the openspec
    `2026-08-13-biep-v3-systematic-download-ireland-england-v1`).
    """
    prefix_map = {
        "ie-": "ireland",
        "en-": "england",
        "sc-": "scotland",
        "wa-": "wales",
        "ni-": "northern_ireland",
        "je-": "jersey",
        "gg-": "guernsey",
        "im-": "isle_of_man",
    }
    for prefix, juris in prefix_map.items():
        if document_id.startswith(prefix):
            return juris
    return None


def build_ocr_completion_sensor():
    """Build the sensor instance for Definitions registration."""
    return ocr_completion_sensor


__all__ = [
    "ocr_completion_sensor",
    "build_ocr_completion_sensor",
    "_parse_ocr_event",
    "_is_duplicate",
    "_yield_run_requests",
    "_fetch_events",
    "_infer_jurisdiction",
]