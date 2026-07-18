# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
#     "lancedb>=0.20",
#     "ibis-framework[duckdb,motherduck]>=9.0.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
"""01 — Gaois terminology explorer (BIEP + Gaois cross-cutting).

Added 2026-07-17 by the
`openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
change. Samples every row from the 3 Gaois DuckLake tables
(Téarma + Logainm + Ainm) and exposes 5 Altair panels:

1. Per-language term coverage (ga vs en vs both)
2. Per-domain breakdown (LAW, MED, IT, EDU, ENV, FIN, SCI, etc.)
3. Top 50 most-used terms across the 3 sources
4. Map of Logainm places (lat/lon)
5. Summary stats table

Connection via `nb_utils.connect_biep_lakehouse()` (MotherDuck or
local DuckDB fallback).

Dual-mode usage:
    # Interactive
    marimo edit 01_gaois_terminology_explorer.py
    # CLI
    uv run 16_celtic_language/01_gaois_terminology_explorer.py --language ga
"""

from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo
    import os
    import sys

    # Add the project root to the path so we can import nb_utils
    sys.path.insert(0, "/Users/cianmacandeisigh/dev/kings_college_galway")

    import duckdb
    import pandas as pd
    import altair as alt
    import ibis

    return alt, duckdb, ibis, mo, os, pd, sys


@app.cell
def _intro(mo):
    mo.md(
        r"""
        # Gaois Terminology Explorer
        ## *Téarma + Logainm + Ainm*

        **Source data**: 3 Gaois DuckLake tables
        (`cianfhoghlaim.celtic.gaois.tearma_terms`,
        `logainm_places`, `ainm_biographies`) +
        the LanceDB `cianfhoghlaim.language.gaois_chunks` companion.

        Per-language LlamaSwap routing:
        - Irish (`ga`) → `uccix-mistral-24b` (UCCIX)
        - English (`en`) → `gemma-4-26B-A4B`

        See `openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/`
        for the full spec.
        """
    )
    return


@app.cell
def _connect(duckdb, os):
    # MotherDuck or local DuckDB
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"
    if use_md:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            duckdb.sql(f"SET motherduck_token='{token}'")
        con = duckdb.connect("md:cianfhoghlaim", read_only=True)
    else:
        db_path = os.environ.get("DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
        con = duckdb.connect(db_path, read_only=True)
    return (con, use_md)


@app.cell
def _panel_1_language(alt, con, mo, pd):
    mo.md("## 1. Per-language term coverage (ga vs en vs both)")
    rows = con.execute(
        """
        SELECT language, source_kind, COUNT(*) AS n_terms
        FROM (
            SELECT 'ga' AS language, 'tearma' AS source_kind FROM cianfhoghlaim.celtic.gaois.tearma_terms
            UNION ALL SELECT 'en', 'tearma' FROM cianfhoghlaim.celtic.gaois.tearma_terms
            UNION ALL SELECT 'ga', 'logainm' FROM cianfhoghlaim.celtic.gaois.logainm_places
            UNION ALL SELECT 'ga', 'ainm' FROM cianfhoghlaim.celtic.gaois.ainm_biographies
        )
        GROUP BY language, source_kind
        ORDER BY n_terms DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["language", "source_kind", "n_terms"])
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(x="source_kind:N", y="n_terms:Q", color="language:N")
        .properties(height=200)
    )
    mo.ui.plotly(chart.to_dict()) if False else mo.as_html(chart)
    return (chart, df, rows)


@app.cell
def _panel_2_domain(alt, con, mo, pd):
    mo.md("## 2. Per-domain breakdown")
    rows = con.execute(
        """
        SELECT domain, COUNT(*) AS n_terms
        FROM cianfhoghlaim.celtic.gaois.tearma_terms
        WHERE domain IS NOT NULL
        GROUP BY domain
        ORDER BY n_terms DESC
        LIMIT 30
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["domain", "n_terms"])
    chart = alt.Chart(df).mark_bar().encode(x="n_terms:Q", y=alt.Y("domain:N", sort="-x"))
    return (chart, df)


@app.cell
def _panel_3_top_50(alt, con, mo, pd):
    mo.md("## 3. Top 50 most-used terms")
    rows = con.execute(
        """
        SELECT term_en, term_ga, domain
        FROM cianfhoghlaim.celtic.gaois.tearma_terms
        WHERE term_ga IS NOT NULL OR term_en IS NOT NULL
        ORDER BY id
        LIMIT 50
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["term_en", "term_ga", "domain"])
    return (df,)


@app.cell
def _panel_4_logainm_map(alt, con, mo, pd):
    mo.md("## 4. Logainm places map (Ireland)")
    rows = con.execute(
        """
        SELECT place_name, place_name_ga, county, latitude, longitude
        FROM cianfhoghlaim.celtic.gaois.logainm_places
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        LIMIT 5000
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["place_name", "place_name_ga", "county", "latitude", "longitude"])
    if not df.empty:
        chart = (
            alt.Chart(df)
            .mark_circle(size=20)
            .encode(
                longitude="longitude:Q",
                latitude="latitude:Q",
                color=alt.value("steelblue"),
                tooltip=["place_name", "place_name_ga", "county"],
            )
            .properties(height=400)
        )
        return (chart, df)
    return (df,)


@app.cell
def _panel_5_summary(alt, con, mo, pd):
    mo.md("## 5. Summary stats")
    rows = con.execute(
        """
        SELECT
            'tearma_terms' AS table_name, COUNT(*) AS n FROM cianfhoghlaim.celtic.gaois.tearma_terms
        UNION ALL SELECT 'logainm_places', COUNT(*) FROM cianfhoghlaim.celtic.gaois.logainm_places
        UNION ALL SELECT 'ainm_biographies', COUNT(*) FROM cianfhoghlaim.celtic.gaois.ainm_biographies
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["table_name", "n"])
    return (df,)


if __name__ == "__main__":
    app.run()