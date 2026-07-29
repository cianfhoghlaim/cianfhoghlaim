## ADDED Requirements

### Requirement: BIEP v3 MotherDuck Flights operational (Phase 4 follow-up)

The 4 BIEP v3 MotherDuck Flights (`ireland_full_coverage_flight`,
`england_full_coverage_flight`, `sct_wls_ni_flight`,
`crown_dependencies_flight`) MUST execute successfully + emit Dagster
`RunRequest` events when invoked.

#### Scenario: 4 BIEP v3 Flights listed

- **WHEN** `dg list jobs | grep full_coverage` is run
- **THEN** exactly 4 BIEP v3 flight job names are listed

#### Scenario: Each flight emits a Dagster RunRequest

- **WHEN** `dg launch --job ireland_full_coverage_flight` is called
- **THEN** the Dagster event log MUST include at least 1 `RunRequest` event
  with `tags.jurisdiction = "ireland"`

(Same for england, sct_wls_ni, crown_dependencies.)

#### Scenario: MOTHERDUCK_TOKEN is available in dev

- **WHEN** `infisical secrets get MOTHERDUCK_TOKEN --env=dev-baile` is run
- **THEN** a non-empty token value is returned

#### Scenario: Locket sidecar populates env at runtime

- **WHEN** the lakehouse stack is deployed with the real Locket sidecar
- **THEN** `MOTHERDUCK_TOKEN` is injected into the running containers' env

### Requirement: Notebook migration to dual URI

The 8-jurisdiction + 12 corpus overview notebooks MUST support both
`md:cianfhoghlaim` (MotherDuck) and `ducklake:postgres:...` (local
DuckLake) via the `CIANFHOGHLAIM_USE_MOTHERDUCK` env var.

#### Scenario: MotherDuck path

- **WHEN** `CIANFHOGHLAIM_USE_MOTHERDUCK=true`
- **THEN** notebooks connect to `md:cianfhoghlaim`

#### Scenario: Local DuckLake path

- **WHEN** `CIANFHOGHLAIM_USE_MOTHERDUCK=false` (default)
- **THEN** notebooks connect to the `BIEP_REGISTRY_URI` env var