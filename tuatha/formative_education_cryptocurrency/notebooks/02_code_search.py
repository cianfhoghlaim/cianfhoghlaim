# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "lancedb>=0.6.0",
#     "sentence-transformers",
#     "pyarrow",
#     "altair>=5.0.0",
# ]
# ///
"""Code Search Explorer - Semantic Code Search with LanceDB.

This marimo notebook demonstrates:
1. Indexing code repositories into LanceDB
2. Vector, FTS, and hybrid search strategies
3. Comparing search results across strategies
4. Interactive code exploration

Usage:
    marimo edit notebooks/02_code_search.py
"""
import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Code Search Explorer

    This notebook demonstrates **semantic code search** using LanceDB with:
    - **Vector Search**: Find semantically similar code using embeddings
    - **Full-Text Search (FTS)**: Keyword matching with BM25
    - **Hybrid Search**: Combine both with reranking

    ## How It Works

    1. **Indexing**: Code is chunked, embedded, and stored in LanceDB
    2. **Search**: Queries are embedded and compared against stored embeddings
    3. **Reranking**: Hybrid results are reranked for relevance
    """)
    return


@app.cell
def _():
    import marimo as mo
    import os
    from pathlib import Path

    # Change to project root
    project_root = Path(__file__).parent.parent if "__file__" in dir() else Path.cwd().parent
    if (project_root / "pyproject.toml").exists():
        os.chdir(project_root)

    return mo, os, Path, project_root


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1: Index a Repository

    First, let's index a local directory or cloned repository.
    """)
    return


@app.cell
def _(mo, Path):
    # Directory selection
    default_dir = "./data/repos/dlt-hub/dlt" if Path("./data/repos/dlt-hub/dlt").exists() else "."

    dir_input = mo.ui.text(
        value=default_dir,
        label="Directory to index",
        full_width=True,
    )

    patterns_input = mo.ui.text(
        value="*.py,*.md",
        label="File patterns (comma-separated)",
    )

    mo.vstack([dir_input, patterns_input])
    return dir_input, patterns_input, default_dir


@app.cell
def _(mo):
    index_button = mo.ui.run_button(label="Index Directory")
    index_button
    return (index_button,)


@app.cell
def _(mo, dir_input, patterns_input, index_button, Path):
    import sys
    sys.path.insert(0, str(Path.cwd()))

    from cocoindex.config import CodeIndexingConfig
    from cocoindex.flows.code_indexing import CodeIndexingFlow

    index_result = None

    if index_button.value:
        mo.status.spinner(title="Indexing code...")

        directory = dir_input.value
        patterns = [p.strip() for p in patterns_input.value.split(",")]

        config = CodeIndexingConfig(
            repo_owner="local",
            repo_name=Path(directory).name,
            included_patterns=patterns,
            lancedb_uri="./data/github_intelligence.lancedb",
        )

        flow = CodeIndexingFlow(config)
        num_chunks = flow.index_directory(directory)

        index_result = {
            "directory": directory,
            "chunks_indexed": num_chunks,
            "table_name": config.table_name,
        }

    index_result
    return CodeIndexingConfig, CodeIndexingFlow, index_result


@app.cell
def _(index_result, mo):
    if index_result:
        mo.md(f"""
        ## Indexing Complete

        - **Directory**: `{index_result['directory']}`
        - **Chunks indexed**: {index_result['chunks_indexed']}
        - **Table**: `{index_result['table_name']}`
        """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: Search Code

    Enter a query to search for semantically similar code.
    """)
    return


@app.cell
def _(mo):
    query_input = mo.ui.text(
        value="how to create a dlt pipeline",
        label="Search query",
        full_width=True,
    )

    search_type = mo.ui.dropdown(
        options=["hybrid", "vector", "fts"],
        value="hybrid",
        label="Search type",
    )

    limit_slider = mo.ui.slider(
        start=5,
        stop=20,
        value=10,
        label="Results limit",
    )

    mo.hstack([query_input, search_type, limit_slider])
    return query_input, search_type, limit_slider


@app.cell
def _(mo):
    search_button = mo.ui.run_button(label="Search")
    search_button
    return (search_button,)


@app.cell
def _(mo, query_input, search_type, limit_slider, search_button, index_result, Path):
    from cocoindex.search import LanceDBSearch

    search_results = []

    if search_button.value and index_result:
        mo.status.spinner(title="Searching...")

        search = LanceDBSearch(
            db_uri="./data/github_intelligence.lancedb",
            table_name=index_result["table_name"],
        )

        search_results = search.search(
            query=query_input.value,
            search_type=search_type.value,
            limit=limit_slider.value,
        )

    search_results
    return LanceDBSearch, search_results, search


@app.cell
def _(search_results, mo):
    if search_results:
        results_md = "## Search Results\n\n"

        for i, result in enumerate(search_results, 1):
            score_pct = f"{result.score * 100:.1f}%"
            results_md += f"""
### {i}. `{result.filename}` (Score: {score_pct})

**Location**: {result.location} | **Language**: {result.language}

```{result.language}
{result.code[:500]}{'...' if len(result.code) > 500 else ''}
```

---
"""

        mo.md(results_md)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 3: Compare Search Strategies

    Let's compare how different search strategies perform on the same query.
    """)
    return


@app.cell
def _(mo):
    compare_button = mo.ui.run_button(label="Compare Strategies")
    compare_button
    return (compare_button,)


@app.cell
def _(mo, query_input, compare_button, index_result):
    from cocoindex.search import compare_search_strategies

    comparison = {}

    if compare_button.value and index_result:
        mo.status.spinner(title="Comparing search strategies...")

        comparison = compare_search_strategies(
            db_uri="./data/github_intelligence.lancedb",
            table_name=index_result["table_name"],
            query=query_input.value,
            limit=5,
        )

    comparison
    return compare_search_strategies, comparison


@app.cell
def _(comparison, mo):
    if comparison:
        import altair as alt
        import pandas as pd

        # Build comparison dataframe
        data = []
        for strategy, results in comparison.items():
            for i, r in enumerate(results):
                data.append({
                    "strategy": strategy,
                    "rank": i + 1,
                    "filename": r.filename[:30],
                    "score": r.score,
                })

        df = pd.DataFrame(data)

        # Create comparison chart
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("rank:O", title="Rank"),
            y=alt.Y("score:Q", title="Score"),
            color="strategy:N",
            column="strategy:N",
            tooltip=["filename", "score", "rank"]
        ).properties(
            width=200,
            height=200,
            title="Search Strategy Comparison"
        )

        mo.ui.altair_chart(chart)
    return


@app.cell
def _(comparison, mo):
    if comparison:
        # Show top result from each strategy
        comp_md = "### Top Result per Strategy\n\n"

        for strategy, results in comparison.items():
            if results:
                top = results[0]
                comp_md += f"""
**{strategy.upper()}**: `{top.filename}` (Score: {top.score:.3f})
```
{top.code[:200]}...
```

"""

        mo.md(comp_md)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Understanding Search Strategies

    | Strategy | How It Works | Best For |
    |----------|--------------|----------|
    | **Vector** | Compares semantic embeddings | Conceptual queries ("how to X") |
    | **FTS** | BM25 keyword matching | Exact terms, function names |
    | **Hybrid** | Combines both + reranking | General purpose, best overall |

    ### Reranking Options

    - **RRF (Reciprocal Rank Fusion)**: Fast, no model needed
    - **Cross-Encoder**: More accurate, uses BERT model
    - **ColBERT**: Good balance of speed and accuracy
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Next Steps

    - **GitHub API**: Run `01_github_api_explorer.py` to ingest GitHub metadata
    - **Knowledge Graph**: Run `03_knowledge_graph.py` to explore entity relationships
    - **Dashboard**: Run `04_unified_dashboard.py` for combined analytics

    ## Resources

    - [LanceDB Documentation](https://lancedb.github.io/lancedb/)
    - [Sentence Transformers](https://www.sbert.net/)
    - [DLT + LanceDB Integration](https://dlthub.com/docs/dlt-ecosystem/destinations/lancedb)
    """)
    return


if __name__ == "__main__":
    app.run()
