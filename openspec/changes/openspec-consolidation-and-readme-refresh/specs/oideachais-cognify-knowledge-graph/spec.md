## ADDED Requirements

The `oideachais-cognify-knowledge-graph` capability is consolidated
from the old `knowledge-graph` and
`leabharlann-cognify-and-cross-archive-edges` specs. The full
Requirements + Scenarios are in the canonical spec at
`openspec/specs/oideachais-cognify-knowledge-graph/spec.md`.

### Requirement: 5-stage cross-stage cognify

The system SHALL build a 5-stage curriculum knowledge graph with 8
cross-stage edges via the `cross_stage_cognify` Dagster asset.

#### Scenario: 8 cross-stage edges

- **WHEN** the `cross_stage_cognify` asset materialises
- **THEN** 8 cross-stage edges are created in Cognee (BRIDGES_TO,
  PREPARES_FOR, PROGRESSES_TO, ASSESSED_BY, REQUIRED_FOR,
  DELIVERS, LADDERS_INTO, ALTERNATIVE_TO)

### Requirement: 3 leabharlann cognify datasets

The system SHALL cognify the 3 leabharlann corpora into 3 Cognee
datasets: `leabharlann_books`, `leabharlann_zotero`, `leabharlann_takeout`.

#### Scenario: 3 datasets populate

- **WHEN** the 3 cognify Dagster assets materialise
- **THEN** 3 Cognee datasets are populated

### Requirement: Cross-archive FalkorDB edges

The system SHALL populate FalkorDB with 3 cross-archive edge types
via the `cross_archive_edges` Dagster asset: CITES (arxiv_id),
TEACHES (module title), CITES (URL).

#### Scenario: 3 edge types created

- **WHEN** the `cross_archive_edges` asset materialises
- **THEN** FalkorDB has CITES, TEACHES, CITES edges

### Requirement: Cross-archive graph query API

The system SHALL expose a FastAPI route at
`GET /cross-archive-graph/{query}` that runs a FalkorDB query.

#### Scenario: Live query returns 200

- **WHEN** a user issues `GET /cross-archive-graph/irish%20NLP`
- **THEN** the route returns HTTP 200 with `{"nodes": [...], "edges": [...], "total": N}`

### Requirement: Daily cognify cron

The system SHALL fire the 4 cognify + cross-archive assets on a daily
cron at 02:00 UTC.

#### Scenario: Daily cron fires

- **WHEN** the cron tick at 02:00 UTC arrives
- **THEN** the `cognee_cron_sensor` fires 4 `RunRequest`s
