# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "neo4j",
#     "python-dotenv",
#     "altair>=5.0.0",
#     "networkx",
#     "pandas",
# ]
# ///
"""Knowledge Graph Explorer - Memgraph/Neo4j Integration.

This marimo notebook demonstrates:
1. Connecting to graph databases
2. Exploring entities and relationships
3. Querying with Cypher
4. Visualizing graph structures

Usage:
    marimo edit crypteolas/notebooks/03_knowledge_graph.py

Prerequisites:
    - Memgraph running: docker run -p 7687:7687 memgraph/memgraph
    - Or Neo4j: docker run -p 7687:7687 neo4j
"""
import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Knowledge Graph Explorer

    This notebook demonstrates exploring **knowledge graphs** for crypto protocol
    documentation and code relationships.

    ## Supported Databases

    - **Memgraph**: Fast in-memory graph database
    - **Neo4j**: Popular graph database
    - **FalkorDB**: Redis-based graph database

    ## Data Sources

    - Protocol documentation (Aave, Compound, Pendle, Ethena)
    - GitHub code relationships
    - DeFi protocol dependencies
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
    load_dotenv()
    return (load_dotenv,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1: Connect to Graph Database

    Enter your connection details:
    """)
    return


@app.cell
def _(mo, os):
    uri_input = mo.ui.text(
        value=os.environ.get("GRAPH_DATABASE_URL", "bolt://localhost:7687"),
        label="Database URI",
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
    ## Step 2: Explore the Graph

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
        node_summary = ', '.join(f"{n['label']}: {n['count']}" for n in stats['nodes']) if stats['nodes'] else 'No nodes'
        edge_summary = ', '.join(f"{e['type']}: {e['count']}" for e in stats['edges']) if stats['edges'] else 'No edges'
        mo.md(f"""
        **Node Types**: {node_summary}

        **Edge Types**: {edge_summary}
        """)
    return (stats,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Protocol Search

    Search for DeFi protocols in the knowledge graph:
    """)
    return


@app.cell
def _(mo):
    protocol_search = mo.ui.text(
        value="",
        label="Search protocols",
        placeholder="Enter protocol name (e.g., Aave, Ethena, Pendle)...",
    )
    protocol_search
    return (protocol_search,)


@app.cell
def _(driver, protocol_search, mo):
    protocol_results = []

    if driver and protocol_search.value:
        try:
            with driver.session() as session:
                result = session.run("""
                    MATCH (p:Protocol)
                    WHERE toLower(p.name) CONTAINS toLower($query)
                    OPTIONAL MATCH (p)-[r]-(related)
                    RETURN p.name as protocol,
                           p.category as category,
                           collect(DISTINCT {
                               type: type(r),
                               related: CASE WHEN startNode(r) = p THEN labels(endNode(r))[0] ELSE labels(startNode(r))[0] END,
                               name: CASE WHEN startNode(r) = p THEN endNode(r).name ELSE startNode(r).name END
                           }) as relationships
                    LIMIT 10
                """, query=protocol_search.value)
                protocol_results = [dict(r) for r in result]
        except Exception as e:
            mo.md(f"*Error: {e}*")

    if protocol_results:
        for proto in protocol_results:
            rels = proto.get("relationships", [])
            rel_strs = [f"{r['type']} -> {r['name']}" for r in rels if r.get('name')]
            mo.md(f"""
**{proto['protocol']}** ({proto.get('category', 'Unknown')})
- Relationships: {len(rels)}
- {', '.join(rel_strs[:5])}{'...' if len(rel_strs) > 5 else ''}
""")
    return (protocol_results,)


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
        value="""MATCH (p:Protocol)-[r:USES]->(t:Token)
RETURN p.name as protocol, t.symbol as token, t.name as token_name
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
                    MATCH (n)-[r]-()
                    WHERE n.name IS NOT NULL
                    RETURN n.name as entity, labels(n)[0] as type, count(r) as connections
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
            color="type:N",
            tooltip=["entity", "type", "connections"]
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
    ## Common Cypher Queries for DeFi

    ```cypher
    -- Find all protocols using a specific token
    MATCH (p:Protocol)-[:USES]->(t:Token {symbol: 'ETH'})
    RETURN p.name, t.symbol

    -- Find protocol dependencies
    MATCH (p1:Protocol)-[:DEPENDS_ON]->(p2:Protocol)
    RETURN p1.name as dependent, p2.name as dependency

    -- Find yield sources for a protocol
    MATCH (p:Protocol)-[:GENERATES_YIELD]->(s:YieldSource)
    RETURN p.name, s.type, s.apy

    -- Find all stablecoin relationships
    MATCH (t:Token {type: 'stablecoin'})-[r]-(n)
    RETURN t.symbol, type(r), labels(n)[0], n.name

    -- Protocol TVL ranking
    MATCH (p:Protocol)
    WHERE p.tvl IS NOT NULL
    RETURN p.name, p.tvl
    ORDER BY p.tvl DESC
    LIMIT 10
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Next Steps

    - **GitHub API**: Run `01_github_explorer.py` to ingest GitHub metadata
    - **Code Search**: Run `02_code_search.py` for semantic code search
    - **DeFi Dashboard**: Run `04_defi_dashboard.py` for DeFi analytics

    ## Resources

    - [Memgraph Documentation](https://memgraph.com/docs)
    - [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual)
    - [FalkorDB Documentation](https://docs.falkordb.com)
    """)
    return


if __name__ == "__main__":
    app.run()
