## ADDED Requirements

### Requirement: Commonwealth of Nations path contract

The system MUST place every Commonwealth pipeline at the canonical
path:

```text
dlt/commonwealth/<iso3>/<domain>/<source>.py
```

where `iso3` is the lowercase ISO 3166-1 alpha-3 code (e.g. `aus`,
`can`, `nzl`, `ind`, `zaf`), `domain` is one of
`education | law | medicine | statistics | government`, and `source`
is a snake_case slug. Every source MUST declare its `source_id` as
`commonwealth.<iso3>.<domain>.<source_slug>` and land in the canonical
DuckLake namespace `oideachais.<domain>.commonwealth.<iso3>`.

#### Scenario: A new Australian curriculum source obeys the contract

- **WHEN** a developer adds the ACARA DLT source
- **THEN** the file MUST be created at
  `dlt/commonwealth/aus/education/acara.py`
- **AND** its `source_id` MUST be
  `commonwealth.aus.education.acara`
- **AND** the DuckLake table MUST be
  `oideachais.education.commonwealth.aus`
- **AND** the file MUST NOT be created at any legacy path
  (`dlt/aus/acara.py`, `dlt/commonwealth/acara/`, etc.)

### Requirement: 5 pilot Commonwealth nations ship 25 DLT sources

The system MUST ship 5 DLT sources (one per canonical domain) for each
of the 5 pilot Commonwealth nations, totalling 25 DLT sources.

#### Scenario: Australia ships 5 sources

- **WHEN** the Commonwealth pipeline change is materialised
- **THEN** the system MUST provide 5 DLT sources at
  - `dlt/commonwealth/aus/education/acara.py`
  - `dlt/commonwealth/aus/law/federal_register_legislation.py`
  - `dlt/commonwealth/aus/medicine/tga.py`
  - `dlt/commonwealth/aus/statistics/abs.py`
  - `dlt/commonwealth/aus/government/gov_au.py`

### Requirement: Per-nation Commonwealth curriculum extraction

The system MUST provide a BAML extraction function
`ExtractCommonwealthCurriculumSpec(country_code, language, text) -> CommonwealthCurriculumSpec`
at `cianfhoghlaim/baml/commonwealth/<iso3>/education.baml` that
extracts the canonical Commonwealth per-nation curriculum
specification.

#### Scenario: A Canadian curriculum document is extracted

- **WHEN** the Canadian education DLT source yields a new
  Council of Ministers of Education (CMEC) document
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractCommonwealthCurriculumSpec(country_code="can",
   language="en" | "fr", text=<text>)`
- **AND** the resulting `CommonwealthCurriculumSpec` MUST carry
  `country_code="can"`, the `language` partition, the
  curriculum framework name, and the learning outcomes

### Requirement: Commonwealth institutional layer

The system MUST provide DLT sources at
`dlt/commonwealth/official/{commonwealth_secretariat,commonwealth_foundation}.py`
that crawl the Commonwealth Secretariat + Commonwealth Foundation
websites and emit one row per publication × language.

#### Scenario: A new Commonwealth Secretariat press release is ingested

- **WHEN** the Commonwealth Secretariat DLT source ingests a new
  press release
- **THEN** the system MUST emit one row per available language
  edition
- **AND** each row MUST include `press_release_id`, `language`,
  `institution="commonwealth_secretariat"`, `title`, `publication_date`,
  `source_url`, `content_hash`

### Requirement: Commonwealth CocoIndex v1 + Dagster + MotherDuck

The system MUST provide:

- 1 CocoIndex v1 App (`commonwealth_education_embedding`) that embeds
  the 5 pilot countries' education rows into a shared LanceDB table
- 1 MotherDuck Dive (`commonwealth_curriculum_matrix`) that surfaces
  the cross-nation coverage matrix
- 1 daily MotherDuck Flight (`commonwealth_daily_sync_flight`) that
  BAML-backfills the 25 per-nation sources

#### Scenario: A new Australian curriculum row lands

- **WHEN** the Australian education DLT source emits a new row
- **THEN** the daily Flight MUST pick it up within 24h
- **AND** the `commonwealth_curriculum_matrix` Dive MUST reflect the
  new row within 60 seconds of the Flight completing

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-union-official-language-pipeline`](../european-union-official-language-pipeline/spec.md) —
  the EU institutional counterpart
- [`european-nations-ukraine-pipeline`](../european-nations-ukraine-pipeline/spec.md) —
  the EU nations counterpart
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the seed instance
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
