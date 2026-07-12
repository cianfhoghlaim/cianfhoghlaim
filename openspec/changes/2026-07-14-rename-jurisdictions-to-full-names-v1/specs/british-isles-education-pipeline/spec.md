## ADDED Requirements

### Requirement: BIEP display strings use full nation names

The system MUST use the full British Isles nation name (Scotland /
England / Wales / Northern Ireland / Isle of Man / Jersey /
Guernsey / Ireland) in every BAML class + function name, Python
class name, docstring, Dagster `metadata.country_name`, and MotherDuck
Dive description for the BIEP layer. The short identifiers
(`sct`, `wls`, `en`, `ni`, `isle_of_man`, `jersey`, `guernsey`,
`ireland`) remain in file paths, source_id strings, partition
values, and DuckLake table names.

#### Scenario: Scotland BAML class uses the full name

- **WHEN** the rename change is materialised
- **THEN** the BAML class at `baml/education/sct/education.baml`
  MUST be named `class ScotlandSubjectCurriculum`
- **AND** the function MUST be named
  `function ExtractScotlandSubjectCurriculum`
