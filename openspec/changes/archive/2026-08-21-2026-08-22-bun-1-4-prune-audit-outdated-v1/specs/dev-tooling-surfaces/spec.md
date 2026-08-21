# dev-tooling-surfaces — bun 1.4 (adopt latest + add outdated gate) (delta)

## Purpose

This delta extends `dev-tooling-surfaces` with the canonical adoption
of bun 1.4 (released 2026-08-20) + the new `core:bun:outdated` and
`core:bun:upgrade` tasks that surface dependency freshness.

## ADDED Requirements

### Requirement: bun-1-4-and-outdated-gate

The dev environment SHALL pin `bun@1.4` (or higher) in `package.json` and
provide 2 bun-related tasks in the `core` namespace:

1. `core:bun:outdated` — list outdated dependencies per workspace
2. `core:bun:upgrade` — one-command bun upgrade (uses `bun upgrade`)

#### Scenario: bun version pin is current

- **WHEN** the `package.json` is read
- **THEN** `packageManager` MUST be `bun@1.4` or higher
- **AND** the engines field MUST require `bun >= 1.4`

#### Scenario: bun outdated is the freshness gate

- **WHEN** `mise run core:bun:outdated` runs
- **THEN** the command MUST invoke `bun outdated`
- **AND** exit 0 with a list of outdated dependencies per workspace
- **AND** exit 1 if any critical dependency is >2 majors behind

#### Scenario: bun upgrade is the one-command update

- **WHEN** `mise run core:bun:upgrade` runs
- **THEN** the command MUST invoke `bun upgrade`
- **AND** exit 0 with the new bun version printed

## Cross-references

- `package.json` — the `packageManager` and `engines.bun` fields
- `bun.lock` — the current bun lockfile
- https://bun.com/1.4 — the 1.4 release post
- `openspec/specs/dev-tooling-surfaces/spec.md` — the canonical contract
