# Oideachais — Refactoring Backlog

**Last updated:** 2026-06-16

This file is the canonical refactor backlog for the `oideachais/` data platform. Each item has a `Status` field (`done` | `in_progress` | `backlog` | `superseded`) and links to a tracking openspec change (where applicable).

> **Workflow**: pick an item from `backlog`, open an openspec change, change the status to `in_progress` in the same commit as the first code change, then to `done` in the commit that closes the change.

---

## Top of the backlog (priority order)

### 1. Primary + Junior Cycle British Isles dlt + BAML loop

**Status**: `backlog`
**Tracks**: queued openspec change `primary-secondary-british-isles-dlt-baml` (to be opened)
**Effort**: ~2 weeks
**Why**: `baml_src/primary.baml` and `baml_src/junior_cycle.baml` define 4 BAML functions (`ExtractPrimaryFramework`, `ExtractPrimaryLearningOutcomes`, `ExtractJCSpec`, `ExtractCBADescriptor`) but **no matching dlt source backs them in `oideachais/dlt_sources/ireland/`** (only `aistear.py` and `senior_cycle.py` exist). The BAML extraction is unreachable. UK nations primary/secondary sources are also missing.

**What it lands**:
- `oideachais/dlt_sources/ireland/primary.py` + `junior_cycle.py` (4 new dlt sources, 6 resources each).
- `oideachais/dlt_sources/uk/{england,scotland,wales,northern_ireland}/primary.py` + `secondary.py` (8 new dlt sources for Key Stage 1-2 / 3-4 / CfE Early-First-Second Level / KS3-4).
- 12 new Dagster assets under `oideachais/dagster_defs/assets/curriculum_cycle_assets.py` (12 nation × cycle partitions).
- 4 BAML extraction functions now invoked from the dlt `extraction_metadata` resource.
- Crown Dependencies primary/secondary coverage (`ggy`, `jey`, `iom`).

**Stack usage**: full Lakehouse + BAML + CocoIndex v1 + Cognee pipeline becomes a *reusable pattern*.

---

### 2. Cognee + FalkorDB cross-archive knowledge graph for the leabharlann + primary/secondary archives

**Status**: `backlog`
**Tracks**: queued openspec change `cognee-falkordb-leabharlann` (to be opened)
**Effort**: ~1 week
**Why**: Today `oideachais/cognee_integration/cross_stage_cognify.py` builds an 8-edge graph for the 5 educational stages (Aistear → Primary → JC → SC → Tertiary), but it's not connected to a real graph store. The leabharlann pipelines (Zotero papers, Gemini reports, UoG artefacts) all have rich BAML-extracted metadata but their relationships are not modelled. The `oideachais/graph/falkordb_client.py` exists but no Dagster asset populates it.

**What it lands**:
- 3 new Dagster cognify assets: `cognee_cognify_books`, `cognee_cognify_zotero`, `cognee_cognify_takeout`. Each runs after the corresponding `leabharlann_cocoindex_*_update` asset materialises.
- 1 cross-archive edges asset: `cognee_cross_archive_edges` (e.g. `GeminiDeepResearchReport -[:CITES]-> ZoteroPaper` when an arxiv_id matches).
- 1 FastAPI route `GET /cross-archive-graph/{query}` that runs a FalkorDB query and returns a JSON node+edge payload.
- 1 daily cron sensor (Cognee is expensive; don't run on every Lakehouse write).
- The FalkorDB compose stack stays at `falkordb.cianfhoghlaim.ie:6379` (already running). `oideachais/config/base.py:falkordb_host` is already plumbed in.

**Stack usage**: Cognee cognify → FalkorDB (graph) + LanceDB (vectors) + DuckLake (tables). All three backends populated from the same BAML-extracted source rows.

---

### 3. LanceDB blob storage via the `lancedb` compose stack + RCLONE FUSE mount

**Status**: `backlog`
**Tracks**: queued openspec change `lancedb-blob-storage-leabharlann` (to be opened)
**Effort**: ~1 week
**Why**: The `infrastructure/stacks/lancedb/compose.yaml:44-75` already has an `rclone` FUSE mount profile for S3-backed LanceDB blob storage. Nothing in `oideachais/` uses it. The 117 Zotero PDFs and 64 Takeout docx files are not stored in blob form anywhere.

**What it lands**:
- New compose file `infrastructure/stacks/lancedb/compose.leabharlann.yaml` that extends the base `lancedb` stack with the `s3` profile enabled, mounting the RCLONE volume to `/data/s3` and pointing the LanceDB viewer at the local mount.
- New Komodo procedure `infrastructure/komodo/procedures/leabharlann-lancedb-blob-deploy.toml` that deploys the lakehouse + `lancedb-leabharlann` stack + Dagster `oideachais_cocoindex_leabharlann_blob_update` asset.
- `oideachais/dlt_utils/destinations.py:118` updated to support `LANCE_DB_URI_BLOB` (pointing at the local FUSE mount) alongside the existing `LANCE_DB_URI_REST`.
- A new Dagster asset `oideachais_cocoindex_leabharlann_blob_update` that uses `LANCEDB_URI=/data/s3/leabharlann.ldb` instead of the REST API.
- All 117 zotero + 64 takeout + 40 gaeilge/aigne books indexed in the blob store.

**Stack usage**: Lakehouse (Garage S3 + Lakekeeper Iceberg) → RCLONE FUSE → LanceDB blob store on disk. Demonstrates the full Lakehouse stack end-to-end with the blob storage pattern that the `lancedb` compose stack was designed for.

---

### 4. Leabharlann full-document processing pipeline (sample PDFs → BAML → Cognee → FalkorDB → LanceDB blob → Dagster UI)

**Status**: `backlog`
**Tracks**: queued openspec change `leabharlann-full-stack-demo` (to be opened)
**Effort**: ~1 week
**Why**: The user explicitly asked to "process sample pdfs from the leabharlann/ollscoil_na_gaillimhe and zotero prcoess pdf documents fully indexing and analysed and further analysable iwhtin our full stack oideachais project". Today the leabharlann dlt sources discover and yield the PDFs but no asset actually processes them end-to-end through the full stack.

**What it lands**:
- A new `oideachais_cocoindex_leabharlann_full_stack_demo` asset that takes 2 sample PDFs:
  - 1 from `leabharlann/ollscoil_na_gaillimhe/irish/gaeilge.pdf` (Irish language exam)
  - 1 from `leabharlann/zotero/Handwritten Text Recognition (HTR) for Irish-Langu.pdf` (relevant Zotero paper)
- The asset:
  1. Extracts text via pymupdf
  2. Calls `b.ExtractUoGArtifact` and `b.ExtractZoteroMetadata` respectively
  3. Embeds the chunks via the `leabharlann_books_app` / `leabharlann_zotero_app` v1 CocoIndex Apps
  4. Stores the embedded chunks in the LanceDB blob store (Feature 3)
  5. Adds the structured rows to Cognee via `cognee.add()` + `cognify()` (Feature 2)
  6. Writes the result metadata to a DuckDB table `leabharlann_full_stack_demo`
- A new Dagster asset check that asserts: `pdf_extraction_status=ok`, `baml_extraction_status=ok`, `cocoindex_chunks_count > 10`, `cognee_episode_count > 1`, `lance_table_size_bytes > 1000`.
- A new Marimo notebook `oideachais/notebooks/leabharlann_full_stack_demo.py` that renders the 5-step pipeline as an interactive UI.

**Stack usage**: The full Lakehouse + Infisical + Locket + BAML + CocoIndex + Cognee + FalkorDB + LanceDB pipeline, exercised end-to-end on 2 sample PDFs. Becomes the canonical "how does this work" demo for the whole project.

---

### 5. Comprehensive `oideachais/STATUS.md` + per-area READMEs that demystify the stack

**Status**: `in_progress` (this change)
**Tracks**: `openspec/changes/data-engineering-documentation-and-refactor-roadmap/`
**Effort**: ~1 week
**Why**: The user explicitly asked to "extensively document these pipelines and the existing pipelines in oideachais focusing on british isles education and the features/benefits of our lackehouse+infisical+locket docker compose stack". Documentation is the high-leverage output that ties everything else together.

**What it lands** (Phase 1 of this change):
- `oideachais/STATUS.md` (single source of truth) ✅
- `oideachais/REFACTORING.md` (this file) ✅
- `oideachais/dlt_sources/uk/README.md` (per-nation × per-cycle coverage matrix) ✅
- `oideachais/dlt_sources/ireland/README.md` (Ireland coverage matrix) ✅
- `oideachais/cocoindex_flows/README.md` (v0/v1 status per flow) ✅
- `oideachais/dagster_defs/assets/README.md` (asset catalogue) ✅
- `baml_src/README.md` (BAML schema catalogue) ✅
- `oideachais/agents/{adk,agno}/README.md` (agent surface) ✅
- `docs/06-infrastructure/leabharlann-stack-overview.md` (end-to-end stack diagram) ✅

---

## Refactoring + redundancy findings (smaller items, backlog)

| # | Item | Status | Notes |
|:--|:--|:--|:--|
| 6 | 10 v0 CocoIndex flows in `oideachais/cocoindex_flows/` not migrated to v1 (only `leabharlann_embedding.py` is v1) | `backlog` | The package `__init__.py` paper-overs the broken imports. Should be migrated one at a time using the `leabharlann_embedding.py` pattern. |
| 7 | `oideachais/graph/temporal.py` reimplements Graphiti in pure Python without ever connecting to the Graphiti compose stack | `backlog` | Decision: (a) delete, (b) re-implement as a thin Python client for the Graphiti compose stack, (c) leave alone. |
| 8 | 2 parallel graph stacks (`oideachais/cognee_integration/` + `oideachais/graph/{memgraph_client,falkordb_client,temporal}.py`) | `backlog` | Unify: Cognee is primary, FalkorDB for cache/queries, Memgraph for the bi-temporal knowledge graph (Cognee uses Memgraph). |
| 9 | 3 document extraction utilities re-implement pymupdf + python-docx: `oideachais/dlt_sources/author_archive/_scanner._extract_text_from_{pdf,word,code}` + `oideachais/document_factory/pdf_converter.py` + `oideachais/cocoindex_flows/pdf_embedding.py:PDFEmbeddingPipeline` | `backlog` | Consolidate into `oideachais/document_extraction/`. |
| 10 | BAML `ExtractHandwrittenEquations` is called only in `oideachais/ocr/author_archive_ocr.py:1`, not wired to any Dagster asset | `backlog` | Wire to `leabharlann_handwriting_ocr` asset (currently just a config check, no real OCR). |
| 11 | BAML `ExtractZoteroMetadata` is defined in `baml_src/author_archive.baml` but never called from any dlt source | `backlog` | Wire to `leabharlann_zotero_raw.extraction_metadata` resource. |
| 12 | 3 leabharlann CocoIndex Apps re-declare the same `@coco.lifespan` 3 times | `backlog` | Consolidate to one module-level `@coco.lifespan`. |
| 13 | The `baml_src/tertiary.baml` schemas are defined but `oideachais/dlt_sources/ireland/tertiary.py` does not call any BAML function | `backlog` | Wire to tertiary extraction. |
| 14 | The `baml_src/curriculum_extraction.baml` 3 functions are referenced by 70+ @dlt_assets but no asset check verifies the BAML output structure | `backlog` | Add asset checks for BAML extraction quality. |
| 15 | `oideachais/cocoindex_flows/transforms/` has 3 transformation helpers (`caighdean_standardize`, `terminology_linking`) but they're not wired into any CocoIndex flow | `backlog` | Add to the v1 `leabharlann_embedding` flow. |
| 16 | `oideachais/dagster_defs/assets/leabharlann_assets.py:cocoindex_books_update` calls `subprocess.run(["cocoindex", "update", ...])` but `cocoindex` may not be on the worker PATH | `in_progress` | Add a try/except + structured error in the asset materialisation. |
| 17 | `oideachais/dagster_defs/assets/author_archive_assets.py` declares 7 assets but `cocoindex update` is never actually invoked (assets are stubs) | `backlog` | Wire to the v1 `author_archive_embedding.py` flow (after the v0 → v1 migration). |
| 18 | `oideachais/cognee_integration/cross_stage_cognify.py` declares `cross_stage_cognify` as a Dagster asset but it is a stub — no actual Cognee cognify call is made | `backlog` | Wire to the real Cognee cognify lifecycle. |
| 19 | `oideachais/dlt_sources/author_archive/google_takeout.py` has `phase2_oauth_drive_export` and `phase2_gmail_export` stubs that raise `NotImplementedError` | `backlog` | Phase 2 of the takeout source. |
| 20 | The 3 `leabharlann_cocoindex_*_update` assets use `subprocess.run` to invoke the v1 Apps. If `cocoindex` is not on PATH (likely on the production MacBook which doesn't have cocoindex installed), the asset materialisation fails | `in_progress` | Add a `try/except FileNotFoundError` and skip the update with a warning, allowing the rest of the pipeline to continue. |
| 21 | The 6 `oideachais/dlt_sources/author_archive/` sources are NOT registered in the `oideachais/dlt_sources/__init__.py` (only the author-archive package itself is) | `done` | Already done — they are re-exported via `oideachais.dlt_sources.author_archive`. |

---

## Recent / done

| # | Item | Status | Closed in |
|:--|:--|:--|:--|
| 1 | `oideachais/STATUS.md` written (single source of truth) | `done` | this change |
| 2 | `oideachais/REFACTORING.md` written (refactor backlog) | `done` | this change |
| 3 | `oideachais/dlt_sources/uk/README.md` written (per-nation × per-cycle coverage) | `done` | this change |
| 4 | `oideachais/dlt_sources/ireland/README.md` written | `done` | this change |
| 5 | `oideachais/cocoindex_flows/README.md` rewritten (v0/v1 status per flow) | `done` | this change |
| 6 | `oideachais/dagster_defs/assets/README.md` written (asset catalogue) | `done` | this change |
| 7 | `baml_src/README.md` written (BAML schema catalogue) | `done` | this change |
| 8 | `oideachais/agents/{adk,agno}/README.md` written (agent surface) | `done` | this change |
| 9 | `docs/06-infrastructure/leabharlann-stack-overview.md` written (end-to-end stack diagram) | `done` | this change |
| 10 | `oideachais/dlt_sources/author_archive/` package created (6 dlt sources for leabharlann + author archive) | `done` | `openspec/changes/leabharlann-cocoindex-v1` (commit `676db8664`) |
| 11 | `oideachais/cocoindex_flows/leabharlann_embedding.py` written (3 v1 Apps + 3 search handlers) | `done` | `openspec/changes/leabharlann-cocoindex-v1` |
| 12 | `baml_src/author_archive.baml` extended with `ZoteroPaper` + `Author` + `PaperKind` enum + `ExtractZoteroMetadata` | `done` | `openspec/changes/leabharlann-cocoindex-v1` |
| 13 | `oideachais/dagster_defs/assets/leabharlann_assets.py` written (7 assets) | `done` | `openspec/changes/leabharlann-cocoindex-v1` |
| 14 | `oideachais/dagster_defs/sensors/leabharlann_sensors.py` written (60 s directory-watch sensor) | `done` | `openspec/changes/leabharlann-cocoindex-v1` |
| 15 | `oideachais/ocr/author_archive_ocr.py` written (Pylaia / TrOCR / PaddleOCR / VLM dispatch) | `done` | `openspec/changes/author-archive-gemini-and-uos-ingestion` |
| 16 | `oideachais/dlt_sources/author_archive/_epub_extractor.py` written (ebooklib-based, graceful degradation) | `done` | `openspec/changes/leabharlann-cocoindex-v1` |
| 17 | `oideachais/dlt_sources/author_archive/_citation_extractor.py` written (PyMuPDF link extraction) | `done` | `openspec/changes/author-archive-gemini-and-uos-ingestion` |
| 18 | `oideachais/dagster_defs/assets/author_archive_assets.py` written (7 author-archive assets) | `done` | `openspec/changes/author-archive-gemini-and-uos-ingestion` |

---

## Cross-references

- `oideachais/STATUS.md` — single source of truth for pipeline state.
- `openspec/changes/data-engineering-documentation-and-refactor-roadmap/` — the openspec change that contains this backlog.
- `docs/02-data-platform/DATA_ARCHITECTURE.md` — data architecture (Tripartite data landscape, BAML schema specs, Cognee ontology).
- `docs/06-infrastructure/leabharlann-stack-overview.md` — end-to-end stack diagram.


## Archive of orphan BAML functions

**Status**: `done` (Q3-2026)
**Tracks**: `openspec/changes/archive-celtic-baml-orphans/`
**Effort**: 1 day

29 BAML functions in 6 files have no current Python consumer in the oideachais quadrant. They are intended for the `meaisinfhoghlaim/` Celtic-linguistic agents and the `croilar/` portfolio surface, which are not yet built.

The 6 files are now in `oideachais/baml_src/_archive/` with ARCHIVED headers:

- `cognates.baml` (5 functions: IdentifyCognates, CompareCelticVocabulary, IdentifyFalseFriends, ExplainSoundChanges, GenerateCognateVocabulary)
- `celtic_linguistics.baml` (3 functions: ExtractMorphology, AnalyzeSentence, IdentifyDialect)
- `morphology.baml` (4 functions: ExtractVerbConjugation, ExtractNounDeclension, IdentifyMorphologicalClass, CompareAdjective)
- `grammar_patterns.baml` (6 functions: ExtractGrammarPatterns, ExtractIrishCopula, AnalyzeVSOOrder, ExtractPossession, GeneratePrepositionalPronouns, DocumentMutationTriggers)
- `named_entities.baml` (5 functions: ExtractCelticEntities, ExtractPersonEntities, ExtractPlaceEntities, ExtractSupernaturalEntities, ExtractFestivalEntities)
- `portfolio_extraction.baml` (6 functions: ExtractProfileFromCV, ExtractProfileFromGitHubReadme, ExtractMusicProfile, ExtractGameProject, MergeProfiles, GenerateProfileSummary)

**Re-activation procedure** (full steps in `oideachais/baml_src/_archive/README.md`):

1. Build the consumer (e.g. `meaisinfhoghlaim/agents/celtic_linguistics.py`)
2. `git mv oideachais/baml_src/_archive/<name>.baml oideachais/baml_src/<name>.baml`
3. Remove the ARCHIVED header from the top
4. Update `oideachais/STATUS.md` to mark the functions as wired
5. Remove this entry from `oideachais/REFACTORING.md`

**What is NOT in this archive**: the 5 `oideachas.baml` functions (`ExtractSyllabus`, `ExtractExamPaper`, `ExtractMarkingScheme`, `BuildCurriculumGraph`, `ExtractCelticLanguageContent`) are tracked separately by the `leaving-cert-2026` openspec change.
