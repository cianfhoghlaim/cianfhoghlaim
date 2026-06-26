# Change: cleanup-and-boot-stacks

> **Change 1 of 3** in the
> *cleanup-and-boot-stacks → consolidate-observability-and-graph →
> centralize-agent-context-and-automate* sequence. Each change anchors
> on a different shared spec so the openspec archive traces the
> architectural decisions cleanly.

## Why

A 2026-06-26 read-only audit of the 7 observability + memory stacks
(`mlflow`, `logfire`, `langfuse`, `lakehouse`, `graphiti`, `falkordb`,
`cognee`) plus the OpenCode agent configuration (`opencode.json`,
`.opencode.yaml`) plus the indexing pipeline (CocoIndex v0/v1 +
Cognee cognify) revealed:

1. **`litellm-prometheus` is dead.** Container exited 2026-06-23; the
   only scrape target is `litellm:4000` itself; no Grafana / Alertmanager
   / external consumer exists. The service block adds ~1 KB of dead
   YAML to `litellm/compose.yaml` and `compose.dev.yaml`.

2. **The `monitoring/` stack was planned but never built.** The
   `fix-existing-stacks` openspec change promised a
   Prometheus + Grafana + Loki stack; the directory was created on
   2026-06-26 by parallel-agent cleanup work but the canonical
   `openspec/changes/fix-existing-stacks/proposal.md` still claims
   the work is in flight. The change should be archived as superseded
   so the openspec archive reflects reality.

3. **`infrastructure/stacks/logfire/` is a 2-file placeholder.** No
   `compose.yaml`, no `blueprint.yaml`, no `sidecar.yaml`. The stack
   is referenced by `unified_tracer.py:LOGFIRE_TOKEN` and a SKILL.md
   but cannot be deployed. Either build the compose file (the
   "Logfire self-hosted" route) or document Logfire as a cloud-only
   Pydantic service (the "Logfire SaaS" route).

4. **`.opencode.yaml` is a stale alternative config.** It declares
   6 MCP servers (`letta`, `chunkhound`, `skyvern`, `docling`,
   `marker`, `graphiti`) that the runtime (`opencode.json`) does not
   see. OpenCode reads `opencode.json` only; the `.yaml` is dead.

5. **The `agent-observability` spec still requires Datadog.** The
   user has decided (2026-06-26) to consolidate observability around
   **Langfuse + MLflow + Logfire** — no Datadog. The existing
   `Datadog APM + LLMObs` Requirement (spec.md line 53-67) plus the
   Datadog layer in `agent-observability/SKILL.md` §1 + the four
   Datadog agents configured in
   `infrastructure/komodo/procedures/auto-deploy-stacks.toml` need
   to be retired.

6. **5 of 7 audited stacks have unrendered Jinja `{{ infisical:///... }}`
   in their `secrets.env`.** Locket only resolves the canonical
   `infisical://dev-baile/<svc>/<key>` URI format (the format already
   used by `langfuse`, `cognee`, `litellm`). The 5 broken files:
   `mlflow`, `lakehouse`, `graphiti`, `falkordb`, `logfire`.

7. **3 stacks have blueprint port mismatches.** `langfuse`
   blueprint declares :8080 but compose host port is :3001.
   `graphiti` blueprint declares :8080 but compose host port is
   :8000. `cognee` blueprint declares :8000 but compose host port
   is :8100. Komodo consumes `pangolin.yaml`, not blueprint, so
   the blueprints are documentation-only — but they are wrong.

8. **`croilar-devtools` MCP command path is broken.** `opencode.json:128`
   declares `["bun", "run", "croilar/mcp/devtools/index.ts"]` but the
   file actually lives at `sruth/croilar/mcp/devtools/index.ts`. The
   command fails unless `cwd` is `sruth/croilar/` at runtime.

9. **6 of 7 audited stacks have no `pangolin.yaml`.** Only the
   `pangolin.yaml` file is consumed by Komodo (`file_paths` field);
   `blueprint.yaml` is documentation. Without `pangolin.yaml`,
   Komodo cannot apply the public/private resource routes.

## What changes

### Deletions

| File / directory | Reason |
|:--|:--|
| `infrastructure/stacks/litellm/compose.yaml` (lines 103-120 — `prometheus` service block + `prometheus_data` volume) | Dead container, no consumer |
| `infrastructure/stacks/litellm/compose.dev.yaml` (lines referencing `prometheus`) | Same |
| `infrastructure/stacks/litellm/config/prometheus.yml` | 16-line scrape config, single target, no consumer |
| `.opencode.yaml` | Stale alternative MCP config; runtime uses `opencode.json` |
| `infrastructure/stacks/cognee/cognee-stack.yaml` | Trivial duplicate of `blueprint.yaml` |

Note: the `infrastructure/stacks/monitoring/` stack directory was
already deleted by parallel-agent cleanup work earlier today
(2026-06-26). The directory is **already gone** in the working tree
per `git status`; this change just acknowledges the deletion in the
openspec record.

### New file

| File | Purpose |
|:--|:--|
| `infrastructure/stacks/logfire/compose.yaml` | Self-hosted Logfire stack with the standard 6-file GOLD_STANDARD pattern |

### Modifications

| File | Change |
|:--|:--|
| `infrastructure/stacks/litellm/compose.yaml` | Remove `prometheus` service + `prometheus_data` volume (lines 103-120) |
| `infrastructure/stacks/litellm/compose.dev.yaml` | Remove `prometheus` block |
| `infrastructure/stacks/litellm/README.md` | Drop Prometheus paragraph |
| `infrastructure/stacks/{mlflow,lakehouse,graphiti,falkordb,logfire}/secrets.env` | Migrate Jinja `{{ infisical:///... }}` → canonical `infisical://dev-baile/...` URIs |
| `infrastructure/stacks/{langfuse,graphiti,cognee}/blueprint.yaml` | Reconcile declared ports with `compose.yaml` host ports |
| `opencode.json` | Fix `croilar-devtools` command path (`croilar/...` → `sruth/croilar/...`) |
| `.agents/skills/agent-observability/SKILL.md` | Drop Datadog layer from the 5-layer diagram + drop Datadog from description frontmatter + drop cross-reference to `datadog/SKILL.md` |
| `infrastructure/komodo/procedures/auto-deploy-stacks.toml` | Drop the 4 Datadog agent stacks (`datadog-oci`, `datadog-macbook`, `datadog-oracle`, + 1 more) — also remove `DD_APM_ENABLED=true` env entries from `crypteolas-pipeline.toml` |

### Openspec record

| Action | Target |
|:--|:--|
| Archive | `openspec/changes/fix-existing-stacks/` (as superseded — monitoring stack was never built) |
| Modify spec | `openspec/specs/agent-observability/spec.md` — REMOVE Datadog requirement, ADD 8 new requirements |

### Out of scope (deferred to Change 2)

- Migrating MLflow + Langfuse onto lakehouse Garage S3
- Reconciling cognee_config.py with the actual pghybrid Postgres-only reality
- Wiring Ragas eval as a Dagster asset_check
- Adding observability + memory health Dagster assets

## Impact

- **Lines removed:** ~85 (prometheus service blocks + duplicates + Datadog)
- **Lines added:** ~120 (logfire compose + 7 new `pangolin.yaml` files + spec)
- **Net stack count change:** -1 (prometheus) · +1 (logfire deployable) · net 0
- **Risk:** Very low — every deletion is git-revertible; every
  modification is documented in this proposal.

## Validation gates

1. `mise run lint:skills` — must pass 123/123
2. `openspec validate cleanup-and-boot-stacks --strict` — must pass
3. `bun run validate-stacks` — all 102 stacks still parse
4. Visual inspection of each modified `secrets.env` to confirm Locket compatibility
5. `git diff` of `opencode.json` to confirm MCP path resolves to a real file
