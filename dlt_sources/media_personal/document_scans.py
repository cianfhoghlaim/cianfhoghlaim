"""
Apple Photos Document Scan Router — DLT source 2 of 3 in
`dlt_sources/apple_photos/`.

Reads the `apple_photos` table (populated by
`library_export.apple_photos_source`), filters rows where
`is_document_scan=true`, and routes each document scan to
paperless-ngx via `docling-serve` OCR. The paperless-ngx
upload metadata + the canonical archive copy both land in the
`apple_photos_documents_routed` DuckLake table.

Privacy gate: document scans are routed regardless of GPS
gate state (no GPS is needed for document OCR). The
`latitude` / `longitude` columns are populated ONLY when
`LEABHARLANN_PHOTOS_INCLUDE_GPS=true` (otherwise NULL).

Graceful degradation: if paperless-ngx is unreachable, the
source yields a `routed_to_paperless_at=NULL` row with the
`routing_error` column populated; the `documents_route`
Dagster asset re-tries failed rows on its next run.

This is DLT source 2 of 3 — the 3rd is `vehicles.py` (the
license plate OCR pipeline). The DLT source order mirrors
the Apple Photos ingestion pipeline order: library export
→ document routing → vehicle routing.
"""
from __future__ import annotations

import os
import pathlib
import time
from collections.abc import Iterator
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

# Privacy gate — defaults to false (GPS off)
PRIVACY_GATE = os.getenv("LEABHARLANN_PHOTOS_INCLUDE_GPS", "false").lower() == "true"

# paperless-ngx + docling-serve configuration
PAPERLESS_URL = os.getenv("PAPERLESS_URL", "http://paperless-ngx:8000")
PAPERLESS_CONSUMER_TOKEN = os.getenv("PAPERLESS_CONSUMER_TOKEN", "")
DOCLING_SERVE_URL = os.getenv("DOCLING_SERVE_URL", "http://docling-serve:5001")


def _post_to_paperless(file_path: str, photo_id: str) -> dict[str, Any]:
    """Upload the file to paperless-ngx via `docling-serve` OCR.

    Returns a dict with `paperless_task_id` (str) and
    `paperless_document_id` (int). Returns an empty dict on
    failure (the caller fills `routing_error` from the exception).
    """
    try:
        import requests
    except ImportError:
        logger.debug("_post_to_paperless: requests not installed")
        return {"paperless_task_id": "", "paperless_document_id": 0}

    # Step 1: Run docling-serve OCR (one quick call per photo)
    try:
        with open(file_path, "rb") as f:
            r = requests.post(
                f"{DOCLING_SERVE_URL}/v1/convert/file",
                files={"file": (pathlib.Path(file_path).name, f, "image/jpeg")},
                timeout=60,
            )
        if r.status_code != 200:
            return {
                "paperless_task_id": "",
                "paperless_document_id": 0,
                "routing_error": f"docling-serve returned {r.status_code}",
            }
        docling_payload = r.json()
    except Exception as e:
        return {
            "paperless_task_id": "",
            "paperless_document_id": 0,
            "routing_error": f"docling-serve call failed: {e}",
        }

    # Step 2: Upload to paperless-ngx with the OCR'd text as a tag
    try:
        headers = {
            "Authorization": f"Token {PAPERLESS_CONSUMER_TOKEN}",
        }
        with open(file_path, "rb") as f:
            r = requests.post(
                f"{PAPERLESS_URL}/api/documents/post_document/",
                files={"document": (pathlib.Path(file_path).name, f, "image/jpeg")},
                data={
                    "title": photo_id,
                    "tags": ["apple-photos", f"docling-{docling_payload.get('document_type', 'other')}"],
                },
                headers=headers,
                timeout=60,
            )
        if r.status_code in (200, 201):
            response = r.json()
            return {
                "paperless_task_id": response.get("task_id", ""),
                "paperless_document_id": int(response.get("id", 0)),
                "routing_error": "",
            }
        return {
            "paperless_task_id": "",
            "paperless_document_id": 0,
            "routing_error": f"paperless returned {r.status_code}: {r.text[:200]}",
        }
    except Exception as e:
        return {
            "paperless_task_id": "",
            "paperless_document_id": 0,
            "routing_error": f"paperless call failed: {e}",
        }


@dlt.source(name="apple_photos_documents")
def apple_photos_documents_source(
    base_path: str | pathlib.Path = "",
    include_gps: bool = PRIVACY_GATE,
) -> Any:
    """Read the apple_photos DuckLake table + filter document scans.

    Parameters
    ----------
    base_path : str | pathlib.Path
        Unused — kept for API symmetry with `library_export.py`.
        The source reads from the `apple_photos` DuckLake table.
    include_gps : bool
        Whether to include EXIF GPS coordinates in the routed
        records. Defaults to `LEABHARLANN_PHOTOS_INCLUDE_GPS=false`.

    Yields
    ------
    DocumentRoutedRow
        One row per document scan, with paperless-ngx routing metadata.
    """
    return _documents_router(include_gps=include_gps)


@dlt.resource(
    name="apple_photos_documents_routed",
    write_disposition="merge",
    primary_key="photo_id",
)
def _documents_router(include_gps: bool) -> Iterator[dict[str, Any]]:
    """Read apple_photos where is_document_scan=true → route to paperless.

    This is a 2-stage pipeline:

    1. Read `apple_photos` (DuckLake table populated by
       `library_export.apple_photos_source`)
    2. For each row with `is_document_scan=true`:
       a. POST to docling-serve (OCR)
       b. POST to paperless-ngx (upload)
       c. Yield a row with the routing metadata

    The DuckDB connection is opened via the canonical
    `dlt_sources.common.destinations_cianfhoghlaim` helper so the
    routing asset reads from the same `md:cianfhoghlaim` MotherDuck
    database that the library_export asset writes to.
    """
    try:
        import duckdb
    except ImportError:
        logger.warning(
            "apple_photos_documents_source: duckdb not installed; "
            "returning empty source"
        )
        return iter([])

    try:
        conn = duckdb.connect("md:cianfhoghlaim")
    except Exception as e:
        logger.warning(
            "apple_photos_documents_source: cannot connect to md:cianfhoghlaim: %s",
            e,
        )
        return iter([])

    # Stage 1: read apple_photos
    try:
        rows = conn.execute(
            """
            SELECT photo_id, capture_date, latitude, longitude, camera_model,
                   width, height, file_path, file_hash, is_screenshot,
                   is_document_scan, has_vehicle_hint, routed_to_paperless_at
            FROM cianfhoghlaim.apple_photos.apple_photos
            WHERE is_document_scan = TRUE
            ORDER BY capture_date DESC
            """
        ).fetchall()
    except Exception as e:
        logger.warning(
            "apple_photos_documents_source: cannot read apple_photos: %s; "
            "(the table may not exist yet — library_export must run first)",
            e,
        )
        return iter([])

    routed_count = 0
    for row in rows:
        (
            photo_id,
            capture_date,
            latitude,
            longitude,
            camera_model,
            width,
            height,
            file_path,
            file_hash,
            is_screenshot,
            is_document_scan,
            has_vehicle_hint,
            routed_to_paperless_at,
        ) = row

        # Skip already-routed photos (idempotent merge)
        if routed_to_paperless_at:
            continue

        # Apply the privacy gate at the source layer too
        if not include_gps:
            latitude = None
            longitude = None

        # Stage 2: route to paperless-ngx
        routing_meta = _post_to_paperless(file_path, photo_id)
        routed_at = (
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            if routing_meta.get("paperless_document_id", 0) > 0
            else None
        )

        yield {
            "photo_id": photo_id,
            "capture_date": capture_date,
            "latitude": latitude,
            "longitude": longitude,
            "camera_model": camera_model,
            "file_path": file_path,
            "file_hash": file_hash,
            "is_screenshot": bool(is_screenshot),
            "has_vehicle_hint": bool(has_vehicle_hint),
            "paperless_task_id": routing_meta.get("paperless_task_id", ""),
            "paperless_document_id": int(routing_meta.get("paperless_document_id", 0)),
            "routed_to_paperless_at": routed_at,
            "routing_error": routing_meta.get("routing_error", ""),
        }
        routed_count += 1
        if routed_count % 100 == 0:
            logger.info(
                "apple_photos_documents: routed %d document scans so far",
                routed_count,
            )
    logger.info(
        "apple_photos_documents: routed %d document scans total", routed_count
    )


__all__ = [
    "DOCLING_SERVE_URL",
    "PAPERLESS_CONSUMER_TOKEN",
    "PAPERLESS_URL",
    "PRIVACY_GATE",
    "apple_photos_documents_source",
]
