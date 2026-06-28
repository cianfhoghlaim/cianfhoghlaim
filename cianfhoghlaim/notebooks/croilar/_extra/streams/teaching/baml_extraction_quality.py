"""BAML Extraction Quality — schema counts and class distribution.

Static analyzer output. When a live Langfuse trace source is configured,
this notebook can be extended to show per-call confidence histograms.

Run with: marimo run croilar/notebooks/streams/teaching/baml_extraction_quality.py
"""

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def header():
    import marimo as mo
    return mo.md("# BAML Extraction Quality")


@app.cell
def imports():
    import json
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import pandas as pd

    alt.data_transformers.enable("vegafusion")

    snapshot_path = (
        Path(__file__).resolve().parents[3] / ".cache" / "webstack-snapshot.json"
    )
    if not snapshot_path.exists():
        return alt, mo, pd, None  # type: ignore
    snapshot = json.loads(snapshot_path.read_text())
    baml = pd.DataFrame(snapshot.get("bamlSchemas", []))
    return alt, baml, mo, pd  # type: ignore


@app.cell
def schema_chart(alt, baml, mo):
    if baml is None or baml.empty:
        chart = mo.md("No BAML schemas in snapshot. Run `bun run croilar/scripts/analyze-web-stack.ts`.")
    else:
        chart = (
            alt.Chart(baml)
            .transform_fold(
                ["classCount", "functionCount", "enumCount"],
                as_=["kind", "count"],
            )
            .mark_bar()
            .encode(
                x=alt.X("project:N", title=None),
                y=alt.Y("count:Q", title="Count"),
                color=alt.Color("kind:N", scale=alt.Scale(scheme="set2")),
                xOffset="kind:N",
                tooltip=["project", "kind", "count"],
            )
            .properties(title="BAML declarations per project", width=500, height=300)
        )
    return (chart,)


@app.cell
def layout(chart, mo):
    mo.vstack([chart]) if chart is not None else mo.md("Loading…")
    return


if __name__ == "__main__":
    app.run()
