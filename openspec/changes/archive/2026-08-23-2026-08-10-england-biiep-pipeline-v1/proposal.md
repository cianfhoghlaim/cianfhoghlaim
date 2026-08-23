# Proposal: England BIEP Pipeline (3 Boards × 92 Subjects)

**Change ID:** `2026-08-10-england-biiep-pipeline-v1`
**Date:** 2026-08-10
**Author:** Build agent
**Status:** Draft

## Why

Of the **276 England CocoIndex Apps already defined** (3 boards × 43 GCSE subjects + 3 × 49 A-Level subjects = 276 Apps in `cocoindex_flows/biep_parity/england_{gcse,a_level}_apps.py`), **zero are wired into a DLT source or Dagster asset**. Per the BIEP v2 spec, this was scoped as out-of-scope (deferred to v2). With the post-v7 flattening + BAML v3 + Dagster 5-layer architecture now stable, the England pipeline is ready for activation.

This change:
1. Adds 6 DLT sources (`gcse_{aqa,ocr,edexcel}_source.py` + `a_level_{aqa,ocr,edexcel}_source.py`) consuming from `stedding/site_scrape_samples/england/`
2. Adds 6 Dagster asset groups (`gcse_assets.py` + `a_level_assets.py`) wrapping the DLT sources + BAML extraction + CocoIndex embedding + MotherDuck load
3. Adds 1 real BAML prompt for the missing 3 of 4 functions in `baml_src/british_isles/england/education/curriculum_syllabus.baml` (ExtractOCRQualSpec, ExtractEdexcelQualSpec, ExtractUKQualSpec already have real prompts; only ExtractAQAQualSpec is stub)
4. Adds `england_education/misconfig_check.py` for cross-board subject coverage
5. Seeds the 92 subjects from existing NCCA + AQA/OCR/Edexcel website metadata (download script)

## What changes

### Code (4 new + 4 modified)

| File | Status | What |
|---|---|---|
| `dlt_sources/british_isles/england/education/gcse/{aqa,ocr,edexcel}_gcse_source.py` | **NEW ×3** | 3 GCSE DLT sources for the 3 boards × 43 subjects |
| `dlt_sources/british_isles/england/education/a_level/{aqa,ocr,edexcel}_a_level_source.py` | **NEW ×3** | 3 A-Level DLT sources for the 3 boards × 49 subjects |
| `orchestration/defs/2_materials/england_education/{gcse,a_level}_assets.py` | **NEW ×2** | 6 asset groups (3 GCSE + 3 A-Level) wrapping the DLT sources + BAML + CocoIndex |
| `orchestration/defs/2_materials/england_education/misconfig_check.py` | **NEW** | Cross-board subject coverage check |
| `scripts/seed_england_pdfs.py` | **NEW** | Scrape 92 subjects × 3 boards (or seed from existing cache) |
| `baml_src/british_isles/england/education/curriculum_syllabus.baml` | modified | Adds 1 real prompt (ExtractAQAQualSpec was stub) |
| `dlt_sources/british_isles/england/education/__init__.py` | modified | Re-exports 6 sources |
| `orchestration/definitions.py` | modified | Loads the 6 new asset groups |

### Spec (1 spec delta, +3 ADDED Requirements)

- `openspec/specs/bie-8-jurisdictions/spec.md` — 3 ADDED Requirements (DLT sources + Dagster assets + BAML extraction for England)

### Openspec (this change)

- `openspec/changes/2026-08-10-england-biiep-pipeline-v1/proposal.md` (this file)
- `openspec/changes/2026-08-10-england-biiep-pipeline-v1/tasks.md`
- `openspec/changes/2026-08-10-england-biiep-pipeline-v1/specs/bie-8-jurisdictions/spec.md` (delta)

## Dependencies

- **Blocked by:** C3 (uses the BAML extraction template established for LC subjects) — ✓ shipped
- **Blocks:** C5 (web UI surfaces England data)

## Success criteria

1. `openspec validate 2026-08-10-england-biiep-pipeline-v1 --strict` returns 0 errors
2. `dagster asset materialize --select england_*_loaded` succeeds for all 6 asset groups
3. The 276 CocoIndex Apps materialize (verified via `dagster asset list | grep england`)
