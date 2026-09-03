## ADDED Requirements

### Requirement: 12 ADK agents use SequentialAgent / ParallelAgent patterns

The system SHALL use the `SequentialAgent` and `ParallelAgent`
classes from `google-adk>=1.10.0` for the 12 ADK agents at
`agents/adk/*.py` instead of bare `LlmAgent` peers.

The reason: per the `2025-08-19-interruptible-agents` demo and the
`llm-auditor` sample, `SequentialAgent` makes the deterministic
flow explicit (e.g., the 12-agent bootstrap is a chain of root →
curriculum → translation → corpus → research).

#### Scenario: SequentialAgent replaces bare LlmAgent chain

- **GIVEN** the 12 ADK agents at `agents/adk/*.py`
- **WHEN** the operator runs
  `python -c "from agents.adk.enhanced_orchestrator import orchestrator; print(type(orchestrator))"`
- **THEN** the `orchestrator` is a `SequentialAgent` (not a bare
  `LlmAgent`)
- **AND** the orchestrator's `sub_agents` list contains all 12 agents
  in the canonical order

### Requirement: 12 ADK agents use BuiltInPlanner + ToolContext.state

The system SHALL use `BuiltInPlanner` (with `thinking_config` +
`include_thoughts=True`) + `ToolContext.state` for all 12 ADK agents
so the agents can inject dashboard state into the prompt + mutate
UI state directly.

The reason: per the `adk-dashboard` sample, `BuiltInPlanner` +
`ToolContext.state` enables context-aware state injection and
prevents consecutive tool calling.

#### Scenario: Every ADK agent uses BuiltInPlanner

- **WHEN** `mise run lint:adk-builtin-planner-coverage` runs
- **THEN** every ADK agent that has a planner MUST use
  `BuiltInPlanner(thinking_config=genai_types.ThinkingConfig(include_thoughts=True))`
- **AND** the lint returns `OK: 12/12 agents with planner`

### Requirement: 12 ADK agents use output_schema (Pydantic)

The system SHALL auto-generate `output_schema` (Pydantic) for all 12
ADK agents via the `BAMLFunctionTool` integration helper (from the
fast-follow).

The reason: per `centralized-schema-registry`, BAML is the single
source of truth for structured data shapes. The 80 hand-written
Pydantic classes in `agents/adk/*.py` are now auto-generated from
BAML.

#### Scenario: Every ADK agent uses BAML-generated Pydantic classes

- **WHEN** the operator runs
  `python -c "from baml_client.types import *; from agents.adk.curriculum_agent import CurriculumAgentOutput; print(issubclass(CurriculumAgentOutput, BaseModel))"`
- **THEN** the agent's `output_schema` is a BAML-generated Pydantic
  class
- **AND** no `BaseModel` re-declaration exists in `agents/adk/*.py`

### Requirement: 8 NCCA Junior Cycle ADK agents

The system SHALL provide 8 ADK agents for the 8 NCCA Junior Cycle
subjects (Mathematics, English, Gaeilge, Science, Geography,
History, CSPE, SPHE). Each agent is auto-generated from the BAML
Junior Cycle template via the `BAMLFunctionTool`.

#### Scenario: Each JC subject has a dedicated ADK agent

- **GIVEN** the 8 NCCA Junior Cycle subjects
- **WHEN** the operator runs
  `python -c "from agents.adk import jc_subject_agent; print(jc_subject_agent.subjects)"`
- **THEN** the output lists 8 agents with their subjects

### Requirement: 4 stage ADK agents (lc_subject_agent, jc_subject_agent, alevel_subject_agent, gcse_subject_agent)

The system SHALL provide 4 stage-specific ADK agents that wrap the
BAML stage templates (one per stage: lc_subject_agent, jc_subject_agent,
alevel_subject_agent, gcse_subject_agent).

#### Scenario: Each stage has a dedicated ADK agent

- **GIVEN** the 4 stages
- **WHEN** the operator inspects `agents/adk/`
- **THEN** the directory contains 4 stage agents + 8 NCCA JC subjects
  + 12 baseline agents = 24 ADK agents total