# oideachais-baml-schemas

## MODIFIED Requirements

### Requirement: BAML schema directory layout uses full jurisdiction names

The BAML schema directory layout SHALL match the proposed canonical
layout: `baml_src/{european_nations,commonwealth,british_isles,
american_nations,european_union}/<full>/{education,law,medicine,
...}.baml`. The legacy ISO-3 paths (`baml_src/european_nations/deu/`,
`baml_src/commonwealth/can/`, `baml_src/education/{en,ni,sct,wls,...}/`,
`baml_src/americas/`) SHALL NOT exist as directories.

#### Scenario: BAML schema directory layout matches the canonical tree

- **WHEN** the directory consolidation change is materialised
- **THEN** `baml_src/european_nations/germany/education.baml` SHALL
  exist with `class GermanySubjectCurriculum`
- **AND** `baml_src/british_isles/ireland/education.baml` SHALL
  exist
- **AND** `baml_src/american_nations/united_states/california.baml`
  SHALL exist (lifting the legacy `baml_src/americas/us_us_ca/`
  hack)
- **AND** `baml_src/education/{en,ni,sct,wls,ggy,iom,jey,england,
  northern_ireland,scotland,wales,isle_of_man,guernsey,jersey}/`
  SHALL NOT exist as directories
- **AND** `baml_src/americas/` SHALL NOT exist