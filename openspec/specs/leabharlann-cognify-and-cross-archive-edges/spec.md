# leabharlann-cognify-and-cross-archive-edges Specification

## Purpose
TBD - created by archiving change leabharlann-cognify-and-cross-archive-edges. Update Purpose after archive.
## Requirements
### Requirement: Cognify of leabharlann corpora

The system SHALL cognify the 3 leabharlann corpora (books, zotero,
takeout) into Cognee datasets `leabharlann_books`, `leabharlann_zotero`,
`leabharlann_takeout`.

#### Scenario: books cognify runs without error

- **WHEN** the `cognify_leabharlann_books` Dagster asset materialises
- **THEN** the asset invokes the Cognee cognify lifecycle for the books DuckLake rows
- **AND** the asset returns a MaterializeResult with `cognee_status=success` (or `skipped_no_cognee` if Cognee is not installed)

### Requirement: Cross-archive edges

The system SHALL populate FalkorDB with cross-archive edges between
leabharlann corpora.

#### Scenario: arxiv_id match creates CITES edge

- **WHEN** a Zotero paper has `arxiv_id=2504.02890` and a Gemini deep research report cites `https://arxiv.org/abs/2504.02890`
- **THEN** the `cross_archive_edges` Dagster asset creates a `CITES` edge in FalkorDB from the Gemini report to the Zotero paper

### Requirement: Web API for cross-archive graph

The system SHALL expose a FastAPI route at `GET /cross-archive-graph/{query}` that runs a FalkorDB query and returns JSON node+edge payload.

#### Scenario: live query returns 200

- **WHEN** the user issues `GET /cross-archive-graph/irish%20NLP`
- **THEN** the route returns HTTP 200 with `{"nodes": [...], "edges": [...]}` for the top 25 matches

