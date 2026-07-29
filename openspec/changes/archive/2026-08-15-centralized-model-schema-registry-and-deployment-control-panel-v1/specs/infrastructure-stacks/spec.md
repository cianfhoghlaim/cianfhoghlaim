# Spec delta: `infrastructure-stacks`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It registers `deployment-choice.yaml` as the canonical enablement
file for the 88+ Docker Compose stacks.

## ADDED Requirements

### Requirement: deployment-choice.yaml is the canonical enablement file for the 88+ stacks

The system SHALL register `deployment-choice.yaml` (committed, ~100
LOC) as the canonical enablement file for the 88+ Docker Compose
stacks in `bonneagar/stacks/`. The file SHALL have a section
`enabled_stacks: dict[str, bool]` listing every stack with on/off
toggle. The CLI + marimo + web UI all read from and write to this
file.

#### Scenario: enabled_stacks section is populated

- **GIVEN** the `deployment-choice.yaml` committed
- **WHEN** the operator reads the file
- **THEN** the `enabled_stacks` section contains every Docker Compose
  stack with `true` (except for any stacks marked as
  `disabled_by_default: true` in `bonneagar/stacks/INDEX.md`)

#### Scenario: Stack toggle writes deployment-choice.yaml

- **GIVEN** the marimo notebook open with Tab 4 "Stacks" visible
- **WHEN** the operator toggles off `lakehouse` and clicks "Save"
- **THEN** `deployment-choice.yaml` is updated with
  `enabled_stacks: {lakehouse: false, ...}`