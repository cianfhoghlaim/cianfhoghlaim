# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
# ]
# ///
"""Leabharlann full-stack demo dashboard — Cianfhoghlaim Oideachais.

5-step pipeline visualisation for the
``leabharlann_full_stack_demo`` Dagster asset. Reads the demo result
from the BIEP MotherDuck + DuckLake lakehouse (``md:oideachais``) by
default; falls back to a local DuckDB file at ``LEABHARLANN_DEMO_DB``
(default ``/tmp/leabharlann_demo.duckdb``) for development.

  1. Sample PDF selection (1 UoG + 1 Zotero)
  2. BAML extraction (ExtractUoGArtifact + ExtractZoteroMetadata)
  3. CocoIndex v1 update status (books + zotero Apps)
  4. LanceDB target (rest | blob)
  5. Cognee dataset queue

The pipeline is fully runnable end-to-end from this notebook via the
`Run full-stack demo` button (calls `dagster asset materialize`).

Reference: openspec/changes/primary-secondary-british-isles-and-full-stack-demo/
"""
from __future__ import annotations

import marimo

__generated_with_marimo__ = "0.9.0"
app = marimo.App(width="wide")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
        # Leabharlann Full-Stack Demo
        ## *Cianfhoghlaim Oideachais*

        End-to-end exercise of the entire Lakehouse + BAML + CocoIndex +
        Cognee + LanceDB stack on 2 sample PDFs (1 from
        `leabharlann/ollscoil_na_gaillimhe/irish/`, 1 from
        `leabharlann/zotero/`).

        The 5 steps below are checked by 4 Dagster asset checks
        (see `cianfhoghlaim/orchestration/components/layer4_asset_generation.py`).
        """
    )
    return


@app.cell
def _():
    import os
    from pathlib import Path

    import duckdb

    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"
    df = None
    demo_db: Path | None = None
    con = None
    db_label = ""

    if use_md:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            try:
                duckdb.sql(f"SET motherduck_token='{token}'")
                con = duckdb.connect("md:oideachais")
                df = con.execute(
                    "SELECT * FROM leabharlann.full_stack_demo "
                    "ORDER BY started_at DESC LIMIT 1"
                ).fetchdf()
                db_label = "md:oideachais (MotherDuck + DuckLake)"
            except Exception:
                df = None
                db_label = "md:oideachais (query failed)"
    else:
        db_path = os.environ.get("LEABHARLANN_DEMO_DB", "/tmp/leabharlann_demo.duckdb")
        demo_db = Path(db_path)
        if demo_db.exists():
            try:
                con = duckdb.connect(str(demo_db), read_only=True)
                df = con.execute(
                    "SELECT * FROM leabharlann_full_stack_demo "
                    "ORDER BY started_at DESC LIMIT 1"
                ).fetchdf()
                db_label = f"local DuckDB ({demo_db})"
            except Exception:
                df = None
                db_label = f"local DuckDB ({demo_db}) — query failed"
        else:
            db_label = f"local DuckDB ({demo_db}) — not yet created"
    if con is not None:
        try:
            con.close()
        except Exception:
            pass
    return Path, con, df, duckdb, db_label, demo_db, os, use_md


@app.cell
def _(mo, df, db_label):
    if df is None or len(df) == 0:
        mo.md(
            f"""
            **No demo results yet** (`{db_label}`). Run the asset first:

            ```
            uv run dg asset materialize leabharlann_full_stack_demo \\
                --module cianfhoghlaim.orchestration.definitions
            ```
            """
        )
    else:
        mo.md(
            f"**Last run** (`{db_label}`): "
            f"{df['started_at'].iloc[0]} → {df['completed_at'].iloc[0]}"
        )
    return


@app.cell
def _(mo):
    mo.md(r"""## 1. Sample PDF selection""")
    return


@app.cell
def _(mo, df):
    if df is not None and len(df) > 0:
        import json

        samples = json.loads(df["samples"].iloc[0])
        rows = []
        for kind, s in samples.items():
            rows.append(
                {
                    "kind": kind,
                    "path": s.get("path", ""),
                    "extracted_chars": s.get("extracted_chars", 0),
                    "arxiv_id": s.get("arxiv_id", ""),
                    "baml_status": s.get("baml_status", ""),
                    "cognee_status": s.get("cognee_status", ""),
                }
            )
        mo.ui.table(rows, label="Sample PDFs")
    return json, rows, samples


@app.cell
def _(mo):
    mo.md(
        r"""
        ## 2. BAML extraction

        The BAML functions are defined in
        `cianfhoghlaim/baml_src/processing/author_archive.baml`
        and invoked via `b.ExtractUoGArtifact(pdf_text, file_name, file_type)`
        and `b.ExtractZoteroMetadata(pdf_text, file_name, arxiv_id)`. The
        client `ExtractEn` is English-only (BAAI/bge-large-en-v1.5).
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ## 3. CocoIndex v1 update

        The asset shells out to `cocoindex update <app>` for:

          - `cianfhoghlaim.cocoindex_flows.leabharlann_embedding:LeabharlannBooksEmbedding`
          - `cianfhoghlaim.cocoindex_flows.leabharlann_embedding:LeabharlannZoteroEmbedding`

        See `docs/cocoindex/AGENTS.md` for the v1 invocation pattern.
        """
    )
    return


@app.cell
def _(mo, df):
    if df is not None and len(df) > 0:
        mo.md(
            f"""
            ## 4. LanceDB target

            - **Target**: `{df["lancedb_target"].iloc[0]}`
            - **URI**: `{df["lancedb_uri"].iloc[0]}`

            Set `LEABHARLANN_LANCEDB_TARGET=blob` to write to the
            `lancedb` compose stack's RCLONE-mounted blob store
            (`/data/s3/leabharlann.ldb`).
            """
        )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ## 5. Cognee + FalkorDB

        The asset adds the demo text to two Cognee datasets:

          - `leabharlann_demo_uog`
          - `leabharlann_demo_zotero`

        The daily cron sensor (`cianfhoghlaim/orchestration/sensors/leabharlann_sensors.py`)
        runs the full `cognify()` + FalkorDB edge-population pipeline.
        """
    )
    return


if __name__ == "__main__":
    app.run()