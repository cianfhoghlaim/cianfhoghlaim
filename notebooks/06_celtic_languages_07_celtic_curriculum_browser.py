# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
#     "ibis-framework[duckdb,motherduck]>=9.0.0",
# ]
# ///
"""07 — Celtic curriculum browser (6 Celtic languages cross-comparison).

Added 2026-07-17. Cross-language comparison view (compare the same topic
across Irish / Welsh / Scottish / Breton / Manx / Cornish). 5-panel layout.

Dual-mode usage:
    marimo edit 07_celtic_curriculum_browser.py
    uv run 16_celtic_language/07_celtic_curriculum_browser.py --language irish
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
    sys.path.insert(0, "/Users/cianmacandeisigh/dev/kings_college_galway")
    import duckdb
    import pandas as pd
    import altair as alt
    return alt, duckdb, mo, os, pd, sys


@app.cell
def _intro(mo):
    mo.md(
        r"""
        # Celtic Curriculum Browser
        ## *Curaclam na dTeangacha Ceilteacha*

        **Source data**: 6 Celtic-language curriculum DuckLake tables
        (`cianfhoghlaim.celtic.curriculum.{irish,scottish_gaelic,welsh,breton,manx,cornish}`)
        + `cianfhoghlaim.celtic.curriculum_chunks` (LanceDB).

        LlamaSwap routing:
        - Irish → `uccix-mistral-24b` (UCCIX)
        - Welsh/Scottish/Breton/Manx/Cornish → `gemma-4-26B-A4B`
        """
    )
    return


@app.cell
def _connect(duckdb, os):
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"
    if use_md:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            duckdb.sql(f"SET motherduck_token='{token}'")
        con = duckdb.connect("md:cianfhoghlaim", read_only=True)
    else:
        con = duckdb.connect(os.environ.get("DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb"), read_only=True)
    return (con, use_md)


@app.cell
def _panel_1_per_lang(alt, con, mo, pd):
    mo.md("## 1. Per-language curriculum coverage")
    rows = con.execute(
        """
        SELECT language, COUNT(*) AS n_specs,
               COUNT(DISTINCT education_level) AS n_levels,
               COUNT(DISTINCT curriculum_body) AS n_bodies
        FROM (
            SELECT 'irish' AS language, education_level, curriculum_body FROM cianfhoghlaim.celtic.curriculum.irish
            UNION ALL SELECT 'scottish_gaelic', education_level, curriculum_body FROM cianfhoghlaim.celtic.curriculum.scottish_gaelic
            UNION ALL SELECT 'welsh', education_level, curriculum_body FROM cianfhoghlaim.celtic.curriculum.welsh
            UNION ALL SELECT 'breton', education_level, curriculum_body FROM cianfhoghlaim.celtic.curriculum.breton
            UNION ALL SELECT 'manx', education_level, curriculum_body FROM cianfhoghlaim.celtic.curriculum.manx
            UNION ALL SELECT 'cornish', education_level, curriculum_body FROM cianfhoghlaim.celtic.curriculum.cornish
        )
        GROUP BY language
        ORDER BY n_specs DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["language", "n_specs", "n_levels", "n_bodies"])
    chart = alt.Chart(df).mark_bar().encode(x="language:N", y="n_specs:Q", color="language:N")
    return (chart, df)


@app.cell
def _panel_2_level(alt, con, mo, pd):
    mo.md("## 2. Per-education-level breakdown")
    rows = con.execute(
        """
        SELECT education_level, language, COUNT(*) AS n_specs
        FROM (
            SELECT 'irish' AS language, education_level FROM cianfhoghlaim.celtic.curriculum.irish
            UNION ALL SELECT 'scottish_gaelic', education_level FROM cianfhoghlaim.celtic.curriculum.scottish_gaelic
            UNION ALL SELECT 'welsh', education_level FROM cianfhoghlaim.celtic.curriculum.welsh
            UNION ALL SELECT 'breton', education_level FROM cianfhoghlaim.celtic.curriculum.breton
            UNION ALL SELECT 'manx', education_level FROM cianfhoghlaim.celtic.curriculum.manx
            UNION ALL SELECT 'cornish', education_level FROM cianfhoghlaim.celtic.curriculum.cornish
        )
        GROUP BY education_level, language
        ORDER BY n_specs DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["education_level", "language", "n_specs"])
    chart = alt.Chart(df).mark_bar().encode(x="education_level:N", y="n_specs:Q", color="language:N")
    return (chart, df)


@app.cell
def _panel_3_body(alt, con, mo, pd):
    mo.md("## 3. Per-curriculum-body breakdown")
    rows = con.execute(
        """
        SELECT curriculum_body, COUNT(*) AS n_specs
        FROM (
            SELECT curriculum_body FROM cianfhoghlaim.celtic.curriculum.irish
            UNION ALL SELECT curriculum_body FROM cianfhoghlaim.celtic.curriculum.scottish_gaelic
            UNION ALL SELECT curriculum_body FROM cianfhoghlaim.celtic.curriculum.welsh
            UNION ALL SELECT curriculum_body FROM cianfhoghlaim.celtic.curriculum.breton
            UNION ALL SELECT curriculum_body FROM cianfhoghlaim.celtic.curriculum.manx
            UNION ALL SELECT curriculum_body FROM cianfhoghlaim.celtic.curriculum.cornish
        )
        WHERE curriculum_body IS NOT NULL
        GROUP BY curriculum_body
        ORDER BY n_specs DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["curriculum_body", "n_specs"])
    chart = alt.Chart(df).mark_bar().encode(x="n_specs:Q", y=alt.Y("curriculum_body:N", sort="-x"))
    return (chart, df)


@app.cell
def _panel_4_cross_lang(alt, con, mo, pd):
    mo.md("## 4. Cross-language comparison: same topic across Celtic languages")
    rows = con.execute(
        """
        SELECT framework_name, language, education_level
        FROM (
            SELECT framework_name, 'irish' AS language, education_level FROM cianfhoghlaim.celtic.curriculum.irish
            UNION ALL SELECT framework_name, 'scottish_gaelic', education_level FROM cianfhoghlaim.celtic.curriculum.scottish_gaelic
            UNION ALL SELECT framework_name, 'welsh', education_level FROM cianfhoghlaim.celtic.curriculum.welsh
            UNION ALL SELECT framework_name, 'breton', education_level FROM cianfhoghlaim.celtic.curriculum.breton
            UNION ALL SELECT framework_name, 'manx', education_level FROM cianfhoghlaim.celtic.curriculum.manx
            UNION ALL SELECT framework_name, 'cornish', education_level FROM cianfhoghlaim.celtic.curriculum.cornish
        )
        WHERE framework_name IS NOT NULL
        ORDER BY framework_name, language
        LIMIT 30
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["framework_name", "language", "education_level"])
    return (df,)


@app.cell
def _panel_5_summary(alt, con, mo, pd):
    mo.md("## 5. Summary stats")
    rows = con.execute(
        """
        SELECT 'irish' AS table_name, COUNT(*) AS n FROM cianfhoghlaim.celtic.curriculum.irish
        UNION ALL SELECT 'scottish_gaelic', COUNT(*) FROM cianfhoghlaim.celtic.curriculum.scottish_gaelic
        UNION ALL SELECT 'welsh', COUNT(*) FROM cianfhoghlaim.celtic.curriculum.welsh
        UNION ALL SELECT 'breton', COUNT(*) FROM cianfhoghlaim.celtic.curriculum.breton
        UNION ALL SELECT 'manx', COUNT(*) FROM cianfhoghlaim.celtic.curriculum.manx
        UNION ALL SELECT 'cornish', COUNT(*) FROM cianfhoghlaim.celtic.curriculum.cornish
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["table_name", "n"])
    return (df,)


if __name__ == "__main__":
    app.run()