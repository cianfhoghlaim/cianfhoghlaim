# oideachais-leabharlann Specification

## Purpose
TBD - created by archiving change 2026-07-15-oideachais-leabharlann-v1. Update Purpose after archive.
## Requirements
### Requirement: Phase 1 complete — 21 requirements all functional end-to-end

The `cianfhoghlaim-leabharlann` capability SHALL be considered Phase 1
complete when ALL of the following are simultaneously true (the
21 pre-existing requirements + the new Phase-1 wrap-up check):

1. All 4 DLT sources at `bianfhoghlaim/dlt/filesystem/`
   AST-parse and register their 6 expected resources each
   (books: `all_documents`, `pdf_documents`, `word_documents`,
   `epub_documents`, `book_chunks`, `previews`; Zotero +
   Takeout + UoG: per-source 6 resources).
2. The 1 Gemini deep research source at
   `bianfhoghlaim/dlt/filesystem/gemini_deep_research.py`
   AST-parses + the shared `_citation_extractor.py` exposes the
   `gemini_citations` column (PyMuPDF-based inline citation
   extraction).
3. All 3 v1 CocoIndex Apps
   (`LeabharlannBooksEmbedding` +
   `LeabharlannZoteroEmbedding` +
   `LeabharlannTakeoutEmbedding`) — plus the `LeabharlannFlow`
   App (the unified `leabharlann_chunks` table) and the
   `LeabharlannInboxEmbedding` App — declare
   `app = coco.App(...)` at module level with the v1
   conventions (`@coco.fn(memo=True)`, `ContextKey` via
   `@coco.lifespan`, `mount_table_target`,
   `mount_each`, `IdGenerator`, `localfs.walk_dir` +
   `PatternFilePathMatcher`, `Annotated[NDArray, EMBEDDER]`).
4. The shared `bianfhoghlaim/cocoindex/_lifespan.py`
   (REFACTORING.md item 12) provides the 3 canonical
   `ContextKey`s (`LANCE_DB`, `EMBEDDER`,
   `RESOLVED_FILE_REGISTRY`) + the `shared_lifespan` for all 5
   leabharlann apps.
5. The Dagster asset group registers 7 assets via 6
   `defs.yaml` components under
   `bianfhoghlaim/orchestration/defs/{1_ingestion/filesystem,3_model_lifecycle/cocoindex_v1}/leabharlann_*/`
   (plus 1 L2 BAML extraction asset =
   `2_materials/baml_extraction/leabharlann/defs.yaml`).
6. The full-stack demo asset at
   `bianfhoghlaim/notebooks/04_biep_motherduck/08_leabharlann_full_stack_demo.py`
   runs the 5-step pipeline on 2 sample PDFs (1 UoG + 1 Zotero)
   with 4 passing asset checks.
7. The directory-watch sensor (retired hand-rolled
   `leabharlann_sensors.py` replaced by the L1
   `CelticIngestionComponent` cron-driven
   `automation: on_dlt_freshness` in the 6 `defs.yaml` files)
   polls every 60 seconds and emits `RunRequest`s for the
   affected partitions.
8. All 4 cross-archive edge rules ship under
   `bianfhoghlaim/storage/cognify/rules/leabharlann_*.py`:
   - `leabharlann → BIEP` (the 2 edges in
     `leabharlann_cross_archive.py`).
   - `leabharlann → official-media` (in
     `leabharlann_official_media.py`).
   - `leabharlann → culture-heritage` (in
     `leabharlann_culture_heritage.py`).
   - `leabharlann → auth-archive` (the 4th edge per the cognify
     dispatch commit `fa9672233`, in
     `leabharlann_authors_archive.py`).
9. The `ExtractLeabharlannDoc` BAML function
   (in
   `bianfhoghlaim/baml/processing/leabharlann_extraction.baml`)
   registers with the `Default` BAML client (minimax-m3 on the
   coding plan API per commit `667635dfd`) and emits a
   `LeabharlannDoc` record.
10. All 6 sub-corpora (`aigne`, `gaeilge`,
    `gemini_deep_research`, `mata`, `ollscoil_na_gaillimhe`,
    `zotero`) are active in Plan 1 with a DLT source + BAML
    extraction + CocoIndex flow.
11. The leabharlann worktree at `leabharlann/` (repo root)
    retains a thin README pointer; the canonical 225-document
    corpus lives in
    https://github.com/cianfhoghlaim/leabharlann.

#### Scenario: Full-stack demo runs end-to-end on 2 sample PDFs

- **GIVEN** the 6 DLT sources + 5 v1 Apps + 1 full-stack demo +
  the 4 cross-archive edge rules are configured
- **WHEN** the `leabharlann_full_stack_demo` Dagster asset
  materialises on 2 sample PDFs (1 from
  `leabharlann/ollscoil_na_gaillimhe/irish/` + 1 from
  `leabharlann/zotero/`)
- **THEN** the pipeline produces 5 successful stages (sample
  selection → BAML extraction → CocoIndex v1 update → LanceDB
  write → Cognee ingestion)
- **AND** all 4 asset checks pass (extraction_OK, baml_OK,
  cocoindex_OK, full_pipeline_OK)
- **AND** `b.ExtractLeabharlannDoc` is invoked at least once
  per sample PDF
- **AND** the metadata is written to `leabharlann_demo_uog` +
  `leabharlann_demo_zotero` Cognee datasets

#### Scenario: All 4 cross-archive edge rules emit during cognify

- **GIVEN** the leabharlann corpus has been ingested + embedded
- **WHEN** the daily `cognify()` pass runs against the
  `oideachais` dataset
- **THEN** all 4 edge rules emit at least 1 `RunRequest`:
  - `leabharlann_cross_archive.populate_cross_archive_edges()`
    emits `GeminiReport-CITES-ZoteroPaper`,
    `UoGArtifact-TEACHES-ZoteroPaper`, and
    `TakeoutDoc-CITES-GeminiReport`
  - `leabharlann_culture_heritage.populate_culture_heritage_edges()`
    emits `leabharlann → culture-heritage`
  - `leabharlann_official_media.populate_official_media_edges()`
    emits `leabharlann → official-media`
  - `leabharlann_authors_archive.populate_authors_archive_edges()`
    emits `leabharlann → auth-archive`
- **AND** the FalkorDB `oideachais` graph contains all 4 edge
  types after the cron run

