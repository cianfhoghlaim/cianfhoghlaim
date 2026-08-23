"""
Apple Photos DLT sources — the 5th leabharlann corpus.

This package contains 3 DLT sources (per the `apple-photos-ingestion`
spec):

1. `library_export.apple_photos_source` — one-shot osxphotos export
   → 12-column `apple_photos` DuckLake table.
2. `document_scans.apple_photos_documents_source` — routes document
   scans (where `is_document_scan=true`) to paperless-ngx via
   docling-serve OCR → `apple_photos_documents_routed` table.
3. `vehicles.apple_photos_vehicles_source` — extracts license plate
   text + VLM vehicle classification (where `has_vehicle_hint=true`)
   via paddleocr + dots-ocr → `vehicle_observations` table.

All 3 sources honor the privacy gate
(`LEABHARLANN_PHOTOS_INCLUDE_GPS`, default `false`). When the gate is
off, `latitude` and `longitude` columns are `NULL` for all rows. Set
the env var to `true` to enable EXIF GPS end-to-end (DLT → geospatial
index → GeoParquet).

The downstream consumers are:

- The 3 v1 CocoIndex Apps in `cocoindex_flows/media/`
  (`apple_photos_metadata`, `apple_photos_chunks`,
  `apple_photos_geospatial`)
- The 8 Dagster assets in
  `orchestration/defs/1_ingestion/apple_photos/`
- The Cognee cognify cross-archive rule at
  `scripts/graph_storage/cognify/cognee_integration/apple_photos_cognify.py`

The 3 sources were split out of this `__init__.py` in Phase D of the
lakehouse plan (commit pending). The original single-source code is
preserved at `library_export.py:apple_photos_source()` — see that
module's docstring for the full history.

This is one of the 4 v1 Apps + DLT source additions in the
`2026-06-30-agent-platform-cluster-hermes-cocoindex` change. It joins
the existing 4 leabharlann sources (books, zotero, takeout, UoG) to
make Apple Photos the 5th corpus.
"""
from __future__ import annotations

from dlt_sources.apple_photos.library_export import (
    DEFAULT_PHOTOS_ROOT,
    IMAGE_EXTENSIONS,
    PRIVACY_GATE,
    apple_photos_source,
)
from dlt_sources.apple_photos.document_scans import (
    DOCLING_SERVE_URL,
    PAPERLESS_CONSUMER_TOKEN,
    PAPERLESS_URL,
    apple_photos_documents_source,
)
from dlt_sources.apple_photos.vehicles import (
    CAMERA_ID_FALLBACK,
    DOTS_OCR_URL,
    PADDLEOCR_URL,
    apple_photos_vehicles_source,
)

__all__ = [
    "CAMERA_ID_FALLBACK",
    "DEFAULT_PHOTOS_ROOT",
    "DOCLING_SERVE_URL",
    "DOTS_OCR_URL",
    "IMAGE_EXTENSIONS",
    "PADDLEOCR_URL",
    "PAPERLESS_CONSUMER_TOKEN",
    "PAPERLESS_URL",
    "PRIVACY_GATE",
    "apple_photos_documents_source",
    "apple_photos_source",
    "apple_photos_vehicles_source",
]
