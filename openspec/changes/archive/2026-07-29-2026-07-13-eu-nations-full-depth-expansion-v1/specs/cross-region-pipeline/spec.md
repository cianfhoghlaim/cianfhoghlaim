## ADDED Requirements

### Requirement: EU full-depth pipeline obeys the cross-region contract

The system MUST route every per-subject DLT source for the EU
nations full-depth expansion through the canonical cross-region
path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Per-subject files live at
`dlt/european_nations/<iso3>/education/subjects/<subject>.py`.

#### Scenario: A new Czech mathematics source obeys the contract

- **WHEN** a developer adds the CZE mathematics source
- **THEN** it MUST be created at
  `dlt/european_nations/cze/education/subjects/mathematics.py`
- **AND** its `source_id` MUST be
  `european_nations.cze.education.subjects.mathematics`
- **AND** it MUST NOT be created at `dlt/czechia/mathematics.py` or
  any other non-conformant path
