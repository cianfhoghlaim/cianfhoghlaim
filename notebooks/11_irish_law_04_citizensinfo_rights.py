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
"""Ireland Legal Pipeline · Citizens Information Rights Explorer.

Citizens Information Board (CIB) — plain-English rights / entitlements /
appeals articles.

5 cells:
  1. Article explorer (filter by category)
  2. Eligibility criteria + entitlements
  3. Appeals procedure index (articles mentioning "appeal")
  4. Statutory references (top-N statutes cited in CIB articles)
  5. Cross-source: rights article → related WRC decision → related ISB
     section

Lakehouse tables consumed:
  - cianfhoghlaim.law.ie.citizensinfo_articles
  - cianfhoghlaim.law.ie.wrc_decisions
  - cianfhoghlaim.education.ie.irish_statute_book.acts

Run:
  cd cianfhoghlaim && uv run marimo edit notebooks/12_ireland_law/04_citizensinfo_rights.py
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
        # Citizens Information Rights Explorer · citizensinformation.ie

        Plain-English rights, entitlements, and appeals procedures from
        the Citizens Information Board — linked to the relevant WRC
        decisions and Irish Statute Book sections.
        """
    )
    return (con, mo)


@app.cell
def _category_filter(mo):
    """1. Article category filter."""
    category = mo.ui.dropdown(
        options=[
            "ALL",
            "JUSTICE",
            "EMPLOYMENT",
            "SOCIAL_WELFARE",
            "HOUSING",
            "HEALTH",
            "CONSUMER",
            "MONEY_AND_TAX",
            "BIRTHS_DEATHS_MARRIAGES",
            "MOVING_COUNTRY",
            "GOVERNMENT_IN_IRELAND",
            "ENVIRONMENTAL_INFORMATION",
        ],
        value="ALL",
        label="CIB category",
    )
    return (category,)


@app.cell
def _articles(con, category):
    """1a. Article explorer (filtered by category)."""
    try:
        if category.value == "ALL":
            sql = (
                """
                SELECT url, title, category, topic, summary,
                       eligibility_criteria, entitlements, steps,
                       agencies, appeals, last_updated
                FROM cianfhoghlaim.law.ie.citizensinfo_articles
                ORDER BY category, topic
                LIMIT 100
                """
            )
        else:
            sql = (
                f"""
                SELECT url, title, category, topic, summary,
                       eligibility_criteria, entitlements, steps,
                       agencies, appeals, last_updated
                FROM cianfhoghlaim.law.ie.citizensinfo_articles
                WHERE category = '{category.value}'
                ORDER BY topic
                LIMIT 100
                """
            )
        rows = con.sql(sql).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _articles_view(mo, rows):
    """1b. Render the articles."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No CIB articles in lakehouse yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No CIB articles in lakehouse yet._")
    return mo.ui.table(df.to_pandas(), label="Citizens Information articles")


@app.cell
def _eligibility(con):
    """2. Eligibility + entitlements matrix."""
    try:
        rows = con.sql(
            """
            SELECT title, category, topic,
                   eligibility_criteria, entitlements
            FROM cianfhoghlaim.law.ie.citizensinfo_articles
            WHERE category IN ('SOCIAL_WELFARE', 'EMPLOYMENT', 'HOUSING', 'HEALTH')
            ORDER BY category, topic
            LIMIT 50
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _eligibility_view(mo, rows):
    """2b. Render the eligibility + entitlements."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No CIB eligibility data yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No CIB eligibility data yet._")
    return mo.ui.table(df.to_pandas(), label="Eligibility + entitlements")


@app.cell
def _appeals(con):
    """3. Articles mentioning 'appeal' (the appeals-procedure index)."""
    try:
        rows = con.sql(
            """
            SELECT url, title, category, topic, appeals, related_statutes
            FROM cianfhoghlaim.law.ie.citizensinfo_articles
            WHERE LOWER(summary) LIKE '%appeal%'
               OR array_length(appeals) > 0
            ORDER BY category
            LIMIT 100
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _appeals_view(mo, rows):
    """3b. Render the appeals index."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No CIB appeals data yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No CIB appeals data yet._")
    return mo.ui.table(df.to_pandas(), label="Appeals procedure index")


@app.cell
def _top_statutes(con):
    """4. Top-N statutes cited in CIB articles."""
    try:
        rows = con.sql(
            """
            SELECT statute_name, COUNT(*) AS n
            FROM (
              SELECT UNNEST(related_statutes) AS statute_name
              FROM cianfhoghlaim.law.ie.citizensinfo_articles
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
    """4b. Render the top statutes bar chart."""
    import altair as alt
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No CIB statute citations yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No CIB statute citations yet._")
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar()
        .encode(
            x=alt.X("n:Q", title="Articles citing"),
            y=alt.Y("statute_name:N", sort="-x", title="Statute"),
            tooltip=["statute_name", "n"],
        )
    )
    return chart.properties(
        title="Top 20 statutes cited in CIB articles",
        height=400,
    )


@app.cell
def _cross_source(con):
    """5. Cross-source: CIB → WRC → ISB (the unified join)."""
    try:
        rows = con.sql(
            """
            SELECT
              c.title       AS cib_title,
              c.category    AS cib_category,
              c.related_statutes,
              w.case_ref    AS wrc_case_ref,
              w.complaint_type,
              w.outcome,
              w.summary     AS wrc_summary
            FROM cianfhoghlaim.law.ie.citizensinfo_articles c
            LEFT JOIN cianfhoghlaim.law.ie.wrc_decisions w
              ON LOWER(c.summary) LIKE '%' || LOWER(REPLACE(w.complaint_type, '_', ' ')) || '%'
             OR LOWER(c.related_statutes) = LOWER(w.statutes_cited::TEXT)
            WHERE c.category = 'EMPLOYMENT'
            LIMIT 50
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _cross_source_view(mo, rows):
    """5b. Render the cross-source CIB ↔ WRC join."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md(
            "_No cross-source joins yet — re-materialise the "
            "citizensinformation and workplace_relations sources to "
            "populate._"
        )
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md(
            "_No cross-source joins yet — re-materialise the "
            "citizensinformation and workplace_relations sources to "
            "populate._"
        )
    return mo.ui.table(
        df.to_pandas(),
        label="CIB article → WRC decision → ISB section",
    )


if __name__ == "__main__":
    app.run()