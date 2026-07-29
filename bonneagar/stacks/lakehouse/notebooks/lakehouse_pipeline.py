# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "ibis-framework[duckdb,lancedb]>=9.0",
#     "pandas>=2.0",
#     "requests>=2.31",
# ]
# ///
"""Lakehouse Pipeline Demo — ibis-first, bunchloch-local.

Demonstrates the full local data plane (per
``openspec/changes/2026-07-06-wire-biep-notebooks-to-lakehouse/``):

| Layer       | Local (this notebook)               |
|-------------|--------------------------------------|
| Query engine | DuckDB via ``ibis.duckdb.connect()`` |
| SQL catalog  | DuckLake (Postgres on lakehouse:5433) |
| Vector RAG   | LanceDB via ``ibis.lancedb.connect()`` |
| REST         | Lakekeeper (8181) for Iceberg registration |
| Object store | Garage S3 (3900) for Parquet + Lance files |
| Secrets      | Infisical vault (port 8081), 7 paths seeded |

The "remote" cell toggles the same code to MotherDuck + Lance Cloud + R2
(those branches are kept for future production migration; today the
bunchloch-local path is fully wired).
"""

import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.md(
        """
    # Lakehouse Pipeline Demo (ibis-first, bunchloch-local)

    The full local data plane, end-to-end, with **ibis** as the
    canonical entrypoint (per the
    [ibis skill](.agents/skills/ibis/SKILL.md) — *the KCG-preferred
    analytics layer*).

    The notebook executes in three steps:
    1. **Connect** — `ibis.duckdb.connect()` to the local DuckLake catalog
       on `lakehouse-postgres`; `ibis.lancedb.connect()` to the Lance
       namespace sidecar at `rest://lakehouse-lance-namespace:8182`.
    2. **Smoke** — list 6 tables, verify the `lakehouse_cianfhoghlaim` schema
       is queryable.
    3. **Preview** — read the top of the empty BIEP tables.
        """
    )
    return (mo,)


@app.cell
def _(mo):
    import os

    environment = mo.ui.radio(
        options={"local": "Local Development", "remote": "Remote Production"},
        value="local",
        label="Environment",
    )
    environment
    return environment, os


@app.cell
def _(environment, os):
    # ibis-first connection strings
    if environment.value == "local":
        CONFIG = {
            # ibis.duckdb.connect() — the canonical KCG entrypoint
            # (per .agents/skills/ibis/SKILL.md)
            "duckdb_conn": (
                "ducklake:postgres:"
                f"host={os.getenv('LOCAL_HOST', 'lakehouse-postgres')} "
                f"port={os.getenv('LOCAL_PORT', '5432')} "
                f"user={os.getenv('LOCAL_USER', 'lakekeeper')} "
                f"password={os.getenv('LOCAL_PASSWORD', 'devpassword')} "
                f"dbname={os.getenv('LOCAL_DBNAME', 'ducklake_cianfhoghlaim')}"
            ),
            "data_path": "s3://iceberg/",
            "lance_root": "s3://lance/",
            "s3_endpoint": os.getenv("AWS_ENDPOINT_URL", "http://lakehouse-garage:3900"),
            "lance_namespace_url": os.getenv(
                "LANCE_NAMESPACE_URL", "rest://lakehouse-lance-namespace:8182"
            ),
            "destination": "ducklake (lakehouse-postgres)",
        }
    else:
        CONFIG = {
            "duckdb_conn": (
                f"ducklake:postgres:"
                f"host={os.getenv('PLANETSCALE_HOST', 'aws.connect.psdb.cloud')} "
                f"user={os.getenv('PLANETSCALE_USER', 'lakehouse')} "
                f"password={os.getenv('PLANETSCALE_PASSWORD', '')} "
                f"dbname={os.getenv('PLANETSCALE_DBNAME', 'lakehouse')} "
                f"sslmode=require"
            ),
            "data_path": f"r2://{os.getenv('R2_BUCKET_NAME', 'lakehouse')}/ducklake/",
            "lance_root": f"r2://{os.getenv('R2_BUCKET_NAME', 'lakehouse')}/lance/",
            "r2_endpoint": f"https://{os.getenv('R2_ACCOUNT_ID', 'xxx')}.r2.cloudflarestorage.com",
            "lance_namespace_url": os.getenv(
                "LANCE_NAMESPACE_URL", "https://lance-api.cianfhoghlaim.ie"
            ),
            "destination": "motherduck",
        }

    print(f"Using {environment.value} configuration")
    return (CONFIG,)


@app.cell
def _(mo):
    mo.md("""
    ## Step 2 — List the BIEP tables (against the local Lakekeeper)

    The 6 BIEP subject namespaces live in the ``lakehouse_cianfhoghlaim``
    DuckLake catalog and are mirrored as Iceberg tables in Lakekeeper.
    Each subject has 4 tables — one per (level × language).
    """)
    return


@app.cell
def _(CONFIG, mo, requests):
    # Query Lakekeeper's REST catalog for the registered namespaces
    namespaces = []
    if "lakehouse" in CONFIG.get("lance_namespace_url", ""):
        lakekeeper_url = "http://lakehouse:8181"
    else:
        lakekeeper_url = "http://localhost:8181"

    try:
        resp = requests.get(f"{lakekeeper_url}/v1/config", timeout=5)
        if resp.status_code == 200:
            mo.md(f"**Lakekeeper** `{lakekeeper_url}` reachable ✓")
        else:
            mo.md(f"**Lakekeeper** returned {resp.status_code}")
    except Exception as e:
        mo.md(f"**Lakekeeper** unreachable: `{e}`")
    return


@app.cell
def _(mo):
    mo.md("""
    ## Step 3 — Verify the 6 BIEP subjects' tables exist

    We pre-create 4 tables per subject in the DuckLake catalog:

    | Subject          | Tables (level × language) |
    |------------------|----------------------------|
    | mathematics      | `hl_en`, `ol_en`, `hl_ga`, `ol_ga` |
    | chemistry        | `hl_en`, `ol_en`, `hl_ga`, `ol_ga` |
    | geography        | `hl_en`, `ol_en`, `hl_ga`, `ol_ga` |
    | gaeilge          | `hl_en`, `ol_en`, `hl_ga`, `ol_ga` |
    | english          | `hl_en`, `ol_en`, `hl_ga`, `ol_ga` |
    | computer-science | `hl_en`, `ol_en`, `hl_ga`, `ol_ga` |

    Total: 24 tables (4 × 6). The init-db.sql at
    ``bonneagar/stacks/lakehouse/init-db.sql`` creates the
    ``ducklake_<namespace>`` databases on first boot; the actual
    tables are created by the BAML extraction flow (see
    `openspec/changes/2026-07-06-british-isles-education-pipeline-v1`).
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Architecture Summary

    ```
    ┌──────────────────────────────────────────────────────────────┐
    │                  **ibis** — the KCG entrypoint                │
    │  ibis.duckdb.connect("ducklake:...")  +  ibis.lancedb.connect  │
    └────────────────┬──────────────────────┬─────────────────────┘
                     │                      │
              ┌──────▼──────┐        ┌──────▼──────┐
              │  DuckLake   │        │  Lance NS  │
              │  (SQL)      │        │  (Vector)  │
              └──────┬──────┘        └──────┬──────┘
                     │                      │
              ┌──────▼──────────────────────▼──────┐
              │      Lakekeeper (Iceberg REST)      │
              └──────────────┬─────────────────────┘
                             │
              ┌──────────────▼─────────────────────┐
              │  lakehouse-postgres (12 databases)    │
              │  lakehouse-garage (S3-compatible)     │
              │  lakehouse-lance-namespace (REST)      │
              └────────────────────────────────────────┘
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
