# Evidence.dev BI Dashboards

The `dagster-evidence` integration lets you run an Evidence.dev BI
dashboard as part of a Dagster asset. Evidence is a markdown-based
BI tool (think "dbt + Observable HQ" for SQL-driven analytics).

## When to use this

- You want a **SQL-driven BI dashboard** (vs a marimo notebook
  for a more code-driven experience)
- The audience is **non-technical** (Evidence dashboards are
  markdown, easy to read)
- The data lives in DuckLake / MotherDuck / Postgres

## Reference

- The `docs/dagster/integrations/dagster-evidence/` example
  (15-line README + `dagster_evidence/resource.py`) was in
  `docs/dagster/integrations/` (deleted with the
  `sync-skills-from-docs` change). The same content is in the
  upstream [dagster-evidence](https://github.com/dagster-io/dagster/tree/master/python_modules/libraries/dagster-evidence)
  package
- The Evidence.dev docs: <https://docs.evidence.dev/>
- The KCG stack currently uses **marimo notebooks** (not Evidence)
  for BI; see the `cianfhoghlaim-marimo-dashboards` openspec spec
