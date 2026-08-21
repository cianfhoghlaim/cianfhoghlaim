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
    marimo edit crypteolas/notebooks/02_code_search.py
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
    ## Step 1: Connect to Code Index

    Connect to the LanceDB code index.
    """)
    return


@app.cell
def _(mo, Path):
    # Directory selection
    lancedb_dirs = list(Path("./data").glob("*.lancedb")) if Path("./data").exists() else []
    default_db = str(lancedb_dirs[0]) if lancedb_dirs else "./data/code_index.lancedb"

    db_input = mo.ui.text(
        value=default_db,
        label="LanceDB path",
        full_width=True,
    )

    db_input
    return db_input, lancedb_dirs, default_db


@app.cell
def _(mo, db_input, Path):
    import lancedb

    db = None
    tables = []

    db_path = Path(db_input.value)
    if db_path.exists():
        try:
            db = lancedb.connect(str(db_path))
            tables = db.table_names()
            mo.md(f"**Connected!** Tables: {', '.join(tables) if tables else 'None'}")
        except Exception as e:
            mo.md(f"*Error connecting: {e}*")
    else:
        mo.md("*Database not found. Create an index first.*")

    db, tables
    return lancedb, db, tables


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
def _(mo, query_input, search_type, limit_slider, search_button, db, tables):
    from sentence_transformers import SentenceTransformer

    search_results = []

    if search_button.value and db and tables:
        mo.status.spinner(title="Searching...")

        # Load embedding model
        model = SentenceTransformer("BAAI/bge-small-en-v1.5")

        # Get first code table
        code_tables = [t for t in tables if "code" in t.lower() or "chunk" in t.lower()]
        table_name = code_tables[0] if code_tables else tables[0]

        table = db.open_table(table_name)

        # Embed query
        query_embedding = model.encode(query_input.value).tolist()

        # Search based on type
        if search_type.value == "vector":
            results = table.search(query_embedding).limit(limit_slider.value).to_pandas()
        elif search_type.value == "fts":
            results = table.search(query_input.value, query_type="fts").limit(limit_slider.value).to_pandas()
        else:  # hybrid
            results = table.search(query_embedding, query_type="hybrid").limit(limit_slider.value).to_pandas()

        search_results = results.to_dict("records")

    search_results
    return SentenceTransformer, search_results


@app.cell
def _(search_results, mo):
    if search_results:
        results_md = "## Search Results\n\n"

        for i, result in enumerate(search_results, 1):
            filename = result.get("filename", result.get("file_path", "unknown"))
            score = result.get("_distance", result.get("score", 0))
            code = result.get("code", result.get("content", result.get("text", "")))
            language = result.get("language", "")

            score_pct = f"{(1 - score) * 100:.1f}%" if score < 1 else f"{score:.3f}"
            results_md += f"""
### {i}. `{filename}` (Score: {score_pct})

```{language}
{code[:500]}{'...' if len(code) > 500 else ''}
```

---
"""

        mo.md(results_md)
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
    ## Step 3: Index New Code

    Index a local directory into LanceDB:
    """)
    return


@app.cell
def _(mo, Path):
    index_dir = mo.ui.text(
        value="./",
        label="Directory to index",
        full_width=True,
    )

    patterns_input = mo.ui.text(
        value="*.py,*.ts,*.sol",
        label="File patterns (comma-separated)",
    )

    mo.vstack([index_dir, patterns_input])
    return index_dir, patterns_input


@app.cell
def _(mo):
    index_button = mo.ui.run_button(label="Index Directory")
    index_button
    return (index_button,)


@app.cell
def _(mo, index_dir, patterns_input, index_button, Path, db_input):
    from sentence_transformers import SentenceTransformer
    import lancedb
    import pyarrow as pa

    index_result = None

    if index_button.value:
        mo.status.spinner(title="Indexing code...")

        directory = Path(index_dir.value)
        patterns = [p.strip() for p in patterns_input.value.split(",")]

        # Collect files
        files = []
        for pattern in patterns:
            files.extend(directory.rglob(pattern))

        if files:
            # Load model
            model = SentenceTransformer("BAAI/bge-small-en-v1.5")

            # Chunk and embed
            chunks = []
            for file in files[:100]:  # Limit for demo
                try:
                    content = file.read_text(errors="ignore")
                    if content.strip():
                        # Simple chunking by function/class
                        chunk_text = content[:2000]  # First 2000 chars
                        embedding = model.encode(chunk_text).tolist()

                        chunks.append({
                            "filename": str(file),
                            "code": chunk_text,
                            "language": file.suffix[1:] if file.suffix else "",
                            "vector": embedding,
                        })
                except:
                    pass

            if chunks:
                # Create/update LanceDB table
                db = lancedb.connect(db_input.value)
                table = db.create_table("code_chunks", chunks, mode="overwrite")

                index_result = {
                    "files_processed": len(files),
                    "chunks_indexed": len(chunks),
                    "table": "code_chunks",
                }

    if index_result:
        mo.md(f"""
        ## Indexing Complete

        - **Files processed**: {index_result['files_processed']}
        - **Chunks indexed**: {index_result['chunks_indexed']}
        - **Table**: `{index_result['table']}`
        """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Next Steps

    - **GitHub API**: Run `01_github_explorer.py` to ingest GitHub metadata
    - **Knowledge Graph**: Run `03_knowledge_graph.py` to explore entity relationships
    - **DeFi Dashboard**: Run `04_defi_dashboard.py` for DeFi analytics

    ## Resources

    - [LanceDB Documentation](https://lancedb.github.io/lancedb/)
    - [Sentence Transformers](https://www.sbert.net/)
    - [DLT + LanceDB Integration](https://dlthub.com/docs/dlt-ecosystem/destinations/lancedb)
    """)
    return


if __name__ == "__main__":
    app.run()
