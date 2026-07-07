# refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline — Tasks

## R1 — Fix drift in baml/ files

- [ ] R1.1 Audit duplicate enum defs in `baml/education/stages/{aistear,primary,junior_cycle,senior_cycle,tertiary}.baml` (`LeavingCertSubject`, `ExamLevel`, etc.)
- [ ] R1.2 Audit cross-file consistency in `baml/education/subjects/qpack_*.baml` (8 files)
- [ ] R1.3 Fix `| null` → `?` syntax bug in remaining BAML files
- [ ] R1.4 Add `@description` to all classes/functions that lack them
- [ ] R1.5 Sweep stale references to deleted modules
- [ ] R1.6 Sweep client references — use `LitellmClient` as canonical
- [ ] R1.7 Commit R1

## R2 — Fix drift in cocoindex/ files

- [ ] R2.1 Audit 8 subject embeddings for `_lifespan` + `mount_table_target` consistency
- [ ] R2.2 Audit 14 v1 Apps for 4-rule conformance (R1-R4)
- [ ] R2.3 Verify `b.ExtractXxx` references match canonical BAML function names
- [ ] R2.4 Sweep `from cianfhoghlaim.baml_src.X` legacy imports
- [ ] R2.5 Commit R2

## R3 — Fix drift in dlt/ files (CONTENT only)

- [ ] R3.1 Audit 8 `dlt/british_isles/{nation}/{domain}/*.py` for correct `dlt.common.*` imports
- [ ] R3.2 Audit 8 `dlt/filesystem/*.py` for `dlt.sources.filesystem` declarative patterns
- [ ] R3.3 Audit 3 `dlt/api_sources/*.py` for `dlt.sources.rest_api.rest_api` declarative
- [ ] R3.4 Audit 25 `dlt/language/*.py` for Celtic-specific patterns
- [ ] R3.5 Audit 7 `dlt/portfolio/*.py` (artwork, cv, labels, teaching)
- [ ] R3.6 Audit 9 `dlt/official_media/*.py`
- [ ] R3.7 Commit R3

## R4 — Reorganize dagster assets to match dlt structure

- [ ] R4.1 Create `dagster/assets/by_domain/education/` + move 11 subject files
- [ ] R4.2 Create `dagster/assets/by_domain/{law,medicine,site_analysis,statistics}/` + move 8 nation dirs
- [ ] R4.3 Create `dagster/assets/by_domain/filesystem/` + move 8 filesystem files
- [ ] R4.4 Create `dagster/assets/by_domain/api/` + move 3 API files
- [ ] R4.5 Create `dagster/assets/by_domain/language/` + move Celtic files
- [ ] R4.6 Create `dagster/assets/by_domain/official_media/` + move 9 files
- [ ] R4.7 Create `dagster/assets/by_domain/portfolio/` + move 7 files
- [ ] R4.8 Create `dagster/assets/by_domain/__init__.py` with backward-compat re-exports
- [ ] R4.9 Update `dagster/definitions.py` to import from `by_domain/`
- [ ] R4.10 `dg list defs` validates all 199+ assets still load
- [ ] R4.11 Commit R4

## R5 — Create the 6-asset pattern for all 11 LC subjects

- [ ] R5.1 `english_assets.py` (extend existing — add 6 assets)
- [ ] R5.2 `gaeilge_assets.py` (extend existing — add 6 assets)
- [ ] R5.3 `mathematics_assets.py` (extend existing — add 6 assets)
- [ ] R5.4 `applied_mathematics_assets.py` (extend existing)
- [ ] R5.5 `chemistry_assets.py` (extend existing)
- [ ] R5.6 `computer_science_assets.py` (extend existing)
- [ ] R5.7 `biology_assets.py` (NEW)
- [ ] R5.8 `business_assets.py` (NEW)
- [ ] R5.9 `french_assets.py` (NEW)
- [ ] R5.10 `geography_assets.py` (extend existing)
- [ ] R5.11 `history_assets.py` (extend existing)
- [ ] R5.12 `technology_assets.py` (NEW)
- [ ] R5.13 `ukrainian_assets.py` (NEW, may skip)
- [ ] R5.14 Commit R5

## R6 — Build the PDF processing pipeline

- [ ] R6.1 Audit `pdf_assets.py` + `pdf_processing_assets.py` + `pdf_processing/__init__.py` for overlap
- [ ] R6.2 Create `dagster/assets/by_domain/pdf_processing.py` with the 8-asset pattern (discover, convert, ocr_compare, extract_baml, embed_cocoindex, cognify, evaluate, quality_check)
- [ ] R6.3 Update `pdf_assets.py`, `pdf_processing_assets.py`, `pdf_processing/__init__.py` to be backward-compat shims
- [ ] R6.4 Add `dagster/assets/by_domain/meaisinfhoghlaim_ocr.py` (24-model registry + 4-converter stack)
- [ ] R6.5 Commit R6

## R7 — Create extensive notebooks

- [ ] R7.1 Create 11 per-subject notebooks: `notebooks/dashboards/education/{subject}_full_pipeline.py`
- [ ] R7.2 `notebooks/dashboards/pdf_processing/pdf_ocr_model_comparison.py`
- [ ] R7.3 `notebooks/dashboards/pdf_processing/pdf_extraction_quality.py`
- [ ] R7.4 `notebooks/dashboards/pdf_processing/pdf_processing_benchmark.py`
- [ ] R7.5 `notebooks/dashboards/observability/irish_extraction_quality.py`
- [ ] R7.6 `notebooks/dashboards/observability/baml_drift_audit.py`
- [ ] R7.7 `notebooks/dashboards/duckdb/dlt_pipeline_overview.py`
- [ ] R7.8 `notebooks/dashboards/duckdb/cocoindex_embedding_coverage.py`
- [ ] R7.9 `notebooks/dashboards/mmo/cianfhoghlaim_mmo_progress.py`
- [ ] R7.10 Commit R7

## Final validation

- [ ] F1 `openspec validate refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline --strict` passes
- [ ] F2 `ccc search "dlt_sources\."` returns 0 hits in dlt/dagster/cocoindex
- [ ] F3 `dg list defs` shows the new by_domain shape with 10 sub-dirs
- [ ] F4 The 11 subject asset files all materialise without error
- [ ] F5 The PDF processing pipeline runs on math subject and produces 7 valid DuckLake tables
- [ ] F6 The 20+ notebooks run successfully via `marimo run`