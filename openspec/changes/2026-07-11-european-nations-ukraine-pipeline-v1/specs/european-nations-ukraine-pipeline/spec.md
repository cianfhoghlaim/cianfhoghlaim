## ADDED Requirements

### Requirement: Canonical per-nation DLT path contract

The system MUST place every new national pipeline at the canonical
path:

```text
dlt/european_nations/<iso3>/<domain>/<source>.py
```

where `iso3` is the lowercase ISO 3166-1 alpha-3 code, `domain` is one
of `education | law | medicine | statistics | government`, and
`source` is a snake_case slug. Every source MUST declare its
`source_id` as `european_nations.<iso3>.<domain>.<source_slug>` and
land in the canonical DuckLake namespace
`oideachais.<domain>.european_nations.<iso3>`.

#### Scenario: A new French statute-book source obeys the contract

- **WHEN** a developer adds the Légifrance DLT source
- **THEN** the file MUST be created at
  `dlt/european_nations/fra/law/legifrance.py`
- **AND** its `source_id` MUST be `european_nations.fra.law.legifrance`
- **AND** the DuckLake table MUST be
  `oideachais.law.european_nations.fra`
- **AND** the file MUST NOT be created at any legacy path
  (`dlt/eu/fra/`, `dlt/france/law/legifrance.py`, etc.)

### Requirement: 6 pilot countries ship 30 DLT sources

The system MUST ship 5 DLT sources (one per canonical domain) for each
of the 6 pilot countries, totalling 30 DLT sources.

#### Scenario: Ukraine ships 5 sources

- **WHEN** the Ukrainian pipeline change is materialised
- **THEN** the system MUST provide 5 DLT sources at
  - `dlt/european_nations/ukr/education/ministry_education_science.py`
  - `dlt/european_nations/ukr/law/zakon_rada.py`
  - `dlt/european_nations/ukr/medicine/ministry_health.py`
  - `dlt/european_nations/ukr/statistics/ukrstat.py`
  - `dlt/european_nations/ukr/government/kmu_portal.py`

### Requirement: Per-nation curriculum extraction

The system MUST provide a BAML extraction function
`ExtractNationCurriculumSpec(country_code, language, text) -> NationCurriculumSpec`
at `baml/european_nations/<iso3>/education.baml` that
extracts the canonical per-nation curriculum specification from any
national education document.

#### Scenario: A Ukrainian curriculum document is extracted

- **WHEN** the Ukrainian education DLT source yields a new
  curriculum framework document
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractNationCurriculumSpec(country_code="ukr", language=<lang>,
   text=<text>)`
- **AND** the resulting `NationCurriculumSpec` MUST carry
  `country_code="ukr"`, the `language` partition, the curriculum
  framework name, the level, and the learning outcomes

### Requirement: Per-nation law extraction

The system MUST provide a BAML extraction function
`ExtractNationStatute(country_code, language, text) -> NationStatute`
at `baml/european_nations/<iso3>/law.baml` that extracts
the canonical per-nation statute record.

#### Scenario: A French statute is extracted

- **WHEN** the French law DLT source yields a new Légifrance statute
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractNationStatute(country_code="fra", language="fr",
   text=<text>)`
- **AND** the resulting `NationStatute` MUST carry `nor` (the
  Légifrance NOR identifier), `titre`, `date_publication`,
  `etat`, and `visa`

### Requirement: Per-nation medicine extraction

The system MUST provide a BAML extraction function
`ExtractNationHealthGuidance(country_code, language, text) -> NationHealthGuidance`
at `baml/european_nations/<iso3>/medicine.baml` that
extracts the canonical per-nation public-health guidance.

#### Scenario: A German RKI guidance is extracted

- **WHEN** the German medicine DLT source yields a new RKI
  epidemiological bulletin
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractNationHealthGuidance(country_code="deu", language="de",
   text=<text>)`
- **AND** the resulting `NationHealthGuidance` MUST carry
  `bulletin_id`, `pathogen`, `reporting_period`, and the
  surveillance summary

### Requirement: Cross-nation CocoIndex v1 Apps

The system MUST provide 3 CocoIndex v1 Apps (education, law, medicine)
that embed every per-nation source's rows into 3 shared LanceDB
tables using `BAAI/bge-m3`. Each App MUST import
`from ._lifespan import shared_lifespan` to satisfy the R1–R4
conformance contract.

#### Scenario: The education CocoIndex v1 App materialises

- **WHEN** the 6 pilot countries' education DLT sources emit rows
- **THEN** the `european_nations_education` CocoIndex v1 App MUST
  embed each row into the shared LanceDB table
  `oideachais.eu_nations.education_chunks`
- **AND** each chunk MUST carry `country_code`, `language`,
  `domain="education"`, and the source_url + content_hash

### Requirement: MotherDuck cross-nation Dive + daily Flight

The system MUST provide:

- 1 MotherDuck Dive: `eu_nation_curriculum_matrix` — cross-nation
  curriculum coverage matrix for the 6 pilot countries
- 1 daily MotherDuck Flight: `eu_nation_daily_sync_flight` — daily
  BAML backfill for the 30 per-nation sources

#### Scenario: A new Ukrainian curriculum row lands

- **WHEN** the Ukrainian education DLT source emits a new row
- **THEN** the daily Flight MUST pick it up within 24h
- **AND** the `eu_nation_curriculum_matrix` Dive MUST reflect the new
  row within 60 seconds of the Flight completing

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-union-official-language-pipeline`](../european-union-official-language-pipeline/spec.md) —
  the institutional counterpart
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the seed instance of the per-nation pattern
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- [`oideachais-baml-schemas`](../oideachais-baml-schemas/spec.md) —
  the BAML cluster taxonomy
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
`nor`, `che`, `isl`) are deferred to a follow-on change.

## Requirements

### Requirement: Canonical per-nation DLT path contract

The system MUST place every new national pipeline at the canonical
path:

```text
dlt/european_nations/<iso3>/<domain>/<source>.py
```

where `iso3` is the lowercase ISO 3166-1 alpha-3 code, `domain` is one
of `education | law | medicine | statistics | government`, and
`source` is a snake_case slug. Every source MUST declare its
`source_id` as `european_nations.<iso3>.<domain>.<source_slug>` and
land in the canonical DuckLake namespace
`oideachais.<domain>.european_nations.<iso3>`.

#### Scenario: A new French statute-book source obeys the contract

- **WHEN** a developer adds the Légifrance DLT source
- **THEN** the file MUST be created at
  `dlt/european_nations/fra/law/legifrance.py`
- **AND** its `source_id` MUST be `european_nations.fra.law.legifrance`
- **AND** the DuckLake table MUST be
  `oideachais.law.european_nations.fra`
- **AND** the file MUST NOT be created at any legacy path
  (`dlt/eu/fra/`, `dlt/france/law/legifrance.py`, etc.)

### Requirement: 6 pilot countries ship 30 DLT sources

The system MUST ship 5 DLT sources (one per canonical domain) for each
of the 6 pilot countries, totalling 30 DLT sources.

#### Scenario: Ukraine ships 5 sources

- **WHEN** the Ukrainian pipeline change is materialised
- **THEN** the system MUST provide 5 DLT sources at
  - `dlt/european_nations/ukr/education/ministry_education_science.py`
  - `dlt/european_nations/ukr/law/zakon_rada.py`
  - `dlt/european_nations/ukr/medicine/ministry_health.py`
  - `dlt/european_nations/ukr/statistics/ukrstat.py`
  - `dlt/european_nations/ukr/government/kmu_portal.py`

### Requirement: Per-nation curriculum extraction

The system MUST provide a BAML extraction function
`ExtractNationCurriculumSpec(country_code, language, text) -> NationCurriculumSpec`
at `baml/european_nations/<iso3>/education.baml` that
extracts the canonical per-nation curriculum specification from any
national education document.

#### Scenario: A Ukrainian curriculum document is extracted

- **WHEN** the Ukrainian education DLT source yields a new
  curriculum framework document
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractNationCurriculumSpec(country_code="ukr", language=<lang>,
   text=<text>)`
- **AND** the resulting `NationCurriculumSpec` MUST carry
  `country_code="ukr"`, the `language` partition, the curriculum
  framework name, the level, and the learning outcomes

### Requirement: Per-nation law extraction

The system MUST provide a BAML extraction function
`ExtractNationStatute(country_code, language, text) -> NationStatute`
at `baml/european_nations/<iso3>/law.baml` that extracts
the canonical per-nation statute record.

#### Scenario: A French statute is extracted

- **WHEN** the French law DLT source yields a new Légifrance statute
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractNationStatute(country_code="fra", language="fr",
   text=<text>)`
- **AND** the resulting `NationStatute` MUST carry `nor` (the
  Légifrance NOR identifier), `titre`, `date_publication`,
  `etat`, and `visa`

### Requirement: Per-nation medicine extraction

The system MUST provide a BAML extraction function
`ExtractNationHealthGuidance(country_code, language, text) -> NationHealthGuidance`
at `baml/european_nations/<iso3>/medicine.baml` that
extracts the canonical per-nation public-health guidance.

#### Scenario: A German RKI guidance is extracted

- **WHEN** the German medicine DLT source yields a new RKI
  epidemiological bulletin
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractNationHealthGuidance(country_code="deu", language="de",
   text=<text>)`
- **AND** the resulting `NationHealthGuidance` MUST carry
  `bulletin_id`, `pathogen`, `reporting_period`, and the
  surveillance summary

### Requirement: Cross-nation CocoIndex v1 Apps

The system MUST provide 3 CocoIndex v1 Apps (education, law, medicine)
that embed every per-nation source's rows into 3 shared LanceDB
tables using `BAAI/bge-m3`. Each App MUST import
`from ._lifespan import shared_lifespan` to satisfy the R1–R4
conformance contract.

#### Scenario: The education CocoIndex v1 App materialises

- **WHEN** the 6 pilot countries' education DLT sources emit rows
- **THEN** the `european_nations_education` CocoIndex v1 App MUST
  embed each row into the shared LanceDB table
  `oideachais.eu_nations.education_chunks`
- **AND** each chunk MUST carry `country_code`, `language`,
  `domain="education"`, and the source_url + content_hash

### Requirement: MotherDuck cross-nation Dive + daily Flight

The system MUST provide:

- 1 MotherDuck Dive: `eu_nation_curriculum_matrix` — cross-nation
  curriculum coverage matrix for the 6 pilot countries
- 1 daily MotherDuck Flight: `eu_nation_daily_sync_flight` — daily
  BAML backfill for the 30 per-nation sources

#### Scenario: A new Ukrainian curriculum row lands

- **WHEN** the Ukrainian education DLT source emits a new row
- **THEN** the daily Flight MUST pick it up within 24h
- **AND** the `eu_nation_curriculum_matrix` Dive MUST reflect the new
  row within 60 seconds of the Flight completing

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-union-official-language-pipeline`](../european-union-official-language-pipeline/spec.md) —
  the institutional counterpart
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the seed instance of the per-nation pattern
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- [`oideachais-baml-schemas`](../oideachais-baml-schemas/spec.md) —
  the BAML cluster taxonomy
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
