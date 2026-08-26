## ADDED Requirements

### Requirement: Langfuse v4 server + SDK deployed before 2026-11-16

The system SHALL migrate from `langfuse/langfuse:3` + Python SDK v3 to `langfuse/langfuse:4` + Python SDK v4 by 2026-11-16. The self-hosted server auto-migrates the v3 schema; no data loss is expected.

#### Scenario: A new trace is created post-migration

- **GIVEN** the platform is on Langfuse v4 + SDK v4
- **WHEN** an agent emits a trace via `@observe` or one of the wrapped helper functions (`llm_chat_with_prompts`, `run_dagster_asset_check`, etc.)
- **THEN** the trace lands in the **Observations** view (v4's default) under the project `cliste`
- **AND** the SDK `langfuse.__version__` prints `4.x`
- **AND** the env-var `LANGFUSE_BASE_URL` (NOT `LANGFUSE_BASEURL`) is set

### Requirement: 47 agent call-sites migrated to v4 method names

The system SHALL audit + replace every v3 SDK call in the 12-agent fleet (`agents/meaisinfhoghlaim/agents/*.py`) + the 5 BIEP notebook helpers (`notebooks/_shared/marimo_patterns.py`) + the 7 BAML-side observability wrappers.

#### Scenario: A call-site uses a deprecated v3 method

- **GIVEN** a Python file in `agents/meaisinfhoghlaim/agents/`
- **WHEN** `bunx ccc:search "start_as_current_span\|start_generation\|update_current_trace\|DatasetItemClient"` flags matches
- **THEN** each match is replaced with the v4 equivalent (`span(...)`, `propagate_attributes(...)`, `set_current_trace_io(...)`, `dataset.run_experiment(...)`, etc.)

### Requirement: Pydantic v2 only

The system SHALL drop Pydantic v1 imports (from `langfuse.pydantic_compat`) and use Pydantic v2 directly throughout.

#### Scenario: A agent call site imports langfuse.pydantic_compat

- **GIVEN** a Python file in `agents/meaisinfhoghlaim/agents/` or `notebooks/_shared/`
- **WHEN** `bunx ccc:search "from langfuse.pydantic_compat"` flags matches
- **THEN** each match is replaced with the Pydantic v2 native imports (no `pydantic_compat`)
- **AND** the file MUST `import pydantic` directly
