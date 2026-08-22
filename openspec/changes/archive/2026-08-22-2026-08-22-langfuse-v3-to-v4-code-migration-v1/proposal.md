# 2026-08-22-langfuse-v3-to-v4-code-migration-v1

## Summary

This change implements the Langfuse v3 → v4 migration that the umbrella change `2026-08-21-upstream-version-alignment-and-pin-resolution-v1` and the proposal `2026-08-21-2026-08-21-langfuse-v3-to-v4-migration-v1/` (archived 2026-08-21) authorised. The proposal specified the v3 → v4 contract; this change is the **implementation** that makes the 47 agent call sites + the env-var rename + the Pydantic v2 audit land in the codebase.

## Why

- **The 2026-11-16 v3 Cloud deprecation date is the single hard deadline in the entire backlog.** Langfuse v3 will stop receiving security updates shortly after; the self-hosted server schema migration is automatic in v4 but the Python SDK v4 has breaking changes (renamed methods, env-var rename, dropped Pydantic v1 support) that won't be caught by the upgrade.
- The umbrella audit (`stedding/audit/2026-08-21-upstream-audit.md`) flagged this as Priority 0.
- The archived proposal `2026-08-21-2026-08-21-langfuse-v3-to-v4-migration-v1/` already added 3 MODIFIED Requirements to `agent-observability`. This change is the implementation of those requirements; no new spec deltas are needed (the v4 contract is already in the canonical spec).

## What changes

- `pyproject.toml`: bump `langfuse>=3,<4` → `langfuse>=4.0,<5.0`.
- `agents/meaisinfhoghlaim/agents/*.py`: migrate 47 call sites (see Tasks §3 for the migration table).
- `agents/meaisinfhoghlaim/firecrawl_mcp/client.py`: the `@observe`-wrapped client.
- `notebooks/_shared/marimo_patterns.py`: the `llm_chat_with_prompts` + `run_dagster_asset_check` helpers.
- `bonneagar/stacks/langfuse/compose.yaml`: `langfuse/langfuse:3` → `langfuse/langfuse:4.0.5` (latest stable patch).
- `bonneagar/stacks/langfuse/sidecar.yaml`: Locket sidecar resolves the new `LANGFUSE_BASE_URL` env var.
- `.env` + `.infisical.env`: rename `LANGFUSE_BASEURL` → `LANGFUSE_BASE_URL` everywhere.
- `bonneagar/stacks/langfuse/secrets.env`: same rename.

### Migration table (call sites)

| v3 method | v4 replacement |
|:--|:--|
| `with langfuse.start_as_current_span(name=...) as span:` | `with langfuse.span(name=...) as span:` |
| `with langfuse.start_as_current_generation(name=...) as gen:` | `with langfuse.generation(name=...) as gen:` |
| `langfuse.update_current_trace(metadata=..., tags=..., session_id=...)` | decompose: `propagate_attributes(metadata=...)` + `set_current_trace_io(input=..., output=...)` + `set_current_trace_as_public()` |
| `from langfuse.api.resources.dataset_items import DatasetItemClient` | `from langfuse import get_dataset; get_dataset(name).run_experiment(run, dataset=...)` |
| `from langfuse.pydantic_compat import v1` | drop entirely; use Pydantic v2 native |
| `LANGFUSE_BASEURL` env var | `LANGFUSE_BASE_URL` env var |

### Pre-migration snapshot

- Take a `pg_dump` of the v3 schema state via the v3 server (currently `langfuse/langfuse:3` on port 3001) → `/tmp/langfuse-v3-snapshot.sql`.
- The v4 server auto-migrates the v3 schema; no data loss is expected per https://langfuse.com/self-hosting/upgrade/upgrade-guides/upgrade-v3-to-v4.

## Test plan

1. `uv sync` resolves cleanly.
2. `python3 -c "import langfuse; print(langfuse.__version__)"` prints `4.x`.
3. `docker compose -f bonneagar/stacks/langfuse/compose.yaml -f bonneagar/stacks/langfuse/sidecar.yaml up -d` brings the v4 server up.
4. `curl -s http://localhost:3001/api/public/health` returns 200.
5. Trigger a sample trace from `agents/meaisinfhoghlaim/agents/root_agent.py` — verify the trace lands in the v4 **Observations** view (not v3's Traces).
6. Run `mise run lint:registry` — exits 0 (no model-registry regressions).
7. `openspec validate 2026-08-22-langfuse-v3-to-v4-code-migration-v1 --strict` exits 0.
8. `openspec archive --yes` succeeds.

## Rollback

- Revert `pyproject.toml` pin to `langfuse>=3,<4`.
- Revert the 47 callsite migrations (the migration table above is symmetric).
- Revert the env-var rename.
- `docker compose down && docker compose up -d` (with `langfuse/langfuse:3` in the compose file) → restores v3.
- Restore the Postgres state from the pre-migration dump.

This is a non-destructive change in the sense that the v3 image + state can be restored independently of the v4 attempt.
