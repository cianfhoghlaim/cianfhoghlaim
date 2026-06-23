# Performance Optimisation

For dlt pipelines that handle > 100k rows, performance matters.
This reference covers the 4 main optimisation levers.

## 1. Parallelised resources

By default, dlt resources are sequential. To parallelise:

```python
@dlt.resource(parallelized=True)
def chunks(pdf_paths: list[str]):
    for path in pdf_paths:
        text = extract_pdf_text(path)
        for chunk in chunk_text(text):
            yield {"text": chunk, "source": path}
```

The `parallelized=True` flag tells dlt to use multiple workers
(via `concurrent.futures.ThreadPoolExecutor` or
`ProcessPoolExecutor`, depending on the resource).

## 2. `add_limit(N)` for testing

Cap a resource for testing without modifying the source:

```python
load_info = pipeline.run(
    add_limit(curriculum(pdf_paths), 100),  # only 100 rows
)
```

Useful for development (skip the 10-minute load, test the schema
instead).

## 3. File rotation

For > 1M rows, dlt buffers to memory and writes in chunks. The
default chunk size is good for most cases, but for very large
loads, tune:

```python
@dlt.resource(
    file_max_items=100_000,  # rotate to a new file every 100k rows
    workers=4,  # number of parallel workers
)
def chunks(pdf_paths: list[str]):
    ...
```

## 4. Multi-pipeline-in-one-process

For multi-destination fan-out, run a single pipeline with multiple
destinations. State is unified:

```python
pipeline = dlt.pipeline(
    pipeline_name="curriculum",
    destination="duckdb",
    dataset_name="curriculum",
    progress="log",  # log progress instead of TUI
)
load_info = pipeline.run([
    curriculum_chunks("ncca.pdf"),
    lancedb_adapter(curriculum_chunks("ncca.pdf"), embed=["text"]),
    cognee_destination(curriculum_chunks("ncca.pdf")),
])
```

One `pipeline.run()`, three destinations, one `pipeline.last_trace`.

## Async generators

For I/O-bound sources, use `async` resources:

```python
@dlt.resource(parallelized=True)
async def chunks(pdf_paths: list[str]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_chunks(session, path) for path in pdf_paths]
        for chunks in asyncio.as_completed(tasks):
            for chunk in await chunks:
                yield chunk
```

## 5. `apply_hints` for incremental loading

For append-only sources that grow over time, use incremental
loading to skip already-seen rows:

```python
@dlt.resource(
    primary_key="id",
    write_disposition="merge",
)
def events():
    for event in fetch_events():
        yield event
```

dlt tracks the highest seen `id` and only inserts new ones. See the
`add-incremental-loading` sub-skill for the full pattern.

## Performance checklist

- [ ] `parallelized=True` for any source > 1k rows
- [ ] `add_limit(N)` for any test run
- [ ] `file_max_items` tuned for > 1M row loads
- [ ] `write_disposition="merge"` with explicit `primary_key` for
  upserts (not append)
- [ ] Multi-destination fan-out via single `pipeline.run(...)`
- [ ] `apply_hints` for incremental loading on growing sources
- [ ] `dlt pipeline ... trace` to inspect state and timing

## Reference

- The `dlt_optimisation.py` reference (900+ lines) was in `docs/dlt/`
  (deleted with the `sync-skills-from-docs` change). The same content
  is in the upstream dltHub docs under
  [performance](https://dlthub.com/docs/performance)
- The `add-incremental-loading` sub-skill
