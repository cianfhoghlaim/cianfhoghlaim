# Author-Archive v1: UoG Coursework Ingestion

## Why

Stage 1 of `author-archive-v1` shipped the web-scraping layer for the
160 official_media sources. Stage 2 extends the same BAML +
DLT + Dagster pattern to the **1,938 University of Galway coursework
files** in `leabharlann/ollscoil_na_gaillimhe/` and the **39 personal
records** in `cian_mac_an_déisigh_uí_liatháin/`.

The user said: "we want to know what data we have and how it was
sourced". The coursework files are the personal data — the user's
own B.Ed, PGCE, BA, HDip, and ongoing MSc work. Stage 1 was about
external sources; Stage 2 is about the user's own intellectual
output.

The four UoG modules (mata, software, irish, education) have very
different shapes:

- **mata/** has heavy LaTeX (cryptography proofs, statistics
  tables), Maple / Python notebooks
- **software_development/** has Java / Python / SQL code with
  technical reports
- **irish/** has Gaeilge essays, translations, reviews — bilingual
  content
- **education/** has reflective journals, lesson plans, BME
  portfolios — the largest module (~1008 files)

The personal records folder has three sub-dirs:
- `achievement/` — transcripts, parchments, awards
- `teaching/` — references, scholarship letters
- `identity/` — **private records (medical, disability, vetting)**,
  excluded by default

This change adds:

- 5 new BAML functions in `baml_src/author_archive.baml` (one per
  module, all returning the new `UoGModuleExtraction` class)
- 5 new DLT sources under `oideachais/dlt_sources/author_archive/`
  (`olscoil_mata.py`, `olscoil_software.py`, `olscoil_irish.py`,
  `olscoil_education.py`, `personal_records.py`)
- 10 new Dagster assets (5 modules × 2 resources: `_raw` for
  filesystem scan + `_extraction` for BAML)
- OpenSpec change `author-archive-uog-coursework/` with 1 spec
  delta (the new pipeline capability)
- Tests for the new assets + DLT sources + BAML functions

## What Changes

### Code

- `baml_src/author_archive.baml`: +5 new functions
  (`ExtractUoGMathModule`, `ExtractUoGSoftwareModule`,
  `ExtractUoGIrishModule`, `ExtractUoGEducationModule`,
  `ExtractPersonalRecord`) + 4 new types (`UoGSubject`,
  `UoGDocumentKind`, `UoGModuleExtraction`).

- `oideachais/dlt_sources/author_archive/olscoil_*.py` (5 new files):
  per-module DLT sources, each with a `_documents` and `_extraction`
  resource.

- `oideachais/dagster_defs/assets/official_media/uog_coursework_assets.py`:
  10 new Dagster assets (5 modules × 2 resources).

- `oideachais/dagster_defs/assets/official_media/__init__.py` +
  `oideachais/dagster_defs/assets/__init__.py`: re-export the 10
  new assets and add them to `all_assets`.

### Spec deltas

- `author-archive-uog-coursework/spec.md` — the new UoG coursework
  capability (BAML + DLT + Dagster matrix)

## Impact

- 1,938 UoG coursework files get BAML extraction into
  `oideachais.oideachais_mata.mata_extraction`,
  `..._software.software_extraction`, etc.
- 39 personal records get extraction (29 by default; identity
  excluded unless the operator has approved)
- The marimo dashboard gets a "UoG Coursework" tab that lists
  every module, every course code, every key topic, and every
  extracted equation

## Out of scope (deferred)

- Stage 3 (cross-corpus knowledge graph) — independent of this
  change
- Stage 4 (multi-target deployment) — Stage 4 of the original
  plan, deferred
- OpenSpec change `author-archive-v2/` for the cross-corpus cognify
  + marimo changes
- The `past/` subdir of `leabharlann/ollscoil_na_gaillimhe/` is
  excluded from this change (it contains old undergraduate
  business/law coursework from 2012-2013; will be a separate
  change)
