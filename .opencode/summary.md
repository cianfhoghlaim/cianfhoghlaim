# Anchored summary — observability + graph + agent-context consolidation

## Goal
- End-to-end observability + agent-context pipeline: integrate 8 stacks (mlflow, logfire, langfuse, lakehouse, graphiti, falkordb, cognee, sruth/oideachais), delete prometheus, automate code indexing, centralize OpenCode agent context/skills/tools — via 3 sequential openspec changes (P0-P1, P2-P3, P4-P6).

## Constraints & Preferences
- **BUILD MODE** (user said "proceed").
- AGENTS.md priority quick-reference applies (4 priority specs, 4 priority skills, 4 priority commands, 1 priority mise task).
- All new code uses `sruth/...` paths (not legacy root).
- CocoIndex v1 canonical pattern: `coco.App(...)` + `@coco.fn(memo=True)` + `@coco.lifespan` delegating to `shared_lifespan`.
- Validate with `openspec validate <change-id> --strict` before any commit.
- Secrets via Infisical (`dev-baile` env) via Locket-canonical `infisical://dev-baile/<svc>/<key>` URIs (NOT Jinja `{{ infisical:///... }}`).
- Agent protocol: never amend, force-push, or skip hooks.
- Image pinning policy: every image SHALL be pinned to semver (no `:latest`).
- 5-file GOLD_STANDARD stack pattern: compose.yaml + sidecar.yaml + secrets.env + blueprint.yaml + README.md (pangolin.yaml required only for stacks with local web UI; SaaS-only stacks may omit it).
- Validator regex accepts both Locket-canonical + legacy Jinja forms during migration period.
- The Datadog Python code is preserved as graceful no-op fallbacks (60+ `from ddtrace import ...` lines stay; only the `datadog_enabled` default flips True → False).

## Progress
### Done
- **Change 1 (`cleanup-and-boot-stacks`) — COMPLETE & ARCHIVED** (commit `3b481e72d` + `8ff1997a1`):
  - Phase 0.1-0.3: litellm prometheus deleted; `.opencode.yaml` deleted; cognee-stack.yaml deleted.
  - Phase 0.4: logfire stack scaffolded as OTEL collector (SaaS-only decision).
  - Phase 0.5: fix-existing-stacks archived; canonical `stack-audit` spec created.
  - Phase 0.6-0.7: Datadog dropped from agent-observability skill + 3 cross-ref skills + references file deleted.
  - Phase 0.8: Datadog removed from Komodo procedures + stack registrations.
  - Phase 0.9: stack-doctor.sh validator regex updated.
  - Phase 1.1: logfire secrets.env migrated; 4 others deferred to Change 2.
  - cleanup-and-boot-stacks archived as `2026-06-26-cleanup-and-boot-stacks`.
- **Change 2 (`consolidate-observability-and-graph`) — COMPLETE & ARCHIVED** (commit `fc0e817cc`):
  - Phase 2.1: 4 secrets.env files migrated (mlflow 5, lakehouse 16, graphiti 3, falkordb 1 = 25 secrets).
  - Phase 2.2: 2 blueprint port fixes (langfuse 8080→3000, graphiti 8080→8000; cognee audit was wrong — already correct).
  - Phase 2.3: opencode.json MCP command path fixed (croilar → sruth/croilar).
  - Phase 2.4: 6 pangolin.yaml files created (mlflow :5000, langfuse :3000, lakehouse :8181, graphiti :8000, falkordb :3000, cognee :8000).
  - Phase 2.5: Datadog no-op defaults flipped in 3 Pydantic Settings files (4 datadog_enabled fields True→False).
  - Phase 2.6: TypeScript comment in mcp.gateway.ts updated (datadog → logfire).
  - Phase 2.7: Spec delta written + applied to `agent-memory-systems` (4 ADDED requirements, 8 scenarios).
  - Phase 2.8: Quality gates pass (`openspec validate --strict`, `mise run lint:skills`, `bun run validate-stacks` clean for 4 migrated stacks).
  - Change 2 archived as `2026-06-27-consolidate-observability-and-graph`.
  - 20 files committed, +504/-62.

### In Progress
- **Change 3 (`centralize-agent-context-and-automate`)** — NOT YET STARTED. Anchors to `indexing-and-cognition` spec (which doesn't exist yet — must be created). Scope: P4 (cognee v1 migrate) + P5 (OpenCode agent scope/skill gate/MCP servers/agent registry) + P6 (CCC v1 v0 retirement, Cognee→Postgres+pgvector, git hooks, CI gate). Estimated 10-13 hr.

### Blocked
- **Change 3 spec anchor doesn't exist** — `openspec/specs/indexing-and-cognition/spec.md` must be created. Will need to plan the canonical shape first.

## Key Decisions
- **3 sequential openspec changes** (P0+P1, P2+P3, P4+P5+P6) for clean rollback + reviewable merges.
- **Anchors**: Change 1 → `agent-observability` · Change 2 → `agent-memory-systems` · Change 3 → `indexing-and-cognition` (to be created).
- **Observability split**: Langfuse (LLM traces) + MLflow (ML experiments) + Logfire (Python tracing); DROP Datadog entirely (docs, skills, Komodo procedures, Python code as no-op fallbacks).
- **Graph stacks**: Keep both graphiti + falkordb; make them actually work (Change 2 wires the Pangolin routes + Infisical URIs; deploy deferred to operational).
- **Logfire = OTEL collector + Logfire cloud forwarding** (the only practical self-hostable Logfire path since Pydantic doesn't publish a Logfire-server image as of 2026-06-26).
- **No `pangolin.yaml` for logfire** (SaaS-only UI at logfire.pydantic.dev).
- **Stack requirement updated** to make `pangolin.yaml` optional for SaaS-only stacks.
- **Validator regex updated** to accept both Locket-canonical + legacy Jinja forms during the migration period.
- **Cognee blueprint audit was wrong**: compose is `"8100:8000"` (host 8100 → container 8000); blueprint's `destination-port: 8000` is the container port and is CORRECT — no change needed.
- **Langfuse blueprint**: compose web service is `3001:3000`; blueprint should be `:3000` (container port).
- **Datadog Python code stays as no-op fallbacks**: only the `datadog_enabled` field defaults flip True→False; `try/except ImportError` blocks already handle the no-ddtrace case.
- **Other agents' working-tree changes intentionally excluded** from my commits: `sruth/meaisinfhoghlaim/*` (modified by other agent), `spaces/data-engineering` (untracked submodule), 12+ untracked archive directories.

## Next Steps
1. **Plan Change 3** (`centralize-agent-context-and-automate`):
   - Create `openspec/specs/indexing-and-cognition/spec.md` (the anchor for Change 3).
   - Write proposal.md covering: OpenCode agent scope/skill gate (6 of 123 skills), OpenCode MCP server registry (10 MCPs documented), agent registry (7 agents), CCC v0→v1 retirement, Cognee → Postgres+pgvector, git hooks, CI gate on index age, `croilar-devtools` MCP wiring.
2. **Implement Change 3** in 3-4 phases.
3. **Update inventory** (`infrastructure/AGENTS.md`, `infrastructure/stacks/README.md`) to add the 6 new pangolin routes (`mlflow.cianfhoghlaim.ie`, `langfuse.cianfhoghlaim.ie`, `lakehouse.cianfhoghlaim.ie`, `graphiti.cianfhoghlaim.ie`, `falkordb.cianfhoghlaim.ie`, `cognee.cianfhoghlaim.ie`).
4. **File issue for deployment** of cognee, mlflow, graphiti, falkordb, lakehouse-garage stacks (they're not booted — needs Docker daemon on bunchloch).
5. **File issue for Infisical vault seeding** (`bun run scripts/init-vault.ts` to push the 25 migrated secrets to `dev-baile`).

## Critical Context
- **OpenSpec workflow confirmed**: create `openspec/changes/<id>/{proposal.md, tasks.md, specs/<anchor>/spec.md}` · validate `--strict` · implement · archive with `--yes`.
- **OpenSpec validator**: requirement must contain SHALL or MUST; ADDED requirement must have ≥1 `#### Scenario:` block; first sentence is parsed for SHALL/MUST.
- **All Change 2 quality gates pass**:
  - ✅ `openspec validate consolidate-observability-and-graph --strict` → pass.
  - ✅ `mise run lint:skills` → 123/123 pass.
  - ✅ `bun run validate-stacks` → 4 migrated stacks show no infisical-URI warnings; 6 new pangolin files parse correctly.
  - ⚠️ `mise run py:typecheck` → pre-existing broken at mise level (mypy no target).
  - ⚠️ `mise run turbo typecheck` → 11/12 pass; only failure is `@croilar/web#typecheck` (pre-existing missing workspace packages from another agent's work, out of scope).
- **Commit hashes**:
  - `3b481e72d` — Change 1 (cleanup + logfire + drop datadog).
  - `8ff1997a1` — Change 1 inventory update.
  - `fc0e817cc` — Change 2 (consolidate observability + graph wiring).
- **Archive directories** (in `openspec/changes/archive/`):
  - `2026-06-25-oideachais-audit-phase-1-delete-dead-code/`
  - `2026-06-26-cleanup-and-boot-stacks/` (Change 1)
  - `2026-06-26-meaisinfhoghlaim-audit-phase-1-fix-typos-stale-paths-and-dead-stubs/`
  - `2026-06-26-meaisinfhoghlaim-audit-phase-2-delete-stale-duplicate-dlt-sources/`
  - `2026-06-26-meaisinfhoghlaim-audit-phase-3-fix-broken-llm-router-import-and-delete-dead-pipeline-modules/`
  - `2026-06-26-meaisinfhoghlaim-audit-phase-4-remove-duplicate-tools-pkg-and-fix-broken-relative-imports/`
  - `2026-06-26-meaisinfhoghlaim-audit-phase-5-delete-pre-split-canuint-and-duchas-images-duplicates/`
  - `2026-06-26-oideachais-audit-phase-3b-drop-domains-wrapper/`
  - `2026-06-26-oideachais-audit-phase-3c-migrate-legacy-single-sources/`
  - `2026-06-26-oideachais-audit-phase-3d-split-multi-source-files/`
  - `2026-06-26-oideachais-audit-phase-3e-split-crown-dependencies/`
  - `2026-06-26-oideachais-audit-phase-4-consolidate-legacy-dirs/`
  - `2026-06-26-oideachais-audit-phase-5-align-pyproject/`
  - `2026-06-26-tuatha-audit-phase-1-delete-broken-storage-shim/`
  - `2026-06-26-tuatha-audit-phase-2-split-leaving-cert-source-in-init/`
  - `2026-06-26-tuatha-audit-phase-3-fix-tuatha-packaging/`
  - `2026-06-26-upstream-package-monitoring/`
  - **`2026-06-27-consolidate-observability-and-graph/` (Change 2 — just created)**.

## Relevant Files
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/specs/agent-observability/spec.md` — Change 1 anchor (13 Requirements).
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/specs/agent-memory-systems/spec.md` — Change 2 anchor (2+4 = 6 Requirements after Change 2 archive).
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/specs/indexing-and-cognition/spec.md` — **TO BE CREATED** (Change 3 anchor).
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/changes/archive/2026-06-27-consolidate-observability-and-graph/` — Change 2 archive (just created).
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/changes/archive/2026-06-26-cleanup-and-boot-stacks/` — Change 1 archive.
- `/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/stacks/logfire/` — 5-file stack (compose.yaml + sidecar.yaml + compose.dev.yaml + blueprint.yaml + secrets.env + README.md + config/otelcol.yaml).
- `/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/stacks/{mlflow,lakehouse,graphiti,falkordb}/secrets.env` — Locket-canonical `infisical://dev-baile/<svc>/<key>` form.
- `/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/stacks/{mlflow,langfuse,lakehouse,graphiti,falkordb,cognee}/pangolin.yaml` — 6-label private-resource routes.
- `/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/stacks/{langfuse,graphiti}/blueprint.yaml` — port mismatches fixed (langfuse :3000, graphiti :8000).
- `/Users/cianmacandeisigh/dev/kings_college_galway/opencode.json` — line 128 MCP path corrected.
- `/Users/cianmacandeisigh/dev/kings_college_galway/sruth/oideachais/observability/unified_tracer.py` — datadog_enabled default → False.
- `/Users/cianmacandeisigh/dev/kings_college_galway/sruth/{oideachais,meaisinfhoghlaim/ocr}/config/base.py` — datadog_enabled Field default → False (2 instances each).
- `/Users/cianmacandeisigh/dev/kings_college_galway/sruth/croilar/apps/portal/src/routes/api/mcp.gateway.ts` — line 10 comment updated.
- Audit reports (in conversation context only):
  - `ses_0faadadf7ffeQVL1huuc9D4DLA` — 7-stack + prometheus audit.
  - `ses_0faadadedffeIy7Wes0mF7ckHn` — opencode.json + agent + skill scoping audit.
  - `ses_0faadade6ffetFB377vitEGVT8` — CCC v1 + Cognee indexing audit.
