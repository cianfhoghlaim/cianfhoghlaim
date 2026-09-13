# openspec-cli-conventions Specification

## Purpose
Defines the canonical conventions for using openspec 1.11 in this repo —
how the CLI is invoked, how new changes are authored (`.openspec.yaml`,
ID convention, capabilities section), and which command-delivery profile
is in use — so contributors and agents produce consistent
openspec-changes bundles without re-deriving these choices per change.

## Requirements

### Requirement: The openspec CLI version is pinned at 1.11.0
The project SHALL use `@fission-ai/openspec@1.11.0` (installed globally
via `bun add -g @fission-ai/openspec@1.11.0`); `openspec --version`
SHALL report `1.11.0` and SHALL be re-verified before any quoted CLI
behaviour is cited.

#### Scenario: A contributor confirms the installed CLI version
- **WHEN** a contributor runs `openspec --version`
- **THEN** the output reports `1.11.0` (or a downstream patch release
  that 1.11.0 anchors to)
- **AND** no project-local install under `node_modules/@fission-ai/openspec`
  exists, since the install is global

### Requirement: `openspec doctor` reports the root healthy
The repo's openspec root SHALL include a valid `openspec/config.yaml`
(or `openspec/config.yml`) with at minimum `schema: spec-driven`, and
`openspec doctor` SHALL report `OpenSpec root: ok` when run from the
repo root.

#### Scenario: A contributor runs the doctor after a CLI upgrade
- **WHEN** a contributor runs `openspec doctor` from the repo root
- **THEN** the Root section reports `OpenSpec root: ok`
- **AND** no `Missing openspec/config.yaml` warning appears

### Requirement: New changes include a `.openspec.yaml` metadata file
Every new `openspec/changes/<id>/` directory created on or after
2026-09-02 SHALL include a `.openspec.yaml` declaring at minimum
`schema: spec-driven` and `created: YYYY-MM-DD`; the file SHALL set
`skip_specs: true` only when no spec-level behaviour change is part of
the change.

#### Scenario: A contributor authors a new change
- **WHEN** a contributor adds a new `openspec/changes/<id>/` directory
- **THEN** the directory contains a `.openspec.yaml` with `schema: spec-driven`
- **AND** if the change modifies no requirements, the file sets
  `skip_specs: true` and `openspec validate <id> --strict` accepts the
  zero-delta change

### Requirement: New change IDs follow the undated-kebab convention
New changes authored on or after 2026-09-02 SHALL use undated kebab IDs
(`add-dark-mode`), not dated-prefixed IDs
(`2026-09-02-add-dark-mode-v1`); existing dated IDs SHALL NOT be
bulk-renamed.

#### Scenario: A contributor names a new change
- **WHEN** a contributor authors a new change after 2026-09-02
- **THEN** the change's directory name contains no leading date prefix
  (e.g. `add-rag-pipeline`, not `2026-09-02-add-rag-pipeline-v1`)

### Requirement: The schema-vs-profile distinction is documented correctly
The `openspec/SKILL.md` and `openspec/AGENTS.md` SHALL describe openspec's
single schema (currently `spec-driven`) and the `/opsx:*`
command-delivery profile (`openspec config profile core|custom`) as
**independent axes**; adopting `/opsx:*` commands SHALL NOT require
migrating to a different schema, and the repo SHALL state which schema
and which profile are currently in use.

#### Scenario: A contributor reads the skill before adopting `/opsx:*`
- **WHEN** a contributor reads `.agents/skills/openspec/SKILL.md` and
  considers using `/opsx:*` commands
- **THEN** the skill explains that `/opsx:*` is a command-delivery
  profile, not a separate schema
- **AND** it states that switching the profile does NOT require
  re-archiving any pending change

### Requirement: Future dates SHALL NOT be encoded in change IDs
No new `openspec/changes/<id>/` directory created on or after 2026-09-02
SHALL encode a future or planned date in its ID; roadmap intent SHALL be
recorded in the change's `.openspec.yaml` `goal:` field or in
`openspec/plans/`, not in the ID.

#### Scenario: A contributor plans work for a future date
- **WHEN** a contributor creates a change meant to be worked on later
- **THEN** the change ID is undated kebab (e.g. `add-rag-pipeline`,
  not `2026-10-15-add-rag-pipeline-v1`)
- **AND** the roadmap intent lives in the `.openspec.yaml` `goal:` field
  or in `openspec/plans/<date>-<topic>-v1.md`
