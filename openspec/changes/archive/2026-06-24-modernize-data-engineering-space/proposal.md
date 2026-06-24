## Why

`spaces/data-engineering/` is a standalone git repo (with its
own .git/ inside the monorepo) that runs a Dagster + dbt +
Evidence dashboard. The spec added by E1
(`openspec/specs/data-engineering-space/spec.md`) captured
the 4 key rules for modernization. This change executes the
modernization.

The Space now:

1. Reads from `stedding/ingest_queue/pypi/` (the KCG
   canonical ingest queue) instead of Google BigQuery
2. Writes to MotherDuck (the canonical lakehouse) instead
   of local DuckDB
3. Uses dbt-duckdb on MotherDuck (the canonical adapter)
4. Runs a 5-stage Cognee + Graphiti cognify pass (the
   canonical memory stack)
5. Routes LLM calls through the LiteLLM gateway

The legacy BigQuery source is preserved at
`package_analytics/dlt_sources/bigquery_pipeline.py` for
backward compatibility but is no longer the primary path.

This is committed inside the data-engineering repo (as a
standalone commit) so the monorepo's git only sees the
submodule reference change.

## What changes

- New `spaces/data-engineering/package_analytics/kcg_data_layer/`
  module (4 files): `__init__.py`, `pypi_source.py`,
  `motherduck_destination.py`, `cognee_cognify.py`
- `spaces/data-engineering/README.md` rewritten to document
  the KCG-canonical stack (with a clear before/after table)
- 1 MODIFIED Requirement to the `data-engineering-space` spec
  (the modernization in action)
