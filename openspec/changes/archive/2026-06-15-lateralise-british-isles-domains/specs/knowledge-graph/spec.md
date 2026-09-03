# Knowledge Graph — Spec Delta (lateralise-british-isles-domains)

## ADDED Requirements

### Requirement: Cognee Dataset Naming (Domain‑Keyed)

The system SHALL create **one Cognee dataset per domain** (e.g.
`oideachais_education_ie`, `oideachais_education_uk`, `oideachais_medicine`,
`oideachais_law`, `oideachais_site_analysis`). A single shared
`oideachais_cross_nation` dataset SHALL hold cross‑domain edges
(`same_as`, `cites`, `prerequisite_to`, `translates_to`).

The existing `cross_stage_cognify` Dagster asset SHALL be renamed to
`cross_domain_cognify` and SHALL operate on the new
`oideachais_cross_nation` dataset.

#### Scenario: Cognify on a new domain
- **GIVEN** `sruth/oideachais/dlt_sources/domains/medicine/ie/hse.py` has been materialised into `oideachais.medicine.ie.hse_pages`
- **WHEN** the cognify asset for `oideachais_medicine` runs
- **THEN** entities and edges are stored in the `oideachais_medicine` Cognee dataset

#### Scenario: Cross‑domain cognify
- **GIVEN** both `oideachais.education.ie.ncca_pages` and `oideachais.medicine.ie.hse_pages` are materialised
- **WHEN** the `cross_domain_cognify` asset runs
- **THEN** cross‑domain edges appear in `oideachais_cross_nation`
- **AND** the existing `cross_stage_cognify` asset is removed in this change
