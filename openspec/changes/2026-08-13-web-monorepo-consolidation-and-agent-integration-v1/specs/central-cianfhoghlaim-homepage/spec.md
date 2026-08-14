# central-cianfhoghlaim-homepage Specification

## Purpose

Formalize the central Cianfhoghlaim homepage at
`web/apps/cianfhoghlaim/` — the canonical entry point that
visualizes ALL data engineering pipeline outputs and provides
an agentic chat wired to DuckLake + LanceDB + Cognee + the
60 subject agents.

The system is added by the
2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
openspec change (Phase T).

## ADDED Requirements

### Requirement: web/apps/cianfhoghlaim/ MUST be the central homepage

The system MUST provide a dedicated app at
`web/apps/cianfhoghlaim/` that serves the central homepage at
`/`. The app MUST be:

- The canonical entry point for the Cianfhoghlaim brand
- A separate app from `apps/oideachais/` (which serves
  per-subject content pages)
- Wired to the same TanStack AI + Convex + AG-UI stack as the
  other apps
- Backed by its own Convex deployment (or sharing the umbrella
  deployment with `oideachais-dashboard/`)

The app MUST visualize:

- The 5 education stages
- The 60 subjects (14 LC + 8 JC + 9 GCSE + 15+ A-Level)
- The 4 resource types per subject (syllabus / papers /
  marking / other resources)
- The pipeline health (Dagster + BAML + CocoIndex + DLT)
- The knowledge graph (Cognee 7 clusters)
- The recent activity (last 24h)
- The 60 subject agents (Phase U)

#### Scenario: A user visits the central homepage

- **WHEN** a user navigates to `/`
- **THEN** the page MUST show the agentic chat at the center
- **AND** the page MUST show the 60 subject cards
- **AND** the page MUST show the pipeline health grid
- **AND** the page MUST show the knowledge graph panel

### Requirement: The homepage SHALL provide an agentic chat with subject-aware routing

The homepage SHALL provide an agentic chat at the center that:

1. Detects the subject from the user's query via LLM
   extraction (using `MODEL_REGISTRY` entry `minimax-m3`)
2. Routes the query to the per-subject agent (Phase U) for the
   detected subject + stage
3. Queries DuckLake for the canonical lakehouse data
4. Searches LanceDB for semantic vector matches
5. Queries Cognee for knowledge graph entities
6. Triggers BAML extractions on-demand
7. Renders results via CopilotKit generative UI

#### Scenario: A user asks the chat to "show me LC Maths 2024 paper"

- **WHEN** the user submits the query "show me LC Maths 2024 paper"
- **THEN** the subject detector MUST extract `{stage: "lc", subject: "mathematics", confidence: 0.98}`
- **AND** the chat MUST dispatch to `mathematics_lc_agent`
- **AND** the agent MUST query DuckLake for
  `ireland.lc.mathematics.papers.2024`
- **AND** MUST render the result via a CopilotKit
  `useRenderTool` PDF preview card
- **AND** MUST stream the AG-UI `TOOL_CALL_*` events for live
  progress

#### Scenario: A user asks the chat to "compare LC vs GCSE Maths curricula"

- **WHEN** the user submits "compare LC vs GCSE Maths curricula"
- **THEN** the subject detector MUST extract BOTH subjects
- **AND** the chat MUST dispatch to BOTH
  `mathematics_lc_agent` AND `mathematics_gcse_agent`
- **AND** MUST query DuckLake for both stages
- **AND** MUST render the comparison via a CopilotKit
  `useComponent` table

#### Scenario: A user asks the chat to "extract the syllabus from this PDF"

- **WHEN** the user uploads a PDF and asks to extract the syllabus
- **THEN** the chat MUST dispatch to `baml_extract()` (TanStack
  AI server function)
- **AND** MUST call the per-subject BAML function (Phase P)
- **AND** MUST render the extracted syllabus via a CopilotKit
  `useRenderTool` typed card list

### Requirement: The chat MUST use state-of-the-art TanStack + Convex + AG-UI

The chat MUST use:

- TanStack Start RC (full-document SSR + streaming + server
  functions)
- TanStack Router (file-based routing + type-safe params)
- TanStack Query (server state + Convex integration)
- TanStack AI GA (type-safe LLM chat + AG-UI compliance per
  https://tanstack.com/blog/ag-ui-compliance)
- Convex (real-time queries + schema-first + vector search)
- Better Auth + ConvexProvider per
  https://labs.convex.dev/better-auth/framework-guides/tanstack-start
- CopilotKit v2 + AG-UI per
  https://docs.copilotkit.ai/concepts/generative-ui-overview
- A2UI per https://docs.copilotkit.ai/learn/generative-ui/specs/a2ui

#### Scenario: The chat is built with the right stack

- **WHEN** the user opens the homepage
- **THEN** the chat MUST be rendered with TanStack AI GA
- **AND** the chat MUST use AG-UI protocol over SSE
- **AND** the chat MUST integrate with Convex realtime
