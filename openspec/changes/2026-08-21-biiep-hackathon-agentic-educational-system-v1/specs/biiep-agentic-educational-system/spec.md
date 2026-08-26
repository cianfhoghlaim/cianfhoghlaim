## ADDED Requirements

### Requirement: 13-agent ADK fleet (the headline)

The system SHALL provide 13 ADK agents that collectively cover the British
Isles education system across 6 jurisdictions (Ireland, England, Scotland,
Wales, Northern Ireland, Isle of Man). The 13 agents are inherited from
the canonical cianfhoghlaim monorepo at `sruth/oideachais/agents/adk/`
and auto-exposed via `__init__.py`:

1. `root_agent` — the orchestrator + query router
2. `curriculum_agent` — 6-jurisdiction curriculum search
3. `corpus_agent` — Dúchas + Gaois + UD corpus search
4. `research_agent` — long-form research + citations
5. `translation_agent` — Celtic-language translation (fallback)
6. `geospatial_agent` — LSOA / Data Zone spatial analysis
7. `statistics_agent` — education metrics + benchmarking
8. `curriculum_comparison_agent` — cross-jurisdiction curriculum mapping
9. `enhanced_orchestrator` — long-running task orchestrator
10. `agui_curriculum_agent` — AG-UI streaming consumer
11. `education_research_agent` — cross-nation policy research
12. `bunchloch_research_agent` — local M4 MacBook research
13. `mcp_curriculum_agent` — MCP-server bridge

#### Scenario: 13 agents registered correctly

- **WHEN** `python -c "from sruth.oideachais.agents.adk import AGENT_REGISTRY; print(len(AGENT_REGISTRY))"` is run
- **THEN** the output MUST be `13` (one entry per agent)

### Requirement: Triple LLM client (litellm + llama-swap + unsloth-serve + cloud)

The system SHALL route every LLM call through the existing `litellm` gateway
at `http://localhost:4000` (the canonical 7-tier fallback chain). The litellm
gateway routes to:

1. **`llama-swap`** (`:8080`) — the 14-entry GGUF roster (Qwen3-VL, Gemma-4, etc.)
2. **`unsloth-serve`** (`:8889`) — the Unsloth Studio with `unsloth/Qwen3.8-27B-GGUF`
3. **Cloud** (Gemini 3.5 Flash via Vertex AI) — only the Cloud Run serving layer

The BAML clients are already wired (`baml_src/clients.baml` + `baml_src/clients_llama_swap.baml`).

#### Scenario: Local litellm → llama-swap fallback works

- **WHEN** the unsloth-serve stack is down (CPU-busy)
- **THEN** litellm SHALL fall back to llama-swap
- **AND** the chat SHALL continue to respond within ≤3 seconds

### Requirement: Hybrid memory (Cognee + Firestore)

The system SHALL provide a hybrid memory stack:

- **Cognee** (`:8000`) for production structured knowledge — the 5 typed clusters + a new `oideachais_tutor_memory` cluster
- **LanceDB** (existing) for vector RAG
- **Firestore** (NEW, on Cloud Run) for cross-instance persistence — the Memory Bank primitive (Collaborative Partner track)

#### Scenario: Firestore persists across Cloud Run instances

- **WHEN** user A sends a message in `biiep-agents-v1` instance
- **AND** the next message is routed to `biiep-agents-v2` instance
- **THEN** the v2 instance SHALL see the previous conversation history via Firestore

### Requirement: Adaptive Marking Grader (Taskmaster + Collaborative Partner fit)

The system SHALL provide a `marking_grader_workflow` SequentialAgent that
executes the 4-step grading pipeline:

1. **Extract** — OCR Router extracts the student answer + the marking scheme
2. **Score** — BAML `ScoreMarkingScheme` matches the answer against the scheme
3. **Feedback** — BAML `GenerateFeedback` writes personalised feedback
4. **Store** — Cognee + Firestore persist the grade + feedback

#### Scenario: 4-step workflow grades a student answer in <60 seconds

- **WHEN** the student uploads (1) their PDF answer + (2) the marking scheme PDF
- **THEN** the workflow SHALL extract via OCR Router
- **AND** BAML SHALL score the answer against the marking scheme
- **AND** BAML SHALL generate personalised feedback in plain English
- **AND** the grade + feedback SHALL be stored in Cognee + Firestore
- **AND** the total time SHALL be <60 seconds

### Requirement: Adaptive Tutor Chat (Collaborative Partner fit)

The system SHALL provide a stateful agentic chat (`/tutor` route) that:
1. Knows the 6-jurisdiction syllabus (via the 13-agent fleet)
2. Remembers past sessions (Cognee + Firestore)
3. Adapts difficulty (BAML `AdaptDifficulty` + `ScoreAnswer`)
4. Supports multimodal (PDF + image + diagram via OCR Router)

#### Scenario: Tutor remembers student weaknesses across sessions

- **WHEN** a student correctly solves a "differentiation" problem
- **AND** then incorrectly solves an "integration" problem
- **AND** closes the browser, comes back 24 hours later
- **THEN** the tutor SHALL recall both attempts
- **AND** SHALL ask the student to re-attempt the integration problem
- **AND** SHALL provide a hint from the syllabus

### Requirement: Cross-Jurisdiction Equivalency Generator (Fortified Fleet + Collaborative Partner fit)

The system SHALL provide a `equivalency_generator` ParallelAgent that:
1. Queries the relevant ADK agents in parallel (curriculum_agent + corpus_agent + curriculum_comparison_agent)
2. Produces a structured equivalency table via BAML `GenerateEquivalencyTable`
3. Renders the comparison in the `/equivalency` route
4. Stores the cross-jurisdiction mappings in Cognee for future queries

#### Scenario: 3-way equivalency comparison renders in <5 seconds

- **WHEN** the user picks "Compare LC Mathematics ↔ A-Level Mathematics ↔ HNC Mathematics"
- **THEN** the ParallelAgent SHALL query 3 ADK agents in parallel
- **AND** BAML SHALL generate the structured equivalency table
- **AND** the UI SHALL render the side-by-side comparison with topics + difficulty
- **AND** the response time SHALL be <5 seconds

### Requirement: Curriculum Change Detection Sensor (Taskmaster enabler)

The system SHALL provide a Dagster sensor that:
1. Watches the NCCA + AQA + OCR + Edexcel + SQA + WJEC + CCEA + Isle of Man websites via the existing ChangeDetection.io stack (`bonneagar/stacks/changedetection/`)
2. On a syllabus change event, fires the `marking_grader_workflow` SequentialAgent
3. The agent re-extracts the syllabus + re-embeds via the BIEP v3 5-phase pattern
4. Updates the centralised schema-registry

#### Scenario: Syllabus change fires the workflow

- **WHEN** ChangeDetection.io detects a syllabus change on `ncca.ie`
- **THEN** the Dagster sensor SHALL fire the `marking_grader_workflow`
- **AND** the agent SHALL re-extract the LC syllabus via BAML
- **AND** the new syllabus SHALL be embedded via the BIEP v3 pipeline
- **AND** the response time SHALL be <60 seconds

### Requirement: Pre-existing code disclosure (Rule 6 compliance)

The system SHALL disclose all pre-existing code carried over from the
main cianfhoghlaim monorepo in `docs/DISCLOSURE.md`. The disclosure MUST
enumerate:
- The 13 ADK agents (~5,600 LOC)
- The BAML extraction functions (~2,500 LOC)
- The MODEL_REGISTRY + VISION_MODELS (~1,200 LOC)
- The web scaffold (the source TanStack Start app)
- The litellm + llama-swap + unsloth-serve + ocr-router stacks

#### Scenario: DISCLOSURE.md lists all carried-over code

- **WHEN** the operator inspects `docs/DISCLOSURE.md`
- **THEN** the file MUST list every ADK agent copied from the main repo
- **AND** the file MUST list every BAML file copied
- **AND** the file MUST be referenced from the submission's README.md
