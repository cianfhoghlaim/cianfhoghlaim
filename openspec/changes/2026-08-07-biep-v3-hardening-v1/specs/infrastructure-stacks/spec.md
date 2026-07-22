## MODIFIED Requirements

### Requirement: BIEP v3 stack hardening (P1)

The system SHALL have:
1. Canonical 3 BAML clients (BIEPV3Extract / BIEPV3ExtractStrong / BIEPV3Vision)
2. CI gate for `baml-cli generate` + `baml-cli check` + drift check
3. 8 jurisdiction sensors (5 existing + 3 Crown Dependencies)
4. 1 Garage S3 PDF-arrival sensor
5. Jurisdiction pipeline base class (no copy-paste across the 4 pipelines)
6. DuckLake connection pool + time-travel helper
7. `mode` + `tenant` + `iceberg` flags on the destination factory
8. Snapshots + Shares for MotherDuck

#### Scenario: BAML canonical clients

- **WHEN** `grep -rE "client (ExtractEn|ExtractEnStrong|LlamaSwap)" baml_src/british_isles/`
  runs
- **THEN** 0 matches SHALL appear (all routes through the 3 canonical clients)

#### Scenario: CI gate

- **WHEN** a PR touches `baml_src/**`
- **THEN** the `baml-cli generate` + `baml-cli check` + drift check steps
  SHALL pass before the PR can merge

#### Scenario: 8 sensors + 1 S3 sensor

- **WHEN** `dg list sensors | grep -E "(jersey|guernsey|isle_of_man|garage)_"`
  runs
- **THEN** 4 sensors SHALL be listed (3 jurisdiction + 1 S3)

#### Scenario: Jurisdiction pipeline base class

- **WHEN** `diff -u dlt/british_isles/ireland/education/ireland_jurisdiction_pipeline.py dlt/british_isles/england/education/england_jurisdiction_pipeline.py`
  runs
- **THEN** the diff SHALL be < 30 LOC (most boilerplate consolidated in base class)