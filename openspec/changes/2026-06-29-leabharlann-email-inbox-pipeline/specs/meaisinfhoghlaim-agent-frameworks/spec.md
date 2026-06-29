# `meaisinfhoghlaim-agent-frameworks` capability spec — leabharlann-email-inbox-pipeline delta

The `meaisinfhoghlaim-agent-frameworks` capability spec governs
the 12 specialised agents in the meaisínfhoghlaim fleet (Root,
Curriculum, Translation, Corpus, Geospatial, Statistics,
Research, Education Research, Bunchloch Research, Curriculum
Comparison, AGUI Curriculum, MCP Curriculum) at
`cianfhoghlaim/agents/meaisinfhoghlaim/`.

This delta adds a 10th agent to the oideachais-stack Google ADK
sub-tree (`email_triage`) at
`cianfhoghlaim/agents/adk/email_triage_agent.py`. The
oideachais ADK agent count grows from 9 → 10. The 12-agent
meaisínfhoghlaim fleet is unchanged.

## ADDED Requirements

### Requirement: Google ADK `email_triage` agent

The system SHALL provide a Google ADK `LlmAgent` named
`email_triage` on the oideachais stack (port 7778) with 4
tools: `classify_email_thread`, `summarise_thread`,
`link_thread_to_research`, `find_loose_threads`.

#### Scenario: Agent reachable from ADK REST

- **GIVEN** the ADK container is up on port 7778
- **WHEN** a client sends
  `POST /agents/email_triage/invocations` with
  `{"message": "summarise thread dkit_ie/thread-123"}`
- **THEN** the agent invokes
  `summarise_thread(thread_id="dkit_ie/thread-123")`
- **AND** returns a ≤ 500-char summary

#### Scenario: `classify_email_thread` tool

- **GIVEN** a thread with 3 messages
- **WHEN** the agent calls
  `classify_email_thread(thread_id="dkit_ie/thread-123")`
- **THEN** the tool invokes BAML `ClassifyEmail` on the
  thread
- **AND** returns an `EmailClassificationResult` with
  `class_label`, `urgency_score`, `summary_5_words`

#### Scenario: `find_loose_threads` tool

- **GIVEN** 100 threads across 4 accounts
- **WHEN** the agent calls
  `find_loose_threads(account="dkit_ie", days_idle_min=7)`
- **THEN** the tool queries DuckLake for threads where the
  user has not replied in ≥ 7 days
- **AND** sorts the results by `urgency_score` DESC
- **AND** returns a `list[ThreadSummary]`

#### Scenario: Citation callbacks inject LanceDB neighbours

- **GIVEN** the `link_thread_to_research` tool is called
- **WHEN** the tool returns 3 `ResearchLink` rows
- **THEN** the `citation_callbacks.py` callback injects the
  top-3 LanceDB vector-search citations into the response
- **AND** the response includes the PDF title + a clickable
  URL

#### Scenario: Langfuse auto-traces every tool call

- **GIVEN** the oideachais ADK container has `LANGFUSE_*`
  env vars set
- **WHEN** the `email_triage` agent is invoked
- **THEN** every tool call (`classify_email_thread`,
  `summarise_thread`, `link_thread_to_research`,
  `find_loose_threads`) is traced to Langfuse with
  `thread_id` + `account` + `cost` + `latency` metadata

## MODIFIED Requirements

*(None — the change only ADDS the `email_triage` ADK agent;
the 9 existing ADK agents (curriculum_agent, translation_agent,
statistics_agent, corpus_agent, curriculum_comparison_agent,
bunchloch_research_agent, education_research_agent,
research_agent, enhanced_orchestrator) are unchanged. The
12-agent meaisínfhoghlaim fleet is unchanged.)*

## REMOVED Requirements

*(None.)*
