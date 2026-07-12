"""
Apple Photos Metadata CocoIndex v1 App — the canonical Apple Photos
metadata discovery surface.

Indexes the 12-column metadata rows from the `apple_photos` DuckLake
table (one row per photo, populated by the `apple_photos_source`
dlt source) into a new `apple_photos_metadata` LanceDB table.
Embedded with BAAI/bge-m3 1024-dim.

Privacy gate: when `LEABHARLANN_PHOTOS_INCLUDE_GPS=false` (the
default), the `latitude` and `longitude` columns SHALL be `NULL`
in the source rows; the v1 App preserves that gate.

This is one of the 4 v1 Apps added in the
`2026-06-30-agent-platform-cluster-hermes-cocoindex` change. Brings
the v1 App count from 13 → 17.

Source: the `apple_photos` DuckLake table (populated by
`apple_photos_source` in `cianfhoghlaim/dlt/apple_photos/`).
IdGenerator() for stable IDs across re-runs.

Query helper: `await search_apple_photos(query, bbox=None, date_range=None, limit=10)`.
"""
from __future__ import annotations

import datetime
import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

from ._lifespan import (
    COCOINDEX_AVAILABLE,
    EMBED_DIM,
    EMBED_MODEL,
    LANCEDB_URI,
    shared_lifespan,
)

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    if COCOINDEX_AVAILABLE:
        from ._lifespan import LANCE_DB  # type: ignore[assignment]
    else:
        LANCE_DB = None  # type: ignore[assignment]
except ImportError as e:
    logger.warning("apple_photos_metadata_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    LANCE_DB = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_TABLE = "apple_photos_metadata"
REFRESH_INTERVAL_SECS = 3600  # 1 hour (the Apple Photos source is incremental)


# =============================================================================
# Data model
# =============================================================================


@dataclass
class ApplePhotoMetadataRecord:
    """One row per photo in the apple_photos_metadata table."""

    photo_id: str  # Apple's UUID (primary key)
    capture_date: str  # ISO 8601
    latitude: float | None  # NULL when LEABHARLANN_PHOTOS_INCLUDE_GPS=false
    longitude: float | None
    camera_model: str
    width: int
    height: int
    file_path: str
    file_hash: str  # SHA-256
    is_screenshot: bool
    is_document_scan: bool
    has_vehicle_hint: bool
    caption: str  # filled by the apple_photos_captioning Dagster asset
    routed_to_paperless_at: str | None  # ISO 8601; NULL = not yet routed
    embedding: Annotated[list[float], "BAAI/bge-m3"]


# =============================================================================
# CocoIndex v1 App
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.App(shared_lifespan)  # type: ignore[misc]
    def apple_photos_metadata_app(
        builder: coco.AppBuilder,  # type: ignore[valid-type]
    ) -> None:
        """Index the apple_photos DuckLake table into apple_photos_metadata."""
        builder.set_source(  # type: ignore[attr-defined]
            "photos",
            coco.duckdb_source(  # type: ignore[attr-defined]
                table_name="apple_photos",
                database="lakehouse",
            ),
        )

        id_gen = IdGenerator()  # type: ignore[call-arg]

        @coco.function(  # type: ignore[misc]
            executor=coco.FunctionExecutor(parallelism=8),  # type: ignore[attr-defined]
        )
        async def index_photo(row: dict) -> ApplePhotoMetadataRecord:  # type: ignore[no-untyped-def,unused-ignore]
            return ApplePhotoMetadataRecord(
                photo_id=row["photo_id"],
                capture_date=str(row.get("capture_date", "")),
                latitude=row.get("latitude"),
                longitude=row.get("longitude"),
                camera_model=row.get("camera_model", ""),
                width=int(row.get("width", 0)),
                height=int(row.get("height", 0)),
                file_path=row.get("file_path", ""),
                file_hash=row.get("file_hash", ""),
                is_screenshot=bool(row.get("is_screenshot", False)),
                is_document_scan=bool(row.get("is_document_scan", False)),
                has_vehicle_hint=bool(row.get("has_vehicle_hint", False)),
                caption=row.get("caption") or "",
                routed_to_paperless_at=row.get("routed_to_paperless_at"),
                embedding=[],
            )

        _metadata_target = lancedb.mount_table_target(  # type: ignore[union-attr]
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=ApplePhotoMetadataRecord,
            primary_key="photo_id",
        )
        _metadata_target.declare_vector_index(column="embedding")

        @coco.index(  # type: ignore[misc]
            target=_metadata_target,
            refresh_interval=datetime.timedelta(seconds=REFRESH_INTERVAL_SECS),
        )
        async def write_records(  # type: ignore[no-untyped-def,unused-ignore]
            records: AsyncIterator[ApplePhotoMetadataRecord],
        ) -> AsyncIterator[ApplePhotoMetadataRecord]:
            async for record in records:
                text = f"{record.caption} {record.camera_model} {'document scan' if record.is_document_scan else ''} {'vehicle' if record.has_vehicle_hint else ''}"
                record.embedding = await _embed(text)  # type: ignore[attr-defined]
                yield record

    async def _embed(text: str) -> list[float]:  # type: ignore[no-untyped-def]
        from ._lifespan import EMBEDDER  # type: ignore[assignment]

        return await EMBEDDER.embed(text)  # type: ignore[union-attr]


# =============================================================================
# Query helpers (the public API)
# =============================================================================


async def search_apple_photos(
    query: str,
    bbox: tuple[float, float, float, float] | None = None,
    date_range: tuple[str, str] | None = None,
    limit: int = 10,
) -> list[ApplePhotoMetadataRecord]:
    """Search the apple_photos_metadata LanceDB table for the top-N matches.

    Parameters
    ----------
    query : str
        The natural-language query (e.g. "Galway 2022", "red Toyota
        Corolla", "receipt from Tesco").
    bbox : tuple[float, float, float, float] | None
        Optional (min_lon, min_lat, max_lon, max_lat) bounding box
        (WGS84). When set, photos outside the bbox are filtered
        out (only effective when LEABHARLANN_PHOTOS_INCLUDE_GPS=true).
    date_range : tuple[str, str] | None
        Optional (start_iso, end_iso) date range filter.
    limit : int
        Number of results to return (default: 10).

    Returns
    -------
    list[ApplePhotoMetadataRecord]
        Ranked matches, sorted by BGE-m3 cosine similarity.
    """
    if not COCOINDEX_AVAILABLE:
        logger.warning(
            "search_apple_photos: CocoIndex not available; returning empty list"
        )
        return []

    from ._lifespan import EMBEDDER  # type: ignore[assignment]
    from ._lifespan import LANCE_DB as _LANCE_DB  # type: ignore[assignment]

    query_embedding = await EMBEDDER.embed(query)  # type: ignore[union-attr]

    where_clauses: list[str] = []
    if bbox is not None:
        min_lon, min_lat, max_lon, max_lat = bbox
        where_clauses.append(
            f"latitude BETWEEN {min_lat} AND {max_lat} AND "
            f"longitude BETWEEN {min_lon} AND {max_lon}"
        )
    if date_range is not None:
        start_iso, end_iso = date_range
        where_clauses.append(
            f"capture_date BETWEEN '{start_iso}' AND '{end_iso}'"
        )
    where = " AND ".join(where_clauses)

    results: list[ApplePhotoMetadataRecord] = []
    async for record in _LANCE_DB.search(  # type: ignore[attr-defined]
        LANCEDB_TABLE,
        query_embedding=query_embedding,
        limit=limit,
        where=where,
    ):
        results.append(record)
    return results
