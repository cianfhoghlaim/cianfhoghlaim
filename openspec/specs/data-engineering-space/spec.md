# data-engineering-space Specification

## Purpose
The data-engineering HuggingFace Space (`spaces/data-engineering/`) — the Dagster + dbt + Evidence dashboard that queries the public PyPI Packages dataset and surfaces a Python 🐍 OLAP Tool Popularity Comparison.

## Requirements
### Requirement: data-engineering Space must use the KCG canonical stack

The data-engineering Space MUST consume the KCG canonical stack:
- **Source**: `stedding/ingest_queue/pypi/` (the KCG pattern), not BigQuery
- **Destination**: MotherDuck (the canonical lakehouse), not local DuckDB
- **dbt**: dbt-duckdb (the canonical adapter), not raw dbt
- **Knowledge graph**: Cognee + Graphiti, via the canonical `agent-memory-systems` skill

The Space's PyPI dataset is the canonical "data plane" example
for the 94 Docker Compose stacks (the `lakehouse` stack is the
source; this Space is the consumer).

#### Scenario: Modernized data-engineering Space

- **WHEN** the data-engineering Space runs
- **THEN** it reads from `stedding/ingest_queue/pypi/` (not BigQuery)
- **AND** it writes to MotherDuck (not local DuckDB)
- **AND** it uses dbt-duckdb (not raw dbt)
- **AND** it has a Cognee + Graphiti cognify pass that surfaces
  the canonical "PyPI download trends" knowledge graph
