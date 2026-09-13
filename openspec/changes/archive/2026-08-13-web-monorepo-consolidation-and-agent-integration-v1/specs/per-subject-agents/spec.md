# per-subject-agents Specification

## Purpose

Formalize the 60 per-subject agents (one per subject × stage
across LC + JC + GCSE + A-Level) that are fully integrated with
the BIEP data platform (DuckLake + CocoIndex + BAML) and bound
to the per-subject web routes.

The system is added by the
2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
openspec change (Phase U).

## ADDED Requirements

### Requirement: every subject MUST have a dedicated agent

The system MUST provide, for every subject × stage combination in
the per-subject coverage matrix (60 subjects total), a dedicated
`SubjectAgentBase` subclass at
`agents/adk/subjects/<stage>/<subject>_agent.py` that is fully
integrated with the BIEP data platform:

- 8 BAML extraction functions (per subject × stage)
- 5 DuckLake queries (per subject × stage)
- 2 LanceDB semantic searches (per subject × stage)
- 3 Convex actions (per subject × stage)
- 8-13 CopilotKit actions (per subject × stage)
- 1 web_integration binding to the per-subject route

Each agent MUST be wired through
`agents/agent_registry.py:AGENT_REGISTRY` with a
`web_integration` field naming:

- `app: "cianfhoghlaim"` (the central homepage app)
- `route: "/<stage>/<subject>"` (the per-subject route)
- `subject_agent_cards: True` (surfaces in the homepage grid)
- `homepage_chat_routing: True` (dispatchable from the chat)

#### Scenario: The homepage chat dispatches to a per-subject agent

- **WHEN** the homepage chat receives a query about LC Maths 2024
- **THEN** the subject detector MUST extract
  `{stage: "lc", subject: "mathematics", confidence: >0.9}`
- **AND** the agent router MUST look up `mathematics_lc_agent`
  in `agents/agent_registry.py:AGENT_REGISTRY`
- **AND** MUST verify `web_integration.homepage_chat_routing == True`
- **AND** MUST dispatch the query to the agent via AG-UI streaming
- **AND** MUST render the agent's response via the per-subject
  CopilotKit actions

#### Scenario: A new subject is added to BIEP

- **WHEN** a developer adds a new subject (e.g. LC Music OL)
- **THEN** all 8 BAML functions MUST be added at
  `baml_src/british_isles/ireland/education/lc_extraction/music.baml`
- **AND** the per-subject agent MUST be added at
  `agents/adk/subjects/lc/music_agent.py`
- **AND** the per-subject config MUST be added at
  `agents/adk/subjects/config/lc.json`
- **AND** the agent MUST be added to
  `agents/agent_registry.py:AGENT_REGISTRY` with the correct
  `web_integration` field
- **AND** the homepage grid MUST auto-include the new agent card
- **AND** the per-subject CopilotKit actions MUST live at
  `web/hono-api/src/routes/copilotkit/lc/music.ts`

### Requirement: every subject agent MUST be fully integrated with DuckLake + CocoIndex + BAML

Each per-subject agent MUST inherit from `SubjectAgentBase` and
provide:

1. **Per-subject BAML tools** — 8 BAML extraction functions
2. **Per-subject DuckLake queries** — 5 queries for syllabus,
   papers, marking schemes, topics, cross-jurisdictional
   equivalences
3. **Per-subject CocoIndex semantic searches** — 2 vector
   searches (BGE-M3 embeddings)
4. **Per-subject Convex actions** — 3 actions for threads,
   annotations, progress
5. **Per-subject CopilotKit actions** — 8-13 actions
6. **Per-subject AG-UI event types** — typed wrappers around the
   17 AG-UI events
7. **Per-subject marimo notebook** — 1 notebook per subject
8. **Per-subject CocoIndex flow** — 1 CocoIndex flow
9. **Per-subject web route** — 1 route per subject
10. **Per-subject BAML extraction client** — the
    `LocalVision` / `ExtractEnStrong` / `MinimaxM3Client` pattern

#### Scenario: A per-subject agent is queried

- **WHEN** the homepage chat routes a query to
  `mathematics_lc_agent`
- **THEN** the agent MUST query DuckLake for the syllabus +
  papers + marking schemes
- **AND** MUST search LanceDB for semantic matches
- **AND** MUST trigger BAML extraction on-demand
- **AND** MUST return the result via the per-subject CopilotKit
  actions
