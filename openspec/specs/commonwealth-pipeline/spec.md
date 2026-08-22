# commonwealth-pipeline Specification

## Purpose
The Commonwealth of Nations pipeline surface covers Australia + Canada (12 provinces + Quebec/Montreal) + India + New Zealand + Nigeria (federal + 36 states) + South Africa across the Cianfhoghlaim monorepo. It defines 12 invariants: the canonical commonwealth/ directory path, the per-nation + per-state + per-province sub-state convention, the English + French language support, the per-nation education system mappings (ACARA, provincial ministries, NCERT, NZQA, NECO, DBE), the cross-nation registry integration, the per-stage source routing, the Indigenous language support (Māori, Hindi, Yoruba, Igbo, Zulu, Xhosa, Afrikaans), the Quebec/Montreal French-language handling, the federal/state split for Nigeria, the per-nation BAML extraction templates, the per-nation cognitive layer rules, and the per-nation marimo notebook convention.

## Requirements
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
at `baml/commonwealth/<iso3>/education.baml` that
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

### Requirement: Nigeria federal + 36 states + FCT DLT scaffolding

The system MUST provide DLT sources for the Nigerian federal tier
(10 sources) + 36 states + the Federal Capital Territory (Abuja)
for a total of 37 sub-units × 5 domains = 185 state DLT sources.

The 37 sub-units are: Abia, Adamawa, Akwa Ibom, Anambra, Bauchi,
Bayelsa, Benue, Borno, Cross River, Delta, Ebonyi, Edo, Ekiti, Enugu,
FCT (Abuja), Gombe, Imo, Jigawa, Kaduna, Kano, Katsina, Kebbi, Kogi,
Kwara, Lagos, Nasarawa, Niger, Ogun, Ondo, Osun, Oyo, Plateau, Rivers,
Sokoto, Taraba, Yobe, Zamfara.

State DLT files MUST live at
`dlt/commonwealth/nga/states/<state_slug>/<domain>/<ministry>.py`
with the per-state language partition (`en` + the state's majority
language).

#### Scenario: Lagos state ships 5 sources

- **WHEN** the Nigeria pipeline change is materialised
- **THEN** the system MUST provide 5 DLT sources under
  `dlt/commonwealth/nga/states/los/`:
  - `dlt/commonwealth/nga/states/los/education/<ministry>.py`
  - `dlt/commonwealth/nga/states/los/law/<legislation>.py`
  - `dlt/commonwealth/nga/states/los/medicine/<health_authority>.py`
  - `dlt/commonwealth/nga/states/los/statistics/<stats_office>.py`
  - `dlt/commonwealth/nga/states/los/government/<gov_portal>.py`
- **AND** each source MUST partition on
  `language ∈ ("en", "yo")` (Lagos = Yoruba majority)

### Requirement: Nigeria BAML extraction

The system MUST provide 2 BAML extraction functions:

- `ExtractNigerianFederalCurriculumSpec(federal_institution, language, text)`
- `ExtractNigerianStateCurriculumSpec(state_code, language, text)`

#### Scenario: A Nigerian federal curriculum document is extracted

- **WHEN** the federal education DLT source yields a new NUC curriculum
  document
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractNigerianFederalCurriculumSpec(federal_institution="nuc",
   language="en", text=<text>)`
- **AND** the resulting record MUST carry
  `federal_institution="nuc"`, `language="en"`, the curriculum name,
  the degree type, and the course list

### Requirement: Nigeria CocoIndex v1 + Dagster + MotherDuck

The system MUST provide:

- 1 CocoIndex v1 App (`nigeria_education_embedding`) that embeds
  every Nigerian federal + state education row into a shared LanceDB
  table partitioned by `state_code + language`
- 1 MotherDuck Dive (`nigeria_state_curriculum_matrix`) that surfaces
  the cross-state coverage matrix
- 1 daily MotherDuck Flight (`nigeria_daily_sync_flight`) that
  BAML-backfills the Nigerian sources

#### Scenario: A new Lagos state curriculum row lands

- **WHEN** the Lagos state education DLT source emits a new row
- **THEN** the daily Flight MUST pick it up within 24h
- **AND** the `nigeria_education_embedding` CocoIndex v1 App MUST
  embed the row into the shared LanceDB table
  `oideachais.commonwealth.nga.education_chunks` partitioned by
  `(state_code="los", language="yo" | "en")`
- **AND** the `nigeria_state_curriculum_matrix` Dive MUST reflect the
  new row within 60 seconds of the Flight completing

### Requirement: 13 Canadian provinces + 3 territories DLT scaffolding

The system MUST provide per-province DLT sources for all 13
Canadian provinces + territories, partitioning on the jurisdiction's
official language(s) (`en` always, plus `fr` for federal + Quebec +
New Brunswick; plus indigenous language codes where relevant).

The 13 jurisdictions are: Ontario (`on`), Quebec (`qc`), British
Columbia (`bc`), Alberta (`ab`), Saskatchewan (`sk`), Manitoba
(`mb`), Nova Scotia (`ns`), New Brunswick (`nb`), PEI (`pe`),
Newfoundland & Labrador (`nl`), Northwest Territories (`nt`),
Nunavut (`nu`), Yukon (`yt`).

Each jurisdiction MUST ship 5 DLT sources (one per canonical domain)
at `dlt/commonwealth/can/<prov>/<domain>/<source>.py`.

#### Scenario: Quebec ships 5 sources + 1 deep education cluster

- **WHEN** the Canada-provinces change is materialised
- **THEN** the system MUST provide the 5 baseline Quebec sources at
  - `dlt/commonwealth/can/qc/education/mees.py`
  - `dlt/commonwealth/can/qc/law/quebec_legislation.py`
  - `dlt/commonwealth/can/qc/medicine/msss.py`
  - `dlt/commonwealth/can/qc/statistics/isq.py`
  - `dlt/commonwealth/can/qc/government/quebec_portal.py`
- **AND** the system MUST provide the 5 deep Quebec education
  cluster sources at
  - `dlt/commonwealth/can/qc/education/mees.py` (Ministry)
  - `dlt/commonwealth/can/qc/education/cssdm.py` (French Montreal)
  - `dlt/commonwealth/can/qc/education/emsb.py` (English Montreal)
  - `dlt/commonwealth/can/qc/education/lbpsb.py` (Lester B. Pearson)
  - `dlt/commonwealth/can/qc/education/mcgill_universities.py`
    (Montreal university cluster)
- **AND** each source MUST partition on
  `language ∈ ("fr", "en")` with `default_language="fr"`

### Requirement: Bilingual Quebec education extraction

The system MUST provide a BAML extraction function
`ExtractQuebecEducationDocument(province, language, text) -> QuebecEducationBilingualRecord`
that returns a record carrying bilingual (French + English) text for
the title, summary, and learning-outcome fields. The default language
for every Quebec partition MUST be French (`fr`).

#### Scenario: A MEES curriculum document is extracted

- **WHEN** the MEES DLT source yields a new curriculum framework
  document in French
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractQuebecEducationDocument(province="qc", language="fr", text=<text>)`
- **AND** the resulting `QuebecEducationBilingualRecord` MUST carry
  `language="fr"`, `province="qc"`, the curriculum framework name,
  the level (preschool / primary / secondary / CEGEP / university),
  and the bilingual learning outcomes

### Requirement: Montreal school boards bilingual coverage

The system MUST provide DLT sources for the 3 Montreal school boards
with bilingual partitioning:

- `cssdm` — Centre de services scolaire de Montréal (default `fr`)
- `emsb` — English Montreal School Board (default `en`)
- `lbpsb` — Lester B. Pearson School Board (default `en`)

#### Scenario: The EMSB publishes a new English-language policy

- **WHEN** the EMSB DLT source ingests a new policy document
- **THEN** the system MUST emit one row per available language
  edition (typically English only)
- **AND** the row MUST carry `language="en"`, `school_board="emsb"`,
  `province="qc"`, the policy ID, the publication date, the source URL

### Requirement: Canada CocoIndex v1 + Dagster + MotherDuck

The system MUST provide:

- 1 CocoIndex v1 App (`quebec_montreal_education_embedding`) that
  embeds every Quebec + Montreal education row into a shared
  LanceDB table partitioned by `language ∈ ("fr", "en")`
- 1 MotherDuck Dive (`quebec_montreal_curriculum_matrix`) that
  surfaces the cross-language curriculum coverage matrix
- 1 daily MotherDuck Flight (`canada_daily_sync_flight`)

#### Scenario: A new Quebec + Montreal curriculum row lands

- **WHEN** the MEES DLT source emits a new curriculum document
- **THEN** the daily Flight MUST pick it up within 24h
- **AND** the `quebec_montreal_education_embedding` CocoIndex v1 App
  MUST embed the row into the shared LanceDB table
  `oideachais.commonwealth.can.qc.education_chunks`
- **AND** the `quebec_montreal_curriculum_matrix` Dive MUST reflect
  the new row within 60 seconds of the Flight completing

