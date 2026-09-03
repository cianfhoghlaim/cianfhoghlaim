# dlt Transformations (chained dlt → dlt)

`dlt.transformer` is the canonical pattern for **chaining dlt
sources together** within a single pipeline. The second source
consumes rows from the first, applies a transformation, and
yields the result.

## Basic pattern

```python
@dlt.resource(name="chunks")
def chunks(pdf_paths: list[str]):
    for path in pdf_paths:
        text = extract_pdf_text(path)
        for i, chunk in enumerate(chunk_text(text)):
            yield {"text": chunk, "source": path, "chunk_id": i}

@dlt.transformer(data_from=chunks)
def embed_chunks(chunk: dict):
    """Consume one row from `chunks` and yield the embedded version."""
    yield {
        **chunk,
        "embedding": embed(chunk["text"]),  # list[float]
    }

# Run: chunks → embed_chunks → destination
pipeline = dlt.pipeline(destination="duckdb", dataset_name="curriculum")
load_info = pipeline.run(embed_chunks(pdf_paths))
```

## SQL-based transformations

For SQL-on-data transformations (e.g. aggregations, joins), use
`dlt.transformer` with a SQL query:

```python
@dlt.transformer(data_from=chunks)
def chunk_stats(chunk: dict):
    """Compute word count per chunk."""
    yield {
        "chunk_id": chunk["chunk_id"],
        "word_count": len(chunk["text"].split()),
    }
```

Or use the `dlt` SQL integration directly:

```python
pipeline = dlt.pipeline(destination="duckdb", dataset_name="curriculum")
pipeline.run([
    chunks(["ncca.pdf"]),       # raw chunks
    "SELECT source, COUNT(*) AS chunk_count FROM chunks GROUP BY source",  # SQL aggregation
])
```

## Ibis aggregation

For complex analytics, use Ibis (a portable dataframe API) on top
of dlt:

```python
import ibis

pipeline = dlt.pipeline(destination="duckdb", dataset_name="curriculum")
con = pipeline.dataset().ibis()  # Ibis connection to the dlt-managed DuckDB

# Now run Ibis expressions
chunks_table = con.table("chunks")
stats = (
    chunks_table
    .group_by("source")
    .aggregate(chunk_count=chunks_table.count(), avg_length=chunks_table.text.length().mean())
    .execute()
)
```

## Multi-yield from a single resource

A `dlt.resource` can yield multiple types of rows:

```python
@dlt.resource(name="document_analysis", primary_key="id")
def document_analysis(pdf_paths: list[str]):
    for path in pdf_paths:
        text = extract_pdf_text(path)
        # Yield the raw text
        yield {"id": path, "type": "raw_text", "text": text}
        # Yield the chunks
        for i, chunk in enumerate(chunk_text(text)):
            yield {"id": f"{path}:{i}", "type": "chunk", "text": chunk}
        # Yield the entities
        entities = b.ExtractEntities(text)
        for e in entities:
            yield {"id": f"{path}:{e.name}", "type": "entity", "name": e.name, "kind": e.type}
```

The destination has 3 tables: `raw_text`, `chunk`, `entity`.

## KCG usage

The KCG stack uses `dlt.transformer` in:

- `dlt/british_isles/ireland/` — chain raw pages → parsed
  curriculum → BAML-extracted outcomes
- `dlt/leabharlann/` — chain Takeout files
  → extracted text → BAML entities

## Reference

- The `Transformations _ dlt Docs.md` reference (25K) was in
  `docs/dlt/` (deleted with the `sync-skills-from-docs` change).
  The same content is in the dltHub docs at
  <https://dlthub.com/docs/dlt-ecosystem/transformations>
- The `ibis` skill for Ibis patterns
