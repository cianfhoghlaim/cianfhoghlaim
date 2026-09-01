## ADDED Requirements

### Requirement: The ciancheiltis sister-repo umbrella mirror SHALL be tracked

The cianfhoghlaim monorepo SHALL maintain a
`ciancheiltis-sister-umbrella-mirror-v1` openspec change at
`openspec/changes/2026-09-01-ciancheiltis-sister-umbrella-mirror-v1/`
that tracks the ciancheiltis-side backlogs (the leanest of the
6 sister backlogs — only 1 change: `ciancheiltis-init-v1`) +
the per-PR reciprocal mirror contract + the per-quadrant
DuckLake `metadata_schema` + the per-sister Langfuse project
mapping (`ciancheiltis-dev` + `ciancheiltis-prod`).

#### Scenario: The ciancheiltis mirror change is in the active openspec list

- **WHEN** the operator runs `uv run openspec list | grep ciancheiltis-sister-umbrella-mirror`
- **THEN** the mirror change SHALL appear in the active list
- **AND** the mirror's `proposal.md` SHALL carry the 4 metadata fields
- **AND** `uv run openspec validate 2026-09-01-ciancheiltis-sister-umbrella-mirror-v1 --strict` SHALL exit 0