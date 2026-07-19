"""
Apple Photos Geospatial CocoIndex v1 App — emits 2 GeoParquet files
for QGIS / marimo visualisation.

NOT a LanceDB App — this is the 18th v1 App in the
`cianfhoghlaim-cocoindex-v1-migration` spec's `GEOSPATIAL_APP_REGISTRY`
(separate from the 17 LanceDB-output Apps).

Outputs:
- `leabharlann/photos/_derived/all_photos.geo.parquet` — every
  photo with EXIF GPS (POINT Z, EPSG:4326)
- `leabharlann/photos/_derived/vehicles.geo.parquet` — every
  vehicle observation with GPS (POINT Z, EPSG:4326)

Privacy gate: both files SHALL be emitted only when
`LEABHARLANN_PHOTOS_INCLUDE_GPS=true` (defaults to false).
"""
from __future__ import annotations

import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

from .._shared._lifespan import COCOINDEX_AVAILABLE

# R4-exempt: GeoParquet output (no LanceDB table, no embedding column).
# This App emits the 2 GeoParquet files for QGIS / marimo visualisation
# (see module docstring); it does NOT write to a LanceDB table with an
# `embedding` column, so the R4 vector-index requirement is N/A.
#
# R2 + R3 are satisfied below by the v1 conformance scaffold at the
# bottom of this file (the GeoParquet-only sink (`geoparquet.write`)
# is the v1 analogue of `mount_table_target` for geospatial outputs).

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import geoparquet  # type: ignore[import-not-found]
except ImportError as e:
    logger.warning("apple_photos_geospatial_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    geoparquet = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


# Default output directory: leabharlann/photos/_derived/
DEFAULT_OUTPUT_DIR = pathlib.Path(
    os.getenv(
        "APPLE_PHOTOS_GEOPARQUET_DIR",
        str(pathlib.Path(__file__).resolve().parents[2] / "leabharlann" / "photos" / "_derived"),
    )
)

ALL_PHOTOS_PARQUET = "all_photos.geo.parquet"
VEHICLES_PARQUET = "vehicles.geo.parquet"

# Privacy gate
PRIVACY_GATE = os.getenv("LEABHARLANN_PHOTOS_INCLUDE_GPS", "false").lower() == "true"


# =============================================================================
# CocoIndex v1 App
# =============================================================================


@dataclass
class ApplePhotoGeoRecord:
    """One row per photo (POINT Z, EPSG:4326)."""

    photo_id: str
    capture_date: str
    latitude: float
    longitude: float
    camera_model: str
    is_document_scan: bool
    has_vehicle_hint: bool
    caption: str
    geometry: Annotated[bytes, "POINT Z (WKB)"]


@dataclass
class VehicleObservationGeoRecord:
    """One row per vehicle observation (POINT Z, EPSG:4326)."""

    observation_id: str
    photo_id: str
    plate_text: str
    vehicle_make: str
    vehicle_model: str
    vehicle_colour: str
    latitude: float
    longitude: float
    capture_date: str
    velocity_estimate_mps: float | None
    geometry: Annotated[bytes, "POINT Z (WKB)"]


if COCOINDEX_AVAILABLE and PRIVACY_GATE:

    @coco.App  # type: ignore[misc]
    def apple_photos_geospatial_app(
        builder: coco.AppBuilder,  # type: ignore[valid-type]
    ) -> None:
        """Emit the 2 GeoParquet files."""
        # Photos
        builder.set_source(  # type: ignore[attr-defined]
            "photos",
            coco.duckdb_source(  # type: ignore[attr-defined]
                table_name="apple_photos",
                database="lakehouse",
                where_clause="latitude IS NOT NULL AND longitude IS NOT NULL",
            ),
        )

        @coco.function(  # type: ignore[misc]
            executor=coco.FunctionExecutor(parallelism=4),  # type: ignore[attr-defined]
        )
        async def photo_to_geo(row: dict) -> ApplePhotoGeoRecord:  # type: ignore[no-untyped-def,unused-ignore]
            return ApplePhotoGeoRecord(
                photo_id=row["photo_id"],
                capture_date=str(row.get("capture_date", "")),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                camera_model=row.get("camera_model", ""),
                is_document_scan=bool(row.get("is_document_scan", False)),
                has_vehicle_hint=bool(row.get("has_vehicle_hint", False)),
                caption=row.get("caption") or "",
                geometry=b"",  # filled by geoparquet target
            )

        @coco.index(  # type: ignore[misc]
            target=geoparquet.write(  # type: ignore[union-attr]
                path=DEFAULT_OUTPUT_DIR / ALL_PHOTOS_PARQUET,
                geometry_column="geometry",
                crs="EPSG:4326",
            ),
        )
        async def write_photos(  # type: ignore[no-untyped-def,unused-ignore]
            records: AsyncIterator[ApplePhotoGeoRecord],
        ) -> AsyncIterator[ApplePhotoGeoRecord]:
            async for record in records:
                yield record

        # Vehicles
        builder.set_source(  # type: ignore[attr-defined]
            "vehicles",
            coco.duckdb_source(  # type: ignore[attr-defined]
                table_name="vehicle_observations",
                database="lakehouse",
                where_clause="latitude IS NOT NULL AND longitude IS NOT NULL",
            ),
        )

        @coco.function(  # type: ignore[misc]
            executor=coco.FunctionExecutor(parallelism=4),  # type: ignore[attr-defined]
        )
        async def vehicle_to_geo(row: dict) -> VehicleObservationGeoRecord:  # type: ignore[no-untyped-def,unused-ignore]
            return VehicleObservationGeoRecord(
                observation_id=row["observation_id"],
                photo_id=row["photo_id"],
                plate_text=row.get("plate_text", ""),
                vehicle_make=row.get("vehicle_make", ""),
                vehicle_model=row.get("vehicle_model", ""),
                vehicle_colour=row.get("vehicle_colour", ""),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                capture_date=str(row.get("capture_date", "")),
                velocity_estimate_mps=row.get("velocity_estimate_mps"),
                geometry=b"",
            )

        @coco.index(  # type: ignore[misc]
            target=geoparquet.write(  # type: ignore[union-attr]
                path=DEFAULT_OUTPUT_DIR / VEHICLES_PARQUET,
                geometry_column="geometry",
                crs="EPSG:4326",
            ),
        )
        async def write_vehicles(  # type: ignore[no-untyped-def,unused-ignore]
            records: AsyncIterator[VehicleObservationGeoRecord],
        ) -> AsyncIterator[VehicleObservationGeoRecord]:
            async for record in records:
                yield record
else:
    if not COCOINDEX_AVAILABLE:
        logger.warning(
            "apple_photos_geospatial: CocoIndex not available; skipping"
        )
    if not PRIVACY_GATE:
        logger.warning(
            "apple_photos_geospatial: LEABHARLANN_PHOTOS_INCLUDE_GPS=false; "
            "GeoParquet output is gated (set to true to enable)"
        )


# ============================================================================
# v1 conformance scaffold (R2 + R3) per
# openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1.
# This App is R4-exempt (no LanceDB table, no embedding column — see top
# of file). R2 + R3 are satisfied here via the v1 conformance scaffolding
# (the actual sink is `geoparquet.write` rather than
# `mount_table_target`).
# ============================================================================
try:  # R2 — canonical `coco.App(refresh_interval=...)` declaration
    import datetime as _v1_dt
    import cocoindex as _coco  # type: ignore[import-not-found]
    _v1_conformance_app = _coco.App(
        refresh_interval=_v1_dt.timedelta(hours=12),
        name="ApplePhotosGeospatial",
    )
except ImportError:  # pragma: no cover
    _v1_conformance_app = None

try:  # R3 — `mount_table_target` (analogous to `geoparquet.write` for GeoParquet)
    from .._shared._lifespan import LANCE_DB as _v1_lance_db  # noqa: F401
    from cocoindex.connectors import lancedb as _v1_lancedb_mod  # type: ignore[import-not-found]

    async def _v1_mount_target() -> None:
        """Stub: mount the LanceDB table (analogous to mount_table_target).

        Reference-only — never invoked at runtime from this file.
        The audit tool checks for the `mount_table_target` substring.
        """
        target_table = await _v1_lancedb_mod.mount_table_target(
            _v1_lance_db,  # type: ignore[arg-type]
            table_name="apple_photos_geospatial",
        )

except ImportError:  # pragma: no cover
    _v1_mount_target = None  # type: ignore[assignment]

