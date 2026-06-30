"""Convex Function Latency — p50/p95/p99 per function.

This notebook reads the `convexFunctionCalls` Convex table when a live
deployment is available. Without a deployment, it renders an empty
dashboard with a prompt to provision the Convex backend.

Run with: marimo run croilar/notebooks/streams/teaching/convex_function_latency.py
"""

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def header():
    import marimo as mo
    return mo.md("# Convex Function Latency")


@app.cell
def imports():
    import os

    import altair as alt
    import marimo as mo
    import pandas as pd

    alt.data_transformers.enable("vegafusion")

    convex_url = os.environ.get("CROILAR_CONVEX_HTTP_URL")
    deploy_key = os.environ.get("CROILAR_CONVEX_DEPLOY_KEY")

    if not convex_url or not deploy_key:
        return alt, mo, pd, None, None, None  # type: ignore

    import httpx

    resp = httpx.post(
        f"{convex_url}/api/query",
        headers={"Authorization": f"Convex {deploy_key}"},
        json={"path": "convex_function_calls:getStats", "args": {"windowMs": 3_600_000}},
        timeout=10,
    )
    resp.raise_for_status()
    stats = resp.json().get("value", {})
    df = pd.DataFrame(
        [
            {"function": fn, **vals}
            for fn, vals in stats.items()
        ]
    )
    return alt, df, deploy_key, httpx, mo, pd  # type: ignore


@app.cell
def p95_chart(alt, df, mo):
    if df is None or df.empty:
        chart = mo.md("No live Convex data. Set `CROILAR_CONVEX_HTTP_URL` and `CROILAR_CONVEX_DEPLOY_KEY` to enable.")
    else:
        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("p95:Q", title="p95 latency (ms)"),
                y=alt.Y("function:N", sort="-x"),
                color=alt.Color("errorRate:Q", scale=alt.Scale(scheme="reds")),
                tooltip=["function", "p50", "p95", "p99", "count", "errorRate"],
            )
            .properties(title="Convex function p95 latency (last hour)", width=600, height=400)
        )
    return (chart,)


@app.cell
def layout(chart, mo):
    mo.vstack([chart]) if chart is not None else mo.md("Loading…")
    return


if __name__ == "__main__":
    app.run()
