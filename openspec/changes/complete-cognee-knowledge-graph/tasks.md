# Tasks: complete-cognee-knowledge-graph

## Phase 1: Copy 3 edge rule builders from leabharlann to author_archive_cross_corpus

- [ ] In `oideachais/cognify_rules/author_archive_cross_corpus.py`:
  - Append `_build_arxiv_match_query` (copied from `leabharlann_cross_archive.py:43-96`)
  - Append `_build_module_title_match_query` (copied from `leabharlann_cross_archive.py:109-168`)
  - Append `_build_takeout_citation_query` (copied from `leabharlann_cross_archive.py:184-225`)
- [ ] In `build_all_cross_corpus_queries`, append 3 more builder calls:
  - `_build_arxiv_match_query(gemini_citations_for_author_pass, zotero_papers)` → Rule 5
  - `_build_module_title_match_query(uog_modules, zotero_papers)` → Rule 3
  - `_build_takeout_citation_query(takeout_docs, gemini_reports)` → Rule 6
- [ ] Update `__all__` to include the 3 new functions

## Phase 2: Replace cross_stage_cognify stub with real implementation

- [ ] In `oideachais/cognee_integration/cross_stage_cognify.py`:
  - Add `try/except ImportError` for `cognee` (graceful when not installed)
  - Add `try/except Exception` around the cognify call (graceful when LLM key is missing)
  - When cognee is available, call `cognee.add(EDGE_DEFINITIONS, dataset_name="oideachais.cross_stage")` and `await cognee.cognify(dataset="oideachais.cross_stage")`
  - Add `@asset_check(cross_stage_cognify)` function `cross_stage_edges_check` that asserts at least 1 cross-stage edge

## Phase 3: Add university_of_galway + personal_records to cognify dict

- [ ] In `oideachais/cognee_integration/author_archive_cognify.py`:
  - In `cognify_all_corpora`, add 2 entries to the cognify dict:
    - `university_of_galway` (already loaded into the same dataset)
    - `personal_records` (if the corresponding dlt source is loaded)
- [ ] Add UoG and Personal Records to `DATASET_NAME` mapping in `EDGE_TYPES`

## Phase 4: Validation

- [ ] `grep "def _build_arxiv_match_query\|def _build_module_title_match_query\|def _build_takeout_citation_query" oideachais/cognify_rules/author_archive_cross_corpus.py` shows 3 hits
- [ ] `from oideachais.cognify_rules.author_archive_cross_corpus import build_all_cross_corpus_queries` succeeds
- [ ] `from oideachais.cognee_integration.cross_stage_cognify import cross_stage_cognify, cross_stage_edges_check` succeeds
- [ ] `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
- [ ] `openspec validate complete-cognee-knowledge-graph --strict` passes

## Phase 5: Land the plane

- [ ] Stage the changes
- [ ] Commit: `git commit -m "complete-cognee-knowledge-graph: wire 3 missing edges + real cross-stage cognify"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
