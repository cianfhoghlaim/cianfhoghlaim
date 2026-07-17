# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""01 — Leabharlann corpus overview (oideachais-marimo-dashboards spec, R-v2-1).

Bird's-eye view of the **leabharlann** corpus — the 216 personal-archive
PDFs spread across the 6 subdirectories (``ollscoil_na_gaillimhe/``,
``gaeilge/``, ``mata/``, ``aigne/``, ``gemini_deep_research/``,
``zotero/``).

Five visualisations:

- **Panel A** — per-subdir document count (horizontal bar of the
  6 subdirectories)
- **Panel B** — per-language distribution (EN / GA / BILINGUAL pie)
- **Panel C** — file-size distribution per subdir (violin)
- **Panel D** — per-year upload trend (line)
- **Panel E** — health banner (engine + row count + status)

Data source: ``md:cianfhoghlaim.leabharlann.documents`` (the canonical
corpus table populated by the ``leabharlann_extract`` DLT source).
Falls back to a synthetic 6-subdir × 36-doc corpus when the lakehouse
is unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R-v2-1 (Phase 2 — leabharlann corpus dashboards).
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
        # 📚 Leabharlann corpus overview

        Bird's-eye view of the **leabharlann** corpus — the 216
        personal-archive PDFs spread across the 6 subdirectories
        (``ollscoil_na_gaillimhe/``, ``gaeilge/``, ``mata/``,
        ``aigne/``, ``gemini_deep_research/``, ``zotero/``).

        Live data: ``md:cianfhoghlaim.leabharlann.documents``. Falls back
        to a 6×36 synthetic corpus when the lakehouse is unreachable.

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
    """The 6 leabharlann subdirectories — canonical corpus layout."""
    LEABHARLANN_SUBDIRS: tuple[str, ...] = (
        "ollscoil_na_gaillimhe",
        "gaeilge",
        "mata",
        "aigne",
        "gemini_deep_research",
        "zotero",
    )
    """The 6 canonical leabharlann subdirs (per the
    ``leabharlann-full-stack-demo`` spec)."""

    LEABHARLANN_LANGUAGES: tuple[str, ...] = ("en", "ga", "bilingual")
    """Per-document language (the corpus is bilingual EN + GA)."""

    return LEABHARLANN_LANGUAGES, LEABHARLANN_SUBDIRS


@app.cell
def _lakehouse_connect(mo, duckdb, os):
    """Connect to the lakehouse with graceful fallback."""
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

    # Best-effort minimal schema
    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_leabharlann_documents ("
        "  doc_id VARCHAR, subdir VARCHAR, language VARCHAR, year INTEGER,"
        "  pages INTEGER, size_kb INTEGER, title VARCHAR"
        ")"
    )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(con, LEABHARLANN_SUBDIRS, engine_label, mo, pd):
    """Read the leabharlann corpus rows — live or synthetic fallback."""
    src = engine_label
    corpus = pd.DataFrame()

    if engine_label == "md:oideachais":
        try:
            corpus = con.execute(
                "SELECT * FROM cianfhoghlaim.leabharlann.documents"
            ).fetchdf()
        except Exception:
            corpus = pd.DataFrame()

    if corpus.empty:
        # Synthetic 6-subdir × 36-doc corpus
        _synth = []
        for _subdir in LEABHARLANN_SUBDIRS:
            for _idx in range(36):
                _seed = (
                    sum(ord(c) for c in _subdir) * 17 + _idx * 31
                ) % 1500 + 100
                _year = 2018 + (_idx % 9)
                _lang = ("en", "ga", "bilingual")[
                    (_idx + sum(ord(c) for c in _subdir)) % 3
                ]
                _synth.append({
                    "doc_id": f"{_subdir}_{_idx:03d}",
                    "subdir": _subdir,
                    "language": _lang,
                    "year": _year,
                    "pages": 50 + (_seed % 250),
                    "size_kb": 500 + (_seed % 5000),
                    "title": f"{_subdir} doc #{_idx}",
                })
        corpus = pd.DataFrame(_synth)
        src = "synthetic (6×36=216 docs; leabharlann canonical corpus)"

    mo.md(f"**Corpus source**: `{src}` — **{len(corpus)}** documents")
    return corpus, src


@app.cell
def _viz_subdir_counts(alt, mo, corpus):
    """Panel A — per-subdir document count (horizontal bar)."""
    per_subdir = (
        corpus.groupby("subdir", as_index=False)
        .size()
        .rename(columns={"size": "doc_count"})
        .sort_values("doc_count", ascending=True)
    )
    chart = (
        alt.Chart(per_subdir)
        .mark_bar()
        .encode(
            x=alt.X("doc_count:Q", title="Documents"),
            y=alt.Y("subdir:N", title="Subdirectory", sort=per_subdir["subdir"].tolist()),
            color=alt.Color("doc_count:Q", scale=alt.Scale(scheme="viridis"), legend=None),
            tooltip=["subdir", "doc_count"],
        )
        .properties(
            width=620,
            height=260,
            title="Panel A — document count per leabharlann subdir",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, per_subdir


@app.cell
def _viz_language_pie(alt, mo, corpus):
    """Panel B — per-language distribution (EN / GA / BILINGUAL)."""
    by_lang = (
        corpus.groupby("language", as_index=False)
        .size()
        .rename(columns={"size": "doc_count"})
    )
    chart = (
        alt.Chart(by_lang)
        .mark_arc(innerRadius=80)
        .encode(
            theta=alt.Theta("doc_count:Q"),
            color=alt.Color("language:N", title="Language"),
            tooltip=["language", "doc_count"],
        )
        .properties(
            width=400,
            height=300,
            title="Panel B — language distribution (EN / GA / BILINGUAL)",
        )
    )
    mo.ui.altair_chart(chart)
    return by_lang, chart


@app.cell
def _viz_size_violin(alt, mo, corpus):
    """Panel C — file-size distribution per subdir (box plot)."""
    chart = (
        alt.Chart(corpus)
        .mark_boxplot(extent="min-max")
        .encode(
            x=alt.X("size_kb:Q", title="File size (KB)"),
            y=alt.Y("subdir:N", title="Subdirectory"),
            color=alt.Color("subdir:N", legend=None),
        )
        .properties(
            width=620,
            height=260,
            title="Panel C — file-size distribution per subdir",
        )
    )
    mo.ui.altair_chart(chart)
    return (chart,)


@app.cell
def _viz_year_trend(alt, mo, corpus):
    """Panel D — per-year upload trend (line)."""
    per_year = (
        corpus.groupby("year", as_index=False)
        .size()
        .rename(columns={"size": "doc_count"})
    )
    chart = (
        alt.Chart(per_year)
        .mark_line(point=True, strokeWidth=2.5)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("doc_count:Q", title="Documents (count)"),
            tooltip=["year", "doc_count"],
        )
        .properties(
            width=620,
            height=240,
            title="Panel D — documents per year (2018..2026)",
        )
        .interactive()
    )
    mo.ui.altair_chart(chart)
    return chart, per_year


@app.cell
def _health_banner(mo, engine_label, corpus):
    """Panel E — engine + row count + status banner."""
    if engine_label == "md:oideachais":
        _n_subdir = (
            int(corpus["subdir"].nunique())
            if "subdir" in corpus.columns else 0
        )
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
        | total docs | {len(corpus)} |
        """
    )
    return (status,)


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        📚 This dashboard backs the
        ``oideachais-marimo-dashboards`` spec R-v2-1 (Phase 2 — the
        leabharlann corpus overview). See
        ``openspec/specs/oideachais-marimo-dashboards/spec.md``.
        """
    )
    return


if __name__ == "__main__":
    app.run()