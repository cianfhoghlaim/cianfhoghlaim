# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""07 — BIEP ↔ official-media cross-archive edges
(oideachais-marimo-dashboards spec, R-v2-7).

Cross-archive **Cognee edge** view between the BIEP v1 oideachais
lakehouse (LC subjects + marking schemes) and the **official-media**
profiles (the Wikipedia + Companies House + CRO + Mastodon + Bluesky
authoritative-resolution surface — per
``dlt/official_media/source_resolver.py``).

Five visualisations:

- **Panel A** — per-subject × resolver matrix (heatmap)
- **Panel B** — resolver distribution (Wikipedia / Companies House /
  CRO / Mastodon / Bluesky pie)
- **Panel C** — top-15 strongest BIEP ↔ official-media edges
- **Panel D** — per-subject match-confidence distribution (violin)
- **Panel E** — health banner (engine + row count + status)

Data source: ``md:cianfhoghlaim.official_media.subject_match`` (the
canonical subject↔profile match table). Falls back to a synthetic
6-subject × 5-resolver match matrix when the lakehouse is
unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R-v2-7 (Phase 2 — BIEP ↔ official-media edges).
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
        # 🏛️ BIEP ↔ official-media edges

        Cross-archive **Cognee edge** view between the BIEP v1
        oideachais lakehouse (LC subjects + marking schemes) and the
        **official-media** profiles (Wikipedia + Companies House + CRO
        + Mastodon + Bluesky authoritative-resolution surface — per
        ``dlt/official_media/source_resolver.py``).

        Reads the ``cianfhoghlaim.official_media.subject_match`` cognify
        edges.

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
    from cianfhoghlaim.notebooks.nb_utils import BIEP_SUBJECTS

    RESOLVERS: tuple[str, ...] = (
        "wikipedia",
        "companies_house",
        "cro",
        "mastodon",
        "bluesky",
    )
    """The 5 official-media resolvers (per ``source_resolver.py``)."""

    return BIEP_SUBJECTS, RESOLVERS


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
        "CREATE TABLE IF NOT EXISTS oideachais_official_media_subject_match ("
        "  subject VARCHAR, resolver VARCHAR, profile_id VARCHAR,"
        "  confidence DOUBLE, edge_type VARCHAR"
        ")"
    )

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(BIEP_SUBJECTS, RESOLVERS, con, engine_label, mo, np, pd):
    """Read BIEP ↔ official-media edges — live or synthetic fallback."""
    src = engine_label
    edges = pd.DataFrame()

    if engine_label == "md:oideachais":
        try:
            edges = con.execute(
                "SELECT * FROM cianfhoghlaim.official_media.subject_match"
            ).fetchdf()
        except Exception:
            edges = pd.DataFrame()

    if edges.empty:
        # Synthetic 6-subject × 5-resolver match matrix
        _rows = []
        _rng = np.random.default_rng(123)
        for _subj in BIEP_SUBJECTS:
            for _resolver in RESOLVERS:
                _conf = float(_rng.uniform(0.55, 0.99))
                _edge = _rng.choice(["REFERENCES", "TEACHES", "LINKS_TO"])
                _rows.append({
                    "subject": _subj,
                    "resolver": _resolver,
                    "profile_id": f"{_resolver}_{_subj}",
                    "confidence": round(_conf, 3),
                    "edge_type": _edge,
                })
                # Add a second profile for wikipedia + companies_house (richer)
                if _resolver in {"wikipedia", "companies_house"}:
                    _conf2 = float(_rng.uniform(0.50, 0.85))
                    _rows.append({
                        "subject": _subj,
                        "resolver": _resolver,
                        "profile_id": f"{_resolver}_{_subj}_alt",
                        "confidence": round(_conf2, 3),
                        "edge_type": _edge,
                    })
        edges = pd.DataFrame(_rows)
        src = "synthetic (6×5=30 + 12 alt profiles = 42 edges)"

    mo.md(f"**Source**: `{src}` — **{len(edges)}** edges")
    return edges, src


@app.cell
def _viz_subject_resolver_matrix(alt, mo, edges):
    """Panel A — per-subject × resolver matrix (heatmap)."""
    pivot = (
        edges.groupby(["subject", "resolver"], as_index=False)
        .size()
        .rename(columns={"size": "profile_count"})
    )
    chart = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("resolver:N", title="Official-media resolver"),
            y=alt.Y("subject:N", title="LC subject"),
            color=alt.Color(
                "profile_count:Q",
                title="Profiles",
                scale=alt.Scale(scheme="viridis"),
            ),
            tooltip=["subject", "resolver", "profile_count"],
        )
        .properties(
            width=620,
            height=260,
            title="Panel A — LC subject × official-media resolver matrix",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, pivot


@app.cell
def _viz_resolver_dist(alt, mo, edges):
    """Panel B — resolver distribution (pie chart)."""
    by_resolver = (
        edges.groupby("resolver", as_index=False)
        .size()
        .rename(columns={"size": "profile_count"})
    )
    chart = (
        alt.Chart(by_resolver)
        .mark_arc(innerRadius=80)
        .encode(
            theta=alt.Theta("profile_count:Q"),
            color=alt.Color("resolver:N", title="Resolver"),
            tooltip=["resolver", "profile_count"],
        )
        .properties(
            width=380,
            height=280,
            title="Panel B — resolver distribution (5 backends)",
        )
    )
    mo.ui.altair_chart(chart)
    return by_resolver, chart


@app.cell
def _viz_top_edges(alt, mo, edges):
    """Panel C — top-15 strongest BIEP ↔ official-media edges."""
    top = edges.sort_values("confidence", ascending=False).head(15)
    chart = (
        alt.Chart(top)
        .mark_bar()
        .encode(
            x=alt.X("confidence:Q", title="Match confidence"),
            y=alt.Y(
                "profile_id:N",
                title="Edge (subject ↔ profile)",
                sort=top["profile_id"].tolist(),
            ),
            color=alt.Color(
                "resolver:N",
                title="Resolver",
                scale=alt.Scale(scheme="category10"),
            ),
            tooltip=["profile_id", "subject", "resolver", "confidence", "edge_type"],
        )
        .properties(
            width=620,
            height=380,
            title="Panel C — top-15 strongest BIEP ↔ official-media edges",
        )
    )
    mo.ui.altair_chart(chart)
    return chart, top


@app.cell
def _viz_confidence_violin(alt, mo, edges):
    """Panel D — per-subject match-confidence distribution (violin/box)."""
    chart = (
        alt.Chart(edges)
        .mark_boxplot(extent="min-max")
        .encode(
            x=alt.X("confidence:Q", title="Match confidence"),
            y=alt.Y("subject:N", title="LC subject"),
            color=alt.Color("subject:N", legend=None, scale=alt.Scale(scheme="tableau20")),
        )
        .properties(
            width=620,
            height=260,
            title="Panel D — per-subject match-confidence distribution",
        )
    )
    mo.ui.altair_chart(chart)
    return (chart,)


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
        | resolvers | 5 |
        """
    )
    return _n, status


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🏛️ This dashboard backs the
        ``oideachais-marimo-dashboards`` spec R-v2-7 (Phase 2 — the
        BIEP ↔ official-media cross-archive edges). See
        ``openspec/specs/oideachais-marimo-dashboards/spec.md``.
        """
    )
    return


if __name__ == "__main__":
    app.run()