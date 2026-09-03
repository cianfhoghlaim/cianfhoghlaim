# Oideachais Pipeline — Spec Delta (lateralise-british-isles-domains)

## ADDED Requirements

### Requirement: Asset Key Convention (renamed)

The system SHALL identify every asset by a domain‑first key tuple
`["{nation_code}", "{domain}", "{entity_slug}"]` where:

- `nation_code` is one of `ie | ni | en | sct | wls | iom | jey | ggy`.
- `domain` is one of `education | medicine | law | statistics | site_analysis`.
- `entity_slug` is the YAML `id` suffix (e.g. `ccea`, `irish_statute_book`).

The system SHALL maintain a backwards‑compatibility alias table in
`sruth/oideachais/dagster_defs/definitions.py` mapping legacy asset keys to the
new ones for one (1) release cycle, then the alias table SHALL be removed in
a follow‑on `drop-asset-key-aliases` change.

#### Scenario: Domain‑first key for an Irish education asset
- **GIVEN** the existing `sruth/oideachais/dagster_defs/assets/ireland/curriculum_dlt_assets.py` `create_cycle_asset("senior_cycle")` whose legacy key is `["ireland", "curriculum", "senior_cycle"]`
- **WHEN** the asset is registered with the SourceFactory
- **THEN** the new key is `["ie", "education", "curriculum", "senior_cycle"]`
- **AND** the legacy key is resolvable via the backwards‑compat alias

#### Scenario: Domain‑first key for a Northern Ireland CCEA asset
- **GIVEN** the existing `sruth/oideachais/dlt_sources/uk/northern_ireland/ccea_curriculum.py::ni_curriculum_source`
- **WHEN** the SourceFactory emits the corresponding Dagster asset
- **THEN** the new key is `["ni", "education", "ccea", "pages"]`
- **AND** the legacy key `["uk", "education", "northern_ireland", "ccea_pages"]` is resolvable

### Requirement: Single `oideachais` DB with per‑domain schemas

The system SHALL register a single `md:oideachais` (MotherDuck) database and a
single `ducklake:oideachais` (Garage S3) catalog, with schemas of the form
`oideachais.{domain}.{nation}`. DLT `dataset_name` MAY remain per‑source for
fine‑grained state, but the underlying DuckLake schema SHALL be the
dotted‑triple.

#### Scenario: One attach, one query
- **GIVEN** the API reader at `sruth/oideachais/api/ducklake_reader.py`
- **WHEN** the SPA requests a Leaving Cert subject
- **THEN** the reader does a single `ATTACH 'oideachais'` (or `ducklake:oideachais`)
- **AND** reads `oideachais.education.ie.leaving_cert WHERE subject = ?`
- **AND** no per‑subject glob() / per‑subject S3 prefix is used

#### Scenario: New domain schema is auto‑created
- **GIVEN** a new DLT run for `sruth/oideachais/dlt_sources/domains/medicine/ie/hse.py`
- **WHEN** the pipeline runs
- **THEN** DuckLake creates the schema `oideachais.medicine.ie` on first write
- **AND** the table is discoverable by `marimo` against `md:oideachais`

## REMOVED Requirements

*None — this change only renames keys and centralises the storage layout.*
