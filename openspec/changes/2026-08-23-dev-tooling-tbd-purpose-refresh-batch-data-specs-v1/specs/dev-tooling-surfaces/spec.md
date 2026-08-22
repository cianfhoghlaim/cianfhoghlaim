## ADDED Requirements

### Requirement: lint-spec-purpose

The dev environment SHALL expose a `lint:spec:purpose` task that
fails CI if any spec under `openspec/specs/*/spec.md` still has a TBD
Purpose field (the standard openspec archive stamp
`## Purpose: TBD - created by archiving change X. Update Purpose after archive.`).

#### Scenario: lint:spec:purpose exits 0 when all specs are filled

- **WHEN** `mise run lint:spec:purpose` runs
- **AND** every spec under `openspec/specs/*/spec.md` has a non-TBD
  Purpose section
- **THEN** the command MUST exit 0
- **AND** the output MUST report the count of specs with non-TBD
  Purposes

#### Scenario: lint:spec:purpose exits 1 when any spec is TBD

- **WHEN** `mise run lint:spec:purpose` runs
- **AND** at least 1 spec still has a TBD Purpose field
- **THEN** the command MUST exit 1
- **AND** the output MUST list each TBD spec by name

#### Scenario: core:lint includes lint:spec:purpose

- **WHEN** `mise run core:lint` runs
- **THEN** the depends DAG MUST include: `lint:skills`, `lint:registry`,
  `core:typecheck`, `core:uv:audit:strict`, `core:uv:check`,
  `lint:spec:purpose`
- **AND** all 6 gates MUST pass before `core:lint` exits 0
