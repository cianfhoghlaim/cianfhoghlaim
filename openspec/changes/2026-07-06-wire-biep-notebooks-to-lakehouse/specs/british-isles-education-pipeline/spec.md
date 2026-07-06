## MODIFIED Requirements

### Requirement: BIEP Subject Notebooks Default to Local Lakehouse

The system SHALL require that the 6 BIEP subject marimo notebooks
(Mathematics, Chemistry, Geography, Gaeilge, English, Computer
Science) default to the local `bunchloch-infra` lakehouse via the
`ibis.duckdb.connect()` + `ibis.lancedb.connect()` entrypoints, with
the per-subject `ducklake_<subject>` database name. The system MUST
reject any raw `duckdb.connect(...)` call in these notebooks per the
ibis-first contract from Change 3's `oideachais-marimo-dashboards`
spec delta.

#### Scenario: All 6 subjects use the same canonical entrypoints

- **WHEN** `ls cianfhoghlaim/notebooks/biep/<subject>.py` is run
  for each of the 6 subjects
- **THEN** every notebook's first data cell SHALL declare
      `conn = ibis.duckdb.connect(...)` with one of:
  - local: `ducklake:postgres:host=lakehouse-postgres port=5432 user=lakekeeper password=… dbname=ducklake_<subject>`
  - cloud: `md:oideachais`
- **AND** every notebook's first Lance cell SHALL declare
      `lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`
- **AND** the notebook's session-state defaults SHALL be
  `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` +
  `DUCKLAKE_DB=ducklake_<subject>` +
  `IBIS_BACKEND=duckdb`