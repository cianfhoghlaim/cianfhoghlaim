# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""02 — Leabharlann 6-subdir matrix (oideachais-marimo-dashboards spec, R-v2-2).

Per-document matrix view of the **leabharlann** corpus — every
document's subdir × language × year-quadrant, plus a top-K topic
co-occurrence matrix within each subdir.

Five visualisations:

- **Panel A** — subdir × language heatmap (document counts)
- **Panel B** — subdir × year-quadrant heatmap (2018-2020 / 2021-2023 /
  2024-2026)
- **Panel C** — per-subdir topic co-occurrence top-12 (horizontal
  bar)
- **Panel D** — per-subdir average pages bar chart
- **Panel E** — health banner (engine + row count + status)

Data source: ``md:cianfhoghlaim.leabharlann.documents`` + the topic
co-occurrence table ``md:cianfhoghlaim.leabharlann.topic_pairs``.

Falls back to a synthetic 6-subdir × 3-language × 3-quadrant
co-occurrence matrix (6×3×3=54 cells + 12 top topic pairs) when the
lakehouse is unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R-v2-2 (Phase 2 — leabharlann 6-subdir matrix).
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
        # 🗂️ Leabharlann 6-subdir matrix

        Per-document matrix view of the **leabharlann** corpus — every
        document's subdir × language × year-quadrant, plus a top-K
        topic co-occurrence matrix within each subdir.

        Live data: ``md:cianfhoghlaim.leabharlann.documents`` +
        ``md:cianfhoghlaim.leabharlann.topic_pairs``.

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
    """Leabharlann canonical contracts."""
    LEABHARLANN_SUBDIRS: tuple[str, ...] = (
        "ollscoil_na_gaillimhe",
        "gaeilge",
        "mata",
        "aigne",
        "gemini_deep_research",
        "zotero",
    )
    LEABHARLANN_LANGUAGES: tuple[str, ...] = ("en", "ga", "bilingual")
    YEAR_QUADRANTS: tuple[str, ...] = ("2018-2020", "2021-2023", "2024-2026")

    return LEABHARLANN_LANGUAGES, LEABHARLANN_SUBDIRS, YEAR_QUADRANTS


@app.cell
def _lakehouse_connect(mo, duckdb, os):
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"

    if use_md and token:
        try:
            duckdb.sql(f"SET motherduck_token='{token}'")
            con = duckdb.connect("md:cianfhoghlaim")
            engine_label = "md:cianfhoghlaim"
        except Exception as exc:
            con = duckdb.connect(":memory:")
            engine_label = f"local_duckdb (md unreachable: {type(exc).__name__})"
    else:
        con = duckdb.connect(":memory:")
        engine_label = "local_duckdb (offline fallback)"

    # Minimal schema
    for _tbl in ("documents", "topic_pairs"):
        con.execute(
            f"CREATE TABLE IF NOT EXISTS oideachais_leabharlann_{_tbl} ("
            "  doc_id VARCHAR, subdir VARCHAR, language VARCHAR, year INTEGER,"
            "  topic_a VARCHAR, topic_b VARCHAR, weight DOUBLE, pages INTEGER"
            ")"
        )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(
    con, LEABHARLANN_SUBDIRS, LEABHARLANN_LANGUAGES, YEAR_QUADRANTS, engine_label,
    mo, pd,
):
    """Read corpus + topic pairs — live or synthetic fallback."""
    src = engine_label
    corpus = pd.DataFrame()
    topic_pairs = pd.DataFrame()

    if engine_label == "md:cianfhoghlaim":
        try:
            corpus = con.execute(
                "SELECT * FROM cianfhoghlaim.leabharlann.documents"
            ).fetchdf()
        except Exception:
            corpus = pd.DataFrame()
        try:
            topic_pairs = con.execute(
                "SELECT * FROM cianfhoghlaim.leabharlann.topic_pairs"
            ).fetchdf()
        except Exception:
            topic_pairs = pd.DataFrame()

    if corpus.empty:
        _synth = []
        for _subdir in LEABHARLANN_SUBDIRS:
            for _lang in LEABHARLANN_LANGUAGES:
                for _idx in range(12):
                    _year = 2018 + (_idx % 9)
                    _synth.append({
                        "doc_id": f"{_subdir}_{_lang}_{_idx:03d}",
                        "subdir": _subdir,
                        "language": _lang,
                        "year": _year,
                        "pages": 60 + (sum(ord(c) for c in _subdir) + _idx) % 220,
                    })
        corpus = pd.DataFrame(_synth)

    if topic_pairs.empty:
        # Top 12 topic co-occurrences — deterministic
        _topic_pairs = []
        _topic_seeds = [
            ("calculus", "algebra"),
            ("mechanics", "waves"),
            ("organic", "thermo"),
            ("litriú", "gramadach"),
            ("eolaíocht", "stair"),
            ("algorithms", "data-structures"),
            ("poetry", "prose"),
            ("fiction", "drama"),
            ("biography", "history"),
            ("neural-networks", "deep-learning"),
            ("research-methods", "writing"),
            ("geometry", "trigonometry"),
        ]
        for _idx, (_ta, _tb) in enumerate(_topic_seeds):
            _subdir = LEABHARLANN_SUBDIRS[_idx % len(LEABHARLANN_SUBDIRS)]
            _weight = round(0.85 - _idx * 0.04, 2)
            _topic_pairs.append({
                "topic_a": _ta,
                "topic_b": _tb,
                "subdir": _subdir,
                "weight": _weight,
            })
        topic_pairs = pd.DataFrame(_topic_pairs)

    # Year-quadrant column (helper)
    def _quadrant(year: int) -> str:
        if year <= 2020:
            return YEAR_QUADRANTS[0]
        if year <= 2023:
            return YEAR_QUADRANTS[1]
        return YEAR_QUADRANTS[2]

    corpus["year_quadrant"] = corpus["year"].apply(_quadrant)

    src = src if not corpus.empty else "synthetic"
    mo.md(f"**Source**: `{src}` — **{len(corpus)}** documents, **{len(topic_pairs)}** topic pairs")
    return corpus, src, topic_pairs


@app.cell
def _viz_subdir_lang_matrix(alt, mo, corpus):
    """Panel A — subdir × language heatmap."""
    pivot = (
        corpus.groupby(["subdir", "language"], as_index=False)
        .size()
        .rename(columns={"size": "doc_count"})
    )
    chart = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("subdir:N", title="Subdirectory"),
            y=alt.Y("language:N", title="Language"),
            color=alt.Color("doc_count:Q", title="Docs", scale=alt.Scale(scheme="viridis")),
            tooltip=["subdir", "language", "doc_count"],
        )
        .properties(
            width=560,
            height=200,
            title="Panel A — subdir × language document count",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, pivot


@app.cell
def _viz_subdir_quadrant_matrix(alt, mo, corpus):
    """Panel B — subdir × year-quadrant heatmap."""
    pivot = (
        corpus.groupby(["subdir", "year_quadrant"], as_index=False)
        .size()
        .rename(columns={"size": "doc_count"})
    )
    chart = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("year_quadrant:N", title="Year quadrant"),
            y=alt.Y("subdir:N", title="Subdirectory"),
            color=alt.Color("doc_count:Q", title="Docs", scale=alt.Scale(scheme="tealblues")),
            tooltip=["subdir", "year_quadrant", "doc_count"],
        )
        .properties(
            width=480,
            height=260,
            title="Panel B — subdir × year-quadrant matrix",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, pivot


@app.cell
def _viz_top_topic_pairs(alt, mo, topic_pairs):
    """Panel C — top-12 topic co-occurrence pairs."""
    top_pairs = topic_pairs.sort_values("weight", ascending=False).head(12)
    chart = (
        alt.Chart(top_pairs)
        .mark_bar()
        .encode(
            x=alt.X("weight:Q", title="Weight (cosine similarity)"),
            y=alt.Y(
                "topic_a:N",
                title="Topic A",
                sort=top_pairs["topic_a"].tolist(),
            ),
            color=alt.Color(
                "subdir:N",
                title="Subdirectory",
                scale=alt.Scale(scheme="category10"),
            ),
            tooltip=["topic_a", "topic_b", "weight", "subdir"],
        )
        .properties(
            width=620,
            height=320,
            title="Panel C — top-12 topic co-occurrence pairs",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, top_pairs


@app.cell
def _viz_avg_pages(alt, mo, corpus):
    """Panel D — per-subdir average pages (horizontal bar)."""
    avg_pages = (
        corpus.groupby("subdir", as_index=False)["pages"]
        .mean()
        .round(1)
        .sort_values("pages", ascending=True)
    )
    chart = (
        alt.Chart(avg_pages)
        .mark_bar()
        .encode(
            x=alt.X("pages:Q", title="Average pages"),
            y=alt.Y("subdir:N", title="Subdirectory", sort=avg_pages["subdir"].tolist()),
            color=alt.Color("pages:Q", scale=alt.Scale(scheme="oranges"), legend=None),
            tooltip=["subdir", "pages"],
        )
        .properties(
            width=620,
            height=240,
            title="Panel D — average pages per subdir",
        )
    )
    mo.ui.altair_chart(chart)
    return avg_pages, chart


@app.cell
def _health_banner(mo, engine_label, corpus):
    if engine_label == "md:cianfhoghlaim":
        _n_subdir = int(corpus["subdir"].nunique()) if "subdir" in corpus.columns else 0
        status = "🟢 live"
    elif engine_label.startswith("local_duckdb (md unreachable"):
        status = "🟡 md unreachable"
    else:
        status = "🟡 offline fallback (synthetic corpus)"
        _n_subdir = 6

    mo.md(
        f"""
        ## Panel E — engine health

        | field | value |
        |-------|-------|
        | engine | `{engine_label}` |
        | status | {status} |
        | subdirs | {_n_subdir} |
        | docs | {len(corpus)} |
        """
    )
    return (status,)


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🗂️ This dashboard backs the
        ``oideachais-marimo-dashboards`` spec R-v2-2 (Phase 2 — the
        leabharlann 6-subdir matrix). See
        ``openspec/specs/oideachais-marimo-dashboards/spec.md``.
        """
    )
    return


if __name__ == "__main__":
    app.run()