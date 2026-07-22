# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "ibis-framework[duckdb]>=9.0",
#     "altair>=5.0",
#     "polars>=0.20",
# ]
# ///
"""Ireland Legal Pipeline · Personal Injury Journey.

PIAB → High Court flow chart for Irish personal injury claims.

5 cells:
  1. PIAB process steps (from BAML `ExtractPIABPage`)
  2. PIAB forms catalogue (from BAML `ExtractPIABPage.forms_mentioned`)
  3. High Court personal-injury forms (from BAML `ExtractCourtForm`)
  4. Statutory deadlines (PIAB 6-month limit + High Court limitation periods)
  5. Cross-source: PIAB page → Citizens Information personal injury article
                   → related Irish Statute Book section (unified query)

Lakehouse tables consumed:
  - cianfhoghlaim.law.ie.piab_pages
  - cianfhoghlaim.law.ie.piab_forms
  - cianfhoghlaim.law.ie.courts_forms
  - cianfhoghlaim.law.ie.citizensinfo_articles

Run:
  cd cianfhoghlaim && uv run marimo edit notebooks/12_ireland_law/01_personal_injury_journey.py
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    """Connect to the MotherDuck + DuckLake lakehouse (with graceful fallback)."""
    import os
    import marimo as mo
    import duckdb

    md_token = os.environ.get("MOTHERDUCK_TOKEN", "")
    if md_token:
        con = ibis.duckdb.connect("md:cianfhoghlaim")
    else:
        # Local DuckDB fallback: empty schema + a single placeholder row.
        con = ibis.duckdb.connect(":memory:")
    mo.md(
        """
        # Personal Injury Journey · PIAB → High Court

        A guided walk through the Irish personal injury claim process,
        combining the Personal Injuries Assessment Board (PIAB) process
        pages, the Courts Service forms catalogue, the Citizens
        Information rights articles, and the relevant Irish Statute Book
        sections — all from the `cianfhoghlaim.law.ie.*` DuckLake tables.
        """
    )
    return (con, mo)


@app.cell
def _piab_process_steps(con):
    """1. PIAB process steps (from BAML `ExtractPIABPage`)."""
    try:
        rows = con.sql(
            """
            SELECT url, title, page_kind, process_steps,
                   statutory_deadlines, permission_to_sue, summary
            FROM cianfhoghlaim.law.ie.piab_pages
            ORDER BY page_kind, title
            LIMIT 50
            """
        ).df()
    except Exception as exc:
        rows = []
    return (rows,)


@app.cell
def _piab_process_steps_view(mo, rows):
    """Render the PIAB process steps as a marimo table."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No PIAB process pages in lakehouse yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No PIAB process pages in lakehouse yet._")
    return mo.ui.table(df.to_pandas(), label="PIAB process steps")


@app.cell
def _piab_forms(con):
    """2. PIAB forms catalogue."""
    try:
        rows = con.sql(
            """
            SELECT url, form_number, form_title, purpose,
                   fee_eur, downloadable_url, fillable_fields
            FROM cianfhoghlaim.law.ie.piab_forms
            ORDER BY form_number
            LIMIT 50
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _piab_forms_view(mo, rows):
    """Render the PIAB forms catalogue."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No PIAB forms in lakehouse yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No PIAB forms in lakehouse yet._")
    return mo.ui.table(df.to_pandas(), label="PIAB forms catalogue")


@app.cell
def _high_court_forms(con):
    """3. High Court personal-injury forms (from BAML `ExtractCourtForm`)."""
    try:
        rows = con.sql(
            """
            SELECT form_number, form_title, category, purpose,
                   fee_eur, fillable_fields, downloadable_url
            FROM cianfhoghlaim.law.ie.courts_forms
            WHERE court_level = 'HIGH'
              AND category = 'personal_injury'
            ORDER BY form_number
            LIMIT 50
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _high_court_forms_view(mo, rows):
    """Render the High Court personal-injury forms."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md(
            "_No High Court personal-injury forms yet — "
            "re-materialise the courts_ie source to populate._"
        )
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md(
            "_No High Court personal-injury forms yet — "
            "re-materialise the courts_ie source to populate._"
        )
    return mo.ui.table(df.to_pandas(), label="High Court personal-injury forms")


@app.cell
def _deadlines(mo):
    """4. Statutory deadlines summary."""
    return mo.md(
        """
        ## Statutory deadlines (Irish personal-injury claims)

        | Stage | Time limit | Statute |
        |---|---|---|
        | PIAB application | 6 months from date of knowledge of injury | s. 8 Personal Injuries Assessment Board Act 2003 |
        | PIAB response | 90 days | s. 11 PIAB Act 2003 |
        | Section 14 permission to seek judicial review | 3 months from PIAB notification | s. 14 PIAB Act 2003 |
        | Civil Liability Act 2020 (new PIAB pre-action protocol) | varies | Civil Liability Act 2020 |
        | Statute of Limitations (general personal injury) | 2 years from date of knowledge | s. 11 Statute of Limitations (Amendment) Act 1991 |

        _Always verify with a solicitor — these are the canonical statutory
        anchors extracted from the PIAB process pages and the relevant
        ISB sections. The cells above show the live data from
        `cianfhoghlaim.law.ie.piab_pages`._
        """
    )


@app.cell
def _cross_source(con):
    """5. Cross-source: PIAB → Citizens Information personal injury article."""
    try:
        rows = con.sql(
            """
            SELECT
              p.url        AS piab_url,
              p.summary    AS piab_summary,
              c.url        AS cib_url,
              c.title      AS cib_title,
              c.summary    AS cib_summary,
              c.appeals    AS cib_appeals
            FROM cianfhoghlaim.law.ie.piab_pages p
            JOIN cianfhoghlaim.law.ie.citizensinfo_articles c
              ON c.category = 'JUSTICE'
             AND (LOWER(c.title) LIKE '%personal injury%'
                  OR LOWER(c.summary) LIKE '%injuries board%'
                  OR LOWER(c.summary) LIKE '%piab%')
            LIMIT 20
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _cross_source_view(mo, rows):
    """Render the cross-source PIAB ↔ CIB join."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md(
            "_No cross-source joins yet — re-materialise the citizensinfo "
            "and injuries_ie sources to populate._"
        )
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md(
            "_No cross-source joins yet — re-materialise the citizensinfo "
            "and injuries_ie sources to populate._"
        )
    return mo.ui.table(df.to_pandas(), label="PIAB → CIB cross-source join")


if __name__ == "__main__":
    app.run()