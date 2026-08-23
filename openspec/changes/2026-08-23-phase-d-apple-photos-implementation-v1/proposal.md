# Phase D — Apple Photos Ingestion Implementation

## Purpose

Phase D of the lakehouse plan. Implements the `apple-photos-ingestion`
spec at `openspec/specs/apple-photos-ingestion/spec.md` (3 Requirements
+ 5 Scenarios). The spec defines the 5th leabharlann corpus — the
macOS Photos library → paperless-ngx (documents) + paddleocr (vehicles)
+ GeoParquet (geospatial, GPS-gated).

The Phase A CCC audit (commit 6cdd732d3) left 3 CocoIndex v1 Apps + 3
L3 `defs.yaml` files + 1 DLT source stub + 1 `AGENTS.md` in place. This
change closes the gap by adding:

- 3 DLT source files (`library_export.py` + `document_scans.py` +
  `vehicles.py`), each honoring the `LEABHARLANN_PHOTOS_INCLUDE_GPS`
  privacy gate
- 8 Dagster assets under `orchestration/defs/1_ingestion/apple_photos/`
  (the L1 ingestion + L2 indexing + L3 asset checks per the
  5-layer Component architecture)
- 1 Cognee cross-archive cognify rule
  (`scripts/graph_storage/cognify/cognee_integration/apple_photos_cognify.py`)
- 1 updated `dlt_sources/apple_photos/AGENTS.md`

This is an **achievable-subset** delivery — the full 1-week scope is
the spec's 8 assets + 3 v1 Apps + privacy gate + cognify edge. The
8-asset decomposition matches the canonical `apple-photos-ingestion`
skill (`.agents/skills/apple-photos-ingestion/SKILL.md`).

## Why

Per the lakehouse plan, Phase D unblocks the 5th leabharlann corpus
(Apple Photos) so it can join the existing 4 corpora (books, zotero,
takeout, UoG) under the cross-archive cognify rule family. Without
this change, the user's macOS Photos library is inaccessible to the
agent fleet — the 12 NCCA subject agents + the `bunchloch_research`
agent all need photo metadata + caption embeddings for context.

The privacy gate (`LEABHARLANN_PHOTOS_INCLUDE_GPS=false` default) is
the critical safety constraint: the Photos library contains
geolocation data; the gate strips GPS before any embedding or
GeoParquet emission unless the operator explicitly opts in.

## What changes

### 1. DLT sources (`dlt_sources/apple_photos/`)

Split the existing single-source `__init__.py` into 3 dedicated
source files (per the lakehouse plan + the apple-photos-ingestion
skill):

| File | Resource name | Purpose |
|:--|:--|:--|
| `library_export.py` | `apple_photos` | One-shot osxphotos export → 12-column metadata table |
| `document_scans.py` | `apple_photos_documents_routed` | Document scans → paperless-ngx via docling-serve |
| `vehicles.py` | `vehicle_observations` | Vehicle photos → paddleocr + dots-ocr plate extraction |

All 3 sources SHALL:

- Honor `LEABHARLANN_PHOTOS_INCLUDE_GPS` (default `false`)
- Emit to `cianfhoghlaim.apple_photos.*` (the per-corpus schema
  namespace; per-tangent sub-directories are deferred per the
  lakehouse plan)
- Degrade gracefully when the upstream service (docling-serve,
  paperless-ngx, paddleocr) is unreachable

### 2. Dagster assets (`orchestration/defs/1_ingestion/apple_photos/`)

8 assets (3 L1 ingestion + 3 L2 materials + 2 L3 asset checks):

| Layer | Asset name | Purpose |
|:--|:--|:--|
| L1 Ingestion | `apple_photos_library_export` | Runs `osxphotos export` (the one-shot scan) |
| L1 Ingestion | `apple_photos_documents_route` | Routes document scans → paperless-ngx |
| L1 Ingestion | `apple_photos_vehicles_route` | Routes vehicle photos → paddleocr plate extraction |
| L2 Materials | `apple_photos_metadata_index` | Materialises `apple_photos_metadata` LanceDB table |
| L2 Materials | `apple_photos_chunks_index` | Materialises `apple_photos_chunks` LanceDB table |
| L2 Materials | `apple_photos_geospatial_index` | Materialises GeoParquet (gated) |
| L3 Check | `apple_photos_metadata_check` | Asserts metadata table is non-empty |
| L3 Check | `apple_photos_chunks_check` | Asserts chunks table is non-empty |

The privacy gate is enforced at the `apple_photos_geospatial_index`
layer: when `LEABHARLANN_PHOTOS_INCLUDE_GPS=false`, the asset
records `GPS_GATE=off` in the Materialization metadata AND skips
the GeoParquet emission.

### 3. Cognee cross-archive edge

`scripts/graph_storage/cognify/cognee_integration/apple_photos_cognify.py`:

- Dataset: `leabharlann_apple_photos` (joins the 4 existing
  `leabharlann_*` datasets)
- Edge types produced (deterministic, Cognee LLM-driven):
  - `Photo -> Location` (when GPS is enabled)
  - `Photo -> CameraModel` (always)
  - `Photo -> Vehicle` (when `has_vehicle_hint=true`)
  - `DocumentScan -> DoclingClassification`
- Follows the `leabharlann_cognify.py` pattern (the same
  `USE_LOCAL_SCRAPES=true` no-op stub mode)

### 4. Documentation

- `dlt_sources/apple_photos/AGENTS.md` updated to reflect the
  new 3-file DLT source structure

## Out of scope (deferred)

These items are intentionally **NOT** included in this change:

- Cross-frame velocity inference (`apple_photos_vehicle_cross_frame`):
  deferred — the cross-frame velocity skill pattern is documented in
  `.agents/skills/apple-photos-ingestion/SKILL.md` but the
  implementation requires a multi-photo state cache that needs
  follow-up work.
- Vision captioning (`apple_photos_captioning`): deferred — needs
  the `minimax-m3-vision` LiteLLM client wiring + the `qwen-vl`
  BAML schema, both out of scope.
- YOLO-v8 vehicle detection: the existing `_has_vehicle_hint` is
  a path-based heuristic; a real YOLO call is documented as TODO
  in the DLT stub and deferred to a follow-up change.
- Per-corpus DuckLake schema isolation (per-tangent work): the
  lakehouse plan defers this to per-tangent work; this change uses
  the `cianfhoghlaim.apple_photos.*` namespace.

## Dependencies

`Blocked by: none`
`Blocked by (soft): 2026-08-13-skill-consolidation-and-extension-v1` (the AGENTS.md + skill surfaces this change builds on top of)
`Affected repos: cianfhoghlaim`

## Cross-references

- `openspec/specs/apple-photos-ingestion/spec.md` — the canonical spec
- `.agents/skills/apple-photos-ingestion/SKILL.md` — the skill that
  this change implements
- `openspec/specs/dagster-5-layer-component-architecture/spec.md` —
  the 5-layer defs/ tree this change wires into
- `openspec/specs/centralized-schema-registry/spec.md` — the
  BAML/Pydantic schema contract
