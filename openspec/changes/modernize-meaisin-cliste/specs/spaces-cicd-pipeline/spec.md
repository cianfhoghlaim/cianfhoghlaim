## ADDED Requirements

### Requirement: meaisin_cliste Pydantic schema validation

The `meaisin_cliste` Space MUST validate every LLM response against the Pydantic schema (PCrossNationComparison) before returning the comparison to the UI. The Space MUST add `pydantic>=2.5` to `spaces/meaisin_cliste/requirements.txt`.
