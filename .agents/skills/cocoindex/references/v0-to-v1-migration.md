# v0 → v1 Migration Guide

CocoIndex v1 is a fundamental redesign. v0 (`@cocoindex.flow_def`,
`data_scope`, `.row()`, `add_collector()`, `cocoindex.sources.X`,
`cocoindex.targets.X`, `cocoindex.functions.X`) is no longer
supported. This reference is a translation table for agents that
must update v0 code.

## Mental model change

| v0 | v1 |
|:--|:--|
| `flow_builder` + `data_scope` + `data_scope.add_collector()` | `coco.App` + `app_main` + `target.declare_row()` |
| `with data_scope["files"].row() as file: file["x"] = ...` | `@coco.fn(memo=True) async def process_file(file, target)` |
| `data_scope.add_collector()` + `collector.collect(field=...)` | `target.declare_row(row=MyRecord(...))` |
| `flow_builder.add_source(cocoindex.sources.X(...))` | `localfs.walk_dir(...)` / `await google_drive.connect(...)` (returns `source`) |
| `flow_builder.declare(...)` | `await lancedb.mount_table_target(...)` (returns `TableTarget`) |
| Engine state in Postgres (`COCOINDEX_DATABASE_URL`) | Engine state in **local LMDB** (no DB required for engine) |
| `cocoindex.GeneratedField.UUID` | `IdGenerator().next_id(text)` |
| `@cocoindex.op.function(behavior_version=1)` | `@coco.fn` (async) or plain Python function |
| `cocoindex.op.FunctionSpec` + `cocoindex.op.executor_class` | `@coco.fn(memo=True)` + shared `ContextKey` resource |
| `SplitRecursively` (decorator) | `RecursiveSplitter` (instance) |
| `DetectProgrammingLanguage` (decorator) | `detect_code_language(filename=...)` (function) |
| `SentenceTransformerEmbed` (decorator) | `SentenceTransformerEmbedder(model=...)` (instance) |
| `ExtractByLlm` (decorator) | Wrap a BAML or DSPy call in a `@coco.fn` |
| `cocoindex.transform_flow()` | Define a `@coco.fn` and call `.eval(...)` |
| `cocoindex.FlowLiveUpdater(...)` | `cocoindex update -L main` (CLI) |
| `my_flow.setup()` / `.update()` / `.drop()` | `cocoindex setup main` / `update main` / `drop main` |
| `flow.key` / `flow.metadata` | Component path derived from source keys (not user-visible) |

## Concrete v0 → v1 example: text embedding

### v0 (deprecated)

```python
import cocoindex
from cocoindex import functions as cf
from cocoindex import sources, targets

@cocoindex.flow_def(name="TextEmbeddingV0")
def text_embedding_flow(flow_builder, data_scope):
    data_scope["files"] = flow_builder.add_source(
        sources.LocalFile(path="markdown_files", included_patterns=["*.md"])
    )
    data_scope["chunks"] = data_scope["files"].transform(
        cf.SplitRecursively(), language="markdown", chunk_size=2000
    )
    data_scope["embeddings"] = data_scope["chunks"].transform(
        cf.SentenceTransformerEmbed(model="all-MiniLM-L6-v2")
    )
    collector = data_scope.add_collector()
    collector.collect(
        id=cocoindex.GeneratedField.UUID,
        text=data_scope["chunks"],
        embedding=data_scope["embeddings"],
        filename=data_scope["files"]["filename"],
    )
    collector.export(
        "embeddings",
        targets.Postgres(),
        primary_key_fields=["id"],
        vector_indexes=[
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
            )
        ],
    )
```

### v1 (current)

```python
import pathlib
from dataclasses import dataclass
from typing import Annotated, AsyncIterator
from numpy.typing import NDArray
import cocoindex as coco
from cocoindex.connectors import localfs, postgres
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.resources.id import IdGenerator
from cocoindex.resources.chunk import Chunk
from cocoindex.ops.text import RecursiveSplitter
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder]("embedder", detect_change=True)
PG_DB = coco.ContextKey[asyncpg.Pool]("pg_db")
_splitter = RecursiveSplitter()

@coco.lifespan
async def coco_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    import asyncpg
    builder.provide(PG_DB, await asyncpg.create_pool(os.environ["POSTGRES_URL"]))
    builder.provide(EMBEDDER, SentenceTransformerEmbedder(EMBED_MODEL))
    yield

@dataclass
class DocEmbedding:
    id: int
    filename: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]

@coco.fn
async def process_chunk(chunk: Chunk, filename: pathlib.PurePath,
                        id_gen: IdGenerator,
                        table: postgres.TableTarget[DocEmbedding]) -> None:
    table.declare_row(row=DocEmbedding(
        id=await id_gen.next_id(chunk.text),
        filename=str(filename),
        text=chunk.text,
        embedding=await coco.use_context(EMBEDDER).embed(chunk.text),
    ))

@coco.fn(memo=True)
async def process_file(file: FileLike, table: postgres.TableTarget[DocEmbedding]) -> None:
    text = await file.read_text()
    chunks = _splitter.split(text, chunk_size=2000, chunk_overlap=500, language="markdown")
    id_gen = IdGenerator()
    await coco.map(process_chunk, chunks, file.file_path.path, id_gen, table)

@coco.fn
async def app_main(sourcedir: pathlib.Path) -> None:
    target_table = await postgres.mount_table_target(
        PG_DB, table_name="doc_embeddings",
        table_schema=await postgres.TableSchema.from_class(DocEmbedding, primary_key=["id"]),
    )
    target_table.declare_vector_index(column="embedding")
    files = localfs.walk_dir(
        sourcedir, recursive=True,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/*.md"]),
        live=True,
    )
    await coco.mount_each(process_file, files.items(), target_table)

app = coco.App(coco.AppConfig(name="TextEmbeddingV1"), app_main,
               sourcedir=pathlib.Path("./markdown_files"))
```

## CLI translation

| v0 | v1 |
|:--|:--|
| `python main.py` (with `flow.update()`) | `cocoindex update main` |
| `python main.py` (with `FlowLiveUpdater`) | `cocoindex update -L main` |
| `python main.py` (with `flow.setup()`) | `cocoindex setup main` |
| `python main.py` (with `flow.drop()`) | `cocoindex drop main` |
| `python main.py` (with `flow.evaluate(...).dump(...))` | `cocoindex evaluate main:<app_name> --output-dir ./test_output` |
| `COCOINDEX_DATABASE_URL` env var | Not required (engine uses local LMDB) |
| `COCOINDEX_SOURCE_MAX_INFLIGHT_ROWS` | Still supported in v1 |

## When v0 is still present in the codebase

- `cocoindex/*.py` — most flows are v1 (e.g.
  `docs_skills_consolidation.py`, `leabharlann_embedding.py`,
  `codebase_indexing.py`); a few older ones (`pdf_embedding.py`,
  `research_embedding.py`) may still be v0
- Any new flow written in v0 should be rewritten in v1 (the
  `cocoindex-v1-migration` spec mandates it)

## When in doubt

- The canonical in-repo v1 example is
  `cocoindex/docs_skills_consolidation.py`
- The canonical external v1 examples are in the
  [upstream `docs/cocoindex/` repo](https://github.com/cocoindex-io/cocoindex/tree/main/examples)
  (these were deleted from this repo in the
  `sync-skills-from-docs` change, but the same examples are mirrored
  in the official cocoindex repo)
