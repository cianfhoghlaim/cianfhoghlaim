# Data Pipeline — Spec Delta (lateralise-british-isles-domains)

## MODIFIED Requirements

### Requirement: Python 3.13 + Latest Stable Dependencies

The system SHALL be built and run on **Python 3.13** and SHALL track the
latest stable releases of `dagster`, `dagster-dlt`, `dlt`, `duckdb`, `lancedb`,
`cognee`, `marimo`, `firecrawl-py`, `playwright`, `pydantic`, `boto3`, `httpx`.

The bump SHALL be a *pure upgrade PR*: no behaviour change, no new sources,
no new tests, no Dagster asset renames. After the bump lands, the existing
`oideachais/test_crawl*.py` smoke scripts SHALL still pass under
`USE_LOCAL_SCRAPES=true` and the existing `dagster dev -m oideachais.dagster_defs.definitions`
SHALL still start.

#### Scenario: Local Dagster dev still starts
- **GIVEN** the upgraded toolchain
- **WHEN** the operator runs `uv run dagster dev -m oideachais.dagster_defs.definitions`
- **THEN** the UI loads at `http://localhost:3000` with the same asset graph

#### Scenario: Existing smoke test still green
- **GIVEN** the upgraded toolchain and `USE_LOCAL_SCRAPES=true`
- **WHEN** the operator runs `uv run python oideachais/test_crawl.py`
- **THEN** the script reads from `/stedding/ingest_queue/` and prints a `load_info` line

### Requirement: Pytest Coverage for DLT × Dagster Asset Graph

The system SHALL have automated pytest coverage of the existing DLT/Dagster
asset graph. Tests SHALL be runnable under `USE_LOCAL_SCRAPES=true` against a
temporary DuckLake fixture (no live network, no production schema mutation).

#### Scenario: All 16 tests pass in CI
- **GIVEN** `bun run test` (or `mise run test`) which runs `uv run pytest oideachais/tests/ tuatha/tests/ croilar/tests/ tests/sources/`
- **WHEN** the test runner executes
- **THEN** all 16 tests in `openspec/changes/lateralise-british-isles-domains/tasks.md` Phase 1b are green

#### Scenario: Cross‑namespace guard
- **GIVEN** a DLT source under `oideachais/dlt_sources/`
- **WHEN** the cross‑namespace test runs
- **THEN** the test fails if any source imports `oideachais.data_platform.*` (the "Zero Absolute Namespaces" rule)

### Requirement: Canonical `sources.yaml` + `SourceFactory`

The system SHALL maintain `oideachais/sources.yaml` as the **single source of
truth** for every DLT source across the four domains (`education`, `medicine`,
`law`, `statistics`) and the eight nations
(`ie, ni, en, sct, wls, iom, jey, ggy`).

The system SHALL provide `oideachais/dlt_utils/source_factory.py` exposing a
7‑method contract: `from_yaml`, `source`, `dlt_asset`, `dagster_asset`,
`lance_table`, `cognee_dataset`, `marimo_path`, `tests_path`.

#### Scenario: A new source entry drives the whole stack
- **GIVEN** a new entry in `sources.yaml` for `ni.education.ccea`
- **WHEN** the operator runs `python -m oideachais.sources.sources_validation`
- **THEN** the report shows: DLT source present, Dagster asset present, LanceDB table wired, Cognee dataset wired, marimo notebook present, pytest present

#### Scenario: Bad YAML entry rejected at load time
- **GIVEN** an entry with an unknown `kind` or unknown `nation_code`
- **WHEN** `SourceFactory.from_yaml(...)` is called
- **THEN** the factory raises `pydantic.ValidationError` with the offending field

### Requirement: Domain‑First DLT Source Layout

The system SHALL organise DLT sources by **domain** first, then by **nation**,
under `oideachais/dlt_sources/domains/{domain}/{nation}/*.py`. The legacy
addresses `oideachais/dlt_sources/{ireland,uk/*,crown_dependencies}/*` SHALL
remain as 1‑line re‑export shims for one release cycle.

#### Scenario: New and legacy addresses both work
- **GIVEN** `oideachais/dlt_sources/domains/education/ni/ccea_curriculum.py::ni_curriculum_source`
- **WHEN** an external consumer imports either `from oideachais.dlt_sources.ireland.ccea_curriculum import …` (legacy, removed; that was never an address) **or** `from oideachais.dlt_sources.uk.northern_ireland.ccea_curriculum import …` (legacy)
- **THEN** both resolve to the same `ni_curriculum_source` callable

## ADDED Requirements

### Requirement: Law Domain — Statutory Only (MVP)

The system SHALL provide a `law/` domain in `sources.yaml` containing **only
statutory** law sources: `irish_statute_book` (IE), `legislation` (NI/EN/SCT/WLS),
`doj` (IE), `lawreform` (IE). Case law (court judgments, tribunals, BAILII
mirrors) SHALL NOT be ingested by this change.

#### Scenario: Law domain in sources.yaml
- **GIVEN** the `sources.yaml` file
- **WHEN** the operator runs `python -m oideachais.sources.sources_validation --filter domain=law`
- **THEN** only statutory entries appear

#### Scenario: Case law entry rejected
- **GIVEN** a hypothetical `ie.law.courts` entry
- **WHEN** the SourceFactory loads the YAML
- **THEN** the factory raises a `pydantic.ValidationError` because `ie.law.courts` is not in the MVP law allowlist
