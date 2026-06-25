## ADDED Requirements

### Requirement: CompareCelticNations Pydantic mirror

The canonical BAML function `CompareCelticNations` (in `sruth/tuatha/baml_src/celtic_curriculum.baml`) MUST have a Pydantic v2 mirror in `spaces/meaisin_cliste/curaclam.py`. The Pydantic classes (`PCurriculumMapping`, `PCrossNationComparison`) MUST mirror the BAML class shapes exactly, and `_coerce` MUST validate the LLM response against the Pydantic schema before falling back to the flat legacy schema.

#### Scenario: LLM returns valid CrossNationComparison

- **WHEN** the LiteLLM gateway returns a JSON object with `{mappings: [...], shared_year_levels: [...], notes: "..."}`
- **THEN** `_coerce` validates it against `PCrossNationComparison`
- **AND** on success, maps to the flat `CrossNationComparison` dataclass
- **AND** on failure, falls back to the flat schema with defaults

#### Scenario: Pydantic not installed

- **WHEN** `pydantic` is not in the requirements
- **THEN** the Space falls back to the flat legacy schema (no Pydantic validation)
- **AND** a warning is logged
