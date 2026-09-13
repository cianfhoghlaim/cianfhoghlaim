## ADDED Requirements

### Requirement: 5 BAML stage templates + 8 NCCA JC agents

The system SHALL provide 5 BAML stage templates
(`lc_extraction_template.baml`, `junior_cycle_template.baml`,
`alevel_extraction_template.baml`, `gcse_extraction_template.baml`,
`qpack_template.baml`) and 12 ADK agents that consume them.

The 12 ADK agents are:
- 4 stage agents (`lc_subject_agent`, `jc_subject_agent`,
  `alevel_subject_agent`, `gcse_subject_agent`)
- 8 NCCA Junior Cycle subject agents (Mathematics, English, Gaeilge,
  Science, Geography, History, CSPE, SPHE)

#### Scenario: Every agent consumes the canonical BAML stage template

- **GIVEN** the 12 ADK agents
- **WHEN** the operator runs
  `python -c "from agents.adk import *; for a in [lc_subject_agent, jc_subject_agent, ...]: print(a.baml_template)"`
- **THEN** each agent references the canonical BAML template via
  `BAMLFunctionTool`
- **AND** no agent re-declares the BAML class in a hand-written
  `BaseModel`