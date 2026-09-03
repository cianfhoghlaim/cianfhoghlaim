# Round 11 Phase 3D — Split Multi-Source DLT Files Per Source

## Why

Phase 3C migrated single-source legacy files to canonical `dlt_sources/{nation}/{domain}/{entity}.py`. But ~13 legacy files contain **multiple** `@dlt.source` functions (e.g. `ireland/oide.py` has 4 sources, `uk/england/national_curriculum.py` has 5). For the canonical layout to be 1 source = 1 file, those multi-source files must be split per source first.

This is the middle slice of the 3C/3D/3E sequence:

- **3C (done)**: Single-source files — whole-file move
- **3D (this change)**: Multi-source files — split per source + migrate to canonical paths
- **3E (future)**: Delete the now-empty legacy trees

## What changes

### 1. IE multi-source files → `dlt_sources/ie/education/` (5 files → 16 sources)

| Legacy file | Sources | Splits into |
|:--|:--|:--|
| `dlt_sources/ireland/oide.py` | `oide_source`, `oide_subject_source`, `oide_gaeilge_source`, `oide_all_subjects_source` (4) | `ie/education/{oide, oide_subject, oide_gaeilge, oide_all_subjects}.py` + shared `_oide_helpers.py` |
| `dlt_sources/ireland/examinations.py` | `examinations_source`, `sec_examinations_browser_source`, `leaving_certificate_source`, `junior_cycle_exams_source`, `mathematics_exams_source`, `science_subjects_exams_source` (6) | `ie/education/{examinations, sec_examinations_browser, leaving_certificate, junior_cycle_exams, mathematics_exams, science_subjects_exams}.py` + shared `_examinations_helpers.py` |
| `dlt_sources/ireland/local_documents.py` | `local_education_documents_source`, `local_documents_by_subject_source` (2) | `ie/culture/{local_education_documents, local_documents_by_subject}.py` |
| `dlt_sources/ireland/agentic_discovery.py` | `agentic_discovery_source`, `deep_research_source` (2) | `ie/education/{agentic_discovery, deep_research}.py` |
| `dlt_sources/ireland/pdf_downloader.py` | `pdf_download_source`, `exam_pdf_download_source` (2) | `ie/education/{pdf_downloads, exam_pdf_downloads}.py` |

### 2. UK multi-source files → `dlt_sources/{en,ni,sct,wls}/education/` (4 files → 14 sources)

| Legacy file | Sources | Splits into |
|:--|:--|:--|
| `dlt_sources/uk/england/national_curriculum.py` | `national_curriculum_source`, `aqa_qualifications_source`, `edexcel_qualifications_source`, `ocr_qualifications_source`, `all_exam_boards_source` (5) | `en/education/{national_curriculum, aqa_qualifications, edexcel_qualifications, ocr_qualifications, all_exam_boards}.py` |
| `dlt_sources/uk/northern_ireland/ccea_curriculum.py` | `ni_curriculum_source`, `ccea_qualifications_source`, `irish_medium_ni_source` (3) | `ni/education/{ni_curriculum, ccea_qualifications, irish_medium_ni}.py` |
| `dlt_sources/uk/scotland/curriculum_for_excellence.py` | `curriculum_for_excellence_source`, `sqa_qualifications_source`, `gaelic_curriculum_source` (3) | `sct/education/{curriculum_for_excellence, sqa_qualifications, gaelic_curriculum}.py` |
| `dlt_sources/uk/wales/curriculum_for_wales.py` | `curriculum_for_wales_source`, `wjec_qualifications_source`, `welsh_medium_source` (3) | `wls/education/{curriculum_for_wales, wjec_qualifications, welsh_medium}.py` |

### 3. Celtic multi-source files → `dlt_sources/ie/culture/` (3 files → 11 sources)

| Legacy file | Sources | Splits into |
|:--|:--|:--|
| `dlt_sources/celtic/canuint.py` | `canuint_source`, `canuint_search_source`, `canuint_audio_source`, `canuint_dialect_summary_source`, `canuint_word_alignment_source` (5) | `ie/culture/canuint/{pronunciation, search, audio_download, dialect_summary, word_alignment}.py` |
| `dlt_sources/celtic/duchas_images.py` | `duchas_images_source`, `hidden_heritages_source` (2) | `ie/culture/{duchas_images, hidden_heritages}.py` |
| `dlt_sources/celtic/gaois.py` | `logainm_source`, `tearma_source`, `ainm_source`, `gaois_combined_source` (4) | `ie/culture/{logainm, tearma, ainm, gaois_combined}.py` |

### 4. Geospatial multi-source files → `dlt_sources/ie/statistics/` (3 files → 7 sources)

| Legacy file | Sources | Splits into |
|:--|:--|:--|
| `dlt_sources/geospatial/met_office.py` | `met_office_source`, `met_office_forecast_source` (2) | `ie/statistics/{met_office, met_office_forecast}.py` |
| `dlt_sources/geospatial/cso_small_areas.py` | `cso_small_areas_source`, `cso_education_source`, `cso_deprivation_source` (3) | `ie/statistics/{cso_small_areas, cso_education, cso_deprivation}.py` |
| `dlt_sources/geospatial/geohive.py` | `geohive_source`, `geohive_deprivation_source` (2) | `ie/statistics/{geohive, geohive_deprivation}.py` |

### 5. bunchloch multi-source file → `dlt_sources/cross/bunchloch/` (1 file → 2 sources)

| Legacy file | Sources | Splits into |
|:--|:--|:--|
| `dlt_sources/bunchloch/filesystem_source.py` | `bunchloch_source`, `bunchloch_by_subject_source` (2) | `cross/bunchloch/{filesystem, filesystem_by_subject}.py` |

### 6. Shared helper extraction

Multi-source files contain shared private helpers (e.g. `_crawl_oide_section`, `_crawl_oide_subject`, `OIDE_URLS` constants). These are extracted into private `_helpers.py` modules alongside the split source files:

- `dlt_sources/ie/education/_oide_helpers.py` (shared by oide/oide_subject/oide_gaeilge/oide_all_subjects)
- `dlt_sources/ie/education/_examinations_helpers.py` (shared by all 6 examinations sources)
- `dlt_sources/ie/statistics/_met_office_helpers.py` (if applicable)
- `dlt_sources/ie/statistics/_cso_helpers.py` (if applicable)
- `dlt_sources/ie/culture/canuint/_canuint_helpers.py` (if applicable)
- `dlt_sources/ie/culture/_gaois_helpers.py` (if applicable)

### 7. Importer updates

All files importing the legacy multi-source modules get their imports rewritten:
- `from dlt_sources.ireland.oide import oide_source` → `from dlt_sources.ie.education.oide import oide_source`
- etc.

## Impact

- 13 legacy files → ~50 new canonical files
- ~25 importer sites updated across dagster_defs/, tests/, scripts/, notebooks/, dlt_utils/
- 0 net LOC change (pure relocation)
- openspec delta: ADDED `Country-First Layout — Multi-Source Split` Requirement

## Risk

- HIGH: Per-source splitting is the most invasive part of the migration. Each `@dlt.source` function and its nested `@dlt.resource` functions must be extracted intact with all decorators and indentation
- Shared helper functions must be identified and extracted to shared helper modules — easy to miss one
- Some sources have nested `@dlt.resource` functions that need to move with their parent source
- Intra-legacy-tree imports (e.g. `oide_subject_source` calling `_crawl_oide_section`) need to be rewired to import from the new helper module

## Out of scope (deferred)

- **Phase 3E**: Delete the now-empty legacy trees `dlt_sources/{ireland,uk,crown_dependencies,celtic,bunchloch,geospatial,official_media}/`
- **official_media/ subtree**: complex (15+ files including fixtures, tests, allowlists); deferred to a future change
- **celtic/teanglann.ie/ + celtic/focloir.ie/**: data directories (no .py files); deferred