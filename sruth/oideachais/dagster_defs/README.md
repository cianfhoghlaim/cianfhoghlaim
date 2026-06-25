# oideachais/dagster_defs — Dagster definitions for the Celtic Education Lakehouse

> The 2026-06 refactor (see
> `openspec/changes/refactor-dlt-dagster-2026-stack-align`):
> this directory is now a **Dagster 1.10 `defs/` folder** —
> `dg load_from_defs_folder()` is the canonical mount point,
> declared in `defs.yaml`.

## Developer workflow

```bash
# From the repo root:
uv run --package oideachais dg list defs        # all 120+ assets
uv run --package oideachais dg list components # the 3 KCG components
uv run --package oideachais dg scaffold defs MyTest my_test
```

The 3 KCG-specific Components are:

| Component | Module | Purpose |
|:--|:--|:--|
| `CelticDltSourceComponent` | `oideachais.dagster_defs.components.celtic_dlt_source` | Wrap a DLT source as a Dagster asset (replaces the hand-written `dlt_asset()` wrapper) |
| `CelticLancedbHnswComponent` | `oideachais.dagster_defs.components.celtic_lancedb_hnsw` | Build an HNSW index on a LanceDB table (consumes `oideachais.lancedb.indexing.build_hnsw_index`) |
| `CelticCocoindexV1Component` | `oideachais.dagster_defs.components.celtic_cocoindex_v1` | Run a CocoIndex v1 App update (consumes the shared lifespan in `oideachais.cocoindex_flows._lifespan`) |

## Layout

```
dagster_defs/
├── __init__.py                # Module docstring
├── README.md                  # this file
├── definitions.py             # Bootstrap entrypoint (calls dg.load_from_defs_folder)
├── defs.yaml                  # The DefsFolderComponent mount point
├── components/                # The 3 KCG-specific Components
│   ├── __init__.py
│   ├── celtic_dlt_source.py
│   ├── celtic_lancedb_hnsw.py
│   └── celtic_cocoindex_v1.py
├── assets/                    # The hand-written assets (still used for the 120+ existing assets)
│   ├── __init__.py
│   ├── ...
│   └── ie/education/...
├── sensors/                   # The 5 directory-watch sensors
├── schedules.py               # The cron schedules
├── asset_checks.py            # The 5 asset checks
├── resources.py               # The 7 resources (DuckDB, LanceDB, etc.)
├── dbt_translator.py          # The CelticDagsterDbtTranslator
├── factories.py               # The factory functions
├── partitions.py              # The legacy partitions
├── partitions_v2.py           # The v2 partitions
├── tenant_resources.py        # The per-tenant resources
└── llm_gateway_assets.py      # The LLM gateway health assets
```

## Adding a new asset

### Option A: via the SourceFactory (new in 2026-06)

For a new DLT source, edit `oideachais/sources.yaml` and add an
entry to the `CelticDltSourceComponent` defs (in
`oideachais/dagster_defs/defs.yaml`):

```yaml
- type: oideachais.dagster_defs.components.CelticDltSourceComponent
  attributes:
    source_id: ie.education.new_source
```

The asset is automatically discovered by `dg list defs`.

### Option B: hand-written (legacy)

For an asset that's not a DLT source (e.g. a BAML extraction or
a Cognee cognify pass), add a file to
`oideachais/dagster_defs/assets/`:

```python
# assets/my_new_asset.py
from dagster import asset

@asset(group_name="my_group", compute_kind="python")
def my_new_asset():
    ...
```

The asset is automatically discovered by `dg list defs` (the
`assets/` directory is a Python module; every `@asset` decorator
is picked up by `dg load_from_defs_folder()`).

## Adding a new Component

Use the `dg scaffold defs` workflow:

```bash
uv run --package oideachais dg scaffold defs CelticMyNew \
  oideachais/dagster_defs/components/celtic_my_new
```

This generates the boilerplate `defs.yaml` + Python module. Edit
the Python module to add your `dg.Component` subclass.

## Reference

- `openspec/specs/oideachais-pipeline/spec.md` — the rules
  every Component must follow
- `openspec/changes/refactor-dlt-dagster-2026-stack-align/` —
  the 2026-06 refactor proposal
- `docs.dagster.io/api/dagster/components` — the upstream
  Components documentation
