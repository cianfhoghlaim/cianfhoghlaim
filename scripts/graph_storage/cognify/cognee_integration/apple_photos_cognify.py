"""
oideachais.cognee_integration.apple_photos_cognify — Cognee cognify
helper for the Apple Photos corpus (the 5th leabharlann corpus).

The dataset name is `leabharlann_apple_photos`. It joins the
existing 4 leabharlann cognify datasets:

1. `leabharlann_books`        — UoG coursework + thesis PDFs
2. `leabharlann_zotero`       — Zotero paper library
3. `leabharlann_takeout`      — Google Takeout export
4. `oideachais_email_inbox`   — Email inbox (legal + research)
5. `leabharlann_apple_photos` — **NEW in Phase D**: macOS Photos export

Edge types produced by the cognify pass (Cognee LLM-driven):

- `Photo -> Location` (when GPS is enabled)
- `Photo -> CameraModel` (always — derived from EXIF)
- `Photo -> Vehicle` (when `has_vehicle_hint=true`)
- `DocumentScan -> DoclingClassification` (when
  `is_document_scan=true` and routed to paperless-ngx)

The cross-archive edge population is in
`oideachais.cognify_rules.leabharlann_apple_photos_cross_archive.populate_cross_archive_edges`
(FalkorDB MERGE queries), which runs after this cognify pass.

Reference: per the
`openspec/changes/2026-08-23-phase-d-apple-photos-implementation-v1/`
change (Phase D of the lakehouse plan) + the
`apple-photos-ingestion` spec.
"""

from __future__ import annotations

import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


DATASET_APPLE_PHOTOS = "leabharlann_apple_photos"

# 4 node types + 4 edge types in the apple_photos graph
NODE_TYPES = [
    "Photo",
    "Location",
    "CameraModel",
    "Vehicle",
    "DocumentScan",
    "DoclingClassification",
]

EDGE_TYPES = [
    "Photo-LOCATED_AT->Location",
    "Photo-CAPTURED_WITH->CameraModel",
    "Photo-CONTAINS->Vehicle",
    "DocumentScan-CLASSIFIED_AS->DoclingClassification",
]

# Privacy gate — defaults to false (GPS off)
PRIVACY_GATE = os.getenv("LEABHARLANN_PHOTOS_INCLUDE_GPS", "false").lower() == "true"


async def cognify_apple_photos_rows(
    rows: list[dict[str, Any]],
    *,
    dataset: str = DATASET_APPLE_PHOTOS,
    include_gps: bool = PRIVACY_GATE,
) -> dict[str, Any]:
    """Cognify a batch of apple_photos rows into the Cognee graph.

    The function is a no-op in test mode (`USE_LOCAL_SCRAPES=true`)
    and a `cognee.add` + `cognee.cognify` call in production.

    Parameters
    ----------
    rows
        A list of dicts. The expected shape is the BAML-extracted
        row produced by `dlt_sources.apple_photos.library_export` +
        the 2 routing assets (`document_scans`, `vehicles`). For
        GPS-gated cognification, the row has `latitude` +
        `longitude` populated; otherwise they're `None`.
    dataset
        Override dataset name. Defaults to
        `leabharlann_apple_photos`.
    include_gps
        Whether to include GPS coordinates in the cognify input.
        Defaults to `LEABHARLANN_PHOTOS_INCLUDE_GPS=false`.

    Returns
    -------
    dict[str, Any]
        `{"dataset": str, "rows": int, "edges": int, "stub": bool,
          "gps_gate": str}`.
    """
    if dataset != DATASET_APPLE_PHOTOS:
        raise ValueError(f"unknown apple_photos dataset: {dataset}")

    # Apply the privacy gate at the cognify layer too (defense-in-depth)
    if not include_gps:
        rows = [
            {**row, "latitude": None, "longitude": None} for row in rows
        ]

    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "apple_photos_cognify_skipped_stub_mode",
            dataset=dataset,
            rows=len(rows),
            gps_gate="on" if include_gps else "off",
        )
        return {
            "dataset": dataset,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
            "gps_gate": "on" if include_gps else "off",
        }

    try:
        import cognee  # type: ignore[import-not-found]
    except ImportError:
        logger.warning(
            "cognee_not_available_skipping_cognify", dataset=dataset
        )
        return {
            "dataset": dataset,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
            "gps_gate": "on" if include_gps else "off",
        }

    for row in rows:
        # Cognee accepts both text strings and structured dicts; we
        # serialise the dict as a JSON line so the LLM can parse it.
        import json

        payload = json.dumps(row, default=str)
        await cognee.add(payload, dataset_name=dataset)
    await cognee.cognify()
    return {
        "dataset": dataset,
        "rows": len(rows),
        "edges": len(rows) * 2,  # Cognee generates ~2 edges per row
        "stub": False,
        "gps_gate": "on" if include_gps else "off",
    }


def _row_to_text(row: dict[str, Any]) -> str:
    """Serialise an apple_photos row to a Cognee-friendly text blob.

    Used by the `cross_archive_edges` rule pass to compute deterministic
    edge keys (e.g. `photo_id` normalisation for `CAPTURED_WITH`
    matches). The privacy gate is applied here too — when the gate
    is off, `latitude`/`longitude` are stripped from the text blob
    so they can't leak into cross-archive rules.
    """
    import json

    safe_row = dict(row)
    if not PRIVACY_GATE:
        safe_row.pop("latitude", None)
        safe_row.pop("longitude", None)
    return json.dumps(safe_row, default=str, sort_keys=True)


__all__ = [
    "DATASET_APPLE_PHOTOS",
    "EDGE_TYPES",
    "NODE_TYPES",
    "PRIVACY_GATE",
    "_row_to_text",
    "cognify_apple_photos_rows",
]
