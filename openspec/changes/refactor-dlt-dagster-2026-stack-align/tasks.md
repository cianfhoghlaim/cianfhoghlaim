# Tasks: refactor-dlt-dagster-2026-stack-align

## Phase 1 — dlt 1.0 alignment

- [ ] Update `oideachais/dlt_utils/source_factory.py` to use
      the canonical `dlt.sources.rest_api.rest_api` and
      `dlt.sources.filesystem` declarative APIs.
- [ ] Add `validate_source_kwargs()` to
      `oideachais/dlt_utils/safety.py` (4 common dlt 1.0
      mistake checks).
- [ ] Add `safe_dlt_run_with_progress()` to
      `oideachais/dlt_utils/safety.py` (streaming progress).
- [ ] Update `oideachais/dlt_utils/__init__.py` to re-export
      the 2 new helpers.
- [ ] Add `oideachais/dlt_utils/README.md` section on the 2
      new helpers.

## Phase 2 — Dagster 1.10 + dg CLI Components

- [ ] Create `oideachais/dagster_defs/components/__init__.py`.
- [ ] Create `oideachais/dagster_defs/components/celtic_dlt_source.py`
      (the CelticDltSourceComponent).
- [ ] Create `oideachais/dagster_defs/components/celtic_lancedb_hnsw.py`
      (the CelticLancedbHnswComponent).
- [ ] Create `oideachais/dagster_defs/components/celtic_cocoindex_v1.py`
      (the CelticCocoindexV1Component).
- [ ] Create `oideachais/dagster_defs/defs.yaml` (the
      DefsFolderComponent mount point).
- [ ] Update `oideachais/dagster_defs/definitions.py` to call
      `dg.load_from_defs_folder()`.
- [ ] Create `oideachais/dagster_defs/README.md` with the
      `dg` CLI developer workflow.

## Phase 3 — DuckLake 1.0 alignment

- [ ] Update `oideachais/dlt_utils/destinations.py` to set
      `data_inlining_row_limit=100` (the 1.0 default).
- [ ] Add `SORTED BY (id)` for the 4 highest-volume tables
      (in the new `oideachais/dlt_utils/ducklake_options.py`).
- [ ] Add `bucket(1000, id)` partitioning for the 3 largest
      fact tables.
- [ ] Create `oideachais/dlt_utils/ducklake_options.py`
      with the SQL helpers.
- [ ] Create `oideachais/dlt_utils/schema.py` with
      `geometry` and `variant` type helpers.

## Phase 4 — MotherDuck managed / BYOB / BYOC

- [ ] Create `oideachais/dlt_utils/motherduck_options.py` with
      the 3 hosting-option helpers.
- [ ] Update `oideachais/dlt_utils/destinations.py` to route
      on `MOTHERDUCK_MODE` env var.
- [ ] Create `oideachais/motherduck_databases.py` with the
      `CREATE DATABASE ... (TYPE ducklake)` helper.
- [ ] Add `MOTHERDUCK_MODE` to `.infisical.env` (default
      `byob`).

## Phase 5 — LanceDB 0.15 HNSW + vector index

- [ ] Create `oideachais/lancedb/__init__.py`.
- [ ] Create `oideachais/lancedb/indexing.py` with
      `build_hnsw_index`, `build_ivf_pq_index`,
      `optimize_index`.
- [ ] Update
      `oideachais/cocoindex_flows/leabharlann_embedding.py`
      to call `build_hnsw_index` on each of the 5 leabharlann
      tables (books, zotero, takeout, gaeilge, aigne).

## Phase 6 — Graphiti 0.5 + FalkorDB 1.0

- [ ] Delete `oideachais/graph/temporal.py`.
- [ ] Create `oideachais/graph/graphiti_client.py` with the
      real `graphiti_core` 0.5 client.
- [ ] Update `oideachais/graph/falkordb_client.py` to add
      the `FalkorDBLite` fallback.
- [ ] Update
      `oideachais/cognee_integration/cross_stage_cognify.py`
      to use the new `graphiti_client`.

## Phase 7 — CocoIndex v1 migration

- [ ] Create `oideachais/cocoindex_flows/_lifespan.py` with
      the shared `@coco.lifespan` + 3 ContextKeys.
- [ ] Migrate `oideachais/cocoindex_flows/curriculum_embedding.py`
      to v1.
- [ ] Migrate `oideachais/cocoindex_flows/curriculum_translation.py`
      to v1.
- [ ] Migrate
      `oideachais/cocoindex_flows/curriculum_specification_extraction.py`
      to v1.
- [ ] Migrate `oideachais/cocoindex_flows/geospatial_indexing.py`
      to v1.
- [ ] Migrate
      `oideachais/cocoindex_flows/learning_outcome_graph.py`
      to v1.
- [ ] Migrate `oideachais/cocoindex_flows/ocr_embedding.py`
      to v1.
- [ ] Migrate `oideachais/cocoindex_flows/pdf_embedding.py`
      to v1.
- [ ] Migrate `oideachais/cocoindex_flows/research_embedding.py`
      to v1.
- [ ] Migrate
      `oideachais/cocoindex_flows/site_analysis_embedding.py`
      to v1.
- [ ] Update
      `oideachais/cocoindex_flows/author_archive_embedding.py`
      to v1.

## Phase 8 — Documentation

- [ ] Update `oideachais/AGENTS.md` "Quick routing" table.
- [ ] Add a "2026-06 stack alignment" section to
      `oideachais/STATUS.md`.
- [ ] Mark REFACTORING.md items 6, 7, 9, 10, 11, 12, 17, 18
      as `done`.
- [ ] Add a "Landed in 2026-06" section to
      `oideachais/REFACTORING.md`.

## Phase 9 — Validation

- [ ] `openspec validate refactor-dlt-dagster-2026-stack-align --strict` passes
- [ ] `uv run --package oideachais python -c "import dagster_defs.definitions"` loads
- [ ] `uv run --package oideachais dg list defs` shows all 120+ assets
- [ ] `uv run --package oideachais dg list components` shows the 3 KCG components
- [ ] `mise run lint:skills` still passes 108/108
- [ ] All Phase 1-8 file edits committed

## Phase 10 — Land the plane

- [ ] Stage all changes
- [ ] Commit: `git commit -m "refactor(oideachais): align dlt + dagster + ducklake + lance + graphiti + cocoindex with 2026-06 stack"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
