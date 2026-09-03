# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""10 — Dagster asset lineage (oideachais-marimo-dashboards spec, R7 + R9).

Operator-facing view of the Dagster asset graph that powers the
BIEP v1 + leabharlann + cognify pipelines. Reads from the Dagster
``asset_materialization_events`` table (the run log surface) +
``asset_observations`` (the lineage surface) to render:

- **Panel A** — materialisation success rate per asset (bar chart)
- **Panel B** — average asset materialisation duration (top-15 slowest)
- **Panel C** — asset group breakdown (lc / leabharlann / cognify /
  cocoindex / mlflow / langfuse)
- **Panel D** — assets currently with a pending re-materialisation
  (lineage fan-out indicator)
- **Panel E** — Dagster ``SDA`` sensor health banner (live
  ``dg sensor list`` summary, simulated fallback)

Data source: Dagster's run log (``md:cianfhoghlaim.dagster.events``).
Falls back to a synthetic 42-asset graph (7 subjects × 6 BAML
stages — the lc5/lc6 chain from
``openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/``)
when the lakehouse is unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R7 + R9 + ``openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/``.
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
        # 🪢 Dagster asset lineage

        Operator-facing view of the Dagster asset graph that powers
        BIEP v1 + leabharlann + cognify. The flagship
        ``british-isles-education-pipeline`` code-location loads
        **42 lc5/lc6 assets** (7 subjects × 6 BAML stages) +
        6 stage-1 ingestion assets + 6 stage-3 CocoIndex assets
        + 6 stage-5 cognify assets + 6 stage-6 Graphiti assets.

        Reads the canonical
        ``openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/``
        graph.

        ---
        """
    )
    return (mo,)


@app.cell
def _imports():
    import os
    import datetime as dt
    import hashlib

    import altair as alt
    import duckdb
    import pandas as pd

    return alt, dt, duckdb, hashlib, os, pd


@app.cell
def _constants():
    from cianfhoghlaim.notebooks.nb_utils import BIEP_SUBJECTS

    return (BIEP_SUBJECTS,)


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
def _data_loading(con, engine_label, mo, pd, hashlib, BIEP_SUBJECTS):
    """Read the asset graph + materialisation events — live or synthetic."""
    rows = []
    src = engine_label

    if engine_label == "md:cianfhoghlaim":
        try:
            df = con.execute(
                """
                SELECT asset_key, asset_group, status, duration_seconds,
                       started_at, retries
                FROM cianfhoghlaim.dagster.events
                ORDER BY started_at DESC
                LIMIT 5000
                """
            ).fetchdf()
            if not df.empty:
                rows = df.to_dict("records")
                src = "md:cianfhoghlaim.dagster.events"
        except Exception as exc:
            rows = []
            src = f"md error: {exc!s:.60s}"

    if not rows:
        # Synthetic — 42 lc5/lc6 assets + 6 stage-1 + 6 stage-3 + 6 stage-5 + 6 stage-6 = 66
        src = "synthetic (42 lc5/lc6 + 6 stage-1 + 6 stage-3 + 6 stage-5 + 6 stage-6 = 66 assets)"
        _asset_groups = ("stage1_ingest", "stage3_cocoindex", "stage5_cognify", "stage6_graphiti")

        # 7 BIEP subjects × 6 BAML stages = 42 lc5/lc6 assets
        for _subj in BIEP_SUBJECTS:
            for _stage in range(1, 7):
                _key = f"lc{_stage}_{_subj}"
                _h = int.from_bytes(
                    hashlib.sha1(_key.encode()).digest()[:4], "big"
                )
                rows.append({
                    "asset_key": _key,
                    "asset_group": f"lc{_stage}",
                    "status": "ok" if (_h % 13) > 0 else "failed",
                    "duration_seconds": 30 + (_h % 270),
                    "retries": (_h >> 8) % 4,
                    "pending_reattempt": (_h >> 12) % 7 == 0,
                })
        # 6 stage-1 + 6 stage-3 + 6 stage-5 + 6 stage-6 assets
        for _grp in _asset_groups:
            for _subj in BIEP_SUBJECTS[:6]:  # only 6 to keep total ≤ 66
                _key = f"{_grp}_{_subj}"
                _h = int.from_bytes(
                    hashlib.sha1(_key.encode()).digest()[:4], "big"
                )
                rows.append({
                    "asset_key": _key,
                    "asset_group": _grp,
                    "status": "ok" if (_h % 11) > 0 else "failed",
                    "duration_seconds": 40 + (_h % 320),
                    "retries": (_h >> 8) % 3,
                    "pending_reattempt": (_h >> 12) % 9 == 0,
                })

    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(
            columns=["asset_key", "asset_group", "status",
                     "duration_seconds", "retries", "pending_reattempt"]
        )
    mo.md(f"**Source**: `{src}` — **{len(df)}** asset materialisation events")
    return df, src


@app.cell
def _viz_success_rate_per_asset(alt, mo, df):
    """Panel A — materialisation success rate per asset (top-15 lowest)."""
    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        agg = (
            df.groupby("asset_key", as_index=False)
            .agg(total=("status", "size"), ok=("status", lambda s: int((s == "ok").sum())))
        )
        agg["success_rate"] = agg["ok"] / agg["total"]
        # Take 15 with lowest success rate (most interesting)
        agg = agg.sort_values("success_rate", ascending=True).head(15)

        chart = (
            alt.Chart(agg)
            .mark_bar()
            .encode(
                x=alt.X("success_rate:Q", title="Success rate", scale=alt.Scale(domain=[0, 1])),
                y=alt.Y("asset_key:N", title="Asset", sort="-x"),
                color=alt.condition(
                    alt.datum.success_rate >= 0.95,
                    alt.value("#4c78a8"),
                    alt.value("#e45756"),
                ),
                tooltip=["asset_key", "success_rate", "total", "ok"],
            )
            .properties(
                width=620, height=320,
                title="Panel A — 15 assets with the lowest success rate (red = < 95%)",
            )
        )
    mo.ui.altair_chart(chart)
    return chart,


@app.cell
def _viz_slowest_15_assets(alt, mo, df):
    """Panel B — top-15 slowest assets (average duration)."""
    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        agg = (
            df.groupby("asset_key", as_index=False)
            .agg(avg_seconds=("duration_seconds", "mean"))
            .sort_values("avg_seconds", ascending=False)
            .head(15)
        )
        chart = (
            alt.Chart(agg)
            .mark_bar()
            .encode(
                x=alt.X("avg_seconds:Q", title="Avg duration (s)"),
                y=alt.Y("asset_key:N", title="Asset", sort="-x"),
                color=alt.Color("avg_seconds:Q", scale=alt.Scale(scheme="viridis"), legend=None),
                tooltip=["asset_key", "avg_seconds"],
            )
            .properties(
                width=620, height=320,
                title="Panel B — top-15 slowest assets (avg duration)",
            )
        )
    mo.ui.altair_chart(chart)
    return chart,


@app.cell
def _viz_asset_group_breakdown(alt, mo, df):
    """Panel C — asset group breakdown (count per group + per-status)."""
    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        agg = (
            df.groupby(["asset_group", "status"], as_index=False)
            .size()
            .rename(columns={"size": "n"})
        )
        chart = (
            alt.Chart(agg)
            .mark_bar()
            .encode(
                x=alt.X("asset_group:N", title="Asset group (lc / stage)"),
                y=alt.Y("n:Q", title="Count", stack=True),
                color=alt.Color("status:N", title="Status"),
                tooltip=["asset_group", "status", "n"],
            )
            .properties(
                width=620, height=240,
                title="Panel C — asset group × status breakdown",
            )
        )
    mo.ui.altair_chart(chart)
    return chart,


@app.cell
def _viz_pending_reattempt_indicator(mo, df):
    """Panel D — assets pending a re-materialisation (lineage fan-out flag)."""
    if df.empty:
        mo.md("_No asset events loaded._")
    else:
        _pending = df[df["pending_reattempt"] == True]  # noqa: E712
        if _pending.empty:
            _text = "✅ No assets have a pending re-materialisation in lineage."
        else:
            _lines = "\n".join(f"- `{row['asset_key']}` (group `{row['asset_group']}`)"
                               for _, row in _pending.iterrows())
            _text = (
                f"⚠️  **{len(_pending)} assets** flagged for re-materialisation "
                f"(lineage fan-out detected):\n\n{_lines}"
            )
        mo.md(f"### Panel D — pending re-materialisation\n\n{_text}")
    return


@app.cell
def _sensor_health_banner(mo, engine_label):
    """Panel E — Dagster SDA sensor health banner.

    Live: ``dg sensor list`` subprocess summary.
    Fallback: synthetic 6-sensor summary (5 SDA + the
    sitemap-hash ChangeDetection.io sensor).
    """
    sensors = []
    try:
        import subprocess
        _proc = subprocess.run(
            ["dg", "sensor", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if _proc.returncode == 0 and _proc.stdout.strip():
            import json as _json
            _parsed = _json.loads(_proc.stdout)
            sensors = _parsed if isinstance(_parsed, list) else []
            src = "dg sensor list --json"
        else:
            sensors = []
            src = f"dg sensor list failed (rc={_proc.returncode})"
    except Exception as exc:
        sensors = []
        src = f"dg unavailable: {exc!s:.60s}"

    if not sensors:
        # Synthetic — 5 SDA sensors + 1 sitemap-hash sensor
        sensors = [
            {"name": "biep_syllabus_sitemap_hash", "status": "running", "last_tick": "2026-07-14T09:30:00"},
            {"name": "biep_exam_paper_sitemap_hash", "status": "running", "last_tick": "2026-07-14T09:30:00"},
            {"name": "biep_marking_scheme_sitemap_hash", "status": "running", "last_tick": "2026-07-14T09:30:00"},
            {"name": "leabharlann_pdf_ingest", "status": "stopped", "last_tick": "2026-07-13T21:14:00"},
            {"name": "cocoindex_v1_conformance", "status": "running", "last_tick": "2026-07-14T09:30:00"},
            {"name": "agent_memory_letta_sync", "status": "running", "last_tick": "2026-07-14T09:30:00"},
        ]
        src = "synthetic (5 SDA + 1 sitemap-hash sensors)"

    _status_counts = {}
    for _s in sensors:
        _st = _s.get("status", "?")
        _status_counts[_st] = _status_counts.get(_st, 0) + 1

    _rows = "\n".join(
        f"| `{_s.get('name', '?')}` | {_s.get('status', '?')} | {_s.get('last_tick', '?')} |"
        for _s in sensors
    )
    mo.md(
        f"""
        ### Panel E — Dagster sensor health (`{src}`)

        **Status counts**: {_status_counts}

        | name | status | last tick |
        |------|--------|-----------|
        {_rows}
        """
    )
    return


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🪢 This dashboard backs the
        ``oideachais-marimo-dashboards`` R7 + R9 dagster lineage
        arms. See
        `openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/`.
        """
    )
    return


if __name__ == "__main__":
    app.run()
