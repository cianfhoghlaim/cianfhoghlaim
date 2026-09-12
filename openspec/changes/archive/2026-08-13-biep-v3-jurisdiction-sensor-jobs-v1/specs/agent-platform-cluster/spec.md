## ADDED Requirements

### Requirement: No dangling `job_name=` in registry sensors

The system SHALL ensure that every `@sensor(job_name=...)` in
`orchestration/sensors/` has a corresponding `define_asset_job` defined
in `orchestration/sensors/jobs.py` whose `name=` matches the sensor's
`job_name=` argument. Each job SHALL select the canonical
`<jurisdiction>_documents_ingested` asset for its jurisdiction (8
assets in total: `ireland_documents_ingested`,
`scotland_documents_ingested`, `northern_ireland_documents_ingested`,
`wales_documents_ingested`, `england_documents_ingested`,
`isle_of_man_documents_ingested`, `jersey_documents_ingested`,
`guernsey_documents_ingested`).

The system MUST provide a `mise run lint:dagster:sensor-job-coverage`
CI gate that fails the build if any sensor's `job_name=` has no
matching `define_asset_job` in the `orchestration.sensors.jobs`
module.

#### Scenario: Sensor with dangling `job_name=` is rejected at lint

- **GIVEN** a developer adds a new `MyJurisdictionRegistrySensor`
  in `orchestration/sensors/my_jurisdiction_registry_sensor.py` with
  `@sensor(job_name="my_jurisdiction_registry_change_job")`
- **WHEN** `mise run lint:dagster:sensor-job-coverage` runs
- **THEN** the lint fails with
  `dangling_job_name: my_jurisdiction_registry_change_job — no
  define_asset_job found in orchestration/sensors/jobs.py`
- **AND** the developer is forced to define the job before the
  change can ship

#### Scenario: All 8 BIEP v3 jurisdictions have wired jobs

- **GIVEN** the 8 jurisdiction registry sensors are present in
  `orchestration/sensors/`
- **WHEN** `dagster job list | grep -E "registry_change_job"`
  executes against the live code-location
- **THEN** the command returns exactly 8 lines:
  `ncca_registry_change_job`, `sqa_registry_change_job`,
  `ccea_registry_change_job`, `wjec_registry_change_job`,
  `jcq_registry_change_job`, `isle_of_man_registry_change_job`,
  `jersey_registry_change_job`, `guernsey_registry_change_job`
- **AND** each job's `selection=` includes the canonical
  `<jurisdiction>_documents_ingested` asset for its jurisdiction

#### Scenario: Sensor tick produces a resolvable RunRequest

- **GIVEN** the `ncca_registry_sensor` detects a new Ireland cohort
- **WHEN** the sensor emits a `RunRequest`
- **THEN** Dagster's job-resolution resolves
  `ncca_registry_change_job` to the `define_asset_job` in
  `orchestration/sensors/jobs.py`
- **AND** the `RunRequest` launches successfully (no
  `JobNotFoundError` in the launch logs)
- **AND** the `ireland_documents_ingested` asset materialises
