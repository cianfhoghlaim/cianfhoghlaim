## ADDED Requirements

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

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`commonwealth-pipeline`](../commonwealth-pipeline/spec.md) —
  the parent pipeline
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the bilingual reference (Ireland `en` + `ga`)
- [`european-nations-ukraine-pipeline`](../european-nations-ukraine-pipeline/spec.md) —
  the multilingual sibling (UKR/FR/GA/DE/PL/ES/IT)
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
