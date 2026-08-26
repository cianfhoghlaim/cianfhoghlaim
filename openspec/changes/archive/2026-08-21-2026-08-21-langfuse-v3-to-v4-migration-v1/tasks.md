# Tasks — 2026-08-21-langfuse-v3-to-v4-migration-v1

## 1. Pre-flight

- [ ] 1.1 Run `mise run lint:skills` to ensure the 166 skill YAML files still validate.
- [ ] 1.2 Run `mise run data:status` to capture the v3 baseline state.
- [ ] 1.3 Take a Postgres dump of the v3 schema: `ssh oci.arm1 'pg_dump -U pangolin -d langfuse > /tmp/langfuse-v3-$(date +%Y%m%d).sql'` (OR `docker exec langfuse-postgres pg_dump ...` if local).
- [ ] 1.4 Document the v3 trace count + dataset count as the rollback baseline.

## 2. Bump

- [ ] 2.1 Edit `pyproject.toml` to bump `langfuse>=3,<4` → `langfuse>=4.0,<5.0`. Run `uv sync`.
- [ ] 2.2 Edit `bonneagar/stacks/langfuse/compose.yaml` to bump `langfuse/langfuse:3` → `langfuse/langfuse:4` (latest stable patch, e.g. `:4.0.5`).
- [ ] 2.3 Run `docker compose -f bonneagar/stacks/langfuse/compose.yaml -f bonneagar/stacks/langfuse/sidecar.yaml --env-file .env pull && docker compose up -d`. Verify the v4 server boots + auto-migrates the v3 schema.
- [ ] 2.4 Verify `curl -s http://localhost:3001/api/public/health` returns 200.

## 3. Migrate call sites (47 sites in `agents/meaisinfhoghlaim/agents/*.py`)

- [ ] 3.1 Use `bunx ccc:search "langfuse"` to enumerate all 47 call sites.
- [ ] 3.2 Replace `with langfuse.start_as_current_span(name=...) as span:` with the v4 equivalent (`with langfuse.span(name=...) as span:` or per the v4 SDK docs).
- [ ] 3.3 Replace `langfuse.update_current_trace(metadata=..., tags=..., session_id=...)` with the v4 split (`propagate_attributes()`, `set_current_trace_io()`, `set_current_trace_as_public()`).
- [ ] 3.4 Replace `from langfuse.api.resources.dataset_items import DatasetItemClient` with `from langfuse import get_dataset; get_dataset(name).run_experiment(...)`.
- [ ] 3.5 Replace `LANGFUSE_BASEURL` with `LANGFUSE_BASE_URL` in `.env` + `.infisical.env` + every `secrets.env` that references it.
- [ ] 3.6 Audit for `from langfuse.pydantic_compat import v1` → either remove or migrate to Pydantic v2 directly.

## 4. Verify

- [ ] 4.1 Run `python3 -c "import langfuse; print(langfuse.__version__)"` — must print `4.x`.
- [ ] 4.2 Open `http://localhost:3001` (or via Pangolin at `langfuse.cianfhoghlaim.ie`) — verify the new Observations view is the default landing page.
- [ ] 4.3 Trigger a sample trace from `agents/meaisinfhoghlaim/agents/root_agent.py` — verify the trace lands in Observations with the right metadata.
- [ ] 4.4 Run `mise run ml:litellm:regenerate` — verify the LiteLLM router still uses Langfuse for observability (no broken ref).
- [ ] 4.5 Run `mise run data:status` — verify the v4 server is healthy.

## 5. openspec workflow

- [ ] 5.1 Run `openspec validate 2026-08-21-langfuse-v3-to-v4-migration-v1 --strict` — must exit 0.
- [ ] 5.2 Archive via `openspec archive 2026-08-21-langfuse-v3-to-v4-migration-v1 --yes`.
- [ ] 5.3 Update the change ticket with the rollback baseline + new trace count.

## 6. Documentation

- [ ] 6.1 Update `AGENTS.md` "Critical Rules" → "Langfuse v4 is now required".
- [ ] 6.2 Update `.agents/skills/agent-observability/SKILL.md` with the v4 method renames.
- [ ] 6.3 Add a 1-page note to `docs/agents/langfuse-v4-migration.md` covering the 5-step migration for future reference.
