## ADDED Requirements

### Requirement: BAML → CocoIndex codegen cross-validation

The system SHALL ensure that every BAML function imported by a
CocoIndex App has a corresponding generated Pydantic class in
`baml_client.types` (per the `centralized-schema-registry` spec).

The reason: BAML is the single source of truth. CocoIndex Apps that
call BAML functions MUST use the generated Pydantic types, not
hand-written ones.

#### Scenario: Every BAML → CocoIndex call uses generated types

- **GIVEN** the 47 BIEP CocoIndex Apps at `cocoindex/biep_parity/*.py`
- **WHEN** `mise run lint:cocoindex-baml-types` runs
- **THEN** every CocoIndex App MUST import its return types from
  `baml_client.types` (e.g.,
  `from baml_client.types import CurriculumSyllabus`)
- **AND** no CocoIndex App declares a hand-written Pydantic class
  that mirrors a BAML class
- **AND** the lint returns `OK: 47/47 Apps use generated types`