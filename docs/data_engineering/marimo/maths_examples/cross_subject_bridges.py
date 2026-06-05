# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "networkx>=3.0",
#     "numpy>=1.24",
#     "pandas>=2.0",
#     "plotly>=5.0",
#     "pyyaml>=6.0",
#     "scipy>=1.10",
# ]
# ///
"""
Cross-Subject Bridges Analysis - Marimo Notebook

Deep analysis of bipartite graph projections to identify how subjects
connect through shared mathematical and scientific concepts.

Mathematical foundations from:
- /Users/cliste/dev/mata/CS4423 - Networks/Notebooks/networks04.ipynb (Bipartite Graphs)
- /Users/cliste/dev/mata/CS4423 - Networks/Notebooks/networks12.ipynb (Clustering)

Data source:
- /Users/cliste/dev/bonneagar/hackathon/data/flows/gaeilge/sources.yaml
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(
    width="full",
    app_title="Cross-Subject Bridges",
)


@app.cell
def _():
    import marimo as mo
    import networkx as nx
    import numpy as np
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    import yaml
    from pathlib import Path
    from scipy import sparse
    from collections import Counter
    return mo, nx, np, pd, go, px, yaml, Path, sparse, Counter


@app.cell
def _(mo):
    mo.md("""
    # Cross-Subject Bridges Analysis

    This notebook performs **bipartite graph projections** to analyze how
    subjects in the Irish curriculum connect through shared concepts.

    ## Key Concepts from networks04.ipynb

    **Bipartite Graphs**: Graphs where nodes can be partitioned into two sets,
    with edges only between sets (not within).

    $$G = (X \\cup Y, E) \\text{ where } E \\subseteq X \\times Y$$

    **Biadjacency Matrix**: For bipartite graph with parts $X$ (m nodes) and $Y$ (n nodes):
    $$B \\in \\{0,1\\}^{m \\times n}$$
    where $B_{ij} = 1$ if there's an edge between $x_i$ and $y_j$.

    **Projection**: Create single-mode network from bipartite:
    - Subject projection: $P_X = B B^T$ (subjects connected by shared concepts)
    - Concept projection: $P_Y = B^T B$ (concepts connected by shared subjects)
    """)
    return


@app.cell
def _(yaml, Path):
    # Load curriculum data
    GAEILGE_PATH = Path("/Users/cliste/dev/bonneagar/hackathon/data/flows/gaeilge")

    with open(GAEILGE_PATH / "sources.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Extract cross-subject concepts with full details
    cross_concepts = config.get('cross_subject_concepts', {})
    senior_subjects = config.get('senior_cycle_subjects', {})

    print(f"Loaded {len(cross_concepts)} cross-subject concepts")
    print(f"Loaded {sum(len(v) for v in senior_subjects.values())} subjects across {len(senior_subjects)} categories")
    return config, cross_concepts, senior_subjects, GAEILGE_PATH


@app.cell
def _(cross_concepts, senior_subjects, nx, np, mo):
    """
    Build the bipartite graph with full metadata.
    """

    # Create bipartite graph
    B = nx.Graph()

    # Subject metadata mapping
    subject_metadata = {}
    all_subjects = []

    for category, subject_list in senior_subjects.items():
        for subj in subject_list:
            name = subj['name']
            all_subjects.append(name)
            subject_metadata[name] = {
                'category': category,
                'code': subj.get('code', ''),
                'levels': subj.get('levels', []),
                'has_oral': subj.get('has_oral', False),
                'has_practical': subj.get('has_practical', False),
            }
            B.add_node(name, bipartite=0, **subject_metadata[name])

    # Concept metadata
    concept_metadata = {}
    all_concepts = []

    for concept, details in cross_concepts.items():
        all_concepts.append(concept)
        concept_metadata[concept] = {
            'description': details.get('description', ''),
            'bridging_strategy': details.get('bridging_strategy', ''),
        }
        B.add_node(concept, bipartite=1, **concept_metadata[concept])

        # Add edges from concept to subjects
        for subj_ref in details.get('subjects', []):
            # Match subject reference to actual name
            for name in all_subjects:
                normalized_ref = subj_ref.lower().replace('_', ' ')
                normalized_name = name.lower()
                if normalized_ref == normalized_name or \
                   normalized_ref.replace(' ', '_') == name.lower().replace(' ', '_'):
                    B.add_edge(concept, name)
                    break

    # Also add concepts from individual subject definitions
    for category, subject_list in senior_subjects.items():
        for subj in subject_list:
            name = subj['name']
            for concept in subj.get('cross_subject_concepts', []):
                if concept not in all_concepts:
                    all_concepts.append(concept)
                    B.add_node(concept, bipartite=1, description='')
                B.add_edge(concept, name)

            # Also check requires_math_concepts
            for concept in subj.get('requires_math_concepts', []):
                concept_node = f"math:{concept}"
                if concept_node not in all_concepts:
                    all_concepts.append(concept_node)
                    B.add_node(concept_node, bipartite=1, description=f'Mathematical concept: {concept}')
                B.add_edge(concept_node, name)

    mo.md(f"""
    ## Bipartite Graph Constructed

    | Component | Count |
    |-----------|-------|
    | Subjects | {len(all_subjects)} |
    | Concepts | {len(all_concepts)} |
    | Edges | {B.number_of_edges()} |
    | Density | {nx.density(B):.4f} |
    """)
    return B, all_subjects, all_concepts, subject_metadata, concept_metadata


@app.cell
def _(B, all_subjects, all_concepts, nx, np, sparse, mo):
    """
    Construct the biadjacency matrix B and compute projections.

    From networks04.ipynb:
    - B: biadjacency matrix (subjects x concepts)
    - P_subjects = B @ B.T (subject similarity via shared concepts)
    - P_concepts = B.T @ B (concept similarity via shared subjects)
    """

    # Build ordered node lists
    subject_list = sorted([n for n in B.nodes() if B.nodes[n].get('bipartite') == 0])
    concept_list = sorted([n for n in B.nodes() if B.nodes[n].get('bipartite') == 1])

    m = len(subject_list)  # Number of subjects
    n = len(concept_list)  # Number of concepts

    # Create biadjacency matrix
    subject_idx = {s: i for i, s in enumerate(subject_list)}
    concept_idx = {c: i for i, c in enumerate(concept_list)}

    # Initialize sparse matrix
    row_indices = []
    col_indices = []

    for edge in B.edges():
        n1, n2 = edge
        if B.nodes[n1].get('bipartite') == 0:
            subj, conc = n1, n2
        else:
            subj, conc = n2, n1

        if subj in subject_idx and conc in concept_idx:
            row_indices.append(subject_idx[subj])
            col_indices.append(concept_idx[conc])

    # Biadjacency matrix (subjects x concepts)
    biadj_matrix = sparse.csr_matrix(
        (np.ones(len(row_indices)), (row_indices, col_indices)),
        shape=(m, n)
    )

    # Compute projections
    # P_subjects[i,j] = number of concepts shared between subject i and j
    P_subjects = (biadj_matrix @ biadj_matrix.T).toarray()

    # P_concepts[i,j] = number of subjects that share concepts i and j
    P_concepts = (biadj_matrix.T @ biadj_matrix).toarray()

    mo.md(f"""
    ## Biadjacency Matrix

    $$B \\in \\{{0,1\\}}^{{{m} \\times {n}}}$$

    **Subject Projection** $P_X = B B^T$:
    - Shape: ${m} \\times {m}$
    - $P_X[i,j]$ = number of shared concepts between subjects $i$ and $j$

    **Concept Projection** $P_Y = B^T B$:
    - Shape: ${n} \\times {n}$
    - $P_Y[i,j]$ = number of subjects sharing both concepts
    """)
    return (biadj_matrix, P_subjects, P_concepts, subject_list, concept_list,
            subject_idx, concept_idx, m, n)


@app.cell
def _(P_subjects, subject_list, nx, pd, mo):
    """
    Analyze subject projection graph.
    """

    # Create NetworkX graph from projection matrix
    G_subjects = nx.Graph()

    for i, subj1 in enumerate(subject_list):
        G_subjects.add_node(subj1)
        for j, subj2 in enumerate(subject_list):
            if i < j and P_subjects[i, j] > 0:
                G_subjects.add_edge(subj1, subj2, weight=P_subjects[i, j])

    # Compute centrality on projection
    if G_subjects.number_of_edges() > 0:
        degree_cent = nx.degree_centrality(G_subjects)
        weighted_degree = {n: sum(d['weight'] for _, _, d in G_subjects.edges(n, data=True))
                          for n in G_subjects.nodes()}

        try:
            eigen_cent = nx.eigenvector_centrality(G_subjects, weight='weight', max_iter=1000)
        except:
            eigen_cent = {n: 0 for n in G_subjects.nodes()}

        between_cent = nx.betweenness_centrality(G_subjects, weight='weight')

        subject_analysis = pd.DataFrame({
            'subject': list(G_subjects.nodes()),
            'degree': [G_subjects.degree(n) for n in G_subjects.nodes()],
            'weighted_degree': [weighted_degree[n] for n in G_subjects.nodes()],
            'eigenvector': [eigen_cent.get(n, 0) for n in G_subjects.nodes()],
            'betweenness': [between_cent.get(n, 0) for n in G_subjects.nodes()],
        }).sort_values('weighted_degree', ascending=False)

        mo.md(f"""
        ## Subject Projection Analysis

        Subjects connected by **shared cross-curricular concepts**.

        - Connected pairs: {G_subjects.number_of_edges()}
        - Average shared concepts per pair: {np.mean([d['weight'] for _, _, d in G_subjects.edges(data=True)]):.2f}
        """)
    else:
        subject_analysis = pd.DataFrame()
        mo.md("No edges in subject projection")

    return G_subjects, subject_analysis, degree_cent, weighted_degree, eigen_cent, between_cent


@app.cell
def _(subject_analysis, mo):
    if len(subject_analysis) > 0:
        mo.md("### Most Connected Subjects")
    return


@app.cell
def _(subject_analysis, mo):
    if len(subject_analysis) > 0:
        mo.ui.table(subject_analysis.head(15))
    return


@app.cell
def _(G_subjects, P_subjects, subject_list, go, mo):
    """
    Heatmap visualization of subject-subject connections.
    """

    # Create heatmap
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=P_subjects,
        x=subject_list,
        y=subject_list,
        colorscale='Blues',
        text=P_subjects.astype(int),
        texttemplate='%{text}',
        textfont={'size': 8},
        hovertemplate='%{x} ↔ %{y}<br>Shared concepts: %{z}<extra></extra>'
    ))

    fig_heatmap.update_layout(
        title='Subject-Subject Connections (Shared Concepts)',
        xaxis_title='Subject',
        yaxis_title='Subject',
        height=700,
        xaxis={'tickangle': 45},
    )

    mo.ui.plotly(fig_heatmap)
    return fig_heatmap,


@app.cell
def _(P_concepts, concept_list, go, mo):
    """
    Concept-concept projection analysis.
    """

    # Create heatmap for concept relationships
    fig_concept = go.Figure(data=go.Heatmap(
        z=P_concepts,
        x=concept_list,
        y=concept_list,
        colorscale='Oranges',
        text=P_concepts.astype(int),
        texttemplate='%{text}',
        textfont={'size': 10},
        hovertemplate='%{x} ↔ %{y}<br>Shared by subjects: %{z}<extra></extra>'
    ))

    fig_concept.update_layout(
        title='Concept-Concept Connections (Shared Subjects)',
        xaxis_title='Concept',
        yaxis_title='Concept',
        height=500,
        xaxis={'tickangle': 45},
    )

    mo.ui.plotly(fig_concept)
    return fig_concept,


@app.cell
def _(G_subjects, subject_metadata, nx, go, mo):
    """
    Interactive network visualization with category coloring.
    """

    # Color by category
    category_colors = {
        'languages': '#1f77b4',
        'mathematics': '#ff7f0e',
        'sciences': '#2ca02c',
        'humanities': '#d62728',
        'business': '#9467bd',
        'technology': '#8c564b',
        'arts': '#e377c2',
    }

    pos = nx.spring_layout(G_subjects, k=3, iterations=100, seed=42)

    # Create traces by category
    traces = []

    # Edge trace
    edge_x, edge_y = [], []
    for edge in G_subjects.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    traces.append(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines',
        name='Connections'
    ))

    # Node traces by category
    for category, color in category_colors.items():
        nodes = [n for n in G_subjects.nodes()
                 if subject_metadata.get(n, {}).get('category') == category]
        if nodes:
            node_x = [pos[n][0] for n in nodes]
            node_y = [pos[n][1] for n in nodes]
            node_text = [f"{n}<br>Degree: {G_subjects.degree(n)}" for n in nodes]

            traces.append(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=nodes,
                textposition='top center',
                hovertext=node_text,
                hoverinfo='text',
                marker=dict(size=15, color=color, line=dict(width=2, color='white')),
                name=category.title()
            ))

    fig_network = go.Figure(
        data=traces,
        layout=go.Layout(
            title='Subject Network (Colored by Category)',
            showlegend=True,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=700,
        )
    )

    mo.ui.plotly(fig_network)
    return fig_network, category_colors, pos


@app.cell
def _(G_subjects, nx, mo):
    """
    Community detection using Louvain method.
    """
    try:
        from networkx.algorithms import community

        # Detect communities
        communities = community.louvain_communities(G_subjects, weight='weight', seed=42)

        community_assignments = {}
        for i, comm in enumerate(communities):
            for node in comm:
                community_assignments[node] = i

        mo.md(f"""
        ## Community Detection (Louvain Algorithm)

        Found **{len(communities)} communities** in the subject network.

        Communities represent natural groupings of subjects based on shared concepts.
        """)

        for i, comm in enumerate(communities):
            print(f"\n**Community {i+1}** ({len(comm)} subjects):")
            print(f"  {', '.join(sorted(comm))}")

    except Exception as e:
        communities = []
        community_assignments = {}
        mo.md(f"Community detection not available: {e}")

    return communities, community_assignments


@app.cell
def _(B, all_subjects, all_concepts, nx, pd, mo):
    """
    Identify bridge concepts - concepts that connect otherwise separate subjects.
    """

    # For each concept, find which subjects it connects
    bridge_analysis = []

    for concept in all_concepts:
        if concept in B.nodes():
            neighbors = list(B.neighbors(concept))
            subject_neighbors = [n for n in neighbors if n in all_subjects]

            if len(subject_neighbors) >= 2:
                # Get categories of connected subjects
                categories = set()
                for subj in subject_neighbors:
                    cat = B.nodes[subj].get('category', 'unknown')
                    categories.add(cat)

                bridge_analysis.append({
                    'concept': concept,
                    'subjects_connected': len(subject_neighbors),
                    'categories_bridged': len(categories),
                    'subjects': ', '.join(subject_neighbors[:5]),
                    'categories': ', '.join(categories),
                })

    bridge_df = pd.DataFrame(bridge_analysis).sort_values(
        ['categories_bridged', 'subjects_connected'],
        ascending=False
    )

    mo.md("""
    ## Bridge Concepts Analysis

    Concepts that bridge multiple subject categories are particularly valuable
    for cross-curricular learning.
    """)
    return bridge_analysis, bridge_df


@app.cell
def _(bridge_df, mo):
    mo.ui.table(bridge_df.head(10))
    return


@app.cell
def _(mo):
    mo.md("""
    ## Summary: Cross-Subject Integration Insights

    ### Key Findings

    1. **High-Value Bridge Concepts**: Mathematics-based concepts (statistics, calculus)
       bridge the most subject categories

    2. **Natural Clusters**: Subjects form communities based on shared conceptual foundations

    3. **Curriculum Design Implications**:
       - Students mastering bridge concepts gain transferable skills
       - Cross-curricular teaching opportunities exist between connected subjects

    ### Applications for Gaeilge Project

    - **Question Difficulty Estimation**: Questions involving bridge concepts may
      transfer knowledge across subjects
    - **Curriculum Gap Analysis**: Identify missing connections between subjects
    - **Study Path Optimization**: Suggest efficient learning sequences

    ### Related Notebooks
    - `curriculum_network_analysis.py` - Overview of curriculum structure
    - `topic_forecasting.py` - Predict exam topics using Markov chains
    """)
    return


if __name__ == "__main__":
    app.run()
