# Spec Delta: no-dead-croilar-shared-subdirs

## ADDED Requirements

### Requirement: No dead `_shared/{observability,agents,mcp,embeddings}` subdirs

The system SHALL NOT include `sruth/croilar/_shared/observability/`,
`sruth/croilar/_shared/agents/`, `sruth/croilar/_shared/mcp/`,
or `sruth/croilar/_shared/embeddings/`. These 4 subdirs were
written for the pre-Croílár Aleyum agent framework but were
never wired into the new Stream-registry-driven architecture
(round 11 phase 0 / commit `6186d70da`). The canonical surfaces
for all 4 modules already exist in other quadrants:
`observability/` → `sruth/oideachais/observability/`;
`agents/` → `sruth/meaisinfhoghlaim/agents/`;
`mcp/` → `sruth/oideachais/mcp/filesystem/`;
`embeddings/` → `sruth/codeolas/core/embeddings.py`.

#### Scenario: Only `_shared/{streams,config,database}` remain

- **WHEN** `ls sruth/croilar/_shared/` is run
- **THEN** the directory SHALL contain only `__init__.py` + `streams.py` + `config/` + `database/`
- **AND** the directory SHALL NOT contain `observability/`, `agents/`, `mcp/`, or `embeddings/`

#### Scenario: `_shared/__init__.py` has no commented-out sibling imports

- **WHEN** `sruth/croilar/_shared/__init__.py` is read
- **THEN** the file SHALL NOT contain `# from .mcp import MCPGateway` or
- **AND** the file SHALL NOT contain `# from .agents import AgentRouter, select_framework` or
- **AND** the file SHALL NOT contain `# from .observability import AleyumTracer`

#### Scenario: Production callers of the kept modules still work

- **WHEN** `dagster_assets/dlt_assets.py` runs `from _shared.streams import Stream, StreamSource, ...`
- **THEN** the canonical Stream registry SHALL remain importable from `sruth.croilar._shared.streams`
- **AND** the production `dagster_assets.dlt_assets` module SHALL remain importable
- **AND** `tests/test_database.py` SHALL remain importable from `sruth.croilar._shared.database`

#### Scenario: No fallback shims

- **WHEN** the round 11 change is committed
- **THEN** there SHALL be no `try/except ImportError` fallback, no `__getattr__` lazy import, no deprecation warning
- **AND** the deleted subdirs SHALL be removed outright (no `.bak`, no `.deprecated`)

#### Scenario: `_shared/__init__.py` docstring updated

- **WHEN** the round 11 change is committed
- **THEN** the docstring SHALL NOT mention "embeddings, MCP gateway, agent orchestration, and observability" (the deleted subdirs)
- **AND** the docstring SHALL continue to mention the kept subdirs ("path resolution, configuration, database access")