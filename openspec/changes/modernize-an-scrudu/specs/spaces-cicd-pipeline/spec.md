## MODIFIED Requirements

### Requirement: an_scrudu Pydantic schema validation

The `an_scrudu` Space MUST validate every LLM response against the Pydantic schema (PCircularExtraction) before returning the extraction to the UI. The validation MUST accept both the nested BAML shape (post-A1) and the flat legacy shape (pre-A1) for backward compatibility. The Space MUST add `pydantic>=2.5` to `spaces/an_scrudu/requirements.txt`.

#### Scenario: Schema validation fails

- **WHEN** the LLM response does not match the Pydantic schema
- **THEN** the Space logs a warning and falls back to the flat schema
- **AND** the heatmap still renders (the UI is never broken)
