# Change: 2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation

## Why

The `2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` change
(archived 2026-06-28) merged the five `sruth/<quadrant>/` quadrants
into a single `cianfhoghlaim/` Python package. The five
sruth-subagents (`oideachais`, `infrastructure`, `meaisinfhoghlaim`,
`croilar`, `tuatha`) were **not** updated by that change — they
still reference the deleted `sruth/` directories in their prompts
and `skill_filter` arrays, and `opencode.json` still contains the
`croilar-devtools` MCP server whose `command` points at
`sruth/croilar/mcp/devtools/index.ts` (a path that no longer
exists).

This breaks dispatch in two ways:

1. **`task` tool calls** that ask for `subagent_type:
   "oideachais"`, `"meaisinfhoghlaim"`, `"croilar"`, or `"tuatha"`
   hit a non-existent agent and fail.
2. **`croilar-devtools` MCP** cannot start; `mise run lint:skills`
   reports a broken-path warning; any agent that lists
   `croilar-devtools` in its `mcp` block will fail to initialize.

The subagent foundation must be rewritten to align with the v4
package layout.

## What

1. **Remove `croilar-devtools` MCP** from `opencode.json`. The MCP
   server code at `sruth/croilar/mcp/devtools/index.ts` no longer
   exists; the MCP server surface (stagehand, firecrawl, codex-cli,
   E2B) is now distributed across the `browserbase`, `firecrawl`,
   and `cocoindex-code` MCP servers. Track migration of any
   surviving croilar-devtools functionality as a follow-up GitHub
   issue.

2. **Replace the 5 sruth-subagents with 4 functional + 1 research
   subagents** in `opencode.json`:

   | Old name | New name | Skills | Routes to |
   |:--|:--|--:|:--|
   | `oideachais` | `data-platform` | 15 | `cianfhoghlaim/dlt_sources/`, `dagster_defs/`, `baml_src/`, `notebooks/`, plus DuckLake / DuckDB / MotherDuck storage decisions |
   | `infrastructure` | `infrastructure` (unchanged name) | 16 | `cianfhoghlaim/stacks/*/`, plus Komodo / Pangolin / Locket / Infisical infrastructure |
   | `meaisinfhoghlaim` | `agent-platform` | 23 | `cianfhoghlaim/agents/meaisinfhoghlaim/`, BAML, OCR, LLM routing, Langfuse, MLflow, RAGAS, Graphiti, Cognee |
   | `croilar` + `tuatha` | `frontend-apps` | 20 | `cianfhoghlaim/web/`, Convex, Babylon.js, Hono, CopilotKit, TanStack Start |
   | (new) | `research` | 11 | BrowserBase, Firecrawl, CCC, Cognee, agent-experience, company-research, event-prospecting, change-detection, search, fetch, agent-observability |

3. **Update `.agents/skills/INDEXING_AND_COGNITION.md`**:
   - Replace 8 `sruth/` path references with `cianfhoghlaim/`
     equivalents (lines 74, 80, 91, 427, 430, 435, 500, 505).
   - Replace 3 `infrastructure/stacks/` references with
     `cianfhoghlaim/stacks/` equivalents (line 144, 146, 163).
   - Replace 1 `infrastructure/scripts/cognee-graph-models/`
     reference with
     `cianfhoghlaim/cognify/cognee_integration/graph_models/`
     (line 510).
   - Remove the `croilar-devtools` row from the §3 MCP table
     (line 287).
   - Update §8.1 to list the 5 new subagent names.
   - Update §8.2 to reference `cianfhoghlaim/agents/meaisinfhoghlaim/`
     instead of `sruth/meaisinfhoghlaim/agents/`.
   - Update §8.3 to list 9 MCP servers (was 10).
   - Update §8.4 health-check expected outputs: `MCPs: 9  Agents: 7`
     and the per-subagent skill counts.
   - Append new §9 "The cianfhoghlaim v4 consolidation (2026-06-28)"
     with the directory migration map, the subagent migration
     map, the MCP migration note, and the spec-delta cross-links.
   - Bump "Last updated" to 2026-06-28.

4. **Rewrite the `build` agent prompt** in `opencode.json`:
   - Update the skill count from "123 skills" to the new totals.
   - Update the 5 subagent names in the workflow section.
   - Replace `sruth/<quadrant>/` path references with
     `cianfhoghlaim/` equivalents.
   - Drop the "Zero Absolute Namespaces in Data Pipelines" rule
     that referenced `oideachais.data_platform.*` (the
     corresponding `sruth/oideachais/data_platform/` directory
     was migrated to `cianfhoghlaim/`, but the absolute-namespace
     rule is now subsumed by the relative-import rule).

5. **Add `.gitignore` rules** for the bloat that's no longer
   tracked:
   - `cianfhoghlaim/leabharlann/` (with trailing slash — matches
     files inside, not just the dir itself)
   - `cianfhoghlaim/*_uv.lock` + `*_uv.lock` (uv.lock is regenerated
     from pyproject.toml)

## Cross-links

- **New canonical spec**: [`openspec/specs/agent-registry/spec.md`](../../specs/agent-registry/spec.md)
  defines the 5 ADDED Requirements that own this contract.
- **Superseded spec section**: The "OpenCode agent + skill + MCP
  registry" subsection of
  [`openspec/specs/indexing-and-cognition/spec.md`](../../specs/indexing-and-cognition/spec.md)
  is now a thin cross-reference into `agent-registry` (out of
  scope for this change; tracked as a separate refactor).
- **Companion change**: `2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`
  (archived) — this rewrite closes the loop on the v4 consolidation.
- **Companion research**: `openspec/research/2026-06-28-browserbase-credit-program/phase-{1a,1b,2,3}/`
  — the 43 research prompts target the new subagent routing
  (especially `data-platform` for Phase 1A and `research` for
  Phase 1B + Phase 3).

## Requirements

Defined in [`specs/agent-registry/spec.md`](specs/agent-registry/spec.md)
as **5 ADDED Requirements**.
