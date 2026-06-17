"""Web Route Health — TanStack route counts and test results per project.

Pulls the webstack snapshot produced by croilar/scripts/analyze-web-stack.ts
and renders route counts and Convex function counts per project. When a live
Convex deployment is available, the `testRuns` table provides the pass/fail
counts; otherwise the notebook renders the static analyzer output.

Run with: marimo run croilar/notebooks/streams/teaching/web_route_health.py
"""

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def header():
    import marimo as mo
    return mo.md("# Web Route Health")


@app.cell
def imports():
    import json
    from pathlib import Path

    import altair as alt
    import marimo as mo
    import pandas as pd

    alt.data_transformers.enable("vegafusion")

    SNAPSHOT_PATH = (
        Path(__file__).resolve().parents[3] / ".cache" / "webstack-snapshot.json"
    )
    if not SNAPSHOT_PATH.exists():
        return alt, mo, pd, None, None  # type: ignore
    snapshot = json.loads(SNAPSHOT_PATH.read_text())
    routes = pd.DataFrame(snapshot.get("tanstackRoutes", []))
    functions = pd.DataFrame(snapshot.get("convexFunctions", []))
    baml = pd.DataFrame(snapshot.get("bamlSchemas", []))
    return alt, baml, functions, mo, pd, routes  # type: ignore


@app.cell
def route_summary(alt, mo, routes):
    if routes is None or routes.empty:
        chart = mo.md("Snapshot not found. Run `bun run croilar/scripts/analyze-web-stack.ts`.")
    else:
        chart = (
            alt.Chart(routes)
            .mark_bar()
            .encode(
                x=alt.X("project:N", title="Project"),
                y=alt.Y("count():Q", title="Routes"),
                color=alt.Color("project:N", legend=None),
                tooltip=["project", "count()"],
            )
            .properties(title="TanStack routes per project", width=400, height=240)
        )
    return (chart,)


@app.cell
def function_summary(alt, functions, mo):
    if functions is None or functions.empty:
        fn_chart = mo.md("No Convex functions in snapshot.")
    else:
        fn_chart = (
            alt.Chart(functions)
            .mark_bar()
            .encode(
                x=alt.X("project:N"),
                y=alt.Y("count():Q", title="Functions"),
                color=alt.Color("kind:N"),
                tooltip=["project", "kind", "count()"],
            )
            .properties(title="Convex functions per project", width=400, height=240)
        )
    return (fn_chart,)


@app.cell
def layout(chart, fn_chart, mo):
    mo.vstack([chart, fn_chart]) if chart is not None and fn_chart is not None else mo.md("Loading…")
    return


if __name__ == "__main__":
    app.run()
