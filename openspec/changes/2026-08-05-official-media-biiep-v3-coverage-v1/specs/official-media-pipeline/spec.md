## MODIFIED Requirements

### Requirement: official-media pipeline covers all 8 British Isles jurisdictions

The system SHALL require the `official-media` pipeline to cover all 5
UK + Crown Dependencies jurisdictions (in addition to the existing
England / Wales / Scotland coverage): Scotland, Wales, IoM, JEY, GGY.

#### Scenario: 5 new jurisdiction sub-assets exist

- **WHEN** `ls dlt/official_media/` runs
- **THEN** 5 new sub-asset files SHALL exist (scotland, wales, iom, jersey, guernsey)
- **AND** `dlt/official_media/source_resolver.py:resolve("tynwald", ...)` SHALL
  return a valid Isle of Man media source

#### Scenario: 12-week HMGCC rolling window runs

- **WHEN** the HMGCC rolling window Dagster asset materialises
- **THEN** the asset SHALL ingest the last 12 weeks of HMGCC publications

#### Scenario: Companies House Crown filter works

- **WHEN** the Crown filter asset materialises
- **THEN** the 6 canonical UK Crown bodies SHALL be tagged with
  `crown_body: true`

#### Scenario: Deplatforming-thesis paper exists

- **WHEN** `ls docs/theses/deplatforming_thesis.md` runs
- **THEN** the file SHALL exist with 1-page executive summary + 10-section outline

#### Scenario: meaisinfhoghlaim web analyzer is live

- **WHEN** `curl http://localhost:3000/analyzer` runs
- **THEN** the page SHALL return 200 OK with the analyzer UI

#### Scenario: PWA loads

- **WHEN** `curl http://localhost:3000/official-media-pwa/` runs
- **THEN** the page SHALL return 200 OK with a valid service worker