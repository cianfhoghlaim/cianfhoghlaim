# Lance Namespace + Iceberg

Lance can expose its tables to **Iceberg** consumers (PyIceberg,
DuckDB `iceberg_attach`, Spark, Trino) via the
`lance.namespace.connect("iceberg", ...)` API. This is the
**companion-table pattern**: the underlying data lives in Lance (for
vector + full-text search performance), and Iceberg provides a
governance layer (ACID transactions, time-travel, schema evolution)
for downstream consumers.

## Use case

KCG writes leabharlann data to Lance (for vector search) but
also wants to expose the same data to PyIceberg consumers
(marimo notebooks, DuckDB queries, dbt models).

## Setup

```python
import lance.namespace

# Connect to an Iceberg REST catalog (Lakekeeper, Polaris, Nessie, etc.)
ns = lance.namespace.connect(
    "iceberg",
    REST_URL="http://lakekeeper.cianfhoghlaim.ie:8181/catalog",
    S3_ENDPOINT="http://minio.cianfhoghlaim.ie:9000",
    S3_ACCESS_KEY_ID="...",
    S3_SECRET_ACCESS_KEY="...",
)
```

## Register a Lance table as an Iceberg table

```python
# 1. Create a Lance table (as usual)
lance_db = lancedb.connect("s3://lance/leabharlann_books")
lance_table = lance_db.create_table("books", schema=BookSchema, mode="overwrite")
lance_table.add([...])

# 2. Register as an Iceberg table
ns.create_namespace("cianfhoghlaim")
ns.create_table(
    "cianfhoghlaim.leabharlann_books",
    metadata={"lance_uri": "s3://lance/leabharlann_books/books"},
)
```

## Query from PyIceberg

```python
from pyiceberg.catalog import load_catalog

catalog = load_catalog(
    "cianfhoghlaim",
    type="rest",
    uri="http://lakekeeper.cianfhoghlaim.ie:8181/catalog",
)
tbl = catalog.load_table("cianfhoghlaim.leabharlann_books")
df = tbl.scan().to_pandas()
```

## Query from DuckDB via `iceberg_attach`

```sql
INSTALL iceberg;
LOAD iceberg;
ATTACH 'cianfhoghlaim' AS oideachais (
    TYPE iceberg,
    ENDPOINT 'http://lakekeeper.cianfhoghlaim.ie:8181/catalog'
);
SELECT * FROM cianfhoghlaim.leabharlann_books WHERE subject = 'irish' LIMIT 10;
```

## Schema evolution

Lance supports adding columns (with `table.add_columns({...})`).
Iceberg mirrors this via `ALTER TABLE ADD COLUMN`. PyIceberg handles
this transparently — the consumer sees the new column with `NULL`
for existing rows.

## When to use this pattern

- You want the **vector + FTS performance of Lance** for the
  write/search hot path
- AND you want **Iceberg governance** (ACID, time-travel, schema
  evolution, multi-engine access) for downstream consumers
- AND you're already running an Iceberg REST catalog (Lakekeeper,
  Polaris, Nessie)

## When NOT to use this pattern

- You only need vector search (use Lance standalone)
- You don't have an Iceberg REST catalog (use plain Lance or plain Iceberg)
- Your dataset is < 1k rows (the namespace overhead is not worth it)

## KCG example

The KCG stack uses **Lakekeeper** as the Iceberg REST catalog
(deployed in `infrastructure/stacks/`), and the `oideachais` DuckLake
sink is a sibling of the Iceberg tables. The companion-table pattern
is documented in the
`orchestration/defs/` Iceberg asset group (see
the `dagster` skill's `references/integrations/dagster-iceberg/INDEX.md`).

## Reference

- The full `iceberg.py` reference implementation (590 lines) lived in
  `docs/lance/iceberg.py` (deleted with the docs subdirectory). The
  same code is in the `lance` upstream repo under
  `python/lance/namespace/iceberg.py`.
