# Langfuse Observability — Tracing the Cognition Pipeline

How Langfuse provides end-to-end observability for all LLM operations in the documentation cognition pipeline, including Cognee cognify, CocoIndex flows, and Graphiti temporal updates.

## Why Langfuse for Cognition Operations

Every cognition operation involves LLM calls — entity extraction, relationship inference, summarization, and GraphRAG search. Without tracing, these calls are opaque black boxes. Langfuse provides:

- **Per-operation cost tracking**: How much did cognify cost for each dataset?
- **Latency measurement**: Which phase of cognition is slowest?
- **Quality evaluation**: Are entity extractions accurate?
- **Prompt versioning**: Which extraction prompt produced the best KG?

## Setup

### MCP Server (opencode.json)

```json
"langfuse": {
  "type": "local",
  "command": ["bunx", "-y", "@langfuse/mcp"],
  "env": {
    "LANGFUSE_PUBLIC_KEY": "infisical://dev-baile/langfuse/public_key",
    "LANGFUSE_SECRET_KEY": "infisical://dev-baile/langfuse/secret_key",
    "LANGFUSE_HOST": "https://langfuse.cianfhoghlaim.ie"
  },
  "enabled": true
}
```

### Docker Stack

```bash
cd infrastructure/stacks/langfuse
docker compose -f compose.yaml -f sidecar.yaml up -d
# Services: langfuse-web (:3000), langfuse-worker, postgres, clickhouse, redis, minio
```

## Tracing Cognee Cognify Operations

### Python Integration

```python
from langfuse import Langfuse
import httpx
import os

langfuse = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host="https://langfuse.cianfhoghlaim.ie",
)

def cognify_with_tracing(dataset: str):
    """Run Cognee cognify with Langfuse tracing."""
    
    # Create a trace for this cognify run
    trace = langfuse.trace(
        name=f"cognee-cognify-{dataset}",
        metadata={"dataset": dataset, "pipeline": "cognition"},
    )
    
    # Span 1: Document loading
    with trace.span(name="document-count") as span:
        doc_count = get_document_count(dataset)
        span.update(metadata={"document_count": doc_count})
    
    # Span 2: Entity extraction (LLM call)
    with trace.span(name="entity-extraction") as span:
        result = httpx.post(
            "http://localhost:8100/api/v1/cognify",
            json={"datasets": [dataset]},
            timeout=600,
        )
        span.update(
            metadata={
                "dataset": dataset,
                "status": "success" if result.status_code == 200 else "failed",
                "documents_processed": doc_count,
            }
        )
    
    # Span 3: Quality evaluation
    with trace.span(name="extraction-quality") as span:
        quality = evaluate_extraction_quality(dataset)
        span.update(metadata={"entities_extracted": quality["entity_count"]})
        span.score("entity_accuracy", quality["accuracy"])
    
    trace.update(output={"status": "complete", "dataset": dataset})
    return result
```

## Monitoring Cognify Costs

### Per-Dataset Cost Tracking

```python
def track_cognify_costs():
    """Report cognition costs by dataset."""
    traces = langfuse.fetch_traces(
        name="cognee-cognify-*",
        limit=50,
    )
    
    costs = {}
    for trace in traces:
        dataset = trace.metadata.get("dataset", "unknown")
        cost = sum(span.cost for span in trace.spans)
        costs[dataset] = costs.get(dataset, 0) + cost
    
    return costs

# Example output:
# {
#   "docs-agents": 0.42,
#   "docs-bonneagar": 1.87,
#   "docs-data-eng": 2.15,
#   "docs-ml": 1.04,
#   "docs-web": 1.12,
#   "docs-context": 0.23,
#   "total": 6.83
# }
```

## Tracing CCC Indexing Operations

```python
def ccc_index_with_tracing():
    """Trace CCC indexing runs."""
    trace = langfuse.trace(name="ccc-index")
    
    with trace.span(name="codebase-scan") as span:
        result = subprocess.run(
            ["bun", "run", "ccc:index"],
            capture_output=True, text=True,
        )
        files_indexed = len(result.stdout.splitlines())
        span.update(metadata={"files_indexed": files_indexed})
    
    trace.update(output={"status": "complete"})
```

## Key Metrics to Track

| Metric | Source | Dashboard |
|:--|:--|:--|
| Cognify cost per dataset | Langfuse traces | Cost by dataset chart |
| Entity extraction quality | RAGAS evaluation | Faithfulness score |
| Cognify latency | Langfuse span duration | Latency histogram |
| Documents processed per run | Trace metadata | Throughput chart |
| LLM token usage | Span token counts | Token usage by model |
| API error rate | Trace error events | Error rate chart |

## Langfuse Web UI

Access at `https://langfuse.cianfhoghlaim.ie`:

**Trace View**: Each cognition operation rendered as a waterfall timeline:
```
┌──────────────────────────────────────────────────────────┐
│ cognee-cognify-docs-agents (2.3s, $0.42)                 │
├──────────────────────────────────────────────────────────┤
│  ├─ document-count (0.1s)         116 documents           │
│  ├─ entity-extraction (1.8s)      1,847 tokens, $0.35    │
│  ├─ relationship-inference (0.3s)  234 edges, $0.05      │
│  └─ quality-evaluation (0.1s)     accuracy: 0.94         │
└──────────────────────────────────────────────────────────┘
```

**Dashboard View**: Aggregate metrics across all cognition runs:
- Total cognition cost (daily/weekly/monthly)
- Documents processed throughput
- Average entity extraction quality
- Most expensive documents (by token count)

## Alerting via Langfuse

Configure alerts for cognition pipeline health:

```
ALERT: cognify_cost > $10/run
  → Unexpected cost spike — may indicate model fallback or error retries

ALERT: extraction_quality < 0.85
  → Entity extraction degrading — may need prompt update or model change

ALERT: cognify_latency > 300s
  → Processing timeout — may indicate overloaded LLM API or Neo4j connection issues
```
