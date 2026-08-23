---
name: apple-photos-ingestion
description: "Apple Photos library ingestion pipeline. Use when processing exports from the macOS Photos library (via osxphotos), routing document scans to paperless-ngx via OCR, extracting license plate / vehicle metadata via paddleocr + dots-ocr, or computing cross-frame vehicle velocity estimates. Trigger phrases include 'apple photos', 'photoslibrary', 'osxphotos', 'license plate', 'vehicle OCR', 'document scan', 'paperless-ngx ingest', 'cross-frame velocity', 'plate text recognition'."

## What's new in 2026-08/09

This skill was refreshed as part of the 2026-08-23 omnibus skill refresh
(per the  change). Key
updates:

- **2026-08 tooling**: aligned with the latest versions of upstream
  libraries (per the dev-tooling version-pinning change)
- **2026-08 patterns**: documented new features surfaced via the
  Phase 3 (surfaces round) refactor
- **Cross-references**: linked to adjacent skills (per the AGENTS.md
  dispatch matrix)

See the linked spec changes for full details.

---

# Apple Photos Ingestion Pipeline

The 5th leabharlann corpus (after books, zotero, takeout, UoG).
Two destination flows from a single source (the `apple_photos`
DuckLake table populated by the `apple_photos_source` dlt source).

## One-shot export

Before the pipeline can run, the operator runs on the MacBook:

```bash
osxphotos export "/Users/cian/Pictures/Photos Library.photoslibrary" \
  --no-progress --use-photokit-info \
  --directory leabharlann/photos/
```

This produces the `leabharlann/photos/` directory the dlt source
scans. The export typically takes 30-60 min for a 50,000-photo
library.

## Components

### 1. DLT source

`dlt/apple_photos/__init__.py` —
`apple_photos_source()`. Scans `leabharlann/photos/` and yields
one row per photo with 12 columns (photo_id, capture_date,
latitude, longitude, camera_model, width, height, file_path,
file_hash, is_screenshot, is_document_scan, has_vehicle_hint).

`write_disposition="merge"` with `primary_key="photo_id"` for
incremental updates.

### 2. Three v1 CocoIndex Apps

- `apple_photos_metadata` (`apple_photos_metadata.py`) —
  indexes the 12-column metadata rows for fast "find photos
  by GPS bbox + date range + semantic query"
- `apple_photos_chunks` (`apple_photos_chunks.py`) — indexes
  the OCR'd text from document scans + license plate reads
- `apple_photos_geospatial` (`apple_photos_geospatial.py`) —
  emits 2 GeoParquet files (POINT Z, EPSG:4326) for QGIS /
  marimo visualisation

### 3. Five Dagster assets (in `apple_photos_assets.py`)

- `apple_photos_raw` — dlt pipeline
- `apple_photos_captioning` — vision captioning via
  `minimax-m3-vision` via LiteLLM
- `apple_photos_cocoindex_metadata_update` — CocoIndex update
- `apple_photos_cocoindex_chunks_update` — CocoIndex update
- `apple_photos_cocoindex_geospatial_update` — CocoIndex
  update (gated by `LEABHARLANN_PHOTOS_INCLUDE_GPS=true`)

### 4. Two routing assets (in `apple_photos_routing_assets.py`)

- `apple_photos_document_scan_route` — routes document scans
  to paperless-ngx via docling-serve OCR
- `apple_photos_vehicle_route` — routes vehicle photos to the
  `vehicle_observations` DuckLake table via paddleocr +
  dots-ocr

### 5. One cross-frame analytics asset

- `apple_photos_vehicle_cross_frame` — joins successive photos
  of the same `plate_text` within 60s, computes
  `velocity_estimate_mps` from GPS delta / time delta

## Privacy gate

`LEABHARLANN_PHOTOS_INCLUDE_GPS=false` (default) → GPS columns
are NULL; GeoParquet output is skipped. Set to `true` to
enable. Document scans and vehicle photos are routed
regardless (no GPS needed for those).

## Vehicle cross-frame velocity inference (HMG precedent)

The user has prior experience with offline vision models for
vehicle analysis (from an HMG government comms project). The
`apple_photos_vehicle_cross_frame` asset is the KCG
implementation of that pattern: given successive photos of the
same vehicle (same `plate_text` OCR'd), compute the velocity
from GPS delta + time delta. Skips pairs where:

- `gps_delta < APPLE_PHOTOS_CROSS_FRAME_MIN_GPS_M` (default
  50m — too close to be reliable)
- `time_delta > APPLE_PHOTOS_CROSS_FRAME_MAX_TIME_S`
  (default 120s — too long to be a single trip)

The result is written to the `vehicle_observations.velocity_estimate_mps`
column for both photos in the pair. Low-confidence pairs
surface a `WARN:` log line.

## Configuration

- `LEABHARLANN_PHOTOS_ROOT` — the photos export root
  (default: `./leabharlann/photos`)
- `LEABHARLANN_PHOTOS_INCLUDE_GPS` — privacy gate
  (default: `false`)
- `DOCLING_SERVE_URL` — the docling-serve base URL
  (default: `http://docling-serve:5001`)
- `PAPERLESS_URL` + `PAPERLESS_CONSUMER_TOKEN` — paperless-ngx
  destination
- `PADDLEOCR_URL` + `DOTS_OCR_URL` — vehicle OCR stacks
- `APPLE_PHOTOS_CROSS_FRAME_MIN_GPS_M` — minimum GPS delta
  (default 50m)
- `APPLE_PHOTOS_CROSS_FRAME_MAX_TIME_S` — maximum time delta
  (default 120s)

## Reference

- `openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/specs/cianfhoghlaim-leabharlann/spec.md`
- `openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md`
- `osxphotos` library: https://github.com/RhetTbull/osxphotos (MIT)
- HMG-precedent cross-frame inference (out of scope; this
  skill mirrors the pattern from the user's prior
  `gov-comms-vehicle-pipeline` project)
