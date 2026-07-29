## ADDED Requirements

### Requirement: EU institutional pipeline obeys the cross-region contract

The system MUST route every new EU institutional pipeline through the
canonical cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. EU institutional files live at
`dlt/european_union/<institution>/<source>.py` and obey the canonical
`source_id` + partition + DuckLake namespace contract.

#### Scenario: A new EU institutional source obeys the contract

- **WHEN** a developer adds a new EMA medicines register source
- **THEN** it MUST be created at
  `dlt/european_union/medicine/ema_medicines_register.py`
- **AND** its `source_id` MUST be
  `european_union.medicine.ema_medicines_register`
- **AND** its asset key MUST be
  `european_union.medicine.ema_medicines_register`
- **AND** it MUST NOT be created at the legacy paths
  (`dlt/eu/`, `dlt/european_union/ema.py`, etc.)
