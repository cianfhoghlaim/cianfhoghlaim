## ADDED Requirements

### Requirement: The tuatha sister-repo umbrella mirror SHALL be tracked

The cianfhoghlaim monorepo SHALL maintain a
`tuatha-sister-umbrella-mirror-v1` openspec change at
`openspec/changes/2026-09-01-tuatha-sister-umbrella-mirror-v1/`
that tracks the tuatha-side backlogs + the per-PR reciprocal
mirror contract + the per-quadrant DuckLake `metadata_schema` +
the per-sister Langfuse project mapping (`tuatha-dev` +
`tuatha-prod`).

The mirror MUST reference the
`2026-08-25-tuatha-british-isles-mmo-consolidation-v1/` and
the deprecated Babylon.js 3D MMO + SpacetimeDB v2 +
Pent-Elemental Cosmology + Crypteolas + Anam Cara + Brown Ajah
legacy theming (per the tuatha consolidation plan).

#### Scenario: The tuatha mirror change is in the active openspec list

- **WHEN** the operator runs `uv run openspec list | grep tuatha-sister-umbrella-mirror`
- **THEN** the mirror change SHALL appear in the active list
- **AND** the mirror's `proposal.md` SHALL carry the 4 metadata fields (sister-side backlogs + per-PR mirror path + DuckLake quadrant + Langfuse project)
- **AND** `uv run openspec validate 2026-09-01-tuatha-sister-umbrella-mirror-v1 --strict` SHALL exit 0