# Spec Delta: apple-photos-ingestion (Phase D implementation)

## ADDED Requirements

### Requirement: Phase D implements the apple-photos-ingestion spec at 3 + 8 + 1 surface

The Phase D implementation of `apple-photos-ingestion` SHALL add 3 DLT
sources + 8 Dagster assets + 1 Cognee cross-archive cognify helper,
each at the locations specified in `openspec/specs/apple-photos-ingestion/spec.md`
(Background + Requirements sections):

- 3 DLT sources at `dlt_sources/apple_photos/`:
  - `library_export.py` — the canonical `apple_photos_source` (12-column
    metadata table; one-shot osxphotos export)
  - `document_scans.py` — the `apple_photos_documents_source` (routes
    document scans to paperless-ngx via docling-serve)
  - `vehicles.py` — the `apple_photos_vehicles_source` (extracts plate
    text + VLM vehicle classification via paddleocr + dots-ocr)
- 8 Dagster assets at `orchestration/defs/1_ingestion/apple_photos/`:
  - L1 Ingestion (3): `apple_photos_library_export`,
    `apple_photos_documents_route`, `apple_photos_vehicles_route`
  - L2 Materials (3): `apple_photos_metadata_index`,
    `apple_photos_chunks_index`, `apple_photos_geospatial_index`
  - L3 Asset checks (2): `apple_photos_metadata_check`,
    `apple_photos_chunks_check`
- 1 Cognee cross-archive cognify helper at
  `scripts/graph_storage/cognify/cognee_integration/apple_photos_cognify.py`:
  - Dataset: `leabharlann_apple_photos`
  - Edge types: `Photo-LOCATED_AT->Location`,
    `Photo-CAPTURED_WITH->CameraModel`,
    `Photo-CONTAINS->Vehicle`,
    `DocumentScan-CLASSIFIED_AS->DoclingClassification`

Per the
`openspec/changes/2026-08-23-phase-d-apple-photos-implementation-v1/`
change (Phase D of the lakehouse plan).

#### Scenario: All 3 DLT sources + 8 Dagster assets + cognify helper are present

- **GIVEN** the openspec change is applied
- **WHEN** the operator runs `ls dlt_sources/apple_photos/*.py`
- **THEN** the output SHALL include `library_export.py`,
  `document_scans.py`, and `vehicles.py` (in addition to `__init__.py`)
- **AND** `ls orchestration/defs/1_ingestion/apple_photos/` SHALL show
  `__init__.py` + `defs.yaml`
- **AND** `ls scripts/graph_storage/cognify/cognee_integration/apple_photos_cognify.py`
  SHALL exit 0

#### Scenario: The 8 Dagster assets are wired into the canonical group_names

- **GIVEN** the Dagster definitions are loaded
- **WHEN** the operator runs `dg list defs --group apple_photos`
- **THEN** the output SHALL include:
  - `1_ingestion_apple_photos/apple_photos_library_export`
  - `1_ingestion_apple_photos/apple_photos_documents_route`
  - `1_ingestion_apple_photos/apple_photos_vehicles_route`
  - `2_materials_apple_photos/apple_photos_metadata_index`
  - `2_materials_apple_photos/apple_photos_chunks_index`
  - `2_materials_apple_photos/apple_photos_geospatial_index`
  - `apple_photos_metadata_check` (L3 asset check)
  - `apple_photos_chunks_check` (L3 asset check)

### Requirement: Privacy gate is enforced at 2 layers (defense-in-depth)

The `LEABHARLANN_PHOTOS_INCLUDE_GPS` privacy gate SHALL be enforced
at 2 layers (per the spec's "Privacy gate" Requirement):

1. **DLT source layer**: `dlt_sources/apple_photos/library_export.py:_read_exif`
   strips GPS when the gate is off (the `_read_exif` function returns
   `latitude=None`, `longitude=None` when `PRIVACY_GATE` is False).
2. **Dagster asset layer**: `apple_photos_geospatial_index` records
   `GPS_GATE=off` in the Materialization metadata AND skips the
   GeoParquet emission when the gate is off.

The default value SHALL be `false` (GPS off). Setting
`LEABHARLANN_PHOTOS_INCLUDE_GPS=true` enables GPS end-to-end (DLT →
geospatial_index → GeoParquet).

#### Scenario: Default GPS off (gate default = false)

- **GIVEN** the operator has NOT set `LEABHARLANN_PHOTOS_INCLUDE_GPS`
- **WHEN** the operator runs
  `dagster asset materialize apple_photos_geospatial_index`
- **THEN** the Asset Materialization log SHALL record `GPS_GATE=off`
- **AND** the GeoParquet emission SHALL be skipped
- **AND** the `apple_photos` DuckLake rows SHALL have
  `latitude=NULL`, `longitude=NULL`

#### Scenario: GPS gate on (opt-in via env var)

- **GIVEN** the operator has set `LEABHARLANN_PHOTOS_INCLUDE_GPS=true`
- **WHEN** the operator runs
  `LEABHARLANN_PHOTOS_INCLUDE_GPS=true dagster asset materialize apple_photos_geospatial_index`
- **THEN** the Asset Materialization log SHALL record `GPS_GATE=on`
- **AND** the GeoParquet files SHALL be emitted to
  `leabharlann/photos/_derived/all_photos.geo.parquet` and
  `leabharlann/photos/_derived/vehicles.geo.parquet`
- **AND** the `apple_photos` DuckLake rows SHALL preserve the EXIF
  `latitude`/`longitude`

### Requirement: Cognee cross-archive cognify rule for Apple Photos

The Phase D implementation SHALL add a Cognee cognify helper at
`scripts/graph_storage/cognify/cognee_integration/apple_photos_cognify.py`
that joins the 5 leabharlann corpora (books + zotero + takeout + email
inbox + **apple_photos**) under a single cross-archive graph.

The helper SHALL:

- Define `DATASET_APPLE_PHOTOS = "leabharlann_apple_photos"`
- Expose 4 edge types (the same 4 listed in the spec's
  "Background" section):
  - `Photo-LOCATED_AT->Location` (gated)
  - `Photo-CAPTURED_WITH->CameraModel` (always)
  - `Photo-CONTAINS->Vehicle` (always)
  - `DocumentScan-CLASSIFIED_AS->DoclingClassification` (always)
- Follow the `leabharlann_cognify.py` pattern
  (`USE_LOCAL_SCRAPES=true` no-op stub mode)
- Apply the privacy gate at the cognify layer too (defense-in-depth):
  when `LEABHARLANN_PHOTOS_INCLUDE_GPS=false`, `latitude`/`longitude`
  are stripped from the cognify input text blob

#### Scenario: Cognify helper runs in stub mode

- **GIVEN** `USE_LOCAL_SCRAPES=true` (the local-dev default)
- **WHEN** the operator invokes `cognify_apple_photos_rows(rows)`
- **THEN** the helper SHALL return
  `{"dataset": "leabharlann_apple_photos", "rows": N, "edges": 0,
    "stub": True, "gps_gate": "off"}` (no Cognee call is made)
- **AND** no GPS coordinates are emitted to Cognee
