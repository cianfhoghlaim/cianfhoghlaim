# 2026-08-21-langfuse-v3-to-v4-migration-v1

## Summary

Migrate the self-hosted Langfuse server + Python SDK from v3 to v4 by the **2026-11-16 v3-Cloud deprecation date**. This is `Priority 0` per the upstream-version audit (`stedding/audit/2026-08-21-upstream-audit.md`); it's the single most time-critical change in the alignment work. Blocked by the umbrella change `2026-08-21-upstream-version-alignment-and-pin-resolution-v1` (now archived).

## Why

- v3 Cloud is **deprecated as of 2026-11-16**; local v3 servers stop receiving security updates shortly after.
- v4 ships **Observations-first data model** (the Traces table is replaced by Observations; traces become a derived view).
- The Python SDK v4 removes `start_span`, `start_as_current_span`, `start_generation`, `start_as_current_generation`, `update_current_trace` (now decomposed into `propagate_attributes()`, `set_current_trace_io()`, `set_current_trace_as_public()`), and the `DatasetItemClient` class (replaced by `dataset.run_experiment()`).
- `LANGFUSE_BASEURL` env-var is renamed to `LANGFUSE_BASE_URL`.
- v4 is OpenTelemetry-first and drops Pydantic v1 support.

The 12-agent fleet in `agents/meaisinfhoghlaim/agents/` is the main migration surface — all `@observe`-decorated call sites need the v4 method renames.

## What changes

- `pyproject.toml`: bump `langfuse>=3,<4` → `langfuse>=4.0,<5.0`.
- `bonneagar/stacks/langfuse/compose.yaml`: replace `langfuse/langfuse:3` with `langfuse/langfuse:4` (the latest stable patch).
- `bonneagar/stacks/langfuse/sidecar.yaml`: the Locket sidecar resolves `LANGFUSE_BASE_URL` (new name) + the 3 langfuse secrets.
- `agents/meaisinfhoghlaim/agents/*.py`: 47 call sites audited + migrated to v4 patterns.
- `agents/meaisinfhoghlaim/firecrawl_mcp/client.py`: the `@observe`-wrapped client updated.
- `notebooks/_shared/marimo_patterns.py`: `llm_chat_with_prompts` helper updated (the `@observe` chain).

### New MODIFIED specs under `openspec/specs/`

| Spec | Change |
|:--|:--|
| `agent-observability` | The umbrella change already added the v3→v4 migration contract + LiteLLM v1.97 router updates. This change implements that contract. |
| `centralized-model-registry` | Add `langfuse-v4` ingest pipeline asset (one new asset) for evaluation runs. |

### Migration steps

1. **Pre-migration snapshot** of the v3 Postgres state. Per https://langfuse.com/self-hosting/upgrade/upgrade-guides/upgrade-v3-to-v4, take a Postgres dump.
2. **Bring up the v4 server** with `docker compose pull && docker compose up -d`. The v4 server auto-migrates the v3 schema.
3. **Upgrade the Python SDK** in a single PR — `pyproject.toml` bump.
4. **Replace the v3 method calls** in the 47 call sites:
   - `with langfuse.start_as_current_span(name="x") as span:` → `with langfuse.span(name="x") as span:` (or the v4 equivalent — confirm via the v4 SDK docs).
   - `langfuse.update_current_trace(...)` → split into `propagate_attributes(...)`, `set_current_trace_io(...)`, etc.
   - `DatasetItemClient` → `langfuse.get_dataset(name).run_experiment(...)`.
5. **Rename env var**: `LANGFUSE_BASEURL` → `LANGFUSE_BASE_URL` everywhere it's set (compose files, Locket secrets.env, .env).
6. **Pydantic v2 audit**: any code that imports `from langfuse.pydantic_compat import v1` needs `from langfuse.pydantic_compat import v2` (or just use Pydantic v2 directly).
7. **Verify the 5 BIEP eval scenarios** still emit traces to the Observations view.

## Test plan

1. `uv sync` succeeds without pinning conflicts (langfuse upgrade + dagster-webserver still works).
2. `docker compose -f bonneagar/stacks/langfuse/compose.yaml -f bonneagar/stacks/langfuse/sidecar.yaml up -d` brings the v4 server up.
3. `curl -s http://localhost:3001/api/public/health` returns 200.
4. `python3 -c "import langfuse; print(langfuse.__version__)"` prints `4.x`.
5. The 12-agent fleet connects + emits a trace → trace visible in `http://localhost:3001/project/cliste/observations`.
6. `mise run lint:registry` exits 0 (model registry + langfuse v4 refs aligned).

## Rollback

- Revert `pyproject.toml` pin to `langfuse>=3,<4`.
- Revert `bonneagar/stacks/langfuse/compose.yaml` to `langfuse/langfuse:3`.
- `docker compose down && docker compose up -d` → restores v3.
- Restore the Postgres state from the pre-migration dump.

This is a non-destructive change in the sense that the v3 image + state can be restored independently of the v4 attempt.
