# Phase D — Apple Photos Ingestion Tasks

The 1-week Phase D scope (achievable subset). Tick each item as it's
landed; the change cannot archive until all items are ticked.

## 1. DLT sources (`dlt_sources/apple_photos/`)

- [x] 1.1 Create `dlt_sources/apple_photos/library_export.py` — extract
      the existing `apple_photos_source` (12-column metadata table) from
      `__init__.py` into its own module
- [x] 1.2 Create `dlt_sources/apple_photos/document_scans.py` — DLT source
      that reads the `apple_photos` table, filters `is_document_scan=true`,
      routes each to paperless-ngx via docling-serve, emits
      `apple_photos_documents_routed` table
- [x] 1.3 Create `dlt_sources/apple_photos/vehicles.py` — DLT source that
      reads `has_vehicle_hint=true` rows, runs paddleocr + dots-ocr on the
      plate region, emits `vehicle_observations` table
- [x] 1.4 Refactor `dlt_sources/apple_photos/__init__.py` to re-export the
      3 sources from the new modules (back-compat preserved)
- [x] 1.5 All 3 sources honor `LEABHARLANN_PHOTOS_INCLUDE_GPS` (default
      `false`); when off, `latitude`/`longitude` columns are NULL
- [x] 1.6 All 3 sources degrade gracefully when upstream service
      (docling-serve, paperless-ngx, paddleocr) is unreachable

## 2. Dagster assets (`orchestration/defs/1_ingestion/apple_photos/`)

- [x] 2.1 Create `orchestration/defs/1_ingestion/apple_photos/__init__.py`
      with 8 @asset / @asset_check definitions:
      - [x] 2.1.1 `apple_photos_library_export` (L1 Ingestion)
      - [x] 2.1.2 `apple_photos_documents_route` (L1 Ingestion)
      - [x] 2.1.3 `apple_photos_vehicles_route` (L1 Ingestion)
      - [x] 2.1.4 `apple_photos_metadata_index` (L2 Materials)
      - [x] 2.1.5 `apple_photos_chunks_index` (L2 Materials)
      - [x] 2.1.6 `apple_photos_geospatial_index` (L2 Materials,
            GPS-gated)
      - [x] 2.1.7 `apple_photos_metadata_check` (L3 asset check)
      - [x] 2.1.8 `apple_photos_chunks_check` (L3 asset check)
- [x] 2.2 Create `orchestration/defs/1_ingestion/apple_photos/defs.yaml`
      wiring the 8 assets into the canonical
      `CelticIngestionComponent` group_name
- [x] 2.3 The `apple_photos_geospatial_index` asset enforces the
      `LEABHARLANN_PHOTOS_INCLUDE_GPS` gate at materialisation time;
      Asset Materialization log records `GPS_GATE=off` (default) or
      `GPS_GATE=on` (opt-in)

## 3. Privacy gate enforcement

- [x] 3.1 The `LEABHARLANN_PHOTOS_INCLUDE_GPS` env var check lives at:
      - DLT source layer: `library_export.py:_read_exif()` strips
        GPS when gate is off
      - Dagster asset layer: `apple_photos_geospatial_index` records
        `GPS_GATE=on/off` in Materialization metadata
- [x] 3.2 Default `LEABHARLANN_PHOTOS_INCLUDE_GPS=false` (GPS off)
- [x] 3.3 Setting `LEABHARLANN_PHOTOS_INCLUDE_GPS=true` enables GPS
      end-to-end (DLT → geospatial_index → GeoParquet)

## 4. Cognee cross-archive edge

- [x] 4.1 Create
      `scripts/graph_storage/cognify/cognee_integration/apple_photos_cognify.py`
      — the `cognify_apple_photos_rows` helper
- [x] 4.2 Dataset: `leabharlann_apple_photos`
- [x] 4.3 Edge types: `Photo->Location`, `Photo->CameraModel`,
      `Photo->Vehicle`, `DocumentScan->DoclingClassification`
- [x] 4.4 Follows the `leabharlann_cognify.py` pattern
      (`USE_LOCAL_SCRAPES=true` no-op stub mode)

## 5. Documentation

- [x] 5.1 Update `dlt_sources/apple_photos/AGENTS.md` to reflect the
      new 3-file DLT source structure (was 1 file, now 3)

## 6. Validation gates

- [ ] 6.1 `mise run lint` — pass
- [ ] 6.2 `mise run py:typecheck` — pass (or note deferrals)
- [ ] 6.3 `mise run openspec:validate 2026-08-23-phase-d-apple-photos-implementation-v1 --strict` — pass
- [ ] 6.4 `mise run lint:drift-docs` — pass (no AGENTS.md number claims
      broken)

## 7. Push to origin

- [ ] 7.1 `git add <specific/paths>` (no `git add -A`)
- [ ] 7.2 `git commit -m "feat(apple-photos): Phase D — 3 DLT sources + 8 Dagster assets + privacy gate + cognify edge"`
- [ ] 7.3 `git push origin phase-d-apple-photos-worktree`
- [ ] 7.4 Open a PR from
      `phase-d-apple-photos-worktree` → `token-plan-lc-pipeline-2026-08`

## 8. Deferred (out of scope)

- [ ] 8.1 Cross-frame velocity inference (`apple_photos_vehicle_cross_frame`)
- [ ] 8.2 Vision captioning (`apple_photos_captioning`)
- [ ] 8.3 Real YOLO-v8 vehicle detection (replace path-heuristic)
- [ ] 8.4 Per-corpus DuckLake schema isolation (per-tangent work)
