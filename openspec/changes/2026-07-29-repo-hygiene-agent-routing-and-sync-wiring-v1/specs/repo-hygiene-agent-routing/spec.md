# Repo Hygiene Agent Routing

> **The convention that every `openspec/specs/<name>/` ships with a sibling `AGENTS.md` (≤30 lines) so an agent asked "how do I implement X for spec Y?" has a single, copied-into-context pointer to the right mise tasks, skills, and adjacent files.**

## ADDED Requirements

### Requirement: Per-spec AGENTS.md sibling

Every `openspec/specs/<name>/` directory SHALL ship with a sibling
`AGENTS.md` file that follows the canonical 6-section outline
(routing sentence, quick start, key sources, adjacent specs,
DO NOT, skill pointers) and is ≤30 lines.

#### Scenario: A new spec is added to `openspec/specs/<name>/`

- **GIVEN** a new spec directory is created (e.g. `openspec/specs/my-new-spec/`)
- **WHEN** the architect runs `uv run python scripts/sync/spec_agents.py`
- **THEN** the generator SHALL emit a sibling `AGENTS.md` from
  `openspec/specs/repo-hygiene-agent-routing/templates/spec-AGENTS.md.tmpl`
- **AND** the emitted `AGENTS.md` SHALL be ≤30 lines
- **AND** the emitted `AGENTS.md` SHALL end with the
  `<!-- generated: ISO date; do not hand-edit -->` footer

#### Scenario: An existing spec's `spec.md` is updated

- **GIVEN** `openspec/specs/<name>/spec.md` is modified
- **WHEN** `mise run sync:all` runs (or the generator is invoked directly)
- **THEN** the generator SHALL detect the `spec.md` modification time is
  newer than the sibling `AGENTS.md`
- **AND** the generator SHALL re-emit the `AGENTS.md` from the template
- **AND** the regenerated `AGENTS.md` SHALL preserve the
  `<!-- generated: ISO date; do not hand-edit -->` footer

### Requirement: Per-spec AGENTS.md lists the 2 most relevant mise tasks

Every per-spec `AGENTS.md` SHALL list the 2 most relevant `mise run`
tasks in the **Quick start** section, so an agent can copy-paste the
right invocation without reading the full `spec.md`.

#### Scenario: An agent reads the per-spec AGENTS.md

- **GIVEN** an agent is asked "how do I add a new jurisdiction to the
  British-Isles Education Pipeline?"
- **WHEN** the agent opens `openspec/specs/british-isles-education-pipeline-v3/AGENTS.md`
- **THEN** the **Quick start** section SHALL list the 2 most relevant
  mise tasks (e.g. `mise run sync:paths`, `mise run biep:v3:m0`)
- **AND** the agent SHALL be able to invoke them without further
  context loading

### Requirement: Per-spec AGENTS.md footer is machine-readable

Every per-spec `AGENTS.md` SHALL end with the footer
`<!-- generated: ISO date; do not hand-edit -->` where the ISO date
matches the date the generator last emitted the file.

#### Scenario: A developer hand-edits a per-spec AGENTS.md

- **GIVEN** a developer opens `openspec/specs/<name>/AGENTS.md` and
  edits it by hand
- **WHEN** the generator runs
- **THEN** the generator SHALL detect the footer is missing or the
  date is older than the spec's `spec.md`
- **AND** the generator SHALL overwrite the hand-edited file with the
  template-rendered version (the convention is "generator wins, not hand-edits")
- **AND** the convention is documented in the `repo-hygiene-agent-routing`
  spec's `## Purpose` section so the behaviour is discoverable

## Cross-references

- `scripts/sync/spec_agents.py` — the generator (Phase 4 deliverable)
- `openspec/specs/repo-hygiene-agent-routing/templates/spec-AGENTS.md.tmpl` — the template
- `openspec/specs/centralize-cross-cutting-docs/spec.md` — the anti-drift contract that
  enforces this convention via CI
- `openspec/specs/knowledge-sync-loop/spec.md` — Layer 4 (skills sync) reuses the
  generator pattern for per-skill AGENTS.md (future extension)
