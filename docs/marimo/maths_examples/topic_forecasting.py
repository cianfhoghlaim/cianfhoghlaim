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
Topic Forecasting with Markov Chains - Marimo Notebook

Uses Markov chain analysis from queueing theory to model and predict
exam topic occurrences in the Irish Leaving Certificate.

Mathematical foundations from:
- /Users/cliste/dev/mata/MP307 - Modelling 2/1. Queueing Theory/L3. Ergodic Markov Chains.pdf
- /Users/cliste/dev/mata/MP307 - Modelling 2/1. Queueing Theory/L5. Poisson Process.pdf

BAML schema reference:
- TopicAnalysis, TopicOccurrence classes from gaeilge/baml_src/classes.baml
"""

import marimo

__generated_with = "0.10.0"
app = marimo.App(
    width="full",
    app_title="Topic Forecasting",
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
    from scipy import linalg
    from scipy.stats import poisson
    from typing import Dict, List, Tuple
    return mo, nx, np, pd, go, px, yaml, Path, linalg, poisson, Dict, List, Tuple


@app.cell
def _(mo):
    mo.md(r"""
    # Topic Forecasting with Markov Chains

    This notebook applies **Markov chain theory** from MP307 Queueing Theory to
    predict which topics are likely to appear on future exams.

    ## Mathematical Foundation

    ### Markov Chains (L3. Ergodic Markov Chains)

    A **Markov chain** is a stochastic process where the future state depends only
    on the current state (memoryless property):

    $$P(X_{n+1} = j | X_n = i, X_{n-1}, \ldots) = P(X_{n+1} = j | X_n = i) = p_{ij}$$

    The **transition matrix** $P = (p_{ij})$ where $p_{ij}$ is the probability
    of transitioning from state $i$ to state $j$.

    ### Ergodic Systems

    For ergodic Markov chains, there exists a **stationary distribution** $\pi$:

    $$\pi P = \pi \quad \text{and} \quad \sum_i \pi_i = 1$$

    This gives us the long-run probability of being in each state (topic appearing).

    ### Application to Exam Topics

    - **States**: Topics that can appear on exams
    - **Transitions**: Topic A appearing in year $n$ → Topic B appearing in year $n+1$
    - **Stationary distribution**: Long-run probability of each topic appearing
    """)
    return


@app.cell
def _(yaml, Path):
    """
    Load curriculum data including topic history.
    """
    GAEILGE_PATH = Path("/Users/cliste/dev/bonneagar/hackathon/data/flows/gaeilge")

    with open(GAEILGE_PATH / "sources.yaml", "r") as f:
        config = yaml.safe_load(f)

    # Get curriculum history
    curriculum_history = config.get('curriculum_history', {})
    math_history = curriculum_history.get('mathematics', [])

    print(f"Mathematics curriculum changes: {len(math_history)}")
    for event in math_history:
        print(f"  - {event.get('year')}: {event.get('event')}")

    return config, curriculum_history, math_history, GAEILGE_PATH


@app.cell
def _(np, pd, mo):
    """
    Simulated topic occurrence data for demonstration.

    In production, this would come from TopicAnalysis BAML extractions
    from actual exam papers.
    """

    # Mathematics topics based on sources.yaml strands
    math_topics = [
        'Algebra',
        'Functions',
        'Calculus',
        'Geometry',
        'Trigonometry',
        'Statistics',
        'Probability',
        'Number Theory',
        'Sequences & Series',
        'Financial Maths',
    ]

    # Simulated appearance data (years 2014-2024)
    years = list(range(2014, 2025))

    # Generate realistic appearance patterns
    np.random.seed(42)

    # Base probabilities for each topic (some topics appear more often)
    base_probs = {
        'Algebra': 0.95,
        'Functions': 0.90,
        'Calculus': 0.85,
        'Geometry': 0.70,
        'Trigonometry': 0.80,
        'Statistics': 0.75,
        'Probability': 0.70,
        'Number Theory': 0.40,
        'Sequences & Series': 0.60,
        'Financial Maths': 0.50,
    }

    # Generate topic occurrences
    topic_occurrences = {}
    for topic in math_topics:
        appearances = []
        for year in years:
            # Topic appears with base probability
            if np.random.random() < base_probs[topic]:
                appearances.append({
                    'year': year,
                    'appeared': True,
                    'marks': np.random.choice([25, 50, 75]),
                    'question_type': np.random.choice(['problem_solving', 'short_answer', 'proof'])
                })
            else:
                appearances.append({
                    'year': year,
                    'appeared': False,
                    'marks': 0,
                    'question_type': None
                })
        topic_occurrences[topic] = appearances

    mo.md(f"""
    ## Topic Occurrence Data

    Analyzing **{len(math_topics)} topics** over **{len(years)} years** ({years[0]}-{years[-1]})

    *Note: This is simulated data for demonstration. In production, this would be
    extracted from exam papers using the TopicAnalysis BAML schema.*
    """)
    return math_topics, years, base_probs, topic_occurrences


@app.cell
def _(math_topics, years, topic_occurrences, np, pd, mo):
    """
    Create topic appearance matrix and compute frequency statistics.
    """

    # Build appearance matrix (topics x years)
    appearance_matrix = np.zeros((len(math_topics), len(years)))

    for i, topic in enumerate(math_topics):
        for j, year in enumerate(years):
            if topic_occurrences[topic][j]['appeared']:
                appearance_matrix[i, j] = 1

    # Create DataFrame for visualization
    appearance_df = pd.DataFrame(
        appearance_matrix,
        index=math_topics,
        columns=years
    )

    # Compute statistics
    topic_stats = pd.DataFrame({
        'topic': math_topics,
        'appearances': appearance_matrix.sum(axis=1),
        'frequency': appearance_matrix.mean(axis=1),
        'last_appeared': [
            years[np.where(appearance_matrix[i] == 1)[0][-1]]
            if appearance_matrix[i].sum() > 0 else None
            for i, _ in enumerate(math_topics)
        ],
        'years_since_last': [
            years[-1] - years[np.where(appearance_matrix[i] == 1)[0][-1]]
            if appearance_matrix[i].sum() > 0 else None
            for i, _ in enumerate(math_topics)
        ]
    }).sort_values('frequency', ascending=False)

    mo.md("""
    ## Topic Frequency Analysis
    """)
    return appearance_matrix, appearance_df, topic_stats


@app.cell
def _(topic_stats, mo):
    mo.ui.table(topic_stats)
    return


@app.cell
def _(appearance_df, go, mo):
    """
    Heatmap of topic appearances over time.
    """

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=appearance_df.values,
        x=[str(y) for y in appearance_df.columns],
        y=appearance_df.index,
        colorscale=[[0, 'white'], [1, '#2ca02c']],
        showscale=False,
        hovertemplate='Topic: %{y}<br>Year: %{x}<br>Appeared: %{z}<extra></extra>'
    ))

    fig_heatmap.update_layout(
        title='Topic Appearance Matrix (Green = Appeared)',
        xaxis_title='Year',
        yaxis_title='Topic',
        height=500,
    )

    mo.ui.plotly(fig_heatmap)
    return fig_heatmap,


@app.cell
def _(appearance_matrix, math_topics, np, linalg, mo):
    """
    Build Markov transition matrix for topic sequences.

    Model: Given topic A appeared in year n, what's the probability
    topic B appears in year n+1?

    This captures "topic cycling" patterns in exam setting.
    """

    n_topics = len(math_topics)
    n_years = appearance_matrix.shape[1]

    # Transition counts: P[i,j] = count of (topic i in year n, topic j in year n+1)
    transition_counts = np.zeros((n_topics, n_topics))

    for year_idx in range(n_years - 1):
        # Topics that appeared in current year
        current_topics = np.where(appearance_matrix[:, year_idx] == 1)[0]
        # Topics that appeared in next year
        next_topics = np.where(appearance_matrix[:, year_idx + 1] == 1)[0]

        # Count co-occurrences
        for i in current_topics:
            for j in next_topics:
                transition_counts[i, j] += 1

    # Normalize to get probabilities (add small epsilon to avoid division by zero)
    row_sums = transition_counts.sum(axis=1, keepdims=True)
    row_sums = np.where(row_sums == 0, 1, row_sums)  # Avoid division by zero
    transition_matrix = transition_counts / row_sums

    # Ensure rows sum to 1 (stochastic matrix)
    transition_matrix = transition_matrix / transition_matrix.sum(axis=1, keepdims=True)
    transition_matrix = np.nan_to_num(transition_matrix, nan=1/n_topics)

    mo.md(r"""
    ## Markov Transition Matrix

    The transition matrix $P = (p_{ij})$ where:

    $$p_{ij} = P(\text{Topic } j \text{ appears in year } n+1 | \text{Topic } i \text{ appeared in year } n)$$

    This captures the "memory" of exam setters - if topic $i$ appeared this year,
    what topics are likely next year?
    """)
    return transition_counts, transition_matrix, n_topics


@app.cell
def _(transition_matrix, math_topics, go, mo):
    """
    Visualize transition matrix.
    """

    fig_trans = go.Figure(data=go.Heatmap(
        z=transition_matrix,
        x=math_topics,
        y=math_topics,
        colorscale='Blues',
        text=np.round(transition_matrix, 2),
        texttemplate='%{text:.2f}',
        textfont={'size': 9},
        hovertemplate='From: %{y}<br>To: %{x}<br>P = %{z:.3f}<extra></extra>'
    ))

    fig_trans.update_layout(
        title='Markov Transition Matrix P(Topic_next | Topic_current)',
        xaxis_title='Next Year Topic',
        yaxis_title='Current Year Topic',
        height=600,
        xaxis={'tickangle': 45},
    )

    mo.ui.plotly(fig_trans)
    return fig_trans,


@app.cell
def _(transition_matrix, math_topics, np, linalg, mo):
    r"""
    Compute stationary distribution (long-run probabilities).

    For ergodic Markov chain, solve: π P = π with Σπ_i = 1

    This is equivalent to finding the left eigenvector for eigenvalue 1.
    """

    # Method 1: Power iteration (from MP307)
    # Start with uniform distribution
    pi = np.ones(len(math_topics)) / len(math_topics)

    # Iterate until convergence
    for _ in range(1000):
        pi_new = pi @ transition_matrix
        if np.allclose(pi, pi_new, rtol=1e-8):
            break
        pi = pi_new

    # Normalize
    pi = pi / pi.sum()

    # Method 2: Eigenvector method (verify)
    eigenvalues, eigenvectors = linalg.eig(transition_matrix.T)

    # Find eigenvector for eigenvalue ≈ 1
    idx = np.argmin(np.abs(eigenvalues - 1))
    stationary_eigenvector = np.real(eigenvectors[:, idx])
    stationary_eigenvector = stationary_eigenvector / stationary_eigenvector.sum()

    mo.md(r"""
    ## Stationary Distribution $\pi$

    The **stationary distribution** gives long-run probabilities of each topic appearing,
    accounting for the cycling patterns in exam setting.

    Computed via:
    1. **Power iteration**: $\pi^{(n+1)} = \pi^{(n)} P$ until convergence
    2. **Eigenvector method**: Left eigenvector for $\lambda = 1$
    """)
    return pi, eigenvalues, eigenvectors, stationary_eigenvector, idx


@app.cell
def _(math_topics, pi, base_probs, np, pd, go, mo):
    """
    Compare stationary distribution with observed frequencies.
    """

    comparison_df = pd.DataFrame({
        'topic': math_topics,
        'observed_frequency': [base_probs[t] for t in math_topics],
        'markov_stationary': pi,
        'difference': pi - np.array([base_probs[t] for t in math_topics])
    }).sort_values('markov_stationary', ascending=False)

    # Bar chart comparison
    fig_compare = go.Figure()

    fig_compare.add_trace(go.Bar(
        name='Observed Frequency',
        x=comparison_df['topic'],
        y=comparison_df['observed_frequency'],
        marker_color='#1f77b4'
    ))

    fig_compare.add_trace(go.Bar(
        name='Markov Stationary π',
        x=comparison_df['topic'],
        y=comparison_df['markov_stationary'],
        marker_color='#ff7f0e'
    ))

    fig_compare.update_layout(
        title='Observed Frequency vs Markov Stationary Distribution',
        xaxis_title='Topic',
        yaxis_title='Probability',
        barmode='group',
        height=500,
        xaxis={'tickangle': 45}
    )

    mo.ui.plotly(fig_compare)
    return comparison_df, fig_compare


@app.cell
def _(appearance_matrix, transition_matrix, math_topics, years, np, pd, mo):
    """
    Predict next year's topics using multi-step transition.

    P(topics in year n+k | topics in year n) = π^(n) × P^k
    """

    # Current year topics (last year in our data)
    current_year = years[-1]
    current_topics = appearance_matrix[:, -1]

    # Predict 1, 2, 3 years ahead
    predictions = {}

    for k in [1, 2, 3]:
        # P^k (k-step transition matrix)
        P_k = np.linalg.matrix_power(transition_matrix, k)

        # Weighted prediction based on current topics
        prediction = current_topics @ P_k
        prediction = prediction / prediction.sum()  # Normalize

        predictions[current_year + k] = prediction

    # Create prediction DataFrame
    pred_df = pd.DataFrame({
        'topic': math_topics,
        f'{current_year + 1}_prob': predictions[current_year + 1],
        f'{current_year + 2}_prob': predictions[current_year + 2],
        f'{current_year + 3}_prob': predictions[current_year + 3],
    }).sort_values(f'{current_year + 1}_prob', ascending=False)

    mo.md(f"""
    ## Topic Predictions for {current_year + 1} - {current_year + 3}

    Using **multi-step Markov predictions**: $P^k$ gives k-year transition probabilities.

    **Current state** ({current_year}): {', '.join([math_topics[i] for i in np.where(current_topics == 1)[0]])}
    """)
    return current_year, current_topics, predictions, pred_df


@app.cell
def _(pred_df, mo):
    mo.ui.table(pred_df)
    return


@app.cell
def _(topic_stats, years, poisson, np, pd, go, mo):
    """
    Poisson process analysis for topic inter-arrival times.

    From L5. Poisson Process:
    If topics appear independently at rate λ, the number of appearances
    in time t follows Poisson(λt).
    """

    # Calculate inter-arrival times for each topic
    inter_arrival_analysis = []

    for _, row in topic_stats.iterrows():
        topic = row['topic']
        appearances = int(row['appearances'])
        freq = row['frequency']

        if appearances > 1:
            # Estimate λ (rate parameter)
            lambda_est = appearances / len(years)

            # Expected inter-arrival time
            expected_gap = 1 / lambda_est if lambda_est > 0 else float('inf')

            # Probability of appearing next year (Poisson)
            prob_next = 1 - poisson.pmf(0, lambda_est)

            inter_arrival_analysis.append({
                'topic': topic,
                'appearances': appearances,
                'lambda_rate': lambda_est,
                'expected_gap_years': expected_gap,
                'prob_appears_next_year': prob_next,
            })

    inter_arrival_df = pd.DataFrame(inter_arrival_analysis).sort_values(
        'prob_appears_next_year', ascending=False
    )

    mo.md(r"""
    ## Poisson Process Analysis

    From **L5. Poisson Process**:

    If topic appearances follow a Poisson process with rate $\lambda$:
    - Number of appearances in $t$ years: $N(t) \sim \text{Poisson}(\lambda t)$
    - Inter-arrival time: $T \sim \text{Exponential}(\lambda)$
    - Expected gap: $E[T] = 1/\lambda$

    $$P(\text{appears next year}) = 1 - P(N(1) = 0) = 1 - e^{-\lambda}$$
    """)
    return inter_arrival_analysis, inter_arrival_df


@app.cell
def _(inter_arrival_df, mo):
    mo.ui.table(inter_arrival_df)
    return


@app.cell
def _(topic_stats, pred_df, inter_arrival_df, np, pd, mo):
    """
    Combined forecast: merge Markov and Poisson predictions.
    """

    # Merge predictions
    forecast = topic_stats[['topic', 'frequency', 'years_since_last']].copy()

    # Add Markov prediction (next year)
    year_col = [c for c in pred_df.columns if '_prob' in c][0]
    forecast = forecast.merge(
        pred_df[['topic', year_col]].rename(columns={year_col: 'markov_prob'}),
        on='topic',
        how='left'
    )

    # Add Poisson prediction
    forecast = forecast.merge(
        inter_arrival_df[['topic', 'prob_appears_next_year']].rename(
            columns={'prob_appears_next_year': 'poisson_prob'}
        ),
        on='topic',
        how='left'
    )

    # Combined score (weighted average)
    forecast['combined_prob'] = (
        0.4 * forecast['markov_prob'].fillna(0) +
        0.4 * forecast['poisson_prob'].fillna(0) +
        0.2 * forecast['frequency'].fillna(0)
    )

    # Adjust for "overdue" topics
    forecast['overdue_factor'] = forecast['years_since_last'].apply(
        lambda x: min(1 + 0.1 * x, 1.5) if pd.notna(x) else 1.0
    )
    forecast['adjusted_prob'] = forecast['combined_prob'] * forecast['overdue_factor']
    forecast = forecast.sort_values('adjusted_prob', ascending=False)

    mo.md("""
    ## Combined Forecast

    Merging multiple models:
    - **Markov chain** (40%): Captures topic cycling patterns
    - **Poisson process** (40%): Independent arrival rate
    - **Historical frequency** (20%): Baseline probability
    - **Overdue adjustment**: Boost for topics not seen recently
    """)
    return forecast,


@app.cell
def _(forecast, mo):
    mo.ui.table(forecast)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Summary: Forecasting Methodology

    ### Key Concepts from MP307

    1. **Markov Chains** (L3):
       - Model topic transitions as state machine
       - Stationary distribution for long-run probabilities
       - Multi-step predictions using $P^k$

    2. **Poisson Processes** (L5):
       - Model topic appearances as random arrivals
       - Inter-arrival time analysis
       - Memoryless property for prediction

    3. **Ergodic Systems**:
       - Convergence to equilibrium
       - Left eigenvector computation

    ### Applications for Gaeilge Project

    - Feed **TopicAnalysis** BAML extractions into this model
    - Generate **prediction_notes** for each topic
    - Support curriculum advisors with data-driven insights
    - Identify topics that are "overdue" for examination

    ### Limitations

    - Assumes stationarity (curriculum changes can invalidate)
    - Requires sufficient historical data
    - Examiner preferences may not follow pure stochastic models

    ### Related Notebooks
    - `curriculum_network_analysis.py` - Network structure
    - `grade_distribution_analysis.py` - Statistical distributions of grades
    """)
    return


if __name__ == "__main__":
    app.run()
