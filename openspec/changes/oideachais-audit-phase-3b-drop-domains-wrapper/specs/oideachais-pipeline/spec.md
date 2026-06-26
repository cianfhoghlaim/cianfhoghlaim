# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: Country-First DLT Source Layout
The canonical DLT source package SHALL use the country-first layout `sruth/oideachais/dlt_sources/{nation}/{domain}/{entity}.py` where `{nation}` is one of `{ie, ni, en, sct, wls, iom, jey, ggy, pan_celtic, cross}` and `{domain}` is one of `{education, culture, law, medicine, statistics, site_analysis}`.

A `domains/` wrapper directory SHALL NOT exist as an intermediate level in the canonical layout. (The legacy `domains/{domain}/{nation}/` tree, when it existed, has been retired.)

#### Scenario: canonical files live at country-first paths
- **WHEN** a developer lists the contents of `sruth/oideachais/dlt_sources/`
- **THEN** a `ie/` directory SHALL exist with `education/`, `culture/`, `law/`, `medicine/` subdirectories
- **AND** an `en/` directory SHALL exist with `education/`, `law/`, `medicine/` subdirectories
- **AND** a `sct/` directory SHALL exist with `education/`, `statistics/`, `medicine/` subdirectories
- **AND** no `domains/` directory SHALL be present

#### Scenario: no stale imports of dlt_sources.domains.*
- **WHEN** a developer runs `grep -rn "dlt_sources\.domains\." --include="*.py" sruth/oideachais/`
- **THEN** zero matches SHALL be returned (excluding frozen `openspec/changes/archive/*` records)

#### Scenario: shims still re-export from legacy ireland/uk/etc.
- **WHEN** Python code executes `from dlt_sources.ie.education import ncca`
- **THEN** the import SHALL succeed (re-exporting from the legacy `dlt_sources.ireland.ncca` path)
- **AND** calling `ncca()` SHALL produce the same source as before the migration
