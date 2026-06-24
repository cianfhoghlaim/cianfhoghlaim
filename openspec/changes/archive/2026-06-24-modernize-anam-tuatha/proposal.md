## Why

`spaces/anam_tuatha/mac_leinn.py` (the formative assessment exit
cards) has the same pattern as the other 3 spaces (C1-C3):
the BAML `GenerateExitCardQuestions` function has been promoted
to `tuatha/baml_src/player_assessment.baml` (A1) and the
LiteLLM gateway is the primary LLM tier (A2), but the Space's
`_coerce` still uses the flat legacy schema.

This change modernizes the Space (same pattern as C1-C3):

1. Add Pydantic v2 schemas (`PExitCardQuestion` + `PExitCardSet`) that mirror the canonical BAML classes
2. Update `_coerce` to validate against the Pydantic schema
3. Add `pydantic>=2.5` to `requirements.txt`

## What changes

- `spaces/anam_tuatha/mac_leinn.py` — add 2 Pydantic models + update `_coerce` to use them
- `spaces/anam_tuatha/requirements.txt` — add `pydantic>=2.5`
- 1 ADDED Requirement to `tuatha-platform` spec
- 1 ADDED Requirement to `spaces-cicd-pipeline` spec
