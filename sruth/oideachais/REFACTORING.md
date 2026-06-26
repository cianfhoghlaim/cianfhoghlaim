# Oideachais — Refactoring Backlog

**Last updated:** 2026-06-26

This file is the canonical refactor backlog for the `oideachais/` data platform. Each item has a `Status` field (`done` | `in_progress` | `backlog` | `superseded`) and links to a tracking openspec change (where applicable).

---

## Round 11 — Cross-Quadrant Sprawl Audit (2026-06-25, in_progress)

The Round 11 multi-quadrant audit identified sprawl across all 5 quadrants + infrastructure + HF Spaces. The oideachais portion is sequenced in 5 phases; each lands as a discrete openspec change.

### Phase 1 — Delete confirmed-dead code (`oideachais-audit-phase-1-delete-dead-code`)

**Status**: `done` (archived 2026-06-25)
**Risk**: LOW (all deletions confirmed 0-importer)
**Impact**: -310 KB, 61 → 56 dirs, 8 root-level files removed

Deleted items (12 total):

| Path | Size | Why dead |
|:--|--:|:--|
| `sruth/oideachais/oideachais/` | 4 dirs | Nested legacy shim; 0 importers; legacy `data_platform` PEP 562 registration removed in phase 5 |
| `sruth/oideachais/services/embedding_service/` | 8 KB | Dead FastAPI; superseded by `clients/embedding_client.py` |
| `sruth/oideachais/marimo/` | 15 KB | Dead 1-file stub; superseded by `sruth/meaisinfhoghlaim/marimo/` |
| `sruth/oideachais/exam_scraper/` | 8 KB | Dead 2-script; superseded by `dlt_sources/ireland/examinations.py` |
| `sruth/oideachais/downloads/curriculum_pdfs/` | 0 B | Empty mount |
| `sruth/oideachais/routes/` (5 .py + README, 2,836 LOC) | 100% byte-identical | Canonical: `api/routes/`; 0 importers |
| `sruth/oideachais/sensors/` (2 .py + __init__ + README, 994 LOC) | 100% byte-identical (curriculum_freshness + domain_sensors) | Canonical: `dagster_defs/sensors/`; stale `__init__.py` missing 3 of 5 sensor groups; 0 importers |
| `sruth/oideachais/middleware/` (6 files + README, 1,668 LOC) | 100% byte-identical | Canonical: `api/middleware/`; 0 importers |
| `sruth/oideachais/storage/serial_executor.py` (29 LOC) | Deprecated stub (untracked) | Canonical: `core/storage/serial_executor.py`; 1 importer (tests/conftest.py, updated) |

### Phase 2B — Legacy Migration to Canonical Homes (`oideachais-audit-phase-2b-migrate-legacy-storage-and-dagster-assets`)

**Status**: `done` (archived 2026-06-25)
**Risk**: MEDIUM (non-trivial file moves + multi-file spec ref updates + Dagster asset import path changes; broken `sruth.shared.utils` import fixed in `lancedb_cloud.py`)
**Impact**: -1,544 LOC deleted (3 dead dagster modules), 5,646 LOC migrated to canonical homes

#### Migrated dagster_assets files

| Source | Destination | LOC |
|:--|:--|--:|
| `dagster_assets/model_conversion.py` | `dagster_defs/assets/model_conversion.py` | 374 |
| `dagster_assets/asset_generation.py` | `dagster_defs/assets/asset_generation.py` | 281 |

#### Deleted (3 dead modules, 0 importers)

| File | LOC | Why dead |
|:--|--:|:--|
| `dagster_assets/grammar_validation.py` | 415 | Gramadóir integration, never wired |
| `dagster_assets/pdf_benchmark.py` | 483 | PDFStract benchmark, never wired |
| `dagster_assets/syntactic_parsing.py` | 535 | UD treebank parser, never wired |

#### Migrated storage files (9 unique, ~5,557 LOC)

| Source | Destination | LOC |
|:--|:--|--:|
| `storage/config.py` | `core/storage/config.py` | 359 |
| `storage/connections.py` | `core/storage/connections.py` | 691 |
| `storage/ducklake.py` | `core/storage/ducklake.py` (legacy Garage+PlanetScale variant, retained for direct import) | 780 |
| `storage/ducklake_client.py` | `core/storage/clients/ducklake.py` (canonical, SQLite/Postgres variant) | 882 |
| `storage/ducklake_filesystem.py` | `core/storage/clients/ducklake_filesystem.py` | 623 |
| `storage/init_schemas.py` | `core/storage/init_schemas.py` | 418 |
| `storage/lance_iceberg.py` | `core/storage/lance_iceberg.py` | 603 |
| `storage/lancedb_cloud.py` | `core/storage/clients/lancedb_cloud.py` | 664 |
| `storage/curriculum_vectors.py` | `core/storage/curriculum_vectors.py` | 427 |

Note: `core/storage/ducklake.py` and `core/storage/clients/ducklake.py` both define `DuckLakeClient` / `DuckLakeSnapshot` / `CELTIC_MANUSCRIPT_SCHEMAS` / `DuckLakeBackend` / `get_ducklake_backend` (different implementations). The `clients/` variant is re-exported as canonical via `core/storage/__init__.py`; the legacy `ducklake.py` remains importable explicitly.

### Phase 3A — Rename `dlt_sources/author_archive/` → `dlt_sources/leabharlann/` (`oideachais-audit-phase-3a-rename-dlt-author-archive-to-leabharlann`)

**Status**: `done` (archived 2026-06-26)
**Risk**: LOW (filesystem rename + import path update + doc reference update; 5 production code files + 2 test files updated)
**Impact**: 12 files renamed in-place (git mv), 0 net LOC change

The DLT source package for the personal archive was named `author_archive/` but all 6 source callables inside already used the `leabharlann_*` prefix (`leabharlann_books`, `leabharlann_zotero`, `leabharlann_takeout`), and the `oideachais-leabharlann` skill describes it as "leabharlann (personal archive)". This created a name mismatch between the filesystem and the source callable names.

This change ONLY renames the DLT source package directory. It does NOT rename the Dagster assets (`author_archive_assets.py`), Cognee cognify pass (`cognee_integration/author_archive_cognify.py`), cross-corpus rules (`cognify_rules/author_archive_cross_corpus.py`), OCR chain (`ocr/author_archive_ocr.py`), or pipeline/dataset name prefixes in `dlt_utils/target_factory.py` — those subsystem names are scoped separately and out of scope here.

#### Files renamed

| Source | Destination |
|:--|:--|
| `dlt_sources/author_archive/__init__.py` | `dlt_sources/leabharlann/__init__.py` |
| `dlt_sources/author_archive/leabharlann_books.py` | `dlt_sources/leabharlann/leabharlann_books.py` |
| `dlt_sources/author_archive/zotero.py` | `dlt_sources/leabharlann/zotero.py` |
| `dlt_sources/author_archive/takeout_v1.py` | `dlt_sources/leabharlann/takeout_v1.py` |
| `dlt_sources/author_archive/google_takeout.py` | `dlt_sources/leabharlann/google_takeout.py` |
| `dlt_sources/author_archive/gemini_deep_research.py` | `dlt_sources/leabharlann/gemini_deep_research.py` |
| `dlt_sources/author_archive/university_of_galway.py` | `dlt_sources/leabharlann/university_of_galway.py` |
| `dlt_sources/author_archive/previews.py` | `dlt_sources/leabharlann/previews.py` |
| `dlt_sources/author_archive/_epub_extractor.py` | `dlt_sources/leabharlann/_epub_extractor.py` |
| `dlt_sources/author_archive/_citation_extractor.py` | `dlt_sources/leabharlann/_citation_extractor.py` |
| `dlt_sources/author_archive/_scanner.py` | `dlt_sources/leabharlann/_scanner.py` |
| `dlt_sources/author_archive/_takeout_paths.py` | `dlt_sources/leabharlann/_takeout_paths.py` |
| `dlt_sources/author_archive/config.example.yaml` | `dlt_sources/leabharlann/config.example.yaml` |

#### Production code imports updated (5 files)

| File | Sites updated |
|:--|--:|
| `dagster_defs/assets/author_archive_assets.py` | 3 |
| `dagster_defs/assets/leabharlann_assets.py` | 3 |
| `dagster_defs/sensors/author_archive_sensors.py` | 1 |
| `cognee_integration/leabharlann_cognify.py` | 1 (docstring) |
| `ocr/author_archive_ocr.py` | 1 (docstring) |

#### Test code imports updated (2 files)

| File | Sites updated |
|:--|--:|
| `tests/test_leabharlann_pipeline.py` | 12 |
| `tests/test_author_archive_pipeline.py` | 4 |

#### Doc references updated (8 files)

`STATUS.md`, `cocoindex_flows/README.md`, `baml_src/README.md`, `oideachais/README.md`, `oideachais/AGENTS.md`, `oideachais/REFACTORING.md`, `dagster_defs/definitions.py` (comment), `dlt_sources/leabharlann/{__init__,_scanner,leabharlann_books,google_takeout}.py` (docstrings), `openspec/specs/{author-archive-uog-coursework,oideachais-leabharlann}/spec.md`, `dlt_sources/ireland/README.md`.

#### Validated

- `openspec validate oideachais-audit-phase-3a-rename-dlt-author-archive-to-leabharlann --strict` passes
- `from dlt_sources.leabharlann import leabharlann_books_source, zotero_source, takeout_v1_source, university_of_galway_source, gemini_deep_research_source` succeeds (5 sources)
- `mise run lint:skills` 123/123 pass
- 0 remaining `dlt_sources.author_archive` references in non-archived files (frozen `openspec/changes/archive/*` records left untouched)

#### Test imports updated (3 files, 11 imports)

- `tests/conftest.py:258` → `core.storage.clients.lancedb_cloud.CircuitBreaker`
- `tests/dlt_sources/test_integration.py:282,317` → `core.storage.clients.lancedb_cloud`
- `tests/storage/test_lancedb_cloud.py` (9 sites) → `core.storage.clients.lancedb_cloud` + fixed `sruth.shared.utils` import to `core.utils.circuit_breaker`

#### openspec spec references updated (5 lines)

- `openspec/specs/oideachais-pipeline/spec.md:166,869,870,912`
- `openspec/changes/refactor-quadrants-to-sruth/proposal.md:182`

#### Broken imports fixed

- `core/storage/clients/lancedb_cloud.py:38` — `from sruth.shared.utils import CircuitBreaker, ...` → split into `from oideachais.core.utils.circuit_breaker import CircuitBreaker, CircuitBreakerOpen` + `from oideachais.core.utils.retry import retry_with_backoff`
- `core/storage/clients/lancedb_cloud.py:41` — `from .serial_executor import SerialDatabaseExecutor` → `from ..serial_executor import SerialDatabaseExecutor` (path resolution after migration)
- `tests/storage/test_lancedb_cloud.py:227` — same `sruth.shared.utils` fix as above
| `sruth/oideachais/leaving_cert_timetable.pdf` | 270 KB | Orphaned binary |
| `sruth/oideachais/PIPELINE_OPERATIONS.md` | 3.7 KB | Orphaned doc; superseded by `STATUS.md` |
| 5× `sruth/oideachais/test_*.py` | 5.7 KB | Orphaned root-level tests; not in canonical `tests/` |



> **Workflow**: pick an item from `backlog`, open an openspec change, change the status to `in_progress` in the same commit as the first code change, then to `done` in the commit that closes the change.

---

## Top of the backlog (priority order)

### 1. Primary + Junior Cycle British Isles dlt + BAML loop

**Status**: `backlog`
**Tracks**: queued openspec change `primary-secondary-british-isles-dlt-baml` (to be opened)
**Effort**: ~2 weeks
**Why**: `baml_src/primary.baml` and `baml_src/junior_cycle.baml` define 4 BAML functions (`ExtractPrimaryFramework`, `ExtractPrimaryLearningOutcomes`, `ExtractJCSpec`, `ExtractCBADescriptor`) but **no matching dlt source backs them in `oideachais/dlt_sources/ireland/`** (only `aistear.py` and `senior_cycle.py` exist). The BAML extraction is unreachable. UK nations primary/secondary sources are also missing.
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
| 9 | 3 document extraction utilities re-implement pymupdf + python-docx: `oideachais/dlt_sources/leabharlann/_scanner._extract_text_from_{pdf,word,code}` + `oideachais/document_factory/pdf_converter.py` + `oideachais/cocoindex_flows/pdf_embedding.py:PDFEmbeddingPipeline` | `backlog` | Consolidate into `oideachais/document_extraction/`. |
| 10 | BAML `ExtractHandwrittenEquations` is called only in `oideachais/ocr/author_archive_ocr.py:1`, not wired to any Dagster asset | `backlog` | Wire to `leabharlann_handwriting_ocr` asset (currently just a config check, no real OCR). |
| 11 | BAML `ExtractZoteroMetadata` is defined in `baml_src/author_archive.baml` but never called from any dlt source | `backlog` | Wire to `leabharlann_zotero_raw.extraction_metadata` resource. |
| 12 | 3 leabharlann CocoIndex Apps re-declare the same `@coco.lifespan` 3 times | `backlog` | Consolidate to one module-level `@coco.lifespan`. |
| 13 | The `baml_src/tertiary.baml` schemas are defined but `oideachais/dlt_sources/ireland/tertiary.py` does not call any BAML function | `backlog` | Wire to tertiary extraction. |
| 14 | The `baml_src/curriculum_extraction.baml` 3 functions are referenced by 70+ @dlt_assets but no asset check verifies the BAML output structure | `backlog` | Add asset checks for BAML extraction quality. |
| 15 | `oideachais/cocoindex_flows/transforms/` has 3 transformation helpers (`caighdean_standardize`, `terminology_linking`) but they're not wired into any CocoIndex flow | `backlog` | Add to the v1 `leabharlann_embedding` flow. |
| 16 | `oideachais/dagster_defs/assets/leabharlann_assets.py:cocoindex_books_update` calls `subprocess.run(["cocoindex", "update", ...])` but `cocoindex` may not be on the worker PATH | `in_progress` | Add a try/except + structured error in the asset materialisation. |
| 17 | `oideachais/dagster_defs/assets/author_archive_assets.py` declares 7 assets but `cocoindex update` is never actually invoked (assets are stubs) | `backlog` | Wire to the v1 `author_archive_embedding.py` flow (after the v0 → v1 migration). |
| 18 | `oideachais/cognee_integration/cross_stage_cognify.py` declares `cross_stage_cognify` as a Dagster asset but it is a stub — no actual Cognee cognify call is made | `backlog` | Wire to the real Cognee cognify lifecycle. |
| 19 | `oideachais/dlt_sources/leabharlann/google_takeout.py` has `phase2_oauth_drive_export` and `phase2_gmail_export` stubs that raise `NotImplementedError` | `backlog` | Phase 2 of the takeout source. |
| 20 | The 3 `leabharlann_cocoindex_*_update` assets use `subprocess.run` to invoke the v1 Apps. If `cocoindex` is not on PATH (likely on the production MacBook which doesn't have cocoindex installed), the asset materialisation fails | `in_progress` | Add a `try/except FileNotFoundError` and skip the update with a warning, allowing the rest of the pipeline to continue. |
| 21 | The 6 `oideachais/dlt_sources/leabharlann/` sources are NOT registered in the `oideachais/dlt_sources/__init__.py` (only the author-archive package itself is) | `done` | Already done — they are re-exported via `oideachais.dlt_sources.leabharlann`. |

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
| 10 | `oideachais/dlt_sources/leabharlann/` package created (6 dlt sources for leabharlann + author archive) | `done` | `openspec/changes/leabharlann-cocoindex-v1` (commit `676db8664`) |
| 11 | `oideachais/cocoindex_flows/leabharlann_embedding.py` written (3 v1 Apps + 3 search handlers) | `done` | `openspec/changes/leabharlann-cocoindex-v1` |
| 12 | `baml_src/author_archive.baml` extended with `ZoteroPaper` + `Author` + `PaperKind` enum + `ExtractZoteroMetadata` | `done` | `openspec/changes/leabharlann-cocoindex-v1` |
| 13 | `oideachais/dagster_defs/assets/leabharlann_assets.py` written (7 assets) | `done` | `openspec/changes/leabharlann-cocoindex-v1` |
| 14 | `oideachais/dagster_defs/sensors/leabharlann_sensors.py` written (60 s directory-watch sensor) | `done` | `openspec/changes/leabharlann-cocoindex-v1` |
| 15 | `oideachais/ocr/author_archive_ocr.py` written (Pylaia / TrOCR / PaddleOCR / VLM dispatch) | `done` | `openspec/changes/author-archive-gemini-and-uos-ingestion` |
| 16 | `oideachais/dlt_sources/leabharlann/_epub_extractor.py` written (ebooklib-based, graceful degradation) | `done` | `openspec/changes/leabharlann-cocoindex-v1` |
| 17 | `oideachais/dlt_sources/leabharlann/_citation_extractor.py` written (PyMuPDF link extraction) | `done` | `openspec/changes/author-archive-gemini-and-uos-ingestion` |
| 18 | `oideachais/dagster_defs/assets/author_archive_assets.py` written (7 author-archive assets) | `done` | `openspec/changes/author-archive-gemini-and-uos-ingestion` |
| 19 | `oideachais/dlt_utils/safety.py` extended with `validate_source_kwargs` + `safe_dlt_run_with_progress` (dlt 1.0 helpers) | `done` | `openspec/changes/refactor-dlt-dagster-2026-stack-align` |
| 20 | `oideachais/dlt_utils/ducklake_options.py` written (DuckLake 1.0: inlining + clustering + bucket partitioning) | `done` | `openspec/changes/refactor-dlt-dagster-2026-stack-align` |
| 21 | `oideachais/dlt_utils/schema.py` written (DuckDB + DuckLake GEOMETRY + VARIANT types) | `done` | `openspec/changes/refactor-dlt-dagster-2026-stack-align` |
| 22 | `oideachais/dlt_utils/motherduck_options.py` written (managed / BYOB / BYOC hosting options) | `done` | `openspec/changes/refactor-dlt-dagster-2026-stack-align` |
| 23 | `oideachais/lancedb/indexing.py` written (HNSW + IVF-PQ + scalar B-tree + optimize) | `done` | `openspec/changes/refactor-dlt-dagster-2026-stack-align` |
| 24 | `oideachais/cocoindex_flows/_lifespan.py` written (shared `@coco.lifespan` + 3 ContextKeys) | `done` | `openspec/changes/refactor-dlt-dagster-2026-stack-align` |
| 25 | `oideachais/dagster_defs/components/` written (3 KCG-specific Dagster Components) | `done` | `openspec/changes/refactor-dlt-dagster-2026-stack-align` |
| 26 | `oideachais/dagster_defs/defs.yaml` written (DefsFolderComponent mount point) | `done` | `openspec/changes/refactor-dlt-dagster-2026-stack-align` |
| 27 | `oideachais/dagster_defs/README.md` written (the `dg` CLI developer workflow) | `done` | `openspec/changes/refactor-dlt-dagster-2026-stack-align` |
| 28 | `oideachais/graph/graphiti_client.py` written (real Graphiti 0.5 client + FalkorDB Lite fallback) | `done` | `openspec/changes/refactor-dlt-dagster-2026-stack-align` |

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
