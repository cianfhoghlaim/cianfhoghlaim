# Spec Delta — `semantic-search` (MODIFIED — add `author-archive` query handler)

## Purpose

`semantic-search` is an existing capability of the Cianfhoghlaim platform. The canonical spec lives at `openspec/specs/semantic-search/spec.md`. This delta adds the `search_author_archive` query handler and the 4 new LanceDB tables introduced by this change.

## MODIFIED Requirements

### Requirement: LanceDB Query Handlers
The system SHALL expose a `search_author_archive` query handler that returns ranked results from the 4 new LanceDB tables in `oideachais/cocoindex_flows/author_archive_embedding.py`.

#### Scenario: Search by free-text query
- **GIVEN** the user invokes `await search_author_archive(query="cross-border medical malpractice", limit=10)`
- **WHEN** the handler runs
- **THEN** the top 10 most similar rows SHALL be returned across `author_archive_gemini`, `author_archive_uog_documents`, `author_archive_uog_code`, and `author_archive_equations` (union, ranked by cosine similarity)
- **AND** each result SHALL include `file_path`, `file_name`, `account`, `domain`, `course_code` (when present), `artifact_kind` (when present), `text`, and `score`

#### Scenario: Filter by account
- **GIVEN** the user invokes `search_author_archive(query, account="gemini_deep_research")`
- **WHEN** the handler runs
- **THEN** only rows with `account="gemini_deep_research"` SHALL be considered

#### Scenario: Filter by domain
- **GIVEN** the user invokes `search_author_archive(query, domain="law")`
- **WHEN** the handler runs
- **THEN** only rows with `domain="law"` SHALL be considered

#### Scenario: Filter by course code
- **GIVEN** the user invokes `search_author_archive(query, course_code="ed305")`
- **WHEN** the handler runs
- **THEN** only rows with `course_code="ed305"` SHALL be considered

#### Scenario: Filter by artefact kind
- **GIVEN** the user invokes `search_author_archive(query, artifact_kind="equation")`
- **WHEN** the handler runs
- **THEN** only rows from the `author_archive_equations` table SHALL be considered

### Requirement: Embedding Model Consistency
The system SHALL use a single English-only embedding model for all `author_archive_*` tables.

#### Scenario: Model selection
- **GIVEN** the embedding model constant in `oideachais/cocoindex_flows/author_archive_embedding.py`
- **WHEN** the flow is compiled by `mise run cocoindex:update`
- **THEN** the model SHALL be `BAAI/bge-large-en-v1.5`
- **AND** the embedding dimension SHALL be 1024
- **AND** the same model SHALL be used for the query embedding in `search_author_archive` (no cross-model mismatch)

## REMOVED Requirements

*(None.)*
