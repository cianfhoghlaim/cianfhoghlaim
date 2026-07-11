## ADDED Requirements

### Requirement: Nigeria pipeline obeys the cross-region contract

The system MUST route every Nigerian pipeline through the canonical
cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Nigerian federal files live at
`dlt/commonwealth/nga/<domain>/<source>.py`; state files live at
`dlt/commonwealth/nga/states/<state_slug>/<domain>/<source>.py`.

#### Scenario: A new Nigerian federal source obeys the contract

- **WHEN** a developer adds the NUC source
- **THEN** it MUST be created at
  `dlt/commonwealth/nga/education/nuc.py`
- **AND** its `source_id` MUST be
  `commonwealth.nga.education.nuc`
- **AND** it MUST NOT be created at `dlt/nigeria/nuc.py` or any
  other non-conformant path
