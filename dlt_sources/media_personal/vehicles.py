"""
Apple Photos Vehicle Plate OCR — DLT source 3 of 3 in
`dlt_sources/apple_photos/`.

Reads the `apple_photos` table (populated by
`library_export.apple_photos_source`), filters rows where
`has_vehicle_hint=true`, runs paddleocr (for the plate text)
+ dots-ocr (for the VLM vehicle classification), and emits
the `vehicle_observations` DuckLake table.

Each observation row has the shape:

    (observation_id, photo_id, capture_date, latitude, longitude,
     plate_text, plate_confidence, vehicle_class, vehicle_make,
     vehicle_model, vehicle_colour, camera_id)

Privacy gate: `latitude` / `longitude` are populated ONLY when
`LEABHARLANN_PHOTOS_INCLUDE_GPS=true` (otherwise NULL). The
`plate_text` + VLM classification are populated regardless
(plate text isn't GPS data).

Graceful degradation: if paddleocr or dots-ocr is
unreachable, the source yields rows with
`plate_text=""` / `vehicle_class=""` and an `ocr_error`
column populated. The `vehicles_route` Dagster asset
re-tries failed rows on its next run.

This is DLT source 3 of 3. It joins the library_export
table with the paddleocr + dots-ocr services via the
canonical `vehicle_observations` schema.
"""
from __future__ import annotations

import os
import time
import uuid
from collections.abc import Iterator
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

# Privacy gate — defaults to false (GPS off)
PRIVACY_GATE = os.getenv("LEABHARLANN_PHOTOS_INCLUDE_GPS", "false").lower() == "true"

# OCR service configuration
PADDLEOCR_URL = os.getenv("PADDLEOCR_URL", "http://paddleocr:8000")
DOTS_OCR_URL = os.getenv("DOTS_OCR_URL", "http://dots-ocr:8001")

# Camera-ID derivation: when no GPS is available, we derive a
# coarse "camera_id" from the file path's parent directory
# (e.g. `leabharlann/photos/2024-01-galway/` → `camera_id=galway`).
# This is a fallback for the cross-frame velocity inference —
# without GPS, the cross-frame match uses the camera_id + time
# delta heuristic instead of GPS delta.
CAMERA_ID_FALLBACK = "unknown"


def _run_paddleocr(file_path: str) -> dict[str, Any]:
    """Run paddleocr on the photo, focusing on the plate region.

    Returns a dict with `plate_text` (str) and `plate_confidence`
    (float in [0, 1]). Returns empty values on failure.
    """
    try:
        import requests
    except ImportError:
        logger.debug("_run_paddleocr: requests not installed")
        return {"plate_text": "", "plate_confidence": 0.0}

    try:
        with open(file_path, "rb") as f:
            r = requests.post(
                f"{PADDLEOCR_URL}/v1/ocr/plate",
                files={"image": (file_path, f, "image/jpeg")},
                timeout=30,
            )
        if r.status_code == 200:
            response = r.json()
            return {
                "plate_text": response.get("plate_text", ""),
                "plate_confidence": float(response.get("confidence", 0.0)),
            }
        return {
            "plate_text": "",
            "plate_confidence": 0.0,
            "ocr_error": f"paddleocr returned {r.status_code}",
        }
    except Exception as e:
        return {
            "plate_text": "",
            "plate_confidence": 0.0,
            "ocr_error": f"paddleocr call failed: {e}",
        }


def _run_dots_ocr(file_path: str) -> dict[str, Any]:
    """Run dots-ocr (VLM) on the photo for vehicle classification.

    Returns a dict with `vehicle_class`, `vehicle_make`,
    `vehicle_model`, `vehicle_colour`. Returns empty values on
    failure.
    """
    try:
        import requests
    except ImportError:
        logger.debug("_run_dots_ocr: requests not installed")
        return {
            "vehicle_class": "",
            "vehicle_make": "",
            "vehicle_model": "",
            "vehicle_colour": "",
        }

    try:
        with open(file_path, "rb") as f:
            r = requests.post(
                f"{DOTS_OCR_URL}/v1/classify/vehicle",
                files={"image": (file_path, f, "image/jpeg")},
                timeout=60,
            )
        if r.status_code == 200:
            response = r.json()
            return {
                "vehicle_class": response.get("vehicle_class", ""),
                "vehicle_make": response.get("vehicle_make", ""),
                "vehicle_model": response.get("vehicle_model", ""),
                "vehicle_colour": response.get("vehicle_colour", ""),
            }
        return {
            "vehicle_class": "",
            "vehicle_make": "",
            "vehicle_model": "",
            "vehicle_colour": "",
            "ocr_error": f"dots-ocr returned {r.status_code}",
        }
    except Exception as e:
        return {
            "vehicle_class": "",
            "vehicle_make": "",
            "vehicle_model": "",
            "vehicle_colour": "",
            "ocr_error": f"dots-ocr call failed: {e}",
        }


def _derive_camera_id(file_path: str, latitude: float | None) -> str:
    """Derive a coarse `camera_id` from the file path or GPS.

    When GPS is enabled, the camera_id is the lat/lon rounded to
    2 decimal places (≈1km resolution — enough to distinguish
    trips). When GPS is off, the camera_id falls back to the
    parent directory name (e.g. `galway` for
    `leabharlann/photos/2024-galway/`).
    """
    if latitude is not None:
        # Round to 2 decimal places (≈1km)
        return f"gps_{round(latitude, 2)}_{round(latitude, 2)}"
    # Fallback: use the parent directory name
    parent = os.path.basename(os.path.dirname(file_path))
    return parent or CAMERA_ID_FALLBACK


@dlt.source(name="apple_photos_vehicles")
def apple_photos_vehicles_source(
    base_path: str | pathlib.Path = "",
    include_gps: bool = PRIVACY_GATE,
) -> Any:
    """Read the apple_photos DuckLake table + filter vehicle rows.

    Parameters
    ----------
    base_path : str | pathlib.Path
        Unused — kept for API symmetry with `library_export.py`.
        The source reads from the `apple_photos` DuckLake table.
    include_gps : bool
        Whether to include EXIF GPS coordinates in the
        observations. Defaults to `LEABHARLANN_PHOTOS_INCLUDE_GPS=false`.

    Yields
    ------
    VehicleObservationRow
        One row per vehicle photo, with plate + VLM metadata.
    """
    return _vehicles_observer(include_gps=include_gps)


@dlt.resource(
    name="vehicle_observations",
    write_disposition="merge",
    primary_key="observation_id",
)
def _vehicles_observer(include_gps: bool) -> Iterator[dict[str, Any]]:
    """Read apple_photos where has_vehicle_hint=true → run OCR.

    This is a 2-stage pipeline:

    1. Read `apple_photos` (DuckLake table populated by
       `library_export.apple_photos_source`)
    2. For each row with `has_vehicle_hint=true`:
       a. Run paddleocr for plate text
       b. Run dots-ocr for vehicle classification
       c. Yield a row with the observation metadata
    """
    try:
        import duckdb
    except ImportError:
        logger.warning(
            "apple_photos_vehicles_source: duckdb not installed; "
            "returning empty source"
        )
        return iter([])

    try:
        conn = duckdb.connect("md:cianfhoghlaim")
    except Exception as e:
        logger.warning(
            "apple_photos_vehicles_source: cannot connect to md:cianfhoghlaim: %s",
            e,
        )
        return iter([])

    # Stage 1: read apple_photos
    try:
        rows = conn.execute(
            """
            SELECT photo_id, capture_date, latitude, longitude, camera_model,
                   file_path, file_hash
            FROM cianfhoghlaim.apple_photos.apple_photos
            WHERE has_vehicle_hint = TRUE
              AND is_screenshot = FALSE
            ORDER BY capture_date DESC
            """
        ).fetchall()
    except Exception as e:
        logger.warning(
            "apple_photos_vehicles_source: cannot read apple_photos: %s; "
            "(the table may not exist yet — library_export must run first)",
            e,
        )
        return iter([])

    observation_count = 0
    for row in rows:
        (
            photo_id,
            capture_date,
            latitude,
            longitude,
            camera_model,
            file_path,
            file_hash,
        ) = row

        # Apply the privacy gate at the source layer too
        if not include_gps:
            latitude = None
            longitude = None

        # Stage 2a: paddleocr for plate text
        plate_meta = _run_paddleocr(file_path)
        # Stage 2b: dots-ocr for vehicle classification
        vlm_meta = _run_dots_ocr(file_path)

        # Derive camera_id (used by the cross-frame velocity heuristic)
        camera_id = _derive_camera_id(file_path, latitude)

        # Stable observation_id: photo_id + plate_text (when present)
        # so re-runs are idempotent.
        plate_text = plate_meta.get("plate_text", "")
        if plate_text:
            obs_id_seed = f"{photo_id}::{plate_text}"
        else:
            obs_id_seed = photo_id
        observation_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, obs_id_seed))

        yield {
            "observation_id": observation_id,
            "photo_id": photo_id,
            "capture_date": capture_date,
            "latitude": latitude,
            "longitude": longitude,
            "plate_text": plate_text,
            "plate_confidence": float(plate_meta.get("plate_confidence", 0.0)),
            "vehicle_class": vlm_meta.get("vehicle_class", ""),
            "vehicle_make": vlm_meta.get("vehicle_make", ""),
            "vehicle_model": vlm_meta.get("vehicle_model", ""),
            "vehicle_colour": vlm_meta.get("vehicle_colour", ""),
            "camera_id": camera_id,
            "camera_model": camera_model,
            "file_path": file_path,
            "file_hash": file_hash,
            "ocr_error": (
                plate_meta.get("ocr_error", "")
                or vlm_meta.get("ocr_error", "")
            ),
            "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        observation_count += 1
        if observation_count % 100 == 0:
            logger.info(
                "apple_photos_vehicles: observed %d vehicles so far",
                observation_count,
            )
    logger.info(
        "apple_photos_vehicles: observed %d vehicles total", observation_count
    )


__all__ = [
    "CAMERA_ID_FALLBACK",
    "DOTS_OCR_URL",
    "PADDLEOCR_URL",
    "PRIVACY_GATE",
    "apple_photos_vehicles_source",
]
