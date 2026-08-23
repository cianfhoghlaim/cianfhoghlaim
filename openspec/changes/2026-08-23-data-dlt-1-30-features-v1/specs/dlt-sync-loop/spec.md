## ADDED Requirements

### Requirement: dlt-1-30-tasks

The `data:dlt:*` task namespace SHALL expose DLT 1.30+ features via 3
new tasks. Per the `2026-08-23-data-dlt-1-30-features-v1` change.

#### Scenario: data:dlt:refresh exists and uses the refresh write_disposition

- **WHEN** `mise run data:dlt:refresh -- <pipeline_name>` runs
- **THEN** the command MUST invoke `dlt pipeline <pipeline_name> refresh`
- **AND** the command MUST exit 0 on success or 1 on failure

#### Scenario: data:dlt:hub:install adds the dlthub plugin

- **WHEN** `mise run data:dlt:hub:install` runs
- **THEN** it MUST run `uv add dlt[hub]` (or equivalent)
- **AND** the plugin MUST be available in the current venv

#### Scenario: data:dlt:hub:deploy scaffolds a deployment manifest

- **WHEN** `mise run data:dlt:hub:deploy -- <pipeline> <destination>` runs
- **THEN** it MUST invoke `dlt deploy <pipeline> <destination>`
- **AND** a deployment manifest MUST be created (or surfaced for review)