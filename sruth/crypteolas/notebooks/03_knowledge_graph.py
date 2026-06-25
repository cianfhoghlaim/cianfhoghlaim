# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "neo4j",
#     "python-dotenv",
#     "altair>=5.0.0",
#     "networkx",
# ]
# ///
"""Knowledge Graph Explorer - Cognee + Memgraph Integration.

This marimo notebook demonstrates:
1. Building knowledge graphs from documents
2. Exploring entities and relationships
3. Querying with Cypher
4. Visualizing graph structures

Usage:
    marimo edit notebooks/03_knowledge_graph.py

Prerequisites:
    - Memgraph running: curl https://install.memgraph.com | sh
    - Access at http://localhost:3000
"""
import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Knowledge Graph Explorer

    This notebook demonstrates building and exploring **knowledge graphs** using
    Cognee for extraction and Memgraph for storage/querying.

    ## Prerequisites

    1. **Start Memgraph**:
    ```bash
    # Linux/macOS
    curl https://install.memgraph.com | sh

    # Windows
    iwr https://windows.memgraph.com | iex
    ```

    2. **Access Memgraph Lab**: http://localhost:3000

    ## How It Works

    1. **Extract**: Cognee uses LLMs to extract entities and relationships
    2. **Store**: Entities and relationships stored in Memgraph
    3. **Query**: Use Cypher queries to explore the graph
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1: Connect to Memgraph

    Enter your Memgraph connection details:
    """)
    return


@app.cell
def _(mo, os):
    uri_input = mo.ui.text(
        value=os.environ.get("GRAPH_DATABASE_URL", "bolt://localhost:7687"),
        label="Memgraph URI",
    )

    user_input = mo.ui.text(
        value=os.environ.get("GRAPH_DATABASE_USERNAME", ""),
        label="Username (leave empty if none)",
    )

    password_input = mo.ui.text(
        value=os.environ.get("GRAPH_DATABASE_PASSWORD", ""),
        label="Password (leave empty if none)",
        kind="password",
    )

    mo.vstack([uri_input, user_input, password_input])
    return uri_input, user_input, password_input


@app.cell
def _(mo):
    connect_button = mo.ui.run_button(label="Connect")
    connect_button
    return (connect_button,)


@app.cell
def _(mo, uri_input, user_input, password_input, connect_button):
    from neo4j import GraphDatabase

    driver = None
    connection_status = None

    if connect_button.value:
        try:
            auth = (user_input.value, password_input.value) if user_input.value else None
            driver = GraphDatabase.driver(uri_input.value, auth=auth)

            # Test connection
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()

            connection_status = "Connected successfully!"
        except Exception as e:
            connection_status = f"Connection failed: {e}"
            driver = None

    if connection_status:
        mo.md(f"**Status**: {connection_status}")

    driver
    return GraphDatabase, driver, connection_status


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: Build Knowledge Graph

    Select a directory of markdown files to process:
    """)
    return


@app.cell
def _(mo, Path):
    docs_dir = mo.ui.text(
        value="./docs" if Path("./docs").exists() else ".",
        label="Documentation directory",
        full_width=True,
    )
    docs_dir
    return (docs_dir,)


@app.cell
def _(mo):
    build_button = mo.ui.run_button(label="Build Knowledge Graph")
    build_button
    return (build_button,)


@app.cell
def _(mo, docs_dir, build_button, driver, Path):
    import sys
    sys.path.insert(0, str(Path.cwd()))

    build_result = None

    if build_button.value and driver:
        mo.status.spinner(title="Building knowledge graph...")

        from cocoindex.config import DocsIndexingConfig
        from cocoindex.flows.docs_indexing import DocsIndexingFlow

        config = DocsIndexingConfig(
            name="docs",
            source_path=docs_dir.value,
            included_patterns=["*.md", "*.mdx"],
        )

        flow = DocsIndexingFlow(config)
        build_result = flow.index_directory(docs_dir.value)

    build_result
    return DocsIndexingConfig, DocsIndexingFlow, build_result


@app.cell
def _(build_result, mo):
    if build_result:
        mo.md(f"""
        ## Build Complete

        - **Documents processed**: {build_result['documents']}
        - **Chunks indexed**: {build_result['chunks']}
        - **Relationships extracted**: {build_result['relationships']}
        - **Entity mentions**: {build_result['mentions']}
        """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 3: Explore the Graph

    ### Graph Statistics
    """)
    return


@app.cell
def _(driver, mo):
    stats = None

    if driver:
        try:
            with driver.session() as session:
                # Node counts
                node_result = session.run("""
                    MATCH (n)
                    RETURN labels(n)[0] as label, count(n) as count
                    ORDER BY count DESC
                """)
                nodes = [dict(r) for r in node_result]

                # Edge counts
                edge_result = session.run("""
                    MATCH ()-[r]->()
                    RETURN type(r) as type, count(r) as count
                    ORDER BY count DESC
                """)
                edges = [dict(r) for r in edge_result]

                stats = {"nodes": nodes, "edges": edges}
        except Exception as e:
            mo.md(f"*Error getting stats: {e}*")

    if stats:
        mo.md(f"""
        **Node Types**: {', '.join(f"{n['label']}: {n['count']}" for n in stats['nodes'])}

        **Edge Types**: {', '.join(f"{e['type']}: {e['count']}" for e in stats['edges'])}
        """)
    return (stats,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Entity Search

    Search for entities in the knowledge graph:
    """)
    return


@app.cell
def _(mo):
    entity_search = mo.ui.text(
        value="",
        label="Search entities",
        placeholder="Enter entity name...",
    )
    entity_search
    return (entity_search,)


@app.cell
def _(driver, entity_search, mo):
    entity_results = []

    if driver and entity_search.value:
        try:
            with driver.session() as session:
                result = session.run("""
                    MATCH (e:Entity)
                    WHERE toLower(e.value) CONTAINS toLower($query)
                    OPTIONAL MATCH (e)-[r]-(related)
                    RETURN e.value as entity,
                           collect(DISTINCT {
                               type: type(r),
                               direction: CASE WHEN startNode(r) = e THEN 'out' ELSE 'in' END,
                               related: CASE WHEN startNode(r) = e THEN endNode(r).value ELSE startNode(r).value END
                           }) as relationships
                    LIMIT 10
                """, query=entity_search.value)
                entity_results = [dict(r) for r in result]
        except Exception as e:
            mo.md(f"*Error: {e}*")

    if entity_results:
        for entity in entity_results:
            rels = entity.get("relationships", [])
            rel_strs = [f"{r['direction']}: {r['type']} -> {r['related']}" for r in rels if r['related']]
            mo.md(f"""
**{entity['entity']}**
- Relationships: {len(rels)}
- {', '.join(rel_strs[:5])}{'...' if len(rel_strs) > 5 else ''}
""")
    return (entity_results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Custom Cypher Query

    Run your own Cypher queries:
    """)
    return


@app.cell
def _(mo):
    cypher_input = mo.ui.text_area(
        value="""MATCH (e:Entity)-[r:RELATIONSHIP]->(related:Entity)
RETURN e.value as subject, r.predicate as predicate, related.value as object
LIMIT 20""",
        label="Cypher Query",
        rows=5,
        full_width=True,
    )
    cypher_input
    return (cypher_input,)


@app.cell
def _(mo):
    run_query_button = mo.ui.run_button(label="Run Query")
    run_query_button
    return (run_query_button,)


@app.cell
def _(driver, cypher_input, run_query_button, mo):
    query_results = []

    if driver and run_query_button.value:
        try:
            with driver.session() as session:
                result = session.run(cypher_input.value)
                query_results = [dict(r) for r in result]
        except Exception as e:
            mo.md(f"*Query error: {e}*")

    if query_results:
        mo.ui.table(query_results)
    return (query_results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Most Connected Entities

    Find entities with the most relationships:
    """)
    return


@app.cell
def _(driver, mo):
    import altair as alt
    import pandas as pd

    connected = []

    if driver:
        try:
            with driver.session() as session:
                result = session.run("""
                    MATCH (e:Entity)-[r]-()
                    RETURN e.value as entity, count(r) as connections
                    ORDER BY connections DESC
                    LIMIT 15
                """)
                connected = [dict(r) for r in result]
        except Exception as e:
            mo.md(f"*Error: {e}*")

    if connected:
        df = pd.DataFrame(connected)

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("connections:Q", title="Connections"),
            y=alt.Y("entity:N", sort="-x", title="Entity"),
            tooltip=["entity", "connections"]
        ).properties(
            title="Most Connected Entities",
            width=500,
            height=300
        )

        mo.ui.altair_chart(chart)
    return alt, pd, connected


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 4: Graph Visualization

    Visualize a portion of the knowledge graph:
    """)
    return


@app.cell
def _(driver, mo):
    import networkx as nx

    G = None

    if driver:
        try:
            with driver.session() as session:
                # Get nodes and edges for visualization
                result = session.run("""
                    MATCH (s:Entity)-[r:RELATIONSHIP]->(t:Entity)
                    RETURN s.value as source, r.predicate as relationship, t.value as target
                    LIMIT 50
                """)
                edges = [dict(r) for r in result]

            if edges:
                G = nx.DiGraph()
                for edge in edges:
                    G.add_edge(
                        edge["source"],
                        edge["target"],
                        label=edge["relationship"]
                    )

                # Get node degrees for sizing
                degrees = dict(G.degree())

                mo.md(f"""
                **Graph loaded**: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges

                Top nodes by degree: {', '.join(sorted(degrees.keys(), key=lambda k: degrees[k], reverse=True)[:5])}
                """)

        except Exception as e:
            mo.md(f"*Error loading graph: {e}*")

    G
    return nx, G


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Common Cypher Queries

    Here are some useful queries to try:

    ```cypher
    -- View entire graph (limited)
    MATCH p=()-[]-() RETURN p LIMIT 100

    -- Find entities related to a topic
    MATCH (e:Entity)-[r]-(related)
    WHERE e.value CONTAINS 'DLT'
    RETURN e, r, related

    -- Find paths between entities
    MATCH p=shortestPath((s:Entity {value: 'Python'})-[*]-(t:Entity {value: 'DuckDB'}))
    RETURN p

    -- Get documents mentioning an entity
    MATCH (d:Document)-[:MENTIONS]->(e:Entity {value: 'Pipeline'})
    RETURN d.filename, d.title

    -- Find most common predicates
    MATCH ()-[r:RELATIONSHIP]->()
    RETURN r.predicate, count(r) as count
    ORDER BY count DESC
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Next Steps

    - **API Data**: Run `01_github_api_explorer.py` to ingest GitHub metadata
    - **Code Search**: Run `02_code_search.py` for semantic code search
    - **Dashboard**: Run `04_unified_dashboard.py` for combined analytics

    ## Resources

    - [Memgraph Documentation](https://memgraph.com/docs)
    - [Cypher Query Language](https://memgraph.com/docs/cypher-manual)
    - [Cognee Documentation](https://github.com/cognee-ai/cognee)
    """)
    return


if __name__ == "__main__":
    app.run()
