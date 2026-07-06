# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
# ]
# ///
"""oideachais.notebooks.dashboards.cross_domain — Marimo notebook
that shows the British Isles data coverage across all 4
lateralise domains (education, medicine, law, site_analysis).

Phase 3.4 of lateralise-british-isles-domains. The
``SourceFactory`` (``cianfhoghlaim/dlt/common/source_adapters.py``) is
the source of truth for which sources exist; the dashboard queries
the MotherDuck + DuckLake lakehouse (``md:oideachais``) to see which
tables have actual parquet files.
"""
from __future__ import annotations

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import os
    import marimo as mo
    import duckdb
    return duckdb, mo, os


@app.cell
def _header(mo):
    mo.md(
        r"""
        # British Isles — Cross-Domain Coverage

        Coverage matrix across the 4 lateralise domains and
        8 nations (IE, EN, NI, SCT, WLS + 3 crown deps):

          | Domain     | IE | EN | NI | SCT | WLS | IOM | JEY | GGY |
          |------------|----|----|----|-----|-----|-----|-----|-----|
          | education  | ✓  | ✓  | ✓  | ✓   | ✓   | ✓   | ✓   | ✓   |
          | medicine   | ✓  | ✓  | ✓  | ✓   | ✓   | —   | —   | —   |
          | law        | ✓  | ✓  | ✓  | ✓   | ✓   | —   | —   | —   |
          | statistics | —  | —  | —  | —   | —   | —   | —   | —   |

        Crown deps medicine/law and all-nations statistics are
        tracked as future work in the openspec change.
        """
    )
    return ()


@app.cell
def _connect(duckdb, os):
    s3_endpoint = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:3900")
    aws_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    use_md = bool(token)
    con = duckdb.connect(":memory:")
    if use_md:
        try:
            duckdb.sql(f"SET motherduck_token='{token}'")
            con.execute("ATTACH 'md:oideachais' (TYPE MOTHERDUCK);")
            con.execute("USE oideachais;")
            engine = "md:oideachais"
        except Exception:
            engine = "local_fallback"
            con.execute("INSTALL httpfs; LOAD httpfs;")
            con.execute(
                f"SET s3_endpoint='{s3_endpoint.replace('http://', '').replace('https://', '')}';"
            )
            con.execute("SET s3_url_style='path';")
            con.execute("SET s3_use_ssl=false;")
            if aws_key:
                con.execute(f"SET s3_access_key_id='{aws_key}';")
            if aws_secret:
                con.execute(f"SET s3_secret_access_key='{aws_secret}';")
    else:
        engine = "local_s3"
        con.execute("INSTALL httpfs; LOAD httpfs;")
        con.execute(
            f"SET s3_endpoint='{s3_endpoint.replace('http://', '').replace('https://', '')}';"
        )
        con.execute("SET s3_url_style='path';")
        con.execute("SET s3_use_ssl=false;")
        if aws_key:
            con.execute(f"SET s3_access_key_id='{aws_key}';")
        if aws_secret:
            con.execute(f"SET s3_secret_access_key='{aws_secret}';")
    return con, engine, use_md


@app.cell
def _query(con, engine):
    """Coverage matrix: how many parquet files per (domain, nation) bucket."""
    import os

    base = os.environ.get("DUCKLAKE_DATA_PATH", "s3://ducklake/oideachais")
    rows = []
    if engine == "md:oideachais":
        # Trust the BIEP lakehouse catalog (MotherDuck + DuckLake)
        for domain in ("education", "medicine", "law", "site_analysis"):
            for nation in ("ie", "en", "ni", "sct", "wls", "iom", "jey", "ggy"):
                try:
                    count = con.execute(
                        f"SELECT count(*) FROM oideachais.education.{nation}.{nation}_pages"
                    ).fetchone()[0]
                except Exception:
                    count = 0
                rows.append(
                    {
                        "domain": domain,
                        "nation": nation,
                        "parquet_files": count,
                    }
                )
    else:
        for domain in ("education", "medicine", "law", "site_analysis"):
            for nation in ("ie", "en", "ni", "sct", "wls", "iom", "jey", "ggy"):
                try:
                    count = con.execute(
                        f"SELECT count(*) FROM glob('{base}/{domain}.{nation}.*/*.parquet')"
                    ).fetchone()[0]
                except Exception:
                    count = 0
                rows.append(
                    {
                        "domain": domain,
                        "nation": nation,
                        "parquet_files": count,
                    }
                )
    return base, rows


@app.cell
def _table(mo, rows):
    if not rows:
        return mo.md("> No data in the lakehouse yet.")
    import pandas as pd

    df = pd.DataFrame(rows)
    pivot = df.pivot(index="domain", columns="nation", values="parquet_files")
    return mo.ui.table(
        pivot, page_size=10, label="Coverage matrix (parquet files per domain × nation)"
    )


if __name__ == "__main__":
    app.run()