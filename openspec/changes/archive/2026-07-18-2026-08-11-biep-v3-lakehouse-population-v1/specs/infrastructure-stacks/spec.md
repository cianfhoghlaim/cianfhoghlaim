## ADDED Requirements

### Requirement: BIEP v3 lakehouse population (P1)

The system SHALL have a populated lakehouse with:

1. The 11-service Lakehouse stack deployed + healthy on `bunchloch`
   (Mac M4).
2. 3,780 rows in `cianfhoghlaim.education._registry.subjects`.
3. All 4 BIEP v3 jurisdiction pipelines executed successfully (writes
   544 + 276 + 1,520 + 720 = 3,060 cohort rows to DuckLake).
4. 8 CocoIndex v1 BIIP parity flows wired (consume DuckLake → LanceDB).
5. 4 BIEP v3 MotherDuck Flights emitting Dagster RunRequests.
6. 0 `md:oideachais` references in `notebooks/` (post-sweep).

#### Scenario: Lakehouse smoke-test passes

- **WHEN** `mise run biep:v3:lakehouse:smoke-test` runs
- **THEN** Nimtable :3018 MUST return HTTP 200 at `/`
- **AND** Olake :3901 MUST return HTTP 200 at `/health`
- **AND** LanceDB Viewer :8081 MUST return HTTP 200 at `/v1/databases`

#### Scenario: Lakekeeper deep health check

- **WHEN** `curl http://localhost:8181/health/deep` runs
- **THEN** the response MUST return HTTP 200
- **AND** the response MUST include `{"postgres": "healthy", "s3": "healthy"}`

#### Scenario: Registry seeds 3,780 rows

- **WHEN** `mise run biep:v3:registry:seed` runs
- **THEN** the registry table MUST contain 3,780 rows
- **AND** Lakekeeper MUST list 8 namespaces under `cianfhoghlaim.education`

#### Scenario: Ireland pipeline writes 544 cohorts

- **WHEN** `dg launch --job ireland_jurisdiction_pipeline` runs
- **THEN** the DuckLake table MUST contain 544 cohort rows

#### Scenario: England pipeline writes 276 cohorts

- **WHEN** `dg launch --job england_jurisdiction_pipeline` runs
- **THEN** the DuckLake table MUST contain 276 cohort rows

#### Scenario: SCT+WLS+NI pipeline writes 1,520 cohorts

- **WHEN** the SCT+WLS+NI pipeline is run with
  `jurisdiction=scotland,wales,northern_ireland`
- **THEN** the combined DuckLake tables MUST contain 600 + 640 + 280 = 1,520 rows

#### Scenario: Crown Dependencies pipeline writes 720 cohorts

- **WHEN** the Crown Dependencies pipeline is run with
  `jurisdiction=jersey,guernsey,isle_of_man`
- **THEN** the combined DuckLake tables MUST contain 240 + 240 + 240 = 720 rows

#### Scenario: All 4 BIEP v3 MotherDuck Flights listed

- **WHEN** `dg list jobs | grep -E "(ireland|england|sct_wls_ni|crown_dependencies)_full_coverage"` runs
- **THEN** exactly 4 BIEP v3 flight job names are listed

#### Scenario: Each flight emits a Dagster RunRequest

- **WHEN** `dg launch --job ireland_full_coverage_flight` runs
- **THEN** the Dagster event log MUST include at least 1 `RunRequest` event
  with `tags.jurisdiction = "ireland"`

(Same for england, sct_wls_ni, crown_dependencies.)

#### Scenario: Zero md:oideachais references in notebooks

- **WHEN** `grep -rn "md:oideachais" notebooks/ | wc -l` runs
- **THEN** the output MUST be `0`
- **AND** all notebooks MUST connect via `notebooks/_shared/db.py:connect_md()`

#### Scenario: LAKEHOUSE_URI_DEFAULT is canonical

- **WHEN** `notebooks/_shared/db.py` is inspected
- **THEN** `LAKEHOUSE_URI_DEFAULT` MUST equal `"md:cianfhoghlaim"`

#### Scenario: 8-jurisdiction overview dashboard runs

- **WHEN** `notebooks/23_8_jurisdiction_overview.py` is launched
- **THEN** the dashboard MUST query `cianfhoghlaim.education._registry.subjects`
- **AND** show all 8 jurisdictions with their subject counts