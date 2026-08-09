# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""08 — CocoIndex v1 conformance dashboard (oideachais-marimo-dashboards spec, R10).

Audits the 7 BIEP v1 CocoIndex Apps for v1-API conformance —
the criteria captured in
``openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1``
which mandates every App uses ``coco.App`` + ``@coco.fn`` +
``ContextKey`` + ``mount_table_target`` and a ``BAAI/bge-m3``
embedder (1024-d).

Five visualisations:

- **Panel A** — App-by-App v1 conformance flag (yes/no badge grid)
- **Panel B** — embedder x App matrix (which App uses which model)
- **Panel C** — LanceDB table coverage (lance_scan hits)
- **Panel D** — embedder row-count per App
- **Panel E** — Apps that *do not* use the canonical ``BAAI/bge-m3``

Data source: ``md:cianfhoghlaim.cocoindex.apps`` +
``md:cianfhoghlaim.cocoindex.embedders``. Falls back to a synthetic
7-App set (the 6 BIEP v1 + the government_circulars App) when the
lakehouse is unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R10 + ``openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1/``.
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
        # 🔍 CocoIndex v1 conformance dashboard

        Audits the 7 BIEP v1 CocoIndex Apps for v1-API conformance
        — the criteria in
        ``openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1/``.

        Per-App conformance flag (yes/no), embedder matrix,
        LanceDB table coverage, and a list of Apps that *don't* use
        the canonical ``BAAI/bge-m3`` 1024-d embedder.

        ---
        """
    )
    return (mo,)


@app.cell
def _imports():
    import os
    import hashlib

    import altair as alt
    import duckdb
    import pandas as pd

    return alt, duckdb, hashlib, os, pd


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

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(con, engine_label, mo, pd, hashlib):
    """Read the CocoIndex Apps + embedders — live or synthetic fallback."""
    rows = []
    embedder_rows = []
    table_rows = []
    src = engine_label

    if engine_label == "md:cianfhoghlaim":
        try:
            df_apps = con.execute(
                "SELECT app_id, app_name, uses_v1_api, uses_bge_m3, "
                "  approximate_row_count, source_file, last_checked_at "
                "FROM cianfhoghlaim.cocoindex.apps"
            ).fetchdf()
            rows = df_apps.to_dict("records")
            src = "md:cianfhoghlaim.cocoindex.apps"
        except Exception as exc:
            rows = []
            src = f"md error: {exc!s:.60s}"

    if not rows:
        # Synthetic — 7 Apps (6 BIEP v1 + government_circulars)
        src = "synthetic (6 BIEP v1 + government_circulars)"
        _apps = [
            ("lc_mathematics_topics_en", "Mathematics EN", True, True),
            ("lc_chemistry_topics_en", "Chemistry EN", True, True),
            ("lc_geography_topics_en", "Geography EN", True, True),
            ("lc_gaeilge_topics_ga", "Gaeilge GA", True, True),
            ("lc_english_topics_en", "English EN", True, True),
            ("lc_computer_science_topics_en", "Computer Science EN", True, True),
            ("government_circulars", "Government Circulars", True, True),
        ]
        for _app_id, _name, _v1, _bge in _apps:
            _h = int.from_bytes(
                hashlib.sha1(_app_id.encode()).digest()[:8], "big"
            )
            rows.append({
                "app_id": _app_id,
                "app_name": _name,
                "uses_v1_api": _v1,
                "uses_bge_m3": _bge,
                "approximate_row_count": (_h % 5000) + 500,
                "source_file": f"ciolanza/cocoindex/{_app_id}.py",
                "last_checked_at": "2026-07-14",
            })

    apps_df = pd.DataFrame(rows)

    # Build the embedder matrix (which App uses which embedder model)
    for _, _r in apps_df.iterrows():
        if _r.get("uses_bge_m3"):
            embedder_rows.append({
                "app_id": _r["app_id"],
                "embedder": "BAAI/bge-m3",
                "dimension": 1024,
            })
        else:
            embedder_rows.append({
                "app_id": _r["app_id"],
                "embedder": _r.get("alt_embedder", "text-embedding-3-small"),
                "dimension": _r.get("alt_embedder_dim", 1536),
            })

    # Synthesise LanceDB table coverage rows
    for _, _r in apps_df.iterrows():
        _h = int.from_bytes(
            hashlib.sha1(f"lance|{_r['app_id']}".encode()).digest()[:4], "big"
        )
        table_rows.append({
            "app_id": _r["app_id"],
            "lance_table": f"cianfhoghlaim.lc.{_r['app_id']}",
            "row_count": _r["approximate_row_count"],
            "search_supported": True,
            "ranker_available": (_h % 4) >= 1,
        })

    embedders_df = pd.DataFrame(embedder_rows)
    tables_df = pd.DataFrame(table_rows)
    mo.md(
        f"**Source**: `{src}` — Apps: {len(apps_df)}, embedder rows: {len(embedders_df)}, "
        f"LanceDB rows: {len(tables_df)}"
    )
    return apps_df, embedders_df, src, tables_df


@app.cell
def _viz_app_conformance_grid(mo, apps_df):
    """Panel A — App-by-App v1 conformance flag (yes/no badge grid)."""
    if apps_df.empty:
        _md = mo.md("_No Apps detected._")
    else:
        _rows = []
        for _, _r in apps_df.iterrows():
            _icon = "✅" if _r.get("uses_v1_api") else "❌"
            _bge = "✅" if _r.get("uses_bge_m3") else "⚠️"
            _rows.append(
                f"| `{_r['app_id']}` | {_r['app_name']} | {_icon} | {_bge} | {_r['approximate_row_count']:,} |"
            )
        _md = mo.md(
            f"""
            ## Panel A — App-by-App v1 conformance

            | app_id | name | uses v1 API | uses bge-m3 | row count |
            |--------|------|--------------|-------------|-----------|
            {chr(10).join(_rows)}
            """
        )
    _md
    return


@app.cell
def _viz_embedder_x_app(alt, mo, embedders_df):
    """Panel B — embedder × App matrix heatmap."""
    # Build a (app_id × embedder) count matrix
    agg = (
        embedders_df.groupby(["app_id", "embedder"], as_index=False)
        .size()
        .rename(columns={"size": "n"})
    )
    chart = (
        alt.Chart(agg)
        .mark_rect()
        .encode(
            x=alt.X("embedder:N", title="Embedder"),
            y=alt.Y("app_id:N", title="App ID"),
            color=alt.Color(
                "n:Q", title="Apps",
                scale=alt.Scale(domain=[0, max(2, int(agg["n"].max()))], scheme="viridis"),
            ),
            tooltip=["app_id", "embedder", "n"],
        )
        .properties(
            width=620, height=300,
            title="Panel B — embedder × App matrix (1.0 = all Apps use this embedder)",
        )
    )
    mo.ui.altair_chart(chart)
    return agg, chart


@app.cell
def _viz_lance_coverage(alt, mo, tables_df):
    """Panel C — LanceDB row coverage per App (horizontal bar)."""
    if tables_df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(tables_df)
            .mark_bar()
            .encode(
                x=alt.X("row_count:Q", title="Row count", scale=alt.Scale(type="log")),
                y=alt.Y("app_id:N", title="App", sort="-x"),
                color=alt.condition(
                    alt.datum.search_supported,
                    alt.value("#4c78a8"),
                    alt.value("#e45756"),
                ),
                tooltip=["app_id", "lance_table", "row_count", "ranker_available"],
            )
            .properties(
                width=620, height=320,
                title="Panel C — LanceDB row coverage (red = search unsupported)",
            )
        )
    mo.ui.altair_chart(chart)
    return chart,


@app.cell
def _viz_apps_not_bge_m3(mo, apps_df):
    """Panel D — Apps that DON'T use BAAI/bge-m3 (highlight)."""
    if apps_df.empty:
        mo.md("_No Apps detected._")
    else:
        _bad = apps_df[apps_df["uses_bge_m3"] == False]  # noqa: E712
        if _bad.empty:
            _text = "✅ All Apps use the canonical BAAI/bge-m3 1024-d embedder."
        else:
            _text = (
                f"⚠️  **{len(_bad)} App(s) NOT using BAAI/bge-m3:**\n\n"
                + "\n".join(
                    f"- `{row['app_id']}` ({row['app_name']})"
                    for _, row in _bad.iterrows()
                )
            )
        mo.md(f"### Panel D — Apps not using BAAI/bge-m3\n\n{_text}")
    return


@app.cell
def _viz_app_row_count_bar(alt, mo, apps_df):
    """Panel E — per-App approximate row count (log-scaled bar)."""
    if apps_df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(apps_df)
            .mark_bar()
            .encode(
                x=alt.X("approximate_row_count:Q", title="Row count", scale=alt.Scale(type="log")),
                y=alt.Y("app_id:N", title="App", sort="-x"),
                color=alt.Color("uses_v1_api:N", title="v1 API", scale=alt.Scale(domain=[True, False], range=["#4c78a8", "#e45756"])),
                tooltip=["app_id", "approximate_row_count", "uses_v1_api"],
            )
            .properties(
                width=620, height=300,
                title="Panel E — per-App row count (log scale, color = v1 API)",
            )
        )
    mo.ui.altair_chart(chart)
    return chart,


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🔍 This dashboard backs the
        ``oideachais-marimo-dashboards`` R10 conformance audit.
        See `openspec/specs/oideachais-marimo-dashboards/spec.md`
        and ``openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1/``.
        """
    )
    return


if __name__ == "__main__":
    app.run()
