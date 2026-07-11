# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""05 — QQI NFQ ladder (oideachais-marimo-dashboards spec, R-v2-5).

Coverage view of the **QQI FET award → CAO course ladder** plus the
NFQ level distribution across the 13 HEIs. Shows how the 8+ QQI FET
awards (Software Development, Computer Science, Laboratory
Techniques, Nursing Studies, General Nursing, Business Studies,
Social Care, Early Childhood Care, etc.) ladder into the 13
institutions.

Five visualisations:

- **Panel A** — QQI award × HEI ladder matrix (heatmap)
- **Panel B** — NFQ level distribution (bar chart)
- **Panel C** — per-NFQ-level ladder density (stacked bar)
- **Panel D** — per-HEI ladder coverage (stacked by QQI award)
- **Panel E** — health banner (engine + row count + status)

Data source: ``md:oideachais.hei.qqi_awards`` (populated from the
``qqi_awards`` array in ``hei.json``). Falls back to a synthetic
8-QQI × 13-HEI ladder matrix when the lakehouse is unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R-v2-5 (Phase 2 — QQI coverage dashboard).
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
        # 🪜 QQI NFQ ladder

        Coverage view of the **QQI FET award → CAO course ladder**
        plus the NFQ level distribution across the 13 HEIs. Shows how
        the 8+ QQI FET awards (Software Development, Computer Science,
        Laboratory Techniques, Nursing Studies, General Nursing,
        Business Studies, Social Care, Early Childhood Care, etc.)
        ladder into the 13 institutions.

        Live data: ``md:oideachais.hei.qqi_awards`` + the
        ``qi_qqi_ladder`` Cognee edges.

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
    """The 8+ canonical QQI FET awards (per ``hei.json``)."""
    QQI_AWARDS: tuple[dict[str, object], ...] = (
        {"code": "5M2787", "title_en": "Software Development",
         "nfq_level": 5, "links": ("DT228", "TU857", "CK401")},
        {"code": "5M5028", "title_en": "Computer Science",
         "nfq_level": 5, "links": ("TU857", "WD165", "GY301")},
        {"code": "5M2061", "title_en": "Laboratory Techniques",
         "nfq_level": 5, "links": ("DT219", "CR330")},
        {"code": "5M18396", "title_en": "Nursing Studies (Pre-Nursing)",
         "nfq_level": 5, "links": ("GY515", "TR091", "CK710")},
        {"code": "5M3782", "title_en": "General Nursing",
         "nfq_level": 5, "links": ("GY515", "TR091", "CK710", "DC215")},
        {"code": "5M2102", "title_en": "Business Studies",
         "nfq_level": 5, "links": ("CK201", "GY201", "TU791", "WD137")},
        {"code": "5M0820", "title_en": "Social Care",
         "nfq_level": 5, "links": ("TU794", "GY2118", "WD191")},
        {"code": "5M2094", "title_en": "Early Childhood Care & Education",
         "nfq_level": 5, "links": ("DT591", "GY114", "CK114")},
    )

    NFQ_LEVELS: tuple[int, ...] = (5, 6, 7, 8, 9, 10)
    """The 6 NFQ levels (5-10) covered by the BIEP ladder."""

    HEI_CODES: tuple[str, ...] = (
        "UCD", "UCG", "UCC", "UL", "MU", "TCD", "DCU",
        "ATU", "TUS", "SETU", "MTU", "MIC", "RCSI",
    )

    return HEI_CODES, NFQ_LEVELS, QQI_AWARDS


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
        "CREATE TABLE IF NOT EXISTS oideachais_hei_qqi_awards ("
        "  award_code VARCHAR, title_en VARCHAR, nfq_level INTEGER,"
        "  hei_code VARCHAR, course_code VARCHAR"
        ")"
    )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(HEI_CODES, QQI_AWARDS, con, engine_label, mo, pd):
    """Read the QQI ladder edges — live or synthetic fallback."""
    src = engine_label
    ladder = pd.DataFrame()

    if engine_label == "md:oideachais":
        try:
            ladder = con.execute(
                "SELECT * FROM oideachais.hei.qqi_awards"
            ).fetchdf()
        except Exception:
            ladder = pd.DataFrame()

    if ladder.empty:
        # Synthetic QQI ladder — 8 awards × 13 HEIs (with coverage
        # depending on the award's ``links`` tuple)
        _rows = []
        for _award in QQI_AWARDS:
            for _hei in HEI_CODES:
                # NFQ_5 awards ladder into all HEIs with NFQ >= 6
                # (synthetic — NUI/QQI rules)
                if _hei in {"RCSI"}:
                    continue  # specialist medical, no QQI ladder
                _rows.append({
                    "award_code": _award["code"],
                    "title_en": _award["title_en"],
                    "nfq_level": _award["nfq_level"],
                    "hei_code": _hei,
                    "course_code": f"{_hei}-QQI-{_award['code']}",
                })
        ladder = pd.DataFrame(_rows)
        src = "synthetic (8 QQI awards × 13 HEIs = ~96 ladder edges)"

    mo.md(f"**Source**: `{src}` — **{len(ladder)}** ladder edges")
    return ladder, src


@app.cell
def _viz_award_hei_matrix(alt, mo, ladder):
    """Panel A — QQI award × HEI ladder matrix (heatmap)."""
    pivot = (
        ladder.groupby(["award_code", "hei_code"], as_index=False)
        .size()
        .rename(columns={"size": "course_count"})
    )
    chart = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("hei_code:N", title="HEI"),
            y=alt.Y("award_code:N", title="QQI award"),
            color=alt.Color(
                "course_count:Q",
                title="Courses",
                scale=alt.Scale(scheme="viridis"),
            ),
            tooltip=["award_code", "hei_code", "course_count"],
        )
        .properties(
            width=620,
            height=320,
            title="Panel A — QQI award × HEI ladder matrix",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, pivot


@app.cell
def _viz_nfq_distribution(alt, mo, ladder):
    """Panel B — NFQ level distribution (bar chart)."""
    by_nfq = (
        ladder.groupby("nfq_level", as_index=False)
        .size()
        .rename(columns={"size": "course_count"})
    )
    chart = (
        alt.Chart(by_nfq)
        .mark_bar()
        .encode(
            x=alt.X("nfq_level:O", title="NFQ level"),
            y=alt.Y("course_count:Q", title="Course count"),
            color=alt.Color("course_count:Q", scale=alt.Scale(scheme="tealblues"), legend=None),
            tooltip=["nfq_level", "course_count"],
        )
        .properties(
            width=420,
            height=280,
            title="Panel B — NFQ level distribution",
        )
    )
    mo.ui.altair_chart(chart)
    return by_nfq, chart


@app.cell
def _viz_ladder_density(alt, mo, ladder):
    """Panel C — per-NFQ-level ladder density (stacked bar)."""
    by_nfq_award = (
        ladder.groupby(["nfq_level", "title_en"], as_index=False)
        .size()
        .rename(columns={"size": "course_count"})
    )
    chart = (
        alt.Chart(by_nfq_award)
        .mark_bar()
        .encode(
            x=alt.X("nfq_level:O", title="NFQ level"),
            y=alt.Y("course_count:Q", title="Courses", stack=True),
            color=alt.Color("title_en:N", title="QQI award", scale=alt.Scale(scheme="tableau20")),
            tooltip=["nfq_level", "title_en", "course_count"],
        )
        .properties(
            width=520,
            height=300,
            title="Panel C — ladder density by NFQ level",
        )
    )
    mo.ui.altair_chart(chart)
    return by_nfq_award, chart


@app.cell
def _viz_hei_ladder(alt, mo, ladder):
    """Panel D — per-HEI ladder coverage (stacked by QQI award)."""
    by_hei = (
        ladder.groupby(["hei_code", "title_en"], as_index=False)
        .size()
        .rename(columns={"size": "course_count"})
    )
    chart = (
        alt.Chart(by_hei)
        .mark_bar()
        .encode(
            x=alt.X("hei_code:N", title="HEI"),
            y=alt.Y("course_count:Q", title="Courses", stack=True),
            color=alt.Color("title_en:N", title="QQI award", scale=alt.Scale(scheme="tableau20")),
            tooltip=["hei_code", "title_en", "course_count"],
        )
        .properties(
            width=620,
            height=300,
            title="Panel D — per-HEI ladder coverage by QQI award",
        )
    )
    mo.ui.altair_chart(chart)
    return by_hei, chart


@app.cell
def _health_banner(mo, engine_label, ladder):
    if engine_label == "md:oideachais":
        _n = len(ladder)
        status = "🟢 live"
    elif engine_label.startswith("local_duckdb (md unreachable"):
        _n = 0
        status = "🟡 md unreachable"
    else:
        _n = len(ladder)
        status = "🟡 offline fallback (synthetic QQI ladder)"

    mo.md(
        f"""
        ## Panel E — engine health

        | field | value |
        |-------|-------|
        | engine | `{engine_label}` |
        | status | {status} |
        | ladder edges | {_n} |
        | source | ``hei.json#qqi_awards`` |
        """
    )
    return _n, status


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🪜 This dashboard backs the
        ``oideachais-marimo-dashboards`` spec R-v2-5 (Phase 2 — the
        QQI NFQ ladder). See
        ``openspec/specs/oideachais-marimo-dashboards/spec.md``.
        """
    )
    return


if __name__ == "__main__":
    app.run()