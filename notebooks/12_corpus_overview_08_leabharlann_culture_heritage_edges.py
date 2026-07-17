# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""08 — Leabharlann ↔ culture-heritage edges
(oideachais-marimo-dashboards spec, R-v2-8).

Cross-archive **Cognee edge** view between the **leabharlann**
corpus (216 PDFs × 6 subdirs) and the **culture-heritage** archive
(Dúchas + National Museum + Digital Repository of Ireland + Irish
Traditional Music Archive + Cultural Heritage Agency datasets).
Surfaces the citation graph between personal-archive documents and
authoritative culture-heritage records.

Five visualisations:

- **Panel A** — leabharlann subdir × culture-heritage dataset matrix
- **Panel B** — edge-type distribution (CITES / DERIVED_FROM /
  ILLUSTRATES / TRANSLATES)
- **Panel C** — top-15 strongest cross-archive edges
- **Panel D** — per-language edge parity (EN / GA / BILINGUAL)
- **Panel E** — health banner (engine + row count + status)

Data source: ``md:cianfhoghlaim.culture_heritage.leabharlann_match``
(populated by the cognify cross-archive pass). Falls back to a
synthetic 6-subdir × 5-dataset matrix when the lakehouse is
unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R-v2-8 (Phase 2 — leabharlann ↔ culture-heritage edges).
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
        # 🏺 Leabharlann ↔ culture-heritage edges

        Cross-archive **Cognee edge** view between the **leabharlann**
        corpus (216 PDFs × 6 subdirs) and the **culture-heritage**
        archive (Dúchas + National Museum + Digital Repository of
        Ireland + Irish Traditional Music Archive + Cultural Heritage
        Agency datasets).

        Surfaces the citation graph between personal-archive
        documents and authoritative culture-heritage records.

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
    LEABHARLANN_SUBDIRS: tuple[str, ...] = (
        "ollscoil_na_gaillimhe",
        "gaeilge",
        "mata",
        "aigne",
        "gemini_deep_research",
        "zotero",
    )

    CULTURE_HERITAGE_DATASETS: tuple[str, ...] = (
        "duchas",
        "national_museum",
        "digital_repository_ireland",
        "irish_traditional_music_archive",
        "cultural_heritage_agency",
    )
    """The 5 culture-heritage datasets per the cognify cross-archive pass."""

    EDGE_TYPES: tuple[str, ...] = (
        "CITES",
        "DERIVED_FROM",
        "ILLUSTRATES",
        "TRANSLATES",
    )

    return CULTURE_HERITAGE_DATASETS, EDGE_TYPES, LEABHARLANN_SUBDIRS


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
        "CREATE TABLE IF NOT EXISTS oideachais_culture_heritage_leabharlann_match ("
        "  subdir VARCHAR, dataset VARCHAR, language VARCHAR, edge_type VARCHAR,"
        "  doc_id VARCHAR, record_id VARCHAR, weight DOUBLE"
        ")"
    )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(
    CULTURE_HERITAGE_DATASETS, EDGE_TYPES, LEABHARLANN_SUBDIRS,
    con, engine_label, mo, pd,
):
    """Read leabharlann ↔ culture-heritage edges — live or synthetic."""
    src = engine_label
    edges = pd.DataFrame()

    if engine_label == "md:oideachais":
        try:
            edges = con.execute(
                "SELECT * FROM cianfhoghlaim.culture_heritage.leabharlann_match"
            ).fetchdf()
        except Exception:
            edges = pd.DataFrame()

    if edges.empty:
        # Synthetic 6-subdir × 5-dataset × 4-edge-type cross-archive matrix
        _rows = []
        for _subdir in LEABHARLANN_SUBDIRS:
            for _dataset in CULTURE_HERITAGE_DATASETS:
                for _edge in EDGE_TYPES:
                    _seed = (
                        sum(ord(c) for c in _subdir) * 5
                        + sum(ord(c) for c in _dataset) * 7
                        + sum(ord(c) for c in _edge) * 11
                    ) % 250 + 10
                    # Higher density for IRISH/Gaeilge subdir ↔ Irish datasets
                    if _subdir == "gaeilge" and _dataset in {
                        "duchas", "irish_traditional_music_archive",
                    }:
                        _seed += 100
                    if _seed < 80:
                        continue
                    _lang = "ga" if _subdir == "gaeilge" else (
                        "bilingual" if _dataset == "duchas" else "en"
                    )
                    _rows.append({
                        "subdir": _subdir,
                        "dataset": _dataset,
                        "language": _lang,
                        "edge_type": _edge,
                        "doc_id": f"{_subdir}_{_dataset}_{_edge.lower()}",
                        "record_id": f"{_dataset}-REC-{_seed}",
                        "weight": round(0.4 + (_seed % 50) / 100, 3),
                    })
        edges = pd.DataFrame(_rows)
        src = "synthetic (6×5×4=120 candidate cells; ~25% populated)"

    mo.md(f"**Source**: `{src}` — **{len(edges)}** edges")
    return edges, src


@app.cell
def _viz_subdir_dataset_matrix(alt, mo, edges):
    """Panel A — leabharlann subdir × culture-heritage dataset matrix."""
    pivot = (
        edges.groupby(["subdir", "dataset"], as_index=False)
        .size()
        .rename(columns={"size": "edge_count"})
    )
    chart = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("dataset:N", title="Culture-heritage dataset"),
            y=alt.Y("subdir:N", title="Leabharlann subdir"),
            color=alt.Color(
                "edge_count:Q",
                title="Edges",
                scale=alt.Scale(scheme="viridis"),
            ),
            tooltip=["subdir", "dataset", "edge_count"],
        )
        .properties(
            width=620,
            height=260,
            title="Panel A — leabharlann subdir × culture-heritage matrix",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, pivot


@app.cell
def _viz_edge_type_dist(alt, mo, edges):
    """Panel B — edge-type distribution (bar chart)."""
    by_edge = (
        edges.groupby("edge_type", as_index=False)
        .size()
        .rename(columns={"size": "edge_count"})
    )
    chart = (
        alt.Chart(by_edge)
        .mark_bar()
        .encode(
            x=alt.X("edge_type:N", title="Edge type"),
            y=alt.Y("edge_count:Q", title="Edge count"),
            color=alt.Color(
                "edge_type:N",
                title="Edge type",
                scale=alt.Scale(scheme="set3"),
                legend=None,
            ),
            tooltip=["edge_type", "edge_count"],
        )
        .properties(
            width=420,
            height=280,
            title="Panel B — edge-type distribution",
        )
    )
    mo.ui.altair_chart(chart)
    return by_edge, chart


@app.cell
def _viz_top_edges(alt, mo, edges):
    """Panel C — top-15 strongest cross-archive edges."""
    top = edges.sort_values("weight", ascending=False).head(15)
    chart = (
        alt.Chart(top)
        .mark_bar()
        .encode(
            x=alt.X("weight:Q", title="Edge weight"),
            y=alt.Y(
                "doc_id:N",
                title="Edge (doc ↔ record)",
                sort=top["doc_id"].tolist(),
            ),
            color=alt.Color(
                "dataset:N",
                title="Dataset",
                scale=alt.Scale(scheme="category10"),
            ),
            tooltip=["doc_id", "subdir", "dataset", "weight", "edge_type"],
        )
        .properties(
            width=620,
            height=380,
            title="Panel C — top-15 strongest leabharlann ↔ culture-heritage edges",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, top


@app.cell
def _viz_lang_parity(alt, mo, edges):
    """Panel D — per-language edge parity (stacked)."""
    by_lang = (
        edges.groupby(["language", "edge_type"], as_index=False)
        .size()
        .rename(columns={"size": "edge_count"})
    )
    chart = (
        alt.Chart(by_lang)
        .mark_bar()
        .encode(
            x=alt.X("language:N", title="Language"),
            y=alt.Y("edge_count:Q", title="Edge count", stack=True),
            color=alt.Color("edge_type:N", title="Edge type", scale=alt.Scale(scheme="set3")),
            tooltip=["language", "edge_type", "edge_count"],
        )
        .properties(
            width=420,
            height=300,
            title="Panel D — per-language edge parity (stacked)",
        )
    )
    mo.ui.altair_chart(chart)
    return by_lang, chart


@app.cell
def _health_banner(mo, edges, engine_label):
    if engine_label == "md:oideachais":
        _n = len(edges)
        status = "🟢 live"
    elif engine_label.startswith("local_duckdb (md unreachable"):
        _n = 0
        status = "🟡 md unreachable"
    else:
        _n = len(edges)
        status = "🟡 offline fallback (synthetic edges)"

    mo.md(
        f"""
        ## Panel E — engine health

        | field | value |
        |-------|-------|
        | engine | `{engine_label}` |
        | status | {status} |
        | edges | {_n} |
        | datasets | 5 |
        """
    )
    return _n, status


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🏺 This dashboard backs the
        ``oideachais-marimo-dashboards`` spec R-v2-8 (Phase 2 — the
        leabharlann ↔ culture-heritage cross-archive edges). See
        ``openspec/specs/oideachais-marimo-dashboards/spec.md``.
        """
    )
    return


if __name__ == "__main__":
    app.run()