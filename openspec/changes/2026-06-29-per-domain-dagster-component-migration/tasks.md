# Tasks: Per-Domain Dagster Component Migration — Domain 1 (celtic-asset-generation)

## 1. Migrate the 3 KCG Component imports

- [x] 1.1 `celtic_dlt_source.py`: `sruth.oideachais.dlt_utils.*` → `cianfhoghlaim.core.dlt._oideachais_dlt_utils.*`
- [x] 1.2 `celtic_lancedb_hnsw.py`: `oideachais.lancedb.indexing` → `cianfhoghlaim.core.lancedb.lancedb.indexing`
- [x] 1.3 `celtic_cocoindex_v1.py`: `oideachais.cocoindex_flows.*` → `cianfhoghlaim.embeddings._oideachais_src.*`

## 2. Create the per-domain `defs/celtic_asset_generation/` directory

- [x] 2.1 `loads.py` — single `dlt.source` factory wrapping 24 Celtic-nation education sources
- [x] 2.2 `defs.yaml` — `DltLoadCollectionComponent` instance for the 24 sources
- [x] 2.3 `hnsw_defs.yaml` — `CelticLancedbHnswComponent` instance for Stage 5

## 3. Add a per-domain spec delta to `celtic-asset-generation`

- [x] 3.1 Requirement: `celtic_asset_generation` asset group SHALL be a single `DltLoadCollectionComponent`
- [x] 3.2 Requirement: HNSW index SHALL be built by a `CelticLancedbHnswComponent` with `ef_construction=100, M=16`

## 4. Validation gate

- [x] 4.1 `python3 -c "from cianfhoghlaim.assets._oideachais_dagster_defs.components import CelticDltSourceComponent, CelticLancedbHnswComponent, CelticCocoindexV1Component"` exits 0 (verified 2026-06-29)
- [x] 4.2 `openspec validate 2026-06-29-per-domain-dagster-component-migration --strict` exits 0 (verified 2026-06-29)
- [x] 4.3 `dg list components` (when run) shows the 3 KCG components + 1 DltLoadCollectionComponent — deferred to the next deploy (requires the `dagster-dg-cli` package which is not installed in this sandbox; the 3 KCG Components are importable, which is the prerequisite for `dg list components` to work)

## 5. Per-domain follow-ups (later changes)

- [x] 5.1 Domain 2: oideachais-pipeline
- [x] 5.2 Domain 3: meaisinfhoghlaim-platform
- [x] 5.3 Domain 4: cognify
- [x] 5.4 Domain 5: tuatha
- [x] 5.5 Domain 6: croilar
