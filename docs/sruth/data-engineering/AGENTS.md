# data-engineering (spaces/data-engineering/) — PyPI Package Analytics

## Priority quick reference

The 3 priority skills, the 3 priority commands, the 1 stack
this Space uses, and the 1 openspec spec. **Read this first**.

### Priority skills (3 of 108)

| Skill | When to load |
|:--|:--|
| [`dagster`](../.agents/skills/dagster/SKILL.md) | The Dagster asset patterns (this Space IS a Dagster deployment) |
| [`dlt`](../.agents/skills/dlt/SKILL.md) | The DLT source patterns (replace BigQuery with `stedding/ingest_queue/`) |
| [`evidence`](../.agents/skills/evidence/SKILL.md) | The Evidence dashboard framework (this Space uses it) |

### Priority commands

```bash
bun run ccc:search "Evidence dashboard DAG"        # find prior art
openspec list --specs                              # 32 specs total
openspec validate <change-id> --strict             # MUST pass before commit
```

### Priority openspec spec for data-engineering

| Spec | One-liner |
|:--|:--|
| (to be created) `data-engineering-space` | The PyPI Package Analytics Space (the only non-Gradio Space; dagster + dbt + evidence) |

## What this Space does

A non-Gradio Space. A Dagster + dbt + Evidence dashboard that queries
the public PyPI Packages dataset (~360 TB, ~1,020,000,000,000 rows)
on Google BigQuery and surfaces a Python 🐍 OLAP Tool Popularity
Comparison (DuckDB, ibis-framework, polars, trino, clickhouse-connect).

## Architecture

```
spaces/data-engineering/
├── package_analytics/      # the Dagster code-location
│   ├── assets.py          # the 2 Dagster assets (ingest_pypi, pypi_daily_stats)
│   ├── dlt_sources/        # the BigQuery DLT source
│   ├── resources.py        # the dbt CLI resource
│   ├── constants.py        # DATA_PATH, BIGQUERY_DATASET
│   └── models.py           # the PyArrow schema models
├── dbt_project/            # the dbt-duckdb project (pypi_analytics)
│   └── models/             # the dbt models
├── dashboard/              # the Evidence dashboard
│   ├── pages/              # the dashboard pages
│   ├── sources/            # the dbt-built DuckDB sources
│   └── evidence.plugins.yaml
├── docs/                   # screenshots (dagster_ui.png, dashboard.gif)
├── pyproject.toml          # the Python project
├── setup.py                # the setup.py (setuptools)
└── README.md
```

## What needs to change (the modernization plan)

The Space is **functional but disconnected from the KCG monorepo**.
Modernization is captured in the `modernize-data-engineering-space`
openspec change. The 4 key shifts:

1. **Source**: replace BigQuery with `stedding/ingest_queue/pypi/`
   (the KCG pattern)
2. **Storage**: replace local DuckDB with MotherDuck (using the
   new `motherduck-connections` + `motherduck-data-modeling` skills)
3. **Knowledge graph**: add Cognee + Graphiti for the curriculum KG
4. **Extraction**: add BAML extraction (using the new `baml` skill)

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — the Spaces parent
- [`../../oideachais/AGENTS.md`](../../oideachais/AGENTS.md) — the oideachais quadrant
- [`../../infrastructure/AGENTS.md`](../../infrastructure/AGENTS.md) — the 94 stacks
- [`../../.agents/skills/dagster/SKILL.md`](../../.agents/skills/dagster/SKILL.md) — the Dagster patterns
