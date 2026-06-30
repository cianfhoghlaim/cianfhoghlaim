"""Apple Photos routing Dagster assets — the 2 destination flows.

Added in the `2026-06-30-agent-platform-cluster-hermes-cocoindex` change.
Companion to the 5 Apple Photos assets in `apple_photos_assets.py`.

1. `apple_photos_document_scan_route` — for each row in
   `apple_photos_metadata` where `is_document_scan = true`, calls
   `docling-serve` to OCR + classify, then POSTs to `paperless-ngx`.
2. `apple_photos_vehicle_route` — for each row in
   `apple_photos_metadata` where `has_vehicle_hint = true`, calls
   `paddleocr` for the plate + `dots-ocr` for make/model, then
   writes to the `vehicle_observations` DuckLake table.

Plus the cross-frame velocity inference:
3. `apple_photos_vehicle_cross_frame` — joins successive photos of
   the same `plate_text` within 60 seconds and computes
   `velocity_estimate_mps` from GPS delta / time delta.
"""
from __future__ import annotations

import os
import time
from collections.abc import Iterator
from datetime import datetime

import requests
import structlog
from dagster import AssetExecutionContext, asset

logger = structlog.get_logger(__name__)


# Configurable thresholds (env-overridable)
CROSS_FRAME_MIN_GPS_M = float(os.getenv("APPLE_PHOTOS_CROSS_FRAME_MIN_GPS_M", "50"))
CROSS_FRAME_MAX_TIME_S = float(os.getenv("APPLE_PHOTOS_CROSS_FRAME_MAX_TIME_S", "120"))


@asset(
    group_name="apple_photos_routing",
    compute_kind="ocr",
    description="Route document scans to paperless-ngx via docling-serve.",
)
def apple_photos_document_scan_route(
    context: AssetExecutionContext,
) -> Iterator[str]:
    """For each `is_document_scan=true` row, OCR + POST to paperless-ngx."""
    context.log.info("[apple_photos_document_scan_route] starting")
    docling_url = os.getenv("DOCLING_SERVE_URL", "http://docling-serve:5001")
    paperless_url = os.getenv("PAPERLESS_URL", "http://paperless-ngx:8000")
    paperless_token = os.getenv("PAPERLESS_CONSUMER_TOKEN", "")

    # Fetch the next batch of un-routed document scans
    un_routed = _fetch_unrouted_document_scans(limit=20)
    routed_count = 0
    for photo in un_routed:
        try:
            # 1. OCR via docling-serve
            with open(photo["file_path"], "rb") as f:
                ocr_response = requests.post(
                    f"{docling_url}/v1/convert/file",
                    files={"file": (photo["photo_id"], f, "image/jpeg")},
                    timeout=60,
                )
            if not ocr_response.ok:
                context.log.warning(
                    f"[apple_photos_document_scan_route] docling-serve failed for {photo['photo_id']}"
                )
                continue

            ocr_data = ocr_response.json()
            doc_text = ocr_data.get("text", "")
            doc_type = ocr_data.get("document_type", "other")

            # 2. POST to paperless-ngx
            paperless_response = requests.post(
                f"{paperless_url}/api/documents/post_document/",
                headers={"Authorization": f"Token {paperless_token}"},
                files={
                    "document": (
                        f"{photo['photo_id']}.pdf",
                        doc_text.encode("utf-8"),
                        "application/pdf",
                    )
                },
                data={
                    "title": f"{doc_type} {photo['photo_id']}",
                    "tags": f"apple_photos,{doc_type},capture_date_{photo['capture_date']}",
                },
                timeout=60,
            )
            if paperless_response.ok:
                # 3. Mark as routed
                _mark_routed_to_paperless(photo["photo_id"])
                routed_count += 1
                context.log.info(
                    f"[apple_photos_document_scan_route] routed {photo['photo_id']} to paperless-ngx"
                )
        except Exception as e:
            logger.warning(
                "[apple_photos_document_scan_route] failed for %s: %s",
                photo["photo_id"], e,
            )
    context.log.info(
        f"[apple_photos_document_scan_route] routed {routed_count} document scans"
    )
    yield f"routed {routed_count} document scans"


@asset(
    group_name="apple_photos_routing",
    compute_kind="vision",
    description="Route vehicle photos to the vehicle_observations table via paddleocr + dots-ocr.",
)
def apple_photos_vehicle_route(
    context: AssetExecutionContext,
) -> Iterator[str]:
    """For each `has_vehicle_hint=true` row, plate-OCR + make/model + insert."""
    context.log.info("[apple_photos_vehicle_route] starting")
    paddleocr_url = os.getenv("PADDLEOCR_URL", "http://paddleocr:5000")
    dots_ocr_url = os.getenv("DOTS_OCR_URL", "http://dots-ocr:5000")

    un_routed = _fetch_unrouted_vehicle_photos(limit=20)
    routed_count = 0
    for photo in un_routed:
        try:
            # 1. Plate OCR via paddleocr
            with open(photo["file_path"], "rb") as f:
                plate_response = requests.post(
                    f"{paddleocr_url}/predict",
                    files={"image": (photo["photo_id"], f, "image/jpeg")},
                    timeout=30,
                )
            plate_text = plate_response.json().get("text", "") if plate_response.ok else ""

            # 2. Vehicle make/model via dots-ocr
            with open(photo["file_path"], "rb") as f:
                mm_response = requests.post(
                    f"{dots_ocr_url}/predict",
                    files={"image": (photo["photo_id"], f, "image/jpeg")},
                    data={"task": "vehicle_classification"},
                    timeout=30,
                )
            mm_data = mm_response.json() if mm_response.ok else {}
            vehicle_make = mm_data.get("make", "")
            vehicle_model = mm_data.get("model", "")
            vehicle_colour = mm_data.get("colour", "")

            # 3. Insert into vehicle_observations
            _insert_vehicle_observation(
                photo_id=photo["photo_id"],
                plate_text=plate_text,
                vehicle_make=vehicle_make,
                vehicle_model=vehicle_model,
                vehicle_colour=vehicle_colour,
                latitude=photo["latitude"],
                longitude=photo["longitude"],
                capture_date=photo["capture_date"],
            )
            routed_count += 1
            context.log.info(
                f"[apple_photos_vehicle_route] routed {photo['photo_id']} (plate={plate_text}, make={vehicle_make})"
            )
        except Exception as e:
            logger.warning(
                "[apple_photos_vehicle_route] failed for %s: %s",
                photo["photo_id"], e,
            )
    context.log.info(
        f"[apple_photos_vehicle_route] routed {routed_count} vehicle photos"
    )
    yield f"routed {routed_count} vehicle photos"


@asset(
    group_name="apple_photos_routing",
    compute_kind="analytics",
    description="Cross-frame velocity inference: joins successive photos of the same plate within 60s, computes velocity from GPS delta / time delta.",
)
def apple_photos_vehicle_cross_frame(
    context: AssetExecutionContext,
) -> Iterator[str]:
    """Compute velocity estimates for vehicle pairs within 60s of each other."""
    context.log.info("[apple_photos_vehicle_cross_frame] starting")
    pairs = _fetch_vehicle_pairs(within_seconds=60)
    estimated_count = 0
    for pair in pairs:
        gps_delta_m = _haversine_distance(
            pair["first_latitude"], pair["first_longitude"],
            pair["second_latitude"], pair["second_longitude"],
        )
        time_delta_s = _time_delta_seconds(
            pair["first_capture_date"], pair["second_capture_date"]
        )
        if gps_delta_m < CROSS_FRAME_MIN_GPS_M:
            context.log.info(
                f"[cross_frame] skipping pair (plate={pair['plate_text']}, "
                f"gps_delta={gps_delta_m:.1f}m < {CROSS_FRAME_MIN_GPS_M}m threshold)"
            )
            continue
        if time_delta_s > CROSS_FRAME_MAX_TIME_S:
            context.log.info(
                f"[cross_frame] skipping pair (plate={pair['plate_text']}, "
                f"time_delta={time_delta_s:.1f}s > {CROSS_FRAME_MAX_TIME_S}s threshold)"
            )
            continue
        velocity_mps = gps_delta_m / time_delta_s
        _update_velocity_estimate(pair["first_observation_id"], velocity_mps)
        _update_velocity_estimate(pair["second_observation_id"], velocity_mps)
        estimated_count += 1
        context.log.info(
            f"[cross_frame] plate={pair['plate_text']}, "
            f"gps_delta={gps_delta_m:.1f}m, time_delta={time_delta_s:.1f}s, "
            f"velocity={velocity_mps:.2f} m/s"
        )
    context.log.info(
        f"[apple_photos_vehicle_cross_frame] estimated velocity for {estimated_count} pairs"
    )
    yield f"estimated velocity for {estimated_count} pairs"


# ============================================================================
# Helper functions (stubs — real implementations use the DuckLake resource)
# ============================================================================


def _fetch_unrouted_document_scans(limit: int) -> list[dict]:
    """Fetch the next batch of `is_document_scan=true` rows where
    `routed_to_paperless_at IS NULL`. Stub: returns empty list."""
    return []


def _fetch_unrouted_vehicle_photos(limit: int) -> list[dict]:
    """Fetch the next batch of `has_vehicle_hint=true` rows where
    no row in `vehicle_observations` exists for the same `photo_id`.
    Stub: returns empty list."""
    return []


def _fetch_vehicle_pairs(within_seconds: int) -> list[dict]:
    """Fetch vehicle observation pairs within `within_seconds` of each other,
    grouped by `plate_text`. Stub: returns empty list."""
    return []


def _mark_routed_to_paperless(photo_id: str) -> None:
    """UPDATE apple_photos SET routed_to_paperless_at = NOW() WHERE photo_id = $photo_id."""
    logger.info(
        f"[apple_photos_document_scan_route] UPDATE apple_photos SET routed_to_paperless_at=NOW() WHERE photo_id='{photo_id}'"
    )


def _insert_vehicle_observation(
    photo_id: str,
    plate_text: str,
    vehicle_make: str,
    vehicle_model: str,
    vehicle_colour: str,
    latitude: float | None,
    longitude: float | None,
    capture_date: str,
) -> None:
    """INSERT INTO vehicle_observations (...) VALUES (...)."""
    logger.info(
        f"[apple_photos_vehicle_route] INSERT INTO vehicle_observations "
        f"(photo_id, plate_text, vehicle_make, vehicle_model, vehicle_colour, "
        f"latitude, longitude, capture_date, velocity_estimate_mps) "
        f"VALUES ('{photo_id}', '{plate_text}', '{vehicle_make}', '{vehicle_model}', "
        f"'{vehicle_colour}', {latitude}, {longitude}, '{capture_date}', NULL)"
    )


def _update_velocity_estimate(observation_id: str, velocity_mps: float) -> None:
    """UPDATE vehicle_observations SET velocity_estimate_mps = $velocity WHERE observation_id = $id."""
    logger.info(
        f"[cross_frame] UPDATE vehicle_observations SET velocity_estimate_mps={velocity_mps:.2f} "
        f"WHERE observation_id='{observation_id}'"
    )


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine distance in metres between two WGS84 points."""
    from math import asin, cos, radians, sin, sqrt

    R = 6371000.0  # Earth radius in metres
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))


def _time_delta_seconds(date1: str, date2: str) -> float:
    """Delta in seconds between two ISO 8601 datetime strings."""
    try:
        d1 = datetime.fromisoformat(date1)
        d2 = datetime.fromisoformat(date2)
        return abs((d2 - d1).total_seconds())
    except Exception:
        return 0.0
