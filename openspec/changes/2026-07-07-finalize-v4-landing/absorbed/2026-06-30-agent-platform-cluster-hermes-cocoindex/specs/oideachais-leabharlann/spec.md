# `oideachais-leabharlann` capability spec — apple-photos delta

The oideachais-leabharlann capability spec governs the
leabharlann (personal + academic archive) pipeline: the 4
existing dlt sources (`leabharlann_books`, `leabharlann_zotero`,
`leabharlann_takeout_v1`, the UoG artefacts source), the
3 existing v1 CocoIndex Apps (`leabharlann_books_embedding`,
`leabharlann_zotero_embedding`, `leabharlann_takeout_embedding`),
and the 7 Dagster assets in
`cianfhoghlaim/dagster/assets/leabharlann_assets.py`.

This delta adds a 5th leabharlann corpus: **Apple Photos**.
The Apple Photos corpus has two distinct destination flows
because the user's photo library contains two semantically
different content types:

1. **Document screenshots & scans** (receipts, letters, forms)
   → OCR'd via `docling-serve` → routed to `paperless-ngx` for
   permanent archive
2. **License plate / vehicle photos** (the user's extensive
   Galway / Belfast / London collection documenting traffic-law
   violations) → plate OCR via `paddleocr` + vehicle
   classification via `dots-ocr` + captioning via
   `minimax-m3-vision` → routed to the new
   `vehicle_observations` DuckLake table

The Apple Photos pipeline also has a 3rd cross-cutting
capability: the **cross-frame velocity inference** for
successive photos of the same vehicle, which derives a
velocity estimate from GPS delta / time delta (precedent:
the user's prior HMG government comms project that did
offline vehicle velocity / acceleration inference).

## ADDED Requirements

### Requirement: apple_photos dlt source scans the leabharlann/photos/ export

The system SHALL provide a `apple_photos` dlt source at
`cianfhoghlaim/dlt/apple_photos/__init__.py` that scans the
`leabharlann/photos/` directory (the user's exported
`Photos Library.photoslibrary` directory, produced by the
one-shot operator action
`osxphotos export /Users/cian/Pictures/Photos\ Library.photoslibrary --no-progress --use-photokit-info --directory leabharlann/photos/`).

The source yields a single `apple_photos` resource with the
12 columns: `photo_id` (Apple's UUID; primary key),
`capture_date`, `latitude`, `longitude`, `camera_model`,
`width`, `height`, `file_path`, `file_hash` (SHA-256),
`is_screenshot`, `is_document_scan`, `has_vehicle_hint`.

`write_disposition="merge"` with `primary_key="photo_id"` for
incremental updates. The source SHALL respect
`LEABHARLANN_PHOTOS_INCLUDE_GPS` env var: when `false` (the
default), the `latitude` and `longitude` columns SHALL be
`NULL` for privacy.

#### Scenario: Apple Photos source yields rows with EXIF metadata

- **GIVEN** the `leabharlann/photos/` directory contains
  3 sample photos (1 document scan + 1 vehicle + 1 sunset)
- **WHEN** the `apple_photos_source()` source runs
- **THEN** the source yields 3 rows
- **AND** the document scan row has `is_document_scan=true`
- **AND** the vehicle row has `has_vehicle_hint=true`
- **AND** the sunset row has both flags `false`
- **AND** all 3 rows have `photo_id` set to the Apple UUID
  + `file_hash` set to the SHA-256 of the file contents

#### Scenario: Privacy gate defaults to GPS-off

- **GIVEN** `LEABHARLANN_PHOTOS_INCLUDE_GPS` is unset (the
  default)
- **WHEN** the `apple_photos_source()` source runs
- **THEN** the `latitude` and `longitude` columns SHALL be
  `NULL` for all rows
- **AND** a `WARN:` log line SHALL be emitted to stdout
- **WHEN** the operator sets
  `LEABHARLANN_PHOTOS_INCLUDE_GPS=true` and re-runs
- **THEN** the `latitude` and `longitude` columns SHALL
  be populated from EXIF

### Requirement: apple_photos_metadata + apple_photos_chunks v1 Apps are the canonical Apple Photos discovery surfaces

The system SHALL provide 2 new CocoIndex v1 Apps in
`cianfhoghlaim/cocoindex/`:

- `apple_photos_metadata.py` named `ApplePhotosMetadataIndex`
  → target `apple_photos_metadata` LanceDB table, BGE-m3
  1024-dim. Indexes the 12-column metadata rows (without
  image bytes). Embeds the `caption` column (filled by the
  `apple_photos_captioning` Dagster asset). Query helper:
  `async def search_apple_photos(query: str,
  bbox: tuple[float, float, float, float] | None = None,
  date_range: tuple[str, str] | None = None,
  limit: int = 10)`.
- `apple_photos_chunks.py` named `ApplePhotosChunksIndex` →
  target `apple_photos_chunks` LanceDB table, BGE-m3
  1024-dim. Indexes the OCR'd text from document scans +
  license plate reads.

Plus 1 third non-LanceDB App:
- `apple_photos_geospatial.py` named
  `ApplePhotosGeospatialIndex` → emits 2 GeoParquet files
  (POINT Z, EPSG:4326):
  - `leabharlann/photos/_derived/all_photos.geo.parquet`
  - `leabharlann/photos/_derived/vehicles.geo.parquet`

The GeoParquet output is gated by
`LEABHARLANN_PHOTOS_INCLUDE_GPS=true` (defaults to false).

#### Scenario: search_apple_photos returns ranked results

- **GIVEN** the `apple_photos_metadata` v1 App has materialised
- **AND** the library contains 50 photos taken in Galway
  between 2020-2024
- **WHEN** a developer runs
  `await search_apple_photos("Galway 2022", bbox=(53.27, -9.10, 53.35, -8.99), date_range=("2022-01-01", "2022-12-31"), limit=5)`
- **THEN** the function SHALL return the top-5 photos
  ranked by BGE-m3 cosine similarity to "Galway 2022"
  AND filtered by the Galway bbox AND filtered by the
  2022 date range
- **AND** each row SHALL carry `photo_id`, `capture_date`,
  `latitude`, `longitude`, `caption`

#### Scenario: GeoParquet output is gated

- **GIVEN** `LEABHARLANN_PHOTOS_INCLUDE_GPS` is unset
- **WHEN** the `apple_photos_geospatial` v1 App materialises
- **THEN** the 2 GeoParquet files SHALL be `gitignored`
  (or omitted from the output entirely)
- **WHEN** the operator sets
  `LEABHARLANN_PHOTOS_INCLUDE_GPS=true` and re-runs
- **THEN** the 2 GeoParquet files SHALL be written to
  `leabharlann/photos/_derived/`

### Requirement: apple_photos_document_scan_route asset routes document scans to paperless-ngx

The system SHALL provide a Dagster asset at
`cianfhoghlaim/dagster/assets/apple_photos_routing_assets.py`
named `apple_photos_document_scan_route` that polls the
`apple_photos_metadata` table for rows where
`is_document_scan = true`. For each match, the asset:

1. Calls the `docling-serve` stack at
   `http://docling-serve:5001/v1/convert/file` to OCR + classify
   the document (invoice / receipt / letter / form / other).
2. POSTs the result to the `paperless-ngx` stack at
   `http://paperless-ngx:8000/api/documents/post_document/`
   with the original photo as the source PDF, the OCR'd text
   as the body, and the EXIF GPS + timestamp as metadata
   tags.
3. Marks the row as `routed_to_paperless_at` to avoid
   re-routing on subsequent re-runs.

The asset SHALL use the `PAPERLESS_CONSUMER_TOKEN` from the
Infisical `dev-baile/apple_photos/paperless_consumer_token`
slot for the paperless-ngx auth.

#### Scenario: Document scan photo routes to paperless-ngx

- **GIVEN** a row in `apple_photos_metadata` with
  `is_document_scan=true` and `routed_to_paperless_at IS NULL`
- **WHEN** the `apple_photos_document_scan_route` asset runs
- **THEN** the asset SHALL call `docling-serve` with the
  photo's `file_path` and receive OCR text + classification
- **AND** the asset SHALL POST to `paperless-ngx` with the
  OCR'd text + EXIF GPS + timestamp as tags
- **AND** the `paperless-ngx` response SHALL return
  `{"id": <new_doc_id>}`
- **AND** the row's `routed_to_paperless_at` SHALL be set
  to the current UTC timestamp

### Requirement: apple_photos_vehicle_route + apple_photos_vehicle_cross_frame assets route vehicle photos to the vehicle_observations table

The system SHALL provide 2 Dagster assets in
`cianfhoghlaim/dagster/assets/apple_photos_routing_assets.py`:

- `apple_photos_vehicle_route` — polls the
  `apple_photos_metadata` table for rows where
  `has_vehicle_hint = true`. For each match, the asset:
  1. Calls `paddleocr` (port 5000) for license plate OCR.
  2. Calls `dots-ocr` (port 5000) for vehicle make/model
     classification (VLM fallback for ambiguous cases).
  3. Calls `minimax-m3-vision` via LiteLLM for a 1-2
     sentence caption.
  4. Writes a row to the new `vehicle_observations` DuckLake
     table with: `photo_id` (FK to apple_photos),
     `plate_text`, `vehicle_make`, `vehicle_model`,
     `vehicle_colour`, `latitude`, `longitude`,
     `capture_date`, `velocity_estimate_mps` (NULL for
     single photos; populated by the cross-frame asset
     below).

- `apple_photos_vehicle_cross_frame` (scheduled weekly
  Sundays 04:00 UTC on `bunchloch`) — joins successive
  photos of the same `plate_text` within 60 seconds and
  computes `velocity_estimate_mps` from
  `GPS_delta_meters / time_delta_seconds`. Skips pairs
  where `GPS_delta < 50m` OR `time_delta > 120s` (both
  thresholds configurable via
  `APPLE_PHOTOS_CROSS_FRAME_MIN_GPS_M` and
  `APPLE_PHOTOS_CROSS_FRAME_MAX_TIME_S` env vars).

#### Scenario: Vehicle photo writes a row to vehicle_observations

- **GIVEN** a row in `apple_photos_metadata` with
  `has_vehicle_hint=true` and no row in
  `vehicle_observations` with the same `photo_id`
- **WHEN** the `apple_photos_vehicle_route` asset runs
- **THEN** the asset SHALL call `paddleocr` and receive
  a plate text (e.g. `"05-D-12345"`)
- **AND** the asset SHALL call `dots-ocr` and receive
  make/model (e.g. `"Toyota"`, `"Corolla"`)
- **AND** the asset SHALL insert a row into
  `vehicle_observations` with all 9 columns populated
  + `velocity_estimate_mps=NULL`

#### Scenario: Cross-frame velocity inference

- **GIVEN** 2 photos of the same vehicle (`plate_text="05-D-12345"`)
  are 30 seconds apart
- **AND** the first photo's GPS is `(53.270, -9.050)` and
  the second's is `(53.275, -9.048)` (GPS delta = ~580m)
- **WHEN** the `apple_photos_vehicle_cross_frame` asset runs
- **THEN** the asset SHALL join the 2 photos on `plate_text`
  + `time_delta <= 60s`
- **AND** the asset SHALL compute
  `velocity_estimate_mps = 580 / 30 = 19.3`
- **AND** BOTH rows in `vehicle_observations` SHALL have
  `velocity_estimate_mps = 19.3` (back-filled to both
  photos of the pair)
- **AND** the asset SHALL emit a Langfuse trace event
  `cross_frame_velocity_inference: plate=05-D-12345, velocity=19.3 m/s`

#### Scenario: Low-confidence cross-frame pairs are skipped

- **GIVEN** 2 photos of the same vehicle are 180 seconds
  apart (above the 120s threshold)
- **WHEN** the `apple_photos_vehicle_cross_frame` asset runs
- **THEN** the asset SHALL NOT join the 2 photos
- **AND** BOTH rows in `vehicle_observations` SHALL have
  `velocity_estimate_mps = NULL`
- **AND** a `WARN:` log line SHALL be emitted:
  `cross_frame: skipping pair (plate=05-D-12345, time_delta=180s > 120s threshold)`

## Cross-references

- [`openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/proposal.md`](../proposal.md)
- [`openspec/changes/archive/2026-06-16-leabharlann-cocoindex-v1/proposal.md`](../archive/2026-06-16-leabharlann-cocoindex-v1/proposal.md)
- [`openspec/specs/oideachais-leabharlann/spec.md`](../../specs/oideachais-leabharlann/spec.md)
- [`bonneagar/stacks/paperless-ngx/`](../../../bonneagar/stacks/paperless-ngx/)
- [`bonneagar/stacks/docling-serve/`](../../../bonneagar/stacks/docling-serve/)
- [`bonneagar/stacks/paddleocr/`](../../../bonneagar/stacks/paddleocr/)
- [`bonneagar/stacks/dots-ocr/`](../../../bonneagar/stacks/dots-ocr/)
- [`osxphotos` library](https://github.com/RhetTbull/osxphotos)
