## ADDED Requirements

### Requirement: 2 New Source Groups (CISP + Megalithic Portal)

The system SHALL extend the celtic-language-pipeline from 7 source groups
to 9 source groups by adding CISP and Megalithic Portal.

#### Scenario: Source group count is 9
- **WHEN** the user runs `openspec list --specs | grep celtic-language-pipeline`
- **THEN** the spec body SHALL list 9 source groups

### Requirement: Ogham Stone Agent in Agent Fleet

The system SHALL register the Ogham Stone Agent under
`meaisinfhoghlaim-agent-frameworks` with `litellm_routing_key="ogham"`.

#### Scenario: Ogham agent is in the agent registry
- **WHEN** the user runs `python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; print('ogham_stone_agent' in AGENT_REGISTRY)"`
- **THEN** the script SHALL print `True`