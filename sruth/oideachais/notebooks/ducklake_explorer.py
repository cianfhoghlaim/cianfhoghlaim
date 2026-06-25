"""
DuckLake Explorer - Interactive validation for curriculum pipelines.

This Marimo notebook provides interactive exploration of DuckLake data
for validating locally before deploying to production.

Usage:
    # Local development
    marimo edit ducklake_explorer.py

    # Or run as app
    marimo run ducklake_explorer.py

Features:
    - Environment switching (local/production)
    - Schema inspection with DLT widgets
    - Dataset browser with SQL queries
    - Table previews and row counts
    - Pipeline health checks
"""

import marimo

__generated_with = "0.10.14"
app = marimo.App(width="medium")


@app.cell
def _():
    """Setup and imports."""
    import os

    import marimo as mo

    mo.md("""
    # DuckLake Explorer

    Interactive validation for **oideachais** curriculum pipelines.

    Validate data locally before deploying to production.
    """)
    return mo, os


@app.cell
def _(mo, os):
    """Environment selector."""
    # Environment dropdown
    env_options = ["local", "production"]
    current_env = os.environ.get("DLT_ENVIRONMENT", "local")

    env_dropdown = mo.ui.dropdown(
        options=env_options,
        value=current_env,
        label="Environment",
    )

    mo.hstack([
        mo.md("**Select Environment:**"),
        env_dropdown,
    ])
    return current_env, env_dropdown, env_options


@app.cell
def _(env_dropdown, mo, os):
    """Update environment when changed."""
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
def _(mo, selected_env):
    """DLT Pipeline status."""
    import dlt

    try:
        # Get pipeline info
        pipeline = dlt.attach("curriculum_unified")

        # Get dataset info
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
    return client, dlt, pipeline, status_msg, tables, tables_query


@app.cell
def _(mo):
    """SQL query interface."""
    query_input = mo.ui.text_area(
        value="SELECT COUNT(*) as row_count FROM curriculum.curriculum_pages",
        label="SQL Query",
        rows=3,
        full_width=True,
    )

    run_button = mo.ui.run_button(label="Run Query")

    mo.vstack([
        mo.md("### Query Dataset"),
        query_input,
        run_button,
    ])
    return query_input, run_button


@app.cell
def _(mo, pipeline, query_input, run_button):
    """Execute query and show results."""
    mo.stop(not run_button.value, mo.md("*Click 'Run Query' to execute*"))

    try:
        with pipeline.sql_client() as client:
            with client.execute_query(query_input.value) as cursor:
                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = cursor.fetchall()

        if rows:
            # Create table from results
            import pandas as pd

            df = pd.DataFrame(rows, columns=columns)
            mo.ui.table(df)
        else:
            mo.md("*No results returned*")

    except Exception as e:
        mo.md(f"**Query Error:** `{e}`")
    return client, columns, df, pd, result, rows


@app.cell
def _(mo):
    """Preview table selector."""
    table_select = mo.ui.dropdown(
        options=["curriculum_pages", "_dlt_loads", "_dlt_version"],
        value="curriculum_pages",
        label="Table to Preview",
    )

    preview_limit = mo.ui.slider(
        start=5,
        stop=100,
        value=10,
        step=5,
        label="Row Limit",
    )

    mo.hstack([
        mo.md("### Table Preview"),
        table_select,
        preview_limit,
    ])
    return preview_limit, table_select


@app.cell
def _(mo, pipeline, preview_limit, table_select):
    """Show table preview."""
    try:
        import pandas as pd

        table_name = table_select.value
        limit = preview_limit.value

        with pipeline.sql_client() as client:
            query = f"SELECT * FROM curriculum.{table_name} LIMIT {limit}"
            with client.execute_query(query) as cursor:
                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = cursor.fetchall()

        if rows:
            df = pd.DataFrame(rows, columns=columns)
            mo.ui.table(df)
        else:
            mo.md(f"*Table `{table_name}` is empty*")

    except Exception as e:
        mo.md(f"**Error:** `{e}`")
    return client, columns, df, limit, pd, query, result, rows, table_name


@app.cell
def _(mo):
    """Schema export options."""
    mo.md("""
    ### Export Schema

    Use DLT CLI to export schema for documentation:

    ```bash
    # Export to DBML (for dbdiagram.io)
    dlt pipeline curriculum_unified schema --format dbml

    # Export to JSON
    dlt pipeline curriculum_unified schema --format json

    # View in dashboard
    dlt workspace
    ```
    """)
    return ()


@app.cell
def _(mo):
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
       DLT_ENVIRONMENT=local python -c "from oideachais.dlt_utils import create_pipeline; ..."
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
    return ()


if __name__ == "__main__":
    app.run()
