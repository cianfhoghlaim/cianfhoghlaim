## ADDED Requirements

### Requirement: BIEP Notebooks Wire to Local Lakehouse (ibis-first)

The system SHALL provide marimo notebooks for each of the 6 LC subjects
(Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science)
that default to the local `bunchloch-infra` lakehouse — not to
PlanetScale or Lance Cloud — and that prefer the ibis DataFrame API
over raw `duckdb` SQL, per the canonical KCG pattern documented in
`.agents/skills/ibis/SKILL.md` (entrypoint `ibis.duckdb.connect(uri)`).

#### Scenario: Math notebook reads from local Lakekeeper via ibis

- **GIVEN** the lakehouse stack (Garage + Lakekeeper + Lance) is up
  per Change 2
- **WHEN** the operator runs
  `marimo run cianfhoghlaim/notebooks/biep/mathematics.py`
- **THEN** the notebook's first data cell SHALL execute
      `conn = ibis.duckdb.connect("ducklake:postgres:host=lakehouse-postgres port=5432 user=lakekeeper password=… dbname=ducklake_oideachais")`
- **AND** it SHALL resolve
      `lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`
- **AND** every data query SHALL be expressed as an ibis expression
      (`conn.table(...).filter(...).mutate(...).execute()`) rather
      than raw SQL strings
- **AND** the operation SHALL complete within 10 seconds against the
      empty Lakekeeper (returns 0-row DataFrames, not errors)
- **AND** the notebook SHALL be reproducible when the same operator
      swaps the URI to `md:oideachais` for the cloud-remote path
      (only one env var difference; no code change)

#### Scenario: ibis is the canonical entrypoint, not raw duckdb

- **WHEN** the 7 BIEP + lakehouse notebooks are grepped
- **THEN** every `import duckdb` is replaced by `import ibis`
- **AND** every `duckdb.connect(uri)` call is replaced by
  `ibis.duckdb.connect(uri)`
- **AND** zero raw `duckdb.connect(` calls remain in the notebooks
- **AND** the `ibis` skill is referenced in the per-notebook
      `## KCG patterns used` docstring

#### Scenario: All 6 BIEP subject notebooks pass the per-subject smoke

- **GIVEN** the lakehouse stack from Change 2 is healthy
- **WHEN** `opencode/scripts/run-biep-notebooks.sh` is run for all 6
  subjects
- **THEN** each notebook's first data cell completes within 2 seconds
  (no Lakekeeper timeouts)
- **AND** each notebook's first Lance cell lists the expected
  `oideachais.lc.<subject>.<level>_<lang>` tables
- **AND** zero notebooks leave "Pending" cells after 5 seconds