## ADDED Requirements

### Requirement: British Isles path contract is one instance of the global cross-region contract

The system MUST treat the BIEP v1 path contract (`dlt/british_isles/<nation>/<domain>/<source>.py`)
as the seed instance of the canonical cross-region contract
declared by the [`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. v2 cross-nation expansion (Scotland / Wales / England /
NI / Crown Dependencies), the EU institutional expansion, and the EU
nations + Ukraine expansion MUST all reuse this contract verbatim.

#### Scenario: A v2 cross-nation expansion obeys the new global contract

- **WHEN** the BIEP v2 cross-nation expansion adds a new Scottish
  SQA source
- **THEN** it SHALL be created at
  `dlt/british_isles/scotland/education/sqa/syllabus_source.py`
  (the existing on-disk path), not at `dlt/sct/education/sqa/` or
  any new shortened alias
- **AND** its `source_id` SHALL be
  `british_isles.scotland.education.sqa.syllabus`
- **AND** its asset key SHALL match the canonical 5-layer group
  name `1_ingestion/curriculum/sct`
