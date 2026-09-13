## ADDED Requirements

### Requirement: 4 stage CocoIndex factories conform R1-R4

The system SHALL provide 4 stage CocoIndex factories at
`cocoindex/biep_parity/` (one per stage: ireland_lc_factory,
ireland_jc_factory, england_alevel_factory, england_gcse_factory),
each conforming to the canonical R1-R4 v1 conformance contract:

- **R1** — Imports from `.._shared._lifespan` (the shared lifespan home)
- **R2** — Uses the canonical `LANCE_DB` + `EMBEDDER` ContextKeys
- **R3** — `coco.App(coco.AppConfig(name=...))` at module scope
- **R4** — At least 1 `@coco.fn(` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

#### Scenario: Every stage factory passes R1-R4

- **WHEN** `mise run cocoindex:conformance` runs
- **THEN** all 4 stage factories MUST pass R1-R4 (no `R2-exempt`
  comments, no `app = coco.App(...)` inside a function body, no
  hand-rolled ContextKey declarations)

### Requirement: BAML → CocoIndex codegen invariant

The system SHALL ensure that every CocoIndex App (one per stage) calls
at least 1 BAML function via `BAMLFunctionTool` (per the
2026-08-26-mega-3a-baml-and-adk-v1 foundation).

#### Scenario: Every CocoIndex App calls BAML

- **WHEN** `mise run lint:cocoindex-baml-coverage` runs
- **THEN** every CocoIndex App MUST import at least 1 BAML function
  via `from baml_client.async_client import b` (or the typed
  `from baml_client.types import ...`)
- **AND** the App's `@coco.fn` MUST call the BAML function as part
  of the data flow

### Requirement: 4 stage CocoIndex factories use shared_lifespan

The system SHALL ensure that the 4 stage CocoIndex factories import
from `.._shared._lifespan import shared_lifespan` (per the canonical
R1 conformance contract).

#### Scenario: Each factory imports shared_lifespan

- **GIVEN** the 4 stage factories: ireland_lc_factory,
  ireland_jc_factory, england_alevel_factory, england_gcse_factory
- **WHEN** the operator runs `grep "from .*_shared._lifespan" cocoindex/biep_parity/*.py`
- **THEN** all 4 factories MUST contain at least 1 such import

### Requirement: 4 stage CocoIndex factories emit `BAAI/bge-m3` embedder

The system SHALL ensure that the 4 stage CocoIndex factories all use
the canonical `BAAI/bge-m3` 1024-d embedder (per the
centralized-model-registry spec).

#### Scenario: No hardcoded embedder strings

- **WHEN** `mise run lint:cocoindex-embedder-drift` runs
- **THEN** no CocoIndex App MUST contain hardcoded embedder strings
  (e.g., `sentence-transformers/all-MiniLM-L6-v2`)
- **AND** every App MUST use the canonical `EMBEDDER` ContextKey from
  `.._shared._lifespan`