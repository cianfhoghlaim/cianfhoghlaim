# Pipeline Orchestrator Agent Capability

## Purpose

`pipeline-orchestrator-agent` is the bundle of 3 ADK agents
(`dlt_trigger_agent`, `cocoindex_index_agent`, `baml_extract_agent`)
wrapped in a `SequentialAgent` called `pipeline_orchestrator` that
drives the canonical DLT → BAML → CocoIndex pipeline from inside the
ADK runtime.

## Requirements

### Requirement: 3 pipeline-trigger agents as ADK LlmAgents
The system SHALL provide 3 ADK `LlmAgent` subclasses — one per stage of
the canonical pipeline:

- `dlt_trigger_agent` (uses `run_dlt_source` FunctionTool)
- `baml_extract_agent` (uses `extract_baml_function` FunctionTool)
- `cocoindex_index_agent` (uses `update_cocoindex_app` FunctionTool)

Each agent MUST resolve its LLM model via `MODEL_REGISTRY.resolve("text_llm", "default")`.

#### Scenario: Agent initialisation
- **WHEN** `pipeline_orchestrator` is instantiated
- **THEN** all 3 agents MUST be initialised with the `minimax` LiteLLM alias
- **AND** each agent MUST register exactly 1 FunctionTool

### Requirement: SequentialAgent orchestration
The system SHALL wrap the 3 agents in an ADK `SequentialAgent` named
`pipeline_orchestrator` that runs them in dependency order:
`dlt_trigger_agent` → `baml_extract_agent` → `cocoindex_index_agent`.

#### Scenario: Run pipeline in order
- **WHEN** `pipeline_orchestrator.run(source="...")` is called
- **THEN** `dlt_trigger_agent` MUST run first
- **AND** `baml_extract_agent` MUST run second (consuming DLT output)
- **AND** `cocoindex_index_agent` MUST run third (consuming BAML-extracted rows)

### Requirement: LoopAgent quality loop around baml_extract_agent
The system SHALL wrap `baml_extract_agent` in an ADK `LoopAgent`
called `extract_quality_loop` with `max_iterations=3` that retries on
rows where `quality_score < 0.6`, falling back to the 4-tier provider
chain.

#### Scenario: Retry on low quality
- **WHEN** `baml_extract_agent` returns a row with `quality_score < 0.6`
- **THEN** `extract_quality_loop` MUST retry up to 3 times
- **AND** MUST fall back through Unsloth → LiteLLM → MiniMax → Gemini providers
- **AND** MUST emit a `TOOL_CALL_ERROR` AG-UI event if all 3 retries fail
