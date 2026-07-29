# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
#     "lancedb>=0.20",
#     "ibis-framework[duckdb,motherduck]>=9.0.0",
# ]
# ///
"""06 — Local documents by subject viewer.

Added 2026-07-17. Per-subject PDF viewer (comp_science, gaeilge, mata,
oideachas) with LanceDB semantic search. 5-panel layout.

Dual-mode usage:
    marimo edit 06_local_documents_subject_viewer.py
    uv run 16_celtic_language/06_local_documents_subject_viewer.py --subject mata
"""

from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    import os
    import sys
    sys.path.insert(0, "/Users/cianmacandeisigh/dev/kings_college_galway")
    import duckdb
    import pandas as pd
    import altair as alt
    return alt, duckdb, mo, os, pd, sys


@app.cell
def _intro(mo):
    mo.md(
        r"""
        # Local Documents Viewer
        ## *Doiciméid Áitiúla de réir Ábhar*

        **Source data**: `cianfhoghlaim.celtic.local_documents.{subject}_documents`
        + `cianfhoghlaim.language.local_documents_chunks` (LanceDB).

        LlamaSwap routing: `qwen3-vl-8b` (OCR workhorse).
        """
    )
    return


@app.cell
def _connect(duckdb, os):
    """Connect to the canonical BIEP lakehouse via the shared helper.

    Per the post-trilogy contract, this notebook routes through
    `notebooks/_shared/db.py:connect_md()` (MotherDuck + `md:cianfhoghlaim`)
    or `connect_local()` (in-memory DuckDB fallback) rather than calling
    `ibis.duckdb.connect(...)` directly. The previous direct call
    bypassed the helper and made the alias brittle.
    """
    import sys
    sys.path.insert(0, "/Users/cianmacandeisigh/dev/kings_college_galway")
    from notebooks._shared.db import connect_md, connect_local

    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"
    if use_md:
        con = connect_md(read_only=True)
    else:
        con = connect_local(read_only=True)
    return (con, use_md)


@app.cell
def _panel_1_per_subject(alt, con, mo, pd):
    mo.md("## 1. Per-subject document count + total bytes")
    rows = con.execute(
        """
        SELECT 'comp_science' AS subject, COUNT(*) AS n_documents, SUM(size_bytes) AS total_bytes
        FROM cianfhoghlaim.celtic.local_documents.comp_science_documents
        UNION ALL SELECT 'gaeilge', COUNT(*), SUM(size_bytes) FROM cianfhoghlaim.celtic.local_documents.gaeilge_documents
        UNION ALL SELECT 'mata', COUNT(*), SUM(size_bytes) FROM cianfhoghlaim.celtic.local_documents.mata_documents
        UNION ALL SELECT 'oideachas', COUNT(*), SUM(size_bytes) FROM cianfhoghlaim.celtic.local_documents.oideachas_documents
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["subject", "n_documents", "total_bytes"])
    chart = alt.Chart(df).mark_bar().encode(x="subject:N", y="n_documents:Q", color="subject:N")
    return (chart, df)


@app.cell
def _panel_2_extension(alt, con, mo, pd):
    mo.md("## 2. Per-file extension breakdown")
    rows = con.execute(
        """
        SELECT extension, COUNT(*) AS n_files
        FROM (
            SELECT extension FROM cianfhoghlaim.celtic.local_documents.comp_science_documents
            UNION ALL SELECT extension FROM cianfhoghlaim.celtic.local_documents.gaeilge_documents
            UNION ALL SELECT extension FROM cianfhoghlaim.celtic.local_documents.mata_documents
            UNION ALL SELECT extension FROM cianfhoghlaim.celtic.local_documents.oideachas_documents
        )
        WHERE extension IS NOT NULL
        GROUP BY extension
        ORDER BY n_files DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["extension", "n_files"])
    chart = alt.Chart(df).mark_bar().encode(x="n_files:Q", y=alt.Y("extension:N", sort="-x"))
    return (chart, df)


@app.cell
def _panel_3_size(alt, con, mo, pd):
    mo.md("## 3. Per-subject size distribution")
    rows = con.execute(
        """
        SELECT
            subject,
            CASE
                WHEN size_bytes < 1024 THEN '< 1 KB'
                WHEN size_bytes < 1024*1024 THEN '1 KB - 1 MB'
                WHEN size_bytes < 10*1024*1024 THEN '1 MB - 10 MB'
                ELSE '> 10 MB'
            END AS size_bucket,
            COUNT(*) AS n_files
        FROM (
            SELECT 'comp_science' AS subject, size_bytes FROM cianfhoghlaim.celtic.local_documents.comp_science_documents
            UNION ALL SELECT 'gaeilge', size_bytes FROM cianfhoghlaim.celtic.local_documents.gaeilge_documents
            UNION ALL SELECT 'mata', size_bytes FROM cianfhoghlaim.celtic.local_documents.mata_documents
            UNION ALL SELECT 'oideachas', size_bytes FROM cianfhoghlaim.celtic.local_documents.oideachas_documents
        )
        GROUP BY subject, size_bucket
        ORDER BY subject, n_files DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["subject", "size_bucket", "n_files"])
    chart = alt.Chart(df).mark_bar().encode(x="subject:N", y="n_files:Q", color="size_bucket:N")
    return (chart, df)


@app.cell
def _panel_4_recent(alt, con, mo, pd):
    mo.md("## 4. Recent additions")
    rows = con.execute(
        """
        SELECT file_name, subject, size_bytes, modified_at
        FROM (
            SELECT file_name, 'comp_science' AS subject, size_bytes, modified_at
            FROM cianfhoghlaim.celtic.local_documents.comp_science_documents
            UNION ALL SELECT file_name, 'gaeilge', size_bytes, modified_at FROM cianfhoghlaim.celtic.local_documents.gaeilge_documents
            UNION ALL SELECT file_name, 'mata', size_bytes, modified_at FROM cianfhoghlaim.celtic.local_documents.mata_documents
            UNION ALL SELECT file_name, 'oideachas', size_bytes, modified_at FROM cianfhoghlaim.celtic.local_documents.oideachas_documents
        )
        WHERE modified_at IS NOT NULL
        ORDER BY modified_at DESC
        LIMIT 30
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["file_name", "subject", "size_bytes", "modified_at"])
    return (df,)


@app.cell
def _panel_5_search(alt, con, mo, pd):
    mo.md("## 5. Sample files (for LanceDB semantic search demo)")
    rows = con.execute(
        """
        SELECT file_name, subject, size_bytes
        FROM (
            SELECT file_name, 'comp_science' AS subject, size_bytes FROM cianfhoghlaim.celtic.local_documents.comp_science_documents
            UNION ALL SELECT file_name, 'gaeilge', size_bytes FROM cianfhoghlaim.celtic.local_documents.gaeilge_documents
            UNION ALL SELECT file_name, 'mata', size_bytes FROM cianfhoghlaim.celtic.local_documents.mata_documents
            UNION ALL SELECT file_name, 'oideachas', size_bytes FROM cianfhoghlaim.celtic.local_documents.oideachas_documents
        )
        ORDER BY subject, file_name
        LIMIT 20
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["file_name", "subject", "size_bytes"])
    return (df,)


if __name__ == "__main__":
    app.run()