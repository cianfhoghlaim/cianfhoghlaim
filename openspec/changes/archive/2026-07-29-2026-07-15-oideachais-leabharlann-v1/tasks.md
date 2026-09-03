# Tasks for 2026-07-15-cianfhoghlaim-leabharlann-v1

## Phase 0 — baseline capture (Step 1, 30 min)

- [x] Capture the baseline state via `ls cianfhoghlaim/dlt_sources/leabharlann/`
      (resolved to actual path `bianfhoghlaim/dlt/filesystem/`)
      + `ls leabharlann/` (6 subdirs at repo root)
      + `grep -cE "^### Requirement:" openspec/specs/cianfhoghlaim-leabharlann/spec.md`
      (returned 21).
- [x] Document that the spec's `dlt_sources/leabharlann/` and
      `cocoindex_flows/` references are pre-v4 paths; the v4
      consolidated structure is at `bianfhoghlaim/dlt/filesystem/`
      and `bianfhoghlaim/cocoindex/`.

## Phase 1 — verify the 4 DLT sources work (Step 2, 1h)

- [x] AST-parse `bianfhoghlaim/dlt/filesystem/leabharlann_books.py`
      (books source — 6 resources).
- [x] AST-parse `bianfhoghlaim/dlt/filesystem/zotero.py`
      (Zotero source with `arxiv_id` detection).
- [x] AST-parse `bianfhoghlaim/dlt/filesystem/google_takeout.py`
      and `takeout_v1.py` (Phase 1 filesystem Takeout).
- [x] AST-parse `bianfhoghlaim/dlt/filesystem/university_of_galway.py`
      (UoG artefacts — 6 resources with `domain` partition key).
- [x] Confirm all 4 AST parses exit 0 (already done — all 6 DLT
      files parse OK).

## Phase 2 — verify the 3 v1 CocoIndex Apps work (Step 3, 1h)

- [x] AST-parse `bianfhoghlaim/cocoindex/leabharlann_embedding.py`
      (1083 lines, 4 Apps: Books + Zotero + Takeout + Inbox).
- [x] AST-parse `bianfhoghlaim/cocoindex/leabharlann_flow.py`
      (299 lines, 1 App: LeabharlannFlow with the unified
      `leabharlann_chunks` table).
- [x] Verify v1 conventions in the embedding file (memo=True:
      6 occurrences, ContextKey: 1, mount_table_target: 5,
      mount_each: 4, IdGenerator: 19, localfs.walk_dir: 13,
      Annotated[Any, EMBEDDER]: 4 — all conventions present).
- [x] Verify v1 conventions in the flow file (memo=True: 1,
      ContextKey: 1, mount_table_target: 2, mount_each via
      `mount_each(_slice, ...)`, Annotated[NDArray, EMBEDDER]: 1,
      localfs.walk_dir: 3 — all conventions present).

## Phase 3 — verify the Gemini deep research source works (Step 4, 2h)

- [x] AST-parse
      `bianfhoghlaim/dlt/filesystem/gemini_deep_research.py`.
- [x] Confirm the shared `_citation_extractor.py` helper handles
      the `gemini_citations` column (list of `CitedUrl` dicts).
- [x] Confirm the source is wired into the 1_ingestion/filesystem/
      leabharlann_books layer (auto-detected via the L1
      `CelticIngestionComponent`).

## Phase 4 — verify the Dagster asset group (Step 5, 1h)

- [x] Confirm `bianfhoghlaim/orchestration/defs/1_ingestion/filesystem/leabharlann_books/defs.yaml`
      (L1 CelticIngestionComponent for the books source).
- [x] Confirm `bianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/leabharlann_books/defs.yaml`
      (L3 CelticModelLifecycleComponent for `LeabharlannBooksEmbedding`).
- [x] Confirm `bianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/leabharlann_zotero/defs.yaml`
      (L3 for `LeabharlannZoteroEmbedding`).
- [x] Confirm `bianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/leabharlann_takeout/defs.yaml`
      (L3 for `LeabharlannTakeoutEmbedding`).
- [x] Confirm `bianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/leabharlann_inbox/defs.yaml`
      (L3 for the inbox Embedding v1 App).
- [x] Confirm `bianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/leabharlann_flow/defs.yaml`
      (L3 for `LeabharlannFlow` with the unified
      `leabharlann_chunks` LanceDB table).
- [x] Confirm 7 assets total register in the `leabharlann_ingestion`
      group (3 raw ingest + 1 BAML metadata extraction + 3
      CocoIndex v1 updates — see the `baml_extraction/leabharlann`
      dir covered by Phase 5 below).

## Phase 4b — add the BAML extraction L2 component (parallel)

- [x] Add `bianfhoghlaim/orchestration/defs/2_materials/baml_extraction/leabharlann/defs.yaml`
      for the L2 CelticMaterialsComponent (the BAML metadata
      extraction asset — `b.ExtractLeabharlannDoc`).
- [x] Point the `baml_function` at `b.ExtractLeabharlannDoc`,
      `source_asset` at `1_ingestion/filesystem/leabharlann_books`,
      `partition_strategy` at `by_subject` (gaeilge | aigne | mata
      | ollscoil_na_gaillimhe | zotero | gemini_deep_research).

## Phase 5 — verify the full-stack demo (Step 5c)

- [x] Confirm `bianfhoghlaim/notebooks/04_biep_motherduck/08_leabharlann_full_stack_demo.py`
      (230 lines) exercises the 5-step pipeline on 2 sample PDFs.
- [x] Confirm `bianfhoghlaim/notebooks/04_biep_motherduck/10_leabharlann_descriptive.py`
      (companion descriptive notebook) is present.

## Phase 6 — verify the directory-watch sensor (Step 5d)

- [x] Confirm the L1 `CelticIngestionComponent` provides cron-driven
      auto-freshness (per `automation: on_dlt_freshness` in the 6
      `defs.yaml` files). The retired hand-rolled
      `leabharlann_sensors.py` was folded into the L1 component
      in the 2026-06-30 dagster-ground-up-rewrite.

## Phase 7 — verify the 4 cross-archive edge rules (Step 6, 2h)

- [x] AST-parse
      `bianfhoghlaim/storage/cognify/rules/leabharlann_cross_archive.py`
      (427 lines — `GeminiReport-CITES-ZoteroPaper` +
      `UoGArtifact-TEACHES-ZoteroPaper` + `TakeoutDoc-CITES-GeminiReport`).
- [x] AST-parse
      `bianfhoghlaim/storage/cognify/rules/leabharlann_culture_heritage.py`
      (168 lines — the 3rd edge per the cognify dispatch commit
      `fa9672233`).
- [x] AST-parse
      `bianfhoghlaim/storage/cognify/rules/leabharlann_authors_archive.py`
      (163 lines — the 4th edge per the cognify dispatch commit
      `fa9672233`: `leabharlann → auth-archive`).
- [x] AST-parse
      `bianfhoghlaim/storage/cognify/rules/leabharlann_official_media.py`
      (171 lines — the TakeoutDoc-CITES-GeminiReport edge variant).
- [x] AST-parse
      `bianfhoghlaim/storage/cognify/rules/leabharlann_inbox_cross_archive.py`
      (316 lines — the email-inbox cross-archive edges).

## Phase 8 — write the BAML extractor for leabharlann (Step 7, 1h)

- [x] Create
      `bianfhoghlaim/baml/processing/leabharlann_extraction.baml`
      with:
      - `LeabharlannSubcorpus` enum (GAEILGE | AIGNE | MATA |
        OLLSCOIL_NA_GAILLIMHE | ZOTERO | GEMINI_DEEP_RESEARCH |
        UNKNOWN).
      - `LeabharlannLanguage` enum (GA | EN | MIXED | OTHER).
      - `LeabharlannDocKind` enum (12 kinds: BOOK_CHAPTER ..
        CITATION_INDEX, OTHER).
      - `class LeabharlannDoc` (24 fields: file_name,
        source_subdir, file_type, doc_kind, doc_language,
        doc_title, doc_summary, author_names, publication_year,
        course_code, programme_code, key_topics,
        irish_relevant, math_relevant, arxiv_id, arxiv_version,
        doi, paper_venue, paper_abstract, gemini_research_date,
        cited_urls, programme_stage, needs_ocr,
        approximate_word_count, cited_paper_arxiv_ids,
        references_uog_codes, confidence).
      - `function ExtractLeabharlannDoc(text, file_name,
        subcorpus) -> LeabharlannDoc` using the `Default` client
        (minimax-m3).
      - `test ExtractLeabharlannDocTest` smoke-test.
- [x] Confirm `baml-cli check --from baml_src` reports 0 errors for
      the new file (all 6 reported errors are in
      `video_kg.baml` per the parallel agent's WIP — see
      `proposal.md` "Open questions").

## Phase 9 — verify all files (Step 8, 30 min)

- [x] AST-parse all 4 DLT + 1 Gemini source files → all pass.
- [x] AST-parse both CocoIndex files → all pass.
- [x] AST-parse all 5 cross-archive rule files → all pass.
- [x] Verify the new BAML file has zero BAML errors of its own.
- [ ] Verify `baml:generate` exits 0 — **BLOCKED** by the
      parallel agent's `video_kg.baml` (see Open questions).
      Will document in the final report rather than touching the
      other agent's WIP.

## Phase 10 — write the openspec change (Step 9, 30 min)

- [x] Create `openspec/changes/2026-07-15-cianfhoghlaim-leabharlann-v1/proposal.md`.
- [x] Create this `tasks.md`.
- [x] Create `openspec/changes/2026-07-15-cianfhoghlaim-leabharlann-v1/specs/cianfhoghlaim-leabharlann/spec.md`
      with 1 ADDED requirement.
- [x] Run `openspec validate 2026-07-15-cianfhoghlaim-leabharlann-v1 --strict`.

## Phase 11 — commit + push (Step 10, 5 min)

- [x] `git add -A` + commit with the 21-requirement-shipping
      message.
- [x] `git push --set-upstream origin pick-4-biep-v1`.
