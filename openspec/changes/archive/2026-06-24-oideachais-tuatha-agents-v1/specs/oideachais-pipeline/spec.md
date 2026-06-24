# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: V1 Celtic tutor agent (celtic_tutor_agent)

The system SHALL provide a Celtic-language tutor agent at
`oideachais.agents.adk.celtic_tutor_agent:celtic_tutor_agent` that
exposes the LlmAgent previously at
`tuatha.agents.adk.celtic_tutor:celtic_tutor_agent`. The agent
uses 4 tools: `search_curriculum_tool`, `get_vocabulary_tool`,
`translate_text_tool`, `get_learning_outcomes_tool`. The
`tuatha.agents.adk.celtic_tutor` file is a thin re-export of the
canonical agent.

#### Scenario: A consumer imports the agent via the oideachais path

- **GIVEN** the `oideachais.agents.adk.celtic_tutor_agent` module
- **WHEN** a consumer does `from oideachais.agents.adk.celtic_tutor_agent import celtic_tutor_agent`
- **THEN** the imported `celtic_tutor_agent` is a fully constructed
  `google.adk.agents.LlmAgent` with name `celtic_tutor_agent`

#### Scenario: A consumer imports the agent via the legacy tuatha path

- **GIVEN** the `tuatha.agents.adk.celtic_tutor` thin wrapper
- **WHEN** a consumer does `from tuatha.agents.adk.celtic_tutor import celtic_tutor_agent`
- **THEN** the imported `celtic_tutor_agent` is the **same object**
  as `oideachais.agents.adk.celtic_tutor_agent.celtic_tutor_agent`

### Requirement: V1 mythology narrator agent (mythology_narrator_agent)

The system SHALL provide a Celtic mythology narrator agent at
`oideachais.agents.adk.mythology_narrator_agent:mythology_narrator_agent`.
Uses 3 tools: `search_mythology_tool`, `get_character_info`,
`get_location_info`. The `tuatha.agents.adk.mythology_narrator`
file is a thin re-export.

#### Scenario: A consumer imports the agent via the oideachais path

- **GIVEN** the `oideachais.agents.adk.mythology_narrator_agent` module
- **WHEN** a consumer does `from oideachais.agents.adk.mythology_narrator_agent import mythology_narrator_agent`
- **THEN** the imported `mythology_narrator_agent` is a fully
  constructed `LlmAgent` with name `mythology_narrator_agent`

#### Scenario: A consumer imports the agent via the legacy tuatha path

- **GIVEN** the `tuatha.agents.adk.mythology_narrator` thin wrapper
- **WHEN** a consumer does `from tuatha.agents.adk.mythology_narrator import mythology_narrator_agent`
- **THEN** the imported `mythology_narrator_agent` is the **same
  object** as `oideachais.agents.adk.mythology_narrator_agent.mythology_narrator_agent`

### Requirement: V1 quest guide agent (quest_guide_agent)

The system SHALL provide a quest guide agent at
`oideachais.agents.adk.quest_guide_agent:quest_guide_agent` that
exposes the LlmAgent previously at
`tuatha.agents.adk.quest_guide:quest_guide_agent`. Uses 4 tools:
`get_quest_hints_tool`, `get_player_progress_tool`,
`search_related_curriculum`, `get_learning_outcomes_for_quest`.

#### Scenario: A consumer imports the agent via the oideachais path

- **GIVEN** the `oideachais.agents.adk.quest_guide_agent` module
- **WHEN** a consumer does `from oideachais.agents.adk.quest_guide_agent import quest_guide_agent`
- **THEN** the imported `quest_guide_agent` is a fully constructed
  `LlmAgent` with name `quest_guide_agent`

#### Scenario: A consumer imports the agent via the legacy tuatha path

- **GIVEN** the `tuatha.agents.adk.quest_guide` thin wrapper
- **WHEN** a consumer does `from tuatha.agents.adk.quest_guide import quest_guide_agent`
- **THEN** the imported `quest_guide_agent` is the **same object**
  as `oideachais.agents.adk.quest_guide_agent.quest_guide_agent`

### Requirement: V1 research assistant agent (research_assistant_agent)

The system SHALL provide a research assistant agent at
`oideachais.agents.adk.research_assistant_agent:research_assistant_agent`.
Uses 3 tools: `research_curriculum`, `research_mythology`,
`compare_languages`.

#### Scenario: A consumer imports the agent via the oideachais path

- **GIVEN** the `oideachais.agents.adk.research_assistant_agent` module
- **WHEN** a consumer does `from oideachais.agents.adk.research_assistant_agent import research_assistant_agent`
- **THEN** the imported `research_assistant_agent` is a fully
  constructed `LlmAgent` with name `research_assistant_agent`

#### Scenario: A consumer imports the agent via the legacy tuatha path

- **GIVEN** the `tuatha.agents.adk.research_assistant` thin wrapper
- **WHEN** a consumer does `from tuatha.agents.adk.research_assistant import research_assistant_agent`
- **THEN** the imported `research_assistant_agent` is the **same
  object** as `oideachais.agents.adk.research_assistant_agent.research_assistant_agent`

### Requirement: V1 Tuatha root agent (tuatha_root_agent)

The system SHALL provide a root orchestrator agent at
`oideachais.agents.adk.tuatha_root_agent:root_agent` that wraps
the 4 specialist agents as `sub_agents`. Also constructs the
`google.adk.apps.app.App(name="tuath")` and exports a
`classify_query(query) -> str` helper for routing
("tutor" / "mythology" / "quest" / "research").

The `tuatha.agents.adk.root_agent` thin wrapper re-exports the
root agent + the 4 specialists + the `app` + the `classify_query`
helper for backwards compatibility with
`tuatha.agents.orchestrator.AgentRegistry.initialize_defaults()`.

#### Scenario: A consumer imports the root agent via the oideachais path

- **GIVEN** the `oideachais.agents.adk.tuatha_root_agent` module
- **WHEN** a consumer does `from oideachais.agents.adk.tuatha_root_agent import root_agent`
- **THEN** the imported `root_agent` is a fully constructed
  `LlmAgent` with name `tuath_agent` and 4 sub_agents
  (`celtic_tutor_agent`, `mythology_narrator_agent`,
  `quest_guide_agent`, `research_assistant_agent`)

#### Scenario: A consumer classifies a query

- **GIVEN** the `tuatha.agents.adk.root_agent` thin wrapper
- **WHEN** a consumer calls `classify_query("translate hello into Irish")`
- **THEN** the function returns `"tutor"` (the first matching
  keyword bucket, per the v0 logic)

## REMOVED Requirements

(None.)
