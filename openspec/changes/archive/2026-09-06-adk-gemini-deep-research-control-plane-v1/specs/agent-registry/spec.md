## MODIFIED Requirements

### Requirement: root_agent framework classification
The `agents/agent_registry.py:281` `AGENT_REGISTRY` SHALL declare
`root_agent.framework = AgentFramework.ADK` (replacing the prior
`AgentFramework.CUSTOM` value). The `root_agent` SHALL be backed by an
ADK `SequentialAgent` named `cian_root` that classifies the incoming
`Query` by domain and routes to one of the 8 ADK agents in the
registry. The 4 shared dispatchers in
`agents/_workflow_handlers.py:299` SHALL invoke the new `cian_root`
runner instead of returning stub data.

#### Scenario: Framework classification flip
- **WHEN** `openspec list --specs | grep agent-registry` is run
- **THEN** `agent-registry` MUST list `root_agent.framework = AgentFramework.ADK` in its `MODIFIED Requirements` block

#### Scenario: Dispatcher invokes cian_root
- **WHEN** `dispatch_deep_research(ResearchQuery(domain="research", ...))` is called
- **THEN** the dispatcher MUST invoke `cian_root.run_async(query)`
- **AND** MUST emit AG-UI events
- **AND** MUST NOT return stub data
