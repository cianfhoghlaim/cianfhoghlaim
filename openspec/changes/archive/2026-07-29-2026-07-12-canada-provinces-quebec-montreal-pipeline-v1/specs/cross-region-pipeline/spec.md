## ADDED Requirements

### Requirement: Canada provinces obey the cross-region contract

The system MUST route every new Canadian provincial pipeline
through the canonical cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Provincial files live at
`dlt/commonwealth/can/<prov>/<domain>/<source>.py` with the
canonical `source_id` + partition + DuckLake namespace contract.

#### Scenario: A new Quebec education source obeys the contract

- **WHEN** a developer adds the MEES source
- **THEN** it MUST be created at
  `dlt/commonwealth/can/qc/education/mees.py`
- **AND** its `source_id` MUST be
  `commonwealth.can.qc.education.mees`
- **AND** it MUST NOT be created at `dlt/canada/qc/mees.py` or any
  other non-conformant path
