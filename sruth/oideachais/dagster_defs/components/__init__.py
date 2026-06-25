"""
oideachais.dagster_defs.components — Dagster dg CLI Components.

The 3 KCG-specific Components that wrap the canonical oideachais
patterns as reusable, schema-based Components per the Dagster 1.10
Components preview (`docs.dagster.io/api/dagster/components`).

Each Component subclasses `dg.Component` and implements
`build_defs()`. They are discoverable via `dg list components`
and can be instantiated from YAML via `dg scaffold defs`.

The 3 Components:
- `CelticDltSourceComponent` — wraps a single DLT source and
  registers it as a `dg.asset`. (Replaces the hand-written
  `dlt_asset()` wrapper in `oideachais/dlt_utils/source_factory.py`.)
- `CelticLancedbHnswComponent` — wraps a LanceDB table and
  registers an `dg.asset` that builds an HNSW index.
  (Consumes `oideachais.lancedb.indexing.build_hnsw_index`.)
- `CelticCocoindexV1Component` — wraps a CocoIndex v1 App
  and registers an `dg.asset` that calls `app.update()`.
  (Consumes the shared lifespan in
  `oideachais/cocoindex_flows/_lifespan.py`.)

Reference: openspec/changes/refactor-dlt-dagster-2026-stack-align
"""
