# `celtic-data-engineering-pipeline` capability spec

> The marimo-native counterpart to the Evidence-style static dashboard
> demonstrated by the prior-art `spaces/data-engineering/` repo. Codifies
> the Dagster+DLT+dbt+MotherDuck stack as a first-class capability of the
> `oideachais/` quadrant, and adds the marimo statistical-analysis surface
> under `meaisinfhoghlaim/marimo/`.

## ADDED Requirements

### Requirement: dbt-duckdb project for celtic data
The system SHALL provide a dbt project at `oideachais/dbt_project/` that
transforms raw curriculum + OCR data into analytics-ready models, with
dev (local DuckDB) and prod (MotherDuck) targets.

#### Scenario: Dev target builds 3 models
- **GIVEN** `DUCKDB_DATABASE` is unset (defaults to local path)
- **WHEN** `dbt build --project-dir oideachais/dbt_project --target dev` is run
- **THEN** all 3 models (`weekly_downloads`, `language_distribution`,
  `ocr_confidence_by_model`) SHALL materialize as `table`
- **AND** the output database SHALL be at
  `dashboard/sources/oideachais/oideachais.duckdb`

#### Scenario: Prod target materializes incrementally
- **GIVEN** `MOTHERDUCK_TOKEN` is set
- **AND** `DUCKDB_DATABASE=md:oideachais?motherduck_token=$MOTHERDUCK_TOKEN`
- **WHEN** `dbt build --project-dir oideachais/dbt_project --target prod` is run
- **THEN** the 3 models SHALL materialize as `incremental` (per the
  `{{ 'incremental' if target.name == 'prod' else 'table' }}` config)
- **AND** `weekly_downloads` SHALL use `+unique_key: (download_date, project)`

### Requirement: Custom Dagster dbt translator
The system SHALL provide `oideachais/dagster_defs/dbt_translator.py` with
`CelticDagsterDbtTranslator` that maps dbt resource names to `AssetKey`s
with `group_name="prepared"`.

#### Scenario: dbt assets inherit the prepared group
- **GIVEN** a dbt model `weekly_downloads` is registered in `dbt_project.yml`
- **WHEN** Dagster loads the assets via `dbt_assets(manifest=...)`
- **THEN** the resulting Dagster asset SHALL have `group_name="prepared"`
- **AND** the asset key SHALL be `AssetKey(["weekly_downloads"])`

### Requirement: Marimo statistical-analysis surface under meaisinfhoghlaim
The system SHALL provide at least 2 marimo notebooks under
`meaisinfhoghlaim/marimo/` that read from `oideachais` via MotherDuck and
expose reactive descriptive + time-series analysis.

#### Scenario: Descriptive notebook renders
- **GIVEN** `meaisinfhoghlaim/marimo/01_leabharlann_descriptive.py` exists
- **WHEN** `marimo edit meaisinfhoghlaim/marimo/01_leabharlann_descriptive.py` is run
- **THEN** the notebook SHALL render with 4 altair charts and 1 reactive `mo.ui.slider`
- **AND** the data source SHALL be `md:oideachais` (MotherDuck) per the
  `.infisical.env` template

#### Scenario: Time-series notebook renders
- **GIVEN** `meaisinfhoghlaim/marimo/02_dpre_lag_analysis.py` exists
- **WHEN** `marimo edit` is run
- **THEN** the notebook SHALL render with a 1 correlation heatmap + 1 line chart
- **AND** the `mo.sql` cell SHALL reference the `weekly_downloads` dbt model

## MODIFIED Requirements

### Requirement: meaisinfhoghlaim-platform adds marimo/ sub-package
The system SHALL include `meaisinfhoghlaim/marimo/` as a first-class
sub-package of the meaisinfhoghlaim quadrant, exposed as a `[marimo]`
optional extra in `meaisinfhoghlaim/pyproject.toml`.

#### Scenario: marimo extra installs
- **GIVEN** the user runs `uv pip install -e "meaisinfhoghlaim[marimo]"`
- **THEN** `marimo>=0.13`, `altair>=5`, and `ibis-framework[duckdb,motherduck]`
  SHALL be installed
- **AND** the `meaisinfhoghlaim.marimo` package SHALL be importable
