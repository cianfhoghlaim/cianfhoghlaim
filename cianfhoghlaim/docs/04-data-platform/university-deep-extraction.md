# University Deep Extraction

## Purpose for the Cianfhoghlaim project

The `oideachais-university-deep-extraction` capability turns a single
British Isles university website (case study: University of Galway)
into a structured lakehouse of course descriptors, module
descriptors, programme descriptors, reading lists, and lecturer
information. The BAML extraction is reusable; the per-university
configuration is a 5-line `sources.yaml` entry.

## What the user can do

After the change lands, the user can:

1. **Open `/dashboards/university-courses`** in their browser, click
   the "M.Sc. AI 25/26" tab, and see all 12+ modules in the M.Sc. AI
   2025-26 programme with module codes, ECTS, semesters, lecturers,
   assessment breakdowns, and recommended reading.
2. **Switch to the "Cross-archive" tab** and see their past UoG
   assignments (`CT511`, `MA335`, `ED305`, etc.) joined to the
   matching scraped `CourseDescriptor` rows — answering the question
   "how does my B.Sc. Mathematics & Education and H.Dip Software Design
   & Development connect to my upcoming M.Sc. AI?"
3. **Click "Group by ISBN-13"** on the Reading lists tab to see
   which books appear across multiple M.Sc. AI modules.
4. **Add 23 more British Isles universities in 5-line follow-up
   changes** — Maynooth, TCD, UCD, Limerick, QUB, etc. are already
   registered in `sources.yaml`; each becomes a 5-line change
   flipping `kind: firecrawl_pages` to `kind: university_deep_extraction`
   plus the per-university config block.

## How to add a new university (5 lines)

Append the following to
`cianfhoghlaim/sources/_oideachais_sources.yaml`:

```yaml
  - id: ie.university.maynooth
    name: "Maynooth University"
    domain: education
    nation: ie
    kind: university_deep_extraction
    base_url: "https://www.maynoothuniversity.ie"
    catalogue_paths: ["/study/**"]
    school_subdomain_paths: ["/departments/**"]
    handbook_root_path: "/handbooks/2025-26/"
    academic_year: 2025
    asset_key: [ie, education, university, maynooth, deep]
```

That's it. The SourceFactory picks up the new entry on the next load
and the factory creates a working DLT source with 5 resources
(`course_pages`, `module_pages`, `programme_pages`, `handbook_pdfs`,
`lecturer_pages`). **No new Python code required.**

## The 5 resources (per university DLT source)

| Resource | Source surface | Output BAML function |
|:--|:--|:--|
| `course_pages` | `catalogue_paths` (e.g. `/courses/**`) | `ExtractCourseDescriptor` |
| `module_pages` | `school_subdomain_paths` (e.g. `/schools/computer-science/**`) | `ExtractModuleDescriptor` |
| `programme_pages` | `catalogue_paths` (re-tagged) | `ExtractProgrammeDescriptor` |
| `handbook_pdfs` | `handbook_root_path` (e.g. `/handbooks/2025-26/`) | `ExtractReadingList` |
| `lecturer_pages` | `school_subdomain_paths` (re-tagged, `/people` suffix) | (extracted from page markdown) |

## The 5 Dagster assets (per university)

1. `uog_pre_research` — `BackendRouter.pre_research` (1 credit, free fallback)
2. `uog_bulk_scrape` — `BackendRouter.bulk_scrape` (Crawl4AI primary, Firecrawl paid fallback)
3. `uog_extract_courses` — BAML `ExtractCourseDescriptor` → `oideachais.education.ie.university_courses`
4. `uog_extract_modules` — BAML `ExtractModuleDescriptor` → `oideachais.education.ie.university_modules`
5. `uog_extract_programmes` — BAML `ExtractProgrammeDescriptor` → `oideachais.education.ie.university_programmes`

All 5 assets live in the `university_deep_extraction` asset group.

## Anti-patterns

1. **Do NOT** hard-code the per-university config in Python. The
   `UniversityDeepExtractionConfig` Pydantic model is the only
   blessed source of truth; per-university overrides go in
   `sources.yaml`.
2. **Do NOT** add new BAML classes to the v1 schema. The 5 classes
   (`CourseDescriptor`, `ModuleDescriptor`, `ProgrammeDescriptor`,
   `LecturerInfo`, `ReadingListItem`) are the canonical surface; new
   fields go in a follow-up openspec change.
3. **Do NOT** write to DuckLake directly. The Dagster assets route
   through dlt's `pipeline.run(source)`; the table name is derived
   from the `oideachais.{domain}.{nation}.{entity}` convention.
4. **Do NOT** set `prefer_free_browser=False` to force Firecrawl.
   The 3-stage pipeline prefers Crawl4AI (free) and only falls back
   to Firecrawl when the page is heavy-JS or when the pre-research
   flags `firecrawl-agent`. Setting `prefer_free_browser=False` will
   burn Firecrawl credits unnecessarily.
5. **Do NOT** commit a 2nd entry to `sources.yaml` for the same
   university. The `SourceEntry.id` validator requires the form
   `{nation}.{domain}.{entity}`; duplicate ids raise `ValueError`.

## Cross-references

- **OpenSpec change**: `openspec/changes/university-of-galway-deep-extraction/`
  (proposal + tasks + 5 spec deltas + canonical spec)
- **Canonical spec**: `openspec/specs/oideachais-university-deep-extraction/spec.md`
- **BAML**: `cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml`
  (5 classes + 4 functions + 4 deterministic tests)
- **DLT factory**: `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/_university_deep_factory.py`
- **DLT case study**: `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/university_of_galway_deep.py`
- **Dagster assets**: `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/university_deep_extraction/`
- **CocoIndex v1 Apps**: `cianfhoghlaim/embeddings/_oideachais_src/university_embedding.py`
- **Cross-archive rule**: `cianfhoghlaim/cognify/rules/university_cross_archive.py`
- **Marimo notebook**: `cianfhoghlaim/notebooks/_oideachais/university_courses.py`
  (mounted at `/dashboards/university-courses`)
- **Modified specs**: `oideachais-baml-schemas`, `oideachais-leabharlann`,
  `oideachais-marimo-dashboards`, `oideachais-cocoindex-v1-migration`
- **Test file**: `cianfhoghlaim/tests/_oideachais/test_university_deep_extraction.py`
  (31 tests covering the full pipeline)
- **Related**: `author-archive-pipeline` spec (the 3-stage pattern),
  `oideachais-pipeline` spec (asset key + DuckLake conventions),
  `browser-tools` skill (the 5-backend router)

## Tags

- `domain:education`
- `tier:data-platform`
- `surface:lakehouse`
- `pipeline:baml-dlt-dagster-cocoindex-cognee-marimo`
- `template:true` (reusable for any British Isles university)
