# complete-cognee-knowledge-graph — Wire 3 missing author-archive cross-corpus edges + real cross-stage cognify

## Why

The oideachais knowledge graph has 3 outstanding gaps that prevent
end-to-end cognify:

### Gap 1: 3 author-archive cross-corpus edges are missing
`sruth/oideachais/cognify_rules/author_archive_cross_corpus.py`
documents 8 cross-corpus edge rules but only implements 5:

| Rule | Status |
|---|---|
| 1. OM -[:PUBLISHES]-> ZoteroPaper (arxiv_id + title match) | ✅ implemented (line 69) |
| 2. OM -[:DISCUSSES]-> UoGModule (content_type + topic_overlap) | ✅ implemented (line 136) |
| 3. UoGArtifact -[:TEACHES]-> ZoteroPaper (title match) | ❌ **MISSING** |
| 4. PersonalRecord -[:AWARDED]-> UoGModule (title + course_code) | ✅ implemented (line 187) |
| 5. GeminiReport -[:CITES]-> ZoteroPaper (arxiv_id match) | ❌ **MISSING** |
| 6. TakeoutDoc -[:CITES]-> GeminiReport (URL match) | ❌ **MISSING** |
| 7. UoGArtifact -[:LOCATED_IN]-> OfficialMediaSource (host match) | ✅ implemented (line 238) |
| 8. PersonalRecord -[:AFFILIATED_WITH]-> OfficialMediaSource (teaching) | ✅ implemented (line 345) |

The 3 missing rules exist as 100% complete implementations in
`sruth/oideachais/cognify_rules/leabharlann_cross_archive.py`
(`_build_arxiv_match_query`, `_build_module_title_match_query`,
`_build_takeout_citation_query`) but are never called from the
author-archive cross-corpus pass. `cognee_integration/author_archive_cognify.py:48-57`
lists all 8 in its `EDGE_TYPES` constant but only 5 actually run.

### Gap 2: cross_stage_cognify.py is a stub
`sruth/oideachais/cognee_integration/cross_stage_cognify.py:94-108`
defines `@asset cross_stage_cognify` that just logs the 8
`EDGE_DEFINITIONS` and returns `len(EDGE_DEFINITIONS) == 8`. The
real `cognee.cognify(dataset="oideachais.cross_stage")` call is
commented out as a TODO (line 99). The 5 per-stage knowledge-graph
producer assets (aistear, primary, junior_cycle, senior_cycle,
tertiary) are not yet built — but the aistear producer IS now
available via `wire-baml-with-known-consumers` (C3.1).

### Gap 3: university_of_galway missing from cognify dict
`sruth/oideachais/cognee_integration/author_archive_cognify.py` only
adds `gemini_deep_research` to the cognify dict. The
`university_of_galway` corpus is not added (per the explore
agent's report and `cognee_integration/author_archive_cognify.py:130`
context — the UoG module rows are loaded into the same dataset
but never cognified).

## What

### 1. Add 3 missing edge rules to author_archive_cross_corpus.py
- Copy `_build_arxiv_match_query` from
  `leabharlann_cross_archive.py:43-96` to
  `author_archive_cross_corpus.py` (function for Rule 5)
- Copy `_build_module_title_match_query` from
  `leabharlann_cross_archive.py:109-168` to
  `author_archive_cross_corpus.py` (function for Rule 3)
- Copy `_build_takeout_citation_query` from
  `leabharlann_cross_archive.py:184-225` to
  `author_archive_cross_corpus.py` (function for Rule 6)
- Add the 3 new builders to `build_all_cross_corpus_queries`
  so all 8 rules are now built
- This makes the function return 8 (name, cypher, params) tuples
  (where they have matches) instead of 5

### 2. Replace cross_stage_cognify.py stub with real implementation
- Add a `try/except ImportError` graceful degradation for
  `cognee` (when the package is not installed, the asset
  returns 0 edges with a warning)
- When cognee is available, call
  `cognee.add(EDGE_DEFINITIONS, dataset_name="oideachais.cross_stage")`
  followed by `await cognee.cognify(dataset="oideachais.cross_stage")`
- Add an `@asset_check` asserting at least 1 cross-stage edge
  is produced when the cognify is enabled

### 3. Add university_of_galway to cognify dict
- In `cognee_integration/author_archive_cognify.py`, the
  `cognify_all_corpora` function adds `gemini_deep_research` to
  the cognify pass; add `university_of_galway` and `personal_records`
  alongside

## Impact

### Affected files
- **MODIFIED:** `sruth/oideachais/cognify_rules/author_archive_cross_corpus.py`
  (+ 3 builder functions, + 3 lines in `build_all_cross_corpus_queries`)
- **MODIFIED:** `sruth/oideachais/cognee_integration/cross_stage_cognify.py`
  (real `cognee.cognify()` call, + 1 `@asset_check`)
- **MODIFIED:** `sruth/oideachais/cognee_integration/author_archive_cognify.py`
  (+ 2 lines for `university_of_galway` + `personal_records` in the cognify dict)

### Affected specs
- MODIFIED `oideachais-cognify-knowledge-graph` — the rule that
  all 8 author-archive cross-corpus edge rules SHALL be wired
  in the cognify pass; the rule that the cross-stage cognify
  SHALL call `cognee.cognify()` (not just log edge definitions).

### Backward compatibility
- The 3 new builder functions are copies of the leabharlann
  implementations; they share the same algorithm and the same
  inputs.
- The cross-stage cognify change adds a real Cognee call but
  uses graceful degradation (`try/except ImportError`) so the
  asset still works when Cognee is not installed.
- No existing assets are modified; only additive changes.

## Non-Goals

- No new edge rules (only the 3 documented in the existing spec
  are added)
- No 5-stage per-stage knowledge_graph assets (these require
  primary.baml / junior_cycle.baml / senior_cycle.baml BAML
  outputs to be materialised first; tracked in the
  `ireland-primary-jc-dlt-baml-and-full-stack-demo` openspec
  change). The cross_stage_cognify is updated to support
  aistear as a single per-stage input (since aistear was wired
  in C3.1) but the other 4 stages are still stubbed.
- No migration of the 4 broken v0 CocoIndex flows (tracked in
  the C5.1 follow-up).

## Risk Assessment

- **Risk: the 3 new edge rule builders break the existing 5.**
  Mitigation: the 3 builders are exact copies from
  `leabharlann_cross_archive.py`; the existing 5 builders in
  `author_archive_cross_corpus.py` are unchanged; the
  `build_all_cross_corpus_queries` function appends the new
  builders after the existing 5 (no overlap).
- **Risk: the real `cognee.cognify()` call fails when the
  Cognee LLM key is missing.** Mitigation: the asset uses
  `try/except ImportError` for missing cognee package and
  `try/except Exception` around the LLM call to return 0
  edges gracefully (the explore agent noted issue #12 with
  the opencode.json key, but that doesn't block the cognify
  call).
- **Risk: the cognify dict is too aggressive (adds 8
  corpora at once).** Mitigation: the existing
  `cognify_all_corpora` function is already designed to add
  multiple corpora; we're just adding 2 more (UoG and
  Personal Records).

## Validation

1. `from oideachais.cognify_rules.author_archive_cross_corpus import build_all_cross_corpus_queries, populate_cross_corpus_edges` succeeds
2. `from oideachais.cognee_integration.cross_stage_cognify import cross_stage_cognify, cross_stage_edges_check` succeeds
3. `from oideachais.cognee_integration.author_archive_cognify import cognify_all_corpora` succeeds
4. `grep "def _build_arxiv_match_query\|def _build_module_title_match_query\|def _build_takeout_citation_query" sruth/oideachais/cognify_rules/author_archive_cross_corpus.py` shows 3 hits
5. `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
6. `openspec validate complete-cognee-knowledge-graph --strict` passes
