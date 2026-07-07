# oideachais-cocoindex-v1-migration Specification

## Purpose

`oideachais-cocoindex-v1-migration` is a capability of the Cianfhoghlaim
platform. It defines the canonical pattern for **v1 CocoIndex Apps** in
the consolidated `cianfhoghlaim/` package: every CocoIndex flow is
exposed as a v1 `coco.App` instance with a `@coco.fn` `app_main`
function, a stable identity, v1 R1-R4 rule conformance, and the
`lancedb.mount_table_target` target pattern. Post-v4, the Apps live at
`cianfhoghlaim/cocoindex/<app>.py`. There are 15 Apps in current use
(13 from the BIEP v1 + UoG deep-extraction timeline, plus the 2 from
`apple-photos-ingestion`).
## Requirements
### Requirement: V1 CocoIndex Apps

The system SHALL provide **13 v1 CocoIndex Apps** in
`cianfhoghlaim/core/cocoindex/` (was 11 before this change; the
new `UniversityCoursesApp` + `UniversityModulesApp` per the
`oideachais-university-deep-extraction` spec bring the total to 13).

The 13 Apps are:

1. `leabharlann_books_embedding` → `leabharlann_books` (BGE-large)
2. `leabharlann_zotero_embedding` → `leabharlann_zotero` (BGE-large)
3. `leabharlann_takeout_embedding` → `leabharlann_takeout` (BGE-large)
4. `codebase_indexing` → `codebase_chunks` (BGE-m3 + 7-node/7-edge code graph)
5. `api_indexing` → `api_endpoints` (BGE-m3 + 4-framework HTTP route surface)
6. `filesystem_indexing` → `filesystem_layout` (BGE-m3 + depth 1-4 dirs)
7. `storage_indexing` → `storage_backends` (BGE-m3 + 9 backend kinds)
8. `config_indexing` → `config_files` (BGE-m3 + 12 config kinds)
9. `unified_embedding` → `unified_embeddings` (BGE-m3 + DuckDB source)
10. `code_embeddings` → `code_embeddings` (BGE-m3 + LocalFile source)
11. `docs_skills_consolidation` → `docs_skills` (BGE-m3 + BAML extraction)
12. `UniversityCoursesApp` → `university_courses` (BGE-m3, 1024-dim on `course_description + learning_outcomes`) — **NEW**
13. `UniversityModulesApp` → `university_modules` (BGE-m3, 1024-dim on `module_title + module_description + learning_outcomes`) — **NEW**

All 13 Apps SHALL use the canonical v1 pattern
(`@coco.lifespan` + `@coco.fn` + `lancedb.mount_table_target` +
`SentenceTransformerEmbedder`), respect the 100-batch minimum +
`HNSW-DROP-THRESHOLD=50` rule, and pass `cocoindex_v1_conformance`.

#### Scenario: Semantic search over UoG modules

- **GIVEN** the `UniversityModulesApp` has materialised
- **WHEN** a developer runs `await search_university_modules("transformer attention mechanism", limit=5)`
- **THEN** the App returns the top-5 rows from the `university_modules` table ranked by BGE-M3 cosine similarity
- **AND** each row carries `module_code`, `module_title`, `school_slug`, `programme_codes`, `ects`, `source_url`

#### Scenario: Semantic search over UoG courses

- **GIVEN** the `UniversityCoursesApp` has materialised
- **WHEN** a developer runs `await search_university_courses("applied statistics with R", limit=5)`
- **THEN** the App returns the top-5 rows from the `university_courses` table ranked by BGE-M3 cosine similarity
- **AND** each row carries `course_code`, `course_title`, `nfq_level`, `school`, `ects`, `source_url`

#### Scenario: A 14th v1 App is added without breaking the conformance contract

- **WHEN** a future v1 App is registered
- **THEN** `oideachais.cocoindex_flows.cocoindex_v1_conformance` SHALL pass (per the `oideachais-cocoindex-v1-migration` spec)
- **AND** the total v1 App count SHALL go from 13 to 14
- **AND** the new App SHALL respect the 4-rule conformance contract (R1-R4)
- **AND** the new App SHALL be added to the `APP_REGISTRY` at `cianfhoghlaim.core.cocoindex`

#### Scenario: CocoIndex v1 conformance linter passes

- **WHEN** `mise run lint:v1-conformance` is run
- **THEN** the linter SHALL report `13/13 apps passed` (was 11/11 before this change)
- **AND** the linter SHALL report `0 conformance errors`
- **AND** the linter SHALL report `0 R1-R4 violations`

### Requirement: V0 Archive

The system SHALL archive the **10 v0 broken CocoIndex modules**
at `cianfhoghlaim/cocoindex_flows/_v0_archive/` (the canonical home
for deprecated v0 code). The 10 modules are:

1. `author_archive_embedding.py`
2. `curriculum_embedding.py`
3. `curriculum_translation.py`
4. `curriculum_specification_extraction.py`
5. `geospatial_indexing.py`
6. `learning_outcome_graph.py`
7. `ocr_embedding.py`
8. `pdf_embedding.py`
9. `research_embedding.py`
10. `site_analysis_embedding.py`

The 10 modules SHALL raise `ImportError` when imported
(cocoindex==1.0.9 has no `flow_def` DSL). The
`_v0_archive/__init__.py` SHALL document the deprecation and
point to the canonical v1 Apps in
`cianfhoghlaim/cocoindex_flows/`.

The system SHALL NOT migrate the 10 v0 modules to v1 in this
change (the migration is a 6-week project per
`cianfhoghlaim/REFACTORING.md` #6). The 11 v1 Apps cover the
equivalent use cases.

#### Scenario: A developer tries to import a v0 module

- **GIVEN** the v0 module is archived at
  `cianfhoghlaim/cocoindex_flows/_v0_archive/research_embedding.py`
- **WHEN** a developer does
  `from oideachais.cocoindex_flows.research_embedding import ...`
- **THEN** Python SHALL raise `ModuleNotFoundError` (or
  `ImportError`) with a helpful message pointing at the
  `_v0_archive/` directory
- **AND** the developer SHALL use the v1 App instead (e.g.
  `unified_embedding` for the DuckDB-source research use case)


## Merged from

- `cocoindex-v1-migration` (the original v1 CocoIndex migration spec was merged into this spec on 2026-07-06)
