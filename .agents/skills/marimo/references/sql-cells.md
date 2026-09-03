# Marimo SQL Cells (`mo.sql` patterns)

The canonical SQL-in-marimo patterns. `mo.sql` is the
preferred way to run SQL queries in a reactive cell.

## Pattern 1: Basic query

```python
import duckdb


@app.cell
def _():
    con = duckdb.connect()
    return (con,)


@app.cell
def _():
    con = _
    df = mo.sql(
        "SELECT * FROM curriculum LIMIT 100",
        engine=con,
    )
    return
```

`mo.sql` returns a `polars.DataFrame` by default; the cell
displays it as a table.

## Pattern 2: f-string interpolation (parametrised queries)

```python
@app.cell
def _():
    subject = mo.ui.dropdown(options=["irish", "mathematics", "english"])
    return (subject,)


@app.cell
def _():
    con = _
    subject = _
    df = mo.sql(
        f"SELECT * FROM curriculum WHERE subject = '{subject.value}'",
        engine=con,
        output=False,
    )
    mo.ui.table(df)
    return
```

`output=False` prevents the auto-display; we wrap in
`mo.ui.table` for a nicer presentation.

⚠️ **Security warning**: f-string interpolation is **only**
safe for trusted internal queries. For user-facing apps,
use parameterised queries (see Pattern 3).

## Pattern 3: Parameterised query (safe)

```python
import duckdb


@app.cell
def _():
    subject = mo.ui.dropdown(options=["irish", "mathematics", "english"])
    return (subject,)


@app.cell
def _():
    con = duckdb.connect()
    subject = subject.value
    df = mo.sql(
        "SELECT * FROM curriculum WHERE subject = $subject",
        engine=con,
        output=False,
        parameters={"subject": subject},
    )
    mo.ui.table(df)
    return
```

The `parameters=` kwarg passes parameters safely to DuckDB
via prepared statements.

## Pattern 4: `INSTALL` + `LOAD` extensions

```python
@app.cell
def _():
    con = duckdb.connect()
    con.execute("INSTALL lance; LOAD lance;")
    con.execute("INSTALL iceberg; LOAD iceberg;")
    con.execute("INSTALL ducklake FROM core_nightly; LOAD ducklake;")
    return (con,)
```

## Pattern 5: Query a Lance table directly

```python
@app.cell
def _():
    con = duckdb.connect()
    df = mo.sql(
        "SELECT * FROM lance_scan('s3://lance/leabharlann_books') LIMIT 100",
        engine=con,
        output=False,
    )
    mo.ui.table(df)
    return
```

`lance_scan` is the canonical way to read a Lance table
from DuckDB.

## Pattern 6: MotherDuck connection

```python
@app.cell
def _():
    con = duckdb.connect("md:cianfhoghlaim")
    return (con,)


@app.cell
def _():
    con = _
    df = mo.sql(
        "SELECT subject, COUNT(*) AS n FROM education.ie.curriculum GROUP BY subject",
        engine=con,
        output=False,
    )
    mo.ui.table(df)
    return
```

## Pattern 7: DuckLake connection

```python
@app.cell
def _():
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
    return (con,)


@app.cell
def _():
    con = _
    df = mo.sql(
        "SELECT * FROM cianfhoghlaim.education.ie.curriculum LIMIT 100",
        engine=con,
        output=False,
    )
    mo.ui.table(df)
    return
```

## Pattern 8: Polars DataFrame query

```python
import polars as pl


@app.cell
def _():
    df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    return (df,)


@app.cell
def _():
    df = _
    result = mo.sql(
        "SELECT a, b, a + b AS c FROM df WHERE a > 1",
        output=False,
    )
    mo.ui.table(result)
    return
```

`mo.sql` can query any registered Polars DataFrame by name.

## Pattern 9: Reactive cell — the canonical pattern

```python
@app.cell
def _():
    subject_filter = mo.ui.multiselect(
        options=["irish", "mathematics", "english", "history"],
        value=["irish"],
    )
    return (subject_filter,)


@app.cell
def _():
    con = duckdb.connect()
    subject_filter = subject_filter.value
    # When subject_filter.value changes, this cell re-runs
    df = mo.sql(
        "SELECT * FROM curriculum WHERE subject = ANY ($subjects)",
        engine=con,
        output=False,
        parameters={"subjects": subject_filter},
    )
    mo.ui.table(df)
    return
```

The reactive dataflow means changing the multi-select
automatically re-runs the cell with the new filter. **No
explicit `on_change` callback is needed.**

## KCG conventions

- All SQL queries in marimo notebooks use `mo.sql(engine=conn,
  output=False)` + `mo.ui.table(df)` for display
- F-string interpolation is OK for trusted internal queries
  (e.g. NCCA staging tables), but `parameters=` is the
  default for user-facing apps
- MotherDuck is the preferred connection for production
  notebooks (managed DuckDB, no auth hassle)
- DuckLake is preferred for the canonical "lakehouse as
  DuckDB" pattern (Postgres catalog + S3 storage)

## Resources

- Marimo SQL: <https://docs.marimo.io/api/sql/>
- DuckDB extensions: <https://duckdb.org/docs/extensions/overview>
- MotherDuck: <https://motherduck.com/docs>
- DuckLake: <https://ducklake.org/>
