# oideachais-university-deep-extraction Specification

## Purpose

`oideachais-university-deep-extraction` is a capability of the Cianfhoghlaim
platform that turns a single British Isles university website (case study:
University of Galway) into a structured lakehouse of course descriptors,
module descriptors, programme descriptors, reading lists, and lecturer
information. The corresponding source code lives at:

- BAML: `cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml`
- DLT factory: `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/_university_deep_factory.py`
- DLT source (Galway): `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/university_of_galway_deep.py`
- Dagster assets: `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/university_deep_extraction/`
- CocoIndex v1 Apps: `cianfhoghlaim/core/cocoindex/university_embedding.py`
- Marimo notebook: `cianfhoghlaim/notebooks/_oideachais/university_courses.py`
- Cross-archive edge: `cianfhoghlaim/cognify/rules/university_cross_archive.py`

See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

## Background

The British Isles tertiary education data is currently scraped only at the
generic-official-media level (one BAML `CondenseToCriticalInfo` call per
page; 24 universities registered in `cianfhoghlaim/sources/_oideachais_sources.yaml`
under `kind: firecrawl_pages`, with `/about-us`/`/news`/`/careers` paths).
That pattern yields only the surface-level institutional content; it does
**not** produce structured course / module / programme / reading-list
data suitable for academic analysis.

The new capability adds 5 BAML classes + 4 BAML extraction functions, a
reusable factory function + per-university config schema, a single Galway
DLT source (as the case study + template), 5 Dagster assets, 2 CocoIndex
v1 Apps, 1 marimo notebook, and 1 Cognee cross-archive edge. Subsequent
British Isles universities (Maynooth, TCD, UCD, Limerick, QUB, etc.) are
added in 5-line follow-up changes by editing `sources.yaml` only.

## ADDED Requirements

### Requirement: Per-university config schema

The system SHALL provide a `UniversityDeepExtractionConfig` Pydantic v2
model at `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/_university_deep_factory.py`
that captures the per-university configuration a DLT source needs:

- `university_id` (string, kebab-case, e.g. `"ie-university-galway"`)
- `institution_name` (string, e.g. `"University of Galway"`)
- `base_url` (HttpUrl, e.g. `"https://www.universityofgalway.ie"`)
- `catalogue_paths` (list of glob patterns, e.g. `["/courses/**", "/programmes/**"]`)
- `school_subdomain_paths` (list of glob patterns, e.g. `["/colleges/science-engineering/**", "/schools/computer-science/**"]`)
- `handbook_root_path` (string, e.g. `"/handbooks/current/"`)
- `academic_year` (int, e.g. `2025`)
- `programme_code_regex` (string, e.g. `"[A-Z]{2,4}\\d{3,4}"` to match `MA335`, `CT511`)
- `ects_field_label` (string, e.g. `"ECTS"`)
- `prefer_free_browser` (bool, default `True`)

The factory function `create_university_deep_extraction_source(config: UniversityDeepExtractionConfig) -> dlt.Source`
SHALL return a `@dlt.source(name=f"university_{config.university_id}_deep")`
with 5 resources: `course_pages`, `module_pages`, `programme_pages`, `handbook_pdfs`, `lecturer_pages`.

#### Scenario: A new university is added in 5 lines of `sources.yaml`

- **GIVEN** a developer appends the following to `cianfhoghlaim/sources/_oideachais_sources.yaml`:
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
- **WHEN** the `SourceFactory` is loaded
- **THEN** the new `ie.university.maynooth` source is registered
- **AND** `create_university_deep_extraction_source()` returns a working DLT source
- **AND** `maynooth_university_deep_source()` is callable from any Dagster asset
- **AND** the developer did NOT need to write any new Python code

#### Scenario: Invalid config is rejected at load time

- **WHEN** a developer commits a `sources.yaml` entry with `kind: university_deep_extraction` and a missing required field (e.g. `handbook_root_path`)
- **THEN** the `SourceFactory` SHALL raise `ValueError` with a clear message pointing at the missing field
- **AND** the error SHALL be surfaced in the marimo `university_courses.py` notebook's "Config health" panel

### Requirement: Two URL surfaces per university

The DLT source SHALL crawl two distinct URL surfaces per university:

1. **Catalogue pages** (`config.catalogue_paths`) — the top-level course catalogue (`/courses/**`, `/programmes/**`). Yields `course_pages` and `programme_pages` resources.
2. **School subdomain pages** (`config.school_subdomain_paths`) — the per-school course lists, e.g. Computer Science, Mathematical Science, College of Science & Engineering. Yields `module_pages` and `lecturer_pages` resources.

The `handbook_pdfs` resource SHALL scrape `config.handbook_root_path` for academic-year-specific handbook PDFs (e.g. M.Sc. AI 25/26).

#### Scenario: M.Sc. AI 25/26 handbook is found

- **GIVEN** the `uog_bulk_scrape` Dagster asset runs with `academic_year=2025`
- **WHEN** the `handbook_pdfs` resource is materialised
- **THEN** the resource SHALL scrape the UoG handbook root `https://www.universityofgalway.ie/handbooks/2025-26/`
- **AND** any PDF matching the regex `MSc[_-]AI[_-]25[_-]26` (or the UoG-specific equivalent) SHALL be yielded
- **AND** the row's `handbook_year = 2025` and `programme_code = "MSCAI"` columns SHALL be populated

#### Scenario: School subdomain path is honoured

- **GIVEN** the `uog_bulk_scrape` Dagster asset runs
- **WHEN** the `module_pages` resource is materialised
- **THEN** the resource SHALL scrape every school-subdomain URL matching `config.school_subdomain_paths` (e.g. `/schools/computer-science/**`)
- **AND** the row's `school_slug` column SHALL be derived from the URL path (e.g. `computer-science`)

### Requirement: BAML course + module + programme + reading-list extraction

The system SHALL provide 4 BAML extraction functions in
`cianfhoghlaim/core/baml/_oideachais_src/university_extraction.baml`:

1. `ExtractCourseDescriptor(course_page_markdown, course_url) -> CourseDescriptor`
2. `ExtractModuleDescriptor(module_page_markdown, module_url) -> ModuleDescriptor`
3. `ExtractProgrammeDescriptor(programme_page_markdown, programme_url) -> ProgrammeDescriptor`
4. `ExtractReadingList(module_page_markdown, module_url) -> ReadingListItem[]`

All 4 functions SHALL route through the canonical `ExtractEn` LiteLLM
client (per the `oideachais-baml-schemas` spec). The BAML classes SHALL
include all fields the marimo notebook needs: course code, NFQ level,
school, ECTS, module count, lecturer names + email + profile URL, and
recommended-reading ISBN-13 + DOI + URL.

#### Scenario: M.Sc. AI module descriptor extracted

- **GIVEN** a module page markdown blob from `https://www.universityofgalway.ie/.../ct516-deep-learning/`
- **WHEN** `b.ExtractModuleDescriptor(markdown, url)` is called
- **THEN** the returned `ModuleDescriptor` SHALL include
  - `module_code = "CT516"`
  - `module_title = "Deep Learning"`
  - `ects = 10`
  - `semester = "semester_1"`
  - `programme_codes = ["MSCAI"]`
  - `learning_outcomes` containing the 5-7 outcome bullets
  - `assessment_breakdown` containing the exam/CA percentages
  - `prerequisite_modules = ["CT511", "MA335"]`
  - `lecturers[]` with name, email, profile_url
  - `recommended_reading[]` with 3-5 entries (ISBN-13, DOI, or URL)
  - `confidence` ∈ [0.0, 1.0]
  - `source_url = "https://..."`

#### Scenario: Reading-list ISBN-13 validation

- **GIVEN** the `ExtractReadingList` function returns a list of `ReadingListItem` records
- **WHEN** the deterministic eval `reading_list_isbn13_format` runs
- **THEN** every record with `format = "ISBN_13"` SHALL have an `isbn_13` field matching the regex `^\d{13}$`
- **AND** records failing the check SHALL be reported in the marimo notebook's "Quality" tab

#### Scenario: Programme ECTS sum matches module ECTS sum

- **GIVEN** a `ProgrammeDescriptor` with `modules[]` referencing 8 `ModuleDescriptor`s
- **WHEN** the deterministic eval `programme_ects_sum` runs
- **THEN** `sum(modules[*].ects)` SHALL equal the `ProgrammeDescriptor.total_ects` within ±1
- **AND** the eval SHALL fail loudly (raise + asset_check fail) if the mismatch exceeds ±1

### Requirement: 3-stage pre-research → bulk-scrape → condense pipeline

The DLT source SHALL use the canonical 3-stage pattern (per
`author-archive-pipeline` spec) for every page:

1. **Pre-research** — one-time Firecrawl `/agent` (2 credits) with Crawl4AI free fallback per the existing `BackendRouter.pre_research` method
2. **Bulk-scrape** — Crawl4AI primary (`prefer_free=True`), Firecrawl `/scrape` paid fallback (1 credit per page) per the existing `BackendRouter.bulk_scrape` method
3. **Condense** — BAML `ExtractCourseDescriptor` / `ExtractModuleDescriptor` / `ExtractProgrammeDescriptor` on the bulk-scrape markdown

#### Scenario: Static UoG course page is scraped free

- **GIVEN** the `pre_research` asset flags `recommended_strategy = "crawl4ai-static"`
- **WHEN** `bulk_scrape` runs over the catalogue page
- **THEN** Crawl4AI is used
- **AND** 0 Firecrawl credits are charged
- **AND** the BAML extraction runs on the resulting markdown

#### Scenario: JS-heavy UoG module page falls back to Firecrawl

- **GIVEN** the `pre_research` asset flags `recommended_strategy = "firecrawl-agent"`
- **WHEN** `bulk_scrape` runs over the module page
- **THEN** Firecrawl `/scrape` is used
- **AND** 1 Firecrawl credit is charged
- **AND** the BAML extraction runs on the resulting markdown

#### Scenario: Credit budget exhausted — free fallback

- **GIVEN** the `CreditBudget.has(2)` returns `False` (the global budget is exhausted)
- **WHEN** `pre_research` runs
- **THEN** the method calls `_free_pre_research()` (Crawl4AI sitemap+sample)
- **AND** 0 credits are charged
- **AND** the `backend_used` is `"crawl4ai_local"` in the resulting `ResearchSiteMap`

### Requirement: 5 Dagster assets

The system SHALL provide 5 Dagster assets in
`cianfhoghlaim/assets/_oideachais_dagster_defs/assets/university_deep_extraction/uog_assets.py`:

1. `uog_pre_research` (group `university_deep_extraction`, compute_kind `scrape`)
2. `uog_bulk_scrape` (group `university_deep_extraction`, compute_kind `scrape`)
3. `uog_extract_courses` (group `university_deep_extraction`, compute_kind `baml`)
4. `uog_extract_modules` (group `university_deep_extraction`, compute_kind `baml`)
5. `uog_extract_programmes` (group `university_deep_extraction`, compute_kind `baml`)

The first 2 mirror `official_media_pre_research` + `official_media_bulk_scrape`
(per the `author-archive-pipeline` spec). The last 3 invoke the BAML
extraction functions and persist results to DuckLake
(`oideachais.education.ie.university_courses` / `university_modules` /
`university_programmes`).

#### Scenario: uog_pre_research asset materialises

- **WHEN** `uog_pre_research` runs
- **THEN** it SHALL call `BackendRouter.pre_research(base_url, goal, budget_hint=2)`
- **AND** persist the result to `oideachais.education.ie.university_research_sitemap` (LanceDB)
- **AND** return `MaterializeResult` with metadata `sources_attempted`, `credits_spent`, `backend`

#### Scenario: uog_extract_modules asset materialises

- **GIVEN** the `uog_bulk_scrape` asset has produced N module page rows
- **WHEN** `uog_extract_modules` runs
- **THEN** it SHALL invoke `b.ExtractModuleDescriptor(markdown, url)` for each row
- **AND** persist the resulting `ModuleDescriptor` records to `oideachais.education.ie.university_modules` (DuckLake)
- **AND** the BAML call SHALL be memoised on `(url, content_hash)` so re-materialisation is idempotent

### Requirement: CocoIndex v1 App for course + module embeddings

The system SHALL provide 2 v1 CocoIndex Apps at
`cianfhoghlaim/core/cocoindex/university_embedding.py`:

1. `UniversityCoursesApp` → `university_courses` LanceDB table (BGE-M3, 1024-dim embedding on `course_description + learning_outcomes`)
2. `UniversityModulesApp` → `university_modules` LanceDB table (BGE-M3, 1024-dim embedding on `module_title + module_description + learning_outcomes`)

Both Apps SHALL use the canonical v1 pattern (per `oideachais-cocoindex-v1-migration` spec): `@coco.lifespan` + `@coco.fn` + `lancedb.mount_table_target` + `SentenceTransformerEmbedder("BAAI/bge-m3")`. Both SHALL respect the 100-batch minimum + `HNSW-DROP-THRESHOLD=50` rule.

#### Scenario: Semantic search over UoG modules

- **GIVEN** the `UniversityModulesApp` has materialised
- **WHEN** a developer runs `await search_university_modules("transformer attention mechanism", limit=5)`
- **THEN** the App returns the top-5 rows from the `university_modules` table ranked by BGE-M3 cosine similarity
- **AND** each row has `module_code`, `module_title`, `school_slug`, `programme_codes`, `ects`, `source_url`

#### Scenario: A 14th v1 App is added without breaking the conformance contract

- **WHEN** a future v1 App is registered
- **THEN** `oideachais.cocoindex_flows.cocoindex_v1_conformance` SHALL pass (per the `oideachais-cocoindex-v1-migration` spec)
- **AND** the total v1 App count SHALL go from 13 to 14
- **AND** the new App SHALL respect the 4-rule conformance contract (R1-R4)

### Requirement: Cognee cross-archive edge `UoGArtifact-MATCHES-CourseDescriptor`

The system SHALL provide a Cognee cross-archive edge rule at
`cianfhoghlaim/cognify/rules/university_cross_archive.py`:

- **Edge type**: `UoGArtifact-MATCHES-CourseDescriptor`
- **Left node**: `author_archive_uog_artifact` (the personal-archive artefacts from `leabharlann/ollscoil_na_gaillimhe/`)
- **Right node**: `university_course_descriptor` (the scraped course descriptors)
- **Match condition**: `(left.course_code = right.programme_code) OR (fuzzy_title_similarity(left.module_title, right.course_title) > 0.85)`
- **Match confidence**: stored as an edge property `match_confidence ∈ [0.0, 1.0]`

#### Scenario: User's CT511 maps to Higher Diploma in Software Design & Development

- **GIVEN** a `author_archive_uog_artifact` row with `course_code = "CT511"`, `module_title = "Software Engineering"`, `document_kind = ASSIGNMENT`
- **AND** a `university_course_descriptor` row with `programme_code = "HDSD"`, `course_title = "Higher Diploma in Science (Software Design & Development)"`
- **WHEN** the `university_cross_archive` cognify pass runs
- **THEN** the cognify pass SHALL emit a `UoGArtifact-MATCHES-CourseDescriptor` edge between the two nodes
- **AND** the edge's `match_confidence = 1.0` (exact `course_code` match on the prefix `CT` for `Higher Diploma`)

#### Scenario: User's MA335 maps to Bachelor of Science (Mathematical Science)

- **GIVEN** a `author_archive_uog_artifact` row with `course_code = "MA335"`, `module_title = "Mathematical Statistics"`
- **AND** a `university_course_descriptor` row with `programme_code = "BScMS"`, `course_title = "Bachelor of Science (Mathematical Science)"`
- **WHEN** the `university_cross_archive` cognify pass runs
- **THEN** the cognify pass SHALL emit a `UoGArtifact-MATCHES-CourseDescriptor` edge
- **AND** the edge's `match_confidence ≥ 0.85` (fuzzy match on `Statistics`)

### Requirement: Marimo notebook with 4 tabs

The system SHALL provide a marimo notebook at
`cianfhoghlaim/notebooks/_oideachais/university_courses.py` with 4 tabs:

1. **M.Sc. AI 25/26 modules** (the primary use case) — pre-filtered to `programme_codes = ["MSCAI"]` and `academic_year = 2025`
2. **All UoG courses** — searchable + filterable by school, NFQ level, ECTS, programme stage
3. **Reading lists** — every reading-list item across all modules, with a "Group by module" + "Group by ISBN-13" toggle
4. **Cross-archive** — the user's `leabharlann/ollscoil_na_gaillimhe/` artefacts joined to the matching scraped `CourseDescriptor` rows via the new Cognee edge

The notebook SHALL use `mo.sql(engine=md:oideachais)` for the
underlying queries (the MotherDuck Postgres endpoint) so it loads
against the lakehouse, not against a local Parquet.

#### Scenario: User opens the M.Sc. AI 25/26 modules tab

- **WHEN** the user navigates to `/dashboards/university-courses` and clicks the "M.Sc. AI 25/26" tab
- **THEN** the notebook SHALL display a table of all 12+ modules in the M.Sc. AI 2025-26 programme
- **AND** each row SHALL show `module_code`, `module_title`, `ects`, `semester`, `lecturers[]`, `assessment_breakdown`, and a clickable `source_url`

#### Scenario: Cross-archive tab shows the user's CT511 in HDSD

- **GIVEN** the `university_cross_archive` cognify pass has emitted the `CT511 → HDSD` edge
- **WHEN** the user opens the "Cross-archive" tab
- **THEN** the table SHALL display the user's CT511 assignment on the left, the matching `CourseDescriptor` on the right, and the `match_confidence` between them
- **AND** clicking the `course_descriptor.url` opens the UoG programme page in a new tab
