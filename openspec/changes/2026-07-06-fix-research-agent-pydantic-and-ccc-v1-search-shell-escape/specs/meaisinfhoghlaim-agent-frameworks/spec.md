# Spec Delta — `meaisinfhoghlaim-agent-frameworks`

## ADDED Requirements

### Requirement: ADK package init SHALL resolve cleanly

The `from cianfhoghlaim.agents.adk import <name>` path SHALL resolve all `LlmAgent` instances declared in `__all__` without raising `ImportError` or `pydantic_core.ValidationError`.

#### Scenario: research_agent imports cleanly under google-genai v2.13+

- **WHEN** the user runs `from cianfhoghlaim.agents.adk.research_agent import ResearchFeedback, SearchQuery`
- **AND** the installed `google-genai` version is `>=2.13`
- **THEN** the import SHALL NOT raise `pydantic_core._pydantic_core.ValidationError` on `ThinkingConfig`
- **AND** the import SHALL NOT raise `ImportError` for any name declared in `research_agent.__all__`

#### Scenario: package init resolves all exports

- **WHEN** the user runs `from cianfhoghlaim.agents.adk import dev_env_demo_agent`
- **THEN** `dev_env_demo_agent` SHALL be a `google.adk.agents.LlmAgent` instance
- **AND** it SHALL have all 8 dev-env tools wired
- **AND** it SHALL NOT have raised any error during import

#### Scenario: stale name imports are removed

- **WHEN** the user inspects `cianfhoghlaim/agents/adk/__init__.py:118-127`
- **THEN** the imports from `research_agent` SHALL only contain names declared in `research_agent.__all__`
- **AND** stale names (`ResearchReport`, `compose_report`, `conduct_research`, `evaluate_research`, `execute_research`, `generate_search_queries`) SHALL be absent