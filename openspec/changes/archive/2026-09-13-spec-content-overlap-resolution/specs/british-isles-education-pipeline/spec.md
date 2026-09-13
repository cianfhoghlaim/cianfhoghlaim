## ADDED Requirements

### Requirement: BIEP v3 5-milestone sequential plan (M0-M4)

The British Isles Education Pipeline SHALL follow the v3 5-milestone
sequential plan: M0 (foundation unblock) → M1 (extraction) → M2
(embedding) → M3 (ibis logging) → M4 (analytics). Each milestone
MUST archive before the next milestone begins.

#### Scenario: Milestones archive in order
- **WHEN** a contributor looks at the BIEP v3 roadmap
- **THEN** the 5 milestones SHALL be enumerated in M0-M4 order
- **AND** M(n+1) SHALL NOT begin until M(n) has archived

### Requirement: BIEP v3 4-cadence scheduling policy

The BIEP v3 pipeline SHALL use a 4-cadence scheduling policy: hourly
(heartbeat), daily (MotherDuck Flight backfill), weekly (full DAG
rebuild), and on-demand (BAML row backfill per cohort).

#### Scenario: 4 cadences are scheduled
- **WHEN** Dagster schedules are inspected
- **THEN** exactly 4 cron schedules SHALL be present (hourly,
      daily, weekly, on-demand)
- **AND** each cadence SHALL have at least 1 sensor + 1 job

### Requirement: OCR completion webhook convention

The BIEP v3 pipeline SHALL subscribe to an OCR completion webhook
(from the `meaisinfhoghlaim-ocr-htr` capability) via the
`ocr_completion_sensor` Dagster sensor. When a webhook fires, the
sensor triggers the next-stage extraction job for the matching
cohort.

#### Scenario: OCR completion triggers extraction
- **WHEN** the OCR webhook fires with a `cohort_id` matching an
      in-flight BIEP cohort
- **THEN** the `ocr_completion_sensor` SHALL trigger the cohort's
      extraction job within 5 seconds
- **AND** the next stage's idempotency token SHALL prevent duplicate
      extraction