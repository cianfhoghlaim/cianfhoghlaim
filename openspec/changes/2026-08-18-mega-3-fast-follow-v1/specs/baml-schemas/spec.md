## ADDED Requirements

### Requirement: BAML → CocoIndex codegen invariant for the 47 BIEP Apps

The system SHALL wire the 5 lc6 BAML functions
(`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
`ExtractMarkingSchemeGuideline`, `ExtractCrossLinguisticConcept`,
`ExtractSyllabusDiagram`) into the 47 BIEP CocoIndex Apps at
`cocoindex/biep_parity/*.py` so each App calls the BAML function via
the `BAMLFunctionTool` helper (FF.1).

The reason: per the `centralized-schema-registry` spec, BAML is the
single source of truth for structured data shapes. The 47 BIEP
CocoIndex Apps currently duplicate the LLM call logic instead of
delegating to the canonical BAML functions.

#### Scenario: Every BIEP CocoIndex App calls BAML

- **WHEN** `mise run lint:cocoindex-baml-coverage` runs
- **THEN** all 47 BIEP CocoIndex Apps at `cocoindex/biep_parity/*.py`
  MUST import at least 1 BAML function via `from baml_client.async_client import b`
- **AND** the App's `@coco.fn` MUST call the BAML function as part of
  the data flow
- **AND** the lint returns `OK: 47/47 Apps wired to BAML`

#### Scenario: BAML → ADK wiring via BAMLFunctionTool

- **GIVEN** the 6 LC-subject BAML functions in
  `baml_src/british_isles/ireland/education/subjects/qpack_*.baml`
- **WHEN** the operator runs `python -c "from agents.adk.curriculum_agent import curriculum_agent; print(curriculum_agent.tools)"`
- **THEN** the `curriculum_agent.tools` list contains at least 6
  `BAMLFunctionTool` instances
  (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
  `ExtractMarkingScheme`, `ExtractCrossLinguistic`,
  `ExtractSyllabusDiagram`, `ExtractTopic`)