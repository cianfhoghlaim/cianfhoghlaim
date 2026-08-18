## ADDED Requirements

### Requirement: A2UI Protocol for 12 ADK agents

The system SHALL adopt the A2UI Protocol (per the
`ag-ui-adk` integration) for the 12 ADK agents so that each agent
can emit declarative UI surfaces (chart, graph, playback, lineage,
search) instead of hand-written React components.

The 12 agents get A2UI surfaces for their most common UI outputs:
- `curriculum_agent` → lineage viewer + search
- `curriculum_comparison_agent` → chart + search
- `corpus_agent` → search + graph
- `research_agent` → graph + playback
- `statistics_agent` → chart + lineage
- `education_research_agent` → lineage + playback
- `bunchloch_research_agent` → graph
- `geospatial_agent` → map playback + graph
- `translation_agent` → text
- `agui_curriculum_agent` → lineage
- `mcp_curriculum_agent` → chart
- `root_agent` → orchestrator surface

#### Scenario: Each agent emits an A2UI surface

- **GIVEN** the agent's response includes structured data (e.g.,
  the `curriculum_comparison_agent` returns a `SubjectComparison`
  with `nations`, `age_ranges`, `key_differences`)
- **WHEN** the CopilotKit UI receives the response
- **THEN** the AG-UI protocol emits an A2UI surface that renders the
  data declaratively (no hand-written React component)
- **AND** the surface is interactive (click to drill down, hover for
  details, etc.)

### Requirement: marimo_to_copilotkit integration helper

The system SHALL provide a `marimo_to_copilotkit` integration helper at
`notebooks/_shared/marimo_to_copilotkit.py` that mounts every marimo
notebook as a CopilotKit tool. The helper imports the notebook's
public functions and exposes them as `FunctionTool` instances.

The helper replaces the 4 hand-written fetch patterns in
`web/apps/cianfhoghlaim/components/` (KnowledgeGraphPanel,
PipelineStatus, RecentActivityFeed, SubjectAgentGrid).

#### Scenario: Every notebook becomes a CopilotKit tool

- **GIVEN** the 201 marimo notebooks at `notebooks/*.py`
- **WHEN** the operator runs `python -m notebooks._shared.marimo_to_copilotkit --list-tools`
- **THEN** the helper emits a list of 201 CopilotKit tools, one per
  notebook's public function
- **AND** each tool is documented with the notebook's description +
  parameter signature