# Spec Delta — `leabharlann-ingestion`

The canonical spec for `leabharlann-ingestion` lives at `openspec/specs/leabharlann-ingestion/spec.md` and was created as part of this change. No `ADDED Requirements` delta is required — the canonical spec contains the full requirements.

## MODIFIED Requirements

### Requirement: Source default paths MUST point at `leabharlann/`
The dlt source modules `sruth/oideachais/dlt_sources/author_archive/{university_of_galway,gemini_deep_research}.py` MUST define `DEFAULT_UOG_PATH` and `DEFAULT_GEMINI_PATH` pointing at `leabharlann/ollscoil_na_gaillimhe/` and `leabharlann/gemini_deep_research/` respectively. The source factories SHALL continue to accept any `base_path` argument so callers can pass the old `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/` path explicitly for back-compat.

#### Scenario: Default path under leabharlann
- **GIVEN** the `university_of_galway_source()` factory is called without arguments
- **WHEN** the path is inspected
- **THEN** the path SHALL end with `leabharlann/ollscoil_na_gaillimhe`

#### Scenario: Backwards-compatible explicit path
- **GIVEN** an existing caller passes an explicit `base_path=...` to `university_of_galway_source(base_path=...)`
- **WHEN** the source runs
- **THEN** the `account` column SHALL be the value passed in `base_path`

## REMOVED Requirements

*(None.)*
