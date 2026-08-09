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
"""03 — Heritage sites map (heritage + hidden heritages).

Added 2026-07-17. Altair map visualisation of all heritage sites +
hidden heritages across Ireland. 5-panel layout:

1. Per-county heritage coverage
2. Per-type breakdown (monument / castle / ringfort / church / etc.)
3. Map of all heritage sites (lat/lon)
4. Hidden heritages vs main heritages comparison
5. Summary stats table

Dual-mode usage:
    marimo edit 03_heritage_sites_map.py
    uv run 16_celtic_language/03_heritage_sites_map.py --county cork
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
        # Heritage Sites Map
        ## *Láithreáin Oidhreachta na hÉireann*

        **Source data**: 2 heritage DuckLake tables
        (`cianfhoghlaim.celtic.heritage.sites` + `.hidden_sites`) +
        the LanceDB `cianfhoghlaim.language.heritage_chunks` companion.

        LlamaSwap routing: `gemma-4-26B-A4B` (multilingual MoE).
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
        con = ibis.duckdb.connect("md:cianfhoghlaim", read_only=True)
    else:
        con = ibis.duckdb.connect(os.environ.get("DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb"), read_only=True)
    return (con, use_md)


@app.cell
def _panel_1_county(alt, con, mo, pd):
    mo.md("## 1. Per-county heritage coverage")
    rows = con.execute(
        """
        SELECT county,
               COUNT(*) AS n_sites,
               COUNT(DISTINCT site_type) AS n_types
        FROM (
            SELECT site_name, county, site_type FROM cianfhoghlaim.celtic.heritage.sites
            UNION ALL SELECT site_name, county, 'hidden' FROM cianfhoghlaim.celtic.heritage.hidden_sites
        )
        WHERE county IS NOT NULL
        GROUP BY county
        ORDER BY n_sites DESC
        LIMIT 32
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["county", "n_sites", "n_types"])
    chart = alt.Chart(df).mark_bar().encode(y=alt.Y("county:N", sort="-x"), x="n_sites:Q")
    return (chart, df)


@app.cell
def _panel_2_type(alt, con, mo, pd):
    mo.md("## 2. Per-type breakdown")
    rows = con.execute(
        """
        SELECT site_type, COUNT(*) AS n_sites
        FROM cianfhoghlaim.celtic.heritage.sites
        WHERE site_type IS NOT NULL
        GROUP BY site_type
        ORDER BY n_sites DESC
        LIMIT 20
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["site_type", "n_sites"])
    chart = alt.Chart(df).mark_bar().encode(x="n_sites:Q", y=alt.Y("site_type:N", sort="-x"))
    return (chart, df)


@app.cell
def _panel_3_map(alt, con, mo, pd):
    mo.md("## 3. Map of all heritage sites (Ireland)")
    rows = con.execute(
        """
        SELECT site_name, site_name_ga, county, site_type, latitude, longitude
        FROM cianfhoghlaim.celtic.heritage.sites
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        LIMIT 10000
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["site_name", "site_name_ga", "county", "site_type", "latitude", "longitude"])
    if not df.empty:
        chart = (
            alt.Chart(df)
            .mark_circle(size=20)
            .encode(
                longitude="longitude:Q",
                latitude="latitude:Q",
                color="site_type:N",
                tooltip=["site_name", "site_name_ga", "county", "site_type"],
            )
            .properties(height=400, width=600)
        )
        return (chart, df)
    return (df,)


@app.cell
def _panel_4_hidden(alt, con, mo, pd):
    mo.md("## 4. Hidden heritages vs main heritages comparison")
    rows = con.execute(
        """
        SELECT
            'main' AS kind, COUNT(*) AS n_sites
        FROM cianfhoghlaim.celtic.heritage.sites
        UNION ALL
        SELECT 'hidden', COUNT(*) FROM cianfhoghlaim.celtic.heritage.hidden_sites
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["kind", "n_sites"])
    chart = alt.Chart(df).mark_bar().encode(x="kind:N", y="n_sites:Q", color="kind:N")
    return (chart, df)


@app.cell
def _panel_5_summary(alt, con, mo, pd):
    mo.md("## 5. Summary stats")
    rows = con.execute(
        """
        SELECT
            'heritage_sites' AS table_name, COUNT(*) AS n_rows FROM cianfhoghlaim.celtic.heritage.sites
        UNION ALL SELECT 'hidden_sites', COUNT(*) FROM cianfhoghlaim.celtic.heritage.hidden_sites
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["table_name", "n_rows"])
    return (df,)


if __name__ == "__main__":
    app.run()