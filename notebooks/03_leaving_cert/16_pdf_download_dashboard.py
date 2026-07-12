# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
#     "boto3>=1.34",
# ]
# ///
"""Oideachais · PDF Download Dashboard.

Live monitoring of the ``pdf_downloads`` DLT table (populated by the
``pdf_downloader`` DLT source) plus an S3 inspector for the Garage bucket
that backs DuckLake. Use this to spot stuck downloads, error storms,
or oversized files.

Tabs:
    1. Live status    — counts by status (downloading, downloaded, error_*, skipped_*)
    2. Throughput     — PDFs/min over the last hour
    3. Storage        — treemap by source × cycle
    4. Retry queue    — error rows older than 1 hour
    5. Garage bucket  — list objects in s3://ducklake/oideachais/

Run:
    cd cianfhoghlaim && uv run marimo edit notebooks/pdf_download_dashboard.py
"""
from __future__ import annotations

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="wide")


@app.cell
def _():
    import os
    import pathlib
    from datetime import UTC, datetime, timedelta
    import duckdb
    import pandas as pd
    import altair as alt
    import boto3
    import marimo as mo

    mo.md(
        """
        # PDF Download Dashboard

        Live view of the ``pdf_downloads`` and ``pdf_extracted_text`` tables in
        the BIEP MotherDuck + DuckLake lakehouse (``md:oideachais``).

        The DLT source at
        ``cianfhoghlaim/dlt/british_isles/ireland/education/pdf_download.py``
        queries ``curriculum.curriculum_pdfs`` and
        ``examinations.all_exam_materials`` for pending URLs, HEAD-requests each
        one, and writes the result back with a status (``downloaded``,
        ``skipped_too_large``, ``skipped_not_pdf``, ``error_timeout``,
        ``error_http_XXX``, ``error_unknown``).
        """
    )
    return UTC, alt, boto3, datetime, duckdb, mo, os, pathlib, pd, timedelta


@app.cell
def _(mo, os, pathlib):
    MOTHERDUCK_ENABLED = os.getenv("MOTHERDUCK_ENABLED", "false").lower() == "true"
    DUCKDB_PATH = os.getenv(
        "CIANFHOGHLAIS_PDF_DOWNLOAD_DUCKDB",
        str(pathlib.Path(os.getcwd()) / "cianfhoghlaim" / ".dlt" / "curriculum_unified" / "curriculum.duckdb"),
    )
    AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:3900")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    engine_label = "MotherDuck (remote)" if MOTHERDUCK_ENABLED else "Local DuckDB / DuckLake"
    mo.md(
        f"### Engine: **{engine_label}**\n\n"
        f"Garage endpoint: `{AWS_ENDPOINT}`\n\n"
        "Credentials come from the Infisical `dev-baile` vault — never commit secrets."
    )
    return (
        AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, DUCKDB_PATH,
        MOTHERDUCK_ENABLED, engine_label,
    )


@app.cell
def _(mo):
    refresh_btn = mo.ui.run_button(label="Refresh status")
    mo.vstack([mo.md("### Live status"), refresh_btn])
    return (refresh_btn,)


@app.cell
def _(
    DUCKDB_PATH, MOTHERDUCK_ENABLED, duckdb, mo, os, pathlib, pd, refresh_btn,
):
    if not refresh_btn.value:
        status_ui = mo.md("Click *Refresh status* to load the latest counts.")
    else:
        _err = None
        _df = pd.DataFrame()

        try:
            if MOTHERDUCK_ENABLED:
                _token = os.environ.get("MOTHERDUCK_TOKEN", "")
                duckdb.sql(f"SET motherduck_token='{_token}'")
                _con = duckdb.connect("md:oideachais")
            else:
                if pathlib.Path(DUCKDB_PATH).exists():
                    _con = duckdb.connect(DUCKDB_PATH, read_only=True)
                else:
                    _err = f"Local DuckDB missing: {DUCKDB_PATH}"
            if _err is None:
                _df = _con.execute(
                    """
                    SELECT status, count(*) AS n
                    FROM curriculum.pdf_downloads
                    GROUP BY status
                    ORDER BY n DESC
                    """
                ).fetchdf()
                _con.close()
        except Exception as e:
            _err = str(e)

        if _err:
            status_ui = mo.callout(mo.md(f"**Error:** {_err}"), kind="warn")
        else:
            total = int(_df["n"].sum()) if not _df.empty else 0
            downloaded = int(_df.loc[_df["status"] == "downloaded", "n"].sum()) if not _df.empty else 0
            errors = int(_df[_df["status"].str.startswith("error_", na=False)]["n"].sum()) if not _df.empty else 0
            skipped = int(_df[_df["status"].str.startswith("skipped_", na=False)]["n"].sum()) if not _df.empty else 0

            status_ui = mo.vstack([
                mo.md(f"### PDF downloads — {total} total · {downloaded} ok · {errors} errors · {skipped} skipped"),
                mo.ui.table(_df, page_size=15),
            ])
    return (status_ui,)


@app.cell
def _(
    DUCKDB_PATH, MOTHERDUCK_ENABLED, datetime, duckdb, mo, os, pathlib, pd,
    refresh_btn, timedelta, UTC,
):
    throughput_ui = mo.md("Click *Refresh status* first.")

    if refresh_btn.value:
        _err = None
        _df = pd.DataFrame()
        try:
            if MOTHERDUCK_ENABLED:
                _token = os.environ.get("MOTHERDUCK_TOKEN", "")
                duckdb.sql(f"SET motherduck_token='{_token}'")
                _con = duckdb.connect("md:oideachais")
            else:
                if pathlib.Path(DUCKDB_PATH).exists():
                    _con = duckdb.connect(DUCKDB_PATH, read_only=True)
                else:
                    _err = f"Local DuckDB missing: {DUCKDB_PATH}"
            if _err is None:
                _df = _con.execute(
                    """
                    SELECT date_trunc('minute', downloaded_at) AS bucket,
                           count(*) AS n
                    FROM curriculum.pdf_downloads
                    WHERE downloaded_at >= now() - INTERVAL 1 HOUR
                    GROUP BY bucket
                    ORDER BY bucket
                    """,
                ).fetchdf()
                _con.close()
        except Exception as e:
            _err = str(e)

        if _err:
            throughput_ui = mo.callout(mo.md(f"**Error:** {_err}"), kind="warn")
        elif _df.empty:
            throughput_ui = mo.md("*No downloads in the last hour.*")
        else:
            throughput_ui = mo.ui.table(_df, page_size=15)
    return (throughput_ui,)


@app.cell
def _(
    DUCKDB_PATH, MOTHERDUCK_ENABLED, duckdb, mo, os, pathlib, pd, refresh_btn,
):
    storage_ui = mo.md("Click *Refresh status* first.")

    if refresh_btn.value:
        _err = None
        _df = pd.DataFrame()
        try:
            if MOTHERDUCK_ENABLED:
                _token = os.environ.get("MOTHERDUCK_TOKEN", "")
                duckdb.sql(f"SET motherduck_token='{_token}'")
                _con = duckdb.connect("md:oideachais")
            else:
                if pathlib.Path(DUCKDB_PATH).exists():
                    _con = duckdb.connect(DUCKDB_PATH, read_only=True)
                else:
                    _err = f"Local DuckDB missing: {DUCKDB_PATH}"
            if _err is None:
                _df = _con.execute(
                    """
                    SELECT source,
                           coalesce(cycle, 'unknown') AS cycle,
                           count(*) AS n,
                           sum(coalesce(size_bytes, 0)) / 1024.0 / 1024.0 AS mb
                    FROM curriculum.pdf_downloads
                    WHERE status = 'downloaded'
                    GROUP BY source, cycle
                    ORDER BY mb DESC
                    """
                ).fetchdf()
                _con.close()
        except Exception as e:
            _err = str(e)

        if _err:
            storage_ui = mo.callout(mo.md(f"**Error:** {_err}"), kind="warn")
        elif _df.empty:
            storage_ui = mo.md("*No completed downloads yet.*")
        else:
            storage_ui = mo.vstack([
                mo.md("### Storage by source × cycle"),
                mo.ui.table(_df, page_size=20),
            ])
    return (storage_ui,)


@app.cell
def _(
    DUCKDB_PATH, MOTHERDUCK_ENABLED, duckdb, mo, os, pathlib, pd,
    refresh_btn, timedelta, datetime, UTC,
):
    retry_ui = mo.md("Click *Refresh status* first.")

    if refresh_btn.value:
        _err = None
        _df = pd.DataFrame()
        cutoff = datetime.now(UTC) - timedelta(hours=1)
        try:
            if MOTHERDUCK_ENABLED:
                _token = os.environ.get("MOTHERDUCK_TOKEN", "")
                duckdb.sql(f"SET motherduck_token='{_token}'")
                _con = duckdb.connect("md:oideachais")
            else:
                if pathlib.Path(DUCKDB_PATH).exists():
                    _con = duckdb.connect(DUCKDB_PATH, read_only=True)
                else:
                    _err = f"Local DuckDB missing: {DUCKDB_PATH}"
            if _err is None:
                _df = _con.execute(
                    """
                    SELECT url, status, downloaded_at
                    FROM curriculum.pdf_downloads
                    WHERE status LIKE 'error_%'
                      AND downloaded_at < ?
                    ORDER BY downloaded_at
                    LIMIT 200
                    """,
                    [cutoff],
                ).fetchdf()
                _con.close()
        except Exception as e:
            _err = str(e)

        if _err:
            retry_ui = mo.callout(mo.md(f"**Error:** {_err}"), kind="warn")
        else:
            retry_ui = mo.vstack([
                mo.md(f"### Retry queue — {len(_df)} error rows older than 1h"),
                mo.ui.table(_df, page_size=20),
            ])
    return (retry_ui,)


@app.cell
def _(
    AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, boto3, mo, refresh_btn,
):
    bucket_ui = mo.md("Click *Refresh status* first.")

    if refresh_btn.value:
        try:
            _s3 = boto3.client(
                "s3",
                endpoint_url=AWS_ENDPOINT,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
                region_name="garage",
            )
            _rows = []
            for _bucket in ["ducklake", "lance", "iceberg"]:
                _resp = _s3.list_objects_v2(Bucket=_bucket, MaxKeys=50)
                _count = _resp.get("KeyCount", 0)
                _sample = [o["Key"] for o in _resp.get("Contents", [])[:5]]
                _rows.append({"bucket": _bucket, "key_count": _count, "sample_keys": _sample})
            bucket_ui = mo.vstack([
                mo.md("### Garage bucket inspector"),
                mo.ui.table(_rows, page_size=20),
            ])
        except Exception as e:
            bucket_ui = mo.callout(mo.md(f"**Error:** {e}"), kind="warn")
    return (bucket_ui,)


@app.cell
def _(
    bucket_ui, mo, refresh_btn, retry_ui, status_ui, storage_ui, throughput_ui,
):
    tabs = mo.ui.tabs({
        "Status": mo.vstack([refresh_btn, status_ui]),
        "Throughput": throughput_ui,
        "Storage": storage_ui,
        "Retry queue": retry_ui,
        "Buckets": bucket_ui,
    })
    tabs
    return (tabs,)


if __name__ == "__main__":
    app.run()