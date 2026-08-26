# Tasks — 2026-08-21-mlflow-3.12-to-3.15.1-v1

## 1. Bump

- [ ] 1.1 Edit `pyproject.toml`: `mlflow>=3.12.0` → `mlflow>=3.15.1,<4.0.0`. Run `uv sync`. Verify `uv pip show mlflow | grep Version` prints `3.15.1`.

## 2. Audit callsites

- [ ] 2.1 Use `grep -rn "judge.align" agents/ meaisinfhoghlaim/ notebooks/`. Verify each call site either explicitly uses `optimizer='gepa'` (to preserve old behavior) or is intentional MemAlign semantics.
- [ ] 2.2 Verify the 5 BAML+Mlflow callsites use `mlflow.log_metric` / `mlflow.log_param` (both unchanged in 3.15+).

## 3. Stack updates

- [ ] 3.1 Add `MLFLOW_ALLOW_FILE_STORE=true` to `bonneagar/stacks/mlflow/secrets.env` (legacy `mlruns/` support).
- [ ] 3.2 Add `/api/mcp/registry` path to `bonneagar/stacks/mlflow/pangolin.yaml` (NEW MCP Registry endpoint).

## 4. Verify

- [ ] 4.1 Run `mise run data:status` — verify mlflow reports correctly.
- [ ] 4.2 Run `curl -s http://localhost:5050/api/2.0/mlflow/experiments/list` — verify the API responds.

## 5. openspec

- [ ] 5.1 `openspec validate 2026-08-21-mlflow-3.12-to-3.15.1-v1 --strict`.
- [ ] 5.2 `openspec archive 2026-08-21-mlflow-3.12-to-3.15.1-v1 --yes`.
