# Tasks — Consolidate Observability + Graph DB Stacks

## 1. Phase 2 — Infisical URI migration (4 secrets.env)

- [ ] 1.1 Edit `infrastructure/stacks/mlflow/secrets.env` — replace 5 `{{ infisical:///... }}` with `infisical://dev-baile/mlflow/...`
- [ ] 1.2 Edit `infrastructure/stacks/lakehouse/secrets.env` — replace 16 `{{ infisical:///... }}` with `infisical://dev-baile/lakehouse/...`
- [ ] 1.3 Edit `infrastructure/stacks/graphiti/secrets.env` — replace 3 `{{ infisical:///... }}` with `infisical://dev-baile/graphiti/...`
- [ ] 1.4 Edit `infrastructure/stacks/falkordb/secrets.env` — replace 1 `{{ infisical:///password }}` with `infisical://dev-baile/falkordb/password`
- [ ] 1.5 Run `bun run validate-stacks` — confirm all 4 stacks now pass the infisical-URI check

## 2. Phase 2 — Blueprint port fidelity (2 blueprints)

- [ ] 2.1 Edit `infrastructure/stacks/langfuse/blueprint.yaml` — change `destination-port: 8080` → `3000`
- [ ] 2.2 Edit `infrastructure/stacks/graphiti/blueprint.yaml` — change `destination-port: 8080` → `8000`
- [ ] 2.3 Confirm `infrastructure/stacks/cognee/blueprint.yaml` is unchanged (audit was wrong; container listens on 8000)

## 3. Phase 2 — MCP command path (1 file)

- [ ] 3.1 Edit `opencode.json` line 128 — change `croilar/mcp/devtools/index.ts` → `sruth/croilar/mcp/devtools/index.ts`
- [ ] 3.2 Verify the file exists: `ls sruth/croilar/mcp/devtools/index.ts` (should pass)
- [ ] 3.3 Validate `opencode.json` parses (json.tool)

## 4. Phase 2 — Pangolin.yaml for 6 stacks (6 new files)

- [ ] 4.1 Create `infrastructure/stacks/mlflow/pangolin.yaml` — 6-label private resource `mlflow.cianfhoghlaim.ie` → :5000
- [ ] 4.2 Create `infrastructure/stacks/langfuse/pangolin.yaml` — 6-label private resource `langfuse.cianfhoghlaim.ie` → :3000
- [ ] 4.3 Create `infrastructure/stacks/lakehouse/pangolin.yaml` — 6-label private resource `lakehouse.cianfhoghlaim.ie` → :8181 (Lakekeeper REST)
- [ ] 4.4 Create `infrastructure/stacks/graphiti/pangolin.yaml` — 6-label private resource `graphiti.cianfhoghlaim.ie` → :8000
- [ ] 4.5 Create `infrastructure/stacks/falkordb/pangolin.yaml` — 6-label private resource `falkordb.cianfhoghlaim.ie` → :3000 (FalkorDB UI)
- [ ] 4.6 Create `infrastructure/stacks/cognee/pangolin.yaml` — 6-label private resource `cognee.cianfhoghlaim.ie` → :8000
- [ ] 4.7 Run `bun run validate-stacks` — confirm all 6 pangolin files parse + 6 new stacks are valid 6-file GOLD_STANDARD

## 5. Phase 3 — Datadog Python no-op defaults (4 files)

- [ ] 5.1 Edit `sruth/oideachais/observability/unified_tracer.py` line 296 — change `datadog_enabled: bool = True` → `False`
- [ ] 5.2 Edit `sruth/oideachais/observability/__init__.py` — update module docstring to document no-op default
- [ ] 5.3 Edit `sruth/oideachais/observability/fastapi_middleware.py` — add `DD_ENABLED=${DD_ENABLED:-false}` env var read in `setup_datadog_apm`
- [ ] 5.4 Edit `sruth/oideachais/config/base.py` lines 149, 311 — change `datadog_enabled: bool = Field(default=True)` → `Field(default=False)`
- [ ] 5.5 Edit `sruth/meaisinfhoghlaim/ocr/config/base.py` lines 149, 311 — same change
- [ ] 5.6 Edit `sruth/croilar/_shared/observability/tracing.py` line 97 — confirm graceful no-op on ddtrace import (already handled by try/except)

## 6. Phase 3 — Datadog TypeScript comment (1 file)

- [ ] 6.1 Edit `sruth/croilar/apps/portal/src/routes/api/mcp.gateway.ts` line 10 — change `datadog, langfuse, logfire` → `logfire, langfuse`

## 7. Quality gates

- [ ] 7.1 `mise run lint:skills` → 123/123 pass
- [ ] 7.2 `openspec validate consolidate-observability-and-graph --strict` → pass
- [ ] 7.3 `bun run validate-stacks` → all 6 new pangolin files parse
- [ ] 7.4 `mise run py:typecheck` (pre-existing broken at mise level — not blocking)
- [ ] 7.5 `git diff --stat` → confirm only intended files changed

## 8. Commit + push + archive

- [ ] 8.1 Stage only intended files: `git add -p` (carefully)
- [ ] 8.2 Commit with: `chore(infrastructure): consolidate observability + graph DB wiring (Phase 2+3)`
- [ ] 8.3 `git pull --rebase && git push`
- [ ] 8.4 `openspec archive consolidate-observability-and-graph --yes` — archive the change
- [ ] 8.5 Update `infrastructure/AGENTS.md` stack inventory to add the 6 new pangolin routes

## Out of scope (deferred)

- Booting the 5 stopped Docker containers (cognee, mlflow, graphiti, falkordb, lakehouse-garage) — requires Docker daemon on `bunchloch`
- Deploying graphiti + falkordb as the user-requested graph DB stack
- Infisical vault seeding (`bun run scripts/init-vault.ts`)
- Dagster asset wiring for observability + memory health (Change 3)
- OpenCode agent + skill scoping (Change 3)
- CCC v0 → v1 retirement (Change 3)
