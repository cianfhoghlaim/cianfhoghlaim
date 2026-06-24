## ADDED Requirements

### Requirement: cianfhoghlaim Pydantic schema validation

The `cianfhoghlaim` Space MUST validate every LLM response against the Pydantic schema (PNpcDialogue) before returning the dialogue to the UI. The Space MUST add `pydantic>=2.5` to `spaces/cianfhoghlaim/requirements.txt`.

#### Scenario: Pydantic validation fails

- **WHEN** the LLM response does not match the Pydantic schema
- **THEN** the Space logs a warning and falls back to the flat schema
- **AND** the dialogue still renders (the UI is never broken)

