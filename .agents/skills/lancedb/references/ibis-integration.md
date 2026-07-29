# Ibis + DuckDB `lance_scan()` Integration

DuckDB has a `lance` extension that lets you query Lance tables as
if they were native DuckDB tables. Combined with **Ibis** (a portable
dataframe API), this enables federated SQL queries over Lance +
DuckDB + MotherDuck from a single Python (or marimo notebook)
session.

## Setup

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL lance; LOAD lance;")
con.execute(
    "CREATE VIEW books AS SELECT * FROM lance_scan('s3://lance/leabharlann_books')"
)
```

## SQL over Lance

```sql
SELECT filename, text
FROM books
WHERE subject = 'irish'
  AND chunk_start > 1000
LIMIT 10;
```

## Join Lance with DuckDB / MotherDuck

```python
# MotherDuck database (the oideachais lakehouse)
con.execute("ATTACH 'md:cianfhoghlaim' AS oideachais")

# Join: Lance embeddings + DuckDB metadata
results = con.execute("""
    SELECT
        b.filename,
        b.text,
        b.chunk_start,
        m.curriculum_area
    FROM books b
    JOIN cianfhoghlaim.education.ie.curriculum m
      ON b.subject = m.subject
    WHERE b.subject = 'irish'
    LIMIT 10
""").df()
```

## Ibis dataframe API

```python
import ibis

# Connect to DuckDB
db = ibis.duckdb.connect("md:cianfhoghlaim")

# Reference the Lance view as an Ibis table
books = db.table("books")

# Ibis query (translates to DuckDB SQL under the hood)
results = (
    books
    .filter(books.subject == "irish")
    .select("filename", "text", "chunk_start")
    .limit(10)
    .execute()  # → pandas DataFrame
)
```

## marimo notebook pattern

```python
import marimo as mo
import duckdb

@mo.cell
def con():
    c = duckdb.connect()
    c.execute("INSTALL lance; LOAD lance;")
    c.execute("ATTACH 'md:cianfhoghlaim' AS oideachais")
    c.execute("""
        CREATE VIEW books AS
        SELECT * FROM lance_scan('s3://lance/leabharlann_books')
    """)
    return c

@mo.cell
def query_results(con):
    return con.execute("""
        SELECT filename, text
        FROM books
        WHERE subject = 'irish'
        LIMIT 10
    """).df()

@mo.cell
def table_view(query_results):
    return mo.ui.table(query_results)
```

## Performance notes

- `lance_scan` is **read-only** — DuckDB cannot write to Lance
  through this API; use `lancedb` Python API for writes
- For large scans, the first query materialises the metadata cache;
  subsequent queries are fast
- The `lance` extension supports predicate pushdown for the `where`
  clause (filtering happens in Lance, not in DuckDB)
- Vector similarity search is **not** exposed via `lance_scan` — use
  `table.search()` for that, then join the results back to DuckDB

## Reference

- The `Ibis, LanceDB, and Data Stack Integration.md` document (330
  lines) lived in `docs/lance/` (deleted with the docs subdirectory)
- The `lance_scan` extension source is in the
  [duckdb-lance extension](https://github.com/lancedb/duckdb-lance)
- Ibis docs: <https://ibis-project.org/>
