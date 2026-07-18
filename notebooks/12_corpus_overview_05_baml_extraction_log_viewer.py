# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""05 — BAML extraction log viewer (oideachais-marimo-dashboards spec, R7).

Operator-facing log viewer for the 5 canonical BIEP BAML extraction
functions (ExtractCurriculumSyllabus, ExtractExamPaperLayout,
ExtractMarkingSchemeGuideline, ExtractCrossLinguisticConcept,
ExtractSyllabusDiagram) + the per-subject asset generators
(GenerateChemQuestPack, GenerateMathPracticePack, etc.).

Renders:

- **Panel A** — extraction call counts per function (bar chart,
  per-subject stacked)
- **Panel B** — extraction latency distribution per function (box
  plot — synthesis because the BIEP ingestion writes to MLflow
  Traces not DuckLake directly)
- **Panel C** — extraction success rate over time (line chart)
- **Panel D** — retry & timeout counts (grouped bar)
- **Panel E** — live ``b.ExtractCurriculumSyllabus`` invocation on
  a sample syllabus + typed Pydantic dump

Data source: ``md:cianfhoghlaim.mlflow.runs`` (where MLflow Traces
emitted by the BAML client flow during the BIEP ingestion).
Falls back to a synthetic 30-call extraction log (5 functions ×
6 subjects; deterministic latencies from sha-1 hash) when the
lakehouse is unreachable.

Reference: ``openspec/specs/oideachais-marimo-dashboards/spec.md``
R7 ("DLT + LanceDB pipeline pattern in notebooks") — the
operator-view of the BAML half of the canonical
``DLT → BAML → CocoIndex → Cognee → Graphiti`` pipeline.
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
        # 🧪 BAML extraction log viewer

        Operator-facing view of the 5 canonical BIEP BAML extraction
        functions + per-subject asset generators. Shows call counts,
        latency distribution, success rate, retry counts, and a live
        BAML invocation against a sample syllabus.

        Reads from ``md:cianfhoghlaim.mlflow.runs`` (where the BAML
        client emits MLflow Traces during BIEP ingestion).

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
            con = duckdb.connect("md:cianfhoghlaim")
            engine_label = "md:cianfhoghlaim"
        except Exception as exc:
            con = duckdb.connect(":memory:")
            engine_label = f"local_duckdb (md unreachable: {type(exc).__name__})"
    else:
        con = duckdb.connect(":memory:")
        engine_label = "local_duckdb (offline fallback)"

    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _data_loading(con, engine_label, mo, pd, hashlib, dt, BIEP_SUBJECTS):
    """Build the extraction log — live or synthetic fallback."""
    extraction_functions = [
        "ExtractCurriculumSyllabus",
        "ExtractExamPaperLayout",
        "ExtractMarkingSchemeGuideline",
        "ExtractCrossLinguisticConcept",
        "ExtractSyllabusDiagram",
    ]
    rows = []

    if engine_label == "md:cianfhoghlaim":
        try:
            df = con.execute(
                """
                SELECT run_id, function_name, subject, started_at,
                       latency_ms, status, retries
                FROM cianfhoghlaim.mlflow.runs
                WHERE function_name LIKE 'Extract%' OR function_name LIKE 'Generate%'
                ORDER BY started_at DESC
                LIMIT 2000
                """
            ).fetchdf()
            if not df.empty:
                rows = df.to_dict("records")
                src = "md:cianfhoghlaim.mlflow.runs"
        except Exception as exc:
            rows = []
            src = f"md error: {exc!s:.60s}"

    if not rows:
        # Synthetic — 5 functions × 6 subjects; deterministic latencies
        src = "synthetic (5 fns × 6 subj; sha-1 jitter)"
        _base = dt.datetime(2026, 7, 14, 9, 0, 0)
        for _fn in extraction_functions:
            for _subj in BIEP_SUBJECTS:
                for _i in range(1):
                    _key = f"{_fn}|{_subj}|{_i}"
                    _h = int.from_bytes(
                        hashlib.sha1(_key.encode()).digest()[:4], "big"
                    )
                    _latency = 800 + (_h % 2200)  # 800..3000 ms
                    _retries = (_h >> 8) % 3
                    _status = "ok" if (_h >> 16) % 11 > 0 else "timeout"
                    rows.append({
                        "run_id": f"tr_{_key.replace('|', '_')}",
                        "function_name": _fn,
                        "subject": _subj,
                        "started_at": _base,
                        "latency_ms": _latency,
                        "status": _status,
                        "retries": _retries,
                    })
    df = pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["run_id", "function_name", "subject", "started_at", "latency_ms", "status", "retries"]
    )
    mo.md(f"**Source**: `{src}` — **{len(df)}** extraction runs")
    return df, extraction_functions, rows, src


@app.cell
def _viz_call_counts(alt, mo, df, extraction_functions):
    """Panel A — call counts per extraction function (stacked by subject)."""
    agg = (
        df.groupby(["function_name", "subject"], as_index=False)
        .size()
        .rename(columns={"size": "n"})
    )
    chart = (
        alt.Chart(agg)
        .mark_bar()
        .encode(
            x=alt.X("function_name:N", title="Extraction function", sort=extraction_functions),
            y=alt.Y("n:Q", title="Call count", stack=True),
            color=alt.Color("subject:N", title="Subject"),
            tooltip=["function_name", "subject", "n"],
        )
        .properties(
            width=620, height=280,
            title="Panel A — call count per extraction function (stacked by subject)",
        )
    )
    mo.ui.altair_chart(chart)
    return agg, chart


@app.cell
def _viz_latency_boxplot(alt, mo, df, extraction_functions):
    """Panel B — latency distribution per function (box plot)."""
    chart = (
        alt.Chart(df)
        .mark_boxplot(extent="min-max")
        .encode(
            x=alt.X("function_name:N", title="Function", sort=extraction_functions),
            y=alt.Y("latency_ms:Q", title="Latency (ms)", scale=alt.Scale(domain=[0, max(3500, df["latency_ms"].max() + 200)])),
            color=alt.Color("function_name:N", legend=None),
            tooltip=["function_name", "latency_ms"],
        )
        .properties(
            width=620, height=280,
            title="Panel B — latency distribution per extraction function",
        )
    )
    mo.ui.altair_chart(chart)
    return chart,


@app.cell
def _viz_success_over_time(alt, mo, df):
    """Panel C — extraction success rate over time."""
    # Coarse daily buckets
    agg = (
        df.assign(date=pd.to_datetime(df["started_at"]).dt.date)
        .groupby("date", as_index=False)
        .agg(total=("run_id", "size"), ok=("status", lambda s: int((s == "ok").sum())))
    )
    agg["success_rate"] = (agg["ok"] / agg["total"]).fillna(0.0)

    chart = (
        alt.Chart(agg)
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("success_rate:Q", title="Success rate", scale=alt.Scale(domain=[0, 1])),
            tooltip=["date:T", "success_rate:Q", "total:Q"],
        )
        .properties(
            width=620, height=240,
            title="Panel C — extraction success rate over time",
        )
    )
    mo.ui.altair_chart(chart)
    return agg, chart


@app.cell
def _viz_retry_timeouts(alt, mo, df):
    """Panel D — retry & timeout counts per function (grouped bar)."""
    agg = (
        df.groupby("function_name", as_index=False)
        .agg(
            timeouts=("status", lambda s: int((s == "timeout").sum())),
            retries=("retries", "sum"),
        )
    )
    # Reshape to long format for grouped-bar encoding
    _long = agg.melt(
        id_vars="function_name",
        value_vars=["timeouts", "retries"],
        var_name="metric",
        value_name="count",
    )
    chart = (
        alt.Chart(_long)
        .mark_bar()
        .encode(
            x=alt.X("function_name:N", title="Function"),
            y=alt.Y("count:Q", title="Count"),
            color=alt.Color("metric:N", title="Metric"),
            xOffset="metric:N",
            tooltip=["function_name", "metric", "count"],
        )
        .properties(
            width=620, height=240,
            title="Panel D — timeouts + retries per extraction function",
        )
    )
    mo.ui.altair_chart(chart)
    return agg, chart


@app.cell
def _live_baml_call(mo):
    """Panel E — live BAML ``ExtractCurriculumSyllabus`` invocation.

    Wrapped in try/except so the dashboard renders when the BAML
    client is unavailable (the typical ``USE_LOCAL_SCRAPES=true``
    offline state).
    """
    syllabus_input = mo.ui.text_area(
        value=(
            "Sample syllabus: explore atomic structure, bonding, "
            "and reaction kinetics through guided inquiry."
        ),
        label="📝 Syllabus text (BAML input)",
    )
    syllabus_input
    return (syllabus_input,)


@app.cell
def _run_baml_extraction(syllabus_input, mo):
    """Run ``b.ExtractCurriculumSyllabus`` on the syllabus input text."""
    _result = {"status": "skipped"}
    try:
        from cianfhoghlaim.baml_client import b

        _result = b.ExtractCurriculumSyllabus(
            source_pdf="sample_syllabus.pdf",
            subject="chemistry",
            language="en",
        )
        _result = {
            "status": "ok",
            "type": type(_result).__name__,
            "fields": [
                attr for attr in dir(_result)
                if not attr.startswith("_")
            ][:10],
        }
    except Exception as exc:
        _result = {
            "status": "offline",
            "error": str(exc)[:200],
            "note": "BAML client unavailable; dashboard still renders.",
        }

    mo.md(f"### Panel E — BAML result\n\n```json\n{_result!s}\n```")
    return (_result,)


@app.cell
def _footer(mo):
    mo.md(
        r"""
        ---

        🧪 This dashboard backs the
        ``oideachais-marimo-dashboards`` R7 DLT + LanceDB half —
        see `openspec/specs/oideachais-marimo-dashboards/spec.md`.
        """
    )
    return


if __name__ == "__main__":
    app.run()
