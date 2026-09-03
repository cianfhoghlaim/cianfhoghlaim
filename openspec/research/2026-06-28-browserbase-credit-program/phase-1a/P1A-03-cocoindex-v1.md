# P1A-03 — CocoIndex v1 (Phase 1A, Data Plane)

**Date:** 2026-06-28
**Phase:** 1A (Data Plane Foundations)
**Budget:** ~180 credits
**Subagent:** data-platform

## TL;DR

CocoIndex v1 is the **code-first ETL framework** that powers every Cianfhoghlaim embedding pipeline — codebase_indexing, leabharlann_books_embedding, leabharlann_zotero_embedding, leabharlann_takeout_embedding, upstream_blog_monitor, upstream_api_surface, upstream_v1_conformance. The v1 App model (`coco.App` + `@coco.fn` + `ContextKey` + `mount_table_target`) replaced the v0 `CocoIndexFlow` pattern in 2026-Q1.

The **canonical Cianfhoghlaim v1 App pattern** is:

```python
class CodebaseIndex(coco.App):
    """v1 CocoIndex App for code search over the Cianfhoghlaim monorepo."""
    @coco.fn
    async def index_python_files(
        self,
        ctx: coco.Context,
        file_path: Annotated[str, coco.SourceKey],
        content: Annotated[str, coco.BlobReader],
    ) -> Annotated[NDArray, EMBEDDER]:
        # 1. Read file
        # 2. Chunk with semantic splitter
        # 3. Embed with BGE-M3
        # 4. Return embedding vector
        ...
```

Mounted to LanceDB via `mount_table_target("codebase_chunks", LanceDBTarget(...))`.

## Code (where CocoIndex v1 lives in Cianfhoghlaim)

| Path | Purpose |
|:--|:--|
| `cianfhoghlaim/core/cocoindex/codebase_indexing.py` | The `CodebaseIndex` v1 App (16 sub-skills) |
| `cianfhoghlaim/core/cocoindex/leabharlann_flow.py` | Leabharlann corpus (books + zotero + takeout) embeddings |
| `cianfhoghlaim/core/cocoindex/upstream_blog_monitor.py` | Monitors upstream package release notes (motherduck, dlthub, lancedb, cocoindex) |
| `cianfhoghlaim/core/cocoindex/upstream_api_surface.py` | Tracks upstream API surface changes |
| `cianfhoghlaim/core/cocoindex/upstream_v1_conformance.py` | CocoIndex v1 conformance checker (validates each App uses the v1 pattern) |
| `cognify/rules/cocoindex_v1_apps.py` | Lists the 14 v1 Apps that exist + their mount targets |
| `oideachais/dlt_sources/leabharlann/_cocoindex.py` | Bridge between dlt source and CocoIndex App |

**Canonical v1 App example** (`cianfhoghlaim/core/cocoindex/codebase_indexing.py`):

```python
import cocoindex
from cocoindex import Context, DataScope, App
from cocoindex.typing import Annotated, NDArray, EMBEDDER
from typing import Tuple

@cocoindex.App
class CodebaseIndex:
    """v1 CocoIndex App: index Cianfhoghlaim Python source files for semantic search."""
    
    @cocoindex.fn
    async def index_python_file(
        self,
        ctx: Context,
        file_path: Annotated[str, cocoindex.SourceKey],
        content: Annotated[str, cocoindex.BlobReader],
    ) -> Annotated[NDArray, EMBEDDER]:
        # Read file content (passed via BlobReader)
        chunks = semantic_chunk(content, max_tokens=512)
        embeddings = [embed(chunk) for chunk in chunks]
        return embeddings  # NDArray[embedding_dim]
    
    @cocoindex.flow_def
    def mount(self, flow_builder: DataScope):
        # 1. Source: filesystem glob
        flow_builder.source(
            cocoindex.sources.LocalFile(
                path=".",
                glob="**/*.py",
                include_patterns=["*.py"],
            ),
            ordinal_key="file_path",
        )
        # 2. Transform: extract chunks + embed
        chunked = flow_builder.transform(
            self.index_python_file,
            parameters={"file_path": "__source__", "content": "__source__"},
        )
        # 3. Mount: LanceDB HNSW table
        flow_builder.mount(
            chunked,
            cocoindex.targets.LanceDBTarget(
                table="codebase_chunks",
                uri="lance://lakehouse-lance:8182/codebase",
            ),
        )
```

## Env (deployed configuration)

| Env var | Value | Source |
|:--|:--|:--|
| `COCOINDEX_TARGET__MOUNT_TABLE__LANCE_URI` | `lance://lakehouse-lance:8182/codebase` | Locket |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` (1024-dim) | Default in code |
| `EMBEDDING_PROVIDER` | `litellm` (via LiteLLM gateway) | Locket |
| `LITELLM_BASE_URL` | `http://litellm:4000/v1` | docker-compose network |
| `LITELLM_MASTER_KEY` | `${LITELLM_MASTER_KEY}` | Locket |

The CocoIndex runtime is invoked via `cocoindex update <app_module>:<AppClass>` (e.g., `cocoindex update cianfhoghlaim.core.cocoindex.codebase_indexing:CodebaseIndex`).

## CCC anchors (where this code lives)

```
v1 App examples:           cianfhoghlaim/core/cocoindex/
CodebaseIndex:             cianfhoghlaim/core/cocoindex/codebase_indexing.py
Leabharlann embeddings:    cianfhoghlaim/core/cocoindex/leabharlann_flow.py
Upstream monitors:         cianfhoghlaim/core/cocoindex/upstream_*.py
v1 App registry:           cognify/rules/cocoindex_v1_apps.py
Dagster bridge:            cianfhoghlaim/dagster_defs/assets/ingestion/cocoindex_assets.py
Embedding spec:            cianfhoghlaim/core/cocoindex/_embedding_spec.py
Mount target helper:       cianfhoghlaim/core/cocoindex/_mount_targets.py
```

Use these CCC search terms:
```
"@cocoindex.App"            → 7 v1 Apps
"@cocoindex.fn"              → 14 functions across all Apps
"cocoindex.targets.LanceDBTarget" → 5 LanceDB mounts
"BAAI/bge-m3"                → embedding model constant
"mount_table_target"         → v1 mount API
"Annotated[NDArray, EMBEDDER]" → v1 typed-embedding pattern
```

## Drift log

| Date | Event | Action |
|:--|:--|:--|
| 2025-Q4 | v0 `CocoIndexFlow` pattern | Initial leabharlann embedding |
| 2026-Q1 | v1 `App` + `@coco.fn` + `ContextKey` + `mount_table_target` | All Apps migrated; legacy v0 Apps archived |
| 2026-03 | Switched from `BAAI/bge-small-en` to `BAAI/bge-m3` | Multilingual (needed for Irish/Scottish/Welsh) |
| 2026-04 | Added `upstream_v1_conformance.py` asset | Enforces v1 pattern across new Apps |
| 2026-06-04 | Archived `celtic-data-engineering-pipeline` change | 12 requirements, validated |
| 2026-06-28 | v4 consolidation: `sruth/oideachais/cocoindex_flows/` → `cianfhoghlaim/core/cocoindex/` | Pure rename (legacy v0 flow files removed) |

Current CocoIndex version pin:
```toml
[project.dependencies]
cocoindex = ">=1.0.0,<2.0.0"
cocoindex-cli = ">=1.0.0,<2.0.0"
```

## Anti-patterns (don't do this)

1. **Don't use the v0 `CocoIndexFlow` pattern** (e.g., `@cocoindex.flow_def`, `flow_builder.transform()` directly). Use the v1 `@coco.App` + `@coco.fn` + `ContextKey` pattern instead. The v0 patterns are deprecated and will be removed in CocoIndex 2.0.
2. **Don't hardcode embedding model names.** Use the `EMBEDDING_MODEL` constant from `cognify/embedding_registry.py` — it's the single source of truth for which model is currently active.
3. **Don't compute embeddings inside `@coco.fn` functions without batching.** CocoIndex batches automatically if you return `list[NDArray]` instead of `NDArray` for batch-friendly functions.
4. **Don't mount to filesystem directly.** Use `mount_table_target("name", LanceDBTarget(...))` so the table is queryable via the LanceDB REST namespace.
5. **Don't skip the `SourceKey` annotation.** Without it, CocoIndex can't deduplicate re-indexing runs.
6. **Don't use `BAAI/bge-small-en`** for Irish-language content — its 384-dim embeddings miss Irish semantic nuance. Use `BAAI/bge-m3` (1024-dim, multilingual).

## Decision matrix (Phase 1A-03 conclusion)

| Decision | Choice | Rationale |
|:--|:--|:--|
| App model | `coco.App` (v1) | Current standard; v0 deprecated |
| Embedding model | `BAAI/bge-m3` (1024-dim, multilingual) | Irish + Welsh + Scottish + Manx coverage |
| Mount target | LanceDB HNSW via `LanceDBTarget` | Lakehouse-native + supports both HNSW and FTS |
| Chunking | Semantic (512 tokens max, overlap 64) | Better than fixed-size for long PDFs |
| Provider | LiteLLM gateway | Single point of model rotation |
| v1 conformance | Enforced via `upstream_v1_conformance` asset | Prevents accidental v0 patterns |
| Re-indexing trigger | Dagster `@asset` (manual + monthly cron) | Idempotent + cost-controlled |
| Embedding dedup | `SourceKey` annotation | CocoIndex handles restarts gracefully |

## Anti-pattern priority for Phase 1A-04

When researching DuckDB + DuckLake next, look for:
- `ATTACH 'ducklake:postgres://...'` syntax (the DuckLake catalog attach)
- `COPY ... TO iceberg_catalog.metadata` (Iceberg table writes)
- The `pg_lakehouse` extension (PlanetScale Postgres + Lakehouse integration)
- Garage S3 endpoint config (`aws_endpoint_url=http://lakehouse-garage:3900`)

## Files to read next

- `cianfhoghlaim/core/cocoindex/codebase_indexing.py` (canonical v1 App example)
- `cianfhoghlaim/core/cocoindex/_embedding_spec.py` (single source of truth for embedding model)
- `cognify/rules/cocoindex_v1_apps.py` (registry of all 14 v1 Apps)
- `docs/skills/cocoindex/SKILL.md` — canonical CocoIndex skill
