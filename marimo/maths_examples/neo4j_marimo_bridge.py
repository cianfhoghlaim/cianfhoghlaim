# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "networkx>=3.0",
#     "numpy>=1.24",
#     "pandas>=2.0",
#     "plotly>=5.0",
#     "pyyaml>=6.0",
#     "neo4j>=5.0",
# ]
# ///
"""
Neo4j-Marimo Bridge - Utility Module

Provides connectivity between Neo4j graph database and Marimo notebooks
for querying curriculum knowledge graphs.

This module bridges the CocoIndex pipeline (docs_to_knowledge_graph)
with interactive analysis in Marimo.

Database reference:
- CocoIndex example: gaeilge/examples/cocoindex/docs_to_knowledge_graph/main.py
- Storage config: gaeilge/sources.yaml (storage.graph.provider: falkordb)
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(
    width="full",
    app_title="Neo4j-Marimo Bridge",
)


@app.cell
def _():
    import marimo as mo
    import networkx as nx
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    import yaml
    from pathlib import Path
    from dataclasses import dataclass
    from typing import Dict, List, Tuple, Optional, Any
    import os
    return mo, nx, np, pd, go, yaml, Path, dataclass, Dict, List, Tuple, Optional, Any, os


@app.cell
def _(mo):
    mo.md("""
    # Neo4j-Marimo Bridge

    This notebook provides **utilities for connecting Marimo notebooks to Neo4j**
    for querying the curriculum knowledge graph.

    ## Architecture

    ```
    CocoIndex Pipeline          Neo4j Database          Marimo Analysis
    ┌─────────────────┐        ┌──────────────┐        ┌──────────────────┐
    │ PDF Documents   │───────>│ Topic Nodes  │<───────│ Network Analysis │
    │ Curriculum JSON │───────>│ Relationships│<───────│ Centrality       │
    │ BAML Extraction │───────>│ Mentions     │<───────│ Forecasting      │
    └─────────────────┘        └──────────────┘        └──────────────────┘
    ```

    ## Connection Configuration

    From `sources.yaml`:
    - **Provider**: FalkorDB (with Graphiti for temporal)
    - **Database**: education_kg
    """)
    return


@app.cell
def _(dataclass, Optional, Dict, Any):
    """
    Configuration dataclass for Neo4j connection.
    """

    @dataclass
    class Neo4jConfig:
        """Neo4j connection configuration."""
        uri: str = "bolt://localhost:7687"
        user: str = "neo4j"
        password: str = "password"
        database: str = "education_kg"

        @classmethod
        def from_env(cls) -> 'Neo4jConfig':
            """Load from environment variables."""
            import os
            return cls(
                uri=os.getenv('NEO4J_URI', cls.uri),
                user=os.getenv('NEO4J_USER', cls.user),
                password=os.getenv('NEO4J_PASSWORD', cls.password),
                database=os.getenv('NEO4J_DATABASE', cls.database),
            )

        @classmethod
        def from_yaml(cls, path: str) -> 'Neo4jConfig':
            """Load from sources.yaml."""
            import yaml
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
            storage = config.get('storage', {}).get('graph', {})
            return cls(
                database=storage.get('database', cls.database),
            )

    return Neo4jConfig,


@app.cell
def _(Neo4jConfig, nx, pd, Optional, List, Dict, Any):
    """
    Neo4j client wrapper for Marimo notebooks.
    """

    class Neo4jClient:
        """Client for Neo4j operations in Marimo notebooks."""

        def __init__(self, config: Optional[Neo4jConfig] = None):
            self.config = config or Neo4jConfig.from_env()
            self._driver = None
            self._connected = False

        def connect(self) -> bool:
            """Establish connection to Neo4j."""
            try:
                from neo4j import GraphDatabase
                self._driver = GraphDatabase.driver(
                    self.config.uri,
                    auth=(self.config.user, self.config.password)
                )
                # Test connection
                with self._driver.session(database=self.config.database) as session:
                    session.run("RETURN 1")
                self._connected = True
                return True
            except ImportError:
                print("neo4j package not installed. Install with: pip install neo4j")
                return False
            except Exception as e:
                print(f"Connection failed: {e}")
                return False

        def close(self):
            """Close the connection."""
            if self._driver:
                self._driver.close()
                self._connected = False

        def is_connected(self) -> bool:
            return self._connected

        def run_query(self, query: str, parameters: Optional[Dict] = None) -> pd.DataFrame:
            """Run a Cypher query and return results as DataFrame."""
            if not self._connected:
                raise ConnectionError("Not connected to Neo4j")

            with self._driver.session(database=self.config.database) as session:
                result = session.run(query, parameters or {})
                records = [dict(record) for record in result]
                return pd.DataFrame(records)

        def get_all_nodes(self, label: Optional[str] = None) -> pd.DataFrame:
            """Get all nodes, optionally filtered by label."""
            if label:
                query = f"MATCH (n:{label}) RETURN n"
            else:
                query = "MATCH (n) RETURN n, labels(n) as labels"
            return self.run_query(query)

        def get_all_relationships(self, rel_type: Optional[str] = None) -> pd.DataFrame:
            """Get all relationships, optionally filtered by type."""
            if rel_type:
                query = f"MATCH (a)-[r:{rel_type}]->(b) RETURN a, r, b"
            else:
                query = "MATCH (a)-[r]->(b) RETURN a, type(r) as rel_type, r, b"
            return self.run_query(query)

        def to_networkx(self, node_label: Optional[str] = None,
                       rel_type: Optional[str] = None) -> nx.DiGraph:
            """Convert Neo4j subgraph to NetworkX graph."""
            G = nx.DiGraph()

            # Get nodes
            if node_label:
                node_query = f"MATCH (n:{node_label}) RETURN id(n) as id, n, labels(n) as labels"
            else:
                node_query = "MATCH (n) RETURN id(n) as id, n, labels(n) as labels"

            nodes_df = self.run_query(node_query)
            for _, row in nodes_df.iterrows():
                node_id = row['id']
                props = dict(row['n']) if hasattr(row['n'], '__iter__') else {}
                props['labels'] = row.get('labels', [])
                G.add_node(node_id, **props)

            # Get relationships
            if rel_type:
                rel_query = f"""
                MATCH (a)-[r:{rel_type}]->(b)
                RETURN id(a) as source, id(b) as target, type(r) as rel_type, r
                """
            else:
                rel_query = """
                MATCH (a)-[r]->(b)
                RETURN id(a) as source, id(b) as target, type(r) as rel_type, r
                """

            rels_df = self.run_query(rel_query)
            for _, row in rels_df.iterrows():
                props = dict(row['r']) if hasattr(row['r'], '__iter__') else {}
                props['rel_type'] = row['rel_type']
                G.add_edge(row['source'], row['target'], **props)

            return G

        # Curriculum-specific queries

        def get_topics(self) -> pd.DataFrame:
            """Get all curriculum topics."""
            query = """
            MATCH (t:Topic)
            RETURN t.name as name, t.strand as strand,
                   t.description as description
            """
            return self.run_query(query)

        def get_topic_relationships(self) -> pd.DataFrame:
            """Get prerequisite relationships between topics."""
            query = """
            MATCH (a:Topic)-[r:PREREQUISITE]->(b:Topic)
            RETURN a.name as from_topic, b.name as to_topic,
                   r.weight as weight
            """
            return self.run_query(query)

        def get_questions_by_topic(self, topic: str) -> pd.DataFrame:
            """Get all questions for a specific topic."""
            query = """
            MATCH (q:Question)-[:COVERS]->(t:Topic {name: $topic})
            RETURN q.id as question_id, q.text as text,
                   q.marks as marks, q.year as year
            """
            return self.run_query(query, {'topic': topic})

        def get_subject_network(self) -> nx.Graph:
            """Get subject cross-curricular concept network."""
            query = """
            MATCH (s1:Subject)-[:SHARES_CONCEPT]->(c:Concept)<-[:SHARES_CONCEPT]-(s2:Subject)
            WHERE s1 <> s2
            RETURN s1.name as subject1, s2.name as subject2,
                   c.name as shared_concept
            """
            df = self.run_query(query)
            G = nx.Graph()
            for _, row in df.iterrows():
                if not G.has_edge(row['subject1'], row['subject2']):
                    G.add_edge(row['subject1'], row['subject2'], concepts=[])
                G.edges[row['subject1'], row['subject2']]['concepts'].append(row['shared_concept'])
            return G

    return Neo4jClient,


@app.cell
def _(mo):
    # Connection status UI
    connection_status = mo.state(False)
    return connection_status,


@app.cell
def _(Neo4jConfig, Neo4jClient, connection_status, mo):
    """
    Interactive connection panel.
    """

    # Configuration inputs
    uri_input = mo.ui.text(value="bolt://localhost:7687", label="Neo4j URI")
    user_input = mo.ui.text(value="neo4j", label="Username")
    password_input = mo.ui.text(value="", label="Password", kind="password")
    database_input = mo.ui.text(value="education_kg", label="Database")

    def connect_handler():
        config = Neo4jConfig(
            uri=uri_input.value,
            user=user_input.value,
            password=password_input.value,
            database=database_input.value,
        )
        client = Neo4jClient(config)
        success = client.connect()
        connection_status.set_state(success)
        return client if success else None

    connect_button = mo.ui.button(label="Connect", on_click=lambda _: connect_handler())

    mo.vstack([
        mo.md("## Connection Configuration"),
        mo.hstack([uri_input, database_input]),
        mo.hstack([user_input, password_input]),
        connect_button,
        mo.md("**Status**: " + ("Connected" if connection_status.value else "Not connected"))
    ])
    return uri_input, user_input, password_input, database_input, connect_button, connect_handler


@app.cell
def _(nx, pd, np, mo):
    """
    Demo: Simulated knowledge graph for testing without Neo4j.
    """

    def create_demo_graph() -> nx.DiGraph:
        """Create a demo curriculum knowledge graph."""
        G = nx.DiGraph()

        # Topic nodes
        topics = {
            'Algebra': {'strand': 'algebra', 'difficulty': 0.4},
            'Linear Equations': {'strand': 'algebra', 'difficulty': 0.3},
            'Quadratic Equations': {'strand': 'algebra', 'difficulty': 0.5},
            'Functions': {'strand': 'functions', 'difficulty': 0.4},
            'Trigonometry': {'strand': 'geometry', 'difficulty': 0.6},
            'Calculus': {'strand': 'calculus', 'difficulty': 0.7},
            'Differentiation': {'strand': 'calculus', 'difficulty': 0.65},
            'Integration': {'strand': 'calculus', 'difficulty': 0.75},
            'Statistics': {'strand': 'statistics', 'difficulty': 0.5},
            'Probability': {'strand': 'statistics', 'difficulty': 0.45},
        }

        for topic, attrs in topics.items():
            G.add_node(topic, node_type='Topic', **attrs)

        # Prerequisite relationships
        prerequisites = [
            ('Linear Equations', 'Quadratic Equations'),
            ('Algebra', 'Functions'),
            ('Functions', 'Calculus'),
            ('Trigonometry', 'Calculus'),
            ('Calculus', 'Differentiation'),
            ('Calculus', 'Integration'),
            ('Differentiation', 'Integration'),
            ('Probability', 'Statistics'),
        ]

        for prereq, topic in prerequisites:
            G.add_edge(prereq, topic, rel_type='PREREQUISITE')

        # Subject nodes
        subjects = ['Mathematics', 'Physics', 'Biology', 'Economics']
        for subj in subjects:
            G.add_node(subj, node_type='Subject')

        # Subject-topic connections
        G.add_edge('Mathematics', 'Algebra', rel_type='COVERS')
        G.add_edge('Mathematics', 'Calculus', rel_type='COVERS')
        G.add_edge('Mathematics', 'Statistics', rel_type='COVERS')
        G.add_edge('Physics', 'Calculus', rel_type='USES')
        G.add_edge('Physics', 'Trigonometry', rel_type='USES')
        G.add_edge('Biology', 'Statistics', rel_type='USES')
        G.add_edge('Economics', 'Statistics', rel_type='USES')
        G.add_edge('Economics', 'Calculus', rel_type='USES')

        return G

    demo_graph = create_demo_graph()
    mo.md(f"""
    ## Demo Knowledge Graph

    Created simulated curriculum graph for testing:
    - **Nodes**: {demo_graph.number_of_nodes()}
    - **Edges**: {demo_graph.number_of_edges()}

    *Use this when Neo4j is not available.*
    """)
    return create_demo_graph, demo_graph


@app.cell
def _(demo_graph, nx, pd, mo):
    """
    Demonstrate analysis on demo graph.
    """

    # Topic analysis
    topics = [n for n, d in demo_graph.nodes(data=True) if d.get('node_type') == 'Topic']
    topic_subgraph = demo_graph.subgraph(topics)

    # Centrality
    pagerank = nx.pagerank(demo_graph)
    in_degree = dict(demo_graph.in_degree())
    out_degree = dict(demo_graph.out_degree())

    analysis_df = pd.DataFrame({
        'node': list(demo_graph.nodes()),
        'type': [demo_graph.nodes[n].get('node_type', 'Unknown') for n in demo_graph.nodes()],
        'in_degree': [in_degree.get(n, 0) for n in demo_graph.nodes()],
        'out_degree': [out_degree.get(n, 0) for n in demo_graph.nodes()],
        'pagerank': [pagerank.get(n, 0) for n in demo_graph.nodes()],
    }).sort_values('pagerank', ascending=False)

    mo.md("### Graph Analysis")
    return topics, topic_subgraph, pagerank, in_degree, out_degree, analysis_df


@app.cell
def _(analysis_df, mo):
    mo.ui.table(analysis_df.round(4))
    return


@app.cell
def _(demo_graph, go, mo):
    """
    Visualize demo knowledge graph.
    """

    pos = nx.spring_layout(demo_graph, k=2, seed=42)

    # Edges
    edge_x, edge_y = [], []
    for u, v in demo_graph.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Nodes by type
    node_colors = {'Topic': '#1f77b4', 'Subject': '#ff7f0e'}

    node_traces = []
    for node_type, color in node_colors.items():
        nodes = [n for n, d in demo_graph.nodes(data=True) if d.get('node_type') == node_type]
        x = [pos[n][0] for n in nodes]
        y = [pos[n][1] for n in nodes]

        node_traces.append(go.Scatter(
            x=x, y=y,
            mode='markers+text',
            text=nodes,
            textposition='top center',
            marker=dict(size=15, color=color),
            name=node_type
        ))

    fig_demo = go.Figure(
        data=[edge_trace] + node_traces,
        layout=go.Layout(
            title='Demo Curriculum Knowledge Graph',
            showlegend=True,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=500
        )
    )

    mo.ui.plotly(fig_demo)
    return fig_demo, pos, edge_trace, node_traces, node_colors


@app.cell
def _(mo):
    mo.md("""
    ## Cypher Query Examples

    Common queries for curriculum analysis:

    ```cypher
    -- Get all topics with their strands
    MATCH (t:Topic)
    RETURN t.name, t.strand, t.difficulty
    ORDER BY t.difficulty DESC

    -- Find prerequisite chains
    MATCH path = (t1:Topic)-[:PREREQUISITE*]->(t2:Topic)
    RETURN t1.name as start, t2.name as end, length(path) as depth
    ORDER BY depth DESC

    -- Cross-subject concepts
    MATCH (s1:Subject)-[:USES]->(t:Topic)<-[:USES]-(s2:Subject)
    WHERE s1 <> s2
    RETURN s1.name, t.name as shared_topic, s2.name

    -- Questions by difficulty
    MATCH (q:Question)-[:COVERS]->(t:Topic)
    RETURN t.name as topic, AVG(q.difficulty) as avg_difficulty
    ORDER BY avg_difficulty DESC

    -- Topic centrality (PageRank-like)
    CALL gds.pageRank.stream('curriculum-graph')
    YIELD nodeId, score
    RETURN gds.util.asNode(nodeId).name AS topic, score
    ORDER BY score DESC
    ```
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Usage in Other Notebooks

    Import this module in other marimo notebooks:

    ```python
    # Import the client
    from neo4j_marimo_bridge import Neo4jClient, Neo4jConfig

    # Connect
    config = Neo4jConfig.from_env()
    client = Neo4jClient(config)
    client.connect()

    # Query topics
    topics_df = client.get_topics()

    # Get NetworkX graph
    G = client.to_networkx(node_label='Topic', rel_type='PREREQUISITE')

    # Run custom query
    results = client.run_query('''
        MATCH (t:Topic)-[:PREREQUISITE]->(t2:Topic)
        RETURN t.name, t2.name, t.difficulty
    ''')
    ```

    ## Integration with CocoIndex

    The `docs_to_knowledge_graph` example populates Neo4j with:
    - **Document** nodes (curriculum specifications)
    - **Entity** nodes (topics, concepts)
    - **RELATIONSHIP** edges (semantic connections)
    - **MENTION** edges (document-entity links)

    This bridge enables querying that data in marimo.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Summary

    ### Module Components

    | Class | Purpose |
    |-------|---------|
    | `Neo4jConfig` | Connection configuration (URI, credentials) |
    | `Neo4jClient` | Query execution and graph export |
    | `create_demo_graph()` | Testing without Neo4j |

    ### Key Methods

    - `client.connect()` - Establish connection
    - `client.run_query(cypher)` - Execute Cypher query
    - `client.to_networkx()` - Export to NetworkX for analysis
    - `client.get_topics()` - Curriculum-specific query
    - `client.get_subject_network()` - Cross-subject concept graph

    ### Related Notebooks

    - `curriculum_network_analysis.py` - Uses NetworkX graphs
    - `cross_subject_bridges.py` - Subject projection analysis
    - `topic_forecasting.py` - Markov chain predictions
    - `question_difficulty_network.py` - IRT difficulty modeling
    """)
    return


if __name__ == "__main__":
    app.run()
