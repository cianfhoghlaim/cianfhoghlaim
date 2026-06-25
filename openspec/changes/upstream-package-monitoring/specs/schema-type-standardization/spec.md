## MODIFIED Requirements

### Requirement: Canonical Quadrant Enum
The system SHALL expose a single canonical `Quadrant` enum at `oideachais.core.types.Quadrant` with the values `OIDEACHAIS`, `MEISINFHOGHLAIM`, `TUATHA`, `CROILAR`, `SHARED`, and SHALL re-export it from `codeolas.core.types` for the publishable wheel.

#### Scenario: Single import surface
- **GIVEN** a Python module in any quadrant that needs to reference a quadrant by name
- **WHEN** the module imports `Quadrant`
- **THEN** the import SHALL resolve to the canonical enum at
  `oideachais.core.types.Quadrant`
- **AND** no module SHALL redeclare a local `Quadrant` enum

### Requirement: Canonical DocumentType Enum
The system SHALL expose a single canonical `DocumentType` enum at `oideachais.core.types.DocumentType` covering every document class handled by the four-directory indexing sweep (curriculum artefacts, leabharlann PDFs / EPUBs / Takeouts, Zotero papers, research briefs, OpenSpec changes, skill markdowns, doc markdowns, BAML schemas, Dagster assets).

#### Scenario: Single import surface
- **GIVEN** a dlt source or a CocoIndex v1 App that needs to tag a document by class
- **WHEN** the source or App imports `DocumentType`
- **THEN** the import SHALL resolve to the canonical enum
- **AND** no source or App SHALL redeclare a local `DocumentType` enum

### Requirement: Canonical EmbeddingModel Enum and Default Constant
The system SHALL expose a single canonical `EmbeddingModel` enum and a `BgeM3 = "BAAI/bge-m3"` constant at `oideachais.core.types`, re-exported from `codeolas.core.types`, and SHALL replace every hard-coded `"BAAI/bge-m3"` literal in the monorepo with a reference to that constant or to the `os.environ["CODEOLAS_EMBED_MODEL"]` override.

#### Scenario: Default fallback
- **GIVEN** a CocoIndex v1 App that needs the BGE-M3 embedding model and the env var `CODEOLAS_EMBED_MODEL` is unset
- **WHEN** the App reads `os.environ.get("CODEOLAS_EMBED_MODEL", BgeM3)`
- **THEN** it SHALL use `"BAAI/bge-m3"`

#### Scenario: Override
- **GIVEN** the env var `CODEOLAS_EMBED_MODEL=BAAI/bge-large-en-v1.5`
- **WHEN** any CocoIndex v1 App starts
- **THEN** it SHALL honour the override without code changes

### Requirement: Migration Sweep and Report
The system SHALL provide a sweep script at `scripts/sweep_hardcoded_types.py` that walks `sruth/oideachais/`, `sruth/meaisinfhoghlaim/`, `sruth/tuatha/`, `codeolas/`, `baml_src/`, and `infrastructure/` and emits a Markdown report at `docs/refactor/schema-type-standardization-report.md` listing every file migrated, every file skipped, and the count of remaining hard-coded literals.

#### Scenario: Sweep exit code
- **GIVEN** the sweep script at `scripts/sweep_hardcoded_types.py`
- **WHEN** `uv run python scripts/sweep_hardcoded_types.py` is invoked
- **THEN** the script SHALL exit 0 when the migration is complete
- **AND** the script SHALL exit 1 when any hard-coded literal remains
- **AND** the Markdown report SHALL be regenerated on every run

#### Scenario: Dry run
- **GIVEN** the sweep script invoked with `--dry-run`
- **WHEN** the script runs
- **THEN** it SHALL emit the planned migrations to stdout without modifying any file

## ADDED Requirements

### Requirement: Canonical Package Enum

The system SHALL expose a canonical `Package` enum at
`oideachais.core.types.Package` with the values `MOTHERDUCK`,
`DLTHUB`, `LANCEDB`, `COCOINDEX`, re-exported from
`codeolas.core.types` for the publishable wheel. The enum SHALL
be the single source of truth for the four upstream packages
whose blog posts / docs / changelogs the platform's upstream
monitoring pipeline watches.

#### Scenario: Single import surface

- **GIVEN** a CocoIndex v1 App or a Dagster asset that needs to
  tag an artefact by upstream package
- **WHEN** the module imports `Package`
- **THEN** the import SHALL resolve to the canonical enum at
  `oideachais.core.types.Package`
- **AND** no module SHALL redeclare a local `Package` enum

#### Scenario: BAML client enforcement

- **GIVEN** the BAML function
  `ExtractBlogPostMetadata(content, url) -> BlogPostMetadata` in
  `baml_src/upstream_monitoring.baml`
- **WHEN** the function returns
- **THEN** the `package` field SHALL be typed as
  `oideachais.core.types.Package` (not a string)
- **AND** the BAML client SHALL reject any value not in the
  enum at validation time

### Requirement: Canonical BlogPostType Enum

The system SHALL expose a canonical `BlogPostType` enum at
`oideachais.core.types.BlogPostType` with the values
`ANNOUNCEMENT`, `TUTORIAL`, `BENCHMARK`, `CASE_STUDY`,
`RELEASE_NOTES`, `API_DOC`, re-exported from
`codeolas.core.types` for the publishable wheel. The enum SHALL
be the single source of truth for the classification of upstream
blog posts by the `ExtractBlogPostMetadata` BAML function.

#### Scenario: BAML client enforcement

- **GIVEN** the BAML function
  `ExtractBlogPostMetadata(content, url) -> BlogPostMetadata` in
  `baml_src/upstream_monitoring.baml`
- **WHEN** the function returns
- **THEN** the `blog_post_type` field SHALL be typed as
  `oideachais.core.types.BlogPostType` (not a string)
- **AND** the BAML client SHALL reject any value not in the
  enum at validation time
- **AND** the Firecrawl monitor `--goal` strings for each of
  the 4 packages SHALL mention at least 3 of the 6 enum values
  so the LLM judge can classify accurately