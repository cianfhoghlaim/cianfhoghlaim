# Tasks: cleanup-and-boot-stacks

## 0. Pre-flight

- [ ] 0.1 Verify working tree is clean except for other agents' in-flight changes (do not touch `sruth/meaisinfhoghlaim/*` or `spaces/data-engineering`)
- [ ] 0.2 Confirm `openspec list --specs` shows `agent-observability` (5 reqs) — anchor spec for this change
- [ ] 0.3 Confirm `monitoring/` stack is already deleted (parallel-agent work)

## 1. Spec delta — `agent-observability`

- [ ] 1.1 In `openspec/changes/cleanup-and-boot-stacks/specs/agent-observability/spec.md`, write REMOVED Requirements block for `Datadog APM + LLMObs` (the existing requirement at spec.md line 53-67) with reason + migration
- [ ] 1.2 In the same file, write ADDED Requirements block for 8 new requirements:
  - `Prometheus Service Removed from litellm`
  - `Logfire Stack Self-Hosted Compose`
  - `OpenCode Configuration Single Source`
  - `Infisical URI Format Conformance`
  - `Blueprint Port Fidelity`
  - `MCP Command Path Correctness`
  - `Pangolin Config Per Operational Stack`
  - `LLM Observability Tri-Split (Langfuse + MLflow + Logfire)`
- [ ] 1.3 Run `openspec validate cleanup-and-boot-stacks --strict` — must pass before any commit

## 2. Phase 0 deletions

- [ ] 2.1 Delete `infrastructure/stacks/litellm/config/prometheus.yml` (16-line scrape config)
- [ ] 2.2 Edit `infrastructure/stacks/litellm/compose.yaml`: remove lines 103-120 (the `prometheus:` service block + `prometheus_data:` volume declaration)
- [ ] 2.3 Edit `infrastructure/stacks/litellm/compose.dev.yaml`: remove any `prometheus:` block
- [ ] 2.4 Edit `infrastructure/stacks/litellm/README.md`: drop the paragraph that mentions Prometheus
- [ ] 2.5 Delete `.opencode.yaml` (stale alternative MCP config)
- [ ] 2.6 Delete `infrastructure/stacks/cognee/cognee-stack.yaml` (duplicate of `cognee/blueprint.yaml`)
- [ ] 2.7 Archive `openspec/changes/fix-existing-stacks/` via `openspec archive fix-existing-stacks --yes` (the monitoring stack was never built)

## 3. Phase 0 new file — logfire compose

- [x] 3.1 Write `infrastructure/stacks/logfire/compose.yaml` — OpenTelemetry collector forwarding to Logfire cloud (Pydantic Logfire is SaaS-only)
- [x] 3.2 Write `infrastructure/stacks/logfire/blueprint.yaml` — stub file documenting why no Pangolin route (SaaS-only UI)
- [x] 3.3 Write `infrastructure/stacks/logfire/sidecar.yaml` — standard Locket sidecar pattern with `cianchoghlaim_locket_secrets` tmpfs volume
- [x] 3.4 SKIP `infrastructure/stacks/logfire/pangolin.yaml` — local OTEL collector has no web UI; Logfire UI is SaaS at logfire.pydantic.dev (documented in stack README; matches kcg-pangolin-stack skill's "Reference stack (not deployed)" classification)
- [x] 3.5 Update `infrastructure/stacks/logfire/secrets.env` — migrate Jinja `{{ infisical:///write_token }}` → canonical `infisical://dev-baile/logfire/write_token`
- [x] 3.6 Write `infrastructure/stacks/logfire/config/otelcol.yaml` — OTEL Collector configuration (receivers, processors, exporters)
- [x] 3.7 Write `infrastructure/stacks/logfire/compose.dev.yaml` — no-op Locket alpine override + .env fallback
- [x] 3.8 Run `bun run validate-stacks` to confirm logfire is now a valid stack (no warnings for logfire)

## 4. Phase 1 — Infisical URI migration

- [ ] 4.1 Edit `infrastructure/stacks/mlflow/secrets.env` — replace `{{ infisical:///... }}` with `infisical://dev-baile/mlflow/...`
- [ ] 4.2 Edit `infrastructure/stacks/lakehouse/secrets.env` — same migration (15+ secrets)
- [ ] 4.3 Edit `infrastructure/stacks/graphiti/secrets.env` — same migration (OPENAI_API_KEY)
- [ ] 4.4 Edit `infrastructure/stacks/falkordb/secrets.env` — same migration (FALKORDB_PASSWORD)
- [ ] 4.5 (Skip `logfire/secrets.env` — handled in 3.5)
- [ ] 4.6 (Skip `langfuse/secrets.env`, `cognee/secrets.env`, `litellm/secrets.env` — already canonical)

## 5. Phase 1 — Blueprint port fidelity

- [ ] 5.1 Edit `infrastructure/stacks/langfuse/blueprint.yaml`: change port `:8080` → `:3001` (matches compose host port)
- [ ] 5.2 Edit `infrastructure/stacks/graphiti/blueprint.yaml`: change port `:8080` → `:8000`
- [ ] 5.3 Edit `infrastructure/stacks/cognee/blueprint.yaml`: change port `:8000` → `:8100`

## 6. Phase 1 — MCP command path

- [ ] 6.1 Edit `opencode.json` `mcp.croilar-devtools.command` from `["bun", "run", "croilar/mcp/devtools/index.ts"]` to `["bun", "run", "sruth/croilar/mcp/devtools/index.ts"]` (correct path per `ls sruth/croilar/mcp/devtools/`)
- [ ] 6.2 Verify the file exists: `ls sruth/croilar/mcp/devtools/index.ts` (should pass)

## 7. Phase 1 — Pangolin config per stack

- [ ] 7.1 Create `infrastructure/stacks/mlflow/pangolin.yaml` — private resource `mlflow.cianfhoghlaim.ie` → :5000
- [ ] 7.2 Create `infrastructure/stacks/langfuse/pangolin.yaml` — private resource `langfuse.cianfhoghlaim.ie` → :3001
- [ ] 7.3 Create `infrastructure/stacks/lakehouse/pangolin.yaml` — 6 private + 4 public resources per blueprint
- [ ] 7.4 Create `infrastructure/stacks/graphiti/pangolin.yaml` — private resource `graphiti.cianfhoghlaim.ie` → :8000 (compose port)
- [ ] 7.5 Create `infrastructure/stacks/falkordb/pangolin.yaml` — private resource `falkordb.cianfhoghlaim.ie` → :3000 (UI port)
- [ ] 7.6 Create `infrastructure/stacks/cognee/pangolin.yaml` — private resource `cognee.cianfhoghlaim.ie` → :8100 (compose port)
- [ ] 7.7 (Skip logfire — handled in 3.4)

## 8. Skill update — drop Datadog

- [x] 8.1 Edit `.agents/skills/agent-observability/SKILL.md`:
  - Line 3 description frontmatter: drop "Datadog APM + LLMObs (`@llm`, `@agent`, `@workflow`, `@task`)," → keep MLflow + Langfuse + Ragas + structlog
  - Line 16 trigger: drop "Wire Datadog APM + LLMObs for full-stack tracing"
  - Lines 25-49 diagram: replace "Layer 1: Traces (Datadog APM + LLMObs)" with "Layer 1: Traces (Langfuse + Logfire)"
  - Lines 51-89 §1 "Datadog APM + LLMObs" → replaced with "Langfuse + Logfire tracing" section
  - Lines 208, 221, 237, 520, 567, 571, 632: drop remaining Datadog references
- [x] 8.2 Delete `.agents/skills/datadog/SKILL.md` (already absent)
- [x] 8.3 Delete `.agents/skills/agent-observability/references/patterns/observability-patterns.md` (all-Datadog deep-dive; replaced with cross-references in main SKILL.md)
- [x] 8.4 Edit `.agents/skills/kubernetes/SKILL.md` line 145: "Datadog APM" → "Logfire + Langfuse + MLflow + RAGAS"
- [x] 8.5 Edit `.agents/skills/agent-fleet-orchestration/SKILL.md` line 240: drop "+ Datadog"
- [x] 8.6 Edit `.agents/skills/croilar-stream-registry/SKILL.md` line 89: replace `datadog_enabled` with `logfire_enabled`

## 9. Komodo procedure cleanup

- [x] 9.1 Edit `infrastructure/komodo/procedures/auto-deploy-stacks.toml`: dropped the 3 Datadog stacks (oci/macbook/oracle)
- [x] 9.2 Edit `infrastructure/komodo/procedures/crypteolas-pipeline.toml`: replaced `DD_*` env vars with `LOGFIRE_*`
- [x] 9.3 Edit `infrastructure/komodo/procedures/observability.toml`: rewrote from 3 Datadog stacks → single logfire stack
- [x] 9.4 Edit `infrastructure/komodo/stacks/observability.toml`: rewrote from 3 Datadog stacks → single logfire stack
- [x] 9.5 Edit `infrastructure/komodo/procedures/deploy-observability.toml`: removed Datadog Stage 3 + added Logfire collector Stage 3
- [x] 9.6 Edit `infrastructure/komodo/procedures/crypteolas-ui.toml`: replaced `DD_*` with `LOGFIRE_*`
- [x] 9.7 Edit `infrastructure/komodo/procedures/agentos-api.toml`: replaced `DD_*` with `LOGFIRE_*`
- [x] 9.8 Edit `infrastructure/komodo/procedures/codeolas-pipeline.toml`: replaced `DD_*` with `LOGFIRE_*`
- [x] 9.9 Edit `scripts/stack-doctor.sh` line 64: validator regex updated to accept both Locket-canonical + Jinja infisical URI forms

## 10. Quality gates

- [x] 10.1 `mise run lint:skills` → 123/123 pass
- [ ] 10.2 `mise run py:typecheck` → expect pass
- [ ] 10.3 `mise run turbo typecheck` → expect pass
- [x] 10.4 `bun run validate-stacks` → logfire is now a valid stack (no warnings); other 30+ stacks with `:latest` tags are pre-existing out-of-scope warnings
- [x] 10.5 `openspec validate cleanup-and-boot-stacks --strict` → pass
- [ ] 10.6 `git diff --stat` → confirm only intended files changed

## 11. Commit + push + archive

- [ ] 11.1 Stage only intended files: `git add -p` (carefully)
- [ ] 11.2 Commit with: `chore(infrastructure): cleanup dead prometheus + logfire scaffold + drop datadog from observability split`
- [ ] 11.3 `git pull --rebase && git push`
- [ ] 11.4 `openspec archive cleanup-and-boot-stacks --yes` — archive the change
- [ ] 11.5 Update `infrastructure/AGENTS.md` stack inventory to reflect: monitoring removed, logfire deployable

## Out of scope (deferred to Change 2)

- Migrating MLflow + Langfuse onto lakehouse Garage S3
- Reconciling cognee_config.py with the actual pghybrid Postgres-only reality
- Wiring Ragas eval as a Dagster asset_check
- Adding observability + memory health Dagster assets
- Booting the 5 stopped Docker containers (cognee/mlflow/graphiti/falkordb/lakehouse-garage) — require Docker daemon start on `bunchloch`
- Deploying graphiti + falkordb as the user-requested graph DB stack
- **Datadog Python code removal (60+ refs across `sruth/oideachais/observability/`, `sruth/meaisinfhoghlaim/ocr/observability.py`, `sruth/codeolas/core/observability.py`, `sruth/oideachais/api/main.py`, `sruth/meaisinfhoghlaim/agents/api/main.py`, `sruth/croilar/_shared/config/settings.py`, `sruth/oideachais/dagster_defs/assets/embedding_assets.py`, `sruth/croilar/apps/portal/src/routes/api/mcp.gateway.ts`)** — out of scope for this change; the code paths are still functional (Datadog SDK is a no-op when `DD_API_KEY` is unset)
