## MODIFIED Requirements

### Requirement: ADK and Agno AgentOS MUST run as separate compose services
The oideachais quadrant MUST provide separate Docker Compose
services for the Google ADK agent framework and the Agno
AgentOS runtime. The agent frameworks MUST NOT run
in-process inside the `api` image.

#### Scenario: A new oideachais deployment starts
- **WHEN** a user runs `docker compose -f compose.yaml -f sidecar.yaml up -d`
- **THEN** 5 services MUST be created: `dagster`, `api`, `frontend`,
  `agent_os`, `adk_agents`
- **AND** the `api` service MUST NOT include the
  `google-adk` or `agno` Python packages (the agent runtimes
  are isolated to their own containers)
- **AND** the `api` service MUST be able to invoke the ADK
  agents and the AgentOS via HTTP (on the `cianchoghlaim` or
  `lakehouse` Docker network)

#### Scenario: An agent is added to the ADK framework
- **WHEN** a contributor adds a new agent file to
  `oideachais/agents/adk/`
- **THEN** the new agent is automatically picked up by the
  `adk_agents` compose service on next build
- **AND** the `api` image does NOT need to be rebuilt

#### Scenario: A new agent is added to the Agno framework
- **WHEN** a contributor adds a new agent file to
  `oideachais/agent_os/`
- **THEN** the new agent is automatically picked up by the
  `agent_os` compose service on next build
- **AND** the `api` image does NOT need to be rebuilt

### Requirement: ADK and Agno services MUST have separate Traefik routes
The `infrastructure/stacks/oideachais/pangolin.yaml` MUST define
separate Traefik routers for the ADK and Agno services. The ADK
service MUST be routed at `adk.<stack>.cianfhoghlaim.ie` and the
Agno service at `agent.os.<stack>.cianfhoghlaim.ie`.

#### Scenario: A user accesses the ADK web UI
- **WHEN** a user navigates to `https://adk.oideachais.cianfhoghlaim.ie`
- **THEN** the Traefik router MUST forward the request to the
  `adk_agents` compose service on port 7778
- **AND** the user SHALL be able to interact with the ADK agents

#### Scenario: A user accesses the Agno AgentOS web UI
- **WHEN** a user navigates to `https://agent.os.oideachais.cianfhoghlaim.ie`
- **THEN** the Traefik router MUST forward the request to the
  `agent_os` compose service on port 7777
- **AND** the user SHALL be able to interact with the Agno agents
