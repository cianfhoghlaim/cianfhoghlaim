# Round 11 Phase 3C — Migrate Legacy Single-Source DLT Files to Canonical Country-First Layout

## Why

After Phase 3B dropped the `dlt_sources/domains/` wrapper, the canonical layout is
`dlt_sources/{nation}/{domain}/{entity}.py`. But ~22 legacy flat-tree files in
`dlt_sources/ireland/*.py` + ~10 files in `dlt_sources/uk/{england,northern_ireland,scotland,wales}/*.py`
+ 2 files in `dlt_sources/celtic/*.py` + 4 utility files in `dlt_sources/ireland/*.py` still use
the legacy flat layout. Phase 3C migrates these single-source files to the canonical path.

This is the middle slice of the 3C/3D/3E sequence:

- **3C (this change)**: Single-source files. Whole-file move.
- **3D (future)**: Multi-source files (e.g. `ireland/oide.py` with 4 `@dlt.source` defs, `uk/england/national_curriculum.py` with 5 sources). Split per source first, then move.
- **3E (future)**: Delete the now-empty legacy trees `dlt_sources/{ireland,uk,crown_dependencies,celtic,bunchloch,geospatial,official_media}/`.

## What changes

### 1. Single-source IE education files → `dlt_sources/ie/education/`

| Source | Destination |
|:--|:--|
| `dlt_sources/ireland/aistear.py` | `dlt_sources/ie/education/aistear.py` |
| `dlt_sources/ireland/curriculum_source.py` | `dlt_sources/ie/education/curriculum_source.py` |
| `dlt_sources/ireland/junior_cycle.py` | `dlt_sources/ie/education/junior_cycle.py` |
| `dlt_sources/ireland/leaving_cert.py` | `dlt_sources/ie/education/leaving_cert.py` |
| `dlt_sources/ireland/ncca.py` | `dlt_sources/ie/education/ncca.py` |
| `dlt_sources/ireland/primary.py` | `dlt_sources/ie/education/primary.py` |
| `dlt_sources/ireland/senior_cycle.py` | `dlt_sources/ie/education/senior_cycle.py` |
| `dlt_sources/ireland/tertiary.py` | `dlt_sources/ie/education/tertiary.py` |
| `dlt_sources/ireland/sec_aural_transcripts.py` | `dlt_sources/ie/education/sec_aural_transcripts.py` |
| `dlt_sources/ireland/edcolearning.py` | `dlt_sources/ie/education/edcolearning.py` |

### 2. Single-source UK education files → `dlt_sources/{en,ni,sct,wls}/education/`

| Source | Destination |
|:--|:--|
| `dlt_sources/uk/england/ofsted.py` | `dlt_sources/en/education/ofsted.py` |
| `dlt_sources/uk/england/school_info.py` | `dlt_sources/en/education/school_info.py` |
| `dlt_sources/uk/northern_ireland/education_ni.py` | `dlt_sources/ni/education/education_ni.py` |
| `dlt_sources/uk/northern_ireland/etini.py` | `dlt_sources/ni/education/etini.py` |
| `dlt_sources/uk/scotland/insight_benchmarking.py` | `dlt_sources/sct/education/insight_benchmarking.py` |

### 3. Single-source UK statistics files → `dlt_sources/{en,ni,sct,wls}/statistics/`

| Source | Destination |
|:--|:--|
| `dlt_sources/uk/england/dfe_explore_statistics.py` | `dlt_sources/en/statistics/dfe_explore_statistics.py` |
| `dlt_sources/uk/northern_ireland/nisra.py` | `dlt_sources/ni/statistics/nisra.py` |
| `dlt_sources/uk/scotland/gov_scot_statistics.py` | `dlt_sources/sct/statistics/gov_scot_statistics.py` |
| `dlt_sources/uk/scotland/simd.py` | `dlt_sources/sct/statistics/simd.py` |
| `dlt_sources/uk/wales/statswales.py` | `dlt_sources/wls/statistics/statswales.py` |
| `dlt_sources/uk/wales/estyn.py` | `dlt_sources/wls/education/estyn.py` |

### 4. Single-source Celtic files → `dlt_sources/ie/{culture,education}/`

| Source | Destination |
|:--|:--|
| `dlt_sources/celtic/duchas.py` | `dlt_sources/ie/culture/duchas.py` |
| `dlt_sources/celtic/universal_dependencies.py` | `dlt_sources/ie/education/universal_dependencies.py` |

### 5. Shared utilities → `dlt_sources/common/`

| Source | Destination |
|:--|:--|
| `dlt_sources/ireland/source_adapters.py` | `dlt_sources/common/source_adapters.py` |
| `dlt_sources/ireland/curriculum_registry.py` | `dlt_sources/common/curriculum_registry.py` |
| `dlt_sources/ireland/content_deduplication.py` | `dlt_sources/common/content_deduplication.py` |
| `dlt_sources/ireland/json_seed.py` | `dlt_sources/ie/education/json_seed.py` |
| `dlt_sources/ireland/parallel_corpus.py` | `dlt_sources/ie/education/parallel_corpus.py` |
| `dlt_sources/ireland/exam_source_update.py` | `dlt_sources/ie/education/exam_source_update.py` |

### 6. Ireland subjects/ sub-package → `dlt_sources/ie/education/subjects/`

| Source | Destination |
|:--|:--|
| `dlt_sources/ireland/subjects/__init__.py` | `dlt_sources/ie/education/subjects/__init__.py` |
| `dlt_sources/ireland/subjects/base.py` | `dlt_sources/ie/education/subjects/base.py` |
| `dlt_sources/ireland/subjects/junior_cycle.py` | `dlt_sources/ie/education/subjects/junior_cycle.py` |
| `dlt_sources/ireland/subjects/senior_cycle.py` | `dlt_sources/ie/education/subjects/senior_cycle.py` |

### 7. Importer updates

All files that import from `dlt_sources.ireland.X`, `dlt_sources.uk.X`, or `dlt_sources.celtic.X` will have their imports rewritten to the canonical paths.

## Impact

- 35 files moved
- ~15 importer files updated
- 0 net LOC change (pure relocation)
- openspec delta: ADDED `Country-First Layout — Single-Source Migration` Requirement

## Risk

- MEDIUM: many importer sites (15+ files in dlt_sources/, dagster_defs/, tests/) need rewriting
- Single-source files are whole-file moves (lower risk than splitting)
- The 6 utility files (`source_adapters`, `curriculum_registry`, etc.) are imported by other legacy files that stay in `dlt_sources/ireland/` until 3D/3E — those intra-tree imports will break and need updating too
- Pre-existing `dlt_sources/ireland/__init__.py` re-exports many of these modules — must update its imports too

## Out of scope (deferred)

- **Phase 3D**: Multi-source files (ireland/oide.py, ireland/examinations.py, ireland/local_documents.py, ireland/agentic_discovery.py, ireland/pdf_downloader.py, uk/*/*curriculum*.py, geospatial/met_office.py, geospatial/cso_small_areas.py, geospatial/geohive.py, bunchloch/filesystem_source.py, celtic/canuint.py, celtic/duchas_images.py, celtic/gaois.py)
- **Phase 3E**: Delete legacy trees after 3D
- **official_media/ subtree**: complex (15+ files including fixtures, tests, allowlists, fediverse integration); deferred to a future change
- **celtic/teanglann.ie/ + celtic/focloir.ie/**: data directories (no .py files); deferred
- **crown_dependencies/**: empty directories; will be deleted as part of 3E