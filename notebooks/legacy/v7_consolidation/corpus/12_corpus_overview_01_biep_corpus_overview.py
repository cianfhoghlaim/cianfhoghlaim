# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""01 — BIEP corpus overview (oideachais-marimo-dashboards spec, R1 + R9).

Bird's-eye view of the British-Isles Education Pipeline v1 corpus
across the 6 priority Leaving Certificate subjects (Mathematics,
Chemistry, Geography, Gaeilge, English, Computer Science), the 3
LC levels (higher / ordinary / foundation), the 2 working languages
(English + Gaeilge), and the 9-year window (2017-2026).

Five visualisations of the BIEP corpus:

- **Panel A** — per-subject × level matrix (heatmap of topic counts)
- **Panel B** — per-year distribution (stacked bar chart)
- **Panel C** — per-language coverage (grouped bar; en vs ga)
- **Panel D** — per-subject total depth (horizontal bar)
- **Panel E** — engine/fallback health banner

Data source: ``md:cianfhoghlaim`` (MotherDuck + DuckLake lakehouse).
Falls back to a synthetic per-subject table built from the
``BIEP_SUBJECTS`` / ``BIEP_LEVELS`` / ``BIEP_LANGUAGES`` tuples
in ``cianfhoghlaim.notebooks.nb_utils`` when the lakehouse is
unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md`` —
Requirement "5-stage education dashboards" + Requirement "BIEP
Notebooks Wire to Local Lakehouse (ibis-first)".
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
def _intro():
    import marimo as mo

    mo.md(
        r"""
        # 🌐 BIEP corpus overview

        Bird's-eye view of the British-Isles Education Pipeline v1
        corpus — the 6 priority Leaving Certificate subjects
        (Mathematics, Chemistry, Geography, Gaeilge, English, Computer
        Science) × the 3 LC levels (HL/OL/FL) × the 2 working
        languages (English + Gaeilge) × the 9-year window (2017-2026).

        Live data from ``md:cianfhoghlaim`` (MotherDuck + DuckLake
        lakehouse); synthetic fallback for offline development.

        ---
        """
    )
    return (mo,)


@app.cell
def _imports():
    import os
    from datetime import UTC, datetime, timedelta

    import altair as alt
    import duckdb
    import pandas as pd

    return UTC, alt, datetime, duckdb, os, pd, timedelta


@app.cell
def _constants():
    """BIEP canonical contracts — single source of truth."""
    from cianfhoghlaim.notebooks.nb_utils import (
        BIEP_LANGUAGES,
        BIEP_LEVELS,
        BIEP_SUBJECTS,
    )

    return BIEP_LANGUAGES, BIEP_LEVELS, BIEP_SUBJECTS


@app.cell
def _lakehouse_connect(mo, duckdb, os):
    """Connect to the lakehouse with graceful fallback."""
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"

    if use_md and token:
        try:
            duckdb.sql(f"SET motherduck_token='{token}'")
            con = ibis.duckdb.connect("md:cianfhoghlaim")
            engine_label = "md:cianfhoghlaim"
        except Exception as exc:
            con = ibis.duckdb.connect(":memory:")
            engine_label = f"local_duckdb (md unreachable: {type(exc).__name__})"
    else:
        con = ibis.duckdb.connect(":memory:")
        engine_label = "local_duckdb (offline fallback)"

    # Best-effort empty schema so SELECTs render meaningfully offline
    for _subj in (
        "mathematics", "applied_mathematics", "english", "gaeilge",
        "biology", "chemistry", "geography", "computer_science",
    ):
        con.execute(
            f"CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_{_subj}_topics ("
            "  subject VARCHAR, level VARCHAR, language VARCHAR, year INTEGER, "
            "  topic VARCHAR, n BIGINT"
            ")"
        )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(con, BIEP_SUBJECTS, BIEP_LEVELS, BIEP_LANGUAGES, engine_label, mo):
    """Load the BIEP corpus rows — live or synthetic."""
    rows = []
    if engine_label == "md:cianfhoghlaim":
        try:
            for _subj in BIEP_SUBJECTS:
                rel = f"cianfhoghlaim.leaving_cert.{_subj}_topics"
                try:
                    df_subj = con.execute(
                        f"SELECT * FROM {rel}"
                    ).fetchdf()
                    if not df_subj.empty:
                        rows.append(df_subj)
                except Exception:
                    pass
            corpus = (
                pd.concat(rows, ignore_index=True) if rows
                else pd.DataFrame()
            )
            src = "md:cianfhoghlaim"
        except Exception as exc:
            corpus = pd.DataFrame()
            src = f"md error: {exc!s:.60s}"
    else:
        corpus = pd.DataFrame()
        src = engine_label

    if corpus.empty:
        # Synthetic 6-subject × 3-level × 2-lang × 9-year corpus
        _synth = []
        for _subj in BIEP_SUBJECTS:
            for _lvl in BIEP_LEVELS:
                for _lang in BIEP_LANGUAGES:
                    for _year in range(2017, 2027):
                        # Deterministic depth per (subj, level, lang, year)
                        _seed = (
                            sum(ord(c) for c in _subj) * 17
                            + (1 + BIEP_LEVELS.index(_lvl)) * 23
                            + (0 + BIEP_LANGUAGES.index(_lang)) * 31
                            + (_year - 2017) * 5
                        ) % 350 + 50
                        _synth.append({
                            "subject": _subj,
                            "level": _lvl,
                            "language": _lang,
                            "year": _year,
                            "topic_count": _seed,
                        })
        corpus = pd.DataFrame(_synth)
        src = "synthetic (6×3×2×9=324 rows; BIEP canonical contracts)"

    mo.md(f"**Corpus source**: `{src}` — **{len(corpus)}** rows")
    return BIEP_LEVELS, BIEP_SUBJECTS, corpus, src


@app.cell
def _viz_subject_level_matrix(alt, mo, corpus):
    """Panel A — per-subject × level heatmap (topic-count totals)."""
    pivot = (
        corpus.groupby(["subject", "level"], as_index=False)["topic_count"]
        .sum()
    )

    chart = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("subject:N", title="Subject"),
            y=alt.Y("level:N", title="Level", sort="-y"),
            color=alt.Color(
                "topic_count:Q",
                title="Topics",
                scale=alt.Scale(scheme="viridis"),
            ),
            tooltip=["subject", "level", "topic_count"],
        )
        .properties(
            width=620,
            height=240,
            title="Panel A — subject × level topic-count matrix",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, pivot


@app.cell
def _viz_per_year_stacked(alt, mo, corpus):
    """Panel B — per-year distribution, stacked by subject."""
    per_year = (
        corpus.groupby(["year", "subject"], as_index=False)["topic_count"]
        .sum()
    )
    chart = (
        alt.Chart(per_year)
        .mark_area(opacity=0.7)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("topic_count:Q", title="Topics (sum)", stack=True),
            color=alt.Color("subject:N", title="Subject"),
            tooltip=["year", "subject", "topic_count"],
        )
        .properties(
            width=620,
            height=300,
            title="Panel B — topics per year (stacked by subject)",
        )
        .interactive()
    )
    mo.ui.altair_chart(chart)
    return chart, per_year


@app.cell
def _viz_language_coverage(alt, mo, corpus):
    """Panel C — EN + GA bilingual coverage, grouped bar chart."""
    by_lang = (
        corpus.groupby(["subject", "language"], as_index=False)["topic_count"]
        .sum()
    )
    chart = (
        alt.Chart(by_lang)
        .mark_bar()
        .encode(
            x=alt.X("subject:N", title="Subject"),
            y=alt.Y("topic_count:Q", title="Topics (sum)"),
            color=alt.Color("language:N", title="Language"),
            xOffset="language:N",
            tooltip=["subject", "language", "topic_count"],
        )
        .properties(
            width=620,
            height=260,
            title="Panel C — bilingual EN + GA coverage per subject",
        )
    )
    mo.ui.altair_chart(chart)
    return by_lang, chart


@app.cell
def _viz_subject_depth_bar(alt, mo, corpus):
    """Panel D — total topic depth per subject (horizontal bar)."""
    totals = (
        corpus.groupby("subject", as_index=False)["topic_count"]
        .sum()
        .sort_values("topic_count", ascending=True)
    )
    chart = (
        alt.Chart(totals)
        .mark_bar()
        .encode(
            x=alt.X("topic_count:Q", title="Topics (total)"),
            y=alt.Y("subject:N", title="Subject", sort=totals["subject"].tolist()),
            color=alt.Color("topic_count:Q", scale=alt.Scale(scheme="tealblues"), legend=None),
            tooltip=["subject", "topic_count"],
        )
        .properties(
            width=620,
            height=260,
            title="Panel D — total topic depth per subject",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, totals


@app.cell
def _health_banner(mo, engine_label, corpus):
    """Panel E — engine + row count + status banner."""
    if engine_label == "md:cianfhoghlaim":
        _n_subj = (
            int(corpus["subject"].nunique()) if "subject" in corpus.columns else 0
        )
        _n_year = (
            int(corpus["year"].nunique()) if "year" in corpus.columns else 0
        )
        status = "🟢 live"
    elif engine_label.startswith("local_duckdb (md unreachable"):
        status = "🟡 md unreachable"
    else:
        status = "🟡 offline fallback (synthetic data)"
        _n_subj = 6
        _n_year = 9

    mo.md(
        f"""
        ## Panel E — engine health

        | field | value |
        |-------|-------|
        | engine | `{engine_label}` |
        | status | {status} |
        | subjects | {_n_subj} |
        | years | {_n_year} |
        | total rows | {len(corpus)} |
        """
    )
    return (status,)


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🌐 This dashboard backs the `oideachais-marimo-dashboards`
        spec R1 (5-stage education dashboards) + R9 (BIEP Notebooks
        Wire to Local Lakehouse). See
        `openspec/specs/oideachais-marimo-dashboards/spec.md`.
        """
    )
    return


if __name__ == "__main__":
    app.run()
