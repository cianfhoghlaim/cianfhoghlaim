# `oideachais-cocoindex-v1-migration` capability spec — agent-discovery + apple-photos delta

The oideachais-cocoindex-v1-migration capability spec
governs the v1 CocoIndex Apps at
`cianfhoghlaim/cocoindex/`, the 4-rule conformance contract
(R1-R4), the 100-batch minimum + HNSW-DROP-THRESHOLD=50 rule,
and the canonical APP_REGISTRY at
`cianfhoghlaim/cocoindex/__init__.py`.

This delta extends the v1 App count from 13 → 17 by adding
4 new Apps:

- `agent_registry` (the canonical agent discovery surface
  over `opencode.json`; see the
  `indexing-and-cognition` spec)
- `agents_md` (the canonical AGENTS.md discovery surface
  over the 6 AGENTS.md files; see the
  `indexing-and-cognition` spec)
- `apple_photos_metadata` (12-column EXIF + metadata index
  over the Apple Photos DuckLake table; see the
  `oideachais-leabharlann` spec)
- `apple_photos_chunks` (OCR'd text index over the Apple
  Photos document scans + license plate reads; see the
  `oideachais-leabharlann` spec)

Plus a 5th new App for the GeoParquet output:
`apple_photos_geospatial`.

## MODIFIED Requirements

### Requirement: V1 CocoIndex Apps (13 → 17)

The system SHALL provide **17 v1 CocoIndex Apps** in
`cianfhoghlaim/cocoindex/` (was 13). The 4 new Apps SHALL be:
`agent_registry`, `agents_md`, `apple_photos_metadata`,
`apple_photos_chunks` (all 4 use BGE-m3 1024-dim; all 4
target LanceDB tables; all 4 pass `cocoindex_v1_conformance`).
A 5th new App `apple_photos_geospatial` SHALL emit 2
GeoParquet files (POINT Z, EPSG:4326) at
`leabharlann/photos/_derived/all_photos.geo.parquet` and
`leabharlann/photos/_derived/vehicles.geo.parquet`.

The 17 Apps SHALL use the canonical v1 pattern
(`@coco.lifespan` + `@coco.fn` + `lancedb.mount_table_target` +
`SentenceTransformerEmbedder`), SHALL respect the 100-batch
minimum + `HNSW-DROP-THRESHOLD=50` rule, and SHALL pass
`cocoindex_v1_conformance`.

_(Previously the system provided 13 v1 CocoIndex Apps
[listed in the canonical `oideachais-cocoindex-v1-migration`
spec under the prior "V1 CocoIndex Apps" Requirement].)_

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
12. `UniversityCoursesApp` → `university_courses` (BGE-m3, 1024-dim on `course_description + learning_outcomes`)
13. `UniversityModulesApp` → `university_modules` (BGE-m3, 1024-dim on `module_title + module_description + learning_outcomes`)

**Is:** The system provides **17 v1 CocoIndex Apps** in
`cianfhoghlaim/cocoindex/` (was 13; the 4 new
`agent_registry`, `agents_md`, `apple_photos_metadata`,
`apple_photos_chunks` Apps bring the total to 17). Plus a
5th non-LanceDB output (`apple_photos_geospatial` →
GeoParquet files).

The 17 + 1 Apps are:

14. `agent_registry` → `agent_registry` (BGE-m3, 1024-dim
    on `description + prompt` + 12 metadata fields) — **NEW**
15. `agents_md` → `agents_md` (BGE-m3, 1024-dim on the
    6 AGENTS.md files; chunk size 2048, overlap 256) — **NEW**
16. `apple_photos_metadata` → `apple_photos_metadata`
    (BGE-m3, 1024-dim on `caption` + 11 EXIF/metadata
    fields) — **NEW**
17. `apple_photos_chunks` → `apple_photos_chunks`
    (BGE-m3, 1024-dim on OCR'd text from document scans +
    license plate reads) — **NEW**

The 18th App `apple_photos_geospatial` outputs GeoParquet
files (not LanceDB), so it sits in a separate
`GEOSPATIAL_APP_REGISTRY` tuple.

All 17 v1 Apps SHALL use the canonical v1 pattern
(`@coco.lifespan` + `@coco.fn` + `lancedb.mount_table_target` +
`SentenceTransformerEmbedder`), respect the 100-batch minimum +
`HNSW-DROP-THRESHOLD=50` rule, and pass `cocoindex_v1_conformance`.

#### Scenario: Conformance linter reports 17/17 apps passed

- **GIVEN** the 4 new v1 Apps are added to the `APP_REGISTRY`
- **WHEN** `mise run lint:v1-conformance` is run
- **THEN** the linter SHALL report `17/17 apps passed`
  (was 13/13)
- **AND** the linter SHALL report `0 conformance errors`
- **AND** the linter SHALL report `0 R1-R4 violations`

#### Scenario: Apple Photos Apps use BGE-m3

- **GIVEN** the 3 new Apple Photos v1 Apps
  (`apple_photos_metadata`, `apple_photos_chunks`,
  `apple_photos_geospatial`)
- **WHEN** the files are read
- **THEN** all 3 SHALL use `SentenceTransformerEmbedder`
  with `model_name="BAAI/bge-m3"` and `dimensionality=1024`
- **AND** the 2 LanceDB-output Apps SHALL respect the
  100-batch minimum + `HNSW-DROP-THRESHOLD=50` rule
- **AND** the GeoParquet-output App SHALL emit
  `geometry` columns as `POINT Z` in EPSG:4326

#### Scenario: agent_registry indexes opencode.json

- **GIVEN** `opencode.json` declares 7 agents + 10 MCP
  servers
- **AND** the `agent_registry` v1 App has materialised
- **WHEN** a developer runs
  `await search_agents("which agent handles ccc code search", kind="agent", limit=1)`
- **THEN** the function SHALL return the `data-platform`
  agent (it lists `ccc` in its `skill_filter`)

## Cross-references

- [`openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/proposal.md`](../proposal.md)
- [`.agents/skills/oideachais-cocoindex-v1/SKILL.md`](../../.agents/skills/oideachais-cocoindex-v1/SKILL.md)
- [`openspec/changes/oideachais-cocoindex-v1-migration/`](../oideachais-cocoindex-v1-migration/)
- [`openspec/changes/oideachais-university-deep-extraction/`](../oideachais-university-deep-extraction/)
