## ADDED Requirements

### Requirement: Americas pipeline obeys the cross-region contract

The system MUST route every new Americas pipeline through the canonical
cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Americas files live at
`dlt/americas/<jurisdiction>/<domain>/<source>.py` with the canonical
`source_id` + partition + DuckLake namespace contract.

#### Scenario: A new California education source obeys the contract

- **WHEN** a developer adds the CDE source
- **THEN** it MUST be created at
  `dlt/americas/us/us_ca/education/cde.py`
- **AND** its `source_id` MUST be
  `americas.us.us_ca.education.cde`
- **AND** it MUST NOT be created at `dlt/california/cde.py` or any
  other non-conformant path
