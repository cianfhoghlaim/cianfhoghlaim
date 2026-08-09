## ADDED Requirements

### Requirement: 3 Convex Tables for Familiars

The system SHALL provide 3 new Convex tables in
`web/apps/cianfhoghlaim-mmo/convex/`:
`familiars.ts`, `anam_particles.ts`, `familiar_evolution_log.ts`.

#### Scenario: Convex schema deploys
- **WHEN** the user invokes `mise run convex:dev`
- **THEN** the schema SHALL deploy with all 3 new tables

### Requirement: Celtic-Themed Evolution Stages (Sétanta → Cúchulainn)

The system SHALL define 6 evolution stages mapped to the Sétanta →
Cúchulainn myth cycle.

#### Scenario: Evolution from Level 0 to Level 1
- **WHEN** a Familiar has 10+ anam AND has mastered 1 LC Geography core unit
- **THEN** the user SHALL be able to evolve the Familiar from Level 0 to Level 1

#### Scenario: Evolution blocked below threshold
- **WHEN** a Familiar has <10 anam
- **THEN** the system SHALL reject the evolution request

### Requirement: Anam Progression Agent

The system SHALL provide `agents/meaisinfhoghlaim/educational/anam_progression_agent.py`
as an ADK agent with 6 tools. The agent SHALL be registered in `AGENT_REGISTRY`
with `framework="adk"`, `litellm_routing_key="anam"`.

#### Scenario: Agent mints a Sétanta Familiar
- **WHEN** the user invokes `anam_progression_agent` with "Mint me a new Familiar"
- **THEN** the agent creates a new `familiars.ts` record with `archetype="setanta"`, `evolution_level=0`

### Requirement: Bria Fibo Enabled

The system SHALL have `local/image/fibo: true` in `deployment-choice.yaml`
after the Familiar Dynamic NFT System change is archived.

#### Scenario: Fibo deployment check
- **WHEN** the user invokes `mise run cic:stack-doctor`
- **THEN** the `fibo-server` stack SHALL pass the 6-file GOLD_STANDARD validation

### Requirement: fibo-server Docker Stack

The system SHALL provide `bonneagar/stacks/fibo-server/` as a 6-file
GOLD_STANDARD Docker Compose stack.

#### Scenario: fibo-server stack passes cic:stack-doctor
- **WHEN** the user invokes `mise run cic:stack-doctor --strict`
- **THEN** the `fibo-server` stack SHALL pass

### Requirement: x402-Gated Evolve Endpoint

The system SHALL provide `web/apps/cianfhoghlaim-mmo/src/routes/api/familiars/evolve.tsx`
as an x402-gated HTTP endpoint.

#### Scenario: Endpoint returns 402 without credential
- **WHEN** the user invokes the endpoint without credentials
- **THEN** the endpoint SHALL return HTTP 402 with the x402 challenge

#### Scenario: Endpoint evolves with valid credential
- **WHEN** the user invokes the endpoint with valid credentials
- **THEN** the endpoint SHALL return the updated Familiar JSON

### Requirement: Marimo Familiar Generator

The system SHALL provide `notebooks/38_familiar_generator.py` as a
marimo + Altair visualisation with 6 tabs.

#### Scenario: Generator renders
- **WHEN** the user invokes `mise run notebook:familiar`
- **THEN** the generator SHALL render with 6 tabs