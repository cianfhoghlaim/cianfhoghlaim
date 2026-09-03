# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "dlt[lancedb]>=1.0.0",
#     "lancedb>=0.24.0",
#     "polars>=1.0.0",
#     "altair>=5.0.0",
#     "pandas>=2.0.0",
#     "python-dotenv>=1.0.0",
#     "requests>=2.31.0",
#     "rerankers[flashrank]>=0.5.0",
# ]
# ///

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # DLT + LanceDB: Data Pipelines with Vector Search

        This notebook demonstrates how to build data pipelines using **dlt** (data load tool)
        with **LanceDB** as a vector database destination. It showcases:

        1. **DLT Pipeline Patterns** - Incremental loading, REST API sources, schema evolution
        2. **LanceDB Vector Storage** - Embedding columns, hybrid search, index creation
        3. **Data Transformations** - Cleaning, mapping, and enriching data before load
        4. **Interactive Search** - Full-text + vector hybrid search with reranking

        > Based on patterns from the hackathon examples in `/data/examples/dlt/`
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    import os
    from dotenv import load_dotenv

    load_dotenv()
    return mo, os, load_dotenv


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 1. DLT Pipeline Configuration

        DLT pipelines consist of three main components:
        - **Source**: Where data comes from (REST API, database, files)
        - **Pipeline**: Orchestrates extraction, normalization, and loading
        - **Destination**: Where data goes (LanceDB, DuckDB, BigQuery, etc.)
        """
    )
    return


@app.cell
def _(mo, os):
    # Configuration inputs for GitHub API
    github_owner = mo.ui.text(
        value="anthropics",
        label="GitHub Owner",
        placeholder="e.g., anthropics"
    )
    github_repo = mo.ui.text(
        value="anthropic-cookbook",
        label="GitHub Repository",
        placeholder="e.g., anthropic-cookbook"
    )

    mo.hstack([github_owner, github_repo], justify="start")
    return github_owner, github_repo


@app.cell
def _():
    import dlt
    from dlt.sources.rest_api import RESTAPIConfig, rest_api_source
    from dlt.destinations.adapters import lancedb_adapter
    return dlt, RESTAPIConfig, rest_api_source, lancedb_adapter


@app.cell
def _(RESTAPIConfig, github_owner, github_repo, rest_api_source):
    def make_github_issues_source(owner: str, repo: str):
        """
        Create a DLT REST API source for GitHub issues.

        Uses incremental loading to only fetch new/updated issues since last run.
        """
        config: RESTAPIConfig = {
            "client": {
                "base_url": "https://api.github.com",
                "headers": {
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                "paginator": "header_link",  # GitHub uses Link header for pagination
            },
            "resources": [
                {
                    "name": "issues",
                    "endpoint": {
                        "path": f"repos/{owner}/{repo}/issues",
                        "params": {
                            "state": "all",
                            "sort": "updated",
                            "direction": "desc",
                            "per_page": 100
                        },
                        "incremental": {
                            "cursor_path": "updated_at",
                            "initial_value": "2024-01-01T00:00:00Z"
                        }
                    }
                },
            ]
        }
        return rest_api_source(config)

    # Create source with current config
    github_source = make_github_issues_source(
        github_owner.value,
        github_repo.value
    )
    return make_github_issues_source, github_source


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 2. Data Transformation

        Before loading to LanceDB, we clean and transform the data:
        - Strip HTML tags from issue bodies
        - Create clean text fields for embedding
        - Merge title and description for better search
        """
    )
    return


@app.cell
def _():
    import re
    import html

    def clean_text(text: str) -> str:
        """Clean HTML and markdown from text for embedding."""
        if not text:
            return ""
        # Decode HTML entities
        text = html.unescape(text)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove markdown code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        # Remove inline code
        text = re.sub(r'`[^`]+`', '', text)
        # Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        return text.strip()

    def transform_issue(record, meta=None):
        """
        Transform GitHub issue for embedding.
        Creates a clean_content field combining title and body.
        """
        title = record.get('title', '')
        body = record.get('body', '') or ''

        clean_body = clean_text(body)
        record["clean_content"] = f"Title: {title}\n\nDescription: {clean_body}"
        record["clean_body"] = clean_body

        return record

    return clean_text, transform_issue, re, html


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 3. LanceDB Pipeline Execution

        Now we create a DLT pipeline with LanceDB as the destination.
        The `lancedb_adapter` specifies which columns to embed.
        """
    )
    return


@app.cell
def _(dlt, github_owner, github_repo, github_source, lancedb_adapter, transform_issue, mo):
    # Create pipeline
    pipeline = dlt.pipeline(
        pipeline_name=f'github_issues_{github_owner.value}_{github_repo.value}',
        destination='lancedb',
        dataset_name='github_data',
    )

    # Columns to embed for vector search
    embed_cols = ["clean_content"]

    # Show pipeline info
    mo.md(f"""
    **Pipeline Configuration:**
    - Name: `{pipeline.pipeline_name}`
    - Destination: `lancedb`
    - Dataset: `github_data`
    - Embedding columns: `{embed_cols}`
    """)
    return pipeline, embed_cols


@app.cell
def _(mo):
    run_pipeline_btn = mo.ui.run_button(label="Run DLT Pipeline")
    run_pipeline_btn
    return run_pipeline_btn,


@app.cell
def _(embed_cols, github_source, lancedb_adapter, mo, pipeline, run_pipeline_btn, transform_issue):
    load_info = None

    if run_pipeline_btn.value:
        with mo.status.spinner(title="Running DLT pipeline..."):
            # Add transformation and run pipeline
            load_info = pipeline.run([
                lancedb_adapter(
                    github_source.issues.add_map(transform_issue),
                    embed=embed_cols
                ),
            ])

        mo.md(f"""
        **Pipeline completed!**

        ```
        {load_info}
        ```
        """)
    else:
        mo.md("*Click 'Run DLT Pipeline' to load data*")
    return load_info,


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 4. LanceDB Search Interface

        LanceDB supports multiple search types:
        - **Vector search**: Semantic similarity using embeddings
        - **Full-text search**: Keyword matching with Tantivy
        - **Hybrid search**: Combines both with reranking
        """
    )
    return


@app.cell
def _():
    import lancedb
    from lancedb.rerankers import RRFReranker
    return lancedb, RRFReranker


@app.cell
def _(lancedb, pipeline):
    # Connect to the LanceDB created by DLT
    db_path = f".lancedb/{pipeline.pipeline_name}"

    try:
        db = lancedb.connect(db_path)
        tables = db.table_names()
        print(f"Connected to LanceDB at: {db_path}")
        print(f"Available tables: {tables}")
    except Exception as e:
        db = None
        tables = []
        print(f"LanceDB not yet initialized. Run the pipeline first. Error: {e}")

    return db, db_path, tables


@app.cell
def _(db, mo, tables):
    # Table selector
    table_selector = mo.ui.dropdown(
        options=tables if tables else ["issues"],
        value=tables[0] if tables else "issues",
        label="Select Table"
    )

    search_input = mo.ui.text_area(
        label="Search Query",
        placeholder="Enter your search query...",
        value="How to use Claude API for function calling?"
    )

    search_type = mo.ui.dropdown(
        options=["hybrid", "vector", "fts"],
        value="hybrid",
        label="Search Type"
    )

    limit_slider = mo.ui.slider(
        start=5, stop=50, step=5, value=10,
        label="Result Limit"
    )

    mo.vstack([
        mo.hstack([table_selector, search_type, limit_slider]),
        search_input
    ])
    return table_selector, search_input, search_type, limit_slider


@app.cell
def _(mo):
    search_btn = mo.ui.run_button(label="Search")
    search_btn
    return search_btn,


@app.cell
def _(RRFReranker, db, limit_slider, mo, search_btn, search_input, search_type, table_selector):
    import polars as pl

    search_results = None

    if search_btn.value and db:
        try:
            table = db.open_table(f"github_data___{table_selector.value}")

            query = search_input.value
            limit = limit_slider.value

            with mo.status.spinner(title="Searching..."):
                if search_type.value == "hybrid":
                    # Create FTS index if not exists
                    try:
                        table.create_fts_index(['clean_content'], replace=True, use_tantivy=True)
                    except:
                        pass  # Index may already exist

                    search_results = (
                        table.search(query, query_type='hybrid')
                        .select(['url', 'html_url', 'number', 'title', 'clean_body', 'state'])
                        .rerank(reranker=RRFReranker())
                        .limit(limit)
                        .to_polars()
                    )
                elif search_type.value == "vector":
                    search_results = (
                        table.search(query, query_type='vector')
                        .select(['url', 'html_url', 'number', 'title', 'clean_body', 'state'])
                        .limit(limit)
                        .to_polars()
                    )
                else:  # fts
                    try:
                        table.create_fts_index(['clean_content'], replace=True, use_tantivy=True)
                    except:
                        pass
                    search_results = (
                        table.search(query, query_type='fts')
                        .select(['url', 'html_url', 'number', 'title', 'clean_body', 'state'])
                        .limit(limit)
                        .to_polars()
                    )

            mo.md(f"**Found {len(search_results)} results**")
        except Exception as e:
            mo.md(f"**Error:** {e}")
    else:
        mo.md("*Run the pipeline first, then search*")

    return search_results, pl


@app.cell
def _(mo, search_results):
    if search_results is not None and len(search_results) > 0:
        mo.ui.table(search_results.to_pandas(), selection=None)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 5. Visualize Issue Statistics

        Using Ibis and Altair to analyze the loaded GitHub issues.
        """
    )
    return


@app.cell
def _(db, table_selector):
    import altair as alt
    import pandas as pd

    if db:
        try:
            table = db.open_table(f"github_data___{table_selector.value}")
            df_stats = table.to_polars().to_pandas()

            # State distribution
            state_counts = df_stats['state'].value_counts().reset_index()
            state_counts.columns = ['state', 'count']

            chart = alt.Chart(state_counts).mark_bar().encode(
                x=alt.X('state:N', title='Issue State'),
                y=alt.Y('count:Q', title='Count'),
                color='state:N'
            ).properties(
                title='GitHub Issues by State',
                width=400,
                height=300
            )
            chart
        except Exception as e:
            print(f"Could not create visualization: {e}")
    return alt, pd, df_stats, state_counts, chart


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Key Patterns Demonstrated

        ### DLT Pipeline Patterns
        ```python
        # 1. Create REST API source with incremental loading
        config: RESTAPIConfig = {
            "client": {"base_url": "...", "paginator": "header_link"},
            "resources": [{
                "name": "issues",
                "endpoint": {
                    "path": "repos/{owner}/{repo}/issues",
                    "incremental": {"cursor_path": "updated_at"}
                }
            }]
        }

        # 2. Transform data before loading
        source.issues.add_map(transform_function)

        # 3. Use lancedb_adapter for embeddings
        lancedb_adapter(source.issues, embed=["column1", "column2"])

        # 4. Run pipeline
        pipeline.run([adapted_source])
        ```

        ### LanceDB Search Patterns
        ```python
        # Vector search
        table.search(query, query_type='vector').limit(10).to_polars()

        # Full-text search (requires FTS index)
        table.create_fts_index(['col1'], use_tantivy=True)
        table.search(query, query_type='fts').limit(10).to_polars()

        # Hybrid search with reranking
        table.search(query, query_type='hybrid')
            .rerank(reranker=RRFReranker())
            .limit(10).to_polars()
        ```
        """
    )
    return


if __name__ == "__main__":
    app.run()
