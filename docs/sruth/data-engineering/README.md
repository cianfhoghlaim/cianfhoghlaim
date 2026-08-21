# data-engineering (package_analytics)

> **Modernized 2026-06-24 (E2 of the spaces alignment plan).**
> The Space now uses the KCG-canonical stack instead of the legacy
> BigQuery + local DuckDB.

The Cianfhoghlaim PyPI Package Analytics dashboard — a non-Gradio
HuggingFace Space that runs a Dagster + dbt + Evidence dashboard
querying the public PyPI Packages dataset on the **KCG canonical
stack** (not BigQuery).

## KCG-canonical stack (modernized)

| Layer | Before (2026-06) | After (2026-06) |
|:--|:--|:--|
| **Source** | Google BigQuery | `stedding/ingest_queue/pypi/` (KCG ingest queue) |
| **Destination** | Local DuckDB | **MotherDuck** (the canonical lakehouse) |
| **dbt** | dbt-duckdb on local | dbt-duckdb on MotherDuck |
| **Knowledge graph** | None | **Cognee + Graphiti** (the canonical memory stack) |
| **LLM** | BigQuery SQL | **LiteLLM gateway** (the canonical KCG LLM endpoint) |

The legacy BigQuery source is preserved at
`package_analytics/dlt_sources/bigquery_pipeline.py` for backward
compatibility but is no longer the primary path.

## Architecture

```
spaces/data-engineering/
├── package_analytics/                  # the Dagster code-location
│   ├── assets.py                       # the 2 Dagster assets (BigQuery, legacy)
│   ├── dlt_sources/                    # the BigQuery DLT source (legacy)
│   ├── kcg_data_layer/                 # NEW: the KCG-canonical data layer
│   │   ├── __init__.py
│   │   ├── pypi_source.py              # the canonical PyPI DLT source
│   │   ├── motherduck_destination.py   # the canonical MotherDuck destination
│   │   └── cognee_cognify.py           # the 5-stage Cognee + Graphiti cognify
│   ├── resources.py                     # the dbt CLI resource
│   ├── constants.py                     # DATA_PATH, BIGQUERY_DATASET
│   └── models.py                        # the PyArrow schema models
├── dbt_project/                         # the dbt-duckdb project (pypi_analytics)
│   └── models/                          # the dbt models
├── dashboard/                           # the Evidence dashboard
│   ├── pages/                           # the dashboard pages
│   ├── sources/                         # the dbt-built MotherDuck sources
│   └── evidence.plugins.yaml
├── docs/                                # screenshots
├── pyproject.toml                       # the Python project
├── setup.py                             # the setup.py (setuptools)
├── README.md
└── AGENTS.md                            # the Spaces priority quick reference
```

## What's in this Space

A 4-tab Evidence dashboard over the canonical MotherDuck
`oideachais.kcg_pypi` dataset:

1. **Downloads by project** (line chart) — the 5 priority
   packages (duckdb, ibis-framework, polars, trino,
   clickhouse-connect) over the last 30 days
2. **Downloads by Python version** (bar chart) — broken
   down by Python 3.x version
3. **Cognee cognify panel** (text) — the 5-stage Cognee +
   Graphiti cognify results (the canonical pattern)
4. **Source model + Langfuse** (text) — the LLM trace from
   the LiteLLM gateway

## How to run

```bash
# 1. Set the environment
export MOTHERDUCK_TOKEN=<from Infisical dev-baile/motherduck>
export LITELLM_MASTER_KEY=<from Infisical dev-baile/litellm>

# 2. Ingest the PyPI data (uses the canonical KCG source)
cd package_analytics
python -m kcg_data_layer.pypi_source

# 3. Run the dbt models (on MotherDuck)
cd ../dbt_project
dbt build --target motherduck

# 4. Run the Cognee cognify pass
cd ..
python -m kcg_data_layer.cognee_cognify

# 5. Start the Evidence dashboard
cd dashboard
npm run dev
# open http://localhost:3000
```

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../../oideachais/AGENTS.md`](../../oideachais/AGENTS.md) — the oideachais quadrant
- [`../../.agents/skills/dagster/SKILL.md`](../../.agents/skills/dagster/SKILL.md) — the Dagster patterns
- [`../../.agents/skills/motherduck-data-modeling/SKILL.md`](../../.agents/skills/motherduck-data-modeling/SKILL.md) — the MotherDuck + dbt-duckdb pattern
- [`../../.agents/skills/agent-memory-systems/SKILL.md`](../../.agents/skills/agent-memory-systems/SKILL.md) — the Cognee + Graphiti pattern
- [`openspec/specs/data-engineering-space/spec.md`](../../openspec/specs/data-engineering-space/spec.md) — the canonical spec for this Space
