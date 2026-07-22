# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
# ]
# [tool.uv]
# package = "biep-v3-england-dashboard"
# ///

"""BIEP v3 England cohorts dashboard — 276 cohorts (3 boards × 92 subjects)."""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro():
    import marimo as mo
    mo.md("# 🏴󠁧󠁢󠁥󠁮󠁧󠁿 BIEP v3 England cohorts (276 = 3 boards × 92 subjects)")
    return (mo,)


@app.cell
def _ibis_conn(mo):
    from notebooks._shared.db import connect_md
    conn = connect_md()
    return (conn,)


@app.cell
def _matrix(conn, mo):
    df = conn.sql(
        """
        SELECT exam_board, subject_slug, qualification_level, language
        FROM cianfhoghlaim.education.england._all_cohorts
        ORDER BY exam_board, qualification_level, subject_slug
        """
    ).execute()
    mo.ui.table(df, label="276 England cohorts matrix")
    return (df,)


if __name__ == "__main__":
    app.run()
