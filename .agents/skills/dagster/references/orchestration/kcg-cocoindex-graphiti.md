# KCG Orchestration: CocoIndex + Graphiti Asset Graph

The KCG asset graph is the canonical orchestration pattern for
ingesting Celtic education content end-to-end. It chains:

```
raw_pdf → extracted_markdown → semantic_chunks → vector_embeddings → knowledge_graph_episodes
```

with **`DynamicPartitionsDefinition`** per file and a sensor-driven
`add_dynamic_partitions(...)` flow.

This reference is a synthesis of `docs/dagster/dagster-orchestration.md`
(526 lines, the longer / more recent draft) and
`docs/dagster/Dagster Orchestration for Cocoindex, Graphiti.md`
(399 lines, an older draft). The longer one is the source of truth;
the older one is deprecated.

## Asset graph (canonical)

```python
# orchestration/defs/curriculum_assets.py
from dagster import asset, AssetExecutionContext
from dagster_cocoindex import CocoIndexResource

@asset(group_name="curriculum")
def raw_pdf(context: AssetExecutionContext, pdf_path: str) -> str:
    """Read a raw PDF from stedding/ingest_queue."""
    return extract_pdf_text(pdf_path)

@asset(group_name="curriculum")
def extracted_markdown(context: AssetExecutionContext, raw_pdf: str) -> str:
    """Convert the raw PDF text to markdown via docling."""
    return docling_convert(raw_pdf)

@asset(group_name="curriculum")
def semantic_chunks(context: AssetExecutionContext, extracted_markdown: str) -> list[str]:
    """Chunk the markdown via CocoIndex RecursiveSplitter."""
    splitter = RecursiveSplitter()
    return splitter.split(extracted_markdown, chunk_size=2000, chunk_overlap=500)

@asset(group_name="curriculum")
def vector_embeddings(context: AssetExecutionContext, semantic_chunks: list[str]) -> list[list[float]]:
    """Embed the chunks with BGE-large-en-v1.5."""
    embedder = SentenceTransformerEmbedder("BAAI/bge-large-en-v1.5")
    return [embedder.embed(chunk) for chunk in semantic_chunks]

@asset(group_name="curriculum")
def knowledge_graph_episodes(
    context: AssetExecutionContext,
    semantic_chunks: list[str],
    vector_embeddings: list[list[float]],
) -> None:
    """Ingest the chunks as Graphiti episodes (bi-temporal KG)."""
    graphiti = Graphiti(...)
    for chunk, embedding in zip(semantic_chunks, vector_embeddings):
        await graphiti.add_episode(
            name=f"curriculum_{hash(chunk)}",
            episode_body=chunk,
            source_description="NCCA curriculum PDF",
            reference_time=extract_date_from_context(),
        )
```

## Dynamic partitions

The `curriculum` asset group uses `DynamicPartitionsDefinition` to
add a partition per file at runtime:

```python
from dagster import DynamicPartitionsDefinition, sensor, RunRequest, SensorEvaluationContext

curriculum_partitions = DynamicPartitionsDefinition(name="exam_papers")

@sensor(job=curriculum_assets_job)
def leaving_cert_sensor(context: SensorEvaluationContext):
    """Watch for new PDFs in stedding/ingest_queue/leaving_cert/."""
    for pdf in glob("stedding/ingest_queue/leaving_cert/2027/*.pdf"):
        partition_key = f"2027|english_p1"
        # Add the partition if not present
        if partition_key not in context.instance.get_dynamic_partitions("exam_papers"):
            context.instance.add_dynamic_partitions("exam_papers", [partition_key])
        yield RunRequest(run_key=partition_key, partition_key=partition_key)
```

## CocoIndex `SplitRecursively` pattern

The chunking step uses the v0 `SplitRecursively` decorator (the v0
`@cocoindex.flow_def` pattern is preserved for backwards
compatibility, but new flows use the v1 `coco.App` API — see the
`cocoindex` skill for the migration guide):

```python
@cocoindex.flow_def(name="CurriculumChunking")
def curriculum_chunking(flow_builder, data_scope):
    data_scope["chunks"] = data_scope["markdown"].transform(
        cocoindex.functions.SplitRecursively(),
        language="markdown",
        chunk_size=2000,
    )
```

## Graphiti bi-temporal ingestion

The `knowledge_graph_episodes` asset uses Graphiti's bi-temporal
model — it tracks both the **event time** (when the fact was true)
and the **ingestion time** (when Graphiti learned about it). For
curriculum data, the event time is the academic year (e.g.
"2024-09-01" for the 2024-25 syllabus).

## Asset check

Each asset has a check that validates the output:

```python
from dagster import asset_check, AssetCheckResult

@asset_check(asset=vector_embeddings)
def vector_embeddings_check(context: AssetCheckEvaluationContext, vector_embeddings):
    """Validate that all embeddings are 1024-d float32."""
    for i, emb in enumerate(vector_embeddings):
        if len(emb) != 1024:
            return AssetCheckResult(
                passed=False,
                metadata={"row_index": i, "expected_dim": 1024, "actual_dim": len(emb)},
            )
    return AssetCheckResult(passed=True)
```

## KCG production usage

- The `cianfhoghlaim-pipeline` spec — the canonical asset graph
- The `orchestration/defs/curriculum_assets.py` — the
  33+ Ireland curriculum assets
- The `orchestration/sensors/leabharlann_sensors.py` —
  the directory-watch sensors that fire the affected partitions
- The `cocoindex/learning_outcome_graph.py` —
  the Graphiti ingestion flow

## Reference

- The full `docs/dagster/dagster-orchestration.md` (526 lines) and
  the older `Dagster Orchestration for Cocoindex, Graphiti.md` (399
  lines) were in `docs/dagster/` (deleted with the
  `sync-skills-from-docs` change)
- The `cianfhoghlaim-pipeline` openspec spec for the partition scheme
  + asset graph
- The `cocoindex` skill for the v0 → v1 migration
- The `graphiti` skill for the bi-temporal model
