# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
# ]
# [tool.uv]
# package = "biep-v3-8-jurisdiction-overview"
# ///

"""BIEP v3 8-jurisdiction overview — all 1,560 cohorts side-by-side."""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # 🌐 BIEP v3 — 8 British Isles Jurisdictions

        All 1,560 cohorts side-by-side.
        """
    )
    return (mo,)


@app.cell
def _ibis_conn(mo):
    from notebooks._shared.db import connect_md
    conn = connect_md()
    return (conn,)


@app.cell
def _overview(conn, mo):
    df = conn.sql(
        """
        SELECT
            jurisdiction,
            COUNT(*) AS subject_count,
            COUNT(DISTINCT subject_slug) AS distinct_subjects,
            COUNT(DISTINCT exam_board) AS distinct_boards
        FROM cianfhoghlaim.education._registry.subjects
        WHERE status = 'ACTIVE'
        GROUP BY jurisdiction
        ORDER BY jurisdiction
        """
    ).execute()
    mo.ui.table(df, label="1,560 cohorts across 8 jurisdictions")
    return (df,)


@app.cell
def _matrix(conn, mo):
    df = conn.sql(
        """
        SELECT
            jurisdiction,
            educational_stage AS stage,
            exam_board AS board,
            COUNT(*) AS cohort_count
        FROM cianfhoghlaim.education._registry.subjects
        WHERE status = 'ACTIVE'
        GROUP BY jurisdiction, educational_stage, exam_board
        ORDER BY jurisdiction, educational_stage, exam_board
        """
    ).execute()
    mo.ui.table(df, label="Cohorts by jurisdiction × stage × board")
    return (df,)


if __name__ == "__main__":
    app.run()
