# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
# ]
# [tool.uv]
# package = "biep-v3-sct-wls-ni-dashboard"
# ///

"""BIEP v3 SCT + WLS + NI cohorts dashboard — 380 cohorts."""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro():
    import marimo as mo
    mo.md("# 🏴󠁧󠁢󠁳󠁣󠁴󠁿🏴󠁧󠁢󠁷󠁬󠁳󠁿🇬🇧 BIEP v3 SCT + WLS + NI cohorts (380)")
    return (mo,)


@app.cell
def _ibis_conn(mo):
    from notebooks._shared.db import connect_md
    conn = connect_md()
    return (conn,)


@app.cell
def _table(conn, mo):
    df = conn.sql(
        """
        SELECT jurisdiction, subject_slug, qualification_level, COUNT(*) AS row_count
        FROM cianfhoghlaim.education._registry.subjects
        WHERE jurisdiction IN ('scotland', 'wales', 'northern_ireland')
        GROUP BY jurisdiction, subject_slug, qualification_level
        ORDER BY jurisdiction, qualification_level, subject_slug
        """
    ).execute()
    mo.ui.table(df, label="380 SCT/WLS/NI cohorts")
    return (df,)


if __name__ == "__main__":
    app.run()
