# Spec Delta — `semantic-search` (MODIFIED — add leabharlann query handlers)

## Purpose

`semantic-search` is an existing capability of the Cianfhoghlaim platform. The canonical spec lives at `openspec/specs/semantic-search/spec.md`. This delta adds the `search_leabharlann_books`, `search_leabharlann_zotero`, and `search_leabharlann_takeout` query handlers.

## MODIFIED Requirements

### Requirement: Leabharlann Query Handlers
The system SHALL expose three new query handlers for semantic search across the leabharlann archives.

#### Scenario: Books search
- **GIVEN** the user invokes `await search_leabharlann_books(query="Celtic placenames of Belfast", subject="gaeilge", limit=10)`
- **WHEN** the handler runs
- **THEN** the top 10 most similar chunks from `leabharlann_books` SHALL be returned
- **AND** each result SHALL include `filename`, `subject`, `chunk_text`, and `score`

#### Scenario: Zotero search with metadata filter
- **GIVEN** the user invokes `await search_leabharlann_zotero(query="handwritten essay recognition", htr_relevant=True, limit=5)`
- **WHEN** the handler runs
- **THEN** the top 5 most similar `ZoteroPaper` rows SHALL be returned
- **AND** only rows with `htr_relevant=true` SHALL be considered
- **AND** each result SHALL include `title`, `authors`, `year`, `venue`, `chunk_text`, and `score`

#### Scenario: Takeout search
- **GIVEN** the user invokes `await search_leabharlann_takeout(query="disability allowance", account="stedding_takeout", limit=10)`
- **WHEN** the handler runs
- **THEN** the top 10 most similar chunks from `leabharlann_takeout` SHALL be returned
- **AND** only rows with `account="stedding_takeout"` SHALL be considered

## REMOVED Requirements

*(None.)*
