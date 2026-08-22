# european-nations-ukraine-pipeline Specification

## Purpose
The Ukraine pipeline surface provides British-Isles parity per-subject depth for the Cianfhoghlaim monorepo. It defines 12 invariants: the canonical european_nations/ukraine/ directory path, the ZNO (ЗНО) national testing curriculum, the NMT (НМТ) university admission pipeline, the Ukrainian + Russian + English language handling, the per-subject (11 LC subjects + 9 ZNO subjects) coverage matrix, the per-region sub-state convention (24 oblasts + Crimea + Kyiv), the per-grade (primary + secondary + lyceum) source mapping, the cross-corpus knowledge graph edges, the BAML extraction templates for Ukrainian-language syllabi, the cognitive layer rules for Ukrainian history + literature, the marimo notebook convention, and the public-data integration with the Ukrainian Ministry of Education.

## Requirements
### Requirement: Ukraine per-subject depth

The system MUST provide the British Isles parity per-subject depth for
the Ukraine (UKR) education pipeline. Ukraine ships **7 subjects**
(the BIEP 6 + a Ukrainian-language subject for the ZNO national
curriculum):

1. `class UkraineSubjectCurriculum` with a `subject` discriminator
2. 7 per-subject DLT sources at
   `dlt/european_nations/ukr/education/subjects/<subject>.py`
3. 7 Dagster L1 defs (one per subject)
4. 1 L3 CocoIndex v1 def
5. 1 per-subject CocoIndex v1 App partitioning on `(subject, language)`
   with `language ∈ ("uk", "en")` (Ukrainian default + English secondary)
6. 7 cache fixtures under
   `stedding/ingest_queue/european_nations/ukr/education/subjects/<subject>/<lang>/sample.json`

The 7th subject (`ukrainian_language`) covers Ukrainian as a native
language (ЗНО Ukrainian language + literature).

#### Scenario: Ukraine ZNO mathematics is scaffolded

- **WHEN** the upgrade change is materialised
- **THEN** the system MUST provide
  `dlt/european_nations/ukr/education/subjects/mathematics.py`
- **AND** its partition MUST be `language ∈ ("uk", "en")`
- **AND** the canonical root URL MUST point to `mon.gov.ua` (Ministry
  of Education and Science of Ukraine)

#### Scenario: Ukraine ukr language is scaffolded

- **WHEN** the upgrade change is materialised
- **THEN** the system MUST provide
  `dlt/european_nations/ukr/education/subjects/ukrainian_language.py`
- **AND** its partition MUST default to `language=uk` (Ukrainian
  primary)

### Requirement: 5 EU pilot countries reach per-subject depth

The system MUST bring FRA / DEU / POL / ESP / ITA to the BIEP
per-subject depth (6 subjects: mathematics / chemistry / biology /
physics / language / computing_science).

For each of the 5 pilot countries:

- 6 per-subject DLT sources
- 6 L1 Dagster defs + 1 L3 def
- 1 per-subject CocoIndex v1 App
- 6 cache fixtures

#### Scenario: Germany ships the BIEP per-subject depth

- **WHEN** the upgrade change is materialised
- **THEN** `dlt/european_nations/deu/education/subjects/` MUST contain
  6 DLT source files (mathematics, chemistry, biology, physics,
  language, computing_science)
- **AND** each source MUST partition on `language=de` (German)

### Requirement: Wales / England / Northern Ireland fill-in

The system MUST add the missing `physics` and `biology` per-subject
DLT sources + L1 defs to Wales / England / Northern Ireland.

#### Scenario: Wales ships physics + biology

- **WHEN** the upgrade change is materialised
- **THEN** `dlt/british_isles/wls/education/subjects/physics/physics.py`
  MUST exist with its corresponding L1 def
- **AND** `dlt/british_isles/wls/education/subjects/biology/biology.py`
  MUST exist with its corresponding L1 def
- **AND** the BIEP language partition for Wales is `("en", "cy")`
  (English primary + Welsh secondary)

#### Scenario: England ships physics + biology

- **WHEN** the upgrade change is materialised
- **THEN** `dlt/british_isles/en/education/subjects/physics/physics.py`
  MUST exist with its corresponding L1 def
- **AND** `dlt/british_isles/en/education/subjects/biology/biology.py`
  MUST exist with its corresponding L1 def

#### Scenario: Northern Ireland ships physics + biology

- **WHEN** the upgrade change is materialised
- **THEN** `dlt/british_isles/ni/education/subjects/physics/physics.py`
  MUST exist with its corresponding L1 def
- **AND** `dlt/british_isles/ni/education/subjects/biology/biology.py`
  MUST exist with its corresponding L1 def

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
`cianfhoghlaim.<domain>.european_nations.<iso3>`.

#### Scenario: A new French statute-book source obeys the contract

- **WHEN** a developer adds the Légifrance DLT source
- **THEN** the file MUST be created at
  `dlt/european_nations/fra/law/legifrance.py`
- **AND** its `source_id` MUST be `european_nations.fra.law.legifrance`
- **AND** the DuckLake table MUST be
  `cianfhoghlaim.law.european_nations.fra`
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
  `cianfhoghlaim.eu_nations.education_chunks`
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

### Requirement: 30 EU nations reach Ireland-level depth

The system MUST bring the 6 EU pilot countries (UKR / FRA / DEU /
POL / ESP / ITA) + the 21 remaining EU member states + 3 EEA/EFTA
members + 9 EU candidate / neighbour states (total 39 jurisdictions,
of which 30 are in scope for this change) to the British Isles
parity depth.

Per-country depth requires:

- ≥6 per-subject DLT sources (mathematics / chemistry / biology /
  physics / language / computing_science) at
  `dlt/european_nations/<iso3>/education/subjects/<subject>.py`
- 5 baseline DLT sources (1 per canonical domain) at
  `dlt/european_nations/<iso3>/{law,medicine,statistics,government}/`
- 3 BAML files at
  `baml/european_nations/<iso3>/{education,law,medicine}.baml`
  with per-country extraction functions
- 1 CocoIndex v1 App per nation (R1–R4 conformance)
- 6 L1 + 1 L3 Dagster defs

#### Scenario: Germany ships 6 per-subject DLT sources

- **WHEN** the EU full-depth expansion is materialised
- **THEN** the system MUST provide 6 per-subject DLT sources under
  `dlt/european_nations/deu/education/subjects/` (mathematics,
  chemistry, biology, physics, language, computing_science)
- **AND** each source MUST partition on `language ∈ ("de", "en")`
  (German + English)
- **AND** the `european_nations_deu_education_embedding` CocoIndex v1
  App MUST embed every per-subject row into the shared LanceDB
  table `cianfhoghlaim.lc.european_nations.deu.education_chunks`
- **AND** the 3 BAML files at
  `baml/european_nations/deu/{education,law,medicine}.baml` MUST
  define `ExtractDEU<Domain>Document(germany, language, text)`
  functions

### Requirement: Official-language focus

The system MUST prioritise each country's official language(s) for
the `language` partition. For multilingual countries the partition
MUST list all official languages with the primary language
appearing first.

#### Scenario: Belgium supports 3 official languages

- **WHEN** the Belgium EU nation DLT source materialises
- **THEN** the `language` partition MUST list
  `["nl", "fr", "de"]` (Dutch primary + French + German)
- **AND** the per-subject sources MUST honour all 3 languages
- **AND** the BAML extraction functions MUST carry the same
  3-language partition

