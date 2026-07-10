# Tasks — `2026-07-14-oideachais-semantic-search-v1`

## 1. Read spec + audit existing infrastructure (30 min)

- [x] Read `openspec/specs/oideachais-semantic-search/spec.md`
- [x] Audit `storage/lancedb.py` (canonical LanceDB module — already
      in place)
- [x] Audit `cocoindex/_lifespan.py` (canonical embedder BGE-M3 +
      BGE-large-en-v1.5 — already in place)
- [x] Audit `baml/education/lc_extraction/` (7 lc_extraction
      functions — DO NOT MODIFY; owned by BIEP v1 change)
- [x] Confirm `cognify/rules/semantic_search.py` is NEW (does not
      yet exist — to be created in step 2)
- [x] Confirm `notebooks/12_semantic_search/01_search.py` is NEW
      (does not yet exist — to be created in step 4)
- [x] Confirm `api/routes/search.py` is NEW (does not yet exist —
      to be created in step 7)

## 2. Verify the existing BGE-M3 + BGE-large-en-v1.5 embeddings (1 hr)

- [x] Confirm `storage/data/lancedb/` has the canonical instance
      (it has `codebase_chunks` — 576 rows, 8 columns including
      `embedding`)
- [x] Confirm `bge-m3` + `bge-large-en-v1.5` are referenced in
      `cocoindex/_lifespan.py:107`
- [x] Confirm the per-subject `_embedding.py` files exist for the 6
      LC subjects + leabharlann in `cocoindex/`
- [x] Note: the per-subject embeddings would only be populated when
      the dagster assets for the cocoindex flows run (they are
      orchestration-managed, not pre-populated in the source tree).
      The semantic search rules degrade gracefully when no
      per-subject data is available (returns an empty result list
      with `total=0`).

## 3. Create `storage/cognify/rules/semantic_search.py` (1.5 hr)

- [x] Add `embed_query(...)` — embed a single query (BGE-M3 or
      BGE-large-en-v1.5)
- [x] Add `semantic_search(...)` — the canonical cross-corpus search
- [x] Add `bm25_search(...)` — the lexical search path
- [x] Add `hybrid_search(...)` — BM25 + vector + RRF rerank
- [x] Add `multimodal_search(...)` — text + image-blob search
- [x] Add `time_travel_search(...)` — A/B test 2 embedders
- [x] Add `geospatial_fts_search(...)` — FTS + geo compound
- [x] Add `register_embedding_provider(...)` — register an embedder
- [x] Add `ingest_search_telemetry(...)` — emit a LatencySpan
      structlog record
- [x] Add `__all__` listing all public symbols

## 4. Create `baml/education/_shared/semantic_search.baml` (30 min)

- [x] Add `class SearchResult { ... }`
- [x] Add `class SearchFilter { ... }`
- [x] Add `class SearchTelemetry { ... }`
- [x] Add `function SemanticSearch(query: string, filters: string) -> SearchResult[]`
- [x] Wire to `client default` (the `minimax-m3` text generator)

## 5. Create `notebooks/12_semantic_search/01_search.py` (2 hr)

- [x] PEP 723 inline dependency block
- [x] `_imports` cell (marimo + lancedb + cognify)
- [x] `_search_controls` cell (text input + 4 multiselect filters)
- [x] `_page_state` cell (current page + page size)
- [x] `_embed_query` cell (call `embed_query` for the current model)
- [x] `_do_search` cell (call `semantic_search` for the top_k + filters)
- [x] `_results_panel` cell (render the results list + pagination)
- [x] `_detail_panel` cell (render the selected result in EN + GA)
- [x] `_main` cell (compose the 4 mo.vstack blocks)

## 6. Update `notebooks/cli.py` (5 min)

- [x] Add `"12_semantic_search"` to the `GROUPS` tuple

## 7. Create `api/routes/search.py` (30 min)

- [x] FastAPI route `/search/semantic` (GET) — calls into the
      canonical `semantic_search(...)` rules
- [x] Pydantic request + response models
- [x] Latency tracking via `ingest_search_telemetry(...)`

## 8. Verify (1 hr)

- [x] `openspec validate 2026-07-14-oideachais-semantic-search-v1 --strict`
      passes
- [x] The new marimo notebook AST-parses cleanly
- [x] `mise run baml:generate` exits 0 (per the F2 commit)
- [x] The 6 prior `baml/education/lc_extraction/*.baml` files are
      unchanged
- [x] `uv run cianfhoghlaim-marimo list 12_semantic_search` discovers
      1 entry
- [x] The 15 existing leaving_cert notebooks still AST-parse OK

## 9. Commit + push (5 min)

- [ ] `git add -A`
- [ ] `git commit -m "feat(search): ship oideachais-semantic-search (13 reqs)"`
- [ ] `git push --set-upstream origin pick-4-biep-v1`

## Total estimated effort

8-10 hours (per the task description).