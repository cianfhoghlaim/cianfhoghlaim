# dev-tooling-surfaces — OPSX schema migration plan (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the canonical
documentation of the OPSX schema migration plan. No actual migration
is performed — this is a planning change only.

## MODIFIED Requirements

### Requirement: openspec-schema-stability

The repository SHALL remain on the legacy `spec-driven` schema
(proposal + tasks + spec deltas under `openspec/changes/<id>/`).
The OPSX schema (YAML + Markdown templates, DAG dependencies, status
command) is **documented as the future migration target** but is
**time-boxed**: the next 3 changes following this one SHALL pilot
the OPSX schema in a subdirectory (e.g. `openspec/changes/opsx-pilot/`),
and a follow-up change SHALL adopt OPSX as the default schema for
all NEW changes.

#### Scenario: legacy spec-driven remains the default

- **WHEN** a new openspec change is created
- **THEN** the canonical structure SHALL be `proposal.md` + `tasks.md` + `specs/<capability>/spec.md` (the legacy spec-driven schema)
- **AND** the change SHALL pass `openspec validate --strict`

#### Scenario: OPSX pilot subdirectory is the time-box

- **WHEN** the next 3 changes are created after this change is archived
- **THEN** at least 1 of them SHALL pilot the OPSX schema (using `openspec schema fork spec-driven my-pilot-schema`)
- **AND** the pilot change SHALL be in a clearly-marked subdirectory (e.g. `openspec/changes/opsx-pilot/`)

#### Scenario: OPSX adoption is the follow-up

- **WHEN** a follow-up change evaluates the pilot
- **THEN** the follow-up SHALL either:
  - Adopt OPSX as the default schema for all NEW changes (if pilot succeeded), OR
  - Iterate on the pilot (if pilot had issues)

## Cross-references

- `proposal.md` of this change — the full migration strategy
- https://github.com/Fission-AI/OpenSpec/blob/main/docs/opsx.md — the OPSX schema docs
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
