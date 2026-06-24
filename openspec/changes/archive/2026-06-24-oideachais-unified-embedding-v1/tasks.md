# Tasks: oideachais-unified-embedding-v1

## 1. `oideachais/cocoindex_flows/unified_embedding.py`

- [x] Create the v1 port file (unified_embedding.py)
- [x] `UnifiedDocumentRow` + `CodeChunkRow` dataclasses with BGE-M3 embedding
- [x] `DocumentSourceType` enum (v0 parity)
- [x] `get_content_hash` + `classify_content` (v0 parity)
- [x] `_read_duckdb_rows` helper (asyncio.to_thread wrapper around duckdb-python)
- [x] `_chunk_markdown` helper (RecursiveSplitter + paragraph fallback)
- [x] `UnifiedEmbedding` v1 App (name `unified_app`)
- [x] `CodeEmbedding` v1 App (name `code_app`)
- [x] Shared `@coco.lifespan` providing EMBEDDER + LANCE_DB
- [x] `unified_search` async query helper
- [x] `code_search` async query helper
- [x] `batch_embed_texts` async utility (v0 parity)
- [x] 26 `__all__` exports
- [x] Functional test: imports cleanly, both Apps construct (COCOINDEX_AVAILABLE=True)

## 2. `oideachais/dagster_defs/assets/unified_embedding_assets.py`

- [x] Create the asset file
- [x] 2 @asset(group_name="embedding") declarations
- [x] `unified_embeddings` — kicks `oideachais.cocoindex_flows.unified_embedding:unified_app`
- [x] `code_embeddings` — kicks `oideachais.cocoindex_flows.unified_embedding:code_app`
- [x] 2 `_get_*_stats()` helpers (lancedb connect → row count + per-kind breakdown)
- [x] `unified_embedding_assets` export list

## 3. Bug fix: `from __future__ import annotations`

The Phase 1 + 2 asset files used `from __future__ import annotations`
which broke dagster's `is_context_provided` check
(`Cannot annotate \`context\` parameter with type AssetExecutionContext`).
The 3 new asset files (Phases 1, 2, 3) all omit the future import.

- [x] `oideachais/dagster_defs/assets/codebase_assets.py` — removed
- [x] `oideachais/dagster_defs/assets/infrastructure_assets.py` — removed
- [x] `oideachais/dagster_defs/assets/unified_embedding_assets.py` — never added

## 4. Verify imports

- [x] `oideachais.cocoindex_flows.unified_embedding` imports cleanly
- [x] `oideachais.dagster_defs.assets.codebase_assets` imports cleanly
- [x] `oideachais.dagster_defs.assets.infrastructure_assets` imports cleanly
- [x] `oideachais.dagster_defs.assets.unified_embedding_assets` imports cleanly
- [x] 9 new Dagster assets registered: 3 codebase + 4 infrastructure + 2 unified_embedding

## 5. `oideachais/STATUS.md`

- [x] §3 — add 1 new v1 row
- [x] §4 — add `embedding` group row

## 6. `.agents/skills/`

- [x] `.agents/skills/ccc/SKILL.md` — reference the 2 new Dagster assets
- [x] `.agents/skills/cocoindex/SKILL.md` — reference the 2 new v1 Apps

## 7. `openspec/`

- [x] Create `openspec/changes/oideachais-unified-embedding-v1/proposal.md`
- [x] Create `openspec/changes/oideachais-unified-embedding-v1/tasks.md`
- [x] Create `openspec/changes/oideachais-unified-embedding-v1/specs/oideachais-pipeline/spec.md`
  (2 ADDED Requirements)
- [x] `openspec validate oideachais-unified-embedding-v1 --strict`
- [x] `openspec archive oideachais-unified-embedding-v1 --yes`
- [x] Commit + push to `q3-2026-oideachais-consolidation`
