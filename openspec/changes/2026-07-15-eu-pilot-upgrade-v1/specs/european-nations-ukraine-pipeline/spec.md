## ADDED Requirements

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

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-nations-ukraine-pipeline`](../european-nations-ukraine-pipeline/spec.md) —
  the EU nations scaffold (parent of Ukraine)
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the BIEP parent spec (per-subject template)
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
