# 2026-08-21-mlflow-3.12-to-3.15.1-v1

## Summary

Bump mlflow from `>=3.12.0` to `>=3.15.1,<4.0.0`. Priority 1 in the upstream-version audit. The umbrella change `2026-08-21-upstream-version-alignment-and-pin-resolution-v1` already authorized it.

## Why

- mlflow 3.13.0 (Apr 2026) introduced **RBAC overhaul** + **MLServer removed** + `judge.align()` optimizer default change (GEPA → MemAlign).
- mlflow 3.15.1 (Aug 2026) adds **Centralized MCP Registry** + MLflow Assistant + shareable table views + multimodal LLM judges.
- The repo's pin is 3.12.0 — 3 patches behind.

## What changes

- `pyproject.toml`: `mlflow>=3.12.0` → `mlflow>=3.15.1,<4.0.0`.
- `bonneagar/stacks/mlflow/secrets.env`: add `MLFLOW_ALLOW_FILE_STORE=true` (3.13+ requires this for legacy `mlruns/` SQLite fallback).
- `bonneagar/stacks/mlflow/pangolin.yaml`: add the `/api/mcp/registry` path for the new MCP Registry.
- Audit the 5 BAML+Mlflow callsites for `judge.align()` — verify the default optimizer change.

## Test plan

1. `uv sync` resolves cleanly.
2. `uv pip show mlflow` prints `3.15.1`.
3. The MLflow container (running on `localhost:5050`) restarts healthy.
4. The 5 BAML+Mlflow callsites still emit evaluation runs successfully.

## Rollback

- Revert `pyproject.toml` pin to `mlflow>=3.12.0`.
- `uv sync` re-resolves.
- Restart the MLflow container.
