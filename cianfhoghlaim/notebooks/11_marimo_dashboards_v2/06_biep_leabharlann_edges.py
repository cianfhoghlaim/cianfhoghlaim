# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""06 — BIEP ↔ leabharlann cross-archive edges
(oideachais-marimo-dashboards spec, R-v2-6).

Cross-archive **Cognee edge** view between the BIEP v1 oideachais
lakehouse (6 LC subjects × 3 levels × 2 languages × 9 years) and the
leabharlann corpus (216 PDFs × 6 subdirs). Reads the
``oideachais.leabharlann.lc_join`` cognify edges produced by the
5-stage cognify pass (per ``oideachais-cognify-knowledge-graph``).

Five visualisations:

- **Panel A** — per-subject × subdir join matrix (heatmap)
- **Panel B** — join-edge type distribution (book REFERENCES /
  TEACHES / ASSESSED_BY)
- **Panel C** — top-15 strongest BIEP ↔ leabharlann edges
- **Panel D** — per-language edge parity (EN / GA / BILINGUAL)
- **Panel E** — health banner (engine + row count + status)

Data source: ``md:oideachais.leabharlann.lc_join`` (the canonical
cross-archive join table). Falls back to a synthetic 6×6×3=108
join-edge matrix when the lakehouse is unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R-v2-6 (Phase 2 — BIEP ↔ leabharlann edges).
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
        # 🌉 BIEP ↔ leabharlann cross-archive edges

        Cross-archive **Cognee edge** view between the BIEP v1
        oideachais lakehouse (6 LC subjects × 3 levels × 2 languages
        × 9 years) and the leabharlann corpus (216 PDFs × 6 subdirs).

        Reads the ``oideachais.leabharlann.lc_join`` cognify edges
        produced by the 5-stage cognify pass (per
        ``oideachais-cognify-knowledge-graph``).

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
    from cianfhoghlaim.notebooks.nb_utils import BIEP_LANGUAGES, BIEP_SUBJECTS

    LEABHARLANN_SUBDIRS: tuple[str, ...] = (
        "ollscoil_na_gaillimhe",
        "gaeilge",
        "mata",
        "aigne",
        "gemini_deep_research",
        "zotero",
    )
    EDGE_TYPES: tuple[str, ...] = (
        "REFERENCES",
        "TEACHES",
        "ASSESSED_BY",
    )

    return BIEP_LANGUAGES, BIEP_SUBJECTS, EDGE_TYPES, LEABHARLANN_SUBDIRS


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
        "CREATE TABLE IF NOT EXISTS oideachais_leabharlann_lc_join ("
        "  subject VARCHAR, subdir VARCHAR, language VARCHAR, edge_type VARCHAR,"
        "  doc_id VARCHAR, topic VARCHAR, weight DOUBLE"
        ")"
    )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(
    BIEP_LANGUAGES, BIEP_SUBJECTS, EDGE_TYPES, LEABHARLANN_SUBDIRS,
    con, engine_label, mo, pd,
):
    """Read BIEP ↔ leabharlann edges — live or synthetic fallback."""
    src = engine_label
    edges = pd.DataFrame()

    if engine_label == "md:oideachais":
        try:
            edges = con.execute(
                "SELECT * FROM oideachais.leabharlann.lc_join"
            ).fetchdf()
        except Exception:
            edges = pd.DataFrame()

    if edges.empty:
        _rows = []
        for _subj in BIEP_SUBJECTS:
            for _subdir in LEABHARLANN_SUBDIRS:
                for _edge in EDGE_TYPES:
                    for _lang in BIEP_LANGUAGES:
                        _seed = (
                            sum(ord(c) for c in _subj) * 7
                            + sum(ord(c) for c in _subdir) * 11
                            + sum(ord(c) for c in _edge) * 13
                        ) % 200 + 5
                        if _seed < 20:
                            continue  # sparse — only ~10% of cells are populated
                        _rows.append({
                            "subject": _subj,
                            "subdir": _subdir,
                            "language": _lang,
                            "edge_type": _edge,
                            "doc_id": f"{_subdir}_{_subj}_{_edge.lower()}",
                            "topic": f"{_subj} topic #{_seed}",
                            "weight": round(0.4 + (_seed % 60) / 100, 3),
                        })
        edges = pd.DataFrame(_rows)
        src = "synthetic (6×6×3×2=216 candidate cells; ~10% populated)"

    mo.md(f"**Source**: `{src}` — **{len(edges)}** edges")
    return edges, src


@app.cell
def _viz_subject_subdir_matrix(alt, mo, edges):
    """Panel A — per-subject × subdir join matrix (heatmap)."""
    pivot = (
        edges.groupby(["subject", "subdir"], as_index=False)
        .size()
        .rename(columns={"size": "edge_count"})
    )
    chart = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("subdir:N", title="Leabharlann subdir"),
            y=alt.Y("subject:N", title="LC subject"),
            color=alt.Color(
                "edge_count:Q",
                title="Edges",
                scale=alt.Scale(scheme="viridis"),
            ),
            tooltip=["subject", "subdir", "edge_count"],
        )
        .properties(
            width=620,
            height=260,
            title="Panel A — BIEP subject × leabharlann subdir edge matrix",
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
                scale=alt.Scale(scheme="set2"),
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
    """Panel C — top-15 strongest BIEP ↔ leabharlann edges."""
    top = edges.sort_values("weight", ascending=False).head(15)
    chart = (
        alt.Chart(top)
        .mark_bar()
        .encode(
            x=alt.X("weight:Q", title="Edge weight"),
            y=alt.Y(
                "doc_id:N",
                title="Edge (doc ↔ topic)",
                sort=top["doc_id"].tolist(),
            ),
            color=alt.Color(
                "subject:N",
                title="LC subject",
                scale=alt.Scale(scheme="category10"),
            ),
            tooltip=["doc_id", "subject", "subdir", "weight"],
        )
        .properties(
            width=620,
            height=380,
            title="Panel C — top-15 strongest BIEP ↔ leabharlann edges",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, top


@app.cell
def _viz_lang_parity(alt, mo, edges):
    """Panel D — per-language edge parity (EN / GA / BILINGUAL)."""
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
            color=alt.Color("edge_type:N", title="Edge type", scale=alt.Scale(scheme="set2")),
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
        _n_subj = int(edges["subject"].nunique()) if "subject" in edges.columns else 0
        status = "🟢 live"
    elif engine_label.startswith("local_duckdb (md unreachable"):
        _n_subj = 0
        status = "🟡 md unreachable"
    else:
        _n_subj = int(edges["subject"].nunique()) if "subject" in edges.columns else 0
        status = "🟡 offline fallback (synthetic edges)"

    mo.md(
        f"""
        ## Panel E — engine health

        | field | value |
        |-------|-------|
        | engine | `{engine_label}` |
        | status | {status} |
        | subjects | {_n_subj} |
        | edges | {len(edges)} |
        """
    )
    return _n_subj, status


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🌉 This dashboard backs the
        ``oideachais-marimo-dashboards`` spec R-v2-6 (Phase 2 — the
        BIEP ↔ leabharlann cross-archive edges). See
        ``openspec/specs/oideachais-marimo-dashboards/spec.md``.
        """
    )
    return


if __name__ == "__main__":
    app.run()