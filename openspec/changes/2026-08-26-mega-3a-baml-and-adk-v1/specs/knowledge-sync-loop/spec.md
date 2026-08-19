## ADDED Requirements

### Requirement: BAML sync layer (sync:baml) covers the 5 stage templates

The system SHALL extend the `knowledge-sync-loop` architecture to
include a `sync:baml` layer that validates the 5 BAML stage templates
across all 4 stages.

The reason: per `2026-08-15-baml-sync-loop-v1`, the BAML sync layer
already validates BAML health. This change extends it to cover the
5 stage templates.

#### Scenario: sync:baml validates all 5 stage templates

- **WHEN** the operator runs `mise run sync:baml`
- **THEN** the system reports the 5 templates' coverage:
 - `lc_extraction_template.baml` → 14 LC subjects
 - `junior_cycle_template.baml` → 8 JC subjects (the 8 NCCA priority)
 - `alevel_extraction_template.baml` → 15 A-Level × 3 boards
 - `gcse_extraction_template.baml` → 9 GCSE × 3 boards
 - `qpack_template.baml` → 46 subjects (cross-stage)
- **AND** any drift report is written to `stedding/sync-reports/baml-{date}.md`

### Requirement: baml:drift-docs extension for the 4-stage plane

The system SHALL extend `mise run lint:baml-drift-docs` to validate
that every AGENTS.md number claim (e.g., "the 4-stage plane covers
46 subjects across 4 stages") matches the ground-truth counts from
the 5 BAML stage templates.

#### Scenario: drift-docs catches stale subject counts

- **WHEN** the operator updates `lc_extraction_template.baml` to
  cover a 15th LC subject
- **THEN** `mise run lint:baml-drift-docs` flags the AGENTS.md files
  that still claim "14 LC subjects"
- **AND** the lint suggests the updated count