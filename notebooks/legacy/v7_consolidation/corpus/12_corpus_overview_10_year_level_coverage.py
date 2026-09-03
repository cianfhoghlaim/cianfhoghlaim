# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""10 — Year-level coverage (oideachais-marimo-dashboards spec, R-v2-10).

Per-year-level coverage view of the **K-12 → tertiary** pipeline. Shows
how the 9-year window (2017-2026) intersects with the 5 stages, the 3
LC levels, and the 13 HEIs.

Five visualisations:

- **Panel A** — stage × year coverage heatmap (5 stages × 9 years)
- **Panel B** — per-year topic volume (stacked by stage, area chart)
- **Panel C** — per-year HEI pipeline distribution (stacked bar)
- **Panel D** — per-year bilingual coverage (line chart, EN vs GA)
- **Panel E** — health banner (engine + row count + status)

Data source: ``md:cianfhoghlaim.education.stage_topics`` + the
``md:cianfhoghlaim.hei.institutions`` table (joined via stage_id +
academic_year). Falls back to a synthetic 5×9 stage × year matrix +
5×9 stage × HEI matrix when the lakehouse is unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R-v2-10 (Phase 2 — K-12 → university year-level coverage).
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
        # 📅 Year-level coverage

        Per-year-level coverage view of the **K-12 → tertiary**
        pipeline. Shows how the 9-year window (2017-2026) intersects
        with the 5 stages, the 3 LC levels, and the 13 HEIs.

        Live data: ``md:cianfhoghlaim.education.stage_topics`` +
        ``md:cianfhoghlaim.hei.institutions`` (joined via stage_id +
        academic_year).

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
    EDUCATION_STAGES: tuple[str, ...] = (
        "aistear",
        "primary",
        "junior_cycle",
        "senior_cycle",
        "tertiary",
    )
    """The 5 educational stages — Aistear, Primary, Junior Cycle,
    Senior Cycle, Tertiary."""

    YEAR_WINDOW: tuple[int, ...] = (2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026)
    """The 10-year BIEP window (2017-2026)."""

    HEI_CODES: tuple[str, ...] = (
        "UCD", "UCG", "UCC", "UL", "MU", "TCD", "DCU",
        "ATU", "TUS", "SETU", "MTU", "MIC", "RCSI",
    )

    BIEP_LANGUAGES: tuple[str, ...] = ("en", "ga")
    """Bilingual EN + GA per the LC contract."""

    return BIEP_LANGUAGES, EDUCATION_STAGES, HEI_CODES, YEAR_WINDOW


@app.cell
def _lakehouse_connect(mo, duckdb, os):
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

    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_education_year_coverage ("
        "  stage VARCHAR, year INTEGER, language VARCHAR, n_topics BIGINT,"
        "  hei_code VARCHAR"
        ")"
    )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(
    BIEP_LANGUAGES, EDUCATION_STAGES, HEI_CODES, YEAR_WINDOW,
    con, engine_label, mo, pd,
):
    """Read year-level coverage — live or synthetic fallback."""
    src = engine_label
    coverage = pd.DataFrame()

    if engine_label == "md:cianfhoghlaim":
        try:
            coverage = con.execute(
                "SELECT * FROM cianfhoghlaim.education.year_coverage"
            ).fetchdf()
        except Exception:
            coverage = pd.DataFrame()

    if coverage.empty:
        # Synthetic 5-stage × 10-year coverage
        _rows = []
        for _stage_idx, _stage in enumerate(EDUCATION_STAGES):
            for _year in YEAR_WINDOW:
                for _lang in BIEP_LANGUAGES:
                    _seed = (
                        sum(ord(c) for c in _stage) * 13
                        + (_year - 2017) * 23
                        + sum(ord(c) for c in _lang) * 29
                    ) % 500 + 50
                    _rows.append({
                        "stage": _stage,
                        "year": _year,
                        "language": _lang,
                        "n_topics": _seed,
                        "hei_code": HEI_CODES[_year % len(HEI_CODES)] if _stage == "tertiary" else "",
                    })
        coverage = pd.DataFrame(_rows)
        src = "synthetic (5×10×2=100 stage-year-lang cells + tertiary → HEI)"

    mo.md(f"**Source**: `{src}` — **{len(coverage)}** rows")
    return coverage, src


@app.cell
def _viz_stage_year_matrix(alt, mo, coverage):
    """Panel A — stage × year coverage heatmap."""
    pivot = (
        coverage.groupby(["stage", "year"], as_index=False)["n_topics"]
        .sum()
    )
    chart = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("stage:N", title="Stage", sort=("-y",)),
            color=alt.Color(
                "n_topics:Q",
                title="Topics",
                scale=alt.Scale(scheme="viridis"),
            ),
            tooltip=["stage", "year", "n_topics"],
        )
        .properties(
            width=620,
            height=240,
            title="Panel A — stage × year coverage heatmap",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, pivot


@app.cell
def _viz_year_volume(alt, mo, coverage):
    """Panel B — per-year topic volume (stacked by stage)."""
    per_year = (
        coverage.groupby(["year", "stage"], as_index=False)["n_topics"]
        .sum()
    )
    chart = (
        alt.Chart(per_year)
        .mark_area(opacity=0.7)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("n_topics:Q", title="Topics", stack=True),
            color=alt.Color(
                "stage:N",
                title="Stage",
                scale=alt.Scale(scheme="tableau20"),
            ),
            tooltip=["year", "stage", "n_topics"],
        )
        .properties(
            width=620,
            height=300,
            title="Panel B — per-year topic volume (stacked by stage)",
        )
        .interactive()
    )
    mo.ui.altair_chart(chart)
    return chart, per_year


@app.cell
def _viz_year_hei(alt, mo, coverage):
    """Panel C — per-year HEI pipeline distribution (stacked bar)."""
    tertiary = coverage[coverage["stage"] == "tertiary"]
    if not tertiary.empty:
        per_year_hei = (
            tertiary.groupby(["year", "hei_code"], as_index=False)["n_topics"]
            .sum()
        )
    else:
        per_year_hei = coverage.head(0).rename(columns={"n_topics": "n_topics"})

    if per_year_hei.empty:
        # Synthesise a minimal tertiary-year × HEI view
        per_year_hei = (
            coverage[coverage["stage"] == "tertiary"]
            .groupby(["year", "hei_code"], as_index=False)["n_topics"]
            .sum()
        )

    chart = (
        alt.Chart(per_year_hei)
        .mark_bar()
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("n_topics:Q", title="Tertiary topics", stack=True),
            color=alt.Color(
                "hei_code:N",
                title="HEI",
                scale=alt.Scale(scheme="category20"),
            ),
            tooltip=["year", "hei_code", "n_topics"],
        )
        .properties(
            width=620,
            height=300,
            title="Panel C — per-year tertiary HEI pipeline distribution",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, per_year_hei


@app.cell
def _viz_bilingual(alt, mo, coverage):
    """Panel D — per-year bilingual coverage (line chart)."""
    per_year_lang = (
        coverage.groupby(["year", "language"], as_index=False)["n_topics"]
        .sum()
    )
    chart = (
        alt.Chart(per_year_lang)
        .mark_line(point=True, strokeWidth=2.5)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("n_topics:Q", title="Topics"),
            color=alt.Color("language:N", title="Language", scale=alt.Scale(scheme="set1")),
            tooltip=["year", "language", "n_topics"],
        )
        .properties(
            width=620,
            height=280,
            title="Panel D — per-year bilingual coverage (EN vs GA)",
        )
        .interactive()
    )
    mo.ui.altair_chart(chart)
    return chart, per_year_lang


@app.cell
def _health_banner(mo, coverage, engine_label):
    if engine_label == "md:cianfhoghlaim":
        _n_year = int(coverage["year"].nunique()) if "year" in coverage.columns else 0
        status = "🟢 live"
    elif engine_label.startswith("local_duckdb (md unreachable"):
        _n_year = 0
        status = "🟡 md unreachable"
    else:
        _n_year = int(coverage["year"].nunique()) if "year" in coverage.columns else 0
        status = "🟡 offline fallback (synthetic coverage)"

    mo.md(
        f"""
        ## Panel E — engine health

        | field | value |
        |-------|-------|
        | engine | `{engine_label}` |
        | status | {status} |
        | years | {_n_year} |
        | coverage rows | {len(coverage)} |
        """
    )
    return _n_year, status


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        📅 This dashboard backs the
        ``oideachais-marimo-dashboards`` spec R-v2-10 (Phase 2 — the
        K-12 → university year-level coverage). See
        ``openspec/specs/oideachais-marimo-dashboards/spec.md``.
        """
    )
    return


if __name__ == "__main__":
    app.run()