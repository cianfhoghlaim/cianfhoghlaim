## ADDED Requirements

### Requirement: Commonwealth of Nations pipeline obeys the cross-region contract

The system MUST route every new Commonwealth pipeline through the
canonical cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Commonwealth files live at
`dlt/commonwealth/<iso3>/<domain>/<source>.py` (per-nation) or
`dlt/commonwealth/official/<source>.py` (institutional).

#### Scenario: A new Australian curriculum source obeys the contract

- **WHEN** a developer adds the ACARA source
- **THEN** it MUST be created at `dlt/commonwealth/aus/education/acara.py`
- **AND** its `source_id` MUST be `commonwealth.aus.education.acara`
- **AND** it MUST NOT be created at `dlt/aus/acara.py` or any other
  non-conformant path
