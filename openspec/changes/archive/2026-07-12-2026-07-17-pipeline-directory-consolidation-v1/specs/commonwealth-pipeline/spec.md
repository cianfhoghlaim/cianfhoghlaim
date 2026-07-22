# commonwealth-pipeline

## MODIFIED Requirements

### Requirement: Commonwealth jurisdiction directories use full names

Commonwealth jurisdiction directories SHALL use the snake_case full
name: `australia/`, `canada/`, `india/`, `nigeria/`,
`new_zealand/`, `south_africa/`. The ISO 3-letter codes (`aus/`,
`can/`, `ind/`, `nga/`, `nzl/`, `zaf/`) SHALL NOT appear as
directory names. The first-class sub-states (Canadian provinces,
Nigerian states) SHALL nest under the jurisdiction directory in
`provinces/` or `states/` subdirectories using the full name.

#### Scenario: canada provinces live at the full-name nested path

- **WHEN** the directory consolidation change is materialised
- **THEN** `baml_src/commonwealth/canada/provinces/alberta/`,
  `baml_src/commonwealth/canada/provinces/ontario/`, etc. SHALL
  exist
- **AND** `dlt/commonwealth/canada/provinces/alberta/education/`,
  etc. SHALL exist
- **AND** `baml_src/commonwealth/can/ab/`, `dlt/commonwealth/can/ab/`,
  etc. SHALL NOT exist

### Requirement: Nigeria states nest under nigeria/

The Nigeria state-level BAML + DLT sources SHALL live under
`baml_src/commonwealth/nigeria/states/<full>/` and
`dlt/commonwealth/nigeria/states/<full>/`. The legacy compound
slug `nga_los/` (Lagos) SHALL NOT appear as a directory name.

#### Scenario: Lagos state is in nigeria/states/lagos/

- **WHEN** the directory consolidation change is materialised
- **THEN** `baml_src/commonwealth/nigeria/states/lagos/` SHALL
  exist
- **AND** `dlt/commonwealth/nigeria/states/lagos/` SHALL exist
- **AND** `baml_src/commonwealth/nga/_shared/nigeria_states.baml`
  SHALL be re-rooted to
  `baml_src/commonwealth/nigeria/states/_states.baml`