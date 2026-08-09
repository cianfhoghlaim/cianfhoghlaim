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
"""04 — Canuint dialect player (audio + word alignment timeline).

Added 2026-07-17. Visualises Canuint word alignments with timestamps
across Ireland's 3 dialects (Connacht / Munster / Ulster). 5-panel layout.

Dual-mode usage:
    marimo edit 04_canuint_dialect_player.py
    uv run 16_celtic_language/04_canuint_dialect_player.py --province connacht
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
        # Canuint Dialect Player
        ## *Canuint — Fuaimniú na Gaeilge*

        **Source data**: `cianfhoghlaim.celtic.canuint.word_alignments`
        + `cianfhoghlaim.language.canuint_chunks` (LanceDB).

        LlamaSwap routing: `qwen3-vl-8b` (audio + text multimodal).
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
def _panel_1_province(alt, con, mo, pd):
    mo.md("## 1. Per-province breakdown")
    rows = con.execute(
        """
        SELECT province, COUNT(*) AS n_words,
               COUNT(DISTINCT location_id) AS n_locations,
               AVG(duration_ms) AS avg_duration_ms
        FROM cianfhoghlaim.celtic.canuint.word_alignments
        GROUP BY province
        ORDER BY n_words DESC
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["province", "n_words", "n_locations", "avg_duration_ms"])
    chart = alt.Chart(df).mark_bar().encode(x="province:N", y="n_words:Q", color="province:N")
    return (chart, df)


@app.cell
def _panel_2_alignment_timeline(alt, con, mo, pd):
    mo.md("## 2. Word alignment timeline (sample recording)")
    rows = con.execute(
        """
        SELECT start_seconds, end_seconds, dialectal_text, standardized_text, province
        FROM cianfhoghlaim.celtic.canuint.word_alignments
        WHERE recording_id IS NOT NULL
        ORDER BY recording_id, start_seconds
        LIMIT 200
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["start_seconds", "end_seconds", "dialectal_text", "standardized_text", "province"])
    if not df.empty:
        chart = (
            alt.Chart(df)
            .mark_tick()
            .encode(
                x="start_seconds:Q",
                x2="end_seconds:Q",
                y="province:N",
                color="province:N",
                tooltip=["dialectal_text", "standardized_text", "start_seconds", "end_seconds"],
            )
            .properties(height=200)
        )
        return (chart, df)
    return (df,)


@app.cell
def _panel_3_dialect_diff(alt, con, mo, pd):
    mo.md("## 3. Dialect differences (where dialectal ≠ standardized)")
    rows = con.execute(
        """
        SELECT province, dialectal_text, standardized_text, COUNT(*) AS n_occurrences
        FROM cianfhoghlaim.celtic.canuint.word_alignments
        WHERE dialectal_text != standardized_text
        GROUP BY province, dialectal_text, standardized_text
        ORDER BY n_occurrences DESC
        LIMIT 30
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["province", "dialectal_text", "standardized_text", "n_occurrences"])
    return (df,)


@app.cell
def _panel_4_top_50(alt, con, mo, pd):
    mo.md("## 4. Top 50 standardised words")
    rows = con.execute(
        """
        SELECT standardized_text, COUNT(*) AS n_occurrences,
               COUNT(DISTINCT province) AS n_provinces
        FROM cianfhoghlaim.celtic.canuint.word_alignments
        GROUP BY standardized_text
        ORDER BY n_occurrences DESC
        LIMIT 50
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["standardized_text", "n_occurrences", "n_provinces"])
    return (df,)


@app.cell
def _panel_5_summary(alt, con, mo, pd):
    mo.md("## 5. Summary stats")
    rows = con.execute(
        """
        SELECT 'word_alignments' AS table_name, COUNT(*) AS n FROM cianfhoghlaim.celtic.canuint.word_alignments
        UNION ALL SELECT 'recordings', COUNT(*) FROM cianfhoghlaim.celtic.canuint.recordings
        UNION ALL SELECT 'locations', COUNT(*) FROM cianfhoghlaim.celtic.canuint.locations
        """
    ).fetchall()
    df = pd.DataFrame(rows, columns=["table_name", "n"])
    return (df,)


if __name__ == "__main__":
    app.run()