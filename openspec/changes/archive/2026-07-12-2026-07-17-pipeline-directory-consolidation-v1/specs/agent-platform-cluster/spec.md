# agent-platform-cluster

## ADDED Requirements

### Requirement: Agent scripts and registries SHALL use full-name jurisdiction paths

SHALL import from the full-name paths
(`baml_src.british_isles.<full>`, `dlt.british_isles.<full>`,
`dlt.european_nations.<full>`, etc.). Agent-fleet scripts that
import jurisdiction-specific BAML or DLT modules SHALL be
available via the full-name paths. The legacy ISO-3 import paths
SHALL remain available via deprecation shims for at least one
release cycle.

#### Scenario: An agent imports from the new path

- **GIVEN** an agent `agents/meaisinfhoghlaim/curriculum/curriculum_agent.py`
  that previously did `from baml_src.european_nations.deu import …`
- **WHEN** the directory consolidation change is materialised
- **THEN** the import SHALL be `from baml_src.european_nations.germany import …`
- **AND** the old import SHALL still resolve via a deprecation shim
  at `baml_src/european_nations/deu/`