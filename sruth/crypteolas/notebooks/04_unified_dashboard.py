# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "dlt[duckdb]>=1.18.2",
#     "ibis-framework[duckdb]>=11.0.0",
#     "lancedb>=0.6.0",
#     "neo4j",
#     "sentence-transformers",
#     "python-dotenv",
#     "altair>=5.0.0",
#     "pandas",
# ]
# ///
"""Unified Dashboard - Combined GitHub Intelligence Analytics.

This marimo notebook provides a unified view of:
1. GitHub API data (DuckDB) - Issues, PRs, commits, workflows
2. Code search (LanceDB) - Semantic code search
3. Knowledge graph (Memgraph) - Entity relationships

Usage:
    marimo edit notebooks/04_unified_dashboard.py
"""
import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # GitHub Intelligence Dashboard

    A unified view of your GitHub data across three dimensions:

    | Data Source | Storage | Purpose |
    |-------------|---------|---------|
    | **GitHub API** | DuckDB | Issues, PRs, commits, workflows |
    | **Code Index** | LanceDB | Semantic code search |
    | **Knowledge Graph** | Memgraph | Entity relationships |

    ---
    """)
    return


@app.cell
def _():
    import marimo as mo
    import os
    from pathlib import Path

    project_root = Path(__file__).parent.parent if "__file__" in dir() else Path.cwd().parent
    if (project_root / "pyproject.toml").exists():
        os.chdir(project_root)

    return mo, os, Path, project_root


@app.cell
def _():
    from dotenv import load_dotenv
    load_dotenv("config/.env")
    return (load_dotenv,)


@app.cell
def _(mo):
    # Tabs for different views
    tabs = mo.ui.tabs({
        "Overview": "overview",
        "GitHub API": "api",
        "Code Search": "code",
        "Knowledge Graph": "graph",
    })
    tabs
    return (tabs,)


# ============================================================================
# OVERVIEW TAB
# ============================================================================

@app.cell
def _(mo, tabs):
    if tabs.value == "overview":
        mo.md(r"""
        ## Data Sources Overview

        This dashboard integrates three data sources for comprehensive GitHub intelligence:

        ### 1. GitHub REST API (DuckDB)
        - **What**: Issues, pull requests, commits, workflow runs
        - **How**: DLT pipelines with RESTAPIConfig
        - **Storage**: Local DuckDB or Motherduck

        ### 2. Code Index (LanceDB)
        - **What**: Chunked code with semantic embeddings
        - **How**: CocoIndex with tree-sitter chunking
        - **Storage**: LanceDB vector database

        ### 3. Knowledge Graph (Memgraph)
        - **What**: Entities and relationships from docs
        - **How**: Cognee LLM extraction
        - **Storage**: Memgraph graph database
        """)
    return


@app.cell
def _(mo, tabs, Path):
    if tabs.value == "overview":
        # Show available data sources
        duckdb_files = list(Path(".").glob("*.duckdb"))
        lancedb_dirs = list(Path("./data").glob("*.lancedb")) if Path("./data").exists() else []

        mo.md(f"""
        ### Available Data

        **DuckDB Databases**: {', '.join(f.name for f in duckdb_files) or 'None found'}

        **LanceDB Databases**: {', '.join(d.name for d in lancedb_dirs) or 'None found'}

        *Run the individual notebooks to populate these data sources.*
        """)
    return


# ============================================================================
# GITHUB API TAB
# ============================================================================

@app.cell
def _(mo, tabs, Path):
    import ibis
    import pandas as pd
    import altair as alt

    if tabs.value == "api":
        # Find available DuckDB files
        duckdb_files = list(Path(".").glob("*.duckdb"))

        if duckdb_files:
            db_selector = mo.ui.dropdown(
                options=[f.name for f in duckdb_files],
                value=duckdb_files[0].name if duckdb_files else None,
                label="Select database",
            )
            mo.vstack([
                mo.md("## GitHub API Analytics"),
                db_selector,
            ])
        else:
            mo.md("*No DuckDB databases found. Run `01_github_api_explorer.py` first.*")

    return ibis, pd, alt


@app.cell
def _(mo, tabs, ibis, pd, alt, Path):
    if tabs.value == "api":
        duckdb_files = list(Path(".").glob("*.duckdb"))

        if duckdb_files:
            db_path = duckdb_files[0]
            con = ibis.duckdb.connect(str(db_path), read_only=True)
            tables = con.list_tables()

            mo.md(f"**Tables**: {', '.join(tables)}")

            # Show issues summary if available
            issues_tables = [t for t in tables if "issues" in t.lower()]
            if issues_tables:
                issues = con.table(issues_tables[0])
                df = issues.limit(100).execute()

                if "state" in df.columns:
                    state_counts = df["state"].value_counts().reset_index()
                    state_counts.columns = ["state", "count"]

                    chart = alt.Chart(state_counts).mark_arc().encode(
                        theta="count:Q",
                        color="state:N",
                        tooltip=["state", "count"]
                    ).properties(
                        title="Issues by State",
                        width=300,
                        height=300
                    )

                    mo.ui.altair_chart(chart)
    return


# ============================================================================
# CODE SEARCH TAB
# ============================================================================

@app.cell
def _(mo, tabs, Path):
    if tabs.value == "code":
        mo.md("## Semantic Code Search")

        # Find LanceDB databases
        lancedb_dirs = list(Path("./data").glob("*.lancedb")) if Path("./data").exists() else []

        if lancedb_dirs:
            mo.md(f"**Available indexes**: {', '.join(d.name for d in lancedb_dirs)}")
        else:
            mo.md("*No LanceDB indexes found. Run `02_code_search.py` first.*")
    return


@app.cell
def _(mo, tabs):
    if tabs.value == "code":
        code_query = mo.ui.text(
            value="how to create a pipeline",
            label="Search query",
            full_width=True,
        )
        code_query
    return


@app.cell
def _(mo, tabs, Path):
    if tabs.value == "code":
        search_button = mo.ui.run_button(label="Search Code")
        search_button
    return


@app.cell
def _(mo, tabs, Path):
    import sys
    sys.path.insert(0, str(Path.cwd()))

    if tabs.value == "code":
        lancedb_dirs = list(Path("./data").glob("*.lancedb")) if Path("./data").exists() else []

        if lancedb_dirs:
            import lancedb

            db = lancedb.connect(str(lancedb_dirs[0]))
            tables = db.table_names()

            mo.md(f"**Tables**: {', '.join(tables)}")
    return


# ============================================================================
# KNOWLEDGE GRAPH TAB
# ============================================================================

@app.cell
def _(mo, tabs, os):
    if tabs.value == "graph":
        mo.md("## Knowledge Graph Explorer")

        graph_uri = os.environ.get("GRAPH_DATABASE_URL", "bolt://localhost:7687")
        mo.md(f"**Memgraph URI**: {graph_uri}")
    return


@app.cell
def _(mo, tabs, os):
    if tabs.value == "graph":
        from neo4j import GraphDatabase

        graph_driver = None
        graph_stats = None

        try:
            uri = os.environ.get("GRAPH_DATABASE_URL", "bolt://localhost:7687")
            graph_driver = GraphDatabase.driver(uri)

            with graph_driver.session() as session:
                # Get stats
                node_result = session.run("""
                    MATCH (n)
                    RETURN labels(n)[0] as label, count(n) as count
                """)
                nodes = {r["label"]: r["count"] for r in node_result}

                edge_result = session.run("""
                    MATCH ()-[r]->()
                    RETURN type(r) as type, count(r) as count
                """)
                edges = {r["type"]: r["count"] for r in edge_result}

                graph_stats = {"nodes": nodes, "edges": edges}

        except Exception as e:
            mo.md(f"*Could not connect to Memgraph: {e}*")

        if graph_stats:
            total_nodes = sum(graph_stats["nodes"].values())
            total_edges = sum(graph_stats["edges"].values())

            mo.md(f"""
            ### Graph Statistics

            **Total Nodes**: {total_nodes}
            - {', '.join(f'{k}: {v}' for k, v in graph_stats['nodes'].items())}

            **Total Edges**: {total_edges}
            - {', '.join(f'{k}: {v}' for k, v in graph_stats['edges'].items())}
            """)
    return GraphDatabase, graph_driver, graph_stats


@app.cell
def _(mo, tabs, graph_driver, alt, pd):
    if tabs.value == "graph" and graph_driver:
        # Most connected entities
        with graph_driver.session() as session:
            result = session.run("""
                MATCH (e:Entity)-[r]-()
                RETURN e.value as entity, count(r) as connections
                ORDER BY connections DESC
                LIMIT 10
            """)
            top_entities = [dict(r) for r in result]

        if top_entities:
            df = pd.DataFrame(top_entities)

            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X("connections:Q", title="Connections"),
                y=alt.Y("entity:N", sort="-x", title="Entity"),
                color=alt.value("#6366f1"),
                tooltip=["entity", "connections"]
            ).properties(
                title="Top Connected Entities",
                width=400,
                height=250
            )

            mo.ui.altair_chart(chart)
    return


# ============================================================================
# CROSS-DATA INSIGHTS
# ============================================================================

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Cross-Data Insights

    Combining insights from all three data sources:
    """)
    return


@app.cell
def _(mo, Path, ibis, pd):
    # Try to combine insights
    insights = []

    # DuckDB insights
    duckdb_files = list(Path(".").glob("*.duckdb"))
    if duckdb_files:
        try:
            con = ibis.duckdb.connect(str(duckdb_files[0]), read_only=True)
            tables = con.list_tables()

            issues_tables = [t for t in tables if "issues" in t.lower()]
            if issues_tables:
                issues = con.table(issues_tables[0])
                count = issues.count().execute()
                insights.append(f"- **Issues tracked**: {count}")
        except:
            pass

    # LanceDB insights
    lancedb_dirs = list(Path("./data").glob("*.lancedb")) if Path("./data").exists() else []
    if lancedb_dirs:
        try:
            import lancedb
            db = lancedb.connect(str(lancedb_dirs[0]))
            tables = db.table_names()
            total_chunks = sum(db.open_table(t).count_rows() for t in tables)
            insights.append(f"- **Code chunks indexed**: {total_chunks}")
        except:
            pass

    if insights:
        mo.md("### Data Summary\n\n" + "\n".join(insights))
    else:
        mo.md("*Run the individual notebooks to populate data sources.*")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Quick Actions

    - **Refresh Data**: Re-run the individual notebooks to update data
    - **Export**: Use ibis/pandas to export data to CSV, Parquet, etc.
    - **Query**: Use SQL (DuckDB), vector search (LanceDB), or Cypher (Memgraph)

    ## Resources

    - [DLT Documentation](https://dlthub.com/docs)
    - [LanceDB Documentation](https://lancedb.github.io/lancedb/)
    - [Memgraph Documentation](https://memgraph.com/docs)
    - [Marimo Documentation](https://docs.marimo.io)
    """)
    return


if __name__ == "__main__":
    app.run()
