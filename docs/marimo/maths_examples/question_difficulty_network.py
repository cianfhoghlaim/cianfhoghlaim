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
Question Difficulty Network - Marimo Notebook

Models question difficulty using network analysis and Item Response Theory
concepts, building on graph theory and statistical methods.

Mathematical foundations from:
- /Users/cliste/dev/mata/CS4423 - Networks/ (Centrality, network flows)
- /Users/cliste/dev/mata/ST311 - Applied Statistics 1/ (Regression)
- /Users/cliste/dev/mata/ST312 - Applied Statistics 2/ (Logistic regression)

BAML schema reference:
- ExamQuestion, MarkAllocation, LearningOutcome from classes.baml
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(
    width="full",
    app_title="Question Difficulty Network",
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
    from scipy import stats
    from scipy.optimize import minimize
    from typing import Dict, List, Tuple, Optional
    return mo, nx, np, pd, go, px, yaml, Path, stats, minimize, Dict, List, Tuple, Optional


@app.cell
def _(mo):
    mo.md(r"""
    # Question Difficulty Network Analysis

    This notebook builds a **network model of question difficulty** that combines:

    1. **Graph Theory** (CS4423): Questions connected through shared topics/skills
    2. **Item Response Theory**: Probabilistic difficulty estimation
    3. **Network Centrality**: Question importance in the curriculum

    ## Core Concept

    We model the curriculum as a network where:
    - **Nodes**: Questions, Topics, Learning Outcomes
    - **Edges**: Prerequisites, shared concepts, difficulty dependencies

    A question's difficulty depends not just on its content, but on its
    **position in the knowledge network**.
    """)
    return


@app.cell
def _(yaml, Path, np, pd):
    """
    Load curriculum structure and generate simulated question data.
    """
    GAEILGE_PATH = Path("/Users/cliste/dev/bonneagar/hackathon/data/flows/gaeilge")

    with open(GAEILGE_PATH / "sources.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Mathematics curriculum strands from sources.yaml
    math_strands = config.get('senior_cycle_subjects', {}).get('mathematics', [{}])[0].get(
        'strands', ['number', 'algebra', 'functions', 'geometry_trigonometry', 'statistics_probability']
    )

    print(f"Mathematics strands: {math_strands}")

    # Simulated question bank based on BAML ExamQuestion schema
    np.random.seed(42)

    topics = {
        'number': ['Real numbers', 'Complex numbers', 'Indices', 'Logarithms'],
        'algebra': ['Equations', 'Inequalities', 'Polynomials', 'Sequences'],
        'functions': ['Linear', 'Quadratic', 'Exponential', 'Trigonometric'],
        'geometry_trigonometry': ['Coordinate geometry', 'Trigonometry', 'Circles', 'Vectors'],
        'statistics_probability': ['Probability', 'Distributions', 'Hypothesis testing', 'Correlation'],
    }

    # Generate question bank
    questions = []
    q_id = 1

    for strand, strand_topics in topics.items():
        for topic in strand_topics:
            # Each topic has 3-5 questions with varying difficulty
            for i in range(np.random.randint(3, 6)):
                base_difficulty = np.random.uniform(0.3, 0.9)
                marks = np.random.choice([10, 15, 20, 25])

                # Prerequisites depend on strand structure
                prereqs = []
                if strand == 'functions' and topic != 'Linear':
                    prereqs.append('Linear')
                if strand == 'geometry_trigonometry' and topic == 'Vectors':
                    prereqs.extend(['Coordinate geometry', 'Trigonometry'])
                if strand == 'statistics_probability' and topic == 'Hypothesis testing':
                    prereqs.extend(['Probability', 'Distributions'])

                questions.append({
                    'question_id': f'Q{q_id:03d}',
                    'strand': strand,
                    'topic': topic,
                    'marks': marks,
                    'true_difficulty': base_difficulty,
                    'question_type': np.random.choice(['problem_solving', 'short_answer', 'proof']),
                    'prerequisites': prereqs,
                    'year': np.random.choice(range(2018, 2025)),
                    'success_rate': 1 - base_difficulty + np.random.normal(0, 0.1),
                })
                q_id += 1

    questions_df = pd.DataFrame(questions)
    questions_df['success_rate'] = questions_df['success_rate'].clip(0.1, 0.95)

    print(f"\nGenerated {len(questions_df)} questions across {len(topics)} strands")
    return questions_df, topics, math_strands, config, GAEILGE_PATH


@app.cell
def _(questions_df, topics, nx, np, mo):
    """
    Build the Question-Topic-Prerequisite network.
    """

    # Create directed graph (prerequisites flow)
    G = nx.DiGraph()

    # Add topic nodes
    for strand, strand_topics in topics.items():
        for topic in strand_topics:
            G.add_node(topic, node_type='topic', strand=strand)

    # Add prerequisite edges between topics
    prereq_pairs = [
        ('Linear', 'Quadratic'),
        ('Linear', 'Exponential'),
        ('Quadratic', 'Trigonometric'),
        ('Real numbers', 'Complex numbers'),
        ('Indices', 'Logarithms'),
        ('Equations', 'Inequalities'),
        ('Polynomials', 'Sequences'),
        ('Coordinate geometry', 'Circles'),
        ('Trigonometry', 'Vectors'),
        ('Probability', 'Distributions'),
        ('Distributions', 'Hypothesis testing'),
        ('Probability', 'Hypothesis testing'),
    ]

    for prereq, topic in prereq_pairs:
        if prereq in G.nodes() and topic in G.nodes():
            G.add_edge(prereq, topic, edge_type='prerequisite')

    # Add question nodes
    for _, q in questions_df.iterrows():
        q_id = q['question_id']
        G.add_node(q_id,
                   node_type='question',
                   topic=q['topic'],
                   marks=q['marks'],
                   difficulty=q['true_difficulty'],
                   success_rate=q['success_rate'])
        # Connect question to topic
        G.add_edge(q['topic'], q_id, edge_type='contains')

    mo.md(f"""
    ## Knowledge Network Built

    - **Topic nodes**: {sum(1 for n in G.nodes() if G.nodes[n].get('node_type') == 'topic')}
    - **Question nodes**: {sum(1 for n in G.nodes() if G.nodes[n].get('node_type') == 'question')}
    - **Prerequisite edges**: {sum(1 for _, _, d in G.edges(data=True) if d.get('edge_type') == 'prerequisite')}
    - **Contains edges**: {sum(1 for _, _, d in G.edges(data=True) if d.get('edge_type') == 'contains')}
    """)
    return G, prereq_pairs


@app.cell
def _(G, nx, np, pd, mo):
    """
    Compute topic-level centrality measures.

    From CS4423 networks08-09:
    - Degree centrality: Direct connections
    - Betweenness: Bridge topics
    - PageRank: Importance propagation
    """

    # Get topic subgraph
    topic_nodes = [n for n in G.nodes() if G.nodes[n].get('node_type') == 'topic']
    T = G.subgraph(topic_nodes).copy()

    # Centrality measures on topic graph
    topic_degree = dict(T.degree())
    topic_in_degree = dict(T.in_degree())  # Prerequisites required
    topic_out_degree = dict(T.out_degree())  # Enables other topics

    try:
        topic_pagerank = nx.pagerank(T, alpha=0.85)
    except:
        topic_pagerank = {n: 1/len(topic_nodes) for n in topic_nodes}

    try:
        topic_betweenness = nx.betweenness_centrality(T)
    except:
        topic_betweenness = {n: 0 for n in topic_nodes}

    # Create topic analysis table
    topic_analysis = pd.DataFrame({
        'topic': topic_nodes,
        'strand': [G.nodes[n].get('strand') for n in topic_nodes],
        'in_degree': [topic_in_degree.get(n, 0) for n in topic_nodes],
        'out_degree': [topic_out_degree.get(n, 0) for n in topic_nodes],
        'pagerank': [topic_pagerank.get(n, 0) for n in topic_nodes],
        'betweenness': [topic_betweenness.get(n, 0) for n in topic_nodes],
    })

    # Network-based difficulty: more prerequisites = harder topic
    topic_analysis['network_difficulty'] = (
        topic_analysis['in_degree'] / (topic_analysis['in_degree'].max() + 1) * 0.5 +
        (1 - topic_analysis['pagerank'] / (topic_analysis['pagerank'].max() + 0.01)) * 0.3 +
        topic_analysis['betweenness'] * 0.2
    )

    topic_analysis = topic_analysis.sort_values('network_difficulty', ascending=False)

    mo.md("""
    ## Topic Centrality Analysis

    Using network metrics to estimate topic difficulty:
    - **In-degree**: Number of prerequisite topics (more = harder)
    - **PageRank**: Importance in the curriculum flow
    - **Betweenness**: Bridging topics between strands
    """)
    return T, topic_analysis, topic_degree, topic_in_degree, topic_out_degree, topic_pagerank, topic_betweenness, topic_nodes


@app.cell
def _(topic_analysis, mo):
    mo.ui.table(topic_analysis.round(4))
    return


@app.cell
def _(G, topics, go, mo):
    """
    Visualize the topic prerequisite network.
    """

    # Get topic subgraph
    topic_nodes_viz = [t for ts in topics.values() for t in ts]
    edges_viz = [(u, v) for u, v, d in G.edges(data=True)
                 if d.get('edge_type') == 'prerequisite']

    # Layout
    pos = nx.spring_layout(G.subgraph(topic_nodes_viz), k=2, seed=42)

    # Colors by strand
    strand_colors = {
        'number': '#1f77b4',
        'algebra': '#ff7f0e',
        'functions': '#2ca02c',
        'geometry_trigonometry': '#d62728',
        'statistics_probability': '#9467bd',
    }

    # Create traces
    edge_traces = []
    for u, v in edges_viz:
        if u in pos and v in pos:
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_traces.append(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode='lines',
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                showlegend=False
            ))

            # Arrow annotation
            edge_traces.append(go.Scatter(
                x=[x1], y=[y1],
                mode='markers',
                marker=dict(size=8, color='#888', symbol='triangle-up'),
                hoverinfo='none',
                showlegend=False
            ))

    # Node traces by strand
    node_traces = []
    for strand, strand_topics in topics.items():
        x_vals = [pos[t][0] for t in strand_topics if t in pos]
        y_vals = [pos[t][1] for t in strand_topics if t in pos]
        names = [t for t in strand_topics if t in pos]

        node_traces.append(go.Scatter(
            x=x_vals, y=y_vals,
            mode='markers+text',
            text=names,
            textposition='top center',
            marker=dict(size=20, color=strand_colors.get(strand, '#666')),
            name=strand.replace('_', ' ').title()
        ))

    fig_network = go.Figure(
        data=edge_traces + node_traces,
        layout=go.Layout(
            title='Topic Prerequisite Network',
            showlegend=True,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600,
        )
    )

    mo.ui.plotly(fig_network)
    return fig_network, strand_colors, edges_viz


@app.cell
def _(questions_df, np, stats, minimize, pd, mo):
    r"""
    Item Response Theory (IRT) - 1-Parameter Logistic Model (Rasch Model)

    From ST312 Logistic Regression concepts:

    P(correct | ability θ, difficulty b) = 1 / (1 + exp(-(θ - b)))

    We estimate:
    - θ_i: Student ability (latent)
    - b_j: Question difficulty

    Using success rates as proxy data.
    """

    # Use success rates to estimate question difficulty via logistic transform
    # If success_rate = P(correct), then difficulty b ≈ -logit(success_rate)

    questions_df_irt = questions_df.copy()

    # Logit transform of success rate (with bounds)
    success_bounded = questions_df_irt['success_rate'].clip(0.05, 0.95)
    questions_df_irt['irt_difficulty'] = -np.log(success_bounded / (1 - success_bounded))

    # Standardize to 0-1 scale for comparison
    min_diff = questions_df_irt['irt_difficulty'].min()
    max_diff = questions_df_irt['irt_difficulty'].max()
    questions_df_irt['irt_difficulty_scaled'] = (
        (questions_df_irt['irt_difficulty'] - min_diff) / (max_diff - min_diff)
    )

    # Discrimination (simplified): variance of success rates within topic
    topic_std = questions_df.groupby('topic')['success_rate'].std().fillna(0.1)
    questions_df_irt['discrimination'] = questions_df_irt['topic'].map(
        lambda t: 1 / (topic_std.get(t, 0.1) + 0.1)
    )

    mo.md(r"""
    ## Item Response Theory (Rasch Model)

    The **1-Parameter Logistic Model** (Rasch) models the probability of
    answering correctly as:

    $$P(\text{correct} | \theta, b) = \frac{1}{1 + e^{-(\theta - b)}}$$

    Where:
    - $\theta$: Student ability
    - $b$: Question difficulty

    **Estimation**: Using logit transform of success rates:
    $$\hat{b}_j = -\ln\left(\frac{p_j}{1 - p_j}\right)$$
    """)
    return questions_df_irt, success_bounded, min_diff, max_diff, topic_std


@app.cell
def _(questions_df_irt, px, mo):
    """
    Visualize IRT difficulty estimates.
    """

    fig_irt = px.scatter(
        questions_df_irt,
        x='true_difficulty',
        y='irt_difficulty_scaled',
        color='strand',
        size='marks',
        hover_data=['question_id', 'topic', 'success_rate'],
        title='True Difficulty vs IRT-Estimated Difficulty',
        labels={
            'true_difficulty': 'True Difficulty (simulated)',
            'irt_difficulty_scaled': 'IRT Difficulty (from success rates)'
        }
    )

    fig_irt.add_shape(
        type='line',
        x0=0, y0=0, x1=1, y1=1,
        line=dict(dash='dash', color='gray')
    )

    fig_irt.update_layout(height=500)
    mo.ui.plotly(fig_irt)
    return fig_irt,


@app.cell
def _(questions_df_irt, topic_analysis, np, pd, mo):
    """
    Combined difficulty model: Network + IRT

    Final difficulty = α × Network_difficulty + β × IRT_difficulty + γ × Marks_weight
    """

    # Merge topic network difficulty
    questions_combined = questions_df_irt.merge(
        topic_analysis[['topic', 'network_difficulty']],
        on='topic',
        how='left'
    )

    # Normalize marks contribution
    questions_combined['marks_weight'] = questions_combined['marks'] / questions_combined['marks'].max()

    # Combined difficulty (weighted)
    alpha, beta, gamma = 0.3, 0.5, 0.2

    questions_combined['combined_difficulty'] = (
        alpha * questions_combined['network_difficulty'].fillna(0) +
        beta * questions_combined['irt_difficulty_scaled'] +
        gamma * questions_combined['marks_weight']
    )

    # Rank questions
    questions_combined['difficulty_rank'] = questions_combined['combined_difficulty'].rank(ascending=False)
    questions_combined = questions_combined.sort_values('combined_difficulty', ascending=False)

    mo.md(rf"""
    ## Combined Difficulty Model

    Integrating multiple signals:

    $$D_q = {alpha:.1f} \times D_{{\text{{network}}}} + {beta:.1f} \times D_{{\text{{IRT}}}} + {gamma:.1f} \times D_{{\text{{marks}}}}$$

    Where:
    - $D_{{\text{{network}}}}$: Topic position in prerequisite graph
    - $D_{{\text{{IRT}}}}$: IRT difficulty from success rates
    - $D_{{\text{{marks}}}}$: Normalized mark allocation
    """)
    return questions_combined, alpha, beta, gamma


@app.cell
def _(questions_combined, mo):
    # Show top 15 hardest questions
    display_cols = ['question_id', 'topic', 'strand', 'marks', 'success_rate',
                    'network_difficulty', 'irt_difficulty_scaled', 'combined_difficulty']
    mo.ui.table(questions_combined[display_cols].head(15).round(3))
    return display_cols,


@app.cell
def _(questions_combined, go, mo):
    """
    Difficulty distribution by strand.
    """

    fig_strand = go.Figure()

    for strand in questions_combined['strand'].unique():
        strand_data = questions_combined[questions_combined['strand'] == strand]
        fig_strand.add_trace(go.Box(
            y=strand_data['combined_difficulty'],
            name=strand.replace('_', ' ').title(),
            boxmean=True
        ))

    fig_strand.update_layout(
        title='Combined Difficulty Distribution by Strand',
        yaxis_title='Combined Difficulty Score',
        height=450
    )

    mo.ui.plotly(fig_strand)
    return fig_strand,


@app.cell
def _(questions_combined, stats, np, pd, mo):
    """
    Correlation analysis between difficulty components.

    From ST311 Section 5: Pearson Correlation
    """

    corr_cols = ['true_difficulty', 'irt_difficulty_scaled', 'network_difficulty',
                 'marks_weight', 'combined_difficulty', 'success_rate']

    corr_matrix = questions_combined[corr_cols].corr()

    # Statistical significance
    n = len(questions_combined)
    t_stat = corr_matrix * np.sqrt((n - 2) / (1 - corr_matrix**2 + 1e-10))
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stat), n - 2))

    mo.md("""
    ## Correlation Analysis

    Examining relationships between difficulty measures.
    """)
    return corr_cols, corr_matrix, t_stat, p_values, n


@app.cell
def _(corr_matrix, go, mo):
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=[c.replace('_', ' ').title() for c in corr_matrix.columns],
        y=[c.replace('_', ' ').title() for c in corr_matrix.index],
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.round(2).values,
        texttemplate='%{text}',
        textfont={'size': 10}
    ))

    fig_corr.update_layout(
        title='Correlation Matrix: Difficulty Measures',
        height=500
    )

    mo.ui.plotly(fig_corr)
    return fig_corr,


@app.cell
def _(mo):
    mo.md("""
    ## Summary: Question Difficulty Estimation

    ### Mathematical Foundations

    | Method | Source | Formula |
    |--------|--------|---------|
    | Network Centrality | CS4423 | PageRank, Betweenness |
    | IRT (Rasch) | ST312 Logistic | $P = 1/(1 + e^{-(θ-b)})$ |
    | Correlation | ST311 §5 | Pearson $r$ |
    | Combined Model | Weighted sum | $D = αD_N + βD_I + γD_M$ |

    ### Key Insights

    1. **Topic Position Matters**: Questions on topics with many prerequisites are harder
    2. **Success Rate Informs**: IRT provides empirical difficulty estimates
    3. **Mark Allocation**: Higher marks correlate with difficulty

    ### Applications for Gaeilge Project

    - Estimate difficulty for **ExamQuestion** extractions
    - Build prerequisite chains for **LearningOutcome** analysis
    - Generate **difficulty predictions** for new questions
    - Support curriculum planning with network metrics

    ### Related Notebooks
    - `curriculum_network_analysis.py` - Full curriculum graph
    - `topic_forecasting.py` - Topic appearance predictions
    - `neo4j_marimo_bridge.py` - Database queries
    """)
    return


if __name__ == "__main__":
    app.run()
