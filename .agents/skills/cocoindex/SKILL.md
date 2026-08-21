---
name: cocoindex
description: Toolkit for CocoIndex v1 library (pip v1.0.14, 2026-06-25; docs frozen on v1.0.7 / 2026-06-23 — verified live 2026-06-29). Use when users need pipelines with the v1 `coco.App` + `@coco.fn` + `ContextKey` + `mount_table_target` + `Annotated[NDArray, EMBEDDER]` model, 17 source/target connectors (S3, Doris, FalkorDB, Google Drive, Iggy, Kafka, LanceDB, LocalFS, Neo4j, OCI Object Storage, Postgres, Qdrant, SQLite, SurrealDB, Turbopuffer, Valkey, zvec), execution primitives (`memo=True`, `logic_tracking`, `version`, `deps`, `batching=True`, `runner=coco.GPU`, `as_async`), and lifecycle via `@coco.lifespan` + `coco.start() / coco.stop() / coco.runtime()`. Powers the 7 BIEP v1 Apps (6 LC subjects + `government_circulars`) + the canonical `_lifespan.py` shared embedder (`BAAI/bge-m3`, 1024-d). PyPI marks 1.0.8 as yanked; pin `>=1.0,<2.0,!=1.0.8`.
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

## v7 flattening migration notes (added 2026-07-19)

Per openspec/changes/2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1:

- CocoIndex Apps are now under `cianfhoghlaim.cocoindex.<subdir>` (NOT
  `cianfhoghlaim.cocoindex_flows.<subdir>`)
- The shared lifespan is at `cianfhoghlaim.cocoindex_flows._shared._lifespan`
  (use `from .._shared._lifespan import shared_lifespan, LANCE_DB, EMBEDDER`)
- Each App's module-scope `app = coco.App(...)` MUST be named `app` for
  the R3 linter to pass; for Apps using other names (like
  `cross_subject_competency_app` or `leabharlann_books_app`), the R3
  linter has been loosened to accept any `*_app`, `*_embedding`,
  `*App` name as a module-scope CocoIndex App
- Each sub-directory MUST have `__init__.py` for Python to treat it as
  a package (not just a namespace directory)

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

**Round 8 phase 1 (2026-06-23) — code-graph companion pattern:**

The canonical v1 codebase indexer (`cocoindex_flows/codebase_indexing.py`)
now has a code-graph companion v1 App (`codebase_graph_app`) that
extracts AST relationships into 2 LanceDB tables
(`codebase_graph` + `codebase_graph_edges`). 7 node types +
7 edge types, 11 languages with Tree-sitter AST mappings,
29+ languages detected via
`cocoindex_flows/chunking/languages.py`. The companion
App is driven by 3 Dagster assets in
`orchestration/defs/3_model_lifecycle/codebase_assets.py`:
`codebase_chunks`, `codebase_code_graph`, `codebase_architecture_docs`.

**Round 7 phase 2 (2026-06-24) — 4 v1 infrastructure companions:**

The infrastructure surface (HTTP routes, filesystem layout, storage
backends, config files) is now on v1 CocoIndex via 4 new Apps in
`cocoindex/`:

- `api_indexing.py` (v1 App `ApiIndex`) — 4 frameworks (FastAPI +
  Hono + TanStack Start + Convex HTTP) → `api_endpoints` LanceDB
- `filesystem_indexing.py` (v1 App `FilesystemIndex`) — depth 1-4
  dirs + per-dir file-type histogram → `filesystem_layout` LanceDB
- `storage_indexing.py` (v1 App `StorageIndex`) — 9 backend kinds
  (lancedb / duckdb / ducklake / postgres / garage / r2 / d1 / kv /
  iceberg) → `storage_backends` LanceDB
- `config_indexing.py` (v1 App `ConfigIndex`) — 12 config kinds
  (compose / mise / package / pyproject / turbo / wrangler / env /
  k8s / pulumi / dg / github / justfile) → `config_files` LanceDB

Driven by 4 Dagster assets in
`orchestration/defs/3_model_lifecycle/infrastructure_assets.py`:
`api_endpoints`, `filesystem_layout`, `storage_backends`,
`config_files` (group `infrastructure`).

**Round 7 phase 3 (2026-06-24) — 2 v1 embedding Apps:**

The unified embedding pipeline from
`cocoindex_flows/unified_embedding.py` is now on v1
CocoIndex via 2 Apps in `cocoindex_flows/unified_embedding.py`:

- `unified_app` (v1 App `UnifiedEmbedding`) — reads from any DuckDB
  connection (default: `crypteolas_catalog.docs.scraped_documents`),
  chunks with `RecursiveSplitter` (markdown) or paragraph+char
  fallback, embeds with BGE-M3, writes to the `unified_embeddings`
  LanceDB table.
- `code_app` (v1 App `CodeEmbedding`) — walks `UNIFIED_CODE_ROOT`
  for `*.py`/`*.ts`/`*.tsx`/`*.js`/`*.jsx`/`*.rs`/`*.go`/`*.sol`,
  chunks with `RecursiveSplitter(detect_code_language)`, embeds
  with BGE-M3, writes to the `code_embeddings` LanceDB table.

Driven by 2 Dagster assets in
`orchestration/defs/3_model_lifecycle/unified_embedding_assets.py`:
`unified_embeddings`, `code_embeddings` (group `embedding`).

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

### Targets (verified against v1.0.14 docs at https://cocoindex.io/docs/connectors/, 2026-06-29)

See the connector inventory at the top of this skill. KCG v1.0.x only wires **LanceDB / FalkorDB / Postgres**; the 7 NEW connectors since 1.0.7 (Qdrant, Turbopuffer, Valkey, SurrealDB, zvec, Iggy, OCI Object Storage, Doris) are not yet integrated. Track via `openspec/research/2026-06-28-upstream-package-monitoring/`.

#### NEW 1.0.11 — `declare_fts_index` for keyword search

```python
table.declare_fts_index(column="content", language="English", with_position=True)
```

> Per docs: "Indexes are reconciled as part of the table's target state: changing a declaration replaces the index in place, removing a declaration drops the index, and dropping the table removes all its indexes."

#### NEW 1.0.12 — `LanceType` typed column override

```python
from typing import Annotated
from cocoindex.connectors.lancedb import LanceType
import pyarrow as pa

@dataclass
class MyRow:
    id:    Annotated[int,   LanceType(pa.int32())]
    value: Annotated[float, LanceType(pa.float32())]
```

#### NEW 1.0.12 — explicit `TableSchema({…ColumnDef})` form

```python
schema = lancedb.TableSchema(
    {"doc_id":    lancedb.ColumnDef(type=pa.string(),  nullable=False),
     "embedding": lancedb.ColumnDef(type=pa.list_(pa.float32(), list_size=384))},
    primary_key=["doc_id"],
)
```

#### `declare_vector_index` defaults flipped to `ivf_pq`

The default is now IVF-PQ (was HNSW pre-1.0.7). To opt back in:

```python
table.declare_vector_index(
    column="embedding",
    metric="cosine",
    index_type="hnsw_pq",   # explicit
    m=16, ef_construction=200,
)
```

#### Lifecycle knobs on `declare_table_target`

| Parameter | Default | Purpose |
|:--|:--|:--|
| `managed_by` | `"system"` | `"system"` ⇒ CocoIndex manages table; `"user"` ⇒ assume it exists |
| `num_transactions_before_optimize` | `50` | Background `table.optimize()` cadence (1.0.7 #2008) |
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

- **App**: `cocoindex_flows/docs_skills_consolidation.py`
- **Dagster assets**: `orchestration/defs/4_asset_generation/docs_skills_assets.py`
  (groups `docs_skills` + `codebase`)
- **BAML schema**: `baml/docs_skills_consolidation.baml`
- **OpenSpec change**: `openspec/changes/docs-skills-consolidation-pipeline/`
- **Run catch-up**: `bun run docs:consolidate` (or `mise docs:consolidate`)
- **Run live**:    `bun run docs:consolidate:live`
- **Search**: `from cianfhoghlaim.cocoindex.docs_skills_consolidation import search_docs_skills; asyncio.run(search_docs_skills("<query>"))`

The companion codebase-indexing v1 App (replacement for the legacy
`ccc` CLI) lives at
`cocoindex_flows/codebase_indexing.py`; see the `ccc`
skill's deprecation banner.

**For comprehensive documentation:** <https://cocoindex.io/docs/>
**Search specific topics:** <https://cocoindex.io/docs/search?q=url%20encoded%20keyword>

## KCG ColPali cache location (project-specific)

The KCG CocoIndex flows that use `ColPaliEmbedImage` cache the
model weights at:

```
stedding/huggingface/hub/
  models--vidore--colpali-v1.3/
```

The canonical model is **`vidore/colpali-v1.3`** (1024-d
multi-vector, vision + text). For LlamaIndex aliasing via
LiteLLM, use the alias `vision` (set in
`agents/api/router.py`). The KCG marimo dashboard
`/dashboards/curriculum-images` shows a live demo of the
multimodal ColPali + Qdrant MaxSim search.
## 2026-06 update (CocoIndex v1.0.1–1.0.14)

The 7 post-v1 releases add the following production-readiness features:

### Per-argument memoization keys (`memo_key`)

The `@coco.fn` decorator now accepts a `memo_key` mapping for fine-grained control over which arguments participate in the cache key:

```python
@coco.fn(memo=True, memo_key={
    "entry": lambda e: (e.name, e.version),  # callable: transform before fingerprinting
    "client": None,                          # None: exclude from the cache key
})
def transform(entry: SourceDataEntry, client: str) -> str:
    ...
```

**Why it matters**: production functions often take clients, loggers, config objects, or debug flags alongside the meaningful input. Without `memo_key`, changing a client would invalidate the cache. With `memo_key`, the cache stays keyed to the semantic input.

### Scheduled live refresh (`coco.auto_refresh`)

Wraps any processor function as a live component that re-runs on an interval, with consistent error handling and target-state reconciliation:

```python
@coco.fn
async def app_main(db, target) -> None:
    await coco.mount(
        coco.auto_refresh(sync_users, interval=datetime.timedelta(minutes=5)),
        db, target,
    )
```

If `sync_users` stops declaring a row, CocoIndex deletes the corresponding target automatically.

### Per-slice stats (`coco.stats_group`)

Breaks the default aggregate `adds / reprocesses / deletes` counts down by data slice (per tenant, per project, per folder):

```python
@coco.fn
async def app_main(tenants, target):
    for tenant in tenants:
        with coco.stats_group(f"tenant:{tenant.id}", report_to_stdout=True):
            files = localfs.walk_dir(tenant.docs_dir, ...)
            await coco.mount_each(process_doc, files.items(), target)
```

Lets you see growth vs churn vs reprocess storms per slice, not just one aggregate per processor.

### New connectors (2026-06 cycle)

- **Source: OCI Object Storage** with live bucket watching (via OCI Streaming, Kafka protocol, 5s clock-skew tolerance)
- **Source: Apache Iggy** — high-throughput persistent message streaming
- **Target: Turbopuffer** — serverless object-storage-backed vector + full-text search
- **Target: Neo4j** — native property graph target
- **Target: FalkorDB** — Redis-based property graph (KCG uses this for the curriculum KG)
- **Target: LanceDB** — v1 target now optimises (compacts) tables periodically AND adds columns in place for schema evolution

### LiteLLM speech-to-text

The new `LiteLLMTranscriber` wraps any LiteLLM-backed STT provider (e.g. `whisper-1`), extending CocoIndex's multimodal reach from images/PDFs into audio. The KCG `asr/SKILL.md` covers the Celtic-Irish ASR pattern that uses this.

### Code splitter: 8 new languages

`RecursiveSplitter` gained tree-sitter support for Svelte, Vue, Julia, Elm, Astro, Bash, CMake, and HCL. The 29-language matrix (in `celtic-asset-generation/SKILL.md` and the codebase graph v1 App) now includes these.

### Bug fixes (correctness + security)

- Postgres: `halfvec` op classes for half-precision vector indexes; `U+0000` (NUL) bytes stripped from text/jsonb; `pgvector` extension installs into the default schema
- SQL identifier validation in Postgres + SQLite connectors (closes a class of SQL-injection vectors)
- Ownership-transfer race fix under real Postgres I/O latency
- Clean cancellation through task spawn boundaries

For the full changelog, see <https://cocoindex.io/blogs/changelog-101-107/>.

### 2026-06-25 update (CocoIndex v1.0.7 + the `upstream-package-monitoring` skill)

- **`cocoindex_v1_conformance` App** — the 14th v1 App in the KCG
  oideachais tree (`cocoindex_flows/infrastructure/cocoindex_v1_conformance.py`).
  It's a static AST linter that checks every other v1 App against
  the 4-rule conformance contract:
  - **R1** — `from ._lifespan import shared_lifespan` (delegates to
    the canonical shared lifespan).
  - **R2** — Either imports the canonical ContextKeys from `._lifespan`,
    OR declares additional ones with a sibling `# R2-exempt: <reason>`
    comment.
  - **R3** — `coco.App(...)` is at module scope (NOT inside a function
    body).
  - **R4** — At least one `@coco.fn(` decorator.
  Run via `mise run upstream:conformance`. See the
  `cianfhoghlaim-cocoindex-v1` skill for the full 14-App registry.
- **`upstream_api_surface` App** — the 15th v1 App
  (`cocoindex_flows/upstream_api_surface.py`). Watches
  the 5 canonical cocoindex docs URLs + `llms-full.txt` and BAML-extracts
  `ApiChange` records via `ExtractCocoIndexApiChange`. See
  `openspec/changes/upstream-package-monitoring/proposal.md`.
- **`upstream_blog_monitor` App** — the 16th v1 App
  (`cocoindex_flows/upstream_blog_monitor.py`).
  Reads Firecrawl-monitor payloads from
  `s3://cianfhoghlaim-upstream-webhooks/<package>/...`, BAML-extracts
  `BlogPostMetadata` via `ExtractBlogPostMetadata`, embeds chunks, and
  writes `BlogPostNode` + `PackageNode` + `PUBLISHED_BY` edges to the
  `upstream_packages_graph` FalkorDB graph.
- **FalkorDB connector** — used by both new Apps above. Connect via
  `falkordb.mount_table_target(KG_DB, "<NodeName>", ...)` where
  `KG_DB` is `coco.ContextKey[falkordb.ConnectionFactory]`.

### 2026-06-29 update (CocoIndex v1.0.7 → v1.0.14, verified live 2026-06-29)

- **v1.0.14 (25 Jun 2026, `4667e56`) — 19 PRs**: `feat(zvec): add FTS field support` (#2215); `feat(code_match): whole-node boundary \{ P \} ("is")` (#2196); `perf(engine): minimize serialization related to UserStateCache` (#2127); `fix(docs): update broken and redirected documentation links` (#2081).
- **v1.0.13 (22 Jun 2026) — 18 code-match PRs + Doris fix (#2189) + 17 example walkthroughs (#2185)**.
- **v1.0.12 (21 Jun 2026) — `Valkey` target (#2027); LanceDB `drop_index` + lancedb 0.33.0 / pyarrow 23.0.0 (#2132); CocoIndex inspection debug tool (#1920); 23 code-match PRs**.
- **v1.0.11 (17 Jun 2026) — `LanceDB` vector + FTS indexing (#2115); `zvec` target (#2092); OCI incrementality (#2116)**.
- **v1.0.10 (14 Jun 2026) — Agent experience (.md mirrors, llms.txt, skill endpoint, examples agent docs) (#2104) — drove the "Copy page as Markdown / Open in ChatGPT / Open in Claude / Install the CocoIndex v1 skill" buttons on every docs page**.
- **v1.0.9 (12 Jun 2026) — `coco.fn` directly callable outside a component context (#2101)**.
- **v1.0.8 (11 Jun 2026 — YANKED on PyPI per release history) — `coco.use_state()` persistent per-component state (#2034); `LiveMap` in-memory intermediate collection (#2088); Preview mode for update actions (#1945); Token-bucket `RateLimiter` (#2057); `LiteLLMTranscriber` STT (#2059); Tigris alongside MinIO (#2063). Do not install.**

## British-Isles Education pipeline — Canonical KCG pattern (post-v4)

The post-v4 lc6 pipeline (`openspec/changes/lc6-biep/`) defines
**7 v1 CocoIndex Apps** — one per LC subject plus the
`gov.ie` circulars ingester — sharing the canonical
`cocoindex_flows/_lifespan.py` (the `LANCE_DB` +
`EMBEDDER` + `RESOLVED_FILE_REGISTRY` triad per REFACTORING.md
item 12). The BIEP uses `BAAI/bge-m3` (1024-d, multilingual)
for the embedder so Gaeilge and English chunks share a single
vector space.

```python
import pathlib
from dataclasses import dataclass
from typing import Annotated
from numpy.typing import NDArray
import cocoindex as coco
from cocoindex.connectors import lancedb, localfs
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from cocoindex.ops.text import RecursiveSplitter
from cianfhoghlaim.cocoindex._lifespan import shared_lifespan, LANCE_DB, EMBEDDER

_splitter = RecursiveSplitter()


@dataclass
class MathChunk:
    chunk_id: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]


@coco.fn(memo=True)
async def process_mathematics_pdf(
    file: FileLike,
    table: lancedb.TableTarget,
) -> None:
    text = await file.read_text()
    chunks = _splitter.split(
        text, chunk_size=512, chunk_overlap=64, language="markdown"
    )
    for chunk in chunks:
        vec = await coco.use_context(EMBEDDER).embed(chunk.text)
        table.declare_row(
            row=MathChunk(chunk_id=chunk.id, text=chunk.text, embedding=vec)
        )


@coco.fn
async def app_main() -> None:
    table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name="cianfhoghlaim.lc.mathematics.higher_en",
        table_schema=await lancedb.TableSchema.from_class(
            MathChunk, primary_key=["chunk_id"]
        ),
    )
    table.declare_vector_index(column="embedding")
    files = localfs.walk_dir(
        pathlib.Path("leaving_certificate/mathematics/en/"),
        recursive=True,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/*.pdf"]),
    )
    await coco.mount_each(process_mathematics_pdf, files.items(), table)


mathematics_embedding = coco.App(
    coco.AppConfig(name="mathematics_embedding"),
    app_main,
)
```

The 7 BIEP v1 Apps follow this template — swap `MathChunk` for
`ChemChunk` / `GeogChunk` / `GaeilgeChunk` / `EnglishChunk` /
`CompSciChunk` / `GovCircularChunk`, swap the table name
(`cianfhoghlaim.lc.<subject>.<level>_<lang>` /
`cianfhoghlaim.education.ie.gov_circulars`), and update the source
directory. All 7 import `shared_lifespan` from
`cocoindex_flows/_lifespan.py` to satisfy the v1
conformance contract (`R1`–`R4` from
`cianfhoghlaim-cocoindex-v1/SKILL.md`).

**British-Isles Education pipeline use case:**

- **6 LC subjects × English / Gaeilge** — Mathematics, Chemistry,
  Geography, Gaeilge, English, Computer Science; each subject
  has 2 v1 Apps (one per language) → 12 subject Apps + 1
  `government_circulars` App = 13 BIEP v1 Apps (counting
  language partitions; 7 by subject).
- **`gov.ie` circulars** — the `government_circulars` v1 App
  walks `leaving_certificate/government_circulars/` (PDFs from
  `gov.ie/.../circulars/...`) and writes to
  `cianfhoghlaim.education.ie.gov_circulars_archive`.
- **`BAAI/bge-m3` 1024-d embedder** — shared via
  `_lifespan.py`; supports Gaeilge + English + 100+ languages
  in one vector space.
- **Dagster wiring** — each v1 App is driven by a Dagster asset
  in `orchestration/defs/3_model_lifecycle/`
  (group `lc6_embedding`).
- **Downstream RAG** — the 4 MotherDuck Dives
  (`lc_syllabus_topics`, `lc_exam_difficulty`,
  `lc_marking_complexity`, `gov_circulars_archive`) query the
  resulting LanceDB tables via `lance_scan()` from
  DuckDB/MotherDuck.

Cross-references:
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the DLT
  sources that produce the BAML rows the Apps embed
- [`.agents/skills/baml/SKILL.md`](../baml/SKILL.md) — the
  `ExtractCurriculumSyllabus` + 4 sibling functions
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the 4 Dives
- [`.agents/skills/lancedb/SKILL.md`](../lancedb/SKILL.md) —
  the `mount_table_target` canonical pattern
- [`.agents/skills/dagster/SKILL.md`](../dagster/SKILL.md) —
  the 42 lc5/lc6 assets

> Docs badge: every page renders `v 1.0.7` / `Last reviewed Jun 23, 2026` — frozen since 2026-06-23, even after 7 newer releases. The "Copy page as Markdown" / "Open in ChatGPT" / "Open in Claude" buttons are present on every URL fetched in this verification (install path: `npx skills install cocoindex_flows/cocoindex --skill <slug>`).
