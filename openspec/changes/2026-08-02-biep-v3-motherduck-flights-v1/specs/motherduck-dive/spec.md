## MODIFIED Requirements

### Requirement: 4 new MotherDuck Flights + 2 existing flights fixed

The system SHALL provide 4 new MotherDuck Flights
(`ireland_full_coverage_flight`, `england_full_coverage_flight`,
`sct_wls_ni_flight`, `crown_dependencies_flight`) covering the 8 BIEP v3
jurisdictions, AND the 2 existing flights
(`eng_daily_sync_flight`, `jc_pdf_sync_flight`) SHALL have the
`md_oideachais` typo fixed to `md:cianfhoghlaim`.

#### Scenario: 6 MotherDuck Flights exist with the canonical namespace

- **WHEN** `duckdb -c "SELECT name FROM motherduck_dwh.flights WHERE name LIKE '%cianfhoghlaim%' OR name LIKE '%england%' OR name LIKE '%ireland%' OR name LIKE '%sct%' OR name LIKE '%crown%' OR name LIKE '%jc%'"`
  runs
- **THEN** 6 flights SHALL be listed
  (2 existing fixed + 4 new)
- **AND** every flight SHALL reference `md:cianfhoghlaim` (not `md_oideachais`)