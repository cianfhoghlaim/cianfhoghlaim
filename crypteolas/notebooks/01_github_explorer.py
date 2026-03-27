# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "dlt[duckdb]>=1.18.2",
#     "ibis-framework[duckdb]>=11.0.0",
#     "python-dotenv",
#     "altair>=5.0.0",
# ]
# ///
"""GitHub API Explorer - Interactive DLT Pipeline Notebook.

This marimo notebook demonstrates:
1. Running DLT pipelines to ingest GitHub API data
2. Exploring data with ibis + DuckDB
3. Creating interactive visualizations

Usage:
    marimo edit crypteolas/notebooks/01_github_explorer.py
"""
import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # GitHub API Explorer

    This notebook demonstrates how to use **dlt** to ingest data from the GitHub REST API,
    then explore and analyze it with **ibis** and **DuckDB**.

    ## Prerequisites

    1. Set up your GitHub token in environment or `.dlt/secrets.toml`:
    ```bash
    export GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxx
    ```

    2. Install dependencies:
    ```bash
    uv sync
    ```
    """)
    return


@app.cell
def _():
    import marimo as mo
    import os
    from pathlib import Path

    # Change to project root if running from notebooks dir
    project_root = Path(__file__).parent.parent if "__file__" in dir() else Path.cwd().parent
    if (project_root / "pyproject.toml").exists():
        os.chdir(project_root)

    return mo, os, Path, project_root


@app.cell
def _():
    from dotenv import load_dotenv
    load_dotenv()
    return (load_dotenv,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Configuration

    Select a GitHub repository to analyze:
    """)
    return


@app.cell
def _(mo):
    owner_input = mo.ui.text(value="ethena-labs", label="Owner")
    repo_input = mo.ui.text(value="ethena", label="Repository")

    resources_select = mo.ui.multiselect(
        options=["issues", "pull_requests", "commits", "workflow_runs", "contributors"],
        value=["issues", "pull_requests"],
        label="Resources to fetch"
    )

    mo.hstack([owner_input, repo_input])
    return owner_input, repo_input, resources_select


@app.cell
def _(resources_select):
    resources_select
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Run the Pipeline

    Click the button below to ingest data from GitHub into DuckDB.
    """)
    return


@app.cell
def _(mo, owner_input, repo_input, resources_select):
    run_button = mo.ui.run_button(label="Run Pipeline")
    run_button
    return (run_button,)


@app.cell
def _(mo, owner_input, repo_input, resources_select, run_button):
    import dlt
    from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources

    load_info = None
    pipeline = None

    if run_button.value:
        mo.status.spinner(title="Running pipeline...")

        owner = owner_input.value
        repo = repo_input.value
        resources = resources_select.value

        # Build resource configurations
        resource_configs = []

        if "issues" in resources:
            resource_configs.append({
                "name": "issues",
                "endpoint": {
                    "path": f"repos/{owner}/{repo}/issues",
                    "params": {"per_page": 100, "state": "all"},
                    "paginator": {"type": "header_link"},
                },
            })

        if "pull_requests" in resources:
            resource_configs.append({
                "name": "pull_requests",
                "endpoint": {
                    "path": f"repos/{owner}/{repo}/pulls",
                    "params": {"per_page": 100, "state": "all"},
                    "paginator": {"type": "header_link"},
                },
            })

        if "commits" in resources:
            resource_configs.append({
                "name": "commits",
                "endpoint": {
                    "path": f"repos/{owner}/{repo}/commits",
                    "params": {"per_page": 100},
                    "paginator": {"type": "header_link"},
                },
                "primary_key": "sha",
            })

        if "workflow_runs" in resources:
            resource_configs.append({
                "name": "workflow_runs",
                "endpoint": {
                    "path": f"repos/{owner}/{repo}/actions/runs",
                    "params": {"per_page": 100},
                    "data_selector": "workflow_runs",
                    "paginator": {"type": "header_link"},
                },
            })

        if "contributors" in resources:
            resource_configs.append({
                "name": "contributors",
                "endpoint": {
                    "path": f"repos/{owner}/{repo}/contributors",
                    "params": {"per_page": 100},
                    "paginator": {"type": "header_link"},
                },
            })

        # Get token from environment
        import os
        access_token = os.environ.get("GITHUB_ACCESS_TOKEN", "")

        config: RESTAPIConfig = {
            "client": {
                "base_url": "https://api.github.com",
                "auth": {"type": "bearer", "token": access_token},
                "headers": {"Accept": "application/vnd.github.v3+json"},
            },
            "resources": resource_configs,
            "resource_defaults": {
                "primary_key": "id",
                "write_disposition": "merge",
            },
        }

        @dlt.source(name="github_api")
        def github_source():
            yield from rest_api_resources(config)

        pipeline = dlt.pipeline(
            pipeline_name=f"github_{owner}_{repo}",
            destination="duckdb",
            dataset_name="github_data",
        )

        load_info = pipeline.run(github_source())

    load_info, pipeline
    return dlt, RESTAPIConfig, rest_api_resources, load_info, pipeline


@app.cell
def _(load_info, mo):
    if load_info:
        mo.md(f"""
        ## Load Results

        **Pipeline:** `{load_info.pipeline.pipeline_name}`

        **Destination:** `{load_info.destination_type}`

        **Dataset:** `{load_info.dataset_name}`
        """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Explore with Ibis

    Now let's explore the loaded data using ibis for composable queries.
    """)
    return


@app.cell
def _(pipeline, mo):
    import ibis

    # Connect to the DuckDB database
    if pipeline:
        db_path = f"./{pipeline.pipeline_name}.duckdb"
        con = ibis.duckdb.connect(db_path, read_only=True)
        tables = con.list_tables()
        mo.md(f"**Available tables:** {', '.join(tables)}")
    else:
        con = None
        tables = []

    con, tables
    return ibis, con, tables


@app.cell
def _(con, tables, mo):
    if con and "github_data___issues" in tables:
        issues = con.table("github_data___issues")
        mo.ui.table(issues.limit(10).execute())
    elif con and "issues" in tables:
        issues = con.table("issues")
        mo.ui.table(issues.limit(10).execute())
    else:
        issues = None
        mo.md("*No issues table found. Run the pipeline first.*")
    return (issues,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Issue Analytics

    Let's create some analytics on the issues data.
    """)
    return


@app.cell
def _(con, issues, mo):
    if issues is not None:
        # Issues by state
        by_state = issues.group_by("state").aggregate(count=issues.id.count())
        mo.ui.table(by_state.execute())
    return (by_state,)


@app.cell
def _(issues, mo):
    import altair as alt

    if issues is not None:
        # Get data for visualization
        df = issues.select("state", "created_at").execute()
        df["month"] = df["created_at"].dt.to_period("M").astype(str)

        monthly_counts = df.groupby(["month", "state"]).size().reset_index(name="count")

        chart = alt.Chart(monthly_counts).mark_bar().encode(
            x=alt.X("month:O", title="Month"),
            y=alt.Y("count:Q", title="Issues"),
            color="state:N",
            tooltip=["month", "state", "count"]
        ).properties(
            title="Issues by Month and State",
            width=600,
            height=300
        )

        mo.ui.altair_chart(chart)
    return alt,


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## SQL Queries

    You can also run raw SQL queries against the DuckDB database:
    """)
    return


@app.cell
def _(con, mo):
    sql_input = mo.ui.text_area(
        value="SELECT state, COUNT(*) as count FROM github_data___issues GROUP BY state",
        label="SQL Query",
        rows=3,
    )
    sql_input
    return (sql_input,)


@app.cell
def _(con, sql_input, mo):
    if con:
        try:
            result = con.raw_sql(sql_input.value).fetch_arrow_table().to_pandas()
            mo.ui.table(result)
        except Exception as e:
            mo.md(f"*Error: {e}*")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Next Steps

    - **Code Search**: Run `02_code_search.py` to explore semantic code search with LanceDB
    - **Knowledge Graph**: Run `03_knowledge_graph.py` to build and query knowledge graphs
    - **DeFi Dashboard**: Run `04_defi_dashboard.py` for DeFi analytics

    ## Resources

    - [dlt Documentation](https://dlthub.com/docs)
    - [Ibis Documentation](https://ibis-project.org/docs)
    - [Marimo Documentation](https://docs.marimo.io)
    """)
    return


if __name__ == "__main__":
    app.run()
