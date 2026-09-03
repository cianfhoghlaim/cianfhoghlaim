# Change: oideachais-unified-embedding-v1

## Why

Phase 3 of the 6-phase refactor plan. Phases 1 (`oideachais-codebase-graph-v1`,
archived 2026-06-24) and 2 (`oideachais-storage-indexing-v1`, archived
2026-06-24) brought the *code* + *infrastructure* surfaces onto v1 CocoIndex.
Phase 3 brings the *embedding* surface onto v1.

The v0 file `sruth/crypteolas/cocoindex_flows/unified_embedding.py` used
the v0 DSL (`@cocoindex.flow_def`, `FlowBuilder`, `DataScope`,
`cocoindex.sources.DuckDB`, `cocoindex.targets.lancedb`,
`GeneratedField.UUID`, `VectorIndexDef`, `FtsIndexDef`,
`VectorSimilarityMetric.COSINE`, `QueryOutput`, `QueryInfo`). Per
the user's plan, this DSL is being phased out; the v1-native port
lives in `sruth/oideachais/` (per the user's decision that "v1 CocoIndex
Apps stay in `sruth/oideachais/`").

The v1 port follows the canonical v1 primitives used in
`sruth/oideachais/cocoindex_flows/codebase_indexing.py` and
`sruth/oideachais/cocoindex_flows/leabharlann_embedding.py`:

- `@coco.fn` + `@coco.fn(memo=True)` for processing functions
- `@coco.lifespan` providing shared `EMBEDDER` + `LANCE_DB` context keys
- `lancedb.mount_table_target(...)` for output
- `SentenceTransformerEmbedder("BAAI/bge-m3")` for the embedding
- 100-row upsert batches (HNSW-DROP-THRESHOLD respected)
- `asyncio.to_thread` for CPU/IO-bound work (DuckDB read, file walk)

The v1 port also **fixes a pre-existing bug** in 3 Dagster asset files
(`codebase_assets.py`, `infrastructure_assets.py`,
`unified_embedding_assets.py`): the `from __future__ import annotations`
import made `dagster.AssetExecutionContext` annotations become
strings, which dagster's `is_context_provided` check rejected
(`Cannot annotate \`context\` parameter with type AssetExecutionContext`).
The 3 files now omit `from __future__ import annotations` and import
cleanly under dagster 1.12.6.

The 2 v1 Apps and 2 Dagster assets complement the 4 v1 Apps in
`infrastructure_assets.py` (phase 2) and the 3 v1 Apps in
`codebase_assets.py` (phase 1). The `oideachais` lakehouse is now
the canonical embedding + code + infrastructure indexer for the
entire Cianfhoghlaim monorepo.

## What Changes

### 1. `sruth/oideachais/cocoindex_flows/unified_embedding.py` (NEW)

v1 port of `sruth/crypteolas/cocoindex_flows/unified_embedding.py`.
2 v1 CocoIndex Apps:

- `UnifiedEmbedding` (named `unified_app`) — reads from a
  configurable DuckDB connection (default:
  `crypteolas_catalog.docs.scraped_documents`), chunks with
  `RecursiveSplitter` (markdown) or paragraph+char fallback,
  embeds with BGE-M3, writes to the `unified_embeddings` LanceDB
  table.
- `CodeEmbedding` (named `code_app`) — walks `UNIFIED_CODE_ROOT`
  (default: `sruth/crypteolas/storage/data/code/`) for
  `*.py`/`*.ts`/`*.tsx`/`*.js`/`*.jsx`/`*.rs`/`*.go`/`*.sol`,
  chunks with `RecursiveSplitter(detect_code_language)`, embeds
  with BGE-M3, writes to the `code_embeddings` LanceDB table.

2 query helpers (v0 parity): `unified_search(query, source_types=None,
protocol=None, limit=10, similarity_threshold=0.0)` and
`code_search(query, language=None, chunk_type=None, limit=10)`.
1 batch utility (v0 parity): `batch_embed_texts(texts, model, batch_size=100)`.

### 2. `sruth/oideachais/dagster_defs/assets/unified_embedding_assets.py` (NEW)

2 Dagster assets (group `embedding`):

- `unified_embeddings` — kicks
  `oideachais.cocoindex_flows.unified_embedding:unified_app`
- `code_embeddings` — kicks
  `oideachais.cocoindex_flows.unified_embedding:code_app`

### 3. `sruth/oideachais/dagster_defs/assets/codebase_assets.py` (MODIFIED — bug fix)

Removes `from __future__ import annotations` so the
`AssetExecutionContext` type annotation is evaluated at runtime
(dagster 1.12.6 requires the actual class, not a string).

### 4. `sruth/oideachais/dagster_defs/assets/infrastructure_assets.py` (MODIFIED — bug fix)

Same as #3: removes `from __future__ import annotations`.

### 5. `sruth/oideachais/STATUS.md` (MODIFIED)

§3 (CocoIndex v0 vs v1) — add 1 new v1 row.
§4 (Dagster asset catalogue) — add a new `embedding` group row.

### 6. `.agents/skills/cocoindex/SKILL.md` + `.agents/skills/ccc/SKILL.md` (MODIFIED)

Reference the 2 new v1 embedding Apps + 2 new Dagster assets.

### 7. `openspec/specs/oideachais-pipeline/spec.md` (MODIFIED via 2 ADDED Requirements)

2 new ADDED Requirements:

- V1 unified embedding App (`unified_embeddings` asset)
- V1 code embedding App (`code_embeddings` asset)

## Impact

- Affected specs: `oideachais-pipeline` (2 ADDED Requirements)
- Affected code:
  - 1 new file in `sruth/oideachais/cocoindex_flows/`
  - 1 new file in `sruth/oideachais/dagster_defs/assets/`
  - 2 bug fixes in `sruth/oideachais/dagster_defs/assets/`
    (`codebase_assets.py`, `infrastructure_assets.py`)
- Affected skills: `cocoindex` (reference), `ccc` (reference)
- v0 fallback: `sruth/crypteolas/cocoindex_flows/unified_embedding.py`
  retained for 30 days, not deleted
- v1 App update command: `cocoindex update oideachais.cocoindex_flows.unified_embedding:unified_app`
  (and `code_app` for the second App)
- Dagster assets register via `sruth/oideachais/dagster_defs/definitions.py`
  import (`unified_embedding_assets = [...]`)

## Success criteria

- `oideachais.cocoindex_flows.unified_embedding` imports cleanly
- `unified_app` + `code_app` v1 Apps are constructed (no ImportError)
- `sruth/oideachais/dagster_defs/assets/unified_embedding_assets.py` imports
  cleanly under dagster 1.12.6 (no `Cannot annotate` error)
- `codebase_assets.py` + `infrastructure_assets.py` (the 2 bug-fixed
  files) also import cleanly
- `openspec validate oideachais-unified-embedding-v1 --strict` passes
- The 2 new Dagster assets show up in the unified `dg` UI
  alongside the 7 assets from phases 1 + 2
