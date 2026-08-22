## MODIFIED Requirements

### Requirement: spec-purpose-duckdb-ducklake-lakehouse-hydration (MODIFIED)

The Purpose field of this spec MUST be a non-TBD statement that summarizes the spec's topic, scope, and key invariants. Per the 2026-08-23-dev-tooling-tbd-purpose-refresh-batch-data-specs-v1 change.

#### Scenario: DuckLake Purpose is non-TBD

- **WHEN** `grep "TBD" openspec/specs/duckdb-ducklake-lakehouse-hydration/spec.md` runs
- **THEN** it MUST NOT return any match in the `## Purpose` section
