---
name: cocoindex
description: Comprehensive toolkit for developing with the CocoIndex v1 library. Use when users need to create data transformation pipelines (flows) using the v1 `coco.App` + `@coco.fn` + `ContextKey` + `mount_table_target` + `Annotated[NDArray, EMBEDDER]` model, write custom functions, or operate flows via CLI or API. Covers building ETL workflows for AI data processing, including embedding documents into vector databases, building knowledge graphs, creating search indexes, or processing data streams with incremental updates.
---

# CocoIndex v1

> **v0 → v1**: CocoIndex v1 is a fundamental redesign. v0 (`@cocoindex.flow_def`,
> `data_scope`, `.row()`, `add_collector()`, `cocoindex.sources.X`,
> `cocoindex.targets.X`, `cocoindex.functions.X`) is **no longer supported**.
> This skill documents v1 only. See
> [`references/v0-to-v1-migration.md`](references/v0-to-v1-migration.md)
> if you must translate v0 code.

## Overview

CocoIndex v1 is a Rust-backed real-time data transformation framework
for AI with incremental processing. This skill enables building
**indexing flows** (`coco.App` instances) that walk data sources,
apply transformations (chunking, embedding, LLM extraction), and
export to typed targets (vector databases, graph databases, relational
databases, custom sinks).

**Core capabilities:**

1. **Write indexing flows** — `coco.App` + `app_main` + `mount_each`
2. **Create custom functions** — `@coco.fn` (sync/async, `memo=True`/`memo=False`)
3. **Share resources** — `ContextKey[T]` + `@coco.lifespan`
4. **Wire sources** — `localfs.walk_dir`, `google_drive`, `kafka`, `postgres`
5. **Wire targets** — `lancedb`, `postgres`, `qdrant`, `neo4j`, `falkordb`,
   `kafka`, `localfs` (custom file output)
6. **Operate flows** — `cocoindex update <flow>:<app_name>` (CLI)

**The v1 mental model — `target_state = transform(source_state)`.**
You declare what the target should look like; the Rust engine keeps
it in sync, reprocessing only what changed. State is tracked in a
local **LMDB store** (the engine does NOT require a database for its
own state — only when an example writes to a target database).

**Key features:**

- **Incremental processing** — only changed data is reprocessed
- **Live updates** — `cocoindex update -L` watches the source
- **Memoised functions** — `@coco.fn(memo=True)` for LLM/embedding/OCR
- **Multi-target fan-out** — one app, multiple `mount_*_target` calls
- **Pluggable LLMs/embedders** — openai, anthropic, google, voyage, ollama
- **Pluggable sinks** — pgvector, Qdrant, LanceDB, Neo4j, FalkorDB, Kafka

**For detailed documentation:** <https://cocoindex.io/docs/>
**Search documentation:** <https://cocoindex.io/docs/search?q=url%20encoded%20keyword>

## When to Use This Skill

Use when users request:

- "Build a vector search index for my documents" → use `lancedb` or `qdrant` target
- "Create an embedding pipeline for code/PDFs/images" → use `code_embedding`,
  `pdf_embedding`, `image_search` patterns
- "Extract structured information using LLMs" → use `baml_extraction` or
  `dspy_extraction` patterns
- "Build a knowledge graph from documents" → use `knowledge_graph_build` pattern
- "Set up live document indexing" → use `live_updates` pattern with `-L` flag
- "Run/update my CocoIndex flow" → use the CLI section below
- "Watch a Google Drive folder" → use the `google_drive` source

## Flow Writing Workflow

### Step 1: Understand requirements

Ask clarifying questions to understand:

**Data source:**

- Where is the data? (local files, S3, Google Drive, Postgres, Kafka)
- What file types? (text, PDF, JSON, images, code, etc.)
- How often does it change? (one-time, periodic, continuous)

**Transformations:**

- What processing is needed? (chunking, embedding, extraction, etc.)
- Which embedding model? (sentence-transformers, OpenAI, Cohere, etc.)
- Any custom logic? (filtering, parsing, enrichment, BAML extraction)

**Target:**

- Where should results go? (LanceDB, Postgres+pgvector, Qdrant, Neo4j, FalkorDB)
- What schema? (fields, primary keys, vector indexes)
- Vector search needed? (specify similarity metric — usually cosine)

### Step 2: Install dependencies

```bash
# Base
uv add cocoindex

# Embeddings (sentence-transformers)
uv add "cocoindex[embeddings]"

# Multimodal (ColPali for image/document embeddings)
uv add "cocoindex[colpali]"

# LanceDB target
uv add "cocoindex[lancedb]"

# Multiple extras
uv add "cocoindex[embeddings,lancedb]"
```

**For installation details:** <https://cocoindex.io/docs/getting_started/installation>

### Step 3: Set up the environment

**Key change from v0**: CocoIndex v1 does NOT require a database for
its own state. The engine uses a local LMDB store. The target DB
(e.g. Postgres for pgvector, LanceDB, etc.) is the only database
you need.

If your target is Postgres (pgvector):

```bash
# Local Postgres + pgvector
docker compose -f dev/postgres.yaml up -d
```

Set the connection URL:

```bash
# .env
POSTGRES_URL=postgres://cocoindex:cocoindex@localhost/cocoindex
# OR for LanceDB
LANCEDB_URI=./lancedb_data
```

**For flows requiring LLM APIs** (embeddings, extraction):

```bash
OPENAI_API_KEY=sk-...          # For OpenAI (generation + embeddings)
ANTHROPIC_API_KEY=sk-ant-...   # For Anthropic (generation only)
GOOGLE_API_KEY=...             # For Gemini (generation + embeddings)
VOYAGE_API_KEY=pa-...          # For Voyage (embeddings only)
# Ollama requires no API key (local)
```

**Never create manual `.env` files.** See the project AGENTS.md
("Strict Secret Hydration") — use the Infisical + mise path.

### Step 4: Write the App

The minimal v1 app is a `coco.App` + `app_main` + a per-row `@coco.fn`:

```python
import pathlib
from dataclasses import dataclass
from typing import Annotated, AsyncIterator
from numpy.typing import NDArray
from dotenv import load_dotenv
import cocoindex as coco
from cocoindex.connectors import localfs
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.resources.id import IdGenerator
from cocoindex.resources.chunk import Chunk
from cocoindex.ops.text import RecursiveSplitter
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder


EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TABLE_NAME = "doc_embeddings"
EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder](
    "embedder", detect_change=True
)
_splitter = RecursiveSplitter()


@coco.lifespan
async def coco_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    builder.provide(EMBEDDER, SentenceTransformerEmbedder(EMBED_MODEL))
    yield


@dataclass
class DocEmbedding:
    id: int
    filename: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]


@coco.fn
async def process_chunk(
    chunk: Chunk,
    filename: pathlib.PurePath,
    id_gen: IdGenerator,
    table: coco.lancedb.TableTarget[DocEmbedding],  # type: ignore[name-defined]
) -> None:
    table.declare_row(
        row=DocEmbedding(
            id=await id_gen.next_id(chunk.text),
            filename=str(filename),
            text=chunk.text,
            embedding=await coco.use_context(EMBEDDER).embed(chunk.text),
        ),
    )


@coco.fn(memo=True)
async def process_file(
    file: FileLike,
    table: coco.lancedb.TableTarget[DocEmbedding],  # type: ignore[name-defined]
) -> None:
    text = await file.read_text()
    chunks = _splitter.split(text, chunk_size=2000, chunk_overlap=500, language="markdown")
    id_gen = IdGenerator()
    await coco.map(process_chunk, chunks, file.file_path.path, id_gen, table)


@coco.fn
async def app_main(sourcedir: pathlib.Path) -> None:
    from cocoindex.connectors import lancedb  # noqa: PLC0415
    target_table = await lancedb.mount_table_target(
        LANCE_DB,  # type: ignore[name-defined]
        table_name=TABLE_NAME,
        table_schema=await lancedb.TableSchema.from_class(
            DocEmbedding, primary_key=["id"]
        ),
    )
    target_table.declare_vector_index(column="embedding")
    files = localfs.walk_dir(
        sourcedir,
        recursive=True,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/*.md"]),
        live=True,
    )
    await coco.mount_each(process_file, files.items(), target_table)


app = coco.App(
    coco.AppConfig(name="MyEmbeddingApp"),
    app_main,
    sourcedir=pathlib.Path("./markdown_files"),
)


if __name__ == "__main__":
    load_dotenv()
    coco.init()
    app.update()
```

**Key v1 principles:**

- Each source creates a field at the top level (`app_main` receives the
  source dir as a kwarg)
- `@coco.fn(memo=True)` is idempotent — re-runs with the same args are
  cached; use it for expensive per-file/per-chunk work
- `@coco.fn` (no `memo`) always re-runs — use for target mount setup
  and any non-idempotent reconciliation
- `ContextKey[T](name, detect_change=...)` is the typed handle for a
  shared resource (connection, embedder, model)
- `Annotated[NDArray, EMBEDDER]` on a `@dataclass` row tells the
  engine the dimension comes from the `EMBEDDER` ContextKey
- `mount_table_target` returns a `TableTarget[Row]`; call
  `declare_row(row=...)` to emit a row
- `mount_each(fn, source.items(), *extra)` fans out a `@coco.fn` across
  source items
- `map(fn, items, *extra)` is the parallel-processing primitive for
  in-memory lists

**Common v0 mistakes to avoid:**

❌ **v0 (wrong)** — using local variables for transformations

```python
with data_scope["files"].row() as file:
    summary = file["content"].transform(...)  # ❌ local var
```

✅ **v1 (correct)** — assigning to row fields, OR using `@coco.fn`

```python
@coco.fn(memo=True)
async def process_file(file: FileLike, target) -> None:
    summary = some_llm_call(file.text)  # ✅ local var is fine
    target.declare_row(row=MyRecord(summary=summary))
```

### Step 5: Run the flow

```bash
# One-shot catch-up
cocoindex update main

# Live mode (requires live=True on the source)
cocoindex update -L main

# Force reset and re-run
cocoindex update --reset main
```

**For complete v1 reference**, see:
- [`references/api_reference.md`](references/api_reference.md) — the
  canonical v1 API surface
- [`references/connectors.md`](references/connectors.md) — every
  source + target (lancedb, postgres, qdrant, neo4j, falkordb, kafka, …)
- [`references/patterns.md`](references/patterns.md) — 7 v1 flow
  patterns (text embedding, code embedding, knowledge graph, live
  updates, custom targets, concurrency, custom functions)
- [`references/setup_database.md`](references/setup_database.md) —
  target DB setup
- [`references/setup_project.md`](references/setup_project.md) —
  project skeleton
- [`references/cocoindex-api-research.md`](references/cocoindex-api-research.md)
  — openAPI surface research

## Data Types

CocoIndex v1 has a type system independent of programming languages.
All types are determined at flow definition time, making schemas clear
and predictable.

**IMPORTANT — when to define types:**

- **Custom function return values**: type annotations are **required** —
  they are the source of truth for type inference
- **Custom function arguments**: relaxed — can use `Any`, `dict[str, Any]`
- **Flow definitions**: no explicit type annotations needed —
  CocoIndex infers types from sources and functions
- **Dataclasses/Pydantic models**: only create them when **actually
  used** (as function parameters/returns or `mount_table_target`
  row type) — NOT to mirror flow field schemas

**Common type categories:**

1. **Primitives**: `str`, `int`, `float`, `bool`, `bytes`,
   `datetime.date`, `datetime.datetime`, `uuid.UUID`

2. **Vector types** (embeddings): specify dimension via
   `Annotated[NDArray, EMBEDDER]` where `EMBEDDER` is a `ContextKey`
   holding a model/embedder. The dimension is inferred automatically.
   ```python
   from typing import Annotated
   from numpy.typing import NDArray

   @dataclass
   class Record:
       embedding: Annotated[NDArray, EMBEDDER]
   ```

3. **Struct types**: `dataclass`, `NamedTuple`, or `Pydantic BaseModel`
   ```python
   @dataclass
   class Person:
       name: str
       age: int
   ```

4. **Resource types** (from `cocoindex.resources`):
   - `FileLike` — a file from a `walk_dir` source
   - `PatternFilePathMatcher` — the file-path filter
   - `Chunk` — a chunk from `RecursiveSplitter.split(...)`
   - `IdGenerator` — for stable per-row IDs

5. **Optional types**: `T | None` for nullable

**For comprehensive data types documentation:** <https://cocoindex.io/docs/core/data_types>

## Built-in Operations

### Text Processing

**RecursiveSplitter** — chunk text intelligently

```python
from cocoindex.ops.text import RecursiveSplitter

_splitter = RecursiveSplitter()
chunks = _splitter.split(
    text, chunk_size=2000, chunk_overlap=500, language="markdown"
)
# languages: "markdown", "python", "javascript", "rust", "go", …
```

**detect_code_language** — detect language from filename

```python
from cocoindex.ops.text import detect_code_language

language = detect_code_language(filename="server.py")  # → "python"
```

### Embeddings

**SentenceTransformerEmbedder** — local embedding model (requires
`cocoindex[embeddings]`)

```python
from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder("sentence-transformers/all-MiniLM-L6-v2")
vec = await embedder.embed(text)  # NDArray, dim per model
```

**Wrap an external embedder** in a ContextKey + `@coco.lifespan`:

```python
EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder]("embedder", detect_change=True)

@coco.lifespan
async def coco_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    builder.provide(EMBEDDER, SentenceTransformerEmbedder(EMBED_MODEL))
    yield
```

**ColPaliEmbedImage** — multimodal image/document embeddings
(requires `cocoindex[colpali]`)

```python
from cocoindex.ops.colpali import ColPaliEmbedImage  # noqa: F401

image["embedding"] = image["img_bytes"].transform(
    cocoindex.functions.ColPaliEmbedImage(model="vidore/colpali-v1.2")
)
```

### LLM Extraction

**BAML** — see [`references/baml-extraction.md`](references/baml-extraction.md).
BAML functions return typed Python objects via `baml_py`.

**DSPy** — see [`references/dspy-extraction.md`](references/dspy-extraction.md).
DSPy signatures + `dspy.ChainOfThought` work in v1 via `@coco.fn` wrapping
`dspy.Predict` / `dspy.ChainOfThought`.

## Sources

| Source | Module | Use case |
|:--|:--|:--|
| `localfs.walk_dir` | `cocoindex.connectors.localfs` | Local files (PDF/MD/Python/…) |
| `GoogleDriveSource` | `cocoindex.connectors.google_drive` | Google Drive folders |
| `kafka.topic_as_map` | `cocoindex.connectors.kafka` | Kafka consumer |
| `Postgres` | `cocoindex.connectors.postgres` | Query an existing Postgres table |

**For all sources**: <https://cocoindex.io/docs/sources/>

### `localfs.walk_dir` (canonical KCG pattern)

```python
from cocoindex.connectors import localfs
from cocoindex.resources.file import PatternFilePathMatcher

files = localfs.walk_dir(
    pathlib.Path("leabharlann/gaeilge"),
    recursive=True,
    path_matcher=PatternFilePathMatcher(
        included_patterns=["**/*.pdf", "**/*.docx"],
        excluded_patterns=["**/previews", "**/.*", "**/__pycache__"],
    ),
    live=True,  # Required for `cocoindex update -L`
)
```

`files.items()` yields `(path_key, FileLike)` tuples. The `path_key`
is a stable identifier that CocoIndex uses to derive component paths
for memoisation.

## Targets

| Target | Module | Vector index |
|:--|:--|:--|
| `LanceDB` | `cocoindex.connectors.lancedb` | Yes (HNSW) |
| `Postgres+pgvector` | `cocoindex.connectors.postgres` | Yes (ivfflat/HNSW) |
| `Qdrant` | `cocoindex.connectors.qdrant` | Yes |
| `Turbopuffer` | `cocoindex.connectors.turbopuffer` | Yes |
| `Neo4j` (nodes + relations) | `cocoindex.connectors.neo4j` | No |
| `FalkorDB` (nodes + relations) | `cocoindex.connectors.falkordb` | No |
| `Kafka` (stream output) | `cocoindex.connectors.kafka` | No |
| `localfs.declare_file` (custom file output) | `cocoindex.connectors.localfs` | No |

**For all targets**: <https://cocoindex.io/docs/targets/>

### `mount_table_target` (the canonical v1 target pattern)

```python
target_table = await lancedb.mount_table_target(
    LANCE_DB,                  # ContextKey[Connection]
    table_name="my_table",
    table_schema=await lancedb.TableSchema.from_class(
        MyRecord, primary_key=["id"]
    ),
)
target_table.declare_vector_index(column="embedding")
```

Every target has a `mount_*_target` convenience that takes a
`ContextKey` and returns a `TableTarget[Row]`. The target object
exposes `declare_row(row=...)` (and graph targets: `declare_record`,
`declare_relation`).

## See also: docs-skills-consolidation

The Cianfhoghlaim monorepo runs a CocoIndex v1 App that tags, embeds,
and graph-links every file in `docs/` and `.agents/skills/`. It is the
upstream-of-this-skill — every Markdown doc and every skill file in
this repo is the source of one or more `DocSkill` nodes in the
`docs_skills_graph` FalkorDB graph and one or more `docs_skills_chunks`
rows in LanceDB.

- **App**: `oideachais/cocoindex_flows/docs_skills_consolidation.py`
- **Dagster assets**: `oideachais/dagster_defs/assets/docs_skills_assets.py`
  (groups `docs_skills` + `codebase`)
- **BAML schema**: `baml_src/docs_skills_consolidation.baml`
- **OpenSpec change**: `openspec/changes/docs-skills-consolidation-pipeline/`
- **Run catch-up**: `bun run docs:consolidate` (or `mise docs:consolidate`)
- **Run live**:    `bun run docs:consolidate:live`
- **Search**: `from oideachais.cocoindex_flows.docs_skills_consolidation import search_docs_skills; asyncio.run(search_docs_skills("<query>"))`

The companion codebase-indexing v1 App (replacement for the legacy
`ccc` CLI) lives at
`oideachais/cocoindex_flows/codebase_indexing.py`; see the `ccc`
skill's deprecation banner.

**For comprehensive documentation:** <https://cocoindex.io/docs/>
**Search specific topics:** <https://cocoindex.io/docs/search?q=url%20encoded%20keyword>
