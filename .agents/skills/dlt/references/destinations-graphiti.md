# Graphiti Destination (temporal knowledge graph)

Graphiti is a **temporal knowledge graph** — it tracks not just
"what is true" but "when did it become true" and "when did it stop
being true". This is essential for evolving data (e.g. a curriculum
that changes year-over-year).

## Pattern

```python
import dlt
from graphiti import Graphiti

# 1. Initialize the Graphiti client (once)
graphiti = Graphiti(
    uri=os.environ["NEO4J_URI"],
    user=os.environ["NEO4J_USER"],
    password=os.environ["NEO4J_PASSWORD"],
)

@dlt.destination(batch_size=10, loader_file_format="jsonl")
def graphiti_destination(items, table):
    """Ingest records into Graphiti as temporal episodes."""
    async def _run():
        for item in items:
            text = item.get("text") or item.get("description") or str(item)
            await graphiti.add_episode(
                name=f"dlt_{table['name']}_{item.get('id', 'unknown')}",
                episode_body=text,
                source_description=item.get("source", "dlt pipeline"),
                reference_time=item.get("valid_from", datetime.now()),
            )
    asyncio.run(_run())

@dlt.resource(name="curriculum")
def curriculum(pdf_path: str):
    text = extract_pdf_text(pdf_path)
    for i, chunk in enumerate(chunk_text(text)):
        yield {
            "text": chunk,
            "source": pdf_path,
            "id": f"{pdf_path}:{i}",
            "valid_from": extract_date_from_pdf(pdf_path),  # e.g. "2024-09-01"
        }

# Run
pipeline = dlt.pipeline(destination="duckdb", dataset_name="curriculum")
load_info = pipeline.run([
    curriculum("ncca_primary_2024.pdf"),
    graphiti_destination(curriculum("ncca_primary_2024.pdf")),
])
```

## Bi-temporal model

Graphiti tracks 2 time dimensions:

1. **Event time** (`reference_time`) — when the fact was true in
   the real world
2. **Ingestion time** — when Graphiti learned about the fact

When a fact changes (e.g. "the Junior Cycle maths syllabus was
revised in 2024"), Graphiti closes the old fact and opens a new one
**at the right event time**, not at the ingestion time. This is
the bi-temporal query model.

## Querying

```python
# Facts that were true on 2024-01-01
results = await graphiti.search(
    query="Junior Cycle maths syllabus",
    center_node_uuid=...,
    time_range=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
)

# All facts in the graph (for cognify-style analysis)
all_facts = await graphiti.get_all_facts()
```

## KCG usage

- `cocoindex/learning_outcome_graph.py` —
  the CocoIndex v1 App that feeds Graphiti
- `cianfhoghlaim-cognify-knowledge-graph` spec — the cross-archive
  knowledge graph that uses Graphiti's bi-temporal model for
  curriculum changes

## Reference

- The `baml-dlt-integration.md` reference (in `docs/dlt/`, deleted)
  is the canonical source. The same content is in the
  [getzep/graphiti](https://github.com/getzep/graphiti) repo
  under `examples/dlt_integration.py`
- The `graphiti` skill for upstream Graphiti patterns
