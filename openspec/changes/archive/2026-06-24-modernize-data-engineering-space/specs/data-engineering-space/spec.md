## ADDED Requirements

### Requirement: data-engineering Space modernized to the KCG-canonical stack

The data-engineering Space MUST consume the KCG-canonical stack (per the `data-engineering-space` spec). The modernization adds a new `package_analytics/kcg_data_layer/` module that replaces the BigQuery source with `stedding/ingest_queue/pypi/`, the local DuckDB destination with MotherDuck, and the no-op knowledge graph with a 5-stage Cognee + Graphiti cognify pass.

#### Scenario: Modernized data-engineering Space runs end-to-end

- **WHEN** the modernized data-engineering Space runs
- **THEN** it ingests the 5 priority packages from `stedding/ingest_queue/pypi/`
- **AND** it writes to MotherDuck
- **AND** it runs the 5-stage Cognee + Graphiti cognify pass
- **AND** the Evidence dashboard renders the canonical 4 panels
