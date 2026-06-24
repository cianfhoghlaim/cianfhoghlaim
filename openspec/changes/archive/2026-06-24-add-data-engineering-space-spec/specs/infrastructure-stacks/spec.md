## ADDED Requirements

### Requirement: data-engineering Space must use the KCG canonical stack

The data-engineering Space MUST consume the KCG canonical stack: `stedding/ingest_queue/pypi/` as the source (not BigQuery), MotherDuck as the destination (not local DuckDB), dbt-duckdb as the adapter (not raw dbt), and Cognee + Graphiti for the knowledge graph.

#### Scenario: Modernized data-engineering Space

- **WHEN** the data-engineering Space runs
- **THEN** it reads from `stedding/ingest_queue/pypi/`
- **AND** it writes to MotherDuck
- **AND** it uses dbt-duckdb
- **AND** it has a Cognee + Graphiti cognify pass
