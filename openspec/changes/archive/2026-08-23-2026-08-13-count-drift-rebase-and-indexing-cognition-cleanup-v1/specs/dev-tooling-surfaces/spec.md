# Spec Delta: dev-tooling-surfaces

## ADDED Requirements

### Requirement: `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1` superseded

The system SHALL recognize that the count-drift rebase + INDEXING_AND_COGNITION cleanup change is already done implicitly by the linter. `mise run lint:drift-docs` reports 0 drift; the per-area AGENTS.md regeneration (`mise run sync:spec-agents`) is idempotent.

Per the 2026-08-22-stale-changes-triage-v1 (Group B: CLOSE).

#### Scenario: Lint drift is zero

- **WHEN** an agent runs `mise run lint:drift-docs`
- **THEN** the linter reports 0 drift
- **AND** no manual rebase is needed