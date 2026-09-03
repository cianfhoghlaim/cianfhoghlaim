## ADDED Requirements

### Requirement: anam_tuatha Pydantic schema validation

The `anam_tuatha` Space MUST validate every LLM response against the Pydantic schema (PExitCardSet) before returning the exit card to the UI. The Space MUST add `pydantic>=2.5` to `spaces/anam_sruth/tuatha/requirements.txt`.

#### Scenario: Pydantic validation fails

- **WHEN** the LLM response does not match the Pydantic schema
- **THEN** the Space logs a warning and falls back to the template bank
- **AND** the exit card still renders (the UI is never broken)
