## ADDED Requirements

### Requirement: Memory-stack secret contract is uniform across all 5 backends

The system SHALL expose a uniform `infisical://dev-baile/<svc>/<key>`
URI form for every secret consumed by the 5 memory backends
(`cognee`, `graphiti`, `lancedb`, `falkordb`, `memgraph`). Every
`secrets.env` file SHALL pass `bun run validate-stacks --strict
--check-grammar` with zero MIXED warnings. The legacy Jinja
`{{ infisical:///key?path=/svc }}` form SHALL NOT appear in any
memory-backend `secrets.env` file.

#### Scenario: All 5 backends declare secrets in canonical URI form

- **GIVEN** `bonneagar/stacks/{cognee,graphiti,lancedb,falkordb,memgraph}/secrets.env`
- **WHEN** each file is read
- **THEN** every URI line SHALL match the regex `^[^=]+=infisical://dev-baile/<svc>/<key>$`
- **AND** zero lines SHALL match the legacy `{{ infisical:///... }}` Jinja form

#### Scenario: stack-doctor --strict --check-grammar reports zero mixed stacks

- **WHEN** `bun run validate-stacks --strict --check-grammar` runs
- **THEN** the validator SHALL report `MIXED: 0` for all 5 memory-backend stacks
- **AND** the overall exit code SHALL be 0

### Requirement: Memory-stack health is exposed via the marimo doctor

The system SHALL expose the 5-backend memory-stack health via a
dedicated marimo notebook at `notebooks/24_lakehouse_memory_doctor.py`
AND a CLI doctor at `scripts/lakehouse-memory-doctor.ts` (invoked
through `mise run lakehouse:memory:doctor`). The notebook SHALL
display a 5-column grid (one per backend) with per-backend status,
endpoint ping latency, last cognify/episode timestamp, and vector-index
row count. The CLI SHALL write a JSON health report to
`stedding/memory-health/<utc-ts>.json`.

#### Scenario: Operator opens the marimo memory doctor

- **WHEN** the operator runs `marimo edit notebooks/24_lakehouse_memory_doctor.py`
- **THEN** the notebook SHALL display a 5-column grid: cognee / graphiti / lancedb / falkordb / memgraph
- **AND** each column SHALL show: container status (Up/Down), endpoint ping latency in ms, last cognify/episode timestamp, vector-index row count
- **AND** a "federated search" expander SHALL demo a single query routed across all 5 backends via the `MemoryLayer` Protocol from `agents/memory_layer.py`

#### Scenario: CLI doctor emits a JSON health report

- **WHEN** the operator runs `mise run lakehouse:memory:doctor`
- **THEN** the script SHALL probe the 5 backends via:
  - `GET http://cognee:8000/health`
  - `GET http://graphiti:8000/healthcheck`
  - `GET http://lakehouse-lance-namespace:8182/v1/info`
  - `redis-cli -h falkordb ping`
  - `GET http://memgraph:7687`
- **AND** the script SHALL write a JSON report to `stedding/memory-health/<utc-ts>.json`
- **AND** the script SHALL exit 1 if any backend reports `not_healthy`