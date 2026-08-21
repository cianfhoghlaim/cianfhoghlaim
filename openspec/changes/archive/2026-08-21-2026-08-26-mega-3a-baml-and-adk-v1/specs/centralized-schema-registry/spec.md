## ADDED Requirements

### Requirement: Pydantic classes auto-generated from BAML

The system SHALL auto-generate all 80 Pydantic classes currently
declared in `agents/adk/*.py` from the BAML class definitions at
`baml_src/british_isles/_shared/*.baml` via the `BAMLFunctionTool`
integration helper (from the fast-follow).

The reason: per the `centralized-schema-registry` spec, BAML is the
single source of truth. The 80 hand-written Pydantic duplicates are
redundant.

#### Scenario: All 80 Pydantic classes are auto-generated

- **WHEN** the operator runs `mise run baml:generate`
- **THEN** the `baml_client.types` module exposes all 80 classes
  (vs the 21 hand-written ones)
- **AND** no `BaseModel` re-declaration exists in `agents/adk/*.py`

### Requirement: 5 stage templates drive 4-stage plane codegen

The system SHALL ensure that the 5 BAML stage templates
(`lc_extraction_template.baml`, `junior_cycle_template.baml`,
`alevel_extraction_template.baml`, `gcse_extraction_template.baml`,
`qpack_template.baml`) generate consistent Pydantic classes that
match the canonical 4-stage plane schema.

#### Scenario: Generated types match across all 4 stages

- **GIVEN** the 5 BAML stage templates
- **WHEN** `mise run baml:generate` runs
- **THEN** every generated Pydantic class has:
 - A `subject: string` field (the canonical subject slug)
 - A `language: string` field (the canonical language code)
 - A `stage: <StageEnum>` field (the canonical stage enum)
 - A `lineage: LineageTrace?` field (per the R28 lineage spec)
- **AND** the lint returns `OK: 4-stage plane codegen consistent`

### Requirement: qpack codegen invariant

The system SHALL ensure that every `qpack_*.baml` function uses the
same canonical output schema (driven by `qpack_template.baml`).

The reason: per the user's choice on Q15, the 8 qpack files
collapse to 1 template. The codegen invariant ensures all generated
`FormativeItem` classes match.

#### Scenario: All qpack functions use the same FormativeItem schema

- **WHEN** `mise run lint:qpack-schema-consistency` runs
- **THEN** every `GenerateSubjectFormativeItem` function in the
  generated `baml_client.types` has the same field set:
  `item_id`, `lo_code`, `subject`, `language`, `difficulty`,
  `item_type`, `prompt_text`, `expected_response`, `marking_scheme_points`
- **AND** the lint returns `OK: 4-stage plane qpack consistent`