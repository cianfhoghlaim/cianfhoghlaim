## ADDED Requirements

### Requirement: The ciandlithe sister-repo umbrella mirror SHALL be tracked

The cianfhoghlaim monorepo SHALL maintain a
`ciandlithe-sister-umbrella-mirror-v1` openspec change at
`openspec/changes/2026-09-01-ciandlithe-sister-umbrella-mirror-v1/`
that tracks the 8 ciandlithe-side backlogs
(`ciandlithe-init-v1` + `ciandlithe-repo-foundation-v1` +
`ciandlithe-toolchain-repair-v1` + `ciandlithe-bipp-v2-crossref-v1` +
`ciandlithe-blig-v1-spec-v1` +
`ciandlithe-langfuse-prompt-mirror-v1` +
`ciandlithe-leabharlann-corpus-ingest-v1` +
`ciandlithe-ragas-eval-v1`) + the per-PR reciprocal mirror
contract + the per-quadrant DuckLake `metadata_schema` +
the per-sister Langfuse project mapping
(`ciandlithe-dev` + `ciandlithe-prod`).

#### Scenario: The ciandlithe mirror change is in the active openspec list

- **WHEN** the operator runs `uv run openspec list | grep ciandlithe-sister-umbrella-mirror`
- **THEN** the mirror change SHALL appear in the active list
- **AND** the mirror's `proposal.md` SHALL carry the 4 metadata fields
- **AND** `uv run openspec validate 2026-09-01-ciandlithe-sister-umbrella-mirror-v1 --strict` SHALL exit 0