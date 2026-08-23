# `dlt_sources/apple_photos/`

> `apple_photos/`: the 5th leabharlann corpus (macOS Photos library) — 4 .py files (1 package `__init__.py` + 3 DLT sources).

## Quick start

- `__init__.py` — package entrypoint; re-exports the 3 DLT sources + their constants
- `library_export.py` — DLT source 1 of 3 (`apple_photos_source`) — one-shot osxphotos export → 12-column metadata table
- `document_scans.py` — DLT source 2 of 3 (`apple_photos_documents_source`) — document scans → paperless-ngx via docling-serve
- `vehicles.py` — DLT source 3 of 3 (`apple_photos_vehicles_source`) — vehicle photos → paddleocr + dots-ocr plate extraction

## Privacy gate

All 3 sources honor `LEABHARLANN_PHOTOS_INCLUDE_GPS` (default `false`).
When the gate is off, `latitude` and `longitude` columns are `NULL` for
all rows. The `apple_photos_geospatial_index` Dagster asset also
enforces the gate at the materialisation layer (Asset Materialization
log records `GPS_GATE=off`).

## Status

The 3 CocoIndex v1 Apps + 3 L3 `defs.yaml` files exist in
`cocoindex_flows/media/` and `orchestration/defs/3_model_lifecycle/cocoindex_v1/`.
The 3 DLT sources + 8 Dagster assets + privacy gate + cognify
cross-archive edge are added by the
`2026-08-23-phase-d-apple-photos-implementation-v1` openspec change
(Phase D of the lakehouse plan).

The cross-frame velocity inference (`apple_photos_vehicle_cross_frame`)
+ vision captioning (`apple_photos_captioning`) + real YOLO-v8
detection are **deferred** (out of scope for Phase D).
