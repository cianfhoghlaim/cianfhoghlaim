# SQLMesh Init (hand off to the sqlmesh skill)

SQLMesh is a dbt-compatible SQL transformation framework. The
`sqlmesh init -t dlt` command bootstraps a SQLMesh project that
reads from a dlt-pipeline-managed DuckLake / MotherDuck destination
and applies SQL transformations downstream.

## Command

```bash
sqlmesh init -t dlt --dlt-pipeline <dlt-pipeline-name> <dialect>
```

Where:

- `<dlt-pipeline-name>` is the dlt pipeline name (e.g.
  `ireland_curriculum`)
- `<dialect>` is the SQL dialect (e.g. `duckdb`, `snowflake`,
  `bigquery`, `redshift`)

This generates a SQLMesh project with:

- A `models/` directory with starter SQL models
- A `config.yaml` that points at the dlt pipeline's destination
- A `seed.csv` for testing
- A `tests/` directory with example audit + unit tests

## Hand off to the sqlmesh skill

After `sqlmesh init`, the SQLMesh project is a **separate** tool
chain. The `dlt` skill's job is done at the init command; the
SQLMesh-specific patterns (incremental models, audits, unit tests,
virtual data warehouse) are covered by the **`sqlmesh` skill**.

## KCG usage

- The `celtic-data-engineering-pipeline` spec — the dbt-duckdb
  project at `orchestration/sqlmesh/` + `CelticDagsterDbtTranslator`
  + 2 marimo notebooks under `notebooks/`
- The `celtic-data-engineering-patterns` change (in openspec) for
  the full setup

## Reference

- The `dlt - SQLMesh.md` reference was in `docs/dlt/` (deleted with
  the `sync-skills-from-docs` change). The same content is in the
  dltHub docs at <https://dlthub.com/docs/dlt-ecosystem/transformations/sqlmesh>
- The `sqlmesh` skill for the SQLMesh-specific patterns
- The `celtic-data-engineering-patterns` openspec change
