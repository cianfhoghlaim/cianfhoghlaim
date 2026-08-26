# archive-tracking Specification

## Purpose

`archive-tracking` is a capability of the Cianfhoghlaim platform that
documents the 4 superseded openspec changes that are being archived
per the 2026-08-22-stale-changes-triage-v1 (Group B: CLOSE) decision.

This spec captures the tracking metadata for the 4 changes being
archived on 2026-08-22.

## ADDED Requirements

### Requirement: Archive the 4 superseded changes

The 4 superseded openspec changes SHALL be archived per the triage
decision. The canonical archive command is:
`openspec archive <change-id> --yes`.

#### Scenario: The 4 changes are archived

- **WHEN** `openspec list` runs
- **THEN** the 4 superseded changes SHALL NOT be in the active list
- **AND** they SHALL be in `openspec/changes/archive/2026-08-22-archive-4-superseded-changes-v1/`

### Requirement: Archive manifest is preserved
The system SHALL list all 4 superseded change IDs + their original `proposal.md`.
+ `tasks.md` + `specs/` for traceability.

#### Scenario: Archive manifest is intact

- **WHEN** `ls openspec/changes/archive/2026-08-22-archive-4-superseded-changes-v1/` runs
- **THEN** the result SHALL include all 4 change directories
- **AND** each SHALL have a valid `proposal.md` (not blank)

