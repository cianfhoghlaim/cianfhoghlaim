# Iceberg Table Integration

The `dagster-iceberg` integration wraps PyIceberg as a Dagster
IO manager. Iceberg is a lakehouse table format with ACID
transactions, time-travel, and multi-engine access (Spark, Trino,
Flink, DuckDB, PyIceberg).

## When to use this

- You need **Iceberg tables** (not DuckLake) for governance /
  multi-engine access
- The downstream consumer is **Spark / Trino / Flink** (not
  DuckDB / MotherDuck)
- You need **partition evolution** (changing the partition spec
  without rewriting data)

## PyIceberg IO manager

The integration supports multiple compute engines:

- **Arrow** (default) — fast for OLAP scans
- **Daft** — distributed compute
- **Pandas** — for small DataFrames
- **Polars** — fast, multi-threaded

```python
from dagster_iceberg import IcebergIOManager, pyarrow_io_manager

@asset(io_manager_key="iceberg_io")
def my_table():
    return pa.table({"a": [1, 2, 3], "b": [4, 5, 6]})
```

## Schema evolution

Iceberg supports adding, dropping, renaming, and reordering
columns without rewriting data. The IO manager handles this
transparently — the consumer sees the new schema on the next read.

## Reference

- The `docs/dagster/integrations/dagster-iceberg/` example
  (28-line README + 49-line `docs/features.md`) was in
  `docs/dagster/integrations/` (deleted with the
  `sync-skills-from-docs` change). The same content is in the
  upstream [dagster-iceberg](https://github.com/dagster-io/dagster/tree/master/python_modules/libraries/dagster-iceberg)
  package and the PyIceberg docs at <https://py.iceberg.apache.org/>
- The KCG stack uses **DuckLake** (not Iceberg) as the primary
  lakehouse sink — see
  `.agents/skills/dagster/references/integrations/dagster-ducklake/INDEX.md`
- The `lancedb` skill's `lance-namespace-and-iceberg.md` for the
  Lance + Iceberg companion-table pattern
