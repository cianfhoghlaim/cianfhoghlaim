## Why

`spaces/meaisin_cliste/curaclam.py` (Theme 3 of Space 2:
Curaclam Trasteorann) is the same pattern as an_scrudu: the
BAML `CompareCelticNations` function has been promoted to
`sruth/tuatha/baml_src/celtic_curriculum.baml` (A1) and the
LiteLLM gateway is the primary LLM tier (A2), but the Space's
`_coerce` function still uses the flat legacy schema.

This change modernizes the Space (same pattern as C1):

1. Add Pydantic v2 schemas (`PCurriculumMapping` + `PCrossNationComparison`) that mirror the canonical BAML classes
2. Update `_coerce` to validate against the Pydantic schema
3. Add `pydantic>=2.5` to `requirements.txt`

## What changes

- `spaces/meaisin_cliste/curaclam.py` — add 2 Pydantic models + update `_coerce` to use them
- `spaces/meaisin_cliste/requirements.txt` — add `pydantic>=2.5`
- 1 ADDED Requirement to `meaisinfhoghlaim-platform` spec
- 1 ADDED Requirement to `spaces-cicd-pipeline` spec
