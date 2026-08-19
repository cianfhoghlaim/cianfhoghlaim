## ADDED Requirements

### Requirement: Marimo `mo.ai.llm.openai` for native LLM-from-notebook

The system SHALL use `mo.ai.llm.openai(base_url=LITELLM_BASE_URL,
model="minimax-m3")` (per the marimo patterns tour) to allow direct
LLM-from-notebook calls.

The default model is `minimax-m3` (the canonical 7-tier fallback).

#### Scenario: The operator uses mo.ai.llm in a notebook

- **GIVEN** a BIEP v3 dashboard
- **WHEN** the operator runs `mo.ai.llm.openai(base_url=LITELLM_BASE_URL, model="minimax-m3")("Summarise this NCCA syllabus")`
- **THEN** the LLM returns the summary via the canonical 7-tier fallback

### Requirement: Marimo `mo.ui.dropdown` for the model selector

The system SHALL use `mo.ui.dropdown(...)` to allow the operator
to select between `minimax-m3` + `uccix-mistral-24b` + `gemma-4-26B-A4B`
+ `qwen3-vl-8b`.

#### Scenario: The operator selects a different model

- **GIVEN** a BIEP v3 dashboard
- **WHEN** the operator opens the "Model" dropdown
- **THEN** the dropdown shows 4 options (minimax-m3, uccix-mistral-24b,
  gemma-4-26B-A4B, qwen3-vl-8b) + the default value is `minimax-m3`