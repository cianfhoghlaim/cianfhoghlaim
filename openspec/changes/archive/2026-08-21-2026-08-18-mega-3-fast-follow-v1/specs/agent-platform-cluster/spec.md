## ADDED Requirements

### Requirement: BAMLFunctionTool integration helper

The system SHALL provide a `BAMLFunctionTool` integration helper at
`agents/integrations/baml_function_tool.py` that wraps any BAML
`async def` function as a Google ADK `FunctionTool`. The helper
auto-detects the BAML function from `baml_client.async_client.b` and
exposes it as a tool with the right schema (parameter names, types,
descriptions).

The helper replaces the 18 hand-written `FunctionTool` wrappers in
`agents/tools/*.py` (curriculum_search.py, corpus_search.py,
spatial_query.py, statistics_query.py, terminology.py,
translation_tools.py, etc.) — each of which manually wraps a Python
function as a tool.

#### Scenario: BAMLFunctionTool wraps any BAML function

- **GIVEN** the BAML function `ExtractCurriculumSyllabus` at
  `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml`
- **WHEN** the operator runs `from agents.integrations.baml_function_tool import BAMLFunctionTool; tool = BAMLFunctionTool("ExtractCurriculumSyllabus")`
- **THEN** the helper returns a `FunctionTool` instance with
  `name="ExtractCurriculumSyllabus"`, `description="Extract NCCA Leaving Certificate syllabus..."`,
  `parameters={text: string, subject: string}` (from the BAML signature)

#### Scenario: All 18 hand-written FunctionTool wrappers are replaced

- **WHEN** `mise run lint:baml-function-tool-coverage` runs
- **THEN** all 18 functions in `agents/tools/*.py` that match a BAML
  function signature MUST be replaced with `BAMLFunctionTool(<baml_name>)`
- **AND** the lint returns `OK: 18 wrappers replaced`

### Requirement: agent_ui_bridge integration helper

The system SHALL provide an `agent_ui_bridge` integration helper at
`agents/integrations/agent_ui_bridge.py` that ports `ag-ui-adk.ADKAgent`
+ `CopilotKitRuntime` integration. The helper wires any
`google.adk.agents.LlmAgent` to CopilotKit's AG-UI protocol.

The helper replaces the 6 `BuiltInPlanner` boilerplate patterns
(curriculum_comparison_agent, statistics_agent, education_research_agent,
research_agent, curriculum_agent, corpus_agent) that each manually
wire a planner + temperature + max_output_tokens.

#### Scenario: agent_ui_bridge exposes the 12 ADK agents to CopilotKit

- **GIVEN** the 12 ADK agents at `agents/adk/*.py`
- **WHEN** the operator runs `from agents.integrations.agent_ui_bridge import register_adk_agent; register_adk_agent(curriculum_comparison_agent)`
- **THEN** the helper emits the AG-UI registration event so the
  CopilotKit UI can route to it via `CopilotRuntime.agents[name]`

#### Scenario: BuiltInPlanner boilerplate is replaced

- **WHEN** `mise run lint:adk-builtin-planner-coverage` runs
- **THEN** all 6 ADK agents that use `BuiltInPlanner` MUST use the
  `agent_ui_bridge.make_planner_agent()` helper instead
- **AND** the lint returns `OK: 6 planners replaced`