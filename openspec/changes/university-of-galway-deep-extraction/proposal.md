# University of Galway Deep Extraction (case study + reusable template)

## Why

The user has 3 University of Galway degrees on their academic record (B.Sc. Mathematics & Education, H.Dip Software Design & Development, in-progress M.Sc. AI 2025-26) and wants the M.Sc. AI 25/26 handbook as the seed case study. The existing `ie.university.galway` source (line 560 of `cianfhoghlaim/sources/_oideachais_sources.yaml`) is registered under `kind: firecrawl_pages` with a generic `/about-us`, `/news`, `/careers` crawl — it does **not** extract course codes, module descriptors, lecturers, or reading lists. The Gemini deep research on Galway psychiatry modules is a separate cross-archive data point the user wants to ground in the official UoG course handbooks.

The change closes three gaps:

1. **No deep university extractor exists.** The leabharlann pipeline has 6 DLT sources + 4 v1 CocoIndex Apps, but none target *course catalogues* or *module handbooks*. The new capability fills this gap with a reusable factory.
2. **No BAML schema for course / module / programme descriptors exists.** `author_archive.baml` has `ExtractUoGArtifact` (the personal-archive side) but nothing for the *website* side. The change adds 4 typed extraction functions and 4 classes.
3. **No cross-archive edge from personal archive to current course offerings.** The user wants to see "the cryptography assignment I did in 2018 maps to CT511 in 2025 and to the new M.Sc. AI module CTXXX in 2026". The new edge `UoGArtifact-MATCHES-CourseDescriptor` (matched by `course_code` + fuzzy title) makes this possible.

The change also doubles as the **template** for the next 5+ university additions (Maynooth, TCD, UCD, Limerick, QUB, etc.) — the only per-university work will be editing `sources.yaml` (no new code).

## What Changes

### 1. New BAML file `cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml`

5 BAML classes + 4 BAML functions + 4 deterministic tests:

- `class CourseDescriptor` — `course_code`, `course_title`, `nfq_level`, `school`, `stage`, `ects`, `description`, `source_url`, `confidence`
- `class ModuleDescriptor` — `module_code`, `module_title`, `ects`, `semester`, `programme_codes[]`, `learning_outcomes[]`, `assessment_breakdown{}`, `prerequisite_modules[]`, `lecturers[]`, `recommended_reading[]`, `source_url`, `confidence`
- `class ProgrammeDescriptor` — `programme_code`, `programme_title`, `nfq_level`, `school`, `duration_months`, `mode`, `modules[]`, `total_ects`, `source_url`, `confidence`
- `class LecturerInfo` — `name`, `email?`, `school`, `profile_url?`
- `class ReadingListItem` — `format` (ISBN_13 | DOI | URL), `title`, `authors[]`, `year?`, `isbn_13?`, `doi?`, `url?`
- `function ExtractCourseDescriptor(course_page_markdown, course_url) -> CourseDescriptor`
- `function ExtractModuleDescriptor(module_page_markdown, module_url) -> ModuleDescriptor`
- `function ExtractProgrammeDescriptor(programme_page_markdown, programme_url) -> ProgrammeDescriptor`
- `function ExtractReadingList(module_page_markdown, module_url) -> ReadingListItem[]`

All 4 functions route through the canonical `ExtractEn` LiteLLM client (per the `oideachais-baml-schemas` spec). 4 deterministic tests in the BAML file cover the M.Sc. AI 25/26 happy path, ISBN-13 regex, programme ECTS sum, and the cross-failure (no LLM) fallback.

### 2. New DLT factory `_university_deep_factory.py`

`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/_university_deep_factory.py` — the **reusable factory**:

- `class UniversityDeepExtractionConfig` (Pydantic v2) — `university_id`, `institution_name`, `base_url`, `catalogue_paths[]`, `school_subdomain_paths[]`, `handbook_root_path`, `academic_year`, `programme_code_regex`, `ects_field_label`, `prefer_free_browser`
- `def create_university_deep_extraction_source(config) -> dlt.Source` — returns a `@dlt.source(name=f"university_{config.university_id}_deep")` with 5 resources: `course_pages`, `module_pages`, `programme_pages`, `handbook_pdfs`, `lecturer_pages`. Each resource wraps the existing `BackendRouter.bulk_scrape` (Crawl4AI primary, Firecrawl paid fallback) per the 3-stage pattern in `author-archive-pipeline`.

### 3. New DLT source `university_of_galway_deep.py`

`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/university_of_galway_deep.py` — the **case-study** source. Calls the factory with the UoG config:

- `base_url = "https://www.universityofgalway.ie"`
- `catalogue_paths = ["/courses/**", "/programmes/**"]`
- `school_subdomain_paths = ["/colleges/science-engineering/**", "/schools/computer-science/**", "/schools/mathematical-science/**", "/schools/education/**"]`
- `handbook_root_path = "/handbooks/2025-26/"`
- `academic_year = 2025`
- `programme_code_regex = "[A-Z]{2,4}\\d{3,4}"`

### 4. Updated `cianfhoghlaim/sources/_oideachais_sources.yaml`

Line 560-568 — update `ie.university.galway`:

- `kind: firecrawl_pages` → `kind: university_deep_extraction`
- Replace the `crawl: { include_paths: ["/about-us/**", ...] }` block with the new `catalogue_paths` + `school_subdomain_paths` + `handbook_root_path` fields consumed by the factory
- Bump `asset_key` from `[ie, official_media, university, galway, pages]` to `[ie, education, university, galway, deep]`

The 23 other British Isles university sources (Maynooth, TCD, UCD, Limerick, QUB, etc.) are **NOT** modified in this change — they get the same template treatment in future follow-up changes.

### 5. Updated `source_factory.py` dispatch table

`cianfhoghlaim/core/dlt/_oideachais_dlt_utils/source_factory.py` — add `kind: university_deep_extraction` to the dispatch table, mapping to `_build_university_deep_source(config_dict)`.

### 6. 5 new Dagster assets `university_deep_extraction/uog_assets.py`

`cianfhoghlaim/assets/_oideachais_dagster_defs/assets/university_deep_extraction/__init__.py` + `uog_assets.py`:

- `uog_pre_research` (group `university_deep_extraction`, compute_kind `scrape`) — 3-stage pre-research
- `uog_bulk_scrape` (group `university_deep_extraction`, compute_kind `scrape`) — bulk scrape with Crawl4AI primary
- `uog_extract_courses` (group `university_deep_extraction`, compute_kind `baml`) — `b.ExtractCourseDescriptor` per row, persisted to `oideachais.education.ie.university_courses`
- `uog_extract_modules` (group `university_deep_extraction`, compute_kind `baml`) — `b.ExtractModuleDescriptor` per row → `oideachais.education.ie.university_modules`
- `uog_extract_programmes` (group `university_deep_extraction`, compute_kind `baml`) — `b.ExtractProgrammeDescriptor` per row → `oideachais.education.ie.university_programmes`

BAML calls are memoised on `(url, content_hash)` (the same pattern used by `university_of_galway_source` in `leabharlann/`).

### 7. 2 new CocoIndex v1 Apps `university_embedding.py`

`cianfhoghlaim/core/cocoindex/university_embedding.py`:

- `UniversityCoursesApp` (BGE-M3 1024-dim embedding on `course_description + learning_outcomes`) → `university_courses` LanceDB table
- `UniversityModulesApp` (BGE-M3 1024-dim embedding on `module_title + module_description + learning_outcomes`) → `university_modules` LanceDB table

Both follow the canonical v1 pattern (per `oideachais-cocoindex-v1-migration` spec): `@coco.lifespan` + `@coco.fn` + `lancedb.mount_table_target` + `SentenceTransformerEmbedder("BAAI/bge-m3")`. Both respect the 100-batch minimum + `HNSW-DROP-THRESHOLD=50` rule. Brings the total v1 App count from 11 to 13.

### 8. 1 new Cognee cross-archive edge `university_cross_archive.py`

`cianfhoghlaim/cognify/rules/university_cross_archive.py` + registered in `leabharlann_cross_archive.py`:

- **Edge type**: `UoGArtifact-MATCHES-CourseDescriptor`
- **Left node**: `author_archive_uog_artifact` (the user's personal-archive artefacts from `leabharlann/ollscoil_na_gaillimhe/`)
- **Right node**: `university_course_descriptor` (the scraped course descriptors)
- **Match condition**: `(left.course_code = right.programme_code) OR (fuzzy_title_similarity(left.module_title, right.course_title) > 0.85)`
- **Match confidence**: stored as an edge property `match_confidence ∈ [0.0, 1.0]`

### 9. 1 new Marimo notebook `university_courses.py`

`cianfhoghlaim/notebooks/_oideachais/university_courses.py` — mounted at `/dashboards/university-courses` with 4 tabs:

1. **M.Sc. AI 25/26 modules** (the primary use case) — pre-filtered to `programme_codes = ["MSCAI"]` and `academic_year = 2025`
2. **All UoG courses** — searchable + filterable by school, NFQ level, ECTS, programme stage
3. **Reading lists** — every reading-list item, with "Group by module" + "Group by ISBN-13" toggles
4. **Cross-archive** — the user's `leabharlann/ollscoil_na_gaillimhe/` artefacts joined to the matching scraped `CourseDescriptor` rows via the new Cognee edge

The notebook uses `mo.sql(engine=md:oideachais)` (the MotherDuck Postgres endpoint) for the underlying queries.

### 10. 1 new docs page `university-deep-extraction.md`

`cianfhoghlaim/docs/04-data-platform/university-deep-extraction.md` — the **template tutorial** showing how to add a new British Isles university in 5 lines of `sources.yaml` (per the `data-engineering-pipeline-documentation` spec).

### 11. Updated capability tables

- `openspec/AGENTS.md` — add the new `oideachais-university-deep-extraction` row to the priority specs table
- `openspec/project.md` — add the new capability row to the Cianfhoghlaim core group

## Impact

| Surface | Before | After |
|:--|:--|:--|
| `cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml` | (absent) | New — 5 BAML classes + 4 functions + 4 tests |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/_university_deep_factory.py` | (absent) | New — factory + Pydantic config |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/university_of_galway_deep.py` | (absent) | New — case-study source with 5 resources |
| `cianfhoghlaim/sources/_oideachais_sources.yaml` (line 560-568) | `kind: firecrawl_pages`, generic crawl paths | `kind: university_deep_extraction`, 2 URL surfaces + handbook root |
| `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/source_factory.py` | 7 kinds dispatched | 8 kinds dispatched |
| `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/university_deep_extraction/` | (absent) | New — 5 assets |
| `cianfhoghlaim/core/cocoindex/university_embedding.py` | (absent) | New — 2 v1 Apps |
| `cianfhoghlaim/cognify/rules/university_cross_archive.py` | (absent) | New — 1 cross-archive rule |
| `cianfhoghlaim/notebooks/_oideachais/university_courses.py` | (absent) | New — 4-tab marimo notebook |
| `cianfhoghlaim/docs/04-data-platform/university-deep-extraction.md` | (absent) | New — template tutorial |
| v1 CocoIndex Apps | 11 | 13 (+ `UniversityCoursesApp`, `UniversityModulesApp`) |
| Cognee cross-archive rules | 3 | 4 (+ `UoGArtifact-MATCHES-CourseDescriptor`) |
| Marimo notebooks | 11 | 12 (+ `university_courses.py`) |
| BAML extraction functions invoked | 9 of 12 | 13 of 16 |
| Test files | 26 | 27 (+ `test_university_deep_extraction.py`) |

## Out of scope

- The 23 other British Isles university sources (Maynooth, TCD, UCD, Limerick, QUB, etc.) — each becomes a 5-line follow-up change flipping their `kind` and adding the per-university config.
- A separate `official_media` university source — the existing `ie.university.galway` entry under `official_media` is replaced (not duplicated) by the new `kind: university_deep_extraction` entry.
- Bilingual Irish (Gaeilge) course extraction — deferred; this change is English-only. A future `university-bilingual-extraction` change can add a parallel `ExtractModuleDescriptorGa` function.
- Cognee cognify of the scraped course descriptors themselves (the `university_courses` / `university_modules` / `university_programmes` DuckLake tables are not yet cognified into the knowledge graph) — separate `university-cognify-knowledge-graph` change.
- A marimo notebook **per university** — this change ships 1 notebook (the UoG one). Per-university notebooks are a follow-up.

## Cross-references

- `openspec/specs/oideachais-pipeline/spec.md` — the canonical curriculum-pipeline spec (asset key conventions, BAML conventions, DuckLake conventions)
- `openspec/specs/oideachais-leabharlann/spec.md` — the leabharlann pipeline (the personal-archive side this change joins to)
- `openspec/specs/author-archive-pipeline/spec.md` — the 3-stage pre-research → bulk-scrape → condense pattern
- `openspec/specs/author-archive-web-scraping/spec.md` — the browser BackendRouter (Crawl4AI primary, Firecrawl fallback, CreditBudget)
- `openspec/specs/oideachais-baml-schemas/spec.md` — BAML conventions + the 4 deterministic-eval pattern (extended with 3 new evals in this change)
- `openspec/specs/oideachais-cocoindex-v1-migration/spec.md` — the canonical v1 App pattern
- `openspec/specs/oideachais-marimo-dashboards/spec.md` — the marimo notebook conventions
- `.agents/skills/browser-tools/SKILL.md` — the 5-backend browser router
- `.agents/skills/firecrawl-build/SKILL.md` — the Firecrawl integration pattern
- `.agents/skills/oideachais-leabharlann/SKILL.md` — the leabharlann pipeline pattern (the template this change extends)
- `.agents/skills/dagster/SKILL.md` — the Dagster asset + sensor pattern
- `.agents/skills/cocoindex/SKILL.md` — the v1 CocoIndex App pattern
- `docs/06-infrastructure/leabharlann-stack-overview.md` — the stack diagram (will be updated to include the new source group)
- `docs/04-data-platform/university-deep-extraction.md` — the **new** template tutorial (how to add a university in 5 lines)
