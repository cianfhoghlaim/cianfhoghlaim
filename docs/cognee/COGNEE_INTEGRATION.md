# Cognee Integration — Dagster Pipeline + GraphRAG

How Cognee integrates into the Kings' College Galway data platform as a Dagster asset pipeline for automated documentation cognition.

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      DAGSTER ASSET GRAPH                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │ docs_collected    │    │ codebase_indexed  │                   │
│  │ (DLT filesystem)  │    │ (CCC job)         │                   │
│  └────────┬─────────┘    └────────┬─────────┘                   │
│           │                       │                               │
│           ▼                       ▼                               │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │ docs_added_to     │    │ ccc_index_updated│                   │
│  │ cognee            │    │                   │                   │
│  └────────┬─────────┘    └──────────────────┘                   │
│           │                                                       │
│           ▼                                                       │
│  ┌──────────────────────────────────────────┐                    │
│  │           docs_cognified                  │                    │
│  │  (Cognee cognify via HTTP API)            │                    │
│  │  - Entity extraction (DeepSeek V4 Pro)   │                    │
│  │  - Relationship inference                 │                    │
│  │  - Knowledge graph → Neo4j               │                    │
│  │  - Vector embeddings → LanceDB           │                    │
│  └────────┬─────────────────────────────────┘                    │
│           │                                                       │
│           ▼                                                       │
│  ┌──────────────────────────────────────────┐                    │
│  │        graphiti_temporal_layer            │                    │
│  │  (Graphiti records valid/transaction      │                    │
│  │   times for all KG nodes)                 │                    │
│  └────────┬─────────────────────────────────┘                    │
│           │                                                       │
│           ▼                                                       │
│  ┌──────────────────────────────────────────┐                    │
│  │       consolidation_plan_generated        │                    │
│  │  (GraphRAG query → merge clusters)        │                    │
│  └────────┬─────────────────────────────────┘                    │
│           │                                                       │
│           ▼                                                       │
│  ┌──────────────────┐    ┌──────────────────┐                   │
│  │ docs_merged       │    │ langfuse_traced   │                   │
│  │ (subagent exec)   │    │ (all ops)         │                   │
│  └──────────────────┘    └──────────────────┘                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Dagster Asset Definitions

### Asset: `docs_added_to_cognee`

```python
from dagster import asset, Config
import httpx

class CogneeIngestConfig(Config):
    cognee_url: str = "http://localhost:8100"
    dataset_name: str
    docs_directory: str

@asset
def docs_added_to_cognee(config: CogneeIngestConfig) -> dict:
    """Add all .md files from a directory to Cognee."""
    from pathlib import Path
    
    root = Path(config.docs_directory)
    files = list(root.rglob("*.md"))
    
    async with httpx.AsyncClient() as client:
        for fp in files:
            with open(fp, "rb") as f:
                await client.post(
                    f"{config.cognee_url}/api/v1/add",
                    files={"data": (fp.name, f, "text/markdown")},
                    data={"datasetName": config.dataset_name},
                )
    
    return {"files_ingested": len(files), "dataset": config.dataset_name}
```

### Asset: `docs_cognified`

```python
@asset(deps=[docs_added_to_cognee])
def docs_cognified(config: CogneeIngestConfig) -> dict:
    """Trigger Cognee cognify to build the knowledge graph."""
    import httpx
    
    response = httpx.post(
        f"{config.cognee_url}/api/v1/cognify",
        json={"datasets": [config.dataset_name]},
        timeout=600,  # 10 min timeout for LLM processing
    )
    return response.json()
```

## GraphRAG Query Patterns

### Find Related Documents

```python
async def find_related_docs(query: str, dataset: str) -> list[dict]:
    """Use Cognee GraphRAG to find documents related to a query."""
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8100/api/v1/search",
            json={
                "searchType": "GRAPH_COMPLETION",
                "query": query,
                "datasets": [dataset],
            },
        )
        return response.json()
```

### Generate Consolidation Plan

```python
async def generate_merge_plan(dataset: str) -> str:
    """Use GraphRAG to identify documents that should be merged."""
    response = await find_related_docs(
        "find groups of documents that discuss the same specific topics "
        "and should be merged into single comprehensive documents. "
        "Return file paths and suggested merged document titles.",
        dataset,
    )
    return response
```

### Detect Cross-Directory Duplicates

```python
async def detect_cross_dir_duplicates() -> list[dict]:
    """Find documents in different datasets that cover the same topic."""
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8100/api/v1/search",
            json={
                "searchType": "INSIGHTS",
                "query": "identify documents that overlap in content "
                         "across different datasets",
            },
        )
        return response.json()
```

## Cost Tracking with Langfuse

Every Cognee `cognify()` operation generates LLM calls that should be traced:

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host="https://langfuse.cianfhoghlaim.ie",
)

@asset
def docs_cognified_with_tracing(config: CogneeIngestConfig):
    trace = langfuse.trace(name="cognee-cognify")
    
    with trace.span(name="entity-extraction") as span:
        # Cognee cognify call
        result = httpx.post(f"{config.cognee_url}/api/v1/cognify", ...)
        span.update(metadata={"dataset": config.dataset_name})
    
    trace.update(output=result.json())
    return result
```

## Batch Processing Strategy

For large documentation corpora (2,000+ files), use incremental batch processing:

```python
BATCHES = [
    {"dir": "docs/agents", "dataset": "docs-agents"},
    {"dir": "docs/bonneagar", "dataset": "docs-bonneagar"},
    {"dir": "docs/data_engineering", "dataset": "docs-data-eng"},
    {"dir": "docs/meaisínfhoghlaim", "dataset": "docs-ml"},
    {"dir": "docs/web", "dataset": "docs-web"},
    {"dir": "docs/context", "dataset": "docs-context"},
]

# Ingest all batches first (fast)
for batch in BATCHES:
    docs_added_to_cognee(CogneeIngestConfig(**batch))

# Then cognify all at once
docs_cognified(CogneeIngestConfig(dataset_name="__all__"))
```

## Cognee v1.0.1 API — Remember/Recall/Forget/Improve

The newer `remember` API simplifies the flow:

```python
import cognee

# Remember: auto-adds AND cognifies in one call
await cognee.remember(document_content, dataset_name="docs-agents")

# Recall: semantic search
results = await cognee.recall(
    "what are the Pangolin deployment patterns?",
    dataset_name="docs-bonneagar",
)

# Forget: remove data
await cognee.forget(dataset_name="old-docs")
```

This replaces the v0.x `add() → cognify() → search()` flow with a simpler two-step `remember() → recall()` pattern.
