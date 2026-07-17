## MODIFIED Requirements

### Requirement: Marimo WASM export + testRuns.ingest wired to CI

The system SHALL require:
1. All 7 BIEP v3 jurisdiction dashboard notebooks
   (`notebooks/{18,19,20,21,22,23,40}_*.py`) to be exportable as
   WebAssembly bundles + a manifest
2. The `testRuns.ingest` endpoint to be wired to every CI run

#### Scenario: WASM bundles exported

- **WHEN** `bun run marimo:wasm:export` runs
- **THEN** 7+ WASM bundles SHALL exist in
  `web/apps/cianfhoghlaim-web/public/notebooks/`
- **AND** each bundle SHALL be reachable at `/notebooks/<num>_*` in the
  web app

#### Scenario: testRuns.ingest wired

- **WHEN** a CI run completes on `main`
- **THEN** `scripts/test_runs_ingest.py` SHALL be called with
  `passed`, `failed`, `runtime` args
- **AND** the dashboard at the configured URL SHALL reflect the new
  test history

#### Scenario: Dry-run payload valid

- **WHEN** `bun run test-runs:ingest --dry-run` runs
- **THEN** a valid JSON payload SHALL be returned matching the
  `testRuns.ingest` schema