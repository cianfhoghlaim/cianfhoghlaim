# SQLMesh — Data Transformation Framework

## Overview

SQLMesh is an open-source data transformation framework that brings software engineering best practices to SQL. It provides version-controlled SQL transformations, column-level lineage, automated testing, and a virtual data warehouse for development. Created by Tobiko Data, it is designed as a more rigorous alternative to dbt.

## Why This Matters for Kings' College Galway

The curriculum data pipeline involves dozens of SQL transformations: normalising exam paper metadata, aggregating grade distributions by subject/year, creating study path tables from prerequisite graphs, and computing RAGAS evaluation statistics. SQLMesh ensures these transformations are version-controlled, tested, and reproducible. The DuckDB virtual warehouse means developers can test transformations locally before deploying to MotherDuck, and column-level lineage provides an audit trail from raw syllabus data to the final study recommendation query.

## Key Features

- **Column-level lineage** — Trace every column from source to final output
- **Virtual data warehouse** — Test transformations on a subset of data without a real warehouse
- **Automated testing** — Unit tests for SQL models with fixture data
- **Semantic understanding** — SQLMesh understands SQL semantics, not just syntax
- **DuckDB integration** — First-class DuckDB support for local development

## Installation

```bash
uv add sqlmesh
```

## Integration with Our Stack

SQLMesh models live alongside dlt pipelines in the Dagster code location. Transformation runs are triggered by Dagster assets after dlt ingestion completes. The DuckDB virtual warehouse queries the Lakehouse Iceberg catalog for development/testing.

## Upstream

- **Repository**: <https://github.com/TobikoData/sqlmesh>
- **Documentation**: <https://sqlmesh.com>
- **Latest**: Active development (2025) — DuckDB virtual warehouse improvements, dbt project compatibility, CI/CD integration

## Screenshot

SQLMesh provides a CLI with plan/apply workflow (similar to Terraform). The `sqlmesh plan` command shows a diff of changes before applying. The `sqlmesh ui` command launches a web dashboard showing model dependency graphs, column lineage, and test results. The terminal output is colour-coded: green for passing tests, red for failures.
