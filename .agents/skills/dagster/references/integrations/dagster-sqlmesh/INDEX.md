# SQLMesh Integration (`@sqlmesh_assets`)

The `dagster-sqlmesh` integration wraps a SQLMesh project as a set
of Dagster assets. SQLMesh is dbt-compatible; the KCG stack uses it
for the analytical layer on top of the DuckLake raw tables.

## Resource + translator

The canonical pattern uses a **central** `SQLMeshDagsterTranslator`
shared between the `SQLMeshResource` and the `@sqlmesh_assets`
decorator, to prevent key drift between the resource and the asset
views:

```python
from dagster_sqlmesh import SQLMeshResource, sqlmesh_assets, SQLMeshDagsterTranslator
from sqlmesh import Config

class MySQLMeshTranslator(SQLMeshDagsterTranslator):
    def get_asset_key(self, context):
        # Custom asset-key derivation (e.g. partition-based)
        return super().get_asset_key(context)

sqlmesh_resource = SQLMeshResource(
    config=Config(
        gateways="duckdb",
        default_connection=dlt_duckdb_connection(),  # reads from DuckLake
    ),
    translator=MySQLMeshTranslator(),
)

@sqlmesh_assets(
    translator=MySQLMeshTranslator(),  # SAME translator as the resource
)
def my_sqlmesh_assets(context, sqlmesh: SQLMeshResource):
    yield from sqlmesh.run(context=context)
```

## Partition mapping

SQLMesh models can be partitioned (by date, by `nation_code`, by
`domain`, etc.). The translator maps SQLMesh partitions to Dagster
partitions:

```python
class CurriculumSQLMeshTranslator(SQLMeshDagsterTranslator):
    def get_partition_key(self, context):
        return context.partition_key  # e.g. "ie|primary|english"
```

## KCG usage

- The `celtic-data-engineering-patterns` openspec change
- `orchestration/sqlmesh/` (or its SQLMesh equivalent) — the
  analytical models
- The `CelticDagsterDbtTranslator` (the dbt-flavored variant) at
  `orchestration/defs/celtic_dbt_assets.py`

## Reference

- The full `dagster-sqlmesh` reference (149 lines, with the central
  translator pattern) was in
  `docs/dagster/integrations/dagster-sqlmesh/README.md` (deleted
  with the `sync-skills-from-docs` change). The same content is in
  the upstream [dagster-sqlmesh](https://github.com/dagster-io/dagster/tree/master/python_modules/libraries/dagster-sqlmesh)
  package
- The `sqlmesh` skill for upstream SQLMesh patterns
- The `celtic-data-engineering-patterns` openspec change
