## ADDED Requirements

### Requirement: CEFR Learner Analytics Capability

The system SHALL provide a CEFR Learner Analytics capability exposing:
4 CEFR metrics (Lexical Frequency Profile, Mutation Density Index,
Acquisition Velocity, Error Hotspot Identification), 5 BAML extraction
functions, 1 CocoIndex v1 embedding App, 1 Dagster asset module, 1
marimo dashboard, 1 educational agent.

#### Scenario: Lexical Frequency Profile runs
- **WHEN** the user invokes `compute_lexical_frequency_profile(corpus_id="corpas_cc")`
- **THEN** the function returns a profile showing the distribution of vocabulary levels

#### Scenario: Mutation Density Index runs
- **WHEN** the user invokes `compute_mutation_density_index(corpus_id="corpas_cc")`
- **THEN** the function returns the mutation density per 1000 tokens

### Requirement: CEFR Learner Analytics Agent

The system SHALL provide `agents/meaisinfhoghlaim/educational/cefr_learner_analytics_agent.py`
as an ADK agent with 6 tools. The agent SHALL be registered in
`AGENT_REGISTRY` with `litellm_routing_key="cefr"`.

#### Scenario: Agent computes CEFR readiness score
- **WHEN** the user invokes `cefr_learner_analytics_agent` with "Compute CEFR readiness for learner L-12345"
- **THEN** the agent returns a CEFR level prediction

### Requirement: Marimo Dashboard for CEFR

The system SHALL provide `notebooks/36_cefr_readiness_dashboard.py` with
5 tabs.

#### Scenario: Dashboard renders
- **WHEN** the user invokes `mise run notebook:cefr`
- **THEN** the dashboard SHALL render with 5 tabs

### Requirement: OntoLex-Lemon Edge Types in Cognee

The system SHALL register 3 OntoLex-Lemon edge types in the Cognee cognify pipeline.

#### Scenario: Cognify edges exist
- **WHEN** the user queries `cognee.edges("translationOf")`
- **THEN** the query returns at least 100 Celtic translation pairs