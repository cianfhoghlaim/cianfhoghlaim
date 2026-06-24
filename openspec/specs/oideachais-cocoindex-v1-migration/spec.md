# oideachais-cocoindex-v1-migration Specification

## Purpose
TBD - created by archiving change oideachais-v0-to-v1-migration. Update Purpose after archive.
## Requirements
### Requirement: V1 CocoIndex Apps

The system SHALL provide **11 v1 CocoIndex Apps** in
`oideachais/cocoindex_flows/`. The 11 Apps are:

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

The 11 Apps use the canonical v1 pattern documented in
`.agents/skills/oideachais-cocoindex-v1/SKILL.md`:
`@coco.lifespan` + `@coco.fn` + `lancedb.mount_table_target`
+ `SentenceTransformerEmbedder`.

#### Scenario: A developer adds the 12th v1 App

- **GIVEN** a developer adds `celtic_npc_embedding.py` (a new App
  for the Tuatha Pent-Elemental Cosmology NPCs)
- **WHEN** `oideachais.cocoindex_flows` is imported
- **THEN** the registry SHALL have 12 entries
- **AND** the new App SHALL use the canonical v1 pattern (lifespan +
  fn + mount_table_target + SentenceTransformerEmbedder)
- **AND** the new App SHALL respect the 100-batch minimum +
  the HNSW-DROP-THRESHOLD=50 rule

### Requirement: V0 Archive

The system SHALL archive the **10 v0 broken CocoIndex modules**
at `oideachais/cocoindex_flows/_v0_archive/` (the canonical home
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
`oideachais/cocoindex_flows/`.

The system SHALL NOT migrate the 10 v0 modules to v1 in this
change (the migration is a 6-week project per
`oideachais/REFACTORING.md` #6). The 11 v1 Apps cover the
equivalent use cases.

#### Scenario: A developer tries to import a v0 module

- **GIVEN** the v0 module is archived at
  `oideachais/cocoindex_flows/_v0_archive/research_embedding.py`
- **WHEN** a developer does
  `from oideachais.cocoindex_flows.research_embedding import ...`
- **THEN** Python SHALL raise `ModuleNotFoundError` (or
  `ImportError`) with a helpful message pointing at the
  `_v0_archive/` directory
- **AND** the developer SHALL use the v1 App instead (e.g.
  `unified_embedding` for the DuckDB-source research use case)

