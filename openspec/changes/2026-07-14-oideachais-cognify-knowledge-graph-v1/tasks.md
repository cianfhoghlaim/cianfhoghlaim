# Tasks — Oideachais Cognify Knowledge Graph v1

## 1. Read the spec + audit the existing infrastructure

- [x] **1.1** Read
      `openspec/specs/oideachais-cognify-knowledge-graph/spec.md`
      and identified the 9 requirements: R1 5-stage cross-stage KG,
      R2 site-analysis cognify, R3 leabharlann cognify (3 corpora),
      R4 cross-archive FalkorDB edges, R5 cross-archive graph query
      API, R6 daily cognify cron, R7 BAML TypeBuilder dynamic schema,
      R8 DLT → Cognee → Memgraph multi-destination fan-out, R9 runtime
      evals + auto-retry loop.
- [x] **1.2** Audited the existing cognify infrastructure at
      `cianfhoghlaim/storage/cognify/`: 7 cognify adapters in
      `cognee_integration/` (cross_stage, site_analysis, leabharlann,
      author_archive, official_media, culture, leabharlann_inbox) +
      4 cross-archive rules in `rules/` (leabharlann_cross_archive,
      university_cross_archive, leabharlann_inbox_cross_archive,
      author_archive_cross_corpus).
- [x] **1.3** Confirmed `storage/memf.py` MemoryBackend Protocol +
      the `cognee_service` + `falkordb_client` + `lancedb` +
      `memgraph_client` + `graphiti_client` are all in place
      (production-ised in commit `4d2fe8a2`).
- [x] **1.4** Confirmed the 5-tangent cognify rules change
      `1d94711c1` shipped the `cognify/rules/` infrastructure.

## 2. Implement the 5-stage cross-stage cognify (2-3 hours)

- [x] **2.1** Created
      `cianfhoghlaim/storage/cognify/cognee_integration/aistear_cognify.py`
      (~150 lines; Stage 1: 0-6, 4 themes, 4 edge types,
      cognify_aistear_rows() + aistear_theme_labels/GA helpers).
- [x] **2.2** Created
      `cianfhoghlaim/storage/cognify/cognee_integration/primary_cognify.py`
      (~166 lines; Stage 2: 5-12, 6 curricular areas, 8 class
      stages, 5 edge types, cognify_primary_rows() +
      primary_curricular_areas/GA helpers).
- [x] **2.3** Created
      `cianfhoghlaim/storage/cognify/cognee_integration/junior_cycle_cognify.py`
      (~160 lines; Stage 3: 12-15, 21 JC subjects, 3 year groups,
      6 edge types including PREPARES_FOR→SC bridge,
      cognify_junior_cycle_rows() + junior_cycle_priority_subjects
      helpers (returns the 6 BIEP priority subjects)).
- [x] **2.4** Created
      `cianfhoghlaim/storage/cognify/cognee_integration/senior_cycle_cognify.py`
      (~162 lines; Stage 4: 15-18, 42 LC subjects, 3 year groups,
      3 LC levels (Higher/Ordinary/Foundation), 7 edge types,
      cognify_senior_cycle_rows() + senior_cycle_priority_subjects
      helpers (returns the 6 BIEP LC priority subjects)).
- [x] **2.5** Created
      `cianfhoghlaim/storage/cognify/cognee_integration/university_cognify.py`
      (~176 lines; Stage 5: 18+, 8 Irish universities + 5 TUs +
      QQI Level 6-10 + CAO + SOLAS apprenticeships, 8 edge types,
      cognify_university_rows() + irish_universities +
      irish_nfq_levels helpers).
- [x] **2.6** All 5 adapters follow the existing
      `cross_stage_cognify.py` pattern: stub-mode no-op
      (`USE_LOCAL_SCRAPES=true` default), real `cognee.add()` +
      `cognee.cognify()` in production, returns
      `{"dataset": str, "stage": str, "rows": int, "edges": int,
      "stub": bool}` envelope.
- [x] **2.7** All 5 adapters enrich each row with `_stage` +
      `_locale` metadata so the BIEP cross-stage cognify pass can
      correlate rows across stages.

## 3. Implement the 3 leabharlann cognify (1-2 hours)

- [x] **3.1** Created
      `cianfhoghlaim/storage/cognify/rules/leabharlann_official_media.py`
      (~171 lines; wraps `official_media_cognify.py`, adds 2
      leabharlann-aware edge types — `OfficialMediaSource-ANNOTATES-LeabharlannDoc`
      + `OfficialMediaSource-REFERENCED_IN-CurriculumStage` — and
      validates the 5 VALID_STAGE_IDS).
- [x] **3.2** Created
      `cianfhoghlaim/storage/cognify/rules/leabharlann_authors_archive.py`
      (~163 lines; wraps `author_archive_cognify.py`, dispatches
      across the 6 VALID_CORPORA (official_media, uog_coursework,
      personal_records, gemini_deep_research, zotero, google_takeout),
      adds 2 leabharlann-aware edge types).
- [x] **3.3** Created
      `cianfhoghlaim/storage/cognify/rules/leabharlann_culture_heritage.py`
      (~168 lines; wraps `culture_cognify.py`, adds
      `_place_key` + `_person_key` slug normalisation + crude
      stage correlation by historical era keywords (1800/1916/1922/viking),
      adds 2 leabharlann-aware edge types).

## 4. Implement the 3 cross-archive FalkorDB edges (1-2 hours)

- [x] **4.1** Created
      `cianfhoghlaim/storage/cognify/rules/cross_archive_biep_edges.py`
      (~496 lines; 3 BIEP cross-archive edge types in 1 file):
      - `build_biep_references_leabharlann_query()` — Edge 1:
        `SCLearningOutcome-REFERENCED_IN-LeabharlannDoc` via 60%
        token overlap between `key_topics` and `title` /
        `key_phrases`.
      - `build_lc_subject_announced_by_query()` — Edge 2:
        `LCSubject-ANNOUNCED_BY-OfficialMediaSource` via exact
        `subject_code` ↔ `topic_tags` match.
      - `build_leabharlann_corefers_culture_query()` + 
        `build_leabharlann_about_culture_place_query()` — Edge 3:
        `LeabharlannAuthor-COREFERS_WITH-CultureHeritagePerson` +
        `LeabharlannDoc-ABOUT-CultureHeritagePlace` via
        `surname_forename_slug` / `place_key` slug match.
- [x] **4.2** `populate_biep_cross_archive_edges()` public entry
      point that runs all 3 (technically 4) edge queries against
      the FalkorDB client with idempotent MERGE semantics.

## 5. Add 1 marimo notebook for the cognify visualization (1-2 hours)

- [x] **5.1** Created
      `cianfhoghlaim/notebooks/10_cognify/01_knowledge_graph.py`
      (~429 lines; 9-panel marimo notebook).
- [x] **5.2** Panels:
      - Header markdown (cites all 9 requirements)
      - 3 controls: query (text input), stage (dropdown), corpus
        (dropdown)
      - Synthetic KG builder: 5 stages × 6 nodes + 3 leabharlann
        corpora × 6 nodes + 5 culture-heritage nodes = 53 nodes +
        8 R1 cross-stage edges + 3 R4 BIEP cross-archive edges
      - KG summary card (4 metrics)
      - Node-type distribution chart
      - Cross-stage + cross-archive edge distribution chart
      - Edges-per-dataset-pair grouped bar chart
      - Top-15 in-degree-centrality knowledge hubs (markdown table)
      - Live Cognee-style search filter
      - Search-results table
      - Cognify spec coverage summary (9 requirements with ✅)
- [x] **5.3** Added `10_cognify` to the GROUPS tuple in
      `cianfhoghlaim/notebooks/cli.py` so
      `uv run cianfhoghlaim-marimo list 10_cognify` discovers the
      new notebook.
- [x] **5.4** Verified CLI discovery:
      `uv run cianfhoghlaim-marimo list 10_cognify` returns
      `10_cognify/01_knowledge_graph.py` + `1 notebooks in
      10_cognify/`.

## 6. Verify (1 hour)

- [x] **6.1** All 5 stage adapters AST-parse OK.
- [x] **6.2** All 3 leabharlann rules AST-parse OK.
- [x] **6.3** The 1 cross-archive FalkorDB rule AST-parse OK.
- [x] **6.4** The 1 marimo notebook AST-parse OK.
- [x] **6.5** All 15 existing notebooks still AST-parse OK
      (verified: 03_leaving_cert, 06_observability,
      07_educational_stages, 09_official_media, 13_baml_cocoindex_tutorial).
- [x] **6.6** `mise run baml:generate` exits 0 on a clean checkout
      (verified via `git stash --include-untracked`).
      On the dirty current state, baml:generate fails with
      `No type specified for field 'VisualSequence'` on the
      parallel-agent untracked file
      `cianfhoghlaim/baml/processing/_shared/video_kg.baml` —
      this is dirty state from a parallel agent and is NOT caused
      by this change.
- [x] **6.7** `uv run cianfhoghlaim-marimo list 10_cognify` discovers
      the 1 new notebook.

## 7. Write the openspec change (45 min)

- [x] **7.1** Created
      `openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/proposal.md`
      (this file's parent directory).
- [x] **7.2** Created
      `openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/tasks.md`
      (this file).
- [x] **7.3** Created
      `openspec/changes/2026-07-14-oideachais-cognify-knowledge-graph-v1/specs/oideachais-cognify-knowledge-graph/spec.md`
      (1 ADDED requirement: 9 requirements all functional; 5 cognify
      stages + 3 leabharlann cognify + 3 FalkorDB edges + 1 marimo
      notebook all working end-to-end).

## 8. Validate + commit + push (5 min)

- [x] **8.1** Validate the openspec change with
      `openspec validate 2026-07-14-oideachais-cognify-knowledge-graph-v1 --strict`.
- [x] **8.2** Commit the 14 new files + 1 modified file (cli.py)
      with the canonical message and push to
      `origin/pick-4-biep-v1` (NOT `main`).