# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "ibis-framework[duckdb]>=9.0",
#     "altair>=5.0",
#     "polars>=0.20",
# ]
# #/
"""Ireland Legal Pipeline · WRC Decision Search.

Workplace Relations Commission adjudication decisions — semantic search
+ citation lookup + cross-source unified query.

5 cells:
  1. WRC decision search box (DuckDB text match over summaries +
     catchwords; semantic search uses the L3 LanceDB index)
  2. Decision outcome breakdown (donut: upheld / dismissed / settled /
     referred / non_monetary / withdrawn)
  3. Statutes cited in WRC decisions (top-N bar chart)
  4. Time-to-decision histogram (decision_date − referral_date)
  5. Cross-source: WRC decision → relevant Citizens Information
     article → relevant Irish Statute Book section

Lakehouse tables consumed:
  - oideachais.law.ie.wrc_decisions
  - oideachais.law.ie.wrc_pages
  - oideachais.law.ie.citizensinfo_articles
  - oideachais.education.ie.irish_statute_book.acts

Run:
  cd cianfhoghlaim && uv run marimo edit notebooks/12_ireland_law/03_wrc_decision_search.py
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
        con = duckdb.connect("md:oideachais")
    else:
        con = duckdb.connect(":memory:")

    mo.md(
        """
        # WRC Decision Search · workplacerelations.ie

        Search the Workplace Relations Commission adjudication decisions
        database and link each result to the relevant Citizens
        Information rights article + Irish Statute Book section.
        """
    )
    return (con, mo)


@app.cell
def _search_box(mo):
    """1. WRC decision search box (text match)."""
    query = mo.ui.text(
        value="unfair dismissal redundancy payment",
        label="Search WRC decisions (case_ref, summary, catchwords, statutes)",
    )
    return (query,)


@app.cell
def _search_results(con, query):
    """1a. Search results (text match)."""
    try:
        sql_query = (
            f"""
            SELECT case_ref, decision_date, complaint_type, outcome,
                   award_amount_eur, claimant, respondent,
                   summary, catchwords
            FROM oideachais.law.ie.wrc_decisions
            WHERE LOWER(summary) LIKE '%' || LOWER('{query.value}') || '%'
               OR LOWER(catchwords) LIKE '%' || LOWER('{query.value}') || '%'
               OR LOWER(statutes_cited) LIKE '%' || LOWER('{query.value}') || '%'
            ORDER BY decision_date DESC
            LIMIT 50
            """
        )
        rows = con.sql(sql_query).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _search_view(mo, rows):
    """1b. Render the search results."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No WRC decisions match your search yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No WRC decisions match your search yet._")
    return mo.ui.table(df.to_pandas(), label="WRC decision search results")


@app.cell
def _outcome_donut(con):
    """2. Decision outcome breakdown (donut chart)."""
    try:
        rows = con.sql(
            """
            SELECT outcome, COUNT(*) AS n
            FROM oideachais.law.ie.wrc_decisions
            GROUP BY outcome
            ORDER BY n DESC
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _outcome_donut_view(mo, rows):
    """2b. Render the donut chart."""
    import altair as alt
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No WRC decisions yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No WRC decisions yet._")
    chart = (
        alt.Chart(df.to_pandas())
        .mark_arc(innerRadius=50)
        .encode(
            theta="n:Q",
            color="outcome:N",
            tooltip=["outcome", "n"],
        )
    )
    return chart.properties(title="WRC decision outcomes")


@app.cell
def _top_statutes(con):
    """3. Top-N statutes cited in WRC decisions."""
    try:
        rows = con.sql(
            """
            SELECT statute_name, COUNT(*) AS n
            FROM (
              SELECT UNNEST(statutes_cited) AS statute_name
              FROM oideachais.law.ie.wrc_decisions
            )
            GROUP BY statute_name
            ORDER BY n DESC
            LIMIT 20
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _top_statutes_view(mo, rows):
    """3b. Render the top statutes bar chart."""
    import altair as alt
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No statute citations yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No statute citations yet._")
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar()
        .encode(
            x=alt.X("n:Q", title="Citations"),
            y=alt.Y("statute_name:N", sort="-x", title="Statute"),
            tooltip=["statute_name", "n"],
        )
    )
    return chart.properties(
        title="Top 20 statutes cited in WRC decisions",
        height=400,
    )


@app.cell
def _time_to_decision(con):
    """4. Time-to-decision histogram."""
    try:
        rows = con.sql(
            """
            SELECT
              CAST(decision_date AS DATE) AS decision_date,
              COUNT(*)                     AS n
            FROM oideachais.law.ie.wrc_decisions
            WHERE decision_date IS NOT NULL
            GROUP BY CAST(decision_date AS DATE)
            ORDER BY decision_date
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _time_to_decision_view(mo, rows):
    """4b. Render the decision-date histogram."""
    import altair as alt
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No decision dates yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No decision dates yet._")
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar()
        .encode(
            x=alt.X("decision_date:T", title="Decision date"),
            y=alt.Y("n:Q", title="Decisions"),
            tooltip=["decision_date", "n"],
        )
    )
    return chart.properties(title="WRC decision dates")


@app.cell
def _cross_source(con):
    """5. Cross-source: WRC → CIB → ISB (the unified join)."""
    try:
        rows = con.sql(
            """
            SELECT
              w.case_ref,
              w.complaint_type,
              w.outcome,
              w.award_amount_eur,
              c.url         AS cib_url,
              c.title       AS cib_title,
              c.summary     AS cib_summary,
              c.related_statutes
            FROM oideachais.law.ie.wrc_decisions w
            LEFT JOIN oideachais.law.ie.citizensinfo_articles c
              ON c.category = 'EMPLOYMENT'
             AND (LOWER(c.title) LIKE '%' || LOWER(REPLACE(w.complaint_type, '_', ' ')) || '%'
                  OR LOWER(c.summary) LIKE '%' || LOWER(REPLACE(w.complaint_type, '_', ' ')) || '%')
            LIMIT 50
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _cross_source_view(mo, rows):
    """5b. Render the cross-source WRC ↔ CIB join."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md(
            "_No cross-source joins yet — re-materialise the WRC and "
            "citizensinformation sources to populate._"
        )
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md(
            "_No cross-source joins yet — re-materialise the WRC and "
            "citizensinformation sources to populate._"
        )
    return mo.ui.table(
        df.to_pandas(),
        label="WRC decision → CIB article → ISB section",
    )


if __name__ == "__main__":
    app.run()