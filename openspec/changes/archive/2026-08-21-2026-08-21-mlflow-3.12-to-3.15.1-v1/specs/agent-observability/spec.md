## ADDED Requirements

### Requirement: mlflow pin (>=3.15.1,<4.0.0) — Priority 1 bump per the 2026-08-21 audit

The system SHALL pin `mlflow>=3.15.1,<4.0.0` per the 2026-08-21 upstream-version alignment audit. The 3.15.1 bump supersedes 3.12.0 (which was the floor) and includes:

- **3.13.0** — RBAC overhaul (per-resource permission APIs removed; unified `mlflow.set_workspace_permission` model); MLServer removed (`mlflow models serve` no longer bundles MLServer); `judge.align()` optimizer default changed from GEPA → MemAlign; **pytest integration** added (`@mlflow.test` decorator).
- **3.15.1** — Centralized MCP Registry; MLflow Assistant; shareable table views; proxy-less artifact transfers; multimodal LLM judges; `MLFLOW_ALLOW_FILE_STORE=true` env var is **required** for any legacy `mlruns/` SQLite fallback.

#### Scenario: A new BAML function evaluates a model with mlflow

- **GIVEN** the platform is on mlflow 3.15.1 + the operator added `MLFLOW_ALLOW_FILE_STORE=true` to `secrets.env`
- **WHEN** a BAML function calls `mlflow.log_metric(...)` or `mlflow.evaluate(...)`
- **THEN** the call MUST land in the MLflow UI under the experiment `cliste`
- **AND** the legacy `mlruns/` SQLite fallback MUST still work (since the test-suite jobs use it)

#### Scenario: A legacy judge.align() call uses the new default

- **GIVEN** the platform is on mlflow 3.15.1
- **WHEN** a BAML function calls `judge.align(...)` without specifying `optimizer=...`
- **THEN** the default `MemAlign` optimizer is used (NOT GEPA)
- **AND** the bump audits the 5 callsites to either pin `optimizer='gepa'` (legacy compat) or accept the new default

#### Scenario: The MCP Registry endpoint is exposed via Pangolin

- **GIVEN** `pangolin.yaml` has the `/api/mcp/registry` path
- **WHEN** `curl -s https://mlflow.cianfhoghlaim.ie/api/mcp/registry` is called
- **THEN** the response MUST be 200 OK with the MCP registry payload

### Requirement: mlflow 3.13+ MLServer removal — the agent deployment surface MUST NOT regress

The system MUST verify that no agent deployment depends on `mlflow models serve` + MLServer (the latter removed in 3.13). The 12-agent fleet uses the LiteLLM proxy for model serving; MLServer was never wired.

#### Scenario: An agent deployment reaches mlflow

- **WHEN** the 12-agent fleet runs an evaluation
- **THEN** the model is served via LiteLLM (NOT MLServer)
- **AND** mlflow 3.15.1 is used for tracking + evaluation ONLY (not serving)
