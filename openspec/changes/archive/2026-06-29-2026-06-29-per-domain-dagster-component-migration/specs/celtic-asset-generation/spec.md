# Delta: celtic-asset-generation

## ADDED Requirements

### Requirement: celtic_asset_generation DltLoadCollectionComponent

The `celtic_asset_generation` asset group SHALL be declared as a
single `dagster_dlt.DltLoadCollectionComponent` instance at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs/celtic_asset_generation/defs.yaml`.

The Component SHALL wrap a single `dlt.source` factory at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs/celtic_asset_generation/loads.py`
that yields 24 DLT resources (one per Celtic-nation education
source: 8 nations × up to 5 sources per nation).

The Component SHALL be auto-discovered by the parent
`dagster.DefsFolderComponent` at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs.yaml` (per
Dagster 1.10+ Components).

#### Scenario: a Dagster user lists the asset graph

- **GIVEN** the `dagster dev` webserver is running on port 3335
- **WHEN** the user runs `dg list defs` or visits the asset graph
- **THEN** all 24 celtic-nation education DLT resources appear in
  the `celtic_asset_generation` group

### Requirement: CelticLancedbHnswComponent for celtic corpus

The HNSW index for the celtic corpus SHALL be built by a
`cianfhoghlaim.assets._oideachais_dagster_defs.components.CelticLancedbHnswComponent`
instance at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs/celtic_asset_generation/hnsw_defs.yaml`.

The Component SHALL be configured with:
- `table_name: celtic_corpus_embeddings`
- `vector_column: embedding`
- `ef_construction: 100` (the canonical 2026-06 LanceDB 10B-scale default)
- `M: 16` (the canonical 2026-06 LanceDB 10B-scale default)
- `group_name: celtic_asset_generation`

#### Scenario: the HNSW index is built

- **GIVEN** the CocoIndex v1 App for the celtic corpus has populated
  the `celtic_corpus_embeddings` table with the `embedding` column
- **WHEN** the `celtic_asset_generation_hnsw_index` asset materialises
- **THEN** the HNSW index is built with `ef_construction=100, M=16`
- **AND** the asset reports `table_name`, `vector_column`, `ef_construction`,
  and `M` as metadata
