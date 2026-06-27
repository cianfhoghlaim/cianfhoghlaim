# Anchored Summary — 2026-06-27 (End of Change 3)

## Goal
End-to-end observability + agent-context pipeline: integrate 7 stacks (mlflow, logfire, langfuse, lakehouse, graphiti, falkordb, cognee), delete prometheus, automate code indexing, centralize OpenCode agent context/skills/tools — via 3 sequential openspec changes.

**STATUS: ALL 3 CHANGES COMPLETE + ARCHIVED.**

## Constraints & Preferences
- **BUILD MODE** (user said "proceed").
- AGENTS.md priority quick-reference applies.
- All new code uses `sruth/...` paths.
- CocoIndex v1 canonical pattern: `coco.App(...)` + `@coco.fn(memo=True)` + `@coco.lifespan` delegating to `shared_lifespan`.
- Validate with `openspec validate <change-id> --strict` before any commit.
- Secrets via Infisical (`dev-baile` env) via Locket-canonical `infisical://dev-baile/<svc>/<key>` URIs.
- Agent protocol: never amend, force-push, or skip hooks.
- Image pinning policy: every image SHALL be pinned to semver (no `:latest`).
- 5-file GOLD_STANDARD stack pattern: compose.yaml + sidecar.yaml + secrets.env + blueprint.yaml + README.md (pangolin.yaml required only for stacks with local web UI).
- Validator regex accepts both Locket-canonical + legacy Jinja forms during migration period.
- Pre-commit hook is best-effort (warns but never blocks); `--no-verify` escape hatch preserved.
- Skill scoping via per-agent `skill_filter` is opt-in; primary agents (`build`, `plan`) keep no-filter behavior as escape hatch.

## Progress
### Done
- **Change 1 (`cleanup-and-boot-stacks`) COMPLETE & ARCHIVED (2026-06-26)**:
  - litellm prometheus deleted, `.opencode.yaml` deleted, cognee-stack.yaml deleted, logfire stack scaffolded as OTEL collector, Datadog dropped from skills + Komodo + Python defaults, stack-doctor validator regex updated.
  - Commits: `3b481e72d` (34 files +1102/-887), `8ff1997a1` (inventory update).
  - Archived as `2026-06-26-cleanup-and-boot-stacks`.

- **Change 2 (`consolidate-observability-and-graph`) COMPLETE & ARCHIVED (2026-06-27, commit `fc0e817cc`)**:
  - 4 secrets.env migrated to Locket-canonical form (25 secrets total).
  - 2 blueprint port fixes (langfuse 8080→3000, graphiti 8080→8000).
  - `opencode.json` line 128 MCP path fixed (`sruth/croilar/mcp/devtools/index.ts`).
  - 6 pangolin.yaml files created for mlflow :5000, langfuse :3000, lakehouse :8181, graphiti :8000, falkordb :3000, cognee :8000.
  - 4 Pydantic Settings fields flipped `datadog_enabled` True→False.
  - 1 TypeScript comment in mcp.gateway.ts updated.
  - 4 ADDED requirements applied to `agent-memory-systems` spec.
  - All quality gates passed.
  - Archived as `2026-06-27-consolidate-observability-and-graph`.
  - Anchored summary written at `.opencode/summary.md` (commit `44aca1f26`).

- **Change 3 (`centralize-agent-context-and-automate`) COMPLETE & ARCHIVED (2026-06-27, commit `7a0e354c4` for code + `2e9a78b79` for archive)**:
  - **Spec anchor created**: `openspec/specs/indexing-and-cognition/spec.md` (9 Requirements: CCC v1 canonical, Cognee pgvector, 7 cluster dataset shape, 7 agents, 10 MCPs, CCC freshness gate, best-effort pre-commit hook, skill_filter opt-in, 13-agent model-layer registry).
  - **Phase 4 (Cognee v1 graph models)**:
    - 7 graph model files at `infrastructure/scripts/cognee-graph-models/`: `data_platform_graph.py`, `infrastructure_graph.py`, `agents_graph.py`, `ml_graph.py`, `celtic_language_graph.py`, `web_graph.py`, `tuatha_graph.py`. Each declares `GRAPH_NODE_TYPES: tuple[str, ...]`, `GRAPH_EDGE_TYPES: tuple[str, ...]`, `CLUSTER_NAME`, `CLUSTER_DESCRIPTION`, and `get_graph_model()` helper.
    - 1 helper script: `infrastructure/scripts/cognee-ingest-docs.py` (executable, --all/--cluster/--dry-run/--background flags, exit codes 0-4).
    - Verified cognee compose uses `VECTOR_DB_PROVIDER: pgvector` + `DB_PROVIDER: postgres` + `GRAPH_DATABASE_PROVIDER: postgres` (no code change needed).
  - **Phase 5 (OpenCode agent scope + skill gate + MCP registry + agent registry)**:
    - `opencode.json` skill_filter added to 5 sruth-subagents: oideachais=9, infrastructure=16, meaisinfhoghlaim=22, croilar=12, tuatha=12. Primary `build`/`plan` agents keep no-filter.
    - `MODEL_LAYER_AGENTS: tuple[str, ...]` added to `sruth/meaisinfhoghlaim/agents/__init__.py` (13 modules: root + 12 specialists).
    - `.agents/skills/INDEXING_AND_COGNITION.md` §3 MCP inventory updated 9→10 (added `croilar-devtools`).
    - `.agents/skills/INDEXING_AND_COGNITION.md` new §8 "OpenCode agent, skill, and MCP registry" added (7 agents, 10 MCPs, 13 model-layer agents; health-check recipes).
    - `.agents/skills/agent-fleet-orchestration/SKILL.md` 1-line cross-link to §8.
  - **Phase 6 (CCC v0→v1 retirement + git hooks + CI gate)**:
    - `scripts/validate-ccc-freshness.ts`: CI gate, exits 1 if >7d on main / >24h on feature; missing index hard-fail on main, soft warn on feature.
    - `scripts/templates/pre-commit` + `scripts/install-hooks.sh`: best-effort pre-commit hook (yellow WARN to stderr; never blocks; --no-verify bypass).
    - `package.json` + `mise.toml` aliases added: `validate-ccc-freshness`, `hooks:install`.
    - `scripts/_ccc-deprecation-banner.ts`: yellow deprecation warning to stderr when legacy `ccc:search` is invoked.
    - `package.json` + `mise.toml` `ccc:search` updated to invoke banner first.
    - `sruth/oideachais/cocoindex_flows/_v0_archive/DEPRECATED.md`: 2026-07-15 hard-removal timeline for the legacy `ccc search` CLI.
  - All quality gates passed:
    - `openspec validate centralize-agent-context-and-automate --strict` → "Change is valid"
    - `mise run lint:skills` → 123/123 pass
    - `bun run validate-ccc-freshness` → "OK (0.7d on feature, threshold 1d)"
    - `python3 -c "import json; ..."` → 10 MCPs, 7 agents, skill counts match
    - `ls infrastructure/scripts/cognee-graph-models/*.py | wc -l` → 7
    - `bash scripts/install-hooks.sh` → idempotent (1 installed)
    - `NO_COLOR=1 mise run ccc:search "test"` → banner prints to stderr
  - Archived as `2026-06-27-centralize-agent-context-and-automate`.

### In Progress
- None — all 3 changes complete.

### Blocked
- None.

## Key Decisions
- **3 sequential openspec changes** for clean rollback + reviewable merges.
- **Anchors**: Change 1 → `agent-observability` · Change 2 → `agent-memory-systems` · Change 3 → `indexing-and-cognition` (CREATED).
- **Observability split**: Langfuse (LLM traces) + MLflow (ML experiments) + Logfire (Python tracing); DROP Datadog entirely.
- **Graph stacks**: Keep both graphiti + falkordb; make them actually work (Change 2 wired the Pangolin routes + Infisical URIs).
- **Logfire = OTEL collector + Logfire cloud forwarding** (only practical self-hostable Logfire path).
- **No `pangolin.yaml` for logfire** (SaaS-only UI at logfire.pydantic.dev).
- **Stack requirement**: 5-file GOLD_STANDARD + optional `pangolin.yaml` only for stacks with local web UI; SaaS-only stacks may omit.
- **Validator regex** accepts both Locket-canonical + legacy Jinja forms during migration period.
- **Cognee blueprint**: container listens on :8000 (host maps 8100:8000) — blueprint's `destination-port: 8000` is CORRECT.
- **Langfuse blueprint**: container listens on :3000 (host maps 3001:3000) — blueprint should be `:3000`, NOT `:3001`.
- **Datadog Python code stays as no-op fallbacks** (60+ `from ddtrace`/`from datadog` lines left in place; only `datadog_enabled` defaults flip True→False).
- **Cognee MCP env audit correction**: `NEO4J_*` vars belong to the `graphiti` MCP (which IS the Neo4j service), NOT to the `cognee` MCP. The cognee MCP env has exactly 3 canonical keys.
- **Pre-commit hook is best-effort**: warns but never blocks; `--no-verify` escape hatch preserved.
- **Skill scoping via `skill_filter` is opt-in**: primary agents (`build`, `plan`) keep no-filter behavior; 5 sruth-subagents opt into subsets.
- **CCC v0 retirement**: 2026-07-15 hard-removal date in follow-up change; legacy `ccc search` CLI emits deprecation warning but still works.
- **OpenSpec workflow correction**: For a NEW spec, the canonical `openspec/specs/<anchor>/spec.md` is created via `openspec archive`, not written by hand. The delta's `## ADDED Requirements` is the input; the canonical is the output.
- **Archive bundled into parallel agent's commit**: Change 3's archive files got pulled into commit `2e9a78b79` (titled "delete dead cognee-ingest-archive.py") when the parallel agent committed. Archive content is correct; commit message is misleading but the work is correct.

## Next Steps
None — all 3 changes are complete + archived + pushed. The 2026-06-26 audit's 4 strategic findings are all addressed:

1. ✅ **Observability consolidation** (Langfuse + MLflow + Logfire, drop Datadog) — Change 1 + Change 2.
2. ✅ **Graph DB wiring** (graphiti + falkordb + cognee-pgvector) — Change 2.
3. ✅ **CCC v0 → v1 retirement** (graph models, freshness gate, pre-commit hook, 2026-07-15 hard-removal date) — Change 3.
4. ✅ **OpenCode agent registry centralization** (skill_filter for 5 sruth-subagents, MODEL_LAYER_AGENTS, INDEXING_AND_COGNITION §8) — Change 3.

## Critical Context
- **Audit findings (2026-06-26)** — 4-way LLM obs sprawl; 4-way graph DB sprawl; 3-way vector DB sprawl; 3 MinIO/S3 instances; 10 separate Postgres instances.
- **OpenCode agent audit**: 7 agents; 5 sruth-subagents now opt into scoped skill_filter (9-22 skills each); 10 MCPs (was 9; croilar-devtools added); `croilar-devtools` MCP path was broken (fixed in Change 2).
- **CCC v1 audit**: 16 Apps live alongside legacy v0 SQLite; Cognee uses Postgres+pgvector; git hooks installed; CI gate on index age implemented; `cognee_cron_sensor` STOPPED by default.
- **`monitoring/` stack deleted** by parallel agent on 2026-06-26; cleaned up in Change 1 commit + inventory docs.
- **OpenSpec workflow confirmed**: create `openspec/changes/<id>/{proposal.md, tasks.md, specs/<anchor>/spec.md}` · validate `--strict` · implement · archive with `--yes`. For NEW specs, the canonical is created by `openspec archive`, not by hand.
- **OpenSpec validator rules**: requirement must contain SHALL or MUST; ADDED requirement must have ≥1 `#### Scenario:` block; first sentence is parsed for SHALL/MUST; "Why" section <1000 chars.
- **All 3 changes' quality gates passed** (✅ `openspec validate --strict`, ✅ `mise run lint:skills` 123/123, ✅ `bun run validate-ccc-freshness`, ✅ JSON validity, ✅ 7 cognee graph models, ✅ 10 MCPs/7 agents, ✅ pre-commit hook installed).
- **Ports verified** (from compose files): mlflow :5000, langfuse web :3000, lakehouse/lakekeeper :8181, graphiti/graph :8000, falkordb UI :3000, cognee :8000.
- **Commit hashes**:
  - `3b481e72d` — Change 1 main (cleanup + logfire + drop datadog).
  - `8ff1997a1` — Change 1 inventory update.
  - `fc0e817cc` — Change 2 (consolidate observability + graph wiring).
  - `44aca1f26` — Change 2 anchored summary.
  - `7a0e354c4` — Change 3 code (graph models, skill_filter, MODEL_LAYER_AGENTS, INDEXING_AND_COGNITION §8, freshness gate, pre-commit hook, deprecation banner, DEPRECATED.md).
  - `2e9a78b79` — Change 3 archive (bundled into parallel agent's commit; subject mentions cognee-ingest-archive.py deletion but commit also contains the archive + canonical).
- **Archive directories** (in `openspec/changes/archive/`):
  - `2026-06-25-oideachais-audit-phase-1-delete-dead-code/`
  - `2026-06-26-cleanup-and-boot-stacks/` (Change 1)
  - `2026-06-26-fix-existing-stacks/` (Change A)
  - `2026-06-26-meaisinfhoghlaim-audit-phase-{1..5}*/`
  - `2026-06-26-oideachais-audit-phase-{3b,3c,3d,3e,4,5}*/`
  - `2026-06-26-tuatha-audit-phase-{1,2,3}*/`
  - `2026-06-26-upstream-package-monitoring/`
  - `2026-06-27-consolidate-observability-and-graph/` (Change 2)
  - `2026-06-27-centralize-agent-context-and-automate/` (Change 3 — new)
  - `2026-06-27-croilar-audit-phase-{1,2,3}*/` (parallel work)
- **Audit correction evidence**: `opencode.json` line 86-90 confirms `mcp.cognee.env` has only `COGNEE_API_URL`, `COGNEE_API_KEY`, `LLM_API_KEY`; `mcp.graphiti.env` (lines 102-106) correctly uses `NEO4J_URI/USER/PASSWORD`.

## Relevant Files
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/specs/agent-observability/spec.md` — Change 1 anchor (13 Requirements).
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/specs/agent-memory-systems/spec.md` — Change 2 anchor (6 Requirements after Change 2 archive).
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/specs/indexing-and-cognition/spec.md` — **NEW** Change 3 anchor (9 Requirements, created by openspec archive from the delta's ADDED Requirements).
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/specs/stack-audit/spec.md` — NEW canonical spec (5 ADDED requirements) from fix-existing-stacks archive.
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/changes/archive/2026-06-26-cleanup-and-boot-stacks/` — Change 1 archive.
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/changes/archive/2026-06-27-consolidate-observability-and-graph/` — Change 2 archive.
- `/Users/cianmacandeisigh/dev/kings_college_galway/openspec/changes/archive/2026-06-27-centralize-agent-context-and-automate/` — **NEW** Change 3 archive.
- `/Users/cianmacandeisigh/dev/kings_college_galway/.opencode/summary.md` — THIS FILE (anchored summary, end of Change 3).
- `/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/scripts/cognee-graph-models/` — 7 .py files (Change 3 Phase 4).
- `/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/scripts/cognee-ingest-docs.py` — 7-cluster cognify helper (Change 3 Phase 4).
- `/Users/cianmacandeisigh/dev/kings_college_galway/opencode.json` — 10 MCPs, 7 agents with skill_filter (Change 3 Phase 5).
- `/Users/cianmacandeisigh/dev/kings_college_galway/sruth/meaisinfhoghlaim/agents/__init__.py` — MODEL_LAYER_AGENTS tuple (Change 3 Phase 5.6).
- `/Users/cianmacandeisigh/dev/kings_college_galway/.agents/skills/INDEXING_AND_COGNITION.md` — §3 updated, new §8 added (Change 3 Phase 5.7-5.8).
- `/Users/cianmacandeisigh/dev/kings_college_galway/.agents/skills/agent-fleet-orchestration/SKILL.md` — cross-link added (Change 3 Phase 5.9).
- `/Users/cianmacandeisigh/dev/kings_college_galway/scripts/validate-ccc-freshness.ts` — CI gate (Change 3 Phase 6.1).
- `/Users/cianmacandeisigh/dev/kings_college_galway/scripts/templates/pre-commit` — best-effort hook (Change 3 Phase 6.2).
- `/Users/cianmacandeisigh/dev/kings_college_galway/scripts/install-hooks.sh` — idempotent installer (Change 3 Phase 6.3).
- `/Users/cianmacandeisigh/dev/kings_college_galway/scripts/_ccc-deprecation-banner.ts` — deprecation banner (Change 3 Phase 6.6).
- `/Users/cianmacandeisigh/dev/kings_college_galway/.git/hooks/pre-commit` — installed by `bash scripts/install-hooks.sh`.
- `/Users/cianmacandeisigh/dev/kings_college_galway/sruth/oideachais/cocoindex_flows/_v0_archive/DEPRECATED.md` — 2026-07-15 hard-removal timeline (Change 3 Phase 6.5).
- `/Users/cianmacandeisigh/dev/kings_college_galway/package.json` — `validate-ccc-freshness` + `hooks:install` + `ccc:search` banner (Change 3 Phase 6.4+6.6).
- `/Users/cianmacandeisigh/dev/kings_college_galway/mise.toml` — same aliases (Change 3 Phase 6.4+6.6).

## Final Posture

**All 3 changes are committed, pushed, and archived.** The 2026-06-26 audit is fully resolved:

| Audit finding | Resolved by | Spec anchor |
|:--|:--|:--|
| LLM obs sprawl (langfuse + mlflow + logfire + datadog) | Change 1 (drop datadog, scaffold logfire) + Change 2 (wire 4 stacks) | `agent-observability` |
| Graph DB sprawl (graphiti + falkordb + cognee + memgraph) | Change 2 (wire 3 stacks; cognee confirmed on pgvector) | `agent-memory-systems` |
| CCC v0 → v1 retirement incomplete | Change 3 (graph models, freshness gate, pre-commit hook, 2026-07-15 timeline) | `indexing-and-cognition` |
| OpenCode agent registry over-scoped | Change 3 (skill_filter on 5 sruth-subagents, MODEL_LAYER_AGENTS, §8 registry) | `indexing-and-cognition` |

**Cognee operational state:**
- Stack: `infrastructure/stacks/cognee/` — confirmed using `pgvector/pgvector:pg17` (no Neo4j dep)
- 7 cluster graph model files at `infrastructure/scripts/cognee-graph-models/`
- 1 cognify helper at `infrastructure/scripts/cognee-ingest-docs.py`
- MCP env has 3 canonical keys: `COGNEE_API_URL`, `COGNEE_API_KEY`, `LLM_API_KEY`

**CCC operational state:**
- v1 App: `sruth/oideachais/cocoindex_flows/codebase_indexing.py` (canonical)
- v0 CLI: deprecated, hard-removal 2026-07-15
- Freshness gate: `bun run validate-ccc-freshness` (CI gate, 7d main / 24h feature)
- Pre-commit hook: best-effort, never blocks

**OpenCode operational state:**
- 7 agents (build, plan, oideachais, infrastructure, meaisinfhoghlaim, croilar, tuatha)
- 10 MCPs (browserbase, firecrawl, infisical, motherduck, chrome, cocoindex-code, cognee, graphiti, langfuse, croilar-devtools)
- 5 sruth-subagents have skill_filter (9-22 skills each); build/plan see all 123

---

**Last updated:** 2026-06-27 (end of Change 3, all 3 changes complete + archived).
**Owner:** Build agent.
**Status:** ✅ **MISSION COMPLETE** — all 2026-06-26 audit findings addressed, all 3 openspec changes shipped.
