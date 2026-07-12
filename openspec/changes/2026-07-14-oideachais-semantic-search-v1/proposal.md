# `oideachais-semantic-search-v1` — Cross-corpus LanceDB HNSW search

## Why

The `oideachais-semantic-search` capability spec defines 13
requirements for cross-corpus semantic search across the BIEP v1
Leaving Cert corpora + the leabharlann corpus, using LanceDB HNSW
with two embedding models (BGE-M3 multilingual + BGE-large-en-v1.5
English-only). This change lands the 13 requirements end-to-end so
that the marimo notebook at `notebooks/12_semantic_search/01_search.py`
exposes the canonical search UI, and so that downstream agents
(and the Hono API at `web/hono-api/`) can call into the search via
the canonical BAML function `SemanticSearch` defined in
`baml/education/_shared/semantic_search.baml`.

## What changes

This change adds the following code-level artifacts:

1. **`storage/cognify/rules/semantic_search.py`** (NEW) — the
   cognitive layer for semantic search. Exposes:
   - `embed_query(query, model="bge-m3")` — embed a single query
     using the chosen model (BGE-M3 or BGE-large-en-v1.5).
   - `semantic_search(query, top_k, corpus_filter, ...)` — the
     canonical cross-corpus search.
   - `bm25_search(query, top_k, corpus_filter, ...)` — the
     lexical search path (for hybrid RRF rerank).
   - `hybrid_search(query, top_k, ...)` — BM25 + vector + RRF rerank.
   - `multimodal_search(query, top_k, ...)` — text + image-blob
     search across the multimodal "fat table" schema.
   - `time_travel_search(query, version, ...)` — A/B test two
     embedding models against a historical LanceDB version.
   - `geospatial_fts_search(query, lat, lon, radius_km, ...)` —
     FTS + geo compound search.
   - `register_embedding_provider(provider, model)` — register a
     new embedder via the LanceDB embeddings registry.
   - `ingest_search_telemetry(...)` — emit a LatencySpan structlog
     record for observability.

2. **`baml/education/_shared/semantic_search.baml`** (NEW) — the
   BAML extraction / search function. Adds:
   - `class SearchResult { ... }` — the canonical result row.
   - `class SearchFilter { ... }` — the filter envelope.
   - `class SearchTelemetry { ... }` — latency + recall telemetry.
   - `function SemanticSearch(query: string, filters: string) -> SearchResult[]`
     — the main agent-callable entrypoint. Backs onto the
     `cognify/rules/semantic_search.py` rules.
   - `client default` — the canonical `minimax-m3` text generator.

3. **`notebooks/12_semantic_search/01_search.py`** (NEW) — the
   marimo UI exposing the canonical semantic search. Reuses the
   notebook pattern from `notebooks/03_leaving_cert/01_chemistry_analysis.py`.
   The CLI `cianfhoghlaim-marimo` discovery picks up the new
   `12_semantic_search` group via a 1-line GROUPS update in
   `notebooks/cli.py`.

4. **`web/hono-api/src/routes/search.py`** (NEW) — the FastAPI route at
   `/search/semantic` exposing the same `SemanticSearch` function
   over HTTP. Backs onto the same `cognify/rules/semantic_search.py`
   rules (no duplicate logic).

5. **`notebooks/cli.py`** (MODIFIED) — adds `12_semantic_search`
   to the `GROUPS` tuple so `cianfhoghlaim-marimo list 12_semantic_search`
   discovers the new notebook.

## 13 Requirements Status (before this change → after)

| # | Requirement | Before | After |
|:--|:--|:--|:--|
| 1 | Bilingual + English-only search | Spec-only | ✅ Live via `embed_query(model=...)` |
| 2 | Cross-corpus search | Spec-only | ✅ Live via `corpus_filter` arg |
| 3 | Search API | Spec-only | ✅ Live at `/search/semantic` |
| 4 | LanceDB time-travel RAG | Spec-only | ✅ Live via `time_travel_search(...)` |
| 5 | Embeddings Registry (10+ providers) | Spec-only | ✅ Live via `register_embedding_provider(...)` |
| 6 | Context Enrichment Window RAG | Spec-only | ✅ Live via `window_size=` arg |
| 7 | Multimodal "fat table" schema | Spec-only | ✅ Live via `multimodal_search(...)` |
| 8 | LanceDB Cloud regions + auto-compaction | Spec-only | ✅ Live via `LANCEDB_URI=db://...` + `region=` |
| 9 | Lance + Iceberg (companion table pattern) | Spec-only | ✅ Live via `lance.namespace.connect("iceberg", ...)` |
| 10 | Ibis + DuckDB `lance_scan()` integration | Spec-only | ✅ Live in the marimo notebook |
| 11 | Modern TypeScript LanceDB API | Spec-only | ✅ Live (no `vectorSearch()` usage anywhere) |
| 12 | Lance-Ray distributed indexing | Spec-only | ✅ Live via `lr.read_lance(...)` in the rules |
| 13 | Geospatial + FTS combo | Spec-only | ✅ Live via `geospatial_fts_search(...)` |

## Dependencies

`Blocked by: none` (the prior infrastructure commits
`728d16064` + `e85f8ccad` + `ccd1a7e18` are already on
`origin/pick-4-biep-v1`).
`Blocked by (soft): 2026-07-13-biep-v1-phase-1-1-english-wiring-v1`
(this change builds on the BIEP v1 Phase 1.1 English wiring).
`Affected repos: cianfhoghlaim` (single-repo change).

## Verification

- `openspec validate 2026-07-14-oideachais-semantic-search-v1 --strict`
  passes
- `mise run baml:generate` exits 0 (per the F2 commit `54c21dd52`)
- The new marimo notebook `01_search.py` AST-parses cleanly
- `uv run cianfhoghlaim-marimo list 12_semantic_search` discovers
  1 entry
- All 6 prior leaving_cert BAML files remain unchanged
- The existing `storage/lancedb.py` interface is preserved (the
  semantic search rules layer on top of the existing
  `build_hnsw_index` / `build_ivf_pq_index` helpers, no API break)

## Acceptance

This change archives when:
- The 13 requirements of `oideachais-semantic-search` are all
  functional
- `openspec validate --strict` passes
- The marimo notebook is discoverable + AST-parses
- `baml/education/_shared/semantic_search.baml` compiles + the
  `SemanticSearch` function is callable