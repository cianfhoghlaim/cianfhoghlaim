## ADDED Requirements

### Requirement: GenerateExitCardQuestions Pydantic mirror

The canonical BAML function `GenerateExitCardQuestions` (in `tuatha/baml_src/player_assessment.baml`) MUST have a Pydantic v2 mirror in `spaces/anam_tuatha/mac_leinn.py`. The Pydantic classes (`PExitCardQuestion`, `PExitCardSet`) MUST mirror the BAML class shapes exactly, and `_coerce` MUST validate the LLM response against the Pydantic schema before falling back to the flat legacy schema.

#### Scenario: LLM returns valid ExitCardSet

- **WHEN** the LiteLLM gateway returns a JSON object with `{lesson_topic, subject, level, questions: [...], total_questions, estimated_completion_min}`
- **THEN** `_coerce` validates it against `PExitCardSet`
- **AND** on success, maps to the flat `ExitCardSet` dataclass
- **AND** on failure, falls back to the template bank
