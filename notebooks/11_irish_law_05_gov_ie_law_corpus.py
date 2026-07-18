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
"""Ireland Legal Pipeline · gov.ie Law Corpus (ALL sub-departments).

Covers every ministerial sub-department under `gov.ie/en/` — DoJ, DoH,
DES, DBEI, DECC, DAFM, DTCAGSM, DHLGH, DPER, DRCD, DT, DCEDIY, DFHERIS,
DSP, DFA, DoD, Taoiseach, Finance.

6 cells:
  1. Department index (18 departments)
  2. Press releases per department (timeline)
  3. Publications catalogue (filterable by dept + year)
  4. Statutory references in gov.ie press (top-N)
  5. Cross-source: gov.ie press → related WRC decision / CIB article /
     ISB section
  6. Semantic search box (full gov.ie corpus via LanceDB)

Lakehouse tables consumed:
  - cianfhoghlaim.law.ie.gov_ie_pages

Run:
  cd cianfhoghlaim && uv run marimo edit notebooks/12_ireland_law/05_gov_ie_law_corpus.py
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
        con = duckdb.connect("md:cianfhoghlaim")
    else:
        con = duckdb.connect(":memory:")

    mo.md(
        """
        # gov.ie Law Corpus · ALL sub-departments

        Press releases + publications from every Irish ministerial
        sub-department — DoJ, DoH, DES, DBEI, DECC, DAFM, DTCAGSM,
        DHLGH, DPER, DRCD, DT, DCEDIY, DFHERIS, DSP, DFA, DoD,
        Taoiseach, Finance.
        """
    )
    return (con, mo)


@app.cell
def _department_index(con):
    """1. Department index — counts of gov.ie pages per department."""
    try:
        rows = con.sql(
            """
            SELECT department, COUNT(*) AS n
            FROM cianfhoghlaim.law.ie.gov_ie_pages
            GROUP BY department
            ORDER BY n DESC
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _department_index_view(mo, rows):
    """1b. Render the department index as a bar chart."""
    import altair as alt
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No gov.ie pages in lakehouse yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No gov.ie pages in lakehouse yet._")
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar()
        .encode(
            x=alt.X("n:Q", title="Pages"),
            y=alt.Y("department:N", sort="-x", title="Department"),
            tooltip=["department", "n"],
        )
    )
    return chart.properties(
        title="gov.ie pages per department",
        height=400,
    )


@app.cell
def _press_timeline(con):
    """2. Press releases timeline per department."""
    try:
        rows = con.sql(
            """
            SELECT department, publication_date, headline, summary,
                   key_actions, related_agencies, related_statutes
            FROM cianfhoghlaim.law.ie.gov_ie_pages
            ORDER BY publication_date DESC
            LIMIT 100
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _press_timeline_view(mo, rows):
    """2b. Render the press timeline."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No gov.ie press releases yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No gov.ie press releases yet._")
    return mo.ui.table(df.to_pandas(), label="Recent gov.ie press releases")


@app.cell
def _publications(con):
    """3. Publications catalogue — filterable by dept + year."""
    try:
        rows = con.sql(
            """
            SELECT department, publication_date, headline, summary,
                   key_actions, url
            FROM cianfhoghlaim.law.ie.gov_ie_pages
            WHERE LOWER(headline) LIKE '%publication%'
               OR LOWER(summary) LIKE '%published%'
            ORDER BY publication_date DESC
            LIMIT 100
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _publications_view(mo, rows):
    """3b. Render the publications catalogue."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No gov.ie publications yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No gov.ie publications yet._")
    return mo.ui.table(df.to_pandas(), label="gov.ie publications catalogue")


@app.cell
def _top_statutes(con):
    """4. Top-N statutes cited in gov.ie press releases."""
    try:
        rows = con.sql(
            """
            SELECT statute_name, COUNT(*) AS n
            FROM (
              SELECT UNNEST(related_statutes) AS statute_name
              FROM cianfhoghlaim.law.ie.gov_ie_pages
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
        return mo.md("_No gov.ie statute citations yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No gov.ie statute citations yet._")
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar()
        .encode(
            x=alt.X("n:Q", title="Press releases citing"),
            y=alt.Y("statute_name:N", sort="-x", title="Statute"),
            tooltip=["statute_name", "n"],
        )
    )
    return chart.properties(
        title="Top 20 statutes cited in gov.ie press releases",
        height=400,
    )


@app.cell
def _cross_source(con):
    """5. Cross-source: gov.ie → WRC / CIB / Judgements / ISB."""
    try:
        rows = con.sql(
            """
            SELECT
              g.department,
              g.headline,
              g.publication_date,
              g.related_agencies,
              w.case_ref          AS wrc_case_ref,
              w.complaint_type,
              w.outcome,
              c.url               AS cib_url,
              c.title             AS cib_title
            FROM cianfhoghlaim.law.ie.gov_ie_pages g
            LEFT JOIN cianfhoghlaim.law.ie.wrc_decisions w
              ON LOWER(g.summary) LIKE '%' || LOWER(REPLACE(w.complaint_type, '_', ' ')) || '%'
            LEFT JOIN cianfhoghlaim.law.ie.citizensinfo_articles c
              ON LOWER(g.summary) LIKE '%' || LOWER(c.topic) || '%'
            LIMIT 50
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _cross_source_view(mo, rows):
    """5b. Render the cross-source gov.ie ↔ WRC ↔ CIB join."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md(
            "_No cross-source joins yet — re-materialise the gov.ie, "
            "WRC, and citizensinformation sources to populate._"
        )
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md(
            "_No cross-source joins yet — re-materialise the gov.ie, "
            "WRC, and citizensinformation sources to populate._"
        )
    return mo.ui.table(
        df.to_pandas(),
        label="gov.ie → WRC → CIB cross-source join",
    )


@app.cell
def _search_box(mo):
    """6. Semantic search box."""
    query = mo.ui.text(
        value="personal injuries assessment board",
        label="Semantic search across the full gov.ie corpus",
    )
    return (query,)


@app.cell
def _semantic_search_results(con, query):
    """6a. Semantic search results (text match fallback)."""
    try:
        rows = con.sql(
            f"""
            SELECT url, department, publication_date, headline, summary,
                   key_actions, related_agencies, related_statutes
            FROM cianfhoghlaim.law.ie.gov_ie_pages
            WHERE LOWER(headline) LIKE '%' || LOWER('{query.value}') || '%'
               OR LOWER(summary)   LIKE '%' || LOWER('{query.value}') || '%'
               OR LOWER(key_actions) LIKE '%' || LOWER('{query.value}') || '%'
            ORDER BY publication_date DESC
            LIMIT 50
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _search_results_view(mo, rows):
    """6b. Render the search results."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No gov.ie matches._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No gov.ie matches._")
    return mo.ui.table(df.to_pandas(), label="gov.ie search results")


if __name__ == "__main__":
    app.run()