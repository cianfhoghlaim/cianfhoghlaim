# Marimo Vector Search (LanceDB + RRF)

The canonical "vector search in a marimo notebook" pattern.
Combines DLT ingestion + LanceDB storage + RRF reranking +
marimo UI.

## Pattern 1: Hybrid search (vector + FTS + RRF)

```python
from lancedb.rerankers import RRFReranker
import lancedb

@app.cell
def _():
    db = lancedb.connect("./lancedb_data")
    table = db.open_table("chunks")
    return (table,)


@app.cell
def _():
    table = _
    query = mo.ui.text(placeholder="Search the corpus...", value="handwriting")
    return (query,)


@app.cell
def _():
    table = _
    query = _
    results = (table
        .search(query.value, query_type="hybrid")
        .vector(embed(query.value))
        .text(query.value)
        .rerank(RRFReranker())
        .limit(10)
        .to_pandas())
    mo.ui.table(results)
    return
```

## Pattern 2: FTS with Tantivy

```python
@app.cell
def _():
    table = db.open_table("chunks")
    table.create_fts_index(["text"], use_tantivy=True, replace=True)
    return
```

`use_tantivy=True` enables the Rust-based Tantivy FTS engine
(10x faster than the default). `replace=True` overwrites any
existing FTS index.

## Pattern 3: Vector-only search (cosine distance)

```python
@app.cell
def _():
    table = _
    results = (table
        .search(embed_query(query.value))
        .metric("cosine")
        .limit(20)
        .to_pandas())
    mo.ui.table(results)
    return
```

## Pattern 4: Filtered vector search

```python
@app.cell
def _():
    table = _
    results = (table
        .search(embed_query(query.value))
        .where("subject = 'irish' AND year >= 2020")
        .limit(10)
        .to_pandas())
    mo.ui.table(results)
    return
```

The `.where()` filter is applied BEFORE the vector search
(pre-filter); use `.prefilter(False)` for post-filtering
when the filter is non-selective.

## Pattern 5: BGE-M3 multilingual (KCG canonical)

```python
from lancedb.embeddings import get_registry

registry = get_registry()
embedder = registry.get("huggingface").create(
    name="BAAI/bge-m3",  # 1024-d, multilingual
    device="cuda",
)


@app.cell
def _():
    table = db.open_table("chunks")
    results = (table
        .search(embedder.create_query(query.value))
        .limit(10)
        .to_pandas())
    mo.ui.table(results)
    return
```

BGE-M3 is the canonical multilingual model for oideachais
(Irish, Welsh, Scottish Gaelic, Breton).

## Pattern 6: Time-travel query

```python
@app.cell
def _():
    table = db.open_table("chunks")
    versions = table.list_versions()
    mo.ui.dropdown([f"v{v.version} ({v.timestamp})" for v in versions])
    return
```

## KCG conventions

- Vector search always uses `RRFReranker` for hybrid queries
- FTS index is created with `use_tantivy=True`
- BGE-M3 is the default for multilingual corpora
- BGE-large-en-v1.5 is the default for English-only

## Resources

- LanceDB hybrid search: <https://lancedb.github.io/lancedb/hybrid_search/>
- RRF rerankers: <https://lancedb.github.io/lancedb/rerankers/>
- Related skill: `.agents/skills/lancedb/SKILL.md`
