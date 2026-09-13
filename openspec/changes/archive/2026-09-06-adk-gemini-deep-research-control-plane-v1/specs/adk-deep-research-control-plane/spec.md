## ADDED Requirements

### Requirement: ADK root agent orchestrates cross-domain routing
The system SHALL provide an ADK `SequentialAgent` named `cian_root`
that classifies the incoming `Query` by domain (curriculum / translation /
corpus / research / geospatial / statistics / curriculum_comparison /
mcp_curriculum), routes to one of the 8 ADK agents in
`AGENT_REGISTRY`, runs a quality loop via ADK `LoopAgent` wrapping the
`evaluator_agent` pattern, and emits AG-UI events for every step.

#### Scenario: Inbound curriculum query
- **WHEN** a `Query` with `domain=curriculum` arrives
- **THEN** `cian_root` MUST route to `curriculum_agent`
- **AND** MUST wrap the response in a `LoopAgent(max_iterations=2)` calling `evaluator_agent`
- **AND** MUST emit `EVENT_STATE_SNAPSHOT` + `EVENT_STATE_DELTA` AG-UI events

#### Scenario: Deep research trigger
- **WHEN** a `Query` with `domain=research` AND `query.research_kind=deep` arrives
- **THEN** `cian_root` MUST route to `research_agent`
- **AND** MUST call `GoogleDeepResearchBackend.deep_research()` as an ADK `FunctionTool`
- **AND** MUST pass through Deep Research `interactions` to AG-UI as `EVENT_TOOL_CALL` events

### Requirement: Gemini Deep Research API as default RESEARCH backend
The system SHALL provide a `GoogleDeepResearchBackend` class that
wraps the Gemini Deep Research API
(`https://ai.google.dev/gemini-api/docs/deep-research`) via the
`google-genai` SDK with the new `interactions` field. The backend MUST
be registered in `BACKEND_PRIORITY` as **top priority** for the
`RESEARCH` capability, displacing Firecrawl at that role.

#### Scenario: Backend priority resolution
- **WHEN** the `BackendRouter` resolves a `Capability.RESEARCH` request
- **THEN** `GoogleDeepResearchBackend` MUST be tried first
- **AND** Firecrawl MUST be tried second
- **AND** Crawl4AI MUST be tried third

#### Scenario: Deep Research stream event
- **WHEN** the Gemini Deep Research API emits an `interactions` update
- **THEN** the backend MUST convert it to an AG-UI `EVENT_TOOL_CALL_ARGS` event
- **AND** MUST log the event to Langfuse via `@observe`

### Requirement: Pipeline orchestrator wraps DLT + BAML + CocoIndex
The system SHALL provide a `pipeline_orchestrator` ADK sub-package
with 3 agents (`dlt_trigger_agent`, `cocoindex_index_agent`,
`baml_extract_agent`) wrapped in a `SequentialAgent` called
`pipeline_orchestrator`. Each agent MUST expose its operation as an
ADK `FunctionTool` registered in the agent's `tools` list.

#### Scenario: Run a 3-stage pipeline
- **WHEN** an ADK runtime call invokes `pipeline_orchestrator.run(source="dlt_sources._shared.gemini_deep_research")`
- **THEN** `dlt_trigger_agent` MUST invoke the DLT source and emit a `STATE_DELTA` event with `pipeline_run_id`
- **AND** `baml_extract_agent` MUST call `b.ExtractGeminiDeepResearchReport(text=...)` on each row
- **AND** `cocoindex_index_agent` MUST invoke `coco.update()` on the named CocoIndex App
- **AND** every step MUST be wrapped in a Langfuse `@observe` decorator

#### Scenario: Failure cascade
- **WHEN** `baml_extract_agent` returns a `quality_score < 0.6` for any row
- **THEN** `pipeline_orchestrator` MUST emit a `TOOL_CALL_ERROR` AG-UI event
- **AND** MUST fall back to the 4-tier provider chain (Unsloth → LiteLLM → MiniMax → Gemini)

### Requirement: Cross-repo mirror contract
The system SHALL provide a mirrored change in each of the 4 sibling
repos (`cianchosaint`, `ciancheiltis`, `tuatha`, `gemini_hackathon`)
that imports the new `adk-deep-research-control-plane` capabilities
via a thin per-repo adapter. Each mirror MUST satisfy the same 7
Requirements in this spec.

#### Scenario: Mirror existence
- **WHEN** `openspec list` is run against any of the 4 sibling repos
- **THEN** a change named `2026-09-06-adk-gemini-deep-research-control-plane-v1` MUST be listed
- **AND** the mirror change's `proposal.md` MUST reference this spec by ID

### Requirement: Browser stack gold-standard compliance
The system SHALL bring the `bonneagar/stacks/browser` stack into
6-file GOLD_STANDARD compliance by adding `sidecar.yaml` +
`secrets.env` + `blueprint.yaml` + `.env.example`, fixing the
`Dockerfile` CMD, and creating the missing `Dockerfile.mcp`.

#### Scenario: Stack validation passes
- **WHEN** `mise run devops:validate-stacks browser` is run
- **THEN** the `browser` stack MUST pass all 6 GOLD_STANDARD checks
- **AND** the 4 dead-code subdirectories (`agent_os/`, `gemini-3-flash/`, `polymarket-research/`, `tests/fixtures/html_samples/`) MUST be removed

### Requirement: Browser stack promotion to minimax alias
The system SHALL modify `bonneagar/stacks/browser/sruth_browser/agents/orchestrator.py`
to use the `minimax` LiteLLM alias (the canonical 7-tier fallback)
instead of the hard-coded `gemini-2.0-flash` model. The backend router
MUST resolve the `gemini-deep-research` alias to the latest Gemini
model with Deep Research support (`gemini-2.5-pro-deep-research`).

#### Scenario: Alias resolution
- **WHEN** the ADK orchestrator instantiates `LlmAgent(model="minimax")`
- **THEN** LiteLLM MUST resolve it through the 7-tier fallback chain (qwen3-vl-8b → gemma-4-26B-A4B → glm-4.6v-flash → openai/glm-4.6 → gemini/gemini-2.5-pro → minimax → stub)

### Requirement: AG-UI streaming of Deep Research interactions
The system SHALL modify `frontend/adapters/agui.py` to forward the
Gemini Deep Research `interactions` field as AG-UI `EVENT_TOOL_CALL_ARGS`
events, allowing CopilotKit consumers to render the multi-step research
process in real time.

#### Scenario: SSE stream
- **WHEN** a CopilotKit consumer subscribes to `/agui` and triggers a Deep Research call
- **THEN** the consumer MUST receive 1+ `EVENT_TOOL_CALL_ARGS` events
- **AND** MUST receive 1 final `EVENT_MESSAGES_SNAPSHOT` event with the synthesized report
