## ADDED Requirements

### Requirement: dagster-1-13-cli-tasks

The `data:dagster:*` task namespace SHALL expose Dagster 1.13+ features
via 3 new tasks. Per the `2026-08-23-data-dagster-1-13-features-v1`
change.

#### Scenario: data:dagster:list-assets exists and returns assets

- **WHEN** `mise run data:dagster:list-assets` runs
- **THEN** the command MUST emit a JSON list of all Dagster assets
- **AND** the list MUST contain ≥ 199 assets
- **AND** each entry MUST include `key`, `group`, `kinds`, `description`

#### Scenario: data:dagster:materialize exists

- **WHEN** `mise run data:dagster:materialize -- lc5_mathematics_ingested` runs
- **THEN** it MUST materialize the named asset via the `dg launch` CLI
- **AND** the command MUST exit 0 on success or 1 on failure (with logs)

#### Scenario: data:dagster:cli-info exists

- **WHEN** `mise run data:dagster:cli-info` runs
- **THEN** it MUST emit the 5 KCG component paths
- **AND** the output MUST be valid YAML or JSON
