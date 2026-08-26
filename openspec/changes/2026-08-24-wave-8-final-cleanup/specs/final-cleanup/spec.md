# final-cleanup Specification

## Purpose

`final-cleanup` is the post-cascade gate that finalizes the 8-wave
2026-08-24 master refactor. After this spec is implemented:

- All 8 wave commits are tagged as `v2026.08.24-wave8-cascade-complete`
- `lint:drift-docs` passes with 0 drift claims
- The master plan reflects the 8-wave (not 7-wave) status
- A cumulative audit summary is captured in the Wave 8 openspec

## ADDED Requirements

### Requirement: 8-wave master plan

`openspec/plans/2026-08-24-master-refactor-plan.md` §1.4 SHALL reflect
the 8-wave (not 7-wave) status.

#### Scenario: Master plan has 8 waves

- **WHEN** `grep "Wave 8" openspec/plans/2026-08-24-master-refactor-plan.md` runs
- **THEN** at least 1 occurrence is found

### Requirement: lint:drift-docs passes

`mise run lint:drift-docs` SHALL exit 0 (no drift claims) at the
end of the cascade.

#### Scenario: Zero drift

- **WHEN** `uv run python scripts/lint_drift_docs.py --dry-run` runs
- **THEN** the output is `OK: 0 number drift claims in 15 audited AGENTS.md files`

### Requirement: Cascade tag

The git tag `v2026.08.24-wave8-cascade-complete` SHALL exist after
Wave 8 is committed and pushed.

#### Scenario: Tag exists

- **WHEN** `git tag -l | grep wave8` runs
- **THEN** `v2026.08.24-wave8-cascade-complete` is in the list

### Requirement: Audit summary captured

The Wave 8 openspec `proposal.md` SHALL include the cumulative
audit summary (commit hashes + line counts + drift result + final
counts for assets / sensors / pipelines / destinations / apps / packages).

#### Scenario: Audit summary exists

- **WHEN** `grep "Cumulative totals" openspec/changes/2026-08-24-wave-8-final-cleanup/proposal.md` runs
- **THEN** at least 1 occurrence is found

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Wave 0-7: see prior openspec changes
- Audit report: `stedding/sync-reports/docs-drift-2026-08-24.md`
