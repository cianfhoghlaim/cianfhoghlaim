# Spec delta: `centralized-schema-registry`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
The 4 ADDED Requirements were already added to the canonical
`centralized-schema-registry` spec by the parallel-session work. This
delta adds ONE new requirement: the auto-derive hook.

## ADDED Requirements

### Requirement: Auto-derive Pydantic from BAML via baml_client.b

The system SHALL provide an auto-derive hook that emits the Pydantic
v2 models from the canonical BAML `class` declarations at
`baml_src/`. The hook SHALL be invoked via `mise run baml:derive-pydantic`
and SHALL produce the Pydantic models in `baml_client/baml_client/basalt/`.

#### Scenario: Pydantic models are auto-derived from BAML

- **GIVEN** a new BAML `class Foo { ... }` is added to `baml_src/`
- **WHEN** the operator runs `mise run baml:derive-pydantic`
- **THEN** the corresponding Pydantic `class Foo(BaseModel): ...` SHALL
  appear in `baml_client/baml_client/basalt/`
- **AND** the Pydantic model SHALL have the same field names + types
  as the BAML class
