# Spec Delta: agent-memory-systems

## MODIFIED Requirements

### Requirement: LC5 + Gemini consumers of Cognee + Graphiti + FalkorDB

The system SHALL keep the `LC5 + Gemini consumers of Cognee + Graphiti + FalkorDB` requirement inside the main `## Requirements` section of `openspec/specs/agent-memory-systems/spec.md` so OpenSpec strict validation, listing, and archive workflows can see it.

The 3 memory backends (Cognee, Graphiti, and FalkorDB) SHALL be consumed by the LC5-subject pipeline and the Gemini 6-corpus pipeline introduced by the 2026-07-03 pipeline changes.

#### Scenario: Requirement is parsed by strict validation

- **GIVEN** `openspec/specs/agent-memory-systems/spec.md`
- **WHEN** `openspec validate agent-memory-systems --strict` runs
- **THEN** the spec is valid
- **AND** the LC5/Gemini memory-backend requirement is inside the main `## Requirements` section rather than under a delta-style `## ADDED Requirements` section

#### Scenario: Cognee cognify runs over LC5 subjects and Gemini corpora

- **GIVEN** the LC5 + Gemini 6-corpus pipelines
- **WHEN** the L3 memory layer materialises
- **THEN** the system SHALL create Cognee datasets for the LC subjects and Gemini corpora

#### Scenario: Graphiti and FalkorDB initialise the pipeline memory views

- **GIVEN** the same LC5 + Gemini pipelines
- **WHEN** Graphiti and FalkorDB assets materialise
- **THEN** Graphiti streams SHALL be initialised for both pipeline families
- **AND** FalkorDB labels SHALL distinguish the LC5 knowledge graph from the Gemini 6-corpus knowledge graph

### Requirement: Datadog Python observability is a graceful no-op

The system SHALL show actual Python import examples using the v4 `cianfhoghlaim` package root. Legacy `from oideachais...` examples MUST be rewritten when they are code imports rather than documentation shorthand.

#### Scenario: setup_datadog_apm import example uses cianfhoghlaim

- **GIVEN** a Python service that imports the optional Datadog setup helper
- **WHEN** the spec shows the import example
- **THEN** it uses `from cianfhoghlaim.observability.fastapi_middleware import setup_datadog_apm`
- **AND** the helper remains a graceful no-op when `ddtrace` is not installed
