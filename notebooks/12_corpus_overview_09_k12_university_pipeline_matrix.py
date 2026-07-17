# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""09 — K-12 → university pipeline matrix
(oideachais-marimo-dashboards spec, R-v2-9).

Per-stage coverage view of the **5 educational stages** → **tertiary**
pipeline. Shows how the 5 stages (Aistear, Primary, Junior Cycle,
Senior Cycle, Tertiary) feed into the 13 HEIs + the 8+ QQI FET
awards.

Five visualisations:

- **Panel A** — stage × level depth heatmap (5 stages × 3 LC levels)
- **Panel B** — stage × HEI pipeline matrix (heatmap of progression)
- **Panel C** — per-stage average topic depth (horizontal bar)
- **Panel D** — stage-by-stage enrolment funnel (area chart)
- **Panel E** — health banner (engine + row count + status)

Data source: ``md:cianfhoghlaim.education.<stage>_topics`` (per the
``oideachais-pipeline`` spec). Falls back to a synthetic 5×3=15 stage
× level matrix + 5×13 stage × HEI pipeline matrix when the
lakehouse is unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R-v2-9 (Phase 2 — K-12 → university pipeline coverage).
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _intro():
    import marimo as mo

    mo.md(
        r"""
        # 🎓 K-12 → university pipeline matrix

        Per-stage coverage view of the **5 educational stages** →
        **tertiary** pipeline. Shows how the 5 stages (Aistear,
        Primary, Junior Cycle, Senior Cycle, Tertiary) feed into
        the 13 HEIs + the 8+ QQI FET awards.

        Live data: ``md:cianfhoghlaim.education.<stage>_topics`` (per
        the ``oideachais-pipeline`` spec).

        ---
        """
    )
    return (mo,)


@app.cell
def _imports():
    import os

    import altair as alt
    import duckdb
    import pandas as pd

    return alt, duckdb, os, pd


@app.cell
def _constants():
    """The 5 educational stages (per the Irish education system)."""
    EDUCATION_STAGES: tuple[str, ...] = (
        "aistear",
        "primary",
        "junior_cycle",
        "senior_cycle",
        "tertiary",
    )
    """The 5 educational stages — Aistear (early years), Primary,
    Junior Cycle, Senior Cycle (Leaving Cert), Tertiary (CAO + QQI +
    University)."""

    AGE_RANGES: tuple[str, ...] = ("0-6", "4-12", "12-15", "15-18", "18+")

    LC_LEVELS: tuple[str, ...] = ("foundation", "ordinary", "higher")
    """The 3 LC levels (foundation only for L1/L2)."""

    HEI_CODES: tuple[str, ...] = (
        "UCD", "UCG", "UCC", "UL", "MU", "TCD", "DCU",
        "ATU", "TUS", "SETU", "MTU", "MIC", "RCSI",
    )

    return AGE_RANGES, EDUCATION_STAGES, HEI_CODES, LC_LEVELS


@app.cell
def _lakehouse_connect(mo, duckdb, os):
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"

    if use_md and token:
        try:
            duckdb.sql(f"SET motherduck_token='{token}'")
            con = duckdb.connect("md:oideachais")
            engine_label = "md:oideachais"
        except Exception as exc:
            con = duckdb.connect(":memory:")
            engine_label = f"local_duckdb (md unreachable: {type(exc).__name__})"
    else:
        con = duckdb.connect(":memory:")
        engine_label = "local_duckdb (offline fallback)"

    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_education_stage_topics ("
        "  stage VARCHAR, age_range VARCHAR, topic VARCHAR, level VARCHAR,"
        "  pipeline_to VARCHAR, n BIGINT"
        ")"
    )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(
    AGE_RANGES, EDUCATION_STAGES, HEI_CODES, LC_LEVELS,
    con, engine_label, mo, pd,
):
    """Read the 5-stage pipeline — live or synthetic fallback."""
    src = engine_label
    pipeline = pd.DataFrame()

    if engine_label == "md:oideachais":
        try:
            pipeline = con.execute(
                "SELECT * FROM cianfhoghlaim.education.stage_topics"
            ).fetchdf()
        except Exception:
            pipeline = pd.DataFrame()

    if pipeline.empty:
        # Synthetic 5-stage × 3-level depth matrix
        _rows = []
        for _stage_idx, _stage in enumerate(EDUCATION_STAGES):
            _age_range = AGE_RANGES[_stage_idx]
            for _level in LC_LEVELS:
                _n = (
                    (200 - _stage_idx * 30) * (1 + LC_LEVELS.index(_level))
                )
                _pipeline_to = (
                    EDUCATION_STAGES[_stage_idx + 1]
                    if _stage_idx < len(EDUCATION_STAGES) - 1
                    else HEI_CODES[_stage_idx % len(HEI_CODES)]
                )
                _rows.append({
                    "stage": _stage,
                    "age_range": _age_range,
                    "topic": f"{_stage}_{_level}",
                    "level": _level,
                    "pipeline_to": _pipeline_to,
                    "n": _n,
                })
        pipeline = pd.DataFrame(_rows)
        src = "synthetic (5 stages × 3 levels = 15 stage-level cells)"

    mo.md(f"**Source**: `{src}` — **{len(pipeline)}** rows")
    return pipeline, src


@app.cell
def _viz_stage_level_matrix(alt, mo, pipeline):
    """Panel A — stage × level depth heatmap."""
    pivot = (
        pipeline.groupby(["stage", "level"], as_index=False)["n"]
        .sum()
    )
    chart = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("level:N", title="LC level"),
            y=alt.Y("stage:N", title="Stage", sort=("-y",)),
            color=alt.Color(
                "n:Q",
                title="Topics",
                scale=alt.Scale(scheme="viridis"),
            ),
            tooltip=["stage", "level", "n"],
        )
        .properties(
            width=520,
            height=240,
            title="Panel A — stage × LC-level depth matrix",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, pivot


@app.cell
def _viz_stage_hei_matrix(alt, mo, pipeline):
    """Panel B — stage × HEI pipeline matrix."""
    pivot = (
        pipeline.groupby(["stage", "pipeline_to"], as_index=False)["n"]
        .sum()
    )
    chart = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("pipeline_to:N", title="Pipeline destination"),
            y=alt.Y("stage:N", title="Stage", sort=("-y",)),
            color=alt.Color(
                "n:Q",
                title="Topics",
                scale=alt.Scale(scheme="tealblues"),
            ),
            tooltip=["stage", "pipeline_to", "n"],
        )
        .properties(
            width=620,
            height=240,
            title="Panel B — stage × next-pipeline-destination matrix",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, pivot


@app.cell
def _viz_avg_depth(alt, mo, pipeline):
    """Panel C — per-stage average topic depth (horizontal bar)."""
    by_stage = (
        pipeline.groupby("stage", as_index=False)["n"]
        .sum()
        .sort_values("n", ascending=True)
    )
    chart = (
        alt.Chart(by_stage)
        .mark_bar()
        .encode(
            x=alt.X("n:Q", title="Total topics"),
            y=alt.Y("stage:N", title="Stage", sort=by_stage["stage"].tolist()),
            color=alt.Color("n:Q", scale=alt.Scale(scheme="oranges"), legend=None),
            tooltip=["stage", "n"],
        )
        .properties(
            width=620,
            height=240,
            title="Panel C — total topic depth per stage",
        )
    )
    mo.ui.altair_chart(chart)
    return by_stage, chart


@app.cell
def _viz_enrolment_funnel(EDUCATION_STAGES, alt, mo, pipeline):
    """Panel D — stage-by-stage enrolment funnel (area chart)."""
    funnel = (
        pipeline.groupby("stage", as_index=False)["n"]
        .sum()
    )
    chart = (
        alt.Chart(funnel)
        .mark_area(opacity=0.6, color="#4c78a8")
        .encode(
            x=alt.X("stage:N", title="Stage", sort=list(EDUCATION_STAGES)),
            y=alt.Y("n:Q", title="Topics (cumulative)"),
            tooltip=["stage", "n"],
        )
        .properties(
            width=620,
            height=280,
            title="Panel D — stage-by-stage enrolment funnel",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, funnel


@app.cell
def _health_banner(mo, engine_label, pipeline):
    if engine_label == "md:oideachais":
        _n_stages = int(pipeline["stage"].nunique()) if "stage" in pipeline.columns else 0
        status = "🟢 live"
    elif engine_label.startswith("local_duckdb (md unreachable"):
        _n_stages = 0
        status = "🟡 md unreachable"
    else:
        _n_stages = int(pipeline["stage"].nunique()) if "stage" in pipeline.columns else 0
        status = "🟡 offline fallback (synthetic pipeline)"

    mo.md(
        f"""
        ## Panel E — engine health

        | field | value |
        |-------|-------|
        | engine | `{engine_label}` |
        | status | {status} |
        | stages | {_n_stages} |
        | pipeline rows | {len(pipeline)} |
        """
    )
    return _n_stages, status


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🎓 This dashboard backs the
        ``oideachais-marimo-dashboards`` spec R-v2-9 (Phase 2 — the
        K-12 → university pipeline matrix). See
        ``openspec/specs/oideachais-marimo-dashboards/spec.md``.
        """
    )
    return


if __name__ == "__main__":
    app.run()