# Cognee + Memgraph Destination

The Cognee destination is a custom `@dlt.destination` that ingests
records into Cognee (for cognify / knowledge-graph construction)
and writes Cypher edges to Memgraph in parallel. The canonical
pattern is from the `dlt_cognee_memgraph.py` reference.

## When to use this

- You have a corpus that needs **knowledge-graph construction** (Cognee)
  AND **graph queries** (Memgraph Cypher)
- AND you want a **single dlt pipeline run** to populate both

## Pattern

```python
import dlt
import cognee
from cognee import SearchType

@dlt.destination(batch_size=10, loader_file_format="jsonl")
def cognee_destination(items, table):
    """Ingest records into Cognee for cognify."""
    async def _run():
        for item in items:
            text = item.get("text") or item.get("description") or str(item)
            await cognee.add(text)
        await cognee.cognify()  # build the knowledge graph
    asyncio.run(_run())

@dlt.destination(batch_size=100, loader_file_format="jsonl")
def memgraph_destination(items, table):
    """Write edges to Memgraph via Cypher."""
    from gqlalchemy import Memgraph
    mg = Memgraph()
    for item in items:
        if item.get("type") == "edge":
            mg.execute(
                "MATCH (a:Entity {id: $a_id}), (b:Entity {id: $b_id}) "
                "MERGE (a)-[r:RELATES_TO {kind: $kind}]->(b)",
                parameters={"a_id": item["from_id"], "b_id": item["to_id"], "kind": item["kind"]},
            )

@dlt.resource(name="curriculum")
def curriculum(pdf_path: str):
    """Extract text + entities from a PDF."""
    text = extract_pdf_text(pdf_path)
    for chunk in chunk_text(text):
        yield {"text": chunk, "source": pdf_path}

# Run the pipeline to all 3 destinations
pipeline = dlt.pipeline(destination="duckdb", dataset_name="curriculum")
load_info = pipeline.run([
    curriculum("ncca.pdf"),
    cognee_destination(curriculum("ncca.pdf")),
    memgraph_destination(curriculum("ncca.pdf")),
])
```

## Configuration

```bash
# .env
COGNEE_DATABASE_URL=postgres://cognee:cognee@localhost/cognee
MEMGRAPH_HOST=localhost
MEMGRAPH_PORT=7687
```

## Cognee dataset naming

By default, all records go to the `main_dataset`. To use a
project-specific dataset:

```python
import cognee

@cognee_destination(batch_size=10)
def my_destination(items, table):
    await cognee.add(text, dataset_name="cianfhoghlaim_curriculum")
    await cognee.cognify(dataset_name="cianfhoghlaim_curriculum")
```

## Rate limiting

Cognee cognify is expensive. To rate-limit:

```python
@dlt.destination(batch_size=10)
def cognee_destination(items, table):
    async def _run():
        for item in items:
            text = item.get("text")
            await cognee.add(text)
            await asyncio.sleep(0.1)  # 10 RPS
        await cognee.cognify()
    asyncio.run(_run())
```

## KCG usage

- `cianfhoghlaim-cognify-knowledge-graph` spec — 5-stage cross-stage
  cognify + 3 leabharlann cognify + 3 cross-archive FalkorDB edges
- `cocoindex/cognee_integration/` — the 3 cognify adapters
- `storage/graph/` — the application-layer FalkorDB + Memgraph
  clients (FalkorDB is the primary, Memgraph is the secondary)

## Reference

- The `dlt_cognee_memgraph.py` reference (200+ lines) was in
  `docs/dlt/` (deleted with the `sync-skills-from-docs` change)
- The `cognee` and `memgraph` skills for the upstream destination
  patterns
