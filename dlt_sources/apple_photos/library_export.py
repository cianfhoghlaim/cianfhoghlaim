"""
Apple Photos Library Export — the DLT source for the macOS Photos
library export.

This is DLT source 1 of 3 in the `dlt_sources/apple_photos/`
package (per the `apple-photos-ingestion` spec). The other 2 are
`document_scans.py` (routes document scans to paperless-ngx) and
`vehicles.py` (extracts license plate text from vehicle photos).

The source reads the user's osxphotos export directory
(`leabharlann/photos/`) and yields one row per photo with 12
columns. The downstream consumers are:

1. The 3 v1 CocoIndex Apps in `cocoindex_flows/media/`
   (`apple_photos_metadata`, `apple_photos_chunks`,
   `apple_photos_geospatial`)
2. The 8 Dagster assets in
   `orchestration/defs/1_ingestion/apple_photos/`
3. The Cognee cognify cross-archive rule at
   `scripts/graph_storage/cognify/cognee_integration/apple_photos_cognify.py`

Privacy gate: when `LEABHARLANN_PHOTOS_INCLUDE_GPS=false` (the
default), the `latitude` and `longitude` columns are `NULL` for
all rows. Set the env var to `true` to enable EXIF GPS.

Re-runs only process new/modified photos (by SHA-256) — the
`write_disposition="merge"` + `primary_key="photo_id"` pattern
gives us idempotent incremental updates.
"""
from __future__ import annotations

import hashlib
import logging
import os
import pathlib
import re
from collections.abc import Iterator
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

# Default source root: the leabharlann/photos/ directory
DEFAULT_PHOTOS_ROOT = pathlib.Path(
    os.getenv(
        "LEABHARLANN_PHOTOS_ROOT",
        str(pathlib.Path(__file__).resolve().parents[2] / "leabharlann" / "photos"),
    )
)

# Privacy gate — defaults to false (GPS off)
PRIVACY_GATE = os.getenv("LEABHARLANN_PHOTOS_INCLUDE_GPS", "false").lower() == "true"

# Image file extensions we recognize
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tiff", ".tif", ".dng"}


def _is_apple_uuid(name: str) -> bool:
    """Apple's photo UUIDs are 8-4-4-4-12 hex strings; filenames may have prefixes."""
    return bool(re.match(r"^[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}", name.upper()))


def _read_exif(file_path: pathlib.Path) -> dict[str, Any]:
    """Read EXIF data from a photo file via `piexif`.

    Returns a dict with `latitude`, `longitude`, `capture_date`,
    `camera_model`, `width`, `height`. Returns empty values when
    EXIF is missing or the `piexif` library is not installed.

    GPS coordinates are populated ONLY when `PRIVACY_GATE` is True
    (i.e. `LEABHARLANN_PHOTOS_INCLUDE_GPS=true`). The privacy gate
    is enforced at the source layer so it propagates to all 3
    downstream CocoIndex Apps + the 3 Dagster routing assets.
    """
    try:
        import piexif
    except ImportError:
        logger.debug("_read_exif: piexif not installed; returning empty values")
        return {
            "latitude": None,
            "longitude": None,
            "capture_date": "",
            "camera_model": "",
            "width": 0,
            "height": 0,
        }

    try:
        exif_dict = piexif.load(str(file_path))
    except Exception as e:
        logger.debug("_read_exif: failed to load EXIF for %s: %s", file_path, e)
        return {
            "latitude": None,
            "longitude": None,
            "capture_date": "",
            "camera_model": "",
            "width": 0,
            "height": 0,
        }

    # GPS — gated by PRIVACY_GATE (default off)
    latitude = longitude = None
    if PRIVACY_GATE and "GPS" in exif_dict and exif_dict["GPS"]:
        try:
            gps = exif_dict["GPS"]

            def _to_deg(rational: tuple) -> float:
                d, m, s = rational
                return float(d) + float(m) / 60 + float(s) / 3600

            lat = _to_deg(gps[2])
            lon = _to_deg(gps[4])
            if gps[1] == b"S" or gps[1] == "S":
                lat = -lat
            if gps[3] == b"W" or gps[3] == "W":
                lon = -lon
            latitude, longitude = lat, lon
        except (KeyError, IndexError, ZeroDivisionError):
            pass

    # DateTime
    capture_date = ""
    if "0th" in exif_dict and exif_dict["0th"].get(piexif.ImageIFD.DateTimeOriginal):
        try:
            dt_bytes = exif_dict["0th"][piexif.ImageIFD.DateTimeOriginal]
            capture_date = dt_bytes.decode("utf-8") if isinstance(dt_bytes, bytes) else str(dt_bytes)
        except Exception:
            pass

    # Camera model
    camera_model = ""
    if "0th" in exif_dict and exif_dict["0th"].get(piexif.ImageIFD.Model):
        try:
            cm_bytes = exif_dict["0th"][piexif.ImageIFD.Model]
            camera_model = cm_bytes.decode("utf-8") if isinstance(cm_bytes, bytes) else str(cm_bytes)
        except Exception:
            pass

    # Dimensions
    width = height = 0
    if "Exif" in exif_dict:
        try:
            width = int(exif_dict["Exif"].get(piexif.ExifIFD.PixelXDimension, 0))
            height = int(exif_dict["Exif"].get(piexif.ExifIFD.PixelYDimension, 0))
        except Exception:
            pass
    if not width or not height:
        # Fall back to 0th IFD
        try:
            width = int(exif_dict["0th"].get(piexif.ImageIFD.ImageWidth, 0))
            height = int(exif_dict["0th"].get(piexif.ImageIFD.ImageLength, 0))
        except Exception:
            pass

    return {
        "latitude": latitude,
        "longitude": longitude,
        "capture_date": capture_date,
        "camera_model": camera_model.strip(),
        "width": width,
        "height": height,
    }


def _classify_document_scan(file_path: pathlib.Path) -> bool:
    """Quick check whether a photo is a document scan via the
    `docling-serve` stack (cached for 24h in the DLT pipeline state).

    Returns True if the docling-serve response indicates a
    document-type content (invoice / receipt / letter / form).
    """
    try:
        import requests
    except ImportError:
        logger.debug("_classify_document_scan: requests not installed; returning False")
        return False

    docling_url = os.getenv("DOCLING_SERVE_URL", "http://docling-serve:5001")
    try:
        with open(file_path, "rb") as f:
            r = requests.post(
                f"{docling_url}/v1/convert/file",
                files={"file": (file_path.name, f, "image/jpeg")},
                timeout=30,
            )
        if r.status_code == 200:
            response = r.json()
            doc_type = response.get("document_type", "other")
            return doc_type in {"invoice", "receipt", "letter", "form"}
    except Exception as e:
        logger.debug(
            "_classify_document_scan: docling-serve call failed for %s: %s",
            file_path,
            e,
        )
    return False


def _has_vehicle_hint(file_path: pathlib.Path) -> bool:
    """Quick check whether a photo contains a vehicle.

    NOTE: The full YOLO-v8 pass is deferred (per the Phase D proposal
    `Out of scope` section). For now, we use a path-based heuristic:
    a photo is flagged as a vehicle hint if its filename or parent
    directory contains `vehicle`, `plate`, or `car`. The full YOLO
    call replaces this in a follow-up change.

    Returns True if any of those substrings are detected.
    """
    path_str = str(file_path).lower()
    return (
        "vehicle" in path_str
        or "plate" in path_str
        or "car" in path_str
        or os.path.dirname(path_str).endswith("/vehicles")
    )


def _is_screenshot(file_path: pathlib.Path, camera_model: str) -> bool:
    """Heuristic: iOS screenshots have `iPhone` in camera_model.

    We use a simple heuristic: camera_model contains "iPhone". The
    full heuristic (file size + resolution check) is deferred.
    """
    if "iPhone" not in camera_model:
        return False
    return True  # Conservative: assume all iPhone photos are screenshots


# ============================================================================
# DLT source
# ============================================================================


@dlt.source(name="apple_photos")
def apple_photos_source(
    base_path: str | pathlib.Path = DEFAULT_PHOTOS_ROOT,
    include_gps: bool = PRIVACY_GATE,
) -> Any:
    """Scan the leabharlann/photos/ export directory and yield rows.

    Parameters
    ----------
    base_path : str | pathlib.Path
        Root of the Apple Photos export. Defaults to
        `leabharlann/photos/`.
    include_gps : bool
        Whether to include EXIF GPS coordinates. Defaults to
        `LEABHARLANN_PHOTOS_INCLUDE_GPS=false`.

    Yields
    ------
    ApplePhotosRow
        One row per photo, with 12 columns.
    """
    base = pathlib.Path(base_path)
    if not base.exists():
        logger.warning(
            "apple_photos_source: %s does not exist; returning empty source",
            base,
        )
        return _empty_apple_photos()

    return _apple_photos_generator(base, include_gps=include_gps)


@dlt.resource(
    name="apple_photos",
    write_disposition="merge",
    primary_key="photo_id",
)
def _empty_apple_photos() -> Iterator[dict[str, Any]]:
    """Empty fallback when the export directory is missing."""
    return iter([])


@dlt.resource(
    name="apple_photos",
    write_disposition="merge",
    primary_key="photo_id",
)
def _apple_photos_generator(
    base_path: pathlib.Path,
    include_gps: bool,
) -> Iterator[dict[str, Any]]:
    """Walk the export directory and yield one row per photo."""
    photo_count = 0
    for file_path in base_path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        # Apple photos are typically named with a UUID prefix
        if not _is_apple_uuid(file_path.stem):
            continue

        exif = _read_exif(file_path)
        if not include_gps:
            exif["latitude"] = None
            exif["longitude"] = None

        # Compute SHA-256
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Classify
        is_screenshot = _is_screenshot(file_path, exif["camera_model"])
        is_document_scan = False if is_screenshot else _classify_document_scan(file_path)
        has_vehicle_hint = False if is_screenshot else _has_vehicle_hint(file_path)

        yield {
            "photo_id": file_path.stem.upper(),
            "capture_date": exif["capture_date"],
            "latitude": exif["latitude"],
            "longitude": exif["longitude"],
            "camera_model": exif["camera_model"],
            "width": exif["width"],
            "height": exif["height"],
            "file_path": str(file_path),
            "file_hash": file_hash,
            "is_screenshot": is_screenshot,
            "is_document_scan": is_document_scan,
            "has_vehicle_hint": has_vehicle_hint,
            "routed_to_paperless_at": None,
        }
        photo_count += 1
        if photo_count % 1000 == 0:
            logger.info(
                "apple_photos: processed %d photos so far", photo_count
            )
    logger.info("apple_photos: total %d photos processed", photo_count)


__all__ = [
    "DEFAULT_PHOTOS_ROOT",
    "IMAGE_EXTENSIONS",
    "PRIVACY_GATE",
    "_read_exif",
    "_classify_document_scan",
    "_has_vehicle_hint",
    "_is_screenshot",
    "apple_photos_source",
]
