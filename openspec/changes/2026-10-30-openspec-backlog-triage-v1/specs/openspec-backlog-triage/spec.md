# openspec-backlog-triage Specification

## Purpose
The repo has 126 active openspec changes (~80 with 0% progress, per
the live `openspec list --changes` count). The Stage 8 fresh-slate
handoff (`openspec/plans/2026-10-26-stage-8-fresh-slate-spec-handoff-v1.md`)
Gap 2 documents this as the 79-stalled-change backlog. This spec
captures the triage: 30 KEEP, 20 ARCHIVE-AS-RESEARCH, 29
ARCHIVE-AS-OUTDATED, 1 MERGE-INTO-OTHER.

The 30 KEEP changes get a 1-paragraph stub in each `proposal.md`.
The 49 ARCHIVE changes are moved to `openspec/changes/archive/`.
The 107 specs get a doctor pass + the STALE PATHS WARNING in
`openspec/project.md` is fixed. The 80 skills get the conformance
check (the 1 known failure is fixed).

Per the 2026-10-30-openspec-backlog-triage-v1 change (Umbrella 4 of
the 2026-10-30-platform-reset-saga-v1).

## ADDED Requirements

### Requirement: The 80 0/0-progress changes are triaged

The system MUST have classified all 80 changes with 0/0 progress as:
KEEP (30), ARCHIVE-AS-RESEARCH (20), ARCHIVE-AS-OUTDATED (29),
MERGE-INTO-OTHER (1) — per the Stage 8 Gap 2 breakdown. The 49
ARCHIVE changes MUST be moved to `openspec/changes/archive/`.

#### Scenario: An operator runs `openspec list --changes`
- **GIVEN** an operator wants to know the active change count
- **WHEN** they run `openspec list --changes`
- **THEN** it returns ≤ 80 entries (down from 126)

### Requirement: The 30 KEEP changes have a 1-paragraph "what this is for" stub

The system MUST have a 1-paragraph stub in the `proposal.md` of each
of the 30 KEEP changes that explains what the change is for. The
stubs are no-op docs (no code changes); they exist so future
operators can read the change's intent from the proposal instead of
from a 0/40 task list.

#### Scenario: A new operator reads a KEEP change
- **GIVEN** a new operator clones the repo and reads a KEEP change's `proposal.md`
- **WHEN** they look for the change's intent
- **THEN** they find a 1-paragraph stub explaining what the change is for and why it matters

### Requirement: `openspec 1.11 doctor` reports 0 warnings

The system MUST run `openspec 1.11 doctor` across all 107 specs and
fix the 0/zero warnings. The known warning is the STALE PATHS WARNING
in `openspec/project.md` (pre-v7 directory references).

#### Scenario: An operator runs `openspec 1.11 doctor`
- **GIVEN** an operator wants to check the spec health
- **WHEN** they run `openspec 1.11 doctor`
- **THEN** the report shows 0 warnings

### Requirement: The `media-intel-and-curriculum-hydration` spec is registered

The system MUST register the new `media-intel-and-curriculum-hydration`
spec in `openspec/list --specs`. The spec is already documented
(per the 2026-10-10-media-intel-and-curriculum-hydration-v1 change);
it just needs to be registered with `openspec list --specs`.

#### Scenario: A new operator searches for media-intel
- **GIVEN** a new operator wants to know what the media-intel surface is
- **WHEN** they run `openspec list --specs | grep media-intel`
- **THEN** they find the new spec entry

### Requirement: The 80 skills pass the conformance check

The system MUST run the `_tmp_lint.sh` style check (promoted to
`scripts/lint_skills.sh` per Umbrella 1 Group A4) across all 80
skills. The 1 known conformance failure MUST be fixed.

#### Scenario: A developer adds a new skill
- **GIVEN** a developer adds a new skill at `.agents/skills/<name>/SKILL.md`
- **WHEN** `mise run core:lint:skills` runs in CI
- **THEN** the skill passes the frontmatter conformance check (name matches dir, description ≥ 40 chars)

### Requirement: The openspec status dashboard renders

The system MUST provide a marimo notebook at
`notebooks/dashboards/openspec_status.py` AND a
`mise run openspec:status` task that both display: change count
(target ≤ 80), spec count (target 108), skill count, the
49-archived-this-week list.

#### Scenario: An operator wants to know the openspec state
- **GIVEN** an operator wants to see the openspec baseline
- **WHEN** they run `mise run openspec:status` OR open the marimo notebook
- **THEN** they see the 4 numbers + the 49-archived list

### Requirement: `openspec validate --strict` passes

The system MUST pass `openspec validate 2026-10-30-openspec-backlog-triage-v1 --strict`
before this change can be merged.

#### Scenario: A PR opens against main
- **GIVEN** a PR is opened for this change
- **WHEN** the CI workflow runs `openspec validate --strict`
- **THEN** the check passes
