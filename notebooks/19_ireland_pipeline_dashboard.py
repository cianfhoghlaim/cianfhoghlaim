# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13",
#   "ibis-framework[duckdb]>=9.0",
#   "pandas>=2.2",
#   "altair>=5.0",
#   "pyarrow>=15",
# ]
#
# [tool.uv]
# package = "biep-v3-ireland-dashboard"
# ///

"""BIEP v3 Ireland cohorts dashboard.

Per the 2026-08-03-biep-v3-notebook-jurisdiction-dashboards-v1 change.

The 544 Ireland cohorts (384 LC + 108 JC + 16 short courses + 36 CBAs)
from the canonical British Isles subject registry.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- marimo (per `.agents/skills/marimo/SKILL.md`).

TABLES:
- cianfhoghlaim.education.ireland.lc.<subject>.<level>_<lang>  (384 rows)
- cianfhoghlaim.education.ireland.jc.<subject>.<year>_<lang>  (108 rows)
- cianfhoghlaim.education.ireland.jc_short_course.<course>      (16 rows)
- cianfhoghlaim.education.ireland.jc_cba.<subject>.<cba_id>     (36 rows)

Reference: openspec/changes/2026-08-03-biep-v3-notebook-jurisdiction-dashboards-v1/
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # 🇮🇪 BIEP v3 Ireland cohorts

        544 cohorts (canonical from the British Isles subject registry).
        """
    )
    return (mo,)


@app.cell
def _ibis_conn(mo):
    """The ibis-first connection (per the BIEP v3 spec)."""
    from notebooks._shared.db import connect_md
    conn = connect_md()
    mo.md("✓ ibis-first wired — `md:cianfhoghlaim`")
    return (conn,)


@app.cell
def _lc_table(conn, mo):
    """LC subjects (64 subjects × 3 levels × 2 langs = 384 rows)."""
    df = conn.sql(
        """
        SELECT subject_slug, qualification_level, language, COUNT(*) AS row_count
        FROM cianfhoghlaim.education.ireland._all_lc_cohorts
        GROUP BY subject_slug, qualification_level, language
        ORDER BY subject_slug, qualification_level, language
        """
    ).execute()
    mo.ui.table(df, label="LC cohorts (384 rows)")
    return (df,)


@app.cell
def _jc_table(conn, mo):
    """JC subjects (18 subjects × 3 years × 2 langs = 108 rows)."""
    df = conn.sql(
        """
        SELECT subject_slug, qualification_level, language, COUNT(*) AS row_count
        FROM cianfhoghlaim.education.ireland._all_jc_cohorts
        GROUP BY subject_slug, qualification_level, language
        ORDER BY subject_slug, qualification_level, language
        """
    ).execute()
    mo.ui.table(df, label="JC cohorts (108 rows)")
    return (df,)


@app.cell
def _short_table(conn, mo):
    """JC short courses (16 rows)."""
    df = conn.sql(
        """
        SELECT subject_slug, language, COUNT(*) AS row_count
        FROM cianfhoghlaim.education.ireland._all_short_courses
        GROUP BY subject_slug, language
        ORDER BY subject_slug
        """
    ).execute()
    mo.ui.table(df, label="JC short courses (16 rows)")
    return (df,)


@app.cell
def _cba_table(conn, mo):
    """JC CBAs (36 rows)."""
    df = conn.sql(
        """
        SELECT subject_slug, qualification_level, COUNT(*) AS row_count
        FROM cianfhoghlaim.education.ireland._all_cba_cohorts
        GROUP BY subject_slug, qualification_level
        ORDER BY subject_slug, qualification_level
        """
    ).execute()
    mo.ui.table(df, label="JC CBAs (36 rows)")
    return (df,)


if __name__ == "__main__":
    app.run()
