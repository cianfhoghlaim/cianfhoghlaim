# Marimo Data Pipelines (DLT + LanceDB + Iceberg + DuckLake)

The canonical "data-pipeline in a marimo notebook" patterns
for the Cianfhoghlaim platform. DLT for ingestion, LanceDB
for vector search, Iceberg/DuckLake for analytical tables,
MotherDuck for managed DuckDB.

## Pattern 1: DLT REST source with incremental cursor

```python
import dlt

@dlt.source
def curriculum_source(updated_at=dlt.sources.incremental("updated_at")):
    config = {
        "client": {"base_url": "https://ncca.ie/api/"},
        "resources": [{
            "name": "pages",
            "endpoint": {
                "path": "pages",
                "params": {
                    "updated_since": {
                        "type": "incremental",
                        "cursor_path": "updated_at",
                    },
                },
            },
        }],
    }
    return rest_api_source(config)


@app.cell
def _():
    pipeline = dlt.pipeline(destination="duckdb", dataset_name="curriculum")
    load_info = pipeline.run(curriculum_source())
    load_info
    return
```

## Pattern 2: DLT → LanceDB with `lancedb_adapter`

```python
import dlt
from lancedb import lancedb_adapter

@dlt.resource
def chunks():
    for page in fetch_pages():
        for chunk in chunk_text(page["text"]):
            yield {"text": chunk, "source": page["url"]}


@app.cell
def _():
    pipeline = dlt.pipeline(destination="duckdb", dataset_name="curriculum")
    load_info = pipeline.run(
        lancedb_adapter(chunks(), embed=["text"])
    )
    load_info
    return
```

The adapter auto-embeds the `text` column using the configured
model (env var `DESTINATION__LANCEDB__EMBEDDING_MODEL`).

## Pattern 3: Hybrid search with RRF reranking

```python
from lancedb.rerankers import RRFReranker
import lancedb

@app.cell
def _():
    db = lancedb.connect("./lancedb_data")
    table = db.open_table("chunks")
    results = (table
        .search("handwriting recognition for Irish", query_type="hybrid")
        .vector(embed_query("handwriting recognition for Irish"))
        .text("handwriting recognition for Irish")
        .rerank(RRFReranker())
        .limit(10)
        .to_pandas())
    mo.ui.table(results)
    return
```

## Pattern 4: PyIceberg REST catalog on R2

```python
from pyiceberg.catalog import load_catalog

catalog = load_catalog(
    "kcg",
    type="rest",
    uri="https://lakekeeper.cianfhoghlaim.ie/catalog",
    token=os.environ["LAKEKEEPER_TOKEN"],
)

table = catalog.load_table("cianfhoghlaim.education.ie.curriculum")
df = table.scan().to_pandas()
mo.ui.table(df.head(100))
```

## Pattern 5: DuckLake on R2 (Postgres catalog + S3 storage)

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL ducklake FROM core_nightly; LOAD ducklake;")
con.execute("""
    CREATE SECRET r2_secret (
        TYPE R2,
        KEY_ID '...',
        SECRET '...',
        ACCOUNT_ID '...'
    )
""")
con.execute("""
    ATTACH 'ducklake:oideachais' AS oideachais (
        TYPE ducklake,
        SECRET r2_secret,
        CATALOG postgres_catalog
    )
""")

@app.cell
def _():
    df = mo.sql(
        "SELECT * FROM cianfhoghlaim.education.ie.curriculum",
        engine=con,
        output=False,
    )
    mo.ui.table(df)
    return
```

## Pattern 6: MotherDuck (managed DuckDB)

```python
import duckdb

@app.cell
def _():
    con = duckdb.connect("md:cianfhoghlaim")
    return (con,)


@app.cell
def _():
    con = _
    df = mo.sql(
        "SELECT * FROM education.ie.curriculum LIMIT 100",
        engine=con,
        output=False,
    )
    mo.ui.table(df)
    return
```

## Pattern 7: `mo.sql(engine=conn)` — the canonical pattern

```python
@app.cell
def _():
    import duckdb
    con = duckdb.connect()  # or md:cianfhoghlaim, or a DuckDB file
    return (con,)


@app.cell
def _():
    con = _
    df = mo.sql(
        "SELECT subject, COUNT(*) AS n FROM curriculum GROUP BY subject",
        engine=con,
        output=False,  # we'll show it via mo.ui.table
    )
    mo.ui.table(df)
    return
```

`engine=` passes the connection explicitly. `output=False`
prevents auto-display.

## KCG conventions

- All notebooks use `mo.sql(engine=conn, output=False)` +
  `mo.ui.table(df)` for displaying query results
- The DLT destination is `duckdb` (default) or `ducklake`
  (production)
- The LanceDB adapter is used for any vector + metadata
  combination
- The PyIceberg catalog is used for any time-travel or
  multi-engine query

## Resources

- DLT docs: <https://dlthub.com/docs>
- LanceDB docs: <https://lancedb.github.io/lancedb/>
- PyIceberg docs: <https://py.iceberg.apache.org/>
- DuckLake docs: <https://ducklake.org/>
- MotherDuck: <https://motherduck.com/>
- Related skills: `.agents/skills/dlt/`, `.agents/skills/lancedb/`,
  `.agents/skills/ducklake/`, `.agents/skills/motherduck-ducklake/`
