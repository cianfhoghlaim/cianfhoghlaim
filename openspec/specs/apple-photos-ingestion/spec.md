# Apple Photos Ingestion Capability

## Purpose

`apple-photos-ingestion` is the 5th leabharlann corpus of the
Cianfhoghlaim platform. It exports the user's macOS Photos library via
`osxphotos`, routes document scans to paperless-ngx via docling-serve,
extracts license plate / vehicle metadata via paddleocr + dots-ocr, and
computes cross-frame vehicle velocity estimates.

The corresponding source code lives at:

- `cianfhoghlaim/dlt/apple_photos/` (the 3 DLT sources: `library_export.py`,
  `document_scans.py`, `vehicles.py`)
- `cianfhoghlaim/cocoindex/apple_photos_metadata.py` (CocoIndex App 1)
- `cianfhoghlaim/cocoindex/apple_photos_chunks.py` (CocoIndex App 2)
- `cianfhoghlaim/cocoindex/apple_photos_geospatial.py` (CocoIndex App 3 — GeoParquet)
- `cianfhoghlaim/orchestration/defs/1_ingestion/apple_photos/` (5 Dagster assets + 2 routing assets + 1 cross-frame velocity asset)
- `lancedb.mount_table_target(apple_photos_*)` (the v1 CocoIndex target pattern)
- `ognee_integration/apple_photos_cognify.py` (the cognify cross-archive rule)

## Background

Before this capability, the user's Apple Photos library was inaccessible
to the agent fleet. This capability sits behind a privacy gate
(`LEABHARLANN_PHOTOS_INCLUDE_GPS`, default `false`) so the user keeps
control. When the gate is off, all GPS coordinates are stripped before
they reach any CocoIndex embedding or Cognify edge. The 5th corpus
joins the existing 4 leabharlann corpora (aigne + gaeilge +
gemini_deep_research + mata + ollscoil_na_gaillimhe + zotero + email
inbox) via 3 new cross-archive edge types in Cognee.

## Requirements

### Requirement: 3 v1 CocoIndex Apps for Apple Photos

The system SHALL provide 3 v1 CocoIndex Apps:

1. `apple_photos_metadata` — metadata-only indexing (filename, date,
   device, ISO, focal length). Embeds each photo's metadata via
   `BAAI/bge-m3` and yields a `apple_photos_metadata` table.
2. `apple_photos_chunks` — per-photo captioning via a small VLM, then
   chunk + embed. Yields a `apple_photos_chunks` table.
3. `apple_photos_geospatial` — geocoded location via
   `reverse_geocoder` + GEOMETRY (POINT, 4326). Stored as
   GeoParquet (`apple_photos_geo`). GPS stripping is enforced at this
   layer.

All 3 Apps SHALL use the canonical v1 pattern
(`@coco.lifespan` + `@coco.fn` + `lancedb.mount_table_target` +
`SentenceTransformerEmbedder`), respect the 100-batch minimum +
`HNSW-DROP-THRESHOLD=50` rule, and pass `cocoindex_v1_conformance`.

#### Scenario: Embedding pipeline runs

- **WHEN** the developer runs `cocoindex update apple_photos_chunks`
- **THEN** each photo's caption is chunked + embedded via `BAAI/bge-m3` (1024-d)
- **AND** chunks land in `apple_photos_chunks` LanceDB table
- **AND** the App passes `cocoindex_v1_conformance`

### Requirement: 8 Dagster assets

The system SHALL provide 8 Dagster assets:

- `apple_photos_library_export` — runs `osxphotos export` to dump the
  library to `stedding/ingest_queue/apple_photos/`
- `apple_photos_metadata_index` — materialises `apple_photos_metadata`
- `apple_photos_chunks_index` — materialises `apple_photos_chunks`
- `apple_photos_geospatial_index` — materialises `apple_photos_geospatial`
- `apple_photos_documents_route` — routing asset: document scans →
  paperless-ngx
- `apple_photos_vehicles_route` — routing asset: vehicle photos →
  `vehicle_observations`
- `apple_photos_vehicle_velocity` — cross-frame velocity asset
  (plate-text matches between consecutive photos → km/h estimate)

#### Scenario: Library export

- **WHEN** the developer runs `dagster asset materialize apple_photos_library_export`
- **THEN** `osxphotos` exports all photos to `stedding/ingest_queue/apple_photos/`
- **AND** skips any photo that already exists with the same hash (idempotent)

#### Scenario: Document scan routed to paperless-ngx

- **WHEN** a photo is classified as a document scan (heuristic: dominant
  text + rectangular aspect ratio)
- **THEN** the `apple_photos_documents_route` asset SHALL push it to
  paperless-ngx via `docling-serve` OCR
- **AND** the canonical archive copy SHALL remain in the leabharlann
  corpus

#### Scenario: Vehicle photo routed to observations

- **WHEN** a photo is classified as a vehicle (YOLO label `car` or `truck`)
- **THEN** `apple_photos_vehicles_route` SHALL run paddleocr + dots-ocr on
  the plate region
- **AND** emit a `vehicle_observation` record with `(timestamp, lat, lon,
  plate_text, vehicle_class, camera_id)` (the lat/lon only if the GPS
  gate is on)

### Requirement: Privacy gate (GPS off by default)

The system SHALL NOT include GPS coordinates in any extracted record
unless `LEABHARLANN_PHOTOS_INCLUDE_GPS=true` is explicitly set. The
gate SHALL be enforced at the `apple_photos_geospatial` CocoIndex App
layer (before the GeoParquet write).

#### Scenario: Default GPS off

- **WHEN** a developer ingests a Photos export without setting the env var
- **THEN** all GPS coordinates SHALL be stripped from `apple_photos_geospatial`
- **AND** the Asset Materialization log records `GPS_GATE=off`

#### Scenario: GPS gate on

- **WHEN** the developer runs `LEABHARLANN_PHOTOS_INCLUDE_GPS=true dagster asset materialize apple_photos_geospatial_index`
- **THEN** GPS coordinates SHALL be preserved
- **AND** the Asset Materialization log records `GPS_GATE=on`

## Cross-references

- [`oideachais-leabharlann`](../oideachais-leabharlann/spec.md) — the parent capability (6-source leabharlann corpus)
- [`oideachais-cognify-knowledge-graph`](../oideachais-cognify-knowledge-graph/spec.md) — the cognify cross-archive rules
- [`cocoindex`](../../.agents/skills/cocoindex/SKILL.md) — the v1 CocoIndex pattern
- [`apple-photos-ingestion`](../../.agents/skills/apple-photos-ingestion/SKILL.md) — the skill that this spec canonicalises

## Migrated from: *(none)*
