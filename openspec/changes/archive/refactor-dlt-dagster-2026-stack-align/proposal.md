# refactor-dlt-dagster-2026-stack-align — Refactor oideachais DLT + Dagster code to align with 2026-06 stack releases

## Why

The oideachais data platform has accumulated significant drift from
the upstream best-practices of the eight packages it depends on.
Per the 2026-06 package updates, the following releases are now
considered canonical and are already on the venv:

| Package | Released | KCG adoption |
|:--|:--|:--|
| `dagster` + `dg` CLI | 1.10+ (Components preview) | Components are NOT yet used; we hand-write `Definitions(assets=[...])` |
| `dlt` | 1.0 (with `rest_api` + `filesystem` core sources) | We hand-write `@dlt.source` wrappers; `rest_api` declarative is NOT used |
| `duckdb` + `ducklake` | 1.0 (data inlining, clustering, bucket partitioning, geometry, variant) | We use the *beta* DuckLake 0.9 API; no inlining, no clustering |
| `motherduck` | preview DuckLake 1.0 (managed / BYOB / BYOC) | We use neither managed DuckLake nor the three hosting options |
| `lancedb` | 0.15+ (multi-vector index, IVF, HNSW, scalar) | We use no vector indexes (`index=None` default) |
| `graphiti-core` | 0.5+ (FalkorDB Lite embedded support) | We have a hand-rolled `sruth/oideachais/graph/temporal.py` that does NOT use FalkorDB |
| `falkordb` | 1.0 (Cypher + vector + graph) | We have a `falkordb_client.py` that is unused |
| `cocoindex` | 1.0.9 (stable `@coco.fn` + `@coco.lifespan` + `mount_table_target`) | 8 v0 flows are still broken on import |

**The consequence** of this drift is that:
- New contributors cannot read the codebase and follow the canonical
  dlt / Dagster / DuckDB patterns they see in the official docs.
- The 8 packages are each operating at ~50% of their 2026-06
  capability (no vector indexes in LanceDB, no DuckLake inlining,
  no Components, no FalkorDB-backed Graphiti, no CocoIndex v1
  for 8/11 flows).
- The `sruth/oideachais/REFACTORING.md` backlog has 21 items in
  `backlog` and `in_progress`; many of them are blocked on this
  foundational alignment.

**This change lands the 8 foundational alignments** that unblock
the broader REFACTORING.md backlog. After this change, the oideachais
codebase is recognisably idiomatic for the 8 packages, and the
remaining REFACTORING.md items can be tackled one at a time
with confidence that the foundations are correct.

## What

The change has **8 phases**, one per package. Each phase is
independently shippable, but they are landed together because
they share the openspec spec deltas and the validation harness.

### Phase 1 — `dlt` 1.0 alignment
- Add `dlt.sources.rest_api` declarative support to
  `oideachais.dlt_utils.source_factory.SourceFactory`.
  Today `_build_api_table_source` builds a 0-arg
  `rest_api_source(config)` call manually; switch to the
  canonical `dlt.sources.rest_api.rest_api` and expose the
  `client` + `resources` + `endpoint` + `params` schema via
  the YAML.
- Add `dlt.sources.filesystem` declarative support for the
  `filesystem_csv` and `filesystem_parquet` kinds.
  Today `_build_filesystem_{csv,parquet}_source` constructs
  the source manually; switch to `dlt.sources.filesystem` with
  a `readers` argument.
- Add the **dlt best-practice guard** to
  `sruth/oideachais/dlt_utils/safety.py`:
  - `safe_dlt_run()` already exists; add `safe_dlt_run_with_progress()`
    that streams package progress (mimicking the dlt-progress-bar
    pattern from the dlthub.com blog).
  - Add a `validate_source_kwargs()` function that catches
    the 4 common dlt 1.0 mistakes: missing `name`, missing
    `primary_key` on incremental, no `write_disposition`,
    `merge` without `primary_key`.

### Phase 2 — `Dagster` 1.10 + `dg` CLI Components alignment
- Add a `oideachais.dagster_defs.components` package with the
  **3 KCG-specific components**:
  - `CelticDltSourceComponent` — wraps a single DLT source and
    registers it as a `dg.asset` (Dagster Components + dg CLI
    pattern from docs.dagster.io/api/dagster/components).
  - `CelticLancedbHnswComponent` — wraps a LanceDB table and
    registers an `dg.asset` that builds an HNSW index.
  - `CelticCocoindexV1Component` — wraps a CocoIndex v1 App
    and registers an `dg.asset` that calls `app.update()`.
- Add a `sruth/oideachais/dagster_defs/defs.yaml` that uses
  `type: dagster.DefsFolderComponent` to mount the existing
  `assets/`, `sensors/`, `schedules.py`, and the 3 new
  Components, replacing the hand-written
  `Definitions(assets=combined_assets, ...)` line in
  `definitions.py`.
- Keep `definitions.py` as the **bootstrap entrypoint** that
  calls `dg.load_from_defs_folder()` and adds the 3 dbt
  assets + dbt resource.
- The `dg` CLI is the new developer workflow:
  `dg list defs` → `dg list components` →
  `dg scaffold defs MyComponent my_component/`.

### Phase 3 — `DuckLake` 1.0 alignment
- Bump `oideachais.dlt_utils.destinations` to use the stable
  DuckLake 1.0 spec. Add the **3 new 1.0 features**:
  - `data_inlining_row_limit` — set on every created table
    to 100 rows by default (the new DuckLake 1.0 default).
  - `SORTED BY` — for the 4 highest-volume tables (the
    weekly marimo `weekly_downloads`, `language_distribution`,
    `ocr_confidence_by_model`, and the leabharlann
    `*_raw` tables), set `SORTED BY (id)` to enable
    data clustering (the 1.0 + 10x speedup).
  - `bucket(1000, id)` — for the 3 largest fact tables
    (the leabharlann zotero + takeout + cocoindex tables),
    enable bucket partitioning.
- Add the **`geometry` and `variant` types** to the
  `oideachais.dlt_utils.schema` for the geospatial + observability
  tables.
- Update the dest's global_config to use the new
  `data_inlining_threshold` parameter name (1.0 renamed
  `data_inlining_row_limit`).

### Phase 4 — `MotherDuck` managed / BYOB / BYOC alignment
- Add a new `oideachais.dlt_utils.motherduck_options` module
  with the 3 hosting options from
  `motherduck.com/blog/announcing-ducklake-1-0-on-motherduck`:
  - `fully_managed_destination()` — MotherDuck catalog +
    MotherDuck storage + MotherDuck compute.
  - `byob_destination()` — MotherDuck catalog + self-hosted
    S3 + MotherDuck compute.
  - `byoc_destination()` — MotherDuck catalog + self-hosted
    S3 + self-hosted compute (Trino / Spark / DataFusion).
- Wire the new module into `get_dlt_destination()`:
  - `MOTHERDUCK_MODE=managed | byob | byoc` env var.
  - Defaults to `byob` (the new "sweet spot" per the MotherDuck
    launch post).
- Add a `oideachais.motherduck_databases` module that creates
  the 2 managed DuckLake databases (`oideachais`, `tuatha`)
  on MotherDuck via `CREATE DATABASE ... (TYPE ducklake);`.

### Phase 5 — `LanceDB` 0.15 HNSW + vector index alignment
- Add `oideachais.lancedb.indexing` module with the 3
  canonical 2026-06 patterns:
  - `build_hnsw_index(table, column="vector", ef_construction=100, M=16)` —
    creates an HNSW index (the 10B-scale pattern from
    `lancedb.com/blog/how-lancedb-accelerates-vector-search-at-10-billion-scale`).
  - `build_ivf_pq_index(table, column="vector", num_partitions=256, num_sub_vectors=32)` —
    the IVF-PQ index (low-memory mobile pattern).
  - `optimize_index(table)` — runs the compaction + index
    rebuild that the LanceDB 0.15 lifecycle requires.
- Wire the 3 functions into the 5 LanceDB tables in the
  leabharlann full-stack demo (books, zotero, takeout, gaeilge,
  aigne) so each materialises with an HNSW index.

### Phase 6 — `Graphiti` 0.5 + `FalkorDB` 1.0 alignment
- Delete `sruth/oideachais/graph/temporal.py` (the hand-rolled
  Graphiti-in-pure-Python implementation; REFACTORING.md item 7).
- Wire the real `graphiti_core` 0.5 client backed by the
  FalkorDB compose stack:
  - `sruth/oideachais/graph/graphiti_client.py` — wraps
    `graphiti_core.Graphiti(uri="falkordb://falkordb:6379")` and
    exposes `add_episode()`, `search()`, `add_triplet()`.
  - Replace `sruth/oideachais/graph/temporal.py` imports in
    `cognee_integration/cross_stage_cognify.py` with the new
    `graphiti_client`.
- Add a `falkordb_lite` fallback for local dev:
  - `oideachais.graph.falkordb_client.FalkorDBLite` — uses
    `graphiti_core` + `falkordb_lite` (the embedded mode
    introduced in 2026-05) when the `falkordb.cianfhoghlaim.ie`
    compose stack is unreachable.

### Phase 7 — `CocoIndex` 1.0 migration
- Migrate the 8 broken v0 flows to v1 (REFACTORING.md item 6):
  - `curriculum_embedding.py`, `curriculum_translation.py`,
    `curriculum_specification_extraction.py`, `geospatial_indexing.py`,
    `learning_outcome_graph.py`, `ocr_embedding.py`,
    `pdf_embedding.py`, `research_embedding.py`,
    `site_analysis_embedding.py` (9 in total, 8 of which are
    v0 — `author_archive_embedding.py` is the 9th).
- Use the canonical v1 pattern from `leabharlann_embedding.py`:
  - `@coco.fn` for processing functions
  - `@coco.lifespan` for shared resources
  - `localfs.walk_dir()` for file sources
  - `lancedb.mount_table_target()` for vector sinks
  - `IdGenerator()` for stable IDs
  - `@coco.fn(memo=True)` for file-level processors
- Add a `sruth/oideachais/cocoindex_flows/_lifespan.py` module that
  exports the shared `@coco.lifespan` and the 3 ContextKeys
  (RESOLVED_FILE_REGISTRY, EMBEDDER, LANCE_DB) so the 12
  flows don't re-declare the same lifespan 12 times
  (REFACTORING.md item 12).

### Phase 8 — Cross-cutting documentation + validation
- Update `sruth/oideachais/AGENTS.md` "Quick routing" table to point
  to the new `components/` and the consolidated
  `dagster_defs/defs.yaml` layout.
- Update `sruth/oideachais/STATUS.md` with the 8 package-alignment
  deltas.
- Update `sruth/oideachais/REFACTORING.md` to mark items 6, 7, 12
  (and the items in items 9, 10, 11, 17, 18 that are blocked
  on this) as `done`.
- Add a new top-level `sruth/oideachais/dagster_defs/README.md`
  with the `dg` CLI developer workflow
  (`dg list defs` → `dg list components` →
  `dg scaffold defs MyComponent`).

## Impact

### Affected files (all 8 phases)

**Phase 1 (dlt 1.0):**
- **MODIFIED:** `sruth/oideachais/dlt_utils/source_factory.py`
  (canonical `dlt.sources.rest_api` + `dlt.sources.filesystem`)
- **MODIFIED:** `sruth/oideachais/dlt_utils/safety.py`
  (add `safe_dlt_run_with_progress` + `validate_source_kwargs`)

**Phase 2 (Dagster 1.10 + dg):**
- **NEW:** `sruth/oideachais/dagster_defs/components/__init__.py`
- **NEW:** `sruth/oideachais/dagster_defs/components/celtic_dlt_source.py`
- **NEW:** `sruth/oideachais/dagster_defs/components/celtic_lancedb_hnsw.py`
- **NEW:** `sruth/oideachais/dagster_defs/components/celtic_cocoindex_v1.py`
- **NEW:** `sruth/oideachais/dagster_defs/defs.yaml`
- **MODIFIED:** `sruth/oideachais/dagster_defs/definitions.py`
  (bootstrap calls `dg.load_from_defs_folder()`)
- **NEW:** `sruth/oideachais/dagster_defs/README.md`

**Phase 3 (DuckLake 1.0):**
- **MODIFIED:** `sruth/oideachais/dlt_utils/destinations.py`
  (data inlining + clustering + bucket partitioning)
- **NEW:** `sruth/oideachais/dlt_utils/schema.py`
  (geometry + variant type helpers)

**Phase 4 (MotherDuck managed / BYOB / BYOC):**
- **NEW:** `sruth/oideachais/dlt_utils/motherduck_options.py`
- **MODIFIED:** `sruth/oideachais/dlt_utils/destinations.py`
  (route on `MOTHERDUCK_MODE` env var)
- **NEW:** `sruth/oideachais/motherduck_databases.py`

**Phase 5 (LanceDB 0.15 HNSW):**
- **NEW:** `sruth/oideachais/lancedb/__init__.py`
- **NEW:** `sruth/oideachais/lancedb/indexing.py`
- **MODIFIED:** `sruth/oideachais/cocoindex_flows/leabharlann_embedding.py`
  (call `build_hnsw_index` on each table)

**Phase 6 (Graphiti 0.5 + FalkorDB 1.0):**
- **DELETED:** `sruth/oideachais/graph/temporal.py`
- **NEW:** `sruth/oideachais/graph/graphiti_client.py`
- **MODIFIED:** `sruth/oideachais/graph/falkordb_client.py`
  (add `FalkorDBLite` fallback)
- **MODIFIED:** `sruth/oideachais/cognee_integration/cross_stage_cognify.py`
  (use the new `graphiti_client`)

**Phase 7 (CocoIndex v1 migration):**
- **NEW:** `sruth/oideachais/cocoindex_flows/_lifespan.py`
- **MIGRATED:** 9 v0 flows → v1

**Phase 8 (documentation):**
- **MODIFIED:** `sruth/oideachais/AGENTS.md`
- **MODIFIED:** `sruth/oideachais/STATUS.md`
- **MODIFIED:** `sruth/oideachais/REFACTORING.md`
- **NEW:** `sruth/oideachais/dagster_defs/README.md`

### Affected specs

- **MODIFIED `oideachais-pipeline`** — the rule that every DLT
  source for the `oideachais` quadrant MUST use the canonical
  `dlt.sources.rest_api` declarative API (no hand-rolled
  `urllib.request` wrappers); every Dagster asset MUST be
  registered through a `dg.Component` (the new `dg` CLI
  pattern).
- **MODIFIED `oideachais-pipeline`** — the rule that the
  `oideachais` DuckLake destination MUST use the DuckLake 1.0
  spec with `data_inlining_row_limit=100`, `SORTED BY` for the
  4 highest-volume tables, and `bucket(1000, id)` for the 3
  largest fact tables.
- **MODIFIED `oideachais-pipeline`** — the rule that every
  CocoIndex flow in `sruth/oideachais/cocoindex_flows/` MUST be a v1
  App using `@coco.fn` + `@coco.lifespan` +
  `lancedb.mount_table_target` (the canonical v1 pattern).
- **MODIFIED `oideachais-semantic-search`** — the rule that
  every LanceDB table in the leabharlann full-stack demo
  MUST have an HNSW index built on the `vector` column at
  materialisation time.
- **MODIFIED `oideachais-cognify-knowledge-graph`** — the rule
  that the `cross_stage_cognify` pipeline MUST use the
  `graphiti_core` 0.5 client backed by the FalkorDB compose
  stack (no hand-rolled pure-Python implementation).

## Non-Goals

- No change to the 30+ dlt sources themselves (only the
  underlying factory + the destination).
- No change to the BAML schemas (`baml_src/*.baml`).
- No change to the FastAPI endpoints (`sruth/oideachais/api/`).
- No change to the Marimo notebooks (`sruth/oideachais/notebooks/`).
- No change to the front-end (`sruth/oideachais/web/`).
- No new dlt sources added.
- No new Dagster assets added.
- No change to the `sruth/oideachais/sources.yaml` schema (only the
  factory underneath is upgraded).

## Risk Assessment

- **Risk: the v0 → v1 CocoIndex migration changes the schema of
  8 LanceDB tables.** Mitigation: the v1 Apps produce the same
  schema as the v0 Apps (verified by the `leabharlann_embedding.py`
  pattern). Old tables are not deleted; the v1 Apps open
  existing tables via `lancedb.connect()`.
- **Risk: the new DuckLake 1.0 spec is incompatible with the
  DuckLake 0.9 server in the `lakehouse` stack.** Mitigation:
  DuckLake 1.0 is a stable spec with backwards compatibility
  per the 2026-04-13 launch post; the existing 0.9 server
  reads 1.0 tables.
- **Risk: the `dg` Components pattern requires Dagster 1.10+
  and changes the `definitions.py` bootstrap.** Mitigation: the
  new `definitions.py` still creates a `Definitions` object; the
  only difference is that the `assets=`, `sensors=`, `schedules=`
  lists are populated by `dg.load_from_defs_folder()` instead of
  being hand-rolled.
- **Risk: the `graphiti_core` 0.5 import may fail on the MacBook
  Python 3.12 venv if the optional FalkorDB extra is not
  installed.** Mitigation: the new `graphiti_client.py` uses
  the `falkordb_lite` fallback when the `falkordb` Python
  package is not importable, matching the
  `graphiti-core` 0.5+ behaviour per
  `github.com/getzep/graphiti/issues/1240`.

## Validation

1. `openspec validate refactor-dlt-dagster-2026-stack-align --strict` passes
2. `uv run --package oideachais python -c "import dagster_defs.definitions"` loads
3. `uv run --package oideachais dg list defs` shows all 120+ assets
4. `uv run --package oideachais dg list components` shows the 3 KCG components
5. `uv run --package oideachais dg scaffold defs MyTest my_test` scaffolds
6. `uv run --package oideachais python -c "from dlt_utils.source_factory import SourceFactory; f = SourceFactory.from_yaml('sruth/oideachais/sources.yaml'); print(len(f.all_ids()))"` prints 100+ (all 100+ sources resolvable through the new factory)
7. `uv run --package oideachais python -c "from cocoindex_flows import _lifespan; print(_lifespan.LANCE_DB.name)"` succeeds (the shared v1 lifespan is importable)
8. `mise run lint:skills` still passes 108/108
9. `bun run ccc:search "CelticDltSourceComponent"` finds the new component
10. `git diff --stat` shows ~25 files modified + 15 new files
