# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""03 — BGE-M3 embedding coverage (oideachais-marimo-dashboards spec, R-v2-3).

Coverage view of the **BAAI/bge-m3** 1024-d embedder across the
leabharlann corpus. The BGE-M3 model is the canonical multi-vector /
dense / sparse embedder wired into the leabharlann CocoIndex pipeline
(per the ``oideachais-cocoindex-v1-migration`` spec).

Five visualisations:

- **Panel A** — per-subdir embedder coverage (bar chart of docs with
  embeddings vs without)
- **Panel B** — embedding density (1024-d dense vs multi-vector vs
  sparse stack)
- **Panel C** — cosine-similarity distribution histogram
- **Panel D** — per-language embedding parity (EN vs GA bar)
- **Panel E** — health banner (engine + row count + status)

Data source: ``md:cianfhoghlaim.leabharlann.embeddings`` (populated by
the CocoIndex BGE-M3 pass). Falls back to a synthetic 6×36 coverage
matrix + 200 cosine-similarity samples when the lakehouse is
unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R-v2-3 (Phase 2 — BGE-M3 embedding coverage).
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
        # 🧬 BGE-M3 embedding coverage

        Coverage view of the **BAAI/bge-m3** 1024-d embedder across
        the leabharlann corpus. The BGE-M3 model is the canonical
        multi-vector / dense / sparse embedder wired into the
        leabharlann CocoIndex pipeline (per the
        ``oideachais-cocoindex-v1-migration`` spec).

        Live data: ``md:cianfhoghlaim.leabharlann.embeddings``.

        ---
        """
    )
    return (mo,)


@app.cell
def _imports():
    import os

    import altair as alt
    import duckdb
    import numpy as np
    import pandas as pd

    return alt, duckdb, np, os, pd


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
    EMBED_MODES: tuple[str, ...] = ("dense", "sparse", "multi_vector")
    EMBED_DIM: int = 1024

    return EMBED_DIM, EMBED_MODES, LEABHARLANN_SUBDIRS


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
        "CREATE TABLE IF NOT EXISTS oideachais_leabharlann_embeddings ("
        "  doc_id VARCHAR, subdir VARCHAR, language VARCHAR, mode VARCHAR,"
        "  dim INTEGER, has_embedding BOOLEAN"
        ")"
    )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(
    con, EMBED_DIM, EMBED_MODES, LEABHARLANN_SUBDIRS, engine_label, mo, np, pd,
):
    """Read BGE-M3 coverage rows — live or synthetic fallback."""
    src = engine_label
    coverage = pd.DataFrame()

    if engine_label == "md:cianfhoghlaim":
        try:
            coverage = con.execute(
                "SELECT * FROM cianfhoghlaim.leabharlann.embeddings"
            ).fetchdf()
        except Exception:
            coverage = pd.DataFrame()

    if coverage.empty:
        # Synthetic 6-subdir × 36-doc × 3-mode coverage matrix
        _synth = []
        for _subdir in LEABHARLANN_SUBDIRS:
            for _idx in range(36):
                _lang = ("en", "ga", "bilingual")[
                    (_idx + sum(ord(c) for c in _subdir)) % 3
                ]
                for _mode in EMBED_MODES:
                    _has = (_mode != "sparse") or (
                        _idx % 2 == 0  # sparse has 50% coverage
                    )
                    _synth.append({
                        "doc_id": f"{_subdir}_{_idx:03d}",
                        "subdir": _subdir,
                        "language": _lang,
                        "mode": _mode,
                        "dim": EMBED_DIM,
                        "has_embedding": _has,
                    })
        coverage = pd.DataFrame(_synth)
        src = "synthetic (6×36×3=648 embedder coverage rows)"

    # Cosine similarity samples (synthetic)
    _rng = np.random.default_rng(42)
    sims = pd.DataFrame({
        "similarity": _rng.normal(loc=0.62, scale=0.18, size=400).clip(0, 1),
        "mode": ["dense"] * 200 + ["multi_vector"] * 200,
    })

    mo.md(f"**Source**: `{src}` — **{len(coverage)}** coverage rows")
    return coverage, sims, src


@app.cell
def _viz_subdir_coverage(alt, mo, coverage):
    """Panel A — per-subdir embedder coverage (stacked bar)."""
    per_subdir = (
        coverage.groupby(["subdir", "has_embedding"], as_index=False)
        .size()
        .rename(columns={"size": "doc_count"})
    )
    per_subdir["has_embedding"] = per_subdir["has_embedding"].map(
        {True: "embedded", False: "missing"}
    )
    chart = (
        alt.Chart(per_subdir)
        .mark_bar()
        .encode(
            x=alt.X("subdir:N", title="Subdirectory"),
            y=alt.Y("doc_count:Q", title="Documents", stack=True),
            color=alt.Color(
                "has_embedding:N",
                title="Coverage",
                scale=alt.Scale(
                    domain=["embedded", "missing"],
                    range=["#2ca02c", "#d62728"],
                ),
            ),
            tooltip=["subdir", "has_embedding", "doc_count"],
        )
        .properties(
            width=620,
            height=260,
            title="Panel A — BGE-M3 coverage per leabharlann subdir",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, per_subdir


@app.cell
def _viz_mode_density(alt, mo, coverage):
    """Panel B — embedding density by mode."""
    per_mode = (
        coverage.groupby("mode", as_index=False)
        .size()
        .rename(columns={"size": "doc_count"})
    )
    chart = (
        alt.Chart(per_mode)
        .mark_bar()
        .encode(
            x=alt.X("mode:N", title="Embedding mode"),
            y=alt.Y("doc_count:Q", title="Documents"),
            color=alt.Color(
                "mode:N",
                title="Mode",
                scale=alt.Scale(scheme="set2"),
                legend=None,
            ),
            tooltip=["mode", "doc_count"],
        )
        .properties(
            width=420,
            height=280,
            title="Panel B — embedding density by mode (1024-d)",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, per_mode


@app.cell
def _viz_cosine_histogram(alt, mo, sims):
    """Panel C — cosine-similarity distribution histogram."""
    chart = (
        alt.Chart(sims)
        .mark_bar(opacity=0.7)
        .encode(
            x=alt.X("similarity:Q", bin=alt.Bin(maxbins=30), title="Cosine similarity"),
            y=alt.Y("count():Q", title="Documents"),
            color=alt.Color("mode:N", title="Mode"),
            tooltip=["count()", "mode"],
        )
        .properties(
            width=620,
            height=280,
            title="Panel C — cosine similarity distribution",
        )
    )
    mo.ui.altair_chart(chart)
    return (chart,)


@app.cell
def _viz_lang_parity(alt, mo, coverage):
    """Panel D — per-language embedding parity (EN vs GA)."""
    lang_cov = (
        coverage.groupby(["language", "has_embedding"], as_index=False)
        .size()
        .rename(columns={"size": "doc_count"})
    )
    lang_cov["has_embedding"] = lang_cov["has_embedding"].map(
        {True: "embedded", False: "missing"}
    )
    chart = (
        alt.Chart(lang_cov)
        .mark_bar()
        .encode(
            x=alt.X("language:N", title="Language"),
            y=alt.Y("doc_count:Q", title="Documents"),
            color=alt.Color(
                "has_embedding:N",
                title="Coverage",
                scale=alt.Scale(
                    domain=["embedded", "missing"],
                    range=["#1f77b4", "#ff7f0e"],
                ),
            ),
            tooltip=["language", "has_embedding", "doc_count"],
        )
        .properties(
            width=420,
            height=280,
            title="Panel D — embedding parity (EN / GA / BILINGUAL)",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, lang_cov


@app.cell
def _health_banner(mo, coverage, engine_label):
    if engine_label == "md:cianfhoghlaim":
        _coverage_pct = (
            round(100 * coverage["has_embedding"].sum() / max(len(coverage), 1), 1)
        )
        status = "🟢 live"
    elif engine_label.startswith("local_duckdb (md unreachable"):
        _coverage_pct = 0
        status = "🟡 md unreachable"
    else:
        _coverage_pct = round(100 * coverage["has_embedding"].sum() / max(len(coverage), 1), 1)
        status = "🟡 offline fallback (synthetic)"

    mo.md(
        f"""
        ## Panel E — engine health

        | field | value |
        |-------|-------|
        | engine | `{engine_label}` |
        | status | {status} |
        | embedder | `BAAI/bge-m3` (1024-d) |
        | coverage | {_coverage_pct}% |
        """
    )
    return _coverage_pct, status


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🧬 This dashboard backs the
        ``oideachais-marimo-dashboards`` spec R-v2-3 (Phase 2 — the
        BGE-M3 embedding coverage). See
        ``openspec/specs/oideachais-marimo-dashboards/spec.md``.
        """
    )
    return


if __name__ == "__main__":
    app.run()