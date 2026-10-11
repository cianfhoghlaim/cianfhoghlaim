# saga-closure Specification

## Purpose

After the 4 platform-reset umbrella PRs (#209 housekeeping, #210 BAML
repair, #211 openspec triage, #212 lakehouse bring-up) merged to main
on 2026-10-30, this spec captures the **saga-closure + follow-on-issue-repair**
contract. The closure is the 5th umbrella of the saga (not in the
original saga plan; added post-merge).

Per the 2026-10-30-saga-closure-and-baml-repair-v1 change.

## ADDED Requirements

### Requirement: `mise.toml` parses cleanly

The system MUST have a `mise.toml` that `tomllib.loads(open('mise.toml').read())`
parses without raising `tomllib.TOMLDecodeError`. Duplicate
`[tasks."<name>"]` blocks are forbidden.

#### Scenario: A second umbrella adds a task that an earlier umbrella also added

- **GIVEN** Umbrella A adds `[tasks."core:foo"]` and Umbrella B adds
  the same `[tasks."core:foo"]`
- **WHEN** both PRs merge to main
- **THEN** the merged `mise.toml` fails `tomllib.loads(...)` with a
  duplicate-key error
- **AND** the saga-closure change MUST remove the earlier occurrence
  (keeping the canonical version, identified by the simpler `run` command)

### Requirement: `scripts/lint_skills.sh` has no bash syntax errors

The system MUST have `scripts/lint_skills.sh` that passes `bash -n scripts/lint_skills.sh`
without raising a parse error. The argument-parsing loop MUST be a
`while [ $# -gt 0 ]; do case "$1" in ... esac; shift || true; done`
loop (not a `for arg in "$@"; do case "$arg" in ...; shift; esac; done`
loop, which is malformed because `shift` inside `for` skips the loop
iterator and the case patterns match against the literal token, not the
value).

#### Scenario: A developer runs `bash scripts/lint_skills.sh --limit 3`

- **GIVEN** the lint script's argument parsing has been rewritten
- **WHEN** the developer runs `bash scripts/lint_skills.sh --limit 3`
- **THEN** the script checks the first 3 skills and exits 0 (or 1 if
  any skill fails the frontmatter conformance check)

### Requirement: Lakehouse Umbrella 3 `tasks.md` reflects honest progress

The system MUST have `openspec/changes/2026-10-30-lakehouse-bridge-bring-up-v1/tasks.md`
with the **honest** breakdown: 7 tasks done, 14 tasks deferred, 21 tasks
total. The "done" count includes only the tasks whose artifacts shipped
(Group D's 3 marimo + mise tasks, Group E's 3 docs + validate + PR #212
merge, Group F2's skill-doc reference). The "deferred" count includes
all of Groups A/B/C (operator-side OrbStack + bridge bring-up + schema-naming
rollout), F1 (12-services smoke test), and F3 (subagent assignment).

#### Scenario: An operator reviews the lakehouse umbrella's tasks

- **GIVEN** the saga-closure change has reconciled `tasks.md`
- **WHEN** an operator reads the file
- **THEN** they see 21 task IDs (preserved from the original) with the
  honest `7 done / 14 deferred` distribution

### Requirement: Saga-deferred E1/G2/F3 boxes are ticked after merge

The system MUST have all "STATUS.md update" + "skill doc reference" +
"PR merge" boxes in the 3 merged-umbrella `tasks.md` files (housekeeping
D2, baml-repair F3, openspec-triage E3 for PR-merge; openspec-triage E1
for STATUS.md; baml-repair G2 + openspec-triage F2 for skill-doc) ticked
as done once the corresponding PRs merge to main.

#### Scenario: An operator reviews the 3 merged-umbrella tasks.md files

- **GIVEN** PRs #209, #210, #211 all merged on main
- **WHEN** the saga-closure change lands
- **THEN** the 3 `tasks.md` files have the PR-merge + STATUS.md-update +
  skill-doc-reference boxes ticked with attribution comments referencing
  the saga-closure change

### Requirement: `openspec/plans/STATUS.md` and the saga plan reflect closure

The system MUST have `openspec/plans/STATUS.md` with the 4 umbrellas
marked as ✓ MERGED with PR numbers + a new "Status: completed sagas"
section. The saga plan (`openspec/plans/2026-10-30-platform-reset-saga-v1.md`)
MUST have a ✓ CLOSED Status line + a "What was deferred" section listing
the 4 follow-on issues addressed by the saga-closure change.

#### Scenario: An operator scans the openspec/plans/ directory

- **GIVEN** the saga-closure change has shipped
- **WHEN** the operator reads `STATUS.md` + the saga plan
- **THEN** they see the platform-reset saga is ✓ CLOSED with the 4 PR
  numbers + the saga-closure change reference

### Requirement: `AGENTS.md` + `CHEATSHEET.md` reference the 8 new mise tasks

The system MUST have `AGENTS.md` with a "Top mise tasks" section listing
the 8 new tasks (`core:housekeeping:status`, `housekeeping:autofix`,
`core:lint:skills`, `core:lint:baml`, `core:baml:status`,
`core:openspec:status`, `core:lakehouse:health`, `core:lakehouse:up`)
plus the 4 marimo dashboards that consume them. The system MUST have
`CHEATSHEET.md` with the 6 new task rows added to the "Top 10 priority
mise tasks" table + the saga quick path flipped from "(proposed)" to
closed.

#### Scenario: A new operator reads `AGENTS.md` + `CHEATSHEET.md`

- **GIVEN** the saga-closure change has shipped
- **WHEN** the operator scans `AGENTS.md` "Top mise tasks" +
  `CHEATSHEET.md` "Top 10 priority mise tasks"
- **THEN** they see all 8 new `core:*` / `housekeeping:*` tasks listed
  with one-liner descriptions and PR-number attribution