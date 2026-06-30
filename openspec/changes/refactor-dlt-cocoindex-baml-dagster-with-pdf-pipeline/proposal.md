# refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline — Comprehensive refactor + PDF processing pipeline

## Why

The `cianfhoghlaim/` package has been progressively consolidated through
prior openspec changes:

- `baml-reorganize-by-cluster` (3-cluster taxonomy: education / celtic / processing)
- `wire-baml-to-consolidated-pipelines` (consumer docstring sweeps)
- The in-flight 7-phase `consolidate-cianfhoghlaim-pyproject-and-8-dirs` (meaisinfhoghlaim redistribution, browser, observability)

**However**, significant drift remains between the actual content of the files
in `baml/`, `cocoindex/`, `dlt/`, `dagster/`, and `meaisinfhoghlaim/`. The
directory structure now matches the canonical shape, but the FILE CONTENTS
have not been audited for:

1. **BAML drift** — duplicate enum definitions, stale client references, broken syntax (`name: string` colon syntax blocks regeneration)
2. **CocoIndex drift** — 14 v1 Apps have inconsistent `lancedb.mount_table_target` + `_lifespan` usage; some reference deprecated BAML function names
3. **DLT drift** — many dlt sources use legacy `dlt_sources.*` paths; some reference the `craw_sources.ie.culture` sub-package that was renamed to `language/`
4. **Dagster drift** — 65+ asset files scattered at top level + sub-dirs; the asset graph doesn't mirror the new dlt/ structure (`api_sources/`, `filesystem/`, `language/`, `official_media/`, `portfolio/`, `british_isles/{nation}/`)
5. **PDF processing gap** — 133 leaving_certificate/ PDFs (11 subjects × EN/GA × 3 levels) lack a comprehensive dagster pipeline that exercises the new dlt + baml + cocoindex + meaisinfhoghlaim stack
6. **Notebook gap** — few end-to-end notebooks demonstrate the new pipeline capabilities

This change addresses all 6 issues in a coordinated 7-phase refactor (R1-R7).

## What

### R1 — Fix drift in `baml/` files (no regeneration)

**Scope**: 60+ `.baml` files across `baml/{education,celtic,processing}/`.

Tasks:
- **R1.1** Audit all 5 `baml/education/stages/*.baml` for duplicate enum definitions (e.g., `LeavingCertSubject`, `ExamLevel` are defined in 2-3 files each)
- **R1.2** Audit all 8 `baml/education/subjects/qpack_*.baml` for cross-file consistency (`MathNCCALevel` vs `LeavingCertSubject`)
- **R1.3** Fix the `| null` → `?` syntax bug in any remaining files (per `baml-reorganize-by-cluster` R2 already fixed `researchgate_extraction.baml`; other files may have the same issue)
- **R1.4** Add explicit `@description` strings to all classes/functions that lack them
- **R1.5** Sweep all BAML files for stale references to deleted modules (e.g., the `....ireland.curriculum_source` path is gone)
- **R1.6** Sweep all BAML files for client references — `LitellmClient` is canonical (per `clients.baml`)

**Out of scope**: BAML regeneration (`baml-cli generate` is blocked by pre-existing colon-syntax errors per the `wire-baml-to-consolidated-pipelines` follow-up issue).

### R2 — Fix drift in `cocoindex/` files

**Scope**: 36 `.py` files in `cianoindex/`.

Tasks:
- **R2.1** Audit the 8 subject embeddings (`gaeilge_embedding.py`, `english_embedding.py`, etc.) for consistent `lancedb.mount_table_target` + `_lifespan` usage
- **R2.2** Audit the 14 v1 Apps for the 4-rule conformance contract (R1-R4 per `oideachais-cocoindex-v1` skill)
- **R2.3** Verify all `b.ExtractXxx` references in cocoindex files match the canonical BAML function names (post the `baml-reorganize-by-cluster` change)
- **R2.4** Update imports from legacy `from cianfhoghlaim.baml_src.X import Y` → `from cianfhoghlaim.baml_client import b` (none expected, but verify)

### R3 — Fix drift in `dlt/` files (CONTENT ONLY)

**Scope**: 200+ `.py` files in `dlt/`.

Tasks:
- **R3.1** Audit all 8 `dlt/british_isles/{nation}/{domain}/*.py` for:
  - Correct `from cianfhoghlaim.dlt.common.incremental import crawl_source`
  - Correct `from cianfhoghlaim.dlt.law._legislation_helper import _crawl_legislation` for law files
  - Correct `from cianfhoghlaim.dlt.british_isles.{nation}.{domain} import X`
- **R3.2** Audit all 8 `dlt/filesystem/*.py` (leabharlann content):
  - Correct `from cianfhoghlaim.dlt.common.firecrawl_source import crawl_website`
  - Use `dlt.sources.filesystem` declarative for new file-type sources
- **R3.3** Audit all 3 `dlt/api_sources/*.py` (github, linkedin, researchgate):
  - Use `dlt.sources.rest_api.rest_api` declarative where applicable (per 7-phase T1.1)
- **R3.4** Audit all `dlt/language/*.py` (Celtic/Irish sources: canuint, duchas, tearma, gaeilge):
  - Use `dlt.sources.rest_api.rest_api` for the 4 gaois.ie APIs (Dúchas, Logainm, Tearma, AINM)
  - Celtic-specific patterns: Gaeltacht filtering, fada preservation
- **R3.5** Audit `dlt/portfolio/*.py` (artwork, cv, labels, teaching):
  - Consolidate the 7 modules into 4 (artwork, cv, labels_base+scraper, teaching)
- **R3.6** Audit `dlt/official_media/*.py` (instagram + BAML resolver):
  - Use the new BAML cluster taxonomy paths

### R4 — Reorganize dagster assets to match dlt structure

**Scope**: 65+ asset files in `dagster/assets/`.

Tasks:
- **R4.1** Move all 11 subject asset files to `dagster/assets/by_domain/education/` (applied_math, biology, business, chemistry, computer_science, english, french, gaeilge, geography, history, technology, ukrainian)
- **R4.2** Move all 8 `dlt/british_isles/{nation}/{domain}/` asset groups to `dagster/assets/by_domain/{law,medicine,site_analysis,statistics}/`
- **R4.3** Move `dlt/filesystem/` assets to `dagster/assets/by_domain/filesystem/`
- **R4.4** Move `dlt/api_sources/` assets to `dagster/assets/by_domain/api/`
- **R4.5** Move `dlt/language/` assets to `dagster/assets/by_domain/language/`
- **R4.6** Move `dlt/official_media/` assets to `dagster/assets/by_domain/official_media/`
- **R4.7** Move `dlt/portfolio/` assets to `dagster/assets/by_domain/portfolio/`
- **R4.8** Create `dagster/assets/by_domain/__init__.py` with backward-compat re-exports for the old top-level paths (one-release transition)
- **R4.9** Update `dagster/definitions.py` to import from `by_domain/`

**New `dagster/assets/by_domain/` shape**:
```
by_domain/
├── education/         (11 subject asset files)
├── law/               (7 law nation files - already done)
├── medicine/          (1 consolidated - already done)
├── filesystem/        (leabharlann content)
├── api/                (github, linkedin, researchgate)
├── language/          (canuint, duchas, tearma, gaeilge)
├── official_media/    (instagram + resolver)
├── portfolio/         (artwork, cv, labels, teaching)
├── site_analysis/
└── statistics/
```

### R5 — Create the 6-asset pattern for all 11 LC subjects

**Scope**: 11 subject asset files, each ~330 lines.

The 6-asset pattern (template: `mathematics_assets.py`):
1. **`{subject}_syllabus_raw`** — DLT ingestion of the {subject} PDFs into DuckLake
2. **`{subject}_syllabus_structured`** — BAML `ExtractLeavingCertSyllabus` per PDF
3. **`{subject}_quest_pack`** — BAML `Generate{Subject}QuestPack` per level (FL/OL/HL)
4. **`{subject}_embedding`** — CocoIndex v1 embedding into LanceDB (per-subject table)
5. **`{subject}_cognify`** — Cognee cognify pass (subject knowledge graph)
6. **`{subject}_dashboard`** — marimo notebook execution

**Priority order** (focus on bilingual Irish/English LC core first):
- R5.1 `english_assets.py` (extend existing)
- R5.2 `gaeilge_assets.py` (extend existing)
- R5.3 `mathematics_assets.py` (extend existing)
- R5.4 `applied_mathematics_assets.py` (extend existing)
- R5.5 `chemistry_assets.py` (extend existing)
- R5.6 `computer_science_assets.py` (extend existing)
- R5.7 `biology_assets.py` (NEW)
- R5.8 `business_assets.py` (NEW)
- R5.9 `french_assets.py` (NEW)
- R5.10 `geography_assets.py` (extend existing)
- R5.11 `history_assets.py` (extend existing)
- R5.12 `technology_assets.py` (NEW)
- R5.13 `ukrainian_assets.py` (NEW, may skip per user note)

### R6 — Build the PDF processing pipeline (uses meaisinfhoghlaim)

**Scope**: Consolidate the 3 existing PDF asset files + add new ones.

Tasks:
- **R6.1** Audit `dagster/assets/pdf_assets.py` + `pdf_processing_assets.py` + `pdf_processing/__init__.py` for overlap
- **R6.2** Consolidate into a single `dagster/assets/by_domain/pdf_processing.py` with the 8-asset pattern:
  - `pdf_discover` — scan `leaving_certificate/` for all 133 PDFs
  - `pdf_convert` — use `meaisinfhoghlaim/document_factory/converters/` to convert PDFs to markdown
  - `pdf_ocr_compare` — run 5 OCR models in parallel: deepseekocr, docling, marker, pymupdf4llm, unstructured
  - `pdf_extract_baml` — use BAML `ExtractLeavingCertSyllabus` + `ExtractLeavingCertMarkingScheme` + `ExtractLeavingCertPastPaper`
  - `pdf_embed_cocoindex` — embed extracted text into LanceDB via CocoIndex v1
  - `pdf_cognify` — Cognee cognify pass
  - `pdf_evaluate` — Ragas evaluation of extraction quality
  - `pdf_quality_check` — Irish content validation (fada preservation, dialect detection)
- **R6.3** Update `pdf_assets.py`, `pdf_processing_assets.py`, `pdf_processing/__init__.py` to be backward-compat shims
- **R6.4** Add a new `dagster/assets/by_domain/meaisinfhoghlaim_ocr.py` that uses the 24-model registry + 4-converter stack

### R7 — Create extensive notebooks demonstrating the pipelines

**Scope**: 20+ new notebooks in `notebooks/dashboards/`.

Tasks:
- **R7.1** Create 11 per-subject notebooks: `notebooks/dashboards/education/{subject}_full_pipeline.py`
- **R7.2** Create `notebooks/dashboards/pdf_processing/pdf_ocr_model_comparison.py` — compare 5 OCR models on the 133 PDFs
- **R7.3** Create `notebooks/dashboards/pdf_processing/pdf_extraction_quality.py` — Ragas eval across all subjects
- **R7.4** Create `notebooks/dashboards/pdf_processing/pdf_processing_benchmark.py` — performance benchmark
- **R7.5** Create `notebooks/dashboards/observability/irish_extraction_quality.py` — Irish-specific quality checks (fada, dialect)
- **R7.6** Create `notebooks/dashboards/observability/baml_drift_audit.py` — audit all BAML functions vs actual usage
- **R7.7** Create `notebooks/dashboards/duckdb/dlt_pipeline_overview.py` — show the 8-nation dlt pipeline
- **R7.8** Create `notebooks/dashboards/duckdb/cocoindex_embedding_coverage.py` — show all v1 Apps + their LanceDB tables
- **R7.9** Create `notebooks/dashboards/mmo/cianfhoghlaim_mmo_progress.py` — the MMO end-to-end demo

## Impact

| Metric | Before | After |
|--|--|--|
| BAML files with duplicate enum defs | 5+ | 0 |
| BAML files with `| null` syntax bug | 1+ | 0 |
| DLT files with legacy `dlt_sources.*` imports | 100+ | 0 |
| CocoIndex files with stale BAML references | ~10 | 0 |
| Dagster asset files at top level | 50+ | 0 (all under `by_domain/`) |
| Dagster `by_domain/` sub-dirs | 2 (law, medicine) | 10 |
| Per-subject dagster asset files (6-asset pattern) | 4 (math, appm, chem, eng, gael, geog, hist, comp_sci) | 11+ |
| PDF processing dagster assets | 8 (existing scattered) | 8 (consolidated in `by_domain/pdf_processing.py`) |
| Notebooks in `dashboards/` | 14 | 30+ |
| PDF samples processed (leaving_certificate/) | 0 (manual) | 133 (automated) |

### Affected specs
- **MODIFIED `oideachais-baml-schemas`** — the rule that all BAML files live in the 3-cluster taxonomy, with no duplicate enum definitions
- **MODIFIED `oideachais-pipeline`** — the rule that all dlt sources use the canonical `cianfhoghlaim.dlt.*` paths
- **MODIFIED `meaisinfhoghlaim-platform`** — the rule that every dagster asset is grouped by domain under `by_domain/`
- **MODIFIED `meaisinfhoghlaim-ocr-htr`** — the rule that the PDF processing pipeline uses all 24 OCR models + 5 converters

### Backward compatibility
- All consumer imports continue to work via backward-compat re-exports
- The BAML client is NOT regenerated (out of scope per the `wire-baml-to-consolidated-pipelines` follow-up)
- The dagster `definitions.py` continues to expose all 199+ assets (no removals, only re-org)

### Non-Goals
- No new dlt source files added (per user: "we will keep all the subdirectories of dlt now as they are")
- No new BAML functions added
- No new cocoindex v1 Apps added
- No web app changes
- No agents/ flatten (separate change)
- No BAML regeneration (the colon-syntax errors block it)

### Risk Assessment
| Risk | Mitigation |
|:--|:--|
| R1 audit reveals critical BAML dependencies | Stage-by-stage: audit first, fix second, verify no consumer breaks |
| R4 dagster reorg breaks the asset graph | Backward-compat shim files preserve all old paths; `dg list defs` validates after each move |
| R5 11 subject asset files take too long | Start with english + gaeilge + mathematics (the 3 highest-priority); the rest follow the same template |
| R6 PDF processing pipeline has long runtime | Partition by subject × level × language; each partition is independent; Ragas eval runs separately |
| R7 20+ notebooks are too many | Prioritize the 5 most informative (R7.1 english+gaeilge, R7.2 OCR comparison, R7.3 Ragas eval, R7.5 Irish quality, R7.7 dlt overview); the rest follow templates |

## Validation

1. `openspec validate refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline --strict` passes
2. `ccc search "dlt_sources\."` returns 0 hits in `dlt/`, `dagster/`, `cocoindex/`
3. `dg list defs` shows the new `by_domain/` shape with 10 sub-dirs
4. `python -c "from cianfhoghlaim.dlt.british_isles.ireland.education.aistear import aistear_curriculum"` succeeds
5. The 11 subject asset files all materialise without error (via `dg launch --select "*_syllabus_raw"`)
6. The PDF processing pipeline runs on a single subject (math) and produces 7 valid output tables in DuckLake
7. The 20+ notebooks run successfully (no exceptions) via `marimo run`