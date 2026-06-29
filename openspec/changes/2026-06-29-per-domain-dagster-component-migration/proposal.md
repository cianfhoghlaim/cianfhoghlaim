# Per-Domain Dagster Component Migration

## Why

The 2026-06-28 v4 consolidation (openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4)
merged all 5 former `sruth/<quadrant>/` quadrants into the single
`cianfhoghlaim/` package, but the 3 KCG-specific Dagster Components
(`CelticDltSourceComponent`, `CelticLancedbHnswComponent`,
`CelticCocoindexV1Component`) still import from the pre-v4
`sruth.oideachais.dlt_utils.*` and `oideachais.cocoindex_flows.*` paths.
The Components are wired into `defs.yaml` but will not import successfully
at runtime until the paths are migrated.

Additionally, the celtic-asset-generation capability spec describes a
5-stage pipeline (BAML → CocoIndex → Cognee → Graphiti → LanceDB) that
is currently scattered across 30+ hand-written `@dlt_assets` modules in
`cianfhoghlaim/assets/_oideachais_dagster_defs/assets/`. There is no
single `defs/` entry point that wires the 5 stages into a coherent
asset graph for the celtic corpus.

## What Changes

### 1. Migrate the 3 KCG Component imports (sruth → cianfhoghlaim)

- `celtic_dlt_source.py` line 24-26:
  `sruth.oideachais.dlt_utils.{destinations,safety,source_factory}`
  → `cianfhoghlaim.core.dlt._oideachais_dlt_utils.{...}`
- `celtic_lancedb_hnsw.py` line 46:
  `oideachais.lancedb.indexing`
  → `cianfhoghlaim.core.lancedb.lancedb.indexing`
- `celtic_cocoindex_v1.py` line 42:
  `oideachais.cocoindex_flows.leabharlann_embedding`
  → `cianfhoghlaim.embeddings._oideachais_src.leabharlann_embedding`

### 2. Create the per-domain `defs/celtic_asset_generation/` directory

- `loads.py` — a single `dlt.source` factory that yields 24 resources
  (8 Celtic-nation education sources × EN/GA/Manx/Br/Cy/Gd/Kw equivalents)
- `defs.yaml` — the upstream `DltLoadCollectionComponent` that wraps the
  factory into a `celtic_asset_generation` group asset
- `hnsw_defs.yaml` — the `CelticLancedbHnswComponent` instance for the
  final LanceDB HNSW index build (Stage 5)

### 3. Add a per-domain spec delta to `celtic-asset-generation`

- Requirement: The `celtic_asset_generation` asset group SHALL be
  declared as a single `DltLoadCollectionComponent` instance
- Requirement: The HNSW index for the celtic corpus SHALL be built
  by a `CelticLancedbHnswComponent` instance with
  `ef_construction=100, M=16` (the canonical 2026-06 LanceDB defaults)

### 4. Per-domain plan (this PR; later changes for the other 5)

- **Domain 1 (this change)**: celtic-asset-generation
- **Domain 2 (later)**: oideachais-pipeline (10-12 dlt sources)
- **Domain 3 (later)**: meaisinfhoghlaim-platform (8-10 BAML extraction)
- **Domain 4 (later)**: cognify (3-4 ops)
- **Domain 5 (later)**: tuatha (5-6 sources)
- **Domain 6 (later)**: croilar (3-4 functions)
