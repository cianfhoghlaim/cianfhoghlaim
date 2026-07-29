## ADDED Requirements

### Requirement: Display strings use full jurisdiction names

The system MUST use the full official jurisdiction name in every
**display string** (BAML class + function names, Python class
names, docstrings, BAML prompt bodies, MotherDuck Dive descriptions,
Dagster `metadata.country_name` field, CocoIndex v1 App descriptions).

The system MUST keep the **short ID** (ISO 3166-1 alpha-3 for
countries, `<iso3>_<sub>` for sub-states) in every **identifier**
(file paths, module names, variable names, `source_id` strings, asset
keys, Dagster partition values, DuckLake table names, cache
directory names, BAML parameter names).

#### Scenario: Germany BAML class uses the full name

- **WHEN** the rename change is materialised
- **THEN** the BAML class at `baml/european_nations/deu/education.baml`
  MUST be named `class GermanySubjectCurriculum`
  (NOT `class DEUSubjectCurriculum`)
- **AND** the BAML function MUST be named
  `function ExtractGermanySubjectCurriculum`
- **AND** the BAML parameter MUST still be `nation: string`
  (short ID preserved for compatibility)
- **AND** the BAML prompt body MUST mention "German curriculum"
- **AND** the source_id string MUST still be
  `european_nations.deu.education.<subject>`
- **AND** the Dagster partition value MUST still be `country: ["deu"]`
- **AND** the `defs.yaml` MUST add the new metadata field
  `country_name: "Federal Republic of Germany"`

#### Scenario: Nigeria state class uses the full state name

- **WHEN** the rename change is materialised
- **THEN** the BAML class at
  `baml/european_nations/nga/state.baml` for the Lagos state source
  MUST be named `class LagosStateSubjectCurriculum`
- **AND** the Python class at
  `dlt/european_nations/nga/states/nga_los/education/ministry_of_education.py`
  MUST be named `class LagosStateEducationSource(NationSource)`
- **AND** the `country_name` metadata field MUST be
  `"Lagos State, Federal Republic of Nigeria"`

### Requirement: Sub-state BAML class naming

The system MUST follow the sub-state BAML class naming convention:

- Nigerian states: `<FullStateName>SubjectCurriculum` (e.g.
  `LagosStateSubjectCurriculum`)
- US states: `<FullStateName>SubjectCurriculum` (no "State" suffix
  — "California" alone is unambiguous)
- Canadian provinces: `<FullProvinceName>SubjectCurriculum`
- Australian states: `<FullStateName>` CamelCase for multi-word names
  (e.g. `NewSouthWalesSubjectCurriculum`)

#### Scenario: Lagos State BAML class uses the full state name

- **WHEN** the rename change is materialised
- **THEN** the BAML class at `baml/european_nations/nga/state.baml`
  for the Lagos state MUST be named
  `class LagosStateSubjectCurriculum`
- **AND** the function MUST be named
  `function ExtractLagosStateSubjectCurriculum`
- **AND** the source_id string MUST still be
  `european_nations.nga.states.nga_los.education.<subject>`
  (the short `nga_los` is preserved as the identifier)

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the BIEP spec
- [`cianfhoghlaim-pipeline`](../cianfhoghlaim-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
