## ADDED Requirements

### Requirement: EU nations + Ukraine pipeline obeys the cross-region contract

The system MUST route every new per-nation pipeline through the
canonical cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Per-nation files live at
`dlt/european_nations/<iso3>/<domain>/<source>.py` with the
canonical `source_id` + partition + DuckLake namespace contract.

#### Scenario: A new French statute-book source obeys the contract

- **WHEN** a developer adds the Légifrance source
- **THEN** it MUST be created at
  `dlt/european_nations/fra/law/legifrance.py`
- **AND** its `source_id` MUST be `european_nations.fra.law.legifrance`
- **AND** it MUST NOT be created at any legacy path
  (`dlt/eu/fra/law/`, `dlt/europeanunion/fra/law/`, etc.)
