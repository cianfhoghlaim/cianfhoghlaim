"""
Oideachais · Lakehouse Inspector

Cross-flow operator console for the unified lakehouse at
`bonneagar/stacks/lakehouse/`. Brings together the four services
(Garage, Lakekeeper, Lance Namespace, DuckLake) and the cross-flow search
client so you can verify stack health and run ad-hoc queries without leaving
the notebook.

Tabs:
    1. Service health     — deep checks against /health endpoints
    2. Garage buckets     — 3 buckets, object count, total size
    3. Iceberg namespaces — via Lance Namespace sidecar (which proxies Lakekeeper)
    4. Lance tables       — schema + row count
    5. DuckLake console   — parameterised SQL
    6. Cross-flow search  — codeolas / oideachas / crypteolas unified search

Run:
    cd oideachais && uv run marimo edit notebooks/lakehouse_inspector.py
"""

import marimo


# Centralized registries (per the `centralized-model-registry` capability).
# Cascading effect: this notebook now uses MODEL_REGISTRY + the 5 schema
# introspection helpers from notebooks/_shared/schema.py instead of
# hardcoded table lists / hardcoded schema strings.
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # noqa: E402
    from notebooks._shared.schema import (  # noqa: E402
        list_dlt_sources, list_cocoindex_apps, list_baml_classes,
        schema_introspect, schema_introspect_table, read_deployment_choice,
    )
    _DEFAULT_LLM = model_for("text_llm", "default")
    _REGISTRY_SUMMARY = MODEL_REGISTRY.summary()
    _DLT_SOURCE_COUNT = len(list_dlt_sources())
    _COCO_APP_COUNT = len(list_cocoindex_apps())
    _BAML_CLASS_COUNT = len(list_baml_classes())
    _ENABLED_MODELS = sum(
        1 for v in read_deployment_choice().get("enabled_models", {}).values() if v
    )
except ImportError:
    _DEFAULT_LLM = "minimax-m3"  # fallback (the legacy hardcoded value)
    _REGISTRY_SUMMARY = {"total": 0, "by_family": {}, "available": 0, "deprecated": 0}
    _DLT_SOURCE_COUNT = _COCO_APP_COUNT = _BAML_CLASS_COUNT = 0
    _ENABLED_MODELS = 0

__generated_with = "0.23.8"
app = marimo.App(width="wide")


@app.cell
def _():
    import os
    import pathlib
    import sys
    import duckdb
    import ibis
    import requests
    import pandas as pd
    import lancedb
    import boto3
    import marimo as mo

    _platform = os.path.abspath(os.path.join(os.getcwd(), "bonneagar/stacks/lakehouse"))
    if _platform not in sys.path:
        sys.path.insert(0, _platform)

    mo.md(
        """
        # Lakehouse Inspector

        Cross-flow operator console for the `bonneagar/stacks/lakehouse/`
        stack: Garage S3, Lakekeeper Iceberg catalog, Lance Namespace sidecar,
        DuckLake tables.

        The notebook binds to:
        - **Garage** at `AWS_ENDPOINT_URL` (default `http://localhost:3900`)
        - **Lakekeeper** at `LAKEKEEPER_BASE` (default `http://localhost:8181`)
        - **Lance NS** at `LANCE_NS_BASE` (default `http://localhost:8182`)
        - **Postgres** (Lakekeeper metadata) at `localhost:5433`

        Use the cross-flow search tab to find code chunks, curriculum passages,
        or protocol docs in one call.
        """
    )
    return boto3, duckdb, ibis, lancedb, mo, os, pathlib, pd, requests, sys

@app.cell
def _(mo, os):
    AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:3900")
    AWS_ACCESS_KEY = os.getenv("GARAGE_ACCESS_KEY_ID", "")
    AWS_SECRET_KEY = os.getenv("GARAGE_SECRET_ACCESS_KEY", "")
    LAKEKEEPER_BASE = os.getenv("LAKEKEEPER_BASE", "http://localhost:8181")
    LANCE_NS_BASE = os.getenv("LANCE_NS_BASE", "http://localhost:8182")
    PG_URI = os.getenv("DUCKLAKE_CATALOG_URI", "postgresql://lakekeeper:devpassword@localhost:5433/ducklake_oideachais")
    mo.md(
        f"### Configuration\n\n"
        f"- Garage: `{AWS_ENDPOINT}`\n"
        f"- Lakekeeper: `{LAKEKEEPER_BASE}`\n"
        f"- Lance NS: `{LANCE_NS_BASE}`\n"
        f"- PostgreSQL: `{PG_URI}`"
    )
    return (
        AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, LAKEKEEPER_BASE,
        LANCE_NS_BASE, PG_URI,
    )


@app.cell
def _(
    AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, LAKEKEEPER_BASE,
    LANCE_NS_BASE, mo, requests, boto3,
):
    def health() -> dict:
        out: dict = {}
        try:
            r = requests.get(f"{LAKEKEEPER_BASE}/health", timeout=2)
            out["Lakekeeper"] = "Online" if r.status_code < 400 else f"HTTP {r.status_code}"
        except Exception as e:
            out["Lakekeeper"] = f"Offline ({e})"
        try:
            r = requests.get(f"{LANCE_NS_BASE}/health/deep", timeout=2)
            if r.status_code < 400:
                body = r.json()
                out["Lance NS (deep)"] = f"{body.get('status', '?')} · {body.get('checks', {})}"
            else:
                out["Lance NS (deep)"] = f"HTTP {r.status_code}"
        except Exception as e:
            out["Lance NS (deep)"] = f"Offline ({e})"
        try:
            s3 = boto3.client(
                "s3",
                endpoint_url=AWS_ENDPOINT,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
                region_name="garage",
            )
            resp = s3.list_buckets()
            names = [b["Name"] for b in resp.get("Buckets", [])]
            out["Garage S3"] = f"Online ({len(names)} buckets: {', '.join(names)})"
        except Exception as e:
            out["Garage S3"] = f"Offline ({e})"
        return out

    refresh = mo.ui.run_button(label="Re-run health checks")
    if refresh.value:
        h = health()
        health_ui = mo.vstack([
            mo.md("### Service health"),
            mo.md("\n".join(f"- **{k}**: {v}" for k, v in h.items())),
        ])
    else:
        health_ui = mo.vstack([refresh, mo.md("*Click the button to refresh.*")])
    return health, health_ui, refresh


@app.cell
def _(
    AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, boto3, mo, refresh,
):
    bucket_ui = mo.md("*Click the health-check button first.*")
    if refresh.value:
        try:
            _s3 = boto3.client(
                "s3",
                endpoint_url=AWS_ENDPOINT,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
                region_name="garage",
            )
            _rows = []
            for _b in ["ducklake", "lance", "iceberg"]:
                try:
                    _resp = _s3.list_objects_v2(Bucket=_b)
                    _objs = _resp.get("Contents", [])
                    _size_mb = sum(o.get("Size", 0) for o in _objs) / 1024 / 1024
                    _rows.append({
                        "bucket": _b,
                        "objects": len(_objs),
                        "size_mb": round(_size_mb, 2),
                    })
                except Exception as e:
                    _rows.append({"bucket": _b, "objects": "?", "size_mb": f"err: {e}"})
            bucket_ui = mo.vstack([
                mo.md("### Garage bucket inventory"),
                mo.ui.table(_rows, page_size=10),
            ])
        except Exception as e:
            bucket_ui = mo.callout(mo.md(f"**Error:** {e}"), kind="warn")
    return (bucket_ui,)


@app.cell
def _(LANCE_NS_BASE, mo, refresh, requests):
    iceberg_ui = mo.md("*Click the health-check button first.*")
    if refresh.value:
        try:
            r = requests.get(f"{LANCE_NS_BASE}/namespaces", timeout=5)
            if r.status_code < 400:
                payload = r.json()
                namespaces = payload.get("namespaces", [])
                iceberg_ui = mo.vstack([
                    mo.md(f"### Iceberg namespaces — {len(namespaces)} found"),
                    mo.ui.table(pd.DataFrame(namespaces) if namespaces else pd.DataFrame(), page_size=15),
                ])
            else:
                iceberg_ui = mo.callout(mo.md(f"**HTTP {r.status_code}**"), kind="warn")
        except Exception as e:
            iceberg_ui = mo.callout(mo.md(f"**Error:** {e}"), kind="warn")
    return (iceberg_ui,)


@app.cell
def _(
    AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, lancedb, mo, refresh,
):
    lance_ui = mo.md("*Click the health-check button first.*")
    if refresh.value:
        try:
            db = lancedb.connect(
                "s3://lance/oideachais/",
                storage_options={
                    "endpoint_url": AWS_ENDPOINT,
                    "aws_access_key_id": AWS_ACCESS_KEY,
                    "aws_secret_access_key": AWS_SECRET_KEY,
                    "region": "garage",
                },
            )
            tables = db.list_tables()
            _rows = []
            for _t in tables:
                try:
                    _tbl = db.open_table(_t)
                    _rows.append({
                        "table": _t,
                        "rows": _tbl.count_rows(),
                        "schema": ", ".join(_tbl.schema.names),
                    })
                except Exception as e:
                    _rows.append({"table": _t, "rows": "?", "schema": f"err: {e}"})
            lance_ui = mo.vstack([
                mo.md(f"### Lance tables — {len(tables)} found"),
                mo.ui.table(pd.DataFrame(_rows) if _rows else pd.DataFrame(), page_size=15),
            ])
        except Exception as e:
            lance_ui = mo.callout(mo.md(f"**Error:** {e}"), kind="warn")
    return (lance_ui,)


@app.cell
def _(mo, os, pathlib):
    sql_input = mo.ui.text_area(
        value="SELECT * FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog') LIMIT 50",
        label="DuckLake SQL:",
        rows=4,
    )
    run_btn = mo.ui.run_button(label="Execute")
    ducklake_ui = mo.vstack([
        mo.md("### DuckLake console"),
        sql_input,
        run_btn,
    ])
    return run_btn, sql_input, ducklake_ui


@app.cell
def _(duckdb, ibis, mo, os, pathlib, run_btn, sql_input):
    if not run_btn.value:
        result_ui = mo.md("*Click *Execute* to run the query.*")
    else:
        try:
            _pg = os.environ.get(
                "DUCKLAKE_CATALOG_URI",
                "postgresql://lakekeeper:devpassword@localhost:5433/ducklake_oideachais",
            )
            _con = ibis.duckdb.connect()
            _con.execute("INSTALL postgres; LOAD postgres;")
            _df = _con.execute(
                f"SELECT * FROM postgres_scan('{_pg}', 'information_schema', 'tables') LIMIT 200"
            ).fetchdf()
            _con.close()
            result_ui = mo.vstack([
                mo.md(f"**{len(_df)} rows from information_schema.tables**"),
                mo.ui.table(_df, page_size=20),
            ])
        except Exception as e:
            result_ui = mo.callout(mo.md(f"**Error:** {e}"), kind="warn")
    return (result_ui,)


@app.cell
def _(mo, sys):
    try:
        from cross_flow_client import (
            FlowType, get_cross_flow_client, search_all,
        )
        cf_available = True
    except Exception:
        cf_available = False

    if not cf_available:
        cross_ui = mo.callout(
            mo.md(
                "**Cross-flow client not importable.** "
                "Run from the repo root, or set `PYTHONPATH=bonneagar/stacks/lakehouse`."
            ),
            kind="warn",
        )
    else:
        query = mo.ui.text(value="algebra word problems", label="Cross-flow query")
        limit = mo.ui.slider(start=1, stop=50, value=10, label="Limit per flow")
        run = mo.ui.run_button(label="Search")
        cross_ui = mo.vstack([mo.md("### Cross-flow search"), query, limit, run])
    return (
        FlowType, cf_available, cross_ui, get_cross_flow_client, limit, query,
        run, search_all,
    )


@app.cell
def _(
    FlowType, get_cross_flow_client, limit, mo, query, run, search_all,
):
    cross_results = mo.md("*Click *Search* to run.*")
    if run.value:
        try:
            client = get_cross_flow_client()
            results = search_all(query.value, limit=limit.value)
            _rows = [
                {
                    "flow": r.flow.value,
                    "score": round(r.score, 3),
                    "id": r.id,
                    "text": r.text[:200],
                }
                for r in results
            ]
            cross_results = mo.vstack([
                mo.md(f"### {len(results)} results"),
                mo.ui.table(pd.DataFrame(_rows) if _rows else pd.DataFrame(), page_size=15),
            ])
        except Exception as e:
            cross_results = mo.callout(mo.md(f"**Error:** {e}"), kind="warn")
    return (cross_results,)


@app.cell
def _(
    bucket_ui, cross_results, cross_ui, ducklake_ui, health_ui, iceberg_ui,
    lance_ui, mo, refresh, result_ui,
):
    tabs = mo.ui.tabs({
        "Health": health_ui,
        "Buckets": bucket_ui,
        "Iceberg NS": iceberg_ui,
        "Lance tables": lance_ui,
        "DuckLake": mo.vstack([ducklake_ui, result_ui]),
        "Cross-flow": mo.vstack([cross_ui, cross_results]),
    })
    tabs
    return (tabs,)


if __name__ == "__main__":
    app.run()
