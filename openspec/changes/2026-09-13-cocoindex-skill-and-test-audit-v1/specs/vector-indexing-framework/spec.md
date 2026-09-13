## ADDED Requirements

### Requirement: CocoIndex Skill Currency

The system SHALL keep the CocoIndex skill version aligned with the
installed library and document the v1 App pattern compliance of all
flows.

#### Scenario: CocoIndex library version is documented

- **WHEN** any developer runs `uv run pytest tests/cocoindex/`
- **THEN** `uv pip show cocoindex` reports version ≥ 1.0.0
- **AND** `.agents/skills/cocoindex/SKILL.md` documents the same major version

#### Scenario: Flow inventory is stable

- **WHEN** any developer runs `uv run pytest tests/cocoindex/`
- **THEN** the `cocoindex_flows/` directory contains ≥ 30 `*_embedding.py` files
- **AND** the 6 Ireland LC flows + shared scaffold import without errors

#### Scenario: Flows use the v1 App pattern

- **WHEN** auditing any `_embedding.py` flow
- **THEN** it uses `coco.App(coco.AppConfig(...))` at module scope (not the deprecated
  v0 `@cocoindex.flow_def(...)` pattern)

#### Scenario: BAML fallback is in place

- **WHEN** `baml_client.baml_client` is unavailable (per Plan 2)
- **THEN** the Ireland LC flows have a `python_baml_fallback_extract` path
- **AND** the shared scaffold documents the fallback behavior
