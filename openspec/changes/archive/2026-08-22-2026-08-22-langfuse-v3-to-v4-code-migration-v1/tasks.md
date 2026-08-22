# Tasks — 2026-08-22-langfuse-v3-to-v4-code-migration-v1

## 1. Pre-flight

- [ ] 1.1 Verify the v3 server is still on `langfuse/langfuse:3` (`docker inspect langfuse-web --format '{{.Config.Image}}'`).
- [ ] 1.2 Take a Postgres snapshot: `docker exec langfuse-postgres pg_dump -U postgres langfuse > /tmp/langfuse-v3-snapshot-$(date +%Y%m%d).sql` (or the equivalent command for the langfuse-postgres container).
- [ ] 1.3 Capture the current trace count + dataset count as the rollback baseline.

## 2. Install v4 SDK

- [ ] 2.1 Edit `pyproject.toml`: `langfuse>=3,<4` → `langfuse>=4.0,<5.0`. Run `uv sync`.
- [ ] 2.2 Verify `python3 -c "import langfuse; print(langfuse.__version__)"` prints `4.x`.

## 3. Inventory + migrate 47 call sites

- [ ] 3.1 Use `grep -rnE "langfuse\.(start_as_current_span|start_as_current_generation|update_current_trace|DatasetItemClient|start_span|start_as_current_span|start_generation)" agents/meaisinfhoghlaim/ notebooks/_shared/` to enumerate exact callsites.
- [ ] 3.2 For each `start_as_current_span(name=...)` → `with langfuse.span(name=...)`.
- [ ] 3.3 For each `start_as_current_generation(name=...)` → `with langfuse.generation(name=...)`.
- [ ] 3.4 For each `update_current_trace(...)` → decompose into `propagate_attributes(...)`, `set_current_trace_io(...)`, `set_current_trace_as_public()`.
- [ ] 3.5 For each `from langfuse.api.resources.dataset_items import DatasetItemClient` → use `from langfuse import get_dataset; get_dataset(name).run_experiment(run, dataset=...)`.
- [ ] 3.6 For each `from langfuse.pydantic_compat import v1` → drop the import; use Pydantic v2 native (or `pydantic>=2`).

## 4. Env-var rename

- [ ] 4.1 Search `LANGFUSE_BASEURL` across `.env`, `.infisical.env`, every `secrets.env` under `bonneagar/stacks/`, locket templates in `bonneagar/locket-shim/`.
- [ ] 4.2 Rename to `LANGFUSE_BASE_URL` (note the underscore between `BASE` and `URL`).
- [ ] 4.3 Update `bonneagar/stacks/langfuse/sidecar.yaml` locket env: the resolved env-var name must match.

## 5. Stack image bump

- [ ] 5.1 Edit `bonneagar/stacks/langfuse/compose.yaml`: `langfuse/langfuse:3` → `langfuse/langfuse:4.0.5` (latest stable patch; check https://hub.docker.com/r/langfuse/langfuse/tags for the current 4.x latest).
- [ ] 5.2 Run `docker compose -f bonneagar/stacks/langfuse/compose.yaml -f bonneagar/stacks/langfuse/sidecar.yaml --env-file .env pull` (the pull downloads the new image).
- [ ] 5.3 Run `docker compose -f bonneagar/stacks/langfuse/compose.yaml -f bonneagar/stacks/langfuse/sidecar.yaml --env-file .env up -d`. Verify the v4 server boots + auto-migrates the v3 schema.

## 6. Verify

- [ ] 6.1 `curl -s http://localhost:3001/api/public/health` returns 200.
- [ ] 6.2 Open `http://localhost:3001` in a browser; verify the new **Observations** view is the default landing page.
- [ ] 6.3 Trigger a sample trace: `uv run python -c "from langfuse import Langfuse; l = Langfuse(); l.span(name='test_v4_migration').end(); print('trace emitted')"`.
- [ ] 6.4 Refresh the Langfuse UI; the trace lands in the project `cliste` (or the default project).
- [ ] 6.5 Run `mise run lint:registry` — exits 0.
- [ ] 6.6 Run `mise run data:status` — all 7 sections OK.

## 7. openspec workflow

- [ ] 7.1 `openspec validate 2026-08-22-langfuse-v3-to-v4-code-migration-v1 --strict` exits 0.
- [ ] 7.2 `openspec archive 2026-08-22-langfuse-v3-to-v4-code-migration-v1 --yes` succeeds.

## 8. Commit + push

- [ ] 8.1 `git add pyproject.toml agents/meaisinfhoghlaim/agents/ notebooks/_shared/marimo_patterns.py bonneagar/stacks/langfuse/compose.yaml bonneagar/stacks/langfuse/sidecar.yaml .env .infisical.env bonneagar/stacks/langfuse/secrets.env`
- [ ] 8.2 `git commit -F /tmp/commit-msg.txt` (commit message in the standard format with the openspec change-id in the body).
- [ ] 8.3 `git push origin HEAD` to push the feature branch.

## 9. Documentation

- [ ] 9.1 Update `.agents/skills/agent-observability/SKILL.md` with the v4 method renames.
- [ ] 9.2 Add a 1-page note to `docs/agents/langfuse-v4-migration.md` covering the 5-step migration for future reference.
