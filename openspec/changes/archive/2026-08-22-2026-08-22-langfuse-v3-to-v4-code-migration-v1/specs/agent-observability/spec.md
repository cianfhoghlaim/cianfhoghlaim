## ADDED Requirements

### Requirement: Langfuse v4 implementation — 47-call-site migration contract

The system SHALL implement the v4 SDK migration contract (per the archived `2026-08-21-2026-08-21-langfuse-v3-to-v4-migration-v1` proposal's spec deltas) across all 12 agent fleet modules in `agents/meaisinfhoghlaim/agents/*.py`. The migration MUST:

- Replace every `with langfuse.start_as_current_span(name=...) as span:` with `with langfuse.span(name=...) as span:`.
- Replace every `with langfuse.start_as_current_generation(name=...) as gen:` with `with langfuse.generation(name=...) as gen:`.
- Decompose every `langfuse.update_current_trace(metadata=..., tags=..., session_id=...)` call into the v4 trio: `propagate_attributes(...)`, `set_current_trace_io(input=..., output=...)`, `set_current_trace_as_public()`.
- Replace every `from langfuse.api.resources.dataset_items import DatasetItemClient` with the v4 experiment-runner pattern: `from langfuse import get_dataset; get_dataset(name).run_experiment(run, dataset=...)`.
- Drop every `from langfuse.pydantic_compat import v1` import; use Pydantic v2 native (or `pydantic>=2`).

#### Scenario: A new agent uses the v4 SDK

- **GIVEN** the platform is on Langfuse v4 + SDK v4
- **WHEN** the operator runs `python3 -c "import langfuse; print(langfuse.__version__)"` inside `.venv`
- **THEN** the output MUST start with `4.`
- **AND** `from langfuse.pydantic_compat import v1` MUST NOT be referenced anywhere in the repo (verified via `grep -rn "from langfuse.pydantic_compat" agents/ meaisinfhoghlaim/ notebooks/`)
- **AND** `start_as_current_span` + `start_as_current_generation` + `update_current_trace` + `DatasetItemClient` MUST NOT be referenced anywhere in the repo (verified via `grep -rnE "start_as_current_(span|generation)|update_current_trace|DatasetItemClient" agents/ meaisinfhoghlaim/ notebooks/`)

#### Scenario: The env-var rename is complete

- **GIVEN** the platform is on Langfuse v4
- **WHEN** the operator runs `grep -rn "LANGFUSE_BASEURL" .env .infisical.env bonneagar/stacks/*/secrets.env bonneagar/stacks/*/compose.yaml 2>/dev/null`
- **THEN** the output MUST be empty (zero matches) — the legacy `LANGFUSE_BASEURL` is fully replaced by `LANGFUSE_BASE_URL`

### Requirement: Langfuse v4 server image bump — `langfuse/langfuse:4.x`

The system SHALL run `langfuse/langfuse:4.x` (any 4.0+ stable patch) in the self-hosted `langfuse-web` container, replacing the legacy `langfuse/langfuse:3`. The v3 → v4 schema migration is automatic on first boot of the v4 server.

#### Scenario: The v4 server is up

- **GIVEN** the platform is on Langfuse v4
- **WHEN** `docker inspect langfuse-web --format '{{.Config.Image}}'` runs
- **THEN** the image tag MUST start with `langfuse/langfuse:4`
- **AND** `curl -s http://localhost:3001/api/public/health` returns 200 OK

#### Scenario: A new trace is recorded post-migration

- **GIVEN** the platform is on Langfuse v4
- **WHEN** any `@observe`-decorated BAML function in `agents/meaisinfhoghlaim/agents/*.py` runs
- **THEN** the trace MUST land in the v4 **Observations** view (NOT v3's Traces view)
- **AND** the trace MUST be queryable via the v4 `Dataset.run_experiment()` API
