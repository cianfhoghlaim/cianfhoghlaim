# Spec delta: `infrastructure-stacks`

This change adds 1 requirement to the existing `infrastructure-stacks`
spec: the canonical stack count moves from `88` to `89` (the
`pdf-factory` stack added by the 2026-07-17 v7 flattening merged the
canonical IaC into the repo root, and the `cic:stack-doctor` gate
already validates against the live count).

## ADDED Requirements

### Requirement: Stack count is derived from the filesystem, not hardcoded

The system SHALL derive the canonical stack count from the live
filesystem (`ls -d bonneagar/stacks/*/ | wc -l`), not from a hardcoded
constant in `AGENTS.md` or any documentation.

#### Scenario: A new stack is added to `bonneagar/stacks/<name>/`

- **GIVEN** a new stack directory is created at `bonneagar/stacks/<new>/`
- **WHEN** `mise run cic:stack-doctor` runs
- **THEN** the gate SHALL validate the new stack against the 6-file
  GOLD_STANDARD pattern
- **AND** the live stack count SHALL be one higher than before
- **AND** the `AGENTS.md` priority-quick-reference claim SHALL auto-update
  on the next `mise run lint:drift-docs` cycle (the mismatch is detected
  and the fix is suggested)

#### Scenario: The priority-quick-reference claim is stale

- **GIVEN** the live stack count is 89 but `AGENTS.md` claims `88`
- **WHEN** `mise run lint:drift-docs` runs (per the
  `centralize-cross-cutting-docs` spec)
- **THEN** the lint SHALL detect the mismatch (claimed 88, actual 89)
- **AND** the lint SHALL exit 1
- **AND** the lint SHALL suggest the fix: replace `88` with `89` in
  the 3 sites where the claim appears in `AGENTS.md` (the
  *Priority quick reference*, the *Infrastucture Tasks (moved to
  bonneagar)* section, and the README telemetry block)

#### Scenario: All stack claims are in sync

- **GIVEN** the live stack count is 89 and `AGENTS.md` claims `89`
  (in all 3 sites)
- **WHEN** `mise run lint:drift-docs` runs
- **THEN** the lint SHALL emit `OK: 0 stack count drift claims across 12 audited AGENTS.md files`
- **AND** the lint SHALL exit 0

## Cross-references

- `mise run cic:stack-doctor` — the GOLD_STANDARD pattern validator
- `scripts/stack-doctor.sh` — the underlying script
- `openspec/specs/centralize-cross-cutting-docs/spec.md` — the
  `lint:drift-docs` anti-drift gate that enforces this requirement
- `AGENTS.md` — the 3 sites where the stack count claim lives
