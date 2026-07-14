## ADDED Requirements

### Requirement: BIEP v2 England change sensor

The system SHALL provide 1 Dagster sensor at
`orchestration/defs/sensors/england_change_detection_sensor.py` that
re-runs the Change 2 England BAML extraction whenever a ChangeDetection.io
monitor (per `infrastructure-stacks/spec.md` Requirement "ChangeDetection.io
for England awarding bodies") fires for any of the 3 awarding bodies.

The sensor MUST:

- Subscribe to the 3 ChangeDetection.io webhook endpoints (one per board)
- Resolve to the per-board DAG asset key (e.g.
  `eng_aqa_mathematics_ingested` for an AQA maths change)
- Trigger the dagster job `england_england_re_extraction_job`
- Emit a Langfuse trace event with the change metadata
- Write an audit row to
  `oideachais.education.british_isles.england.changes`

#### Scenario: England AQA GCSE math change triggers re-extraction

- **GIVEN** the ChangeDetection.io `aqa_monitor.yaml` fires for the
  GCSE Mathematics specification page
- **WHEN** the webhook posts to the sensor
- **THEN** the sensor resolves
  `asset_key=eng_aqa_mathematics_ingested`
- **AND** the dagster job `england_england_re_extraction_job` materialises
- **AND** the re-extraction produces the 4-path ensemble output + the
  voted canonical row
- **AND** the audit table `oideachais.education.british_isles.england.changes`
  records the change with `ragas_score` and `extraction_status='success'`
