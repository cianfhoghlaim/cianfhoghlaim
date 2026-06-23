# Advanced RAG Patterns

Beyond vanilla vector search, LanceDB supports several RAG patterns
that significantly improve recall on long-doc / multi-doc corpora.

## Context Enrichment Window (sliding-neighbour chunking)

For long documents, vanilla RAG often misses context that spans
chunk boundaries. The **Context Enrichment Window** pattern augments
each chunk with its ±N neighbouring chunks before embedding, then
re-ranks the results by group.

```python
def chunk_with_window(text, chunk_size=500, window=2):
    """Yield (chunk, neighbours) tuples."""
    chunks = text_splitter.split(text, chunk_size=chunk_size)
    for i, chunk in enumerate(chunks):
        neighbours = chunks[max(0, i-window):i+window+1]
        yield chunk, neighbours

# Build a "fat" row: each row's text is the chunk + its neighbours
rows = []
for chunk, neighbours in chunk_with_window(doc):
    enriched = "\n\n---\n\n".join(neighbours)
    rows.append({
        "id": hash(enriched),
        "primary_chunk": chunk,
        "context": enriched,
        "embedding": embed(enriched),
    })
table.add(rows)

# Search: retrieve by context, but return the primary_chunk
results = table.search(query_vec).limit(10).to_pandas()
for r in results:
    print(r["primary_chunk"])  # not the full context
```

This is the canonical pattern from the
`Advanced_RAG_Context_Enrichment_Window` example in the upstream
lancedb/vectordb-recipes repo (the same example that lived in
`docs/lance/examples/Advanced_RAG_Context_Enrichment_Window/`
before the docs were deleted).

## LOTR (Lost in the Middle) Reordering

LLMs pay more attention to the start and end of the context window
than the middle. The LOTR pattern re-orders retrieved chunks so the
most relevant are at the start and end:

```python
def lotr_rerank(results, top_k=10):
    """Re-order so the most relevant are at positions 0, 1, 2, 7, 8, 9."""
    relevant = results.head(top_k - 3)
    middle = results.iloc[2:5]  # the "lost in the middle" positions
    reranked = pd.concat([relevant.head(3), middle, relevant.tail(top_k - 6)])
    return reranked

results = table.search(query_vec).limit(20).to_pandas()
final = lotr_rerank(results, top_k=10)
```

## Agentic RAG (ReAct)

For multi-hop questions, an agent decides what to search next:

```python
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool

@tool
def search_docs(query: str, top_k: int = 5) -> str:
    """Search the LanceDB table for relevant chunks."""
    query_vec = embed(query)
    results = table.search(query_vec).limit(top_k).to_pandas()
    return "\n\n---\n\n".join(results["text"].tolist())

agent = create_react_agent(llm, [search_docs], prompt)
executor = AgentExecutor(agent=agent, tools=[search_docs], verbose=True)
answer = executor.invoke({"input": "Compare the Junior Cycle and Leaving Cert Irish syllabi"})
```

See the `multi-document-agentic-rag` example in the upstream
lancedb/vectordb-recipes repo (the same example that lived in
`docs/lance/examples/multi-document-agentic-rag/` before the docs
were deleted).

## ColPali multi-vector (for PDFs)

ColPali produces a multi-vector representation (one vector per image
patch), which is better for document / page retrieval than single-vector
CLIP. Pair ColPali with Qdrant MaxSim scoring:

```python
# See the full pattern in docs/cocoindex/references/multimodal-image-search.md
# and the upstream image_search_colpali example.
```

## GraphRAG (with Cognee)

For relational queries (e.g. "what topics are prerequisites for X?"),
use a knowledge graph alongside vector search:

```python
import cognee

# 1. Index the docs in LanceDB (vector search)
table.add([...])

# 2. Cognify the same docs in Cognee (knowledge graph)
for doc in docs:
    await cognee.add(doc)
await cognee.cognify()

# 3. Query: vector search returns candidate chunks, knowledge graph
#    returns the relational structure
results = table.search(query_vec).limit(10).to_pandas()
graph = await cognee.search("prerequisites for handwriting recognition", query_type=SearchType.GRAPH_COMPLETION)
```

## Hybrid search with multiple embedders

For multilingual corpora, use one embedder per language and combine
the results:

```python
# Two tables: one for English (BGE-large-en-v1.5), one for Irish (BGE-M3)
table_en = db.open_table("docs_en")
table_ga = db.open_table("docs_ga")

# Search both, merge with RRF
results_en = table_en.search(embed_en(query)).limit(10).to_pandas()
results_ga = table_ga.search(embed_ga(query)).limit(10).to_pandas()
merged = rrf_merge([results_en, results_ga], k=60)
```
