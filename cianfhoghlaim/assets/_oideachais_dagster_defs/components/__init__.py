"""
cianfhoghlaim.assets._oideachais_dagster_defs.components — Dagster dg CLI Components.

The 3 KCG-specific Components that wrap the canonical
`cianfhoghlaim.*` patterns as reusable, schema-based Components
per the Dagster 1.10 Components preview
(`docs.dagster.io/api/dagster/components`).

Each Component subclasses `dg.Component` and implements
`build_defs()`. They are discoverable via `dg list components`
and can be instantiated from YAML via `dg scaffold defs`.

The 3 Components:
- `CelticDltSourceComponent` — wraps a single DLT source and
  registers it as a `dg.asset`. (Replaces the hand-written
  `dlt_asset()` wrapper in
  `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/source_factory.py`.)
- `CelticLancedbHnswComponent` — wraps a LanceDB table and
  registers an `dg.asset` that builds an HNSW index.
  (Consumes
  `cianfhoghlaim/core/lancedb/lancedb/indexing.build_hnsw_index`.)
- `CelticCocoindexV1Component` — wraps a CocoIndex v1 App
  and registers a `dg.asset` that calls `app.update()`.
  (Consumes the shared lifespan in
  `cianfhoghlaim/embeddings/_oideachais_src/_lifespan.py`.)

Reference: openspec/changes/refactor-dlt-dagster-2026-stack-align
openspec/changes/2026-06-29-per-domain-dagster-component-migration
"""
from cianfhoghlaim.assets._oideachais_dagster_defs.components.celtic_cocoindex_v1 import (
    CelticCocoindexV1Component,
)
from cianfhoghlaim.assets._oideachais_dagster_defs.components.celtic_dlt_source import (
    CelticDltSourceComponent,
)
from cianfhoghlaim.assets._oideachais_dagster_defs.components.celtic_lancedb_hnsw import (
    CelticLancedbHnswComponent,
)

__all__ = [
    "CelticCocoindexV1Component",
    "CelticDltSourceComponent",
    "CelticLancedbHnswComponent",
]
