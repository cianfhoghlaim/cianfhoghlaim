## ADDED Requirements

### Requirement: Americas path contract (with US sub-state)

The system MUST place every Americas pipeline at the canonical path:

```text
dlt/americas/<jurisdiction>/<domain>/<source>.py
```

where `jurisdiction` is either:

- a country ISO 3166-1 alpha-3 (e.g. `bra`, `mex`, `ven`, `can`),
- a US sub-state `<us_state>` slug for sub-national US jurisdictions
  (e.g. `us_ca`, `us_tx`, `us_ny`, `us_ma`),
- or `official` for the institutional layer (OAS / PAHO / IDB /
  CELAC).

`domain` is one of `education | law | medicine | statistics |
government`. Every source MUST declare its `source_id` as
`americas.<jurisdiction>.<domain>.<source_slug>` and land in the
canonical DuckLake namespace `cianfhoghlaim.<domain>.americas.<jurisdiction>`.

#### Scenario: A new California education source obeys the contract

- **WHEN** a developer adds the California Department of Education
  DLT source
- **THEN** the file MUST be created at
  `dlt/americas/us/us_ca/education/cde.py`
- **AND** its `source_id` MUST be `americas.us.us_ca.education.cde`
- **AND** the DuckLake table MUST be
  `cianfhoghlaim.education.americas.us_us_ca`
- **AND** the file MUST NOT be created at any legacy path
  (`dlt/california/cde.py`, `dlt/us/cde.py`, etc.)

### Requirement: California ships 5 sub-state DLT sources

The system MUST ship 5 DLT sources for the US sub-state of California
(one per canonical domain), totalling 5 per-sub-state sources.

#### Scenario: California ships 5 sources

- **WHEN** the California pipeline change is materialised
- **THEN** the system MUST provide 5 DLT sources at
  - `dlt/americas/us/us_ca/education/cde.py`
  - `dlt/americas/us/us_ca/law/ca_leginfo.py`
  - `dlt/americas/us/us_ca/medicine/cdph.py`
  - `dlt/americas/us/us_ca/statistics/data_ca_gov.py`
  - `dlt/americas/us/us_ca/government/ca_gov.py`

### Requirement: Brazil / Mexico / Venezuela national pipelines

The system MUST ship 5 DLT sources per national jurisdiction for each
of the 3 named American countries (Brazil, Mexico, Venezuela),
totalling 15 national sources.

#### Scenario: Brazil ships 5 sources

- **WHEN** the Brazil pipeline change is materialised
- **THEN** the system MUST provide 5 DLT sources at
  - `dlt/americas/bra/education/mec.py`
  - `dlt/americas/bra/law/planalto.py`
  - `dlt/americas/bra/medicine/anvisa.py`
  - `dlt/americas/bra/statistics/ibge.py`
  - `dlt/americas/bra/government/planalto_gov.py`

### Requirement: Per-jurisdiction curriculum extraction

The system MUST provide a BAML extraction function
`ExtractAmericasCurriculumSpec(jurisdiction, language, text) -> AmericasCurriculumSpec`
at `baml/americas/<jurisdiction>/education.baml` that
extracts the canonical Americas per-jurisdiction curriculum
specification.

#### Scenario: A California state standard is extracted

- **WHEN** the California education DLT source yields a new CDE
  state-standard document
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractAmericasCurriculumSpec(jurisdiction="us_us_ca",
   language="en", text=<text>)`
- **AND** the resulting `AmericasCurriculumSpec` MUST carry
  `jurisdiction="us_us_ca"`, the `language` partition, the
  subject area, the grade band, and the standard identifier

### Requirement: Americas institutional layer

The system MUST provide DLT sources at
`dlt/americas/official/{oas,paho,idb,celac}.py` that crawl the
Organization of American States + Pan American Health Organization +
Inter-American Development Bank + Community of Latin American and
Caribbean States and emit one row per publication × language.

#### Scenario: A new PAHO epidemiological bulletin is ingested

- **WHEN** the PAHO DLT source ingests a new epidemiological bulletin
- **THEN** the system MUST emit one row per available language
  edition
- **AND** each row MUST include `bulletin_id`, `language`,
  `institution="paho"`, `pathogen`, `reporting_period`, `source_url`,
  `content_hash`

### Requirement: Americas CocoIndex v1 + Dagster + MotherDuck

The system MUST provide:

- 1 CocoIndex v1 App (`americas_california_education_embedding`) that
  embeds every Americas education row into a shared LanceDB table
- 1 MotherDuck Dive (`americas_state_standards_crosswalk`) that
  surfaces the cross-state standards cross-reference
- 1 daily MotherDuck Flight (`americas_daily_sync_flight`) that
  BAML-backfills the Americas sources

#### Scenario: A new California curriculum row lands

- **WHEN** the California education DLT source emits a new row
- **THEN** the daily Flight MUST pick it up within 24h
- **AND** the `americas_state_standards_crosswalk` Dive MUST reflect
  the new row within 60 seconds of the Flight completing

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-union-official-language-pipeline`](../european-union-official-language-pipeline/spec.md) —
  the EU institutional counterpart
- [`european-nations-ukraine-pipeline`](../european-nations-ukraine-pipeline/spec.md) —
  the EU nations counterpart
- [`commonwealth-pipeline`](../commonwealth-pipeline/spec.md) —
  the Commonwealth counterpart
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the seed instance
- [`cianfhoghlaim-pipeline`](../cianfhoghlaim-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
