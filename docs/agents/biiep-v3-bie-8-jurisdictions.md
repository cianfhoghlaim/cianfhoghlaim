# BIEP v3 — 8-Jurisdiction Rollout + 2 Scanner Domains

> Per the `2026-08-13-biep-v3-systematic-download-ireland-england-v1`
> openspec change. The complete 8 British Isles jurisdictions + the 2
> general-purpose scanner domains.

## Overview

The BIEP v3 systematic download plan covers **8 British Isles
jurisdictions** + **2 general-purpose scanner domains**. The 8
jurisdictions are jurisdiction-scoped (each has its own DLT pipeline +
BAML Extract* function + Dagster assets + MotherDuck Dive + Flight).
The 2 scanner domains are jurisdiction-agnostic (they apply across all 8
jurisdictions + cross-cutting).

## 8 British Isles jurisdictions

| Jurisdiction | DLT pipeline | BAML Extract* | Subjects | Cohorts | Cadence | Mise task | ChangeDetection sensor |
|:--|:--|:--|--:|--:|:--|:--|:--|
| 🇮🇪 Ireland (LC) | `dlt_sources/british_isles/ireland/education/ireland_jurisdiction_pipeline.py` | `ExtractCurriculumSyllabus` | 6 | 12 (6 × 2 langs) | Yearly | `biep:v3:m1` | `ncca_registry_sensor` |
| 🇮🇪 Ireland (JC) | (same, multi-stage) | `ExtractJCCurriculum` | 18 + 16 + 36 = 70 | 88 (36 + 16 + 36) | Yearly | `biep:v3:m2` | `ncca_registry_sensor` |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England (A-Level) | `dlt_sources/british_isles/england/education/england_jurisdiction_pipeline.py` | `ExtractUKQualSpec` | 49 | 147 (49 × 3 boards) | Yearly | `biep:v3:m3` | `jcq_registry_sensor` |
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England (GCSE) | (same) | `ExtractUKQualSpec` | 43 | 129 (43 × 3 boards) | Yearly | `biep:v3:m4` | `jcq_registry_sensor` |
| 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland | `dlt_sources/british_isles/scotland/education/scotland_jurisdiction_pipeline.py` | `ExtractScotlandSyllabus` | 50 | 150 (50 × 3 levels) | Yearly | `biep:v3:m5` | `sqa_registry_sensor` |
| 🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales | `dlt_sources/british_isles/wales/education/wales_jurisdiction_pipeline.py` | `ExtractWalesSyllabus` | 80 | 160 (80 × 2 levels) | Yearly | `biep:v3:m6` | `wjec_registry_sensor` |
| 🇬🇧 Northern Ireland | `dlt_sources/british_isles/northern_ireland/education/northern_ireland_jurisdiction_pipeline.py` | `ExtractNIExamPaper` | 35 | 70 (35 × 2 levels) | Yearly | `biep:v3:m7` | `ccea_registry_sensor` |
| 🇯🇪 Jersey | `dlt_sources/british_isles/jersey/education/jersey_jurisdiction_pipeline.py` | `ExtractJerseySyllabus` | 30 | 120 (30 × 4 levels) | Yearly | `biep:v3:m8` | `jersey_registry_sensor` |
| 🇬🇬 Guernsey | `dlt_sources/british_isles/guernsey/education/guernsey_jurisdiction_pipeline.py` | `ExtractGuernseySyllabus` | 30 | 120 (30 × 4 levels) | Yearly | `biep:v3:m9` | `guernsey_registry_sensor` |
| 🇮🇲 Isle of Man | `dlt_sources/british_isles/isle_of_man/education/isle_of_man_jurisdiction_pipeline.py` | `ExtractIsleOfManSyllabus` | 30 | 120 (30 × 4 levels) | Yearly | `biep:v3:m10` | `isle_of_man_registry_sensor` |

**Total: 12 + 88 + 147 + 129 + 150 + 160 + 70 + 120 + 120 + 120 = 1,116 cohorts**
across the 8 British Isles jurisdictions.

## 2 general-purpose scanner domains

| Scanner | DLT sources | Subjects | Cohorts | Cadence | Mise task | MotherDuck Flight |
|:--|:--|--:|--:|:--|:--|:--|
| filesystem | 11 canonical sources (leabharlann_books, gemini_deep_research, google_takeout, takeout_v1, email_inbox, leaving_cert_source, university_of_galway, zotero, gemini_corpus_source, pdf_download_source, previews) | n/a | n/a | Monthly | `biep:v3:filesystem:monthly:sync` | `filesystem_monthly_sync_flight` |
| language | 19 canonical sources (ainm, canuint, canuint_audio, canuint_dialect_summary, canuint_search, canuint_word_alignment, duchas, duchas_images, gaois, gaois_combined, heritage, hidden_heritages, local_documents_by_subject, local_education_documents, logainm, tearma, tearma_search, universal_dependencies) | n/a | n/a | Monthly | `biep:v3:language:monthly:sync` | `language_monthly_sync_flight` |

## Total BIEP v3 coverage

| Category | Count |
|:--|--:|
| 8 jurisdictions (10 milestones M0-M10) | 10 |
| 6 BAML Extract* functions (Scotland + Wales + NI + Jersey + Guernsey + IoM) | 6 |
| 2 scanner domains (filesystem + language) | 2 |
| M0 foundation assets + checks | 4 + 4 = 8 |
| Yearly per-jurisdiction assets (3 per jurisdiction × 10 = 30) + checks (3 × 10 = 30) | 30 + 30 = 60 |
| Monthly per-scanner assets (3 per scanner × 2 = 6) + checks (3 × 2 = 6) | 6 + 6 = 12 |
| Per-subject backfill jobs (49 + 84 + 35 + 30 + 30 + 30 + 11 + 18 = 287) | 287 |
| MotherDuck Dives (6 deferred + 2 scanner + 2 already-existing for Ireland + 4 already-existing for England = 14) | 14 |
| MotherDuck Flights (6 deferred + 2 scanner + 4 already-existing for Ireland/England = 12, but we count 8 BIEP v3 + 4 pre-existing) | 8 BIEP v3 + 4 pre-existing |
| Per-jurisdiction ChangeDetection.io monitors (3 already-existing for AQA/OCR/Edexcel + 6 needed for SCT/WLS/NI/Crown/IoM) | 3 + 6 = 9 |
| BAML functions (6 new + 8 existing + 3 board-specific + 1 generic) | 18 |
| CocoIndex v1 Apps (8 BIEP v3 Ireland + 88 JC + 2 parity + 147 A-Level + 129 GCSE + 6 v1 parity) | 380 |
| **Total Dagster assets** (M0 + yearly + monthly + checks) | 8 + 30 + 6 + 36 = 80 |
| **Total subjects seeded** (50 + 80 + 35 + 30 + 30 + 30 + 11 + 19 = 285) | 285 |

## See also

- `docs/agents/biiep-v3-systematic-download.md` — the canonical newcomer guide
- `docs/agents/biiep-v3-quickstart.md` — the "first 30 minutes" guide
- `docs/agents/biiep-v3-faq.md` — the canonical FAQ
- `docs/agents/biiep-v3-baml-client.md` — how to invoke the 6 new Extract* functions from Python
- `docs/agents/biiep-v3-storage-layout.md` — the DuckLake + Lance + MotherDuck layout
- `docs/agents/biiep-v3-cron-schedule.md` — the 4-cadence scheduling policy in detail
