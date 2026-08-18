## ADDED Requirements

### Requirement: Marimo `mo.ui.chat` with BAML extraction (Phase 5)

The system SHALL use `mo.ui.chat(...)` + `mo.ai.llm.openai(...)` +
the `marimo_baml.py` helper to expose the 5 lc6 BAML extraction
functions as a chat handler (per the 2026-08-18-mega-3-fast-follow-v1
change FF.2).

#### Scenario: The operator extracts a curriculum via chat

- **GIVEN** a BIEP v3 LC dashboard
- **WHEN** the operator asks the chat "Extract the chemistry syllabus"
- **THEN** the chat calls `b.ExtractCurriculumSyllabus(subject="chemistry", ...)`
  and displays the canonical CurriculumSyllabus output

### Requirement: Marimo `mo.ui.chat` with generative UI (A2UI surfaces)

The system SHALL use `mo.ui.chat(...)` with the A2UI surface generator
(per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change) so
the operator can ask "Show me the lineage of this PDF" and get an
A2UI lineage surface as the response.

#### Scenario: The chat emits an A2UI surface

- **GIVEN** a BIEP v3 dashboard
- **WHEN** the operator asks the chat "Show me the lineage"
- **THEN** the chat emits an A2UI lineage surface (from
  `A2UISurfaceGenerator surface="lineage"`)