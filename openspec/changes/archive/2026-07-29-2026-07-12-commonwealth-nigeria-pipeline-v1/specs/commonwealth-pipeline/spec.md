## ADDED Requirements

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

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`commonwealth-pipeline`](../commonwealth-pipeline/spec.md) —
  the parent pipeline
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the per-jurisdiction partition pattern reference
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
