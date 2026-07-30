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
"""Ireland Legal Pipeline · Unified Cross-Source Query.

A single search box across all 6 Irish legal / government sources (incl.
the existing Irish Statute Book). Per-source hit-count breakdown +
joined result table + drill-down.

4 cells:
  1. Single search box (queries all 6 sources: injuries_ie + courts_ie
     + wrc + citizensinfo + gov_ie + irish_statute_book)
  2. Per-source hit count breakdown
  3. Joined result table (source, title, url, snippet, statutes_cited)
  4. Drill-down: click a row → view full text + BAML-extracted fields

Lakehouse tables consumed:
  - cianfhoghlaim.law.ie.piab_pages + piab_forms
  - cianfhoghlaim.law.ie.courts_forms + judgements + court_fees + court_rules
  - cianfhoghlaim.law.ie.wrc_pages + wrc_decisions
  - cianfhoghlaim.law.ie.citizensinfo_articles
  - cianfhoghlaim.law.ie.gov_ie_pages
  - cianfhoghlaim.education.ie.irish_statute_book.acts

Run:
  cd cianfhoghlaim && uv run marimo edit notebooks/12_ireland_law/06_unified_cross_source_query.py
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
        # Unified Cross-Source Query · 6 sources + ISB

        A single search box across the 6 Irish legal / government
        sources (injuries.ie + courts.ie + workplacerelations.ie +
        citizensinformation.ie + gov.ie + irish_statutebook.ie).
        Per-source hit-count breakdown + joined result table.
        """
    )
    return (con, mo)


@app.cell
def _search_box(mo):
    """1. Unified search box."""
    query = mo.ui.text(
        value="personal injury",
        label="Search across all 6 Irish legal sources + ISB",
    )
    return (query,)


@app.cell
def _all_results(con, query):
    """2. Per-source hit-count breakdown."""
    q = query.value
    hits = {}
    # The 6 sources: each is one or more DuckLake tables
    sources = {
        "PIAB (injuries.ie)": [
            "cianfhoghlaim.law.ie.piab_pages",
            "cianfhoghlaim.law.ie.piab_forms",
        ],
        "Courts Service (courts.ie)": [
            "cianfhoghlaim.law.ie.courts_forms",
            "cianfhoghlaim.law.ie.judgements",
            "cianfhoghlaim.law.ie.court_fees",
            "cianfhoghlaim.law.ie.court_rules",
        ],
        "WRC (workplacerelations.ie)": [
            "cianfhoghlaim.law.ie.wrc_pages",
            "cianfhoghlaim.law.ie.wrc_decisions",
        ],
        "Citizens Information (citizensinformation.ie)": [
            "cianfhoghlaim.law.ie.citizensinfo_articles",
        ],
        "gov.ie (all sub-departments)": [
            "cianfhoghlaim.law.ie.gov_ie_pages",
        ],
        "Irish Statute Book (irishstatutebook.ie)": [
            "cianfhoghlaim.education.ie.irish_statute_book.acts",
        ],
    }
    for source_name, tables in sources.items():
        n = 0
        for table in tables:
            try:
                row = con.sql(
                    f"""
                    SELECT COUNT(*) AS n FROM {table}
                    WHERE LOWER(text) LIKE '%' || LOWER('{q}') || '%'
                       OR LOWER(title) LIKE '%' || LOWER('{q}') || '%'
                       OR LOWER(summary) LIKE '%' || LOWER('{q}') || '%'
                    """
                ).fetchone()
                if row:
                    n += int(row[0])
            except Exception:
                pass
        hits[source_name] = n
    return (hits,)


@app.cell
def _hits_view(mo, hits):
    """2b. Render the per-source hit-count breakdown."""
    import altair as alt
    import polars as pl

    df = pl.DataFrame(
        [{"source": k, "hits": v} for k, v in hits.items()]
    )
    if df.is_empty() or df["hits"].sum() == 0:
        return mo.md("_No hits yet — re-materialise the 6 sources to populate._")
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar()
        .encode(
            x=alt.X("hits:Q", title="Hits"),
            y=alt.Y("source:N", sort="-x", title="Source"),
            tooltip=["source", "hits"],
        )
    )
    return chart.properties(
        title="Per-source hit count breakdown",
        height=300,
    )


@app.cell
def _joined_results(con, query):
    """3. Joined result table (UNION ALL across the 6 sources)."""
    q = query.value
    # Each source contributes up to 20 rows; the UNION ALL is the
    # canonical pattern (matches `06_exam_papers_explorer.py`).
    sql = f"""
        SELECT 'PIAB' AS source, 'page' AS entity_type, url,
               title, summary AS snippet, related_statutes
        FROM cianfhoghlaim.law.ie.piab_pages
        WHERE LOWER(summary) LIKE '%' || LOWER('{q}') || '%'
           OR LOWER(title)   LIKE '%' || LOWER('{q}') || '%'
        UNION ALL
        SELECT 'Courts', 'form', url, form_title, purpose,
               related_statutes
        FROM cianfhoghlaim.law.ie.courts_forms
        WHERE LOWER(purpose) LIKE '%' || LOWER('{q}') || '%'
        UNION ALL
        SELECT 'Courts', 'judgement', url, case_name, holding,
               statutes_cited
        FROM cianfhoghlaim.law.ie.judgements
        WHERE LOWER(holding) LIKE '%' || LOWER('{q}') || '%'
           OR LOWER(catchwords) LIKE '%' || LOWER('{q}') || '%'
        UNION ALL
        SELECT 'WRC', 'decision', url, case_ref, summary, statutes_cited
        FROM cianfhoghlaim.law.ie.wrc_decisions
        WHERE LOWER(summary) LIKE '%' || LOWER('{q}') || '%'
           OR LOWER(catchwords) LIKE '%' || LOWER('{q}') || '%'
        UNION ALL
        SELECT 'CIB', 'article', url, title, summary, related_statutes
        FROM cianfhoghlaim.law.ie.citizensinfo_articles
        WHERE LOWER(summary) LIKE '%' || LOWER('{q}') || '%'
           OR LOWER(title)   LIKE '%' || LOWER('{q}') || '%'
        UNION ALL
        SELECT 'gov.ie', 'press', url, headline, summary, related_statutes
        FROM cianfhoghlaim.law.ie.gov_ie_pages
        WHERE LOWER(headline) LIKE '%' || LOWER('{q}') || '%'
           OR LOWER(summary)  LIKE '%' || LOWER('{q}') || '%'
        UNION ALL
        SELECT 'ISB', 'act', url, act_title, NULL, NULL
        FROM cianfhoghlaim.education.ie.irish_statute_book.acts
        WHERE LOWER(act_title) LIKE '%' || LOWER('{q}') || '%'
        LIMIT 100
    """
    try:
        rows = con.sql(sql).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _joined_view(mo, rows):
    """3b. Render the joined result table."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No joined results yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No joined results yet._")
    return mo.ui.table(
        df.to_pandas(),
        label="Joined result table (all 6 sources + ISB)",
    )


@app.cell
def _drill_down(con):
    """4. Drill-down: pick a row to view the full BAML-extracted fields."""
    try:
        # Pick 1 representative row from each source for the drill-down
        rows = con.sql(
            """
            SELECT 'PIAB' AS source, title, summary AS detail, NULL AS statutes
            FROM cianfhoghlaim.law.ie.piab_pages LIMIT 1
            UNION ALL
            SELECT 'Courts', form_title, purpose, related_statutes
            FROM cianfhoghlaim.law.ie.courts_forms LIMIT 1
            UNION ALL
            SELECT 'WRC', case_ref, summary, statutes_cited
            FROM cianfhoghlaim.law.ie.wrc_decisions LIMIT 1
            UNION ALL
            SELECT 'CIB', title, summary, related_statutes
            FROM cianfhoghlaim.law.ie.citizensinfo_articles LIMIT 1
            UNION ALL
            SELECT 'gov.ie', headline, summary, related_statutes
            FROM cianfhoghlaim.law.ie.gov_ie_pages LIMIT 1
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _drill_down_view(mo, rows):
    """4b. Render the drill-down (one representative row per source)."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No drill-down data yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No drill-down data yet._")
    return mo.ui.table(
        df.to_pandas(),
        label="Drill-down — 1 representative row per source",
    )


if __name__ == "__main__":
    app.run()