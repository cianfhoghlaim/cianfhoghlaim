"""
oideachais.notebooks.dashboards.law.all_nations — Marimo notebook
that compares Irish, NI, EN, SCT, WLS legislation pipelines.

Phase 3.4 of lateralise-british-isles-domains. Reads from
`oideachais.law.<nation>.<entity>` (DuckLake). Each nation's
legislative register (Irish Statute Book, legislation.gov.uk
NI/EN/SCT/WLS, DOJ, Law Reform Commission) is plotted.
"""
import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    return (mo,)


@app.cell
def _header(mo):
    mo.md(
        r"""
        # Law — All Nations

        Cross-nation view of the unified lakehouse table
        `oideachais.law.<nation>.<entity>`. The 7 wired DLT sources
        (Phase 3.1-3.3) feed this view:

          | Nation | Source              | Entity |
          |--------|---------------------|--------|
          | IE     | Irish Statute Book  | irish_statute_book |
          | IE     | DOJ                 | doj    |
          | IE     | Law Reform Commission| lawreform |
          | EN     | legislation.gov.uk  | legislation |
          | NI     | legislation.gov.uk  | legislation |
          | SCT    | legislation.gov.uk  | legislation |
          | WLS    | legislation.gov.uk  | legislation |
        """
    )
    return ()


@app.cell
def _connect():
    import duckdb
    con = duckdb.connect(":memory:")
    import os
    s3_endpoint = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:3900")
    aws_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    try:
        con.execute("INSTALL httpfs; LOAD httpfs;")
    except Exception:
        pass
    con.execute(f"SET s3_endpoint='{s3_endpoint.replace('http://','').replace('https://','')}';")
    con.execute("SET s3_url_style='path';")
    con.execute("SET s3_use_ssl=false;")
    if aws_key:
        con.execute(f"SET s3_access_key_id='{aws_key}';")
    if aws_secret:
        con.execute(f"SET s3_secret_access_key='{aws_secret}';")
    return (con,)


@app.cell
def _query(con):
    """Count parquet files per (nation, source) for the law domain."""
    import os
    base = os.environ.get("DUCKLAKE_DATA_PATH", "s3://ducklake/oideachais")
    rows = []
    for nation, entity in [
        ("ie", "irish_statute_book"),
        ("ie", "doj"),
        ("ie", "lawreform"),
        ("en", "legislation"),
        ("ni", "legislation"),
        ("sct", "legislation"),
        ("wls", "legislation"),
    ]:
        for table in ("acts", "pages"):
            path = f"{base}/law.{nation}.{entity}/{table}"
            try:
                count = con.execute(
                    f"SELECT count(*) FROM glob('{path}/*.parquet')"
                ).fetchone()[0]
            except Exception:
                count = 0
            if count > 0:
                rows.append({
                    "nation": nation,
                    "entity": entity,
                    "table": table,
                    "parquet_files": count,
                })
    return (rows,)


@app.cell
def _table(mo, rows):
    if not rows:
        return mo.md("> No law data in the lakehouse yet. "
                     "Run the law_* assets to populate.")
    import pandas as pd
    df = pd.DataFrame(rows)
    return mo.ui.table(df, page_size=20, label="Law — file counts per (nation, source)")


if __name__ == "__main__":
    app.run()
