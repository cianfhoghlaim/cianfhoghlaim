## ADDED Requirements

### Requirement: Google ADK Skill Currency

The system SHALL keep the Google ADK skill aligned with the installed
library version and document the agent fleet architecture
(12 agent files under `agents/meaisinfhoghlaim/` across 4 clusters).

#### Scenario: Google ADK library version is documented

- **WHEN** any developer runs `uv run pytest tests/google_adk/`
- **THEN** `uv pip show google-adk` reports version ≥ 1.0
- **AND** `.agents/skills/google-adk/SKILL.md` documents the same major version

#### Scenario: Agent clusters exist

- **WHEN** any developer runs `uv run pytest tests/google_adk/`
- **THEN** `agents/meaisinfhoghlaim/` contains 4 sub-clusters:
  - `educational/`
  - `firecrawl_mcp/`
  - `media_intel/`
- **AND** the cluster directories each contain at least one agent file

#### Scenario: Agent modules import with graceful BAML degradation

- **WHEN** any developer runs `uv run pytest tests/google_adk/`
- **THEN** the per-agent modules (e.g. `celtic_grammar_agent`,
  `celtic_morphology_agent`, `firecrawl_mcp.client`) import cleanly
- **AND** missing optional deps (`baml_client`, `routing`) are
  gracefully skipped, not raised as ImportError

#### Scenario: BAML fallback pattern is canonical

- **WHEN** auditing any agent module under `agents/meaisinfhoghlaim/`
- **THEN** the module declares a `try: from baml_client import b`
  import block
- **AND** declares a fallback path (`_BAML_AVAILABLE = False` or
  equivalent) when the import fails
