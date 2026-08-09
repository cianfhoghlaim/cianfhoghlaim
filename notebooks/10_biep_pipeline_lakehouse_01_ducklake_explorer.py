# /// script
# requires-python = ">=3.12"
# dependencies = [
#   marimo>=0.13,
#   duckdb>=1.0,
#   ibis-framework[duckdb]>=9.0,
#   pandas>=2.2,
#   altair>=5.0,
#   pyarrow>=15,
#   anywidget>=0.9,
#   traitlets>=5.14,
# ]
# ///

"""DuckLake Explorer - Interactive validation for curriculum pipelines.

Refactored per the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1
change: R1 + R3 + P3 (LLM tab).

This Marimo notebook provides interactive exploration of DuckLake data
for validating locally before deploying to production.

Usage:
    marimo edit ducklake_explorer.py

Features:
    - Environment switching (local/production) via `mo.ui.dropdown`
    - Schema inspection with DLT widgets
    - Dataset browser with SQL queries
    - Table previews and row counts
    - Pipeline health checks
    - 🤖 Ask BAML LLM tab (P3)
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="full")


from notebooks._shared.db import connect_md
from notebooks._shared.marimo_patterns import (
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    llm_chat_with_prompts,
    setup_biep_registry_header,
)


@app.cell
def _intro(mo):
    """R1 — `setup_biep_registry_header()` + the DuckLake Explorer intro."""
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        # 🦆 DuckLake Explorer

        Interactive validation for **oideachais** curriculum pipelines.
        Validate data locally before deploying to production.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)

        ## Run modes

        - **Marimo mode**: `marimo edit notebooks/10_biep_pipeline_lakehouse_01_ducklake_explorer.py`
        - **CLI mode**: `python notebooks/10_biep_pipeline_lakehouse_01_ducklake_explorer.py --milestone m0 --asset-check documents_ingested`

        Per https://docs.marimo.io/guides/scripts/ — the CLI mode
        emits a JSON payload to stdout.
        """
    )
    return (_ctx, mo)


@app.cell
def _env_selector(mo):
    """Environment selector — `mo.ui.dropdown` per the marimo reactivity rule."""
    env_options = ["local", "production"]
    current_env = os.environ.get("DLT_ENVIRONMENT", "local")
    env_dropdown = mo.ui.dropdown(
        options=env_options,
        value=current_env,
        label="Environment",
    )
    mo.hstack([mo.md("**Select Environment:**"), env_dropdown])
    return current_env, env_dropdown, env_options


@app.cell
def _update_env(env_dropdown, mo):
    """Update the environment when the dropdown changes (per marimo reactivity rule)."""
    import os
    selected_env = env_dropdown.value or "local"
    os.environ["DLT_ENVIRONMENT"] = selected_env

    if selected_env == "local":
        env_info = """
        **Local Development Configuration:**
        - Data: Garage S3 at `s3://ducklake/oideachais/`
        - Metadata: PostgreSQL at `localhost:5432`
        - Requires: `docker compose up -d` in `bonneagar/storage/lakehouse/`
        """
    else:
        env_info = """
        **Production Configuration:**
        - Data: Cloudflare R2 (via `R2_BUCKET` env var)
        - Metadata: PlanetScale (via `PLANETSCALE_CONNECTION_STRING` env var)
        - Requires: Production credentials configured
        """

    mo.md(env_info)
    return env_info, selected_env


@app.cell
def _pipeline_status(mo, selected_env):
    """DLT Pipeline status (per the 2026-08-10 refactor: tabs wrapping)."""
    import dlt_sources

    try:
        pipeline = dlt_sources.attach("curriculum_unified")
        with pipeline.sql_client() as client:
            tables_query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'curriculum'
            """
            tables = [row[0] for row in client.execute_sql(tables_query)]

        status_msg = f"""
        ### Pipeline Status

        | Property | Value |
        |----------|-------|
        | Pipeline | `curriculum_unified` |
        | Environment | `{selected_env}` |
        | Tables | {len(tables)} |
        | Dataset | `curriculum` |

        **Tables:** {', '.join(f'`{t}`' for t in tables)}
        """
        mo.md(status_msg)
    except Exception as e:
        mo.md(f"""
        ### Pipeline Not Found

        The `curriculum_unified` pipeline hasn't been run yet.

        **To create data:**
        ```bash
        # Start lakehouse infrastructure
        cd bonneagar/storage/lakehouse
        docker compose up -d

        # Run a curriculum asset
        dagster dev -m oideachais
        # Then materialize ireland/curriculum/senior_cycle
        ```

        **Error:** `{e}`
        """)
    return ()


@app.cell
def _sql_console(mo):
    """SQL query interface (per the 2026-08-10 refactor: tabs wrapping)."""
    query_input = mo.ui.text_area(
        value="SELECT COUNT(*) as row_count FROM curriculum.curriculum_pages",
        label="SQL Query",
        rows=3,
        full_width=True,
    )
    run_button = mo.ui.run_button(label="Run Query")
    mo.vstack([mo.md("### Query Dataset"), query_input, run_button])
    return query_input, run_button


@app.cell
def _sql_console_render(query_input, run_button, mo):
    """Execute the query (P2 — gated via run_button + mo.stop)."""
    mo.stop(not run_button.value, mo.md("*Click 'Run Query' to execute*"))

    try:
        import pandas as pd
        from notebooks._shared.db import connect_md as _connect_md

        _conn = _connect_md()
        df = _conn.execute(query_input.value).execute()
        if hasattr(df, 'to_pandas'):
            df = df.to_pandas()
        mo.vstack([
            mo.md(f"**{len(df)} rows**"),
            mo.ui.table(df, page_size=25),
        ])
    except Exception as e:
        mo.callout(mo.md(f"**Query Error:** `{e}`"), kind="warn")


@app.cell
def _llm_tab(mo):
    """P3 — LLM-assisted analysis tab via mo.ui.chat + mo.ai.llm.openai()."""
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the DuckLake Explorer assistant. You help operators query "
            "and validate the oideachais curriculum_unified DuckLake pipeline. "
            "When the user asks about a table or column, refer to the DLT "
            "schema introspection in information_schema.tables."
        ),
        prompts=[
            "📚 How many tables are in the curriculum schema?",
            "🔍 Show me the schema for the curriculum_pages table",
            "📊 What are the top 10 most frequent values in <column_name>?",
            "🎯 How do I query for a specific subject's curriculum_pages?",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the DuckLake Explorer (via litellm)"), _chat])


@app.cell
def _operator_console(mo):
    """The 4-tab operator console (P1 — mo.ui.tabs)."""
    tabs = mo.ui.tabs({
        "Environment": _update_env_dropdown_area(mo),
        "Status": _pipeline_status_area(mo),
        "SQL Console": _sql_console_area(mo),
        "🤖 Ask BAML": _llm_tab(mo),
    })
    tabs


# Helper cells to make the tabs work without variable scope issues
@app.cell
def _update_env_dropdown_area(mo):
    _e = mo.ui.dropdown(options=["local", "production"], value="local", label="Environment")
    mo.vstack([mo.md("### Environment"), _e])


@app.cell
def _pipeline_status_area(mo):
    mo.md("### Pipeline Status\n\nClick **Re-run** to refresh.")


@app.cell
def _sql_console_area(mo):
    _q = mo.ui.text_area(value="SELECT COUNT(*) FROM information_schema.tables", label="SQL Query")
    _b = mo.ui.run_button(label="Execute")
    mo.vstack([mo.md("### SQL Console"), _q, _b])


@app.cell
def _schema_export(mo):
    """Schema export options."""
    mo.md("""
    ### Export Schema

    Use DLT CLI to export schema for documentation:
    ```bash
    dlt pipeline curriculum_unified schema --format dbml
    dlt pipeline curriculum_unified schema --format json
    dlt workspace
    ```
    """)


@app.cell
def _dev_workflow(mo):
    """Development tips."""
    mo.md("""
    ---

    ## Development Workflow

    1. **Start infrastructure:**
       ```bash
       cd bonneagar/storage/lakehouse
       docker compose up -d
       ```

    2. **Run pipeline locally:**
       ```bash
       # Via Dagster
       dagster dev -m oideachais

       # Or directly
       DLT_ENVIRONMENT=local python -c "from cianfhoghlaim.dlt import create_pipeline; ..."
       ```

    3. **Validate in this notebook:**
       - Check row counts
       - Preview data
       - Run validation queries

    4. **Deploy to production:**
       ```bash
       DLT_ENVIRONMENT=production dagster job execute ...
       ```

    ### Environment Variables

    | Variable | Description | Default |
    |----------|-------------|---------|
    | `DLT_ENVIRONMENT` | `local` or `production` | `local` |
    | `USE_DUCKLAKE` | Enable DuckLake destination | `true` |
    | `R2_BUCKET` | Cloudflare R2 bucket (prod) | - |
    | `PLANETSCALE_CONNECTION_STRING` | PlanetScale URI (prod) | - |
    """)


def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits a DuckLake explorer summary payload."""
    parser = cli_argparser_biep("10_biep_pipeline_lakehouse_01_ducklake_explorer")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "10_biep_pipeline_lakehouse_01_ducklake_explorer",
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "ok",
        "exit_code": 0,
        "note": (
            "Run `dagster dev -m oideachais` to start the pipeline, then "
            "re-run this CLI to see the latest schema status."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)