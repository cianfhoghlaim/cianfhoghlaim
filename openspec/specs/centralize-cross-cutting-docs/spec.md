# centralize-cross-cutting-docs Specification

## Purpose
TBD - created by archiving change 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1. Update Purpose after archive.
## Requirements
### Requirement: lint:drift-docs is the canonical anti-drift gate

The system SHALL provide a `mise run lint:drift-docs` task that
walks the 10 in-repo `AGENTS.md` files + `openspec/AGENTS.md` + the
root `AGENTS.md`, regex-extracts claims of the form
`(\d+) (specs|skills|stacks|models|notebooks)`, and validates each
against the ground truth derived from `openspec list --specs`,
`find .agents/skills -name SKILL.md`, `ls -d bonneagar/stacks/*/`,
`MODEL_REGISTRY.summary()["total"]`, and `find notebooks -name "*.py"`.

#### Scenario: A spec count drift is introduced

- **GIVEN** a new `openspec/specs/<name>/` is added
- **WHEN** the root `AGENTS.md` claims `78 specs` but the new spec
  brings the total to 79
- **THEN** `mise run lint:drift-docs` SHALL exit 1
- **AND** the lint SHALL report the 1 mismatch (claimed 78, actual 79)
- **AND** the lint SHALL write the per-rule result to
  `stedding/sync-reports/docs-drift-{date}.md` (JSON sibling at
  `stedding/sync-reports/docs-drift-{date}.json`)

#### Scenario: All claims are in sync

- **GIVEN** the root `AGENTS.md` claims `78 specs` and the actual count
  is 78 (all other claims similarly in sync)
- **WHEN** `mise run lint:drift-docs` runs
- **THEN** the lint SHALL exit 0
- **AND** the lint SHALL emit `OK: 0 number drift claims in 12 audited AGENTS.md files`

### Requirement: spec_agents.py runs on every PR that touches a spec

The system SHALL run `uv run python scripts/sync/spec_agents.py` on
every PR that touches `openspec/specs/<x>/spec.md` (via the
`.github/workflows/lint-drift-docs.yaml` workflow + the Forgejo
mirror).

#### Scenario: A PR adds a new spec

- **GIVEN** a PR adds `openspec/specs/my-new-spec/spec.md`
- **WHEN** the CI workflow runs
- **THEN** the workflow SHALL fail the PR if the sibling
  `openspec/specs/my-new-spec/AGENTS.md` is missing
- **AND** the PR author MUST either:
  1. Run `uv run python scripts/sync/spec_agents.py` locally and
     commit the generated `AGENTS.md`
  2. Or add the `AGENTS.md` manually but it MUST end with the
     `<!-- generated: ISO date; do not hand-edit -->` footer

#### Scenario: A PR edits an existing spec's `spec.md`

- **GIVEN** a PR edits `openspec/specs/existing-spec/spec.md`
- **WHEN** the CI workflow runs
- **THEN** the workflow SHALL detect the `spec.md` modification time
  is newer than the sibling `AGENTS.md`
- **AND** the workflow SHALL fail the PR if the `AGENTS.md` last-modified
  timestamp is older than the `spec.md` timestamp by more than 7 days
  (the generator should have been run by then)

### Requirement: Priority quick-reference sections are machine-checkable

The system SHALL treat the 6 *Priority* blocks in the root `AGENTS.md`
(Priority skills, Priority openspec commands, Priority compose stacks,
Priority openspec specs, Priority mise tasks, Priority sync commands)
as machine-checkable — no hand-edited integer claims (e.g. no
`7 of 153` written inline; the `7 of N` value SHALL be derived from
the count of the rows in the table).

#### Scenario: A developer hand-edits a number in the priority block

- **GIVEN** a developer edits `AGENTS.md` and changes `7 of 155` to
  `7 of 150` by hand
- **WHEN** `mise run lint:drift-docs` runs
- **THEN** the lint SHALL detect the row count (7) matches the table
  count but the claim (150) does not match the ground truth (155)
- **AND** the lint SHALL exit 1
- **AND** the lint SHALL suggest the fix: `7 of 155` (the ground truth)

#### Scenario: A new skill is added to the priority skills table

- **GIVEN** a developer adds a new row to the Priority skills table
  (making it 8 rows instead of 7)
- **WHEN** `mise run lint:drift-docs` runs
- **THEN** the lint SHALL verify the claimed count matches the row count
- **AND** the lint SHALL verify the claimed total (`8 of 155`) matches
  the ground truth (`find .agents/skills -name SKILL.md | wc -l`)

