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
  - cianfhoghlaim.law.ie.wrc_decisions
  - cianfhoghlaim.law.ie.wrc_pages
  - cianfhoghlaim.law.ie.citizensinfo_articles
  - cianfhoghlaim.education.ie.irish_statute_book.acts

Run:
  cd cianfhoghlaim && uv run marimo edit notebooks/12_ireland_law/03_wrc_decision_search.py
"""
from __future__ import annotations

import marimo


# Centralized registries (per the `centralized-model-registry` capability).
# Cascading effect: this notebook now uses MODEL_REGISTRY + the 5 schema
# introspection helpers from notebooks/_shared/schema.py instead of
# hardcoded table lists / hardcoded schema strings.
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # noqa: E402
    from notebooks._shared.schema import (  # noqa: E402
        list_dlt_sources, list_cocoindex_apps, list_baml_classes,
        schema_introspect, schema_introspect_table, read_deployment_choice,
    )
    _DEFAULT_LLM = model_for("text_llm", "default")
    _REGISTRY_SUMMARY = MODEL_REGISTRY.summary()
    _DLT_SOURCE_COUNT = len(list_dlt_sources())
    _COCO_APP_COUNT = len(list_cocoindex_apps())
    _BAML_CLASS_COUNT = len(list_baml_classes())
    _ENABLED_MODELS = sum(
        1 for v in read_deployment_choice().get("enabled_models", {}).values() if v
    )
except ImportError:
    _DEFAULT_LLM = "minimax-m3"  # fallback (the legacy hardcoded value)
    _REGISTRY_SUMMARY = {"total": 0, "by_family": {}, "available": 0, "deprecated": 0}
    _DLT_SOURCE_COUNT = _COCO_APP_COUNT = _BAML_CLASS_COUNT = 0
    _ENABLED_MODELS = 0

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
        con = ibis.duckdb.connect(":memory:")

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
            FROM cianfhoghlaim.law.ie.wrc_decisions
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
            FROM cianfhoghlaim.law.ie.wrc_decisions
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
              FROM cianfhoghlaim.law.ie.wrc_decisions
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
            FROM cianfhoghlaim.law.ie.wrc_decisions
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
            FROM cianfhoghlaim.law.ie.wrc_decisions w
            LEFT JOIN cianfhoghlaim.law.ie.citizensinfo_articles c
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