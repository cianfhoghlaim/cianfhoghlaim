## ADDED Requirements

### Requirement: ExtractCircularMeta Pydantic mirror

The canonical BAML function `ExtractCircularMeta` (in `sruth/oideachais/baml_src/circular_extraction.baml`) MUST have a Pydantic v2 mirror in `spaces/an_scrudu/extraction.py`. The Pydantic classes (`PCircularReference`, `PTopicDistribution`, `PMarkingSchemeSummary`, `PCircularExtraction`) MUST mirror the BAML class shapes exactly, and `_validate_and_coerce` MUST validate the LLM response against the Pydantic schema before falling back to the flat legacy schema.

#### Scenario: LLM returns the nested BAML shape

- **WHEN** the LiteLLM gateway returns a JSON object with `{circular: {...}, scheme: {topics: [...]}}`
- **THEN** `_validate_and_coerce` validates it against `PCircularExtraction`
- **AND** on success, maps to the flat `CircularExtraction` dataclass
- **AND** on failure, falls back to the flat schema with defaults

#### Scenario: Pydantic not installed

- **WHEN** `pydantic` is not in the requirements
- **THEN** the Space falls back to the flat legacy schema (no Pydantic validation)
- **AND** a warning is logged
