## ADDED Requirements

### Requirement: BAML SSOT for Celtic Mythology + Irish History + Geography Curriculum

The system SHALL provide the single source of truth for Celtic mythology
extraction in `baml/celtic/mythology.baml` (8 functions), Irish dynastic
history extraction in `baml/celtic/irish_history.baml` (6 functions), and
Geography curriculum extraction in `baml/celtic/geography_curriculum.baml`
(4 functions).

The system SHALL NOT have handwritten Pydantic or Zod duplicate classes
for any of these 18 functions. Pydantic + Zod are codegen only.

#### Scenario: All 18 BAML functions codegen Pydantic + Zod
- **WHEN** the user runs `baml-cli generate`
- **THEN** Pydantic V2 classes are generated for all 18 functions
- **THEN** Zod schemas are generated for all 18 functions
- **THEN** no `.py` files outside `baml_client/` define classes with the same names