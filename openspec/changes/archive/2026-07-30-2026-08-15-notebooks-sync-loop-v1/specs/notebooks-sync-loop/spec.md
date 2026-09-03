# Spec delta: notebooks-sync-loop

## ADDED Requirements

### Requirement: Layer 1 - sync:notebooks-drift
The system SHALL provide a sync:notebooks-drift task.

#### Scenario: Notebook drift detection runs
- **WHEN** scripts/sync/notebooks-drift.sh is invoked
- **THEN** the task scans all 119 notebook files
- **AND** detects unregistered notebooks, broken @app.cell decorators,
missing entry points, stale schema references

### Requirement: Layer 2 - sync:notebooks-ccc
The system SHALL provide a sync:notebooks-ccc task.

#### Scenario: 26th concept guide added
- **WHEN** scripts/sync/notebooks-ccc.sh is invoked
- **THEN** the task appends notebook-search to .cocoindex_code/guides.yml
- **AND** runs bun run ccc:index

### Requirement: Layer 3 - sync:notebooks-cognee
The system SHALL provide a sync:notebooks-cognee task.

#### Scenario: 15th Cognee cluster added
- **WHEN** scripts/sync/notebooks-cognee.sh is invoked
- **THEN** the task ingests 119 notebook files into the notebooks Cognee cluster

### Requirement: Layer 4 - sync:notebooks-test
The system SHALL provide a sync:notebooks-test task.

#### Scenario: Notebook import test runs
- **WHEN** scripts/sync/notebooks-test.sh is invoked
- **THEN** the task runs uv run python -c "import notebooks.X"

### Requirement: Layer 5 - sync:notebooks-lint
The system SHALL provide a sync:notebooks-lint task.

#### Scenario: Per-prefix stats
- **WHEN** scripts/sync/notebooks-lint.sh is invoked
- **THEN** the task produces per-prefix notebook stats

### Requirement: Notebooks evolution feedback loop
The system SHALL grow its knowledge surface over time via the
notebooks evolution feedback loop.

#### Scenario: Notebook change triggers re-cognify
- **WHEN** a notebooks/ file is modified
- **THEN** sync:notebooks-cognee detects the change
- **AND** re-cognifies into the notebooks Cognee cluster
