# Spec Delta — `oideachais-cocoindex-v1-migration` (modified)

## Purpose

`oideachais-cocoindex-v1-migration` is a capability of the Cianfhoghlaim
platform that defines the canonical v1 CocoIndex App pattern
(`@coco.lifespan` + `@coco.fn` + `lancedb.mount_table_target` +
`SentenceTransformerEmbedder`) and tracks the v1 App count + the v0
archive. See `docs/00_index.md` for the quadrant map and
`docs/00-core/CLAUDE.md` for the project identity.

This delta adds 2 new v1 Apps (`UniversityCoursesApp` and
`UniversityModulesApp`) per the `oideachais-university-deep-extraction`
spec, bringing the total v1 App count from 11 to 13. The new Apps
back the new `/dashboards/university-courses` marimo notebook with
BGE-M3 1024-dim embeddings over the scraped course + module
descriptors.

## MODIFIED Requirements

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
