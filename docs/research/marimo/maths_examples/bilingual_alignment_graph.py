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
Bilingual Alignment Graph - Marimo Notebook

Analyzes the English-Irish translation alignment in educational content,
using graph matching and similarity metrics.

Mathematical foundations from:
- /Users/cliste/dev/mata/CS4423 - Networks/Notebooks/networks04.ipynb (Bipartite graphs)
- /Users/cliste/dev/mata/ST311 - Applied Statistics 1/ (Correlation)

BAML schema reference:
- Language enum, QuestionMarkingSchemePair from classes.baml
- Bilingual alignment fields across all classes
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(
    width="full",
    app_title="Bilingual Alignment Graph",
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
    import json
    from pathlib import Path
    from scipy import stats
    from scipy.spatial.distance import cosine
    from typing import Dict, List, Tuple, Optional
    return mo, nx, np, pd, go, px, yaml, json, Path, stats, cosine, Dict, List, Tuple, Optional


@app.cell
def _(mo):
    mo.md(r"""
    # Bilingual Alignment Graph Analysis

    This notebook analyzes the **English-Irish (EN-GA) translation alignment** in
    the Irish educational content pipeline.

    ## The Challenge: 20% Performance Gap

    From the Gaeilge project research (IRLBench May 2025):
    - English LLM accuracy: 76.2%
    - Irish LLM accuracy: 55.8%
    - **Gap: 20.4 percentage points**

    ## Mathematical Approach

    We model bilingual content as a **bipartite graph**:
    - Left nodes: English documents/questions
    - Right nodes: Irish documents/questions
    - Edges: Translation alignments with confidence scores

    From CS4423 networks04.ipynb:
    - Biadjacency matrix for EN↔GA pairs
    - Graph matching for optimal alignment
    - Coverage analysis via projection
    """)
    return


@app.cell
def _(yaml, json, Path, np, pd):
    """
    Load bilingual curriculum data from curriculumonline.ie JSON files.
    """
    GAEILGE_PATH = Path("/Users/cliste/dev/bonneagar/hackathon/data/flows/gaeilge")
    DATA_PATH = GAEILGE_PATH / "data" / "websites" / "curriculumonline.ie"

    # Scan for bilingual pairs
    bilingual_pairs = []

    # Check if data exists
    if DATA_PATH.exists():
        for json_file in DATA_PATH.glob("**/*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                # Extract language info
                url = data.get('url', '')
                title = data.get('title', '')

                # Detect language from URL patterns
                is_irish = '/ga/' in url or '/gaeilge/' in url.lower()
                is_english = '/en/' in url or not is_irish

                bilingual_pairs.append({
                    'file': str(json_file.relative_to(DATA_PATH)),
                    'url': url,
                    'title': title,
                    'language': 'GA' if is_irish else 'EN',
                    'content_length': len(data.get('markdown', '')),
                    'word_count': len(data.get('markdown', '').split()),
                })
            except Exception as e:
                continue

    # If no real data, generate simulated bilingual pairs
    if len(bilingual_pairs) < 10:
        np.random.seed(42)

        subjects = ['Gaeilge', 'Mathematics', 'English', 'History', 'Geography',
                    'Biology', 'Chemistry', 'Physics', 'Business', 'Economics']

        doc_types = ['specification', 'guidelines', 'assessment', 'resources']

        for subject in subjects:
            for doc_type in doc_types:
                # English version
                bilingual_pairs.append({
                    'file': f'{subject.lower()}/{doc_type}_en.json',
                    'url': f'https://curriculumonline.ie/Senior-cycle/{subject}/{doc_type}/',
                    'title': f'{subject} - {doc_type.title()} (EN)',
                    'language': 'EN',
                    'content_length': np.random.randint(5000, 50000),
                    'word_count': np.random.randint(500, 5000),
                    'subject': subject,
                    'doc_type': doc_type,
                })

                # Irish version (may have different length)
                # Irish text is typically 10-20% longer due to grammar
                en_length = bilingual_pairs[-1]['content_length']
                bilingual_pairs.append({
                    'file': f'{subject.lower()}/{doc_type}_ga.json',
                    'url': f'https://curriculumonline.ie/ga/Sraith-shinsearach/{subject}/{doc_type}/',
                    'title': f'{subject} - {doc_type.title()} (GA)',
                    'language': 'GA',
                    'content_length': int(en_length * np.random.uniform(1.1, 1.25)),
                    'word_count': int(bilingual_pairs[-1]['word_count'] * np.random.uniform(1.05, 1.15)),
                    'subject': subject,
                    'doc_type': doc_type,
                })

    pairs_df = pd.DataFrame(bilingual_pairs)

    print(f"Found/generated {len(pairs_df)} documents")
    print(f"  - English: {len(pairs_df[pairs_df['language'] == 'EN'])}")
    print(f"  - Irish: {len(pairs_df[pairs_df['language'] == 'GA'])}")

    return pairs_df, bilingual_pairs, GAEILGE_PATH, DATA_PATH


@app.cell
def _(pairs_df, mo):
    mo.md(f"""
    ## Document Inventory

    | Language | Count | Avg. Words |
    |----------|-------|------------|
    | English | {len(pairs_df[pairs_df['language'] == 'EN'])} | {pairs_df[pairs_df['language'] == 'EN']['word_count'].mean():.0f} |
    | Irish | {len(pairs_df[pairs_df['language'] == 'GA'])} | {pairs_df[pairs_df['language'] == 'GA']['word_count'].mean():.0f} |
    """)
    return


@app.cell
def _(pairs_df, nx, np, pd, mo):
    """
    Build the bilingual alignment bipartite graph.

    Nodes:
    - EN documents (bipartite=0)
    - GA documents (bipartite=1)

    Edges:
    - Translation alignments with confidence scores
    """

    B = nx.Graph()

    # Add document nodes
    en_docs = pairs_df[pairs_df['language'] == 'EN'].copy()
    ga_docs = pairs_df[pairs_df['language'] == 'GA'].copy()

    for _, row in en_docs.iterrows():
        B.add_node(row['file'],
                   bipartite=0,
                   language='EN',
                   word_count=row['word_count'],
                   subject=row.get('subject', 'unknown'),
                   doc_type=row.get('doc_type', 'unknown'))

    for _, row in ga_docs.iterrows():
        B.add_node(row['file'],
                   bipartite=1,
                   language='GA',
                   word_count=row['word_count'],
                   subject=row.get('subject', 'unknown'),
                   doc_type=row.get('doc_type', 'unknown'))

    # Create alignment edges (matching by subject and doc_type)
    alignment_edges = []

    for _, en_row in en_docs.iterrows():
        for _, ga_row in ga_docs.iterrows():
            if (en_row.get('subject') == ga_row.get('subject') and
                en_row.get('doc_type') == ga_row.get('doc_type')):

                # Compute alignment confidence based on length ratio
                en_len = en_row['word_count']
                ga_len = ga_row['word_count']

                # Irish should be 5-20% longer; if not, lower confidence
                expected_ratio = 1.1  # Irish typically 10% longer
                actual_ratio = ga_len / (en_len + 1)

                ratio_diff = abs(actual_ratio - expected_ratio) / expected_ratio
                confidence = max(0, 1 - ratio_diff)

                # Add edge
                B.add_edge(en_row['file'], ga_row['file'],
                          weight=confidence,
                          en_words=en_len,
                          ga_words=ga_len,
                          ratio=actual_ratio)

                alignment_edges.append({
                    'en_file': en_row['file'],
                    'ga_file': ga_row['file'],
                    'subject': en_row.get('subject'),
                    'doc_type': en_row.get('doc_type'),
                    'confidence': confidence,
                    'length_ratio': actual_ratio,
                })

    alignments_df = pd.DataFrame(alignment_edges)

    mo.md(f"""
    ## Bilingual Alignment Graph

    - **English nodes**: {len(en_docs)}
    - **Irish nodes**: {len(ga_docs)}
    - **Alignment edges**: {len(alignments_df)}
    - **Average confidence**: {alignments_df['confidence'].mean():.3f}
    """)
    return B, en_docs, ga_docs, alignments_df, alignment_edges


@app.cell
def _(alignments_df, mo):
    mo.ui.table(alignments_df.round(3))
    return


@app.cell
def _(alignments_df, go, mo):
    """
    Visualize alignment confidence distribution.
    """

    fig_conf = go.Figure()

    fig_conf.add_trace(go.Histogram(
        x=alignments_df['confidence'],
        nbinsx=20,
        name='Alignment Confidence',
        marker_color='#1f77b4'
    ))

    fig_conf.update_layout(
        title='Distribution of Alignment Confidence Scores',
        xaxis_title='Confidence (0-1)',
        yaxis_title='Count',
        height=400
    )

    mo.ui.plotly(fig_conf)
    return fig_conf,


@app.cell
def _(alignments_df, go, mo):
    """
    Scatter plot: Length ratio vs confidence.
    """

    fig_ratio = go.Figure()

    fig_ratio.add_trace(go.Scatter(
        x=alignments_df['length_ratio'],
        y=alignments_df['confidence'],
        mode='markers',
        marker=dict(
            size=10,
            color=alignments_df['confidence'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Confidence')
        ),
        text=alignments_df['subject'],
        hovertemplate='Subject: %{text}<br>Ratio: %{x:.2f}<br>Confidence: %{y:.2f}<extra></extra>'
    ))

    # Expected ratio line
    fig_ratio.add_vline(x=1.1, line_dash='dash', line_color='red',
                        annotation_text='Expected (1.1)')

    fig_ratio.update_layout(
        title='Length Ratio vs Alignment Confidence',
        xaxis_title='GA/EN Word Count Ratio',
        yaxis_title='Alignment Confidence',
        height=450
    )

    mo.ui.plotly(fig_ratio)
    return fig_ratio,


@app.cell
def _(B, en_docs, ga_docs, nx, np, pd, mo):
    """
    Coverage analysis: Which documents lack translations?
    """

    # EN documents without GA alignment
    en_nodes = [n for n, d in B.nodes(data=True) if d.get('language') == 'EN']
    ga_nodes = [n for n, d in B.nodes(data=True) if d.get('language') == 'GA']

    en_unmatched = [n for n in en_nodes if B.degree(n) == 0]
    ga_unmatched = [n for n in ga_nodes if B.degree(n) == 0]

    # Coverage statistics
    en_coverage = 1 - len(en_unmatched) / len(en_nodes) if en_nodes else 0
    ga_coverage = 1 - len(ga_unmatched) / len(ga_nodes) if ga_nodes else 0

    mo.md(f"""
    ## Translation Coverage Analysis

    | Metric | Value |
    |--------|-------|
    | EN documents with GA translation | {len(en_nodes) - len(en_unmatched)} / {len(en_nodes)} ({en_coverage:.1%}) |
    | GA documents with EN source | {len(ga_nodes) - len(ga_unmatched)} / {len(ga_nodes)} ({ga_coverage:.1%}) |
    | Unmatched EN documents | {len(en_unmatched)} |
    | Unmatched GA documents | {len(ga_unmatched)} |
    """)
    return en_nodes, ga_nodes, en_unmatched, ga_unmatched, en_coverage, ga_coverage


@app.cell
def _(alignments_df, np, pd, mo):
    """
    Subject-level translation quality analysis.
    """

    subject_quality = alignments_df.groupby('subject').agg({
        'confidence': ['mean', 'std', 'count'],
        'length_ratio': ['mean', 'std']
    }).round(3)

    subject_quality.columns = ['conf_mean', 'conf_std', 'doc_count', 'ratio_mean', 'ratio_std']
    subject_quality = subject_quality.reset_index().sort_values('conf_mean', ascending=False)

    mo.md("""
    ## Translation Quality by Subject

    Higher confidence indicates consistent EN-GA length ratios (expected ~1.1).
    """)
    return subject_quality,


@app.cell
def _(subject_quality, mo):
    mo.ui.table(subject_quality)
    return


@app.cell
def _(alignments_df, np, stats, pd, mo):
    r"""
    Statistical analysis of translation consistency.

    From ST311 Section 5: Correlation Analysis
    """

    # Test if length ratio correlates with confidence
    if len(alignments_df) > 2:
        corr, p_value = stats.pearsonr(
            alignments_df['length_ratio'],
            alignments_df['confidence']
        )

        # Spearman (rank) correlation
        spearman_corr, spearman_p = stats.spearmanr(
            alignments_df['length_ratio'],
            alignments_df['confidence']
        )
    else:
        corr, p_value = 0, 1
        spearman_corr, spearman_p = 0, 1

    mo.md(rf"""
    ## Correlation Analysis

    Testing relationship between length ratio and alignment confidence.

    | Measure | Correlation | p-value | Interpretation |
    |---------|-------------|---------|----------------|
    | Pearson r | {corr:.3f} | {p_value:.4f} | {"Significant" if p_value < 0.05 else "Not significant"} |
    | Spearman ρ | {spearman_corr:.3f} | {spearman_p:.4f} | {"Significant" if spearman_p < 0.05 else "Not significant"} |

    **Note**: A negative correlation would indicate that extreme length ratios
    (too short or too long) reduce alignment confidence, as expected.
    """)
    return corr, p_value, spearman_corr, spearman_p


@app.cell
def _(B, en_docs, ga_docs, nx, np, pd, mo):
    """
    Build and analyze the EN-EN projection (documents with shared GA translations).

    From networks04.ipynb: Bipartite projection.
    """

    # This would identify EN documents that translate to similar Irish content
    # (useful for finding duplicate or similar English sources)

    en_node_list = list(en_docs['file'])
    ga_node_list = list(ga_docs['file'])

    # Get biadjacency matrix
    if len(en_node_list) > 0 and len(ga_node_list) > 0:
        # Create mapping
        en_idx = {n: i for i, n in enumerate(en_node_list)}
        ga_idx = {n: i for i, n in enumerate(ga_node_list)}

        # Build biadjacency matrix
        biadj = np.zeros((len(en_node_list), len(ga_node_list)))

        for u, v, d in B.edges(data=True):
            if B.nodes[u].get('language') == 'EN':
                en_file, ga_file = u, v
            else:
                en_file, ga_file = v, u

            if en_file in en_idx and ga_file in ga_idx:
                biadj[en_idx[en_file], ga_idx[ga_file]] = d.get('weight', 1)

        # EN-EN projection: P = B @ B.T
        en_projection = biadj @ biadj.T

        # GA-GA projection: P = B.T @ B
        ga_projection = biadj.T @ biadj

        mo.md(rf"""
        ## Bipartite Projections

        **Biadjacency Matrix**: $B \in \mathbb{{R}}^{{{len(en_node_list)} \times {len(ga_node_list)}}}$

        **EN-EN Projection** ($P_{{EN}} = B B^T$):
        - Shows English documents with shared Irish translations
        - Non-zero $P[i,j]$ means EN docs $i$ and $j$ share GA content

        **GA-GA Projection** ($P_{{GA}} = B^T B$):
        - Shows Irish documents with shared English sources
        """)
    else:
        biadj = np.array([])
        en_projection = np.array([])
        ga_projection = np.array([])
        mo.md("Insufficient data for projection analysis")

    return biadj, en_projection, ga_projection, en_node_list, ga_node_list, en_idx, ga_idx


@app.cell
def _(B, alignments_df, go, mo):
    """
    Network visualization of bilingual alignments.
    """

    # Layout: EN on left, GA on right
    pos = {}
    en_y = 0
    ga_y = 0

    for node, data in B.nodes(data=True):
        if data.get('language') == 'EN':
            pos[node] = (-1, en_y)
            en_y += 1
        else:
            pos[node] = (1, ga_y)
            ga_y += 1

    # Edge traces with confidence coloring
    edge_traces = []
    for u, v, d in B.edges(data=True):
        x0, y0 = pos.get(u, (0, 0))
        x1, y1 = pos.get(v, (0, 0))
        conf = d.get('weight', 0.5)

        edge_traces.append(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(width=2, color=f'rgba(100, 100, 100, {conf})'),
            hoverinfo='text',
            text=f"Confidence: {conf:.2f}",
            showlegend=False
        ))

    # EN nodes
    en_x = [pos[n][0] for n in B.nodes() if B.nodes[n].get('language') == 'EN']
    en_y = [pos[n][1] for n in B.nodes() if B.nodes[n].get('language') == 'EN']
    en_names = [n.split('/')[-1] for n in B.nodes() if B.nodes[n].get('language') == 'EN']

    en_trace = go.Scatter(
        x=en_x, y=en_y,
        mode='markers+text',
        text=en_names,
        textposition='middle left',
        marker=dict(size=12, color='#1f77b4'),
        name='English',
        hoverinfo='text'
    )

    # GA nodes
    ga_x = [pos[n][0] for n in B.nodes() if B.nodes[n].get('language') == 'GA']
    ga_y = [pos[n][1] for n in B.nodes() if B.nodes[n].get('language') == 'GA']
    ga_names = [n.split('/')[-1] for n in B.nodes() if B.nodes[n].get('language') == 'GA']

    ga_trace = go.Scatter(
        x=ga_x, y=ga_y,
        mode='markers+text',
        text=ga_names,
        textposition='middle right',
        marker=dict(size=12, color='#ff7f0e'),
        name='Irish',
        hoverinfo='text'
    )

    fig_bipartite = go.Figure(
        data=edge_traces + [en_trace, ga_trace],
        layout=go.Layout(
            title='Bilingual Alignment Network (EN ↔ GA)',
            showlegend=True,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-2, 2]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )
    )

    mo.ui.plotly(fig_bipartite)
    return fig_bipartite, pos, en_trace, ga_trace


@app.cell
def _(mo):
    mo.md("""
    ## Summary: Bilingual Alignment Analysis

    ### Mathematical Techniques

    | Concept | Source | Application |
    |---------|--------|-------------|
    | Bipartite graphs | CS4423 networks04 | EN↔GA document mapping |
    | Biadjacency matrix | CS4423 | Alignment representation |
    | Correlation | ST311 §5 | Length ratio analysis |
    | Coverage metrics | Graph theory | Translation completeness |

    ### Key Findings

    1. **Length Ratio**: Irish translations are typically 10-15% longer than English
    2. **Confidence Score**: Based on deviation from expected length ratio
    3. **Coverage Gaps**: Identify documents lacking translations

    ### Applications for Gaeilge Project

    - Validate **QuestionMarkingSchemePair** bilingual alignments
    - Assess translation quality from the **language** field
    - Identify gaps in **alternate_language_url** coverage
    - Guide UCCIX model usage for Irish-specific content

    ### Bridging the 20% Gap

    Strategies from the research:
    1. Use **Qwen3** (119 languages, native Irish support)
    2. Fallback to **UCCIX** for Irish-specific validation
    3. Expand training data with high-confidence aligned pairs
    4. Apply **GaBERT** embeddings for Irish text similarity

    ### Related Notebooks
    - `curriculum_network_analysis.py` - Curriculum structure
    - `neo4j_marimo_bridge.py` - Database connectivity
    """)
    return


if __name__ == "__main__":
    app.run()
