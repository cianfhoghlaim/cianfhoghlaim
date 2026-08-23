## ADDED Requirements

### Requirement: core-lint-includes-spec-purpose

The `core:lint` task SHALL include `lint:spec:purpose` as a sub-gate
once all 100 specs have non-TBD Purpose fields. Per the
`2026-08-23-dev-tooling-tbd-purpose-refresh-batch-oideachais-specs-v1`
change (Phase 5.1.4 final wiring).

#### Scenario: core:lint runs lint:spec:purpose

- **WHEN** `mise run core:lint` runs
- **THEN** the depends DAG MUST include `lint:spec:purpose`
- **AND** `lint:spec:purpose` MUST exit 0 (no TBDs remaining)
- **AND** `core:lint` MUST exit 0
