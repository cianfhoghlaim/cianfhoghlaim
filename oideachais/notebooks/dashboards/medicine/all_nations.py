"""
oideachais.notebooks.dashboards.medicine.all_nations — Marimo
notebook that compares Irish, NI, EN, SCT, WLS medical regulators
side-by-side.

Phase 3.4 of lateralise-british-isles-domains. Reads from
`oideachais.medicine.<nation>.<entity>` (DuckLake). Each
nation's regulator (HSE, nidirect, NHS England, NHS Scotland,
NHS Wales, GMC, NICE) is plotted against the others.
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
        # Medicine — All Nations

        Cross-nation view of the unified lakehouse table
        `oideachais.medicine.<nation>.<entity>`. The 7 wired DLT
        sources (Phase 3.1-3.3) feed this view:

          | Nation | Source              | Entity |
          |--------|---------------------|--------|
          | IE     | HSE                 | hse    |
          | IE     | Medical Council     | medical_council |
          | IE     | Department of Health| doh    |
          | IE     | HPSC                | hpsc   |
          | EN     | NHS England         | nhs_england |
          | EN     | GMC                 | gmc    |
          | EN     | NICE                | nice   |
          | NI     | nidirect            | nidirect |
          | SCT    | NHS Scotland        | nhs_scotland |
          | WLS    | NHS Wales           | nhs_wales |
        """
    )
    return ()


@app.cell
def _connect():
    import duckdb
    con = duckdb.connect(":memory:")
    # Local DuckLake attach (uses the env var DUCKLAKE_DATA_PATH).
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
    """Count parquet files per (nation, source) for the medicine domain."""
    import os
    base = os.environ.get("DUCKLAKE_DATA_PATH", "s3://ducklake/oideachais")
    rows = []
    for nation, entity in [
        ("ie", "hse"),
        ("ie", "medical_council"),
        ("ie", "doh"),
        ("ie", "hpsc"),
        ("en", "nhs_england"),
        ("en", "gmc"),
        ("en", "nice"),
        ("ni", "nidirect"),
        ("sct", "nhs_scotland"),
        ("wls", "nhs_wales"),
    ]:
        for table in ("pages", "register_pages", "guidelines_pages"):
            path = f"{base}/medicine.{nation}.{entity}/{table}"
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
    """Render the row counts as a marimo table."""
    if not rows:
        return mo.md("> No medicine data in the lakehouse yet. "
                     "Run the medicine_* assets to populate.")
    import pandas as pd
    df = pd.DataFrame(rows)
    return mo.ui.table(df, page_size=20, label="Medicine — file counts per (nation, source)")


if __name__ == "__main__":
    app.run()
