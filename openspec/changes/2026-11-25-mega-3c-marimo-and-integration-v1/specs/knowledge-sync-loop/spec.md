## ADDED Requirements

### Requirement: sync:baml extension for the 5 stage templates (Phase 5)

The system SHALL extend the `knowledge-sync-loop` architecture with a
`sync:baml` layer that validates the 5 BAML stage templates
(`lc_extraction_template.baml`, `junior_cycle_template.baml`,
`alevel_extraction_template.baml`, `gcse_extraction_template.baml`,
`qpack_template.baml`).

#### Scenario: sync:baml validates all 5 templates

- **WHEN** the operator runs `mise run sync:baml`
- **THEN** the system reports each template's coverage:
 - `lc_extraction_template.baml` → 14 LC subjects
 - `junior_cycle_template.baml` → 8 JC subjects
 - `alevel_extraction_template.baml` → 15 A-Level × 3 boards
 - `gcse_extraction_template.baml` → 9 GCSE × 3 boards
 - `qpack_template.baml` → 46 subjects (cross-stage)
- **AND** any drift report is written to `stedding/sync-reports/baml-{date}.md`