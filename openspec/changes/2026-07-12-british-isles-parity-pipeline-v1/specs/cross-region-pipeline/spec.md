## ADDED Requirements

### Requirement: British Isles parity pipeline obeys the cross-region contract

The system MUST route every British Isles per-nation + per-subject
pipeline through the canonical cross-region path contract
declared by the [`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Per-nation + per-subject files live at
`dlt/british_isles/<nation>/<domain>/<source>.py` (matching the
existing British Isles contract).

#### Scenario: A new Scottish per-subject source obeys the contract

- **WHEN** a developer adds a new SQA mathematics source
- **THEN** it MUST be created at
  `dlt/british_isles/scotland/education/subjects/mathematics.py`
- **AND** its `source_id` MUST be
  `british_isles.scotland.education.subjects.mathematics`
- **AND** it MUST NOT be created at
  `dlt/scotland/mathematics.py` or any other non-conformant path
