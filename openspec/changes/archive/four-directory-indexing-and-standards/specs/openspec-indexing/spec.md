## ADDED Requirements

### Requirement: OpenSpec Self-Indexing
The system SHALL extract `(change_id, status, quadrant, capability_specs, blocking_deps)` from every `openspec/specs/*/spec.md` and `openspec/changes/*/proposal.md` file, persist an `OpenSpecChange` node per file in the `docs_skills_graph` FalkorDB graph, embed the file content in the `openspec_chunks` LanceDB table, and emit `BLOCKS` / `BLOCKED_BY` / `MODIFIES_SPEC` edges between change nodes and capability spec nodes.

#### Scenario: BAML change extraction
- **GIVEN** a proposal.md under `openspec/changes/four-directory-indexing-and-standards/`
- **WHEN** the `openspec_indexing` CocoIndex v1 App runs
- **THEN** it SHALL call the BAML `ExtractOpenSpecChange` function on the proposal content
- **AND** declare an `OpenSpecChange` node in the shared `docs_skills_graph` FalkorDB graph with the returned `(change_id, status, quadrant, capability_specs)`
- **AND** memoisation SHALL skip re-extraction for unchanged files

#### Scenario: Blocking-dep edge
- **GIVEN** two change proposals where `change_a.blocks` references `change_b.id`
- **WHEN** the Phase 2 graph-build pass runs
- **THEN** it SHALL declare a `BLOCKS` edge from the `change_a` node to the `change_b` node
- **AND** a `BLOCKED_BY` edge in the reverse direction

#### Scenario: Modifies-spec edge
- **GIVEN** a change proposal that names `MODIFIED Requirements` in any capability spec
- **WHEN** the Phase 2 graph-build pass runs
- **THEN** it SHALL declare a `MODIFIES_SPEC` edge from the `OpenSpecChange` node to the corresponding `CapabilitySpec` node
- **AND** the edge SHALL carry the diff-size as an attribute

### Requirement: Leabharlann→OpenSpec Citation Links
The system SHALL extract citation relationships between leabharlann Markdown documents and OpenSpec changes, persist them as `LEABHARLANN_CITES` edges in the shared `docs_skills_graph` FalkorDB graph, and embed the citing context in the `leabharlann_openspec_links` LanceDB table.

#### Scenario: BAML cite extraction
- **GIVEN** a Markdown file under `leabharlann/` that references an `openspec/changes/<id>/` slug in a citation-style line
- **WHEN** the `leabharlann_openspec_links` CocoIndex v1 App runs
- **THEN** it SHALL call the BAML `ExtractLeabharlannCites` function
- **AND** emit one `CitesRecord` per matched citation

#### Scenario: Edge declaration
- **GIVEN** a `CitesRecord(pdf_id, openspec_change_id, quote, page)`
- **WHEN** the Phase 2 graph-build pass runs
- **THEN** it SHALL declare a `LEABHARLANN_CITES` edge from the `LeabharlannDoc` node to the `OpenSpecChange` node
- **AND** the edge SHALL carry the quote text and page number as attributes

#### Scenario: Failure isolation
- **GIVEN** a leabharlann Markdown file with no extractable citations
- **WHEN** the App processes the file
- **THEN** the file SHALL be logged with a `DEBUG` and skipped
- **AND** downstream graph nodes SHALL still declare successfully for the remaining files

### Requirement: Schema and Data-Type Standardisation
The system SHALL provide a single canonical source of truth for the `Quadrant`, `DocumentType`, and `EmbeddingModel` enums, and SHALL replace every hard-coded `"BAAI/bge-m3"` string with a reference to that enum.

#### Scenario: Quadrant enum
- **GIVEN** a Python module that needs to reference the `oideachais` quadrant
- **WHEN** the module imports `Quadrant` from `oideachais.core.types`
- **THEN** the import SHALL resolve to the canonical enum value
- **AND** the module SHALL NOT redeclare a local `Quadrant` enum

#### Scenario: Embedding model constant
- **GIVEN** a CocoIndex v1 App that needs the BGE-M3 embedding model
- **WHEN** the App reads `os.environ.get("CODEOLAS_EMBED_MODEL", BgeM3)`
- **THEN** the default SHALL be the canonical `BgeM3` constant
- **AND** the literal string `"BAAI/bge-m3"` SHALL NOT appear in the App source

#### Scenario: Migration report
- **GIVEN** the migration sweep of Step 4.3 / 4.4 in `tasks.md`
- **WHEN** the sweep completes
- **THEN** `docs/refactor/schema-type-standardization-report.md` SHALL list every file migrated, every file skipped, and the count of remaining hard-coded literals

## MODIFIED Requirements

### Requirement: ChunkHound Deprecation Path
The system SHALL designate `oideachais.cocoindex_flows.codebase_indexing.codebase_app` as the canonical implementation of the `chunkhound-code-search` capability and SHALL remove the legacy ChunkHound MCP server configuration from `.opencode.yaml` by 2026-07-15.

#### Scenario: v1 App is canonical
- **GIVEN** an agent that needs to search the codebase semantically
- **WHEN** the agent imports `search_codebase` from `oideachais.cocoindex_flows.codebase_indexing`
- **THEN** the import SHALL resolve to the v1 Python helper
- **AND** the search SHALL run against the `codebase_chunks` LanceDB table

#### Scenario: Legacy MCP commented out
- **GIVEN** `.opencode.yaml` at the repo root
- **WHEN** the file is read after 2026-07-15
- **THEN** the `chunkhound` MCP entry SHALL be deleted (not merely commented out)
- **AND** a CI guard SHALL fail the build if the entry reappears
