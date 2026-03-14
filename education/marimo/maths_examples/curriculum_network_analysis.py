# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "networkx>=3.0",
#     "numpy>=1.24",
#     "pandas>=2.0",
#     "plotly>=5.0",
#     "pyyaml>=6.0",
# ]
# ///
"""
Curriculum Network Analysis - Marimo Notebook

Applies graph theory concepts from CS4423 Networks course to analyze
the Irish educational curriculum structure from the Gaeilge project.

Mathematical foundations from:
- /Users/cliste/dev/mata/CS4423 - Networks/Notebooks/networks08.ipynb (Centrality)
- /Users/cliste/dev/mata/CS4423 - Networks/Notebooks/networks09.ipynb (Betweenness)

Data source:
- /Users/cliste/dev/bonneagar/hackathon/data/flows/gaeilge/sources.yaml
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(
    width="full",
    app_title="Curriculum Network Analysis",
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
    return mo, nx, np, pd, go, yaml, Path


@app.cell
def _(mo):
    mo.md("""
    # Curriculum Network Analysis

    This notebook applies **graph theory** and **network analysis** concepts to explore
    the Irish educational curriculum structure. We analyze:

    1. **Subject-Topic Networks** - How subjects connect through shared concepts
    2. **Centrality Measures** - Which topics/subjects are most interconnected
    3. **Community Detection** - Natural clustering of subjects
    4. **Prerequisite Chains** - Dependency relationships between topics

    ## Mathematical Foundations

    From CS4423 Networks (Prof. Pfeiffer, NUI Galway):
    - **Degree Centrality**: $c_i^D = k_i = \\sum_j a_{ij}$
    - **Eigenvector Centrality**: $\\lambda c^E = A c^E$ (Perron-Frobenius)
    - **Betweenness Centrality**: Proportion of shortest paths through node
    """)
    return


@app.cell
def _(yaml, Path, mo):
    # Load curriculum configuration from sources.yaml
    GAEILGE_PATH = Path("/Users/cliste/dev/bonneagar/hackathon/data/flows/gaeilge")

    with open(GAEILGE_PATH / "sources.yaml", "r") as f:
        config = yaml.safe_load(f)

    mo.md(f"""
    ## Data Loaded

    - **Senior Cycle Subjects**: {len(config.get('senior_cycle_subjects', {}))} categories
    - **Cross-Subject Concepts**: {len(config.get('cross_subject_concepts', {}))} bridging concepts
    - **Curriculum History Events**: {len(config.get('curriculum_history', {}).get('mathematics', []))} for Mathematics
    """)
    return config, GAEILGE_PATH


@app.cell
def _(config, nx, np):
    """
    Build the Subject-Concept bipartite graph.

    Graph structure:
    - Subject nodes (type='subject')
    - Concept nodes (type='concept')
    - Edges connect subjects to their cross-subject concepts

    This mirrors the bipartite graph construction from networks04.ipynb
    """

    # Create bipartite graph
    B = nx.Graph()

    # Add subject nodes from all categories
    subjects = []
    for category, subject_list in config.get('senior_cycle_subjects', {}).items():
        for subject in subject_list:
            name = subject['name']
            subjects.append(name)
            B.add_node(name,
                       bipartite=0,
                       node_type='subject',
                       category=category,
                       code=subject.get('code', ''),
                       levels=subject.get('levels', []))

    # Add concept nodes and edges from cross_subject_concepts
    concepts = []
    for concept, details in config.get('cross_subject_concepts', {}).items():
        concepts.append(concept)
        B.add_node(concept,
                   bipartite=1,
                   node_type='concept',
                   description=details.get('description', ''))

        # Connect concept to subjects
        for subj_name in details.get('subjects', []):
            # Match subject names (handle underscore to space conversion)
            for subj in subjects:
                if subj.lower().replace(' ', '_') == subj_name.lower() or \
                   subj.lower() == subj_name.lower():
                    B.add_edge(concept, subj)

    # Also add cross_subject_concepts from individual subjects
    for category, subject_list in config.get('senior_cycle_subjects', {}).items():
        for subject in subject_list:
            for concept in subject.get('cross_subject_concepts', []):
                if concept not in concepts:
                    concepts.append(concept)
                    B.add_node(concept, bipartite=1, node_type='concept')
                B.add_edge(concept, subject['name'])

    print(f"Bipartite graph: {B.number_of_nodes()} nodes, {B.number_of_edges()} edges")
    print(f"  - Subjects: {len(subjects)}")
    print(f"  - Concepts: {len(concepts)}")
    return B, subjects, concepts


@app.cell
def _(B, nx, np, pd, mo):
    """
    Compute centrality measures for the curriculum network.

    Following networks08.ipynb methodology:
    1. Degree centrality (direct connections)
    2. Eigenvector centrality (influence through network)
    3. Betweenness centrality (bridging importance)
    """

    # Get the largest connected component for analysis
    if nx.is_connected(B):
        G = B
    else:
        largest_cc = max(nx.connected_components(B), key=len)
        G = B.subgraph(largest_cc).copy()

    # Compute centrality measures
    degree_cent = nx.degree_centrality(G)

    # Eigenvector centrality (may fail on disconnected graphs)
    try:
        eigen_cent = nx.eigenvector_centrality(G, max_iter=1000)
    except nx.NetworkXError:
        eigen_cent = {n: 0 for n in G.nodes()}

    # Betweenness centrality
    between_cent = nx.betweenness_centrality(G)

    # Closeness centrality
    close_cent = nx.closeness_centrality(G)

    # Create DataFrame with all measures
    centrality_df = pd.DataFrame({
        'node': list(G.nodes()),
        'type': [G.nodes[n].get('node_type', 'unknown') for n in G.nodes()],
        'category': [G.nodes[n].get('category', '') for n in G.nodes()],
        'degree': [G.degree(n) for n in G.nodes()],
        'degree_centrality': [degree_cent[n] for n in G.nodes()],
        'eigenvector_centrality': [eigen_cent[n] for n in G.nodes()],
        'betweenness_centrality': [between_cent[n] for n in G.nodes()],
        'closeness_centrality': [close_cent[n] for n in G.nodes()],
    }).sort_values('eigenvector_centrality', ascending=False)

    mo.md(f"""
    ## Centrality Analysis Results

    **Graph Properties:**
    - Nodes in largest component: {G.number_of_nodes()}
    - Edges: {G.number_of_edges()}
    - Density: {nx.density(G):.4f}
    - Average clustering coefficient: {nx.average_clustering(G):.4f}
    """)
    return G, centrality_df, degree_cent, eigen_cent, between_cent, close_cent


@app.cell
def _(centrality_df, mo):
    # Display top nodes by eigenvector centrality
    mo.md("""
    ### Top 10 Most Central Nodes (Eigenvector Centrality)

    Eigenvector centrality identifies nodes connected to other important nodes.
    High values indicate topics/subjects that bridge multiple curriculum areas.
    """)
    return


@app.cell
def _(centrality_df, mo):
    top_10 = centrality_df.head(10)
    mo.ui.table(top_10)
    return top_10,


@app.cell
def _(G, subjects, concepts, nx, pd, mo):
    """
    Create subject-to-subject projection graph.

    From networks04.ipynb: Project bipartite graph onto one node set.
    Two subjects are connected if they share a concept.
    Edge weight = number of shared concepts.
    """

    # Get subject nodes
    subject_nodes = [n for n in G.nodes() if G.nodes[n].get('node_type') == 'subject']

    # Create projection
    if len(subject_nodes) > 1:
        # Build projection manually to include edge weights
        subject_graph = nx.Graph()
        subject_graph.add_nodes_from(subject_nodes)

        for s1 in subject_nodes:
            for s2 in subject_nodes:
                if s1 < s2:  # Avoid duplicates
                    # Find common concept neighbors
                    neighbors_s1 = set(G.neighbors(s1))
                    neighbors_s2 = set(G.neighbors(s2))
                    common = neighbors_s1 & neighbors_s2
                    if common:
                        subject_graph.add_edge(s1, s2,
                                               weight=len(common),
                                               shared_concepts=list(common))

        mo.md(f"""
        ## Subject Projection Graph

        Two subjects are connected if they share cross-curricular concepts.

        - **Subject nodes**: {subject_graph.number_of_nodes()}
        - **Edges (shared concepts)**: {subject_graph.number_of_edges()}
        - **Most connected subjects** (by degree):
        """)
    else:
        subject_graph = nx.Graph()
        mo.md("Not enough subjects to create projection graph")

    return subject_graph, subject_nodes


@app.cell
def _(subject_graph, nx, pd, mo):
    if subject_graph.number_of_edges() > 0:
        # Compute centrality for subject projection
        subj_degree = dict(subject_graph.degree())
        subj_eigen = nx.eigenvector_centrality(subject_graph, max_iter=1000) if subject_graph.number_of_nodes() > 2 else {}
        subj_between = nx.betweenness_centrality(subject_graph)

        subj_centrality = pd.DataFrame({
            'subject': list(subject_graph.nodes()),
            'degree': [subj_degree.get(n, 0) for n in subject_graph.nodes()],
            'eigenvector': [subj_eigen.get(n, 0) for n in subject_graph.nodes()],
            'betweenness': [subj_between.get(n, 0) for n in subject_graph.nodes()],
        }).sort_values('eigenvector', ascending=False)

        mo.ui.table(subj_centrality.head(10))
    else:
        subj_centrality = pd.DataFrame()
        mo.md("No subject projection data available")
    return subj_centrality, subj_degree, subj_eigen, subj_between


@app.cell
def _(G, go, mo):
    """
    Interactive network visualization using Plotly.
    """
    import plotly.graph_objects as go

    # Get positions using spring layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # Separate subject and concept nodes
    subject_x, subject_y, subject_names = [], [], []
    concept_x, concept_y, concept_names = [], [], []

    for node in G.nodes():
        x, y = pos[node]
        if G.nodes[node].get('node_type') == 'subject':
            subject_x.append(x)
            subject_y.append(y)
            subject_names.append(node)
        else:
            concept_x.append(x)
            concept_y.append(y)
            concept_names.append(node)

    # Create edge traces
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    subject_trace = go.Scatter(
        x=subject_x, y=subject_y,
        mode='markers+text',
        hoverinfo='text',
        text=subject_names,
        textposition='top center',
        marker=dict(
            size=15,
            color='#1f77b4',
            line=dict(width=2, color='white')
        ),
        name='Subjects'
    )

    concept_trace = go.Scatter(
        x=concept_x, y=concept_y,
        mode='markers+text',
        hoverinfo='text',
        text=concept_names,
        textposition='top center',
        marker=dict(
            size=12,
            color='#ff7f0e',
            symbol='diamond',
            line=dict(width=1, color='white')
        ),
        name='Concepts'
    )

    fig = go.Figure(
        data=[edge_trace, subject_trace, concept_trace],
        layout=go.Layout(
            title='Curriculum Network: Subjects and Cross-Curricular Concepts',
            showlegend=True,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600,
        )
    )

    mo.ui.plotly(fig)
    return fig, pos


@app.cell
def _(G, nx, np, mo):
    """
    Adjacency matrix analysis - following networks03.ipynb and networks08.ipynb

    Key concepts:
    - Adjacency matrix A where A[i,j] = 1 if edge exists
    - A^k[i,j] = number of paths of length k from i to j
    - Eigenvalues reveal graph structure
    """

    # Get adjacency matrix
    A = nx.adjacency_matrix(G).toarray()

    # Compute eigenvalues
    eigenvalues, eigenvectors = np.linalg.eig(A)

    # Sort by magnitude
    idx = np.argsort(np.abs(eigenvalues))[::-1]
    eigenvalues = eigenvalues[idx]

    # Spectral gap (difference between largest and second-largest eigenvalue)
    if len(eigenvalues) > 1:
        spectral_gap = np.abs(eigenvalues[0]) - np.abs(eigenvalues[1])
    else:
        spectral_gap = 0

    mo.md(f"""
    ## Spectral Analysis (Linear Algebra)

    The **adjacency matrix** $A$ encodes the network structure.

    **Eigenvalue Analysis:**
    - Largest eigenvalue $\\lambda_1$: {np.abs(eigenvalues[0]):.4f}
    - Second eigenvalue $\\lambda_2$: {np.abs(eigenvalues[1]):.4f} (if exists)
    - **Spectral gap**: {spectral_gap:.4f}

    A larger spectral gap indicates:
    - Clear community structure
    - Fast mixing (random walks converge quickly)
    - Strong connectivity

    From Perron-Frobenius theorem (networks08.ipynb):
    - For connected graphs, $\\lambda_1 > |\\lambda_i|$ for all other eigenvalues
    - The corresponding eigenvector has all positive entries
    """)
    return A, eigenvalues, eigenvectors, spectral_gap


@app.cell
def _(eigenvalues, np, go, mo):
    # Plot eigenvalue spectrum
    fig_eigen = go.Figure()

    # Real vs imaginary parts
    fig_eigen.add_trace(go.Scatter(
        x=np.real(eigenvalues[:20]),
        y=np.imag(eigenvalues[:20]),
        mode='markers',
        marker=dict(size=10, color=np.abs(eigenvalues[:20]), colorscale='Viridis'),
        text=[f'λ_{i+1} = {eigenvalues[i]:.3f}' for i in range(min(20, len(eigenvalues)))],
        hoverinfo='text',
        name='Eigenvalues'
    ))

    fig_eigen.update_layout(
        title='Eigenvalue Spectrum (Top 20)',
        xaxis_title='Real Part',
        yaxis_title='Imaginary Part',
        height=400,
    )

    mo.ui.plotly(fig_eigen)
    return fig_eigen,


@app.cell
def _(mo):
    mo.md("""
    ## Summary and Next Steps

    This analysis demonstrates how **graph theory** from CS4423 Networks applies to
    curriculum analysis:

    ### Key Findings
    1. **Central Concepts**: Topics that bridge multiple subjects (high betweenness)
    2. **Subject Clusters**: Natural groupings based on shared concepts
    3. **Prerequisite Structure**: How mathematical concepts build on each other

    ### Integration with Gaeilge Project
    - Use these centrality measures to identify **key curriculum topics**
    - Build **topic forecasting** models using Markov chains (MP307)
    - Connect to **Neo4j knowledge graph** for curriculum relationship queries

    ### Related Notebooks
    - `cross_subject_bridges.py` - Deep dive into subject projections
    - `topic_forecasting.py` - Markov chain analysis of exam topics
    - `neo4j_marimo_bridge.py` - Database connectivity utilities
    """)
    return


if __name__ == "__main__":
    app.run()
