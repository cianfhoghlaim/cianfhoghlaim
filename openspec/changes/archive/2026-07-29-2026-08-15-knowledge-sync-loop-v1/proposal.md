# 2026-08-15-knowledge-sync-loop-v1

## Why

The cianfhoghlaim repo has **8 knowledge surfaces** that need to stay
in sync:

1. **openspec changes** (71 specs, 14 pending, 303 archived)
2. **openspec specs** (71 capability specs)
3. **agent skills** (57 SKILL.md files in `.agents/skills/`)
4. **MCP servers** (14 servers wired in `opencode.json`)
5. **Dagster assets** (~833 across the 5-layer defs/ tree)
6. **CCC chunks** (257,957 / 8,845 files via CocoIndex Code)
7. **Cognee docs** (1,743 .md files / 7 typed clusters)
8. **agent definitions** (12-agent fleet + 8 NCCA subject specialists)

Today, **every sync between these surfaces is manual**:
- `bun run ccc:index` (CCC reindex — not auto-triggered)
- `bash scripts/cognee_ingest.py docs/01-cognee docs-cognee` (cognify — not auto-triggered)
- `bash .agents/skills/lint-skills.sh` (skill lint — only runs in CI)
- No MCP health check at all
- No openspec → CCC link
- No skill → CCC link

Drift accumulates silently. Examples from the Week 4 audit:
- **6 source files** in `cocoindex/` still reference `pathlib.Path("sruth/cianfhoghlaim/cocoindex_flows")` (the pre-v7 path)
- The 20th CCC concept guide should be `openspec-archive-search` (surfaces all 14 pending + 303 archived changes) but doesn't exist yet
- The 9 Cognee clusters should be (7 existing + 2 new for `openspec_changes` + `openspec_specs` + `agent_skills`) but only the 7 docs/ ones are populated
- The 14 MCP servers have no health check (an offline `infisical-mcp` would silently break the litellm → langfuse → agent loop)

This change establishes the **5-layer Pull-based sync architecture** that
keeps all 8 surfaces in sync via 6 `mise run sync:*` tasks + 1
orchestrator. The user's choice (per the planning question) is:
**Pull-based** (not Dagster sensors, not GitHub Actions) + **both
retroactive cleanup + forward prevention**.

## What changes

### 1. The 5 sync layers

| Layer | Trigger | Tool | Output | Synced surface |
|:--|:--|:--|:--|:--|
| 1. **Path** | `mise run sync:paths` | bash + grep (extended `drift-audit` from Week 4) | `stedding/sync-reports/paths-{date}.md` | All 8 surfaces (path references) |
| 2. **Index** | `mise run sync:ccc` | `bun run ccc:index` + the 20th concept guide | `.cocoindex_code/` (incremental) | Code + openspec changes + skills |
| 3. **Graph** | `mise run sync:cognee` | 4 Cognee ingestion scripts | 10 Cognee clusters (7 existing + 3 new) | Docs + openspec + skills |
| 4. **Sync** | `mise run sync:skills` | `lint-skills.sh` + `validate_skill_references.py` | `stedding/sync-reports/skills-{date}.md` | Skill frontmatter + path refs |
| 5. **Telemetry** | `mise run sync:mcp` | 14 `bunx`/`uvx` pings with 5s timeout | `stedding/sync-reports/mcp-{date}.md` | All 14 MCP server health |
| **Orchestrator** | `mise run sync:all` | runs 1-5 in sequence | `stedding/sync-reports/all-{date}.md` (single summary) | All 5 layers |

### 2. The 6 mise tasks

```toml
[tasks."sync:paths"]     # Layer 1
[tasks."sync:ccc"]      # Layer 2
[tasks."sync:cognee"]   # Layer 3
[tasks."sync:skills"]   # Layer 4
[tasks."sync:mcp"]      # Layer 5
[tasks."sync:all"]      # Orchestrator
```

### 3. The 5 new scripts (3 of them Pull-based helpers)

| Script | Purpose | New / modified |
|:--|:--|:--|
| `scripts/sync_openspec_to_ccc.py` | Appends the 20th concept guide (`openspec-archive-search`) to `.cocoindex_code/guides.yml` | NEW |
| `scripts/validate_skill_references.py` | Walks every SKILL.md + grep-checks the `description:` field + body for path references that don't exist on disk | NEW |
| `scripts/sync_report.py` | Generates the per-layer summary at `stedding/sync-reports/` | NEW |
| `scripts/bring-up-smoke-test.sh` | Added a Step 6 = `mise run sync:all` | MODIFIED |
| `scripts/week4-smoke-test.sh` | Added a Gate 6 = `mise run sync:paths` (subset of sync:all for fast CI) | MODIFIED |

### 4. The 2 new Cognee ingestion scripts + 3 new clusters

| Script | Cluster | Source | Cognee dataset name |
|:--|:--|:--|:--|
| `scripts/cognee_ingest_openspec.py` | `openspec_changes` | `openspec/changes/**/*.md` (excludes archive/ for size) | `openspec_changes` |
| `scripts/cognee_ingest_openspec.py` (same) | `openspec_specs` | `openspec/specs/**/*.md` | `openspec_specs` |
| `scripts/cognee_ingest_skills.py` | `agent_skills` | `.agents/skills/**/SKILL.md` | `agent_skills` |

### 5. The 20th CCC concept guide

Append to `.cocoindex_code/guides.yml`:

```yaml
- title: "openspec archive search"
  description: |
    How to find any openspec change (pending or archived) by keyword,
    spec, or implementation status. Use when the user asks "what
    changes have we made for X", "is there a spec for Y", or "where
    is the BIEP v3 Ireland full coverage spec". 14 pending + 303
    archived.
  files:
    - openspec/changes/2026-08-15-knowledge-sync-loop-v1/proposal.md
    - openspec/changes/2026-08-04-skill-and-mcp-migration-v1/proposal.md
    - openspec/specs/knowledge-sync-loop/spec.md
    - openspec/specs/agent-platform-cluster/spec.md
    - openspec/AGENTS.md
  tags: [openspec, changes, specs, archive, knowledge]
  domain: "00-openspec"
```

### 6. Retroactive cleanup — the 6 source files

The Week 4 `drift-audit` found 6 source files in `cocoindex/` + 1 in
`tests_pkg_temp/` with `sruth/cianfhoghlaim/cocoindex_flows` refs.
The new `sync:paths` task includes a one-time bulk sed:

- `tests_pkg_temp/_oideachais/test_canuint_alignment.py` (1 ref) — file in the deprecated `tests_pkg_temp/` dir; mark for deletion in a follow-up
- `cocoindex/knowledge_graph/multihop_search.py` (1 ref) — sed `sruth/cianfhoghlaim/cocoindex_flows` → `cocoindex/codebase_indexing`
- `cocoindex/_shared/reranker.py` (1 ref) — same sed
- `cocoindex/_shared/repo_type_detector.py` (1 ref) — same sed
- `cocoindex/infrastructure/arch_doc_cache.py` (1 ref) — same sed
- `cocoindex/infrastructure/cocoindex_v1_conformance.py` (1 ref) — same sed

The `sync:paths` task runs the sed + verifies via `grep -c "sruth/" $file`
that the count drops to 0.

### 7. Forward prevention

The new `drift-audit` (extended from Week 4) now also greps for
`sruth/` as a 6th pattern. The CI gate
(`.github/workflows/ci.yaml` → `lint:skills` step) runs `drift-audit`
on every PR; any new `sruth/` ref fails the gate.

### 8. The 1 new Dagster asset

`orchestration/defs/sync_assets.py` — `sync_health` asset that
materializes on a `0 */4 * * *` cron (every 4 hours) and via a sensor
that fires on new `stedding/sync-reports/all-*.md` files. The asset
reads the latest report + emits Dagster metadata (paths sync time,
ccc chunk count, cognee cluster count, skill pass rate, mcp server
health).

### 9. The 1 new marimo notebook

`notebooks/24_deployment_control_panel.py` — the canonical sync
health + model registry + schema + stacks dashboard. Consumes
`stedding/sync-reports/all-{date}.md` and surfaces the 5 sync layer
statuses + the 14 MCP server health + the 70+ model names + the 472
CocoIndex Apps + the 88+ stacks in one marimo dashboard.

### 10. The 1 new skill

`.agents/skills/knowledge-sync-loop/SKILL.md` — documents the 5 layers
+ the 3 feedback loops + the 6 sync tasks + the 2 new Cognee
clusters. Auto-loaded by any agent that runs `sync:*` tasks.

## Dependencies

```yaml
Blocked by: none (this is the foundation; Change B below builds on it)
Blocked by (soft): 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `mise run sync:all` runs cleanly + produces `stedding/sync-reports/all-{date}.md` with all 5 layer statuses
- `mise run drift-audit` reports 0 `sruth/` refs in source files
- `bun run ccc:index` succeeds + the 20th concept guide is loaded
- `cognee-mcp` returns the 10 typed clusters (7 existing + 3 new)
- `mise run sync:mcp` reports all 14 MCP servers with health status
- `bash scripts/bring-up-smoke-test.sh` reports "All 6 bring-up steps work" (the new Step 6 = sync:all)
- `openspec validate 2026-08-15-knowledge-sync-loop-v1 --strict` passes

## Cross-references

- `openspec/specs/knowledge-sync-loop/spec.md` (the new spec)
- `.agents/skills/INDEXING_AND_COGNITION.md` (the ccc + cognee setup)
- `.agents/skills/ccc/SKILL.md` (the ccc skill)
- `openspec/AGENTS.md` (the canonical openspec workflow)
- `openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/` (Change B — consumes the sync reports)
- `scripts/drift-audit.sh` (the Week 4 task that this change extends)
- `scripts/bring-up-smoke-test.sh` (the canonical bring-up verification)
- `stedding/` (the canonical scratch dir for sync reports)