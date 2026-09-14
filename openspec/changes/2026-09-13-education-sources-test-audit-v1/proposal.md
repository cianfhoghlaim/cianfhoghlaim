# Change: Education Sources Test Audit v1

## Why

Plan 10 (British Isles education sources deep audit) verified the 8
jurisdictional DLT source surfaces for the British Isles pipeline:

| Jurisdiction | DLT sources | Authority |
|---|---|---|
| **Ireland (NCCA)** | **84** files | curriculumonline.ie, examinations.ie, ncca.ie |
| **England (OFQUAL)** | **29** files | AQA, OCR, Edexcel boards |
| **Scotland (SQA)** | **8** files | sqa.org.uk |
| **Wales (WJEC)** | **8** files | wjec.co.uk |
| **Northern Ireland (CCEA)** | **9** files | ccea.org.uk |
| **Guernsey (CEA)** | **5** files | ccea.org.uk (shared) |
| **Jersey (CEA)** | **6** files | ccea.org.uk (shared) |
| **Isle of Man** | **5** files | gov.im |

This SAFE audit adds smoke tests that verify the existing source
structure is preserved. The actual data fill (using Firecrawl MCP to
scrape NCCA/OFQUAL/SQA/WJEC/CCEA + process the markdown into BAML
extractions) is the next phase after the audit.

## What Changes

### 1. Education source tests
- `tests/education_sources/__init__.py`: new test package
- `tests/education_sources/test_education_sources.py`: 9 tests
  - `test_ncca_ireland_sources_count` — ≥80 NCCA files
  - `test_ofqual_england_sources_count` — ≥25 OFQUAL files
  - `test_sqa_scotland_sources_count` — ≥5 SQA files
  - `test_wjec_wales_sources_count` — ≥5 WJEC files
  - `test_ccea_ni_sources_count` — ≥5 CCEA files
  - `test_crown_dependencies_sources_exist` — ≥3 each (Guernsey, Jersey, IoM)
  - `test_biep_v3_orchestration_change_exists` — openspec change present
  - `test_ncca_unified_curriculum_source` — NCCA unified curriculum source
  - `test_lc_subject_dlt_sources` — 6 Ireland LC subjects covered

## What Does NOT Change

- ❌ No new DLT source files added (the data fill is deferred)
- ❌ No Firecrawl scraping runs (deferred to the data fill phase)
- ❌ No CocoIndex indexing runs (deferred to the data fill phase)
- ❌ No schema changes
- ❌ No openspec changes to the existing pipeline-biep-v3-orchestration

## Dependencies

- `Blocked by: none`
- `Affected repos: cianfhoghlaim`
- Soft dependency: Plan 8 (Firecrawl) — the data fill will use Firecrawl MCP
- Soft dependency: Plan 4 (CocoIndex) — the data fill will index via CocoIndex

## Cross-links

- Sister change: `2026-09-13-lakehouse-skill-and-test-audit-v1` (Plan 9)
- Sister change: `2026-09-13-firecrawl-skill-and-test-audit-v1` (Plan 8)
- Sister change: `2026-09-13-marimo-skill-and-test-audit-v1` (Plan 7)
- Sister change: `2026-09-13-google-adk-skill-and-test-audit-v1` (Plan 6)
- Sister change: `2026-09-13-dagster-skill-and-test-audit-v1` (Plan 5)
- Sister change: `2026-09-13-cocoindex-skill-and-test-audit-v1` (Plan 4)
- Sister change: `2026-09-13-llm-serving-skill-and-test-audit-v1` (Plan 3)
- Sister change: `2026-09-13-baml-health-test-and-skill-update-v1` (Plan 2)
- Sister change: `2026-09-12-dlt-1.29-feature-adoption-v1` (Plan 1)
