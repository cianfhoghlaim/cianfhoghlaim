# Tasks: 2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation

## 1. Pre-flight verification

- [x] 1.1 Confirm branch is `infra/pangolin-newt-infisical-upgrade-2026-06-28` and working tree is clean (modulo the 4 modifications from this change + 7 untracked items from prior sessions).
- [x] 1.2 Confirm 8 `sruth/` path refs and 3 `infrastructure/stacks/` path refs exist in `INDEXING_AND_COGNITION.md`.
- [x] 1.3 Confirm `sruth/croilar/mcp/devtools/index.ts` no longer exists (grep returns 0 hits).
- [x] 1.4 Confirm all 71 skill names referenced by the 5 old subagents resolve to existing directories under `.agents/skills/`.
- [x] 1.5 Confirm `opencode.json` is valid JSON.

## 2. `opencode.json` edits

- [x] 2.1 Remove the `croilar-devtools` MCP entry (was lines 123-134).
- [x] 2.2 Rewrite the `build` agent prompt: update skill count, update 5 subagent names, replace `sruth/<quadrant>/` path refs with `cianfhoghlaim/` equivalents, drop the `oideachais.data_platform.*` absolute-namespace rule.
- [x] 2.3 Replace the `oideachais` subagent → `data-platform`: 15 skills, new prompt referencing `cianfhoghlaim/dlt_sources/`, `dagster_defs/`, `baml_src/`, `notebooks/`.
- [x] 2.4 Update the `infrastructure` subagent prompt: 15 skills (one skill — `dagger` — was already superseded by `dagger-pipelines` and was dropped in the new infra subagent).
- [x] 2.5 Replace the `meaisinfhoghlaim` subagent → `agent-platform`: 23 skills, new prompt referencing `cianfhoghlaim/agents/meaisinfhoghlaim/`.
- [x] 2.6 Merge `croilar` (12 skills) + `tuatha` (12 skills) → `frontend-apps`: 20 unique skills, new prompt referencing `cianfhoghlaim/web/`, Convex, Babylon.js, Hono.
- [x] 2.7 Add the new `research` subagent: 11 skills (final count after dropping `indexing-and-cognition` and `competitor-analysis` from the filter).
- [x] 2.8 Update MiniMax-M3 model limits from 200K/32K to 1M/500K.
- [x] 2.9 Validate JSON: `MCPs: 9  Agents: 7`; BrowserBase preserved as `type: local` (the working config).

## 3. `.agents/skills/INDEXING_AND_COGNITION.md` edits

- [x] 3.1 Fix the 8 `sruth/` path refs → `cianfhoghlaim/` equivalents.
- [x] 3.2 Fix the 3 `infrastructure/stacks/` path refs → `cianfhoghlaim/stacks/` equivalents.
- [x] 3.3 Fix the 1 `infrastructure/scripts/cognee-graph-models/` ref → `cianfhoghlaim/cognify/cognee_integration/graph_models/`.
- [x] 3.4 Remove the `croilar-devtools` row from the §3 MCP table.
- [x] 3.5 Update §8.1 to list the 5 new subagent names.
- [x] 3.6 Update §8.2 to reference `cianfhoghlaim/agents/meaisinfhoghlaim/`.
- [x] 3.7 Update §8.3 to "The 9 MCP servers".
- [x] 3.8 Update §8.4 health-check expected outputs: `MCPs: 9  Agents: 7`, per-subagent counts `build=0, plan=0, data-platform=15, infrastructure=15, agent-platform=23, frontend-apps=20, research=11`.
- [x] 3.9 Append new §9 "The cianfhoghlaim v4 consolidation (2026-06-28)".
- [x] 3.10 Bump "Last updated" to 2026-06-28.
- [x] 3.11 Verify body has no stale path refs (23 matches are all in §9's intentional migration table).

## 4. `.gitignore` edits

- [x] 4.1 Add `cianfhoghlaim/leabharlann/` rule (with trailing slash).
- [x] 4.2 Add `cianfhoghlaim/*_uv.lock` and `*_uv.lock` rules.

## 5. Spec deltas (canonical `openspec/specs/agent-registry/`)

- [x] 5.1 Create `openspec/specs/agent-registry/spec.md` with 5 ADDED Requirements.

## 6. Spec deltas (this change's `specs/agent-registry/spec.md`)

- [x] 6.1 Create the change-delta mirror in `openspec/changes/2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation/specs/agent-registry/spec.md`.

## 7. Validation gate

- [x] 7.1 `python3 -m json.tool opencode.json` exits 0.
- [x] 7.2 MCPs=9, Agents=7 (build, plan, data-platform, infrastructure, agent-platform, frontend-apps, research).
- [x] 7.3 BrowserBase preserved as `type: local` (the working config from infra branch).
- [x] 7.4 `openspec validate 2026-06-28-rewrite-subagent-foundation-for-cianfhoghlaim-consolidation --strict` exits 0.
- [x] 7.5 `git check-ignore -v cianfhoghlaim/leabharlann/foo.pdf` matches; `git check-ignore -v cianfhoghlaim/_oideachais_uv.lock` matches.

## 8. Follow-up issues

- [ ] 8.1 Open a GitHub issue: "Migrate croilar-devtools MCP server code to `cianfhoghlaim/agents/api/_croilar_convex/devtools.ts`".
- [ ] 8.2 Open a GitHub issue: "Migrate 100+ `sruth/<quadrant>/` path references in 40+ `.agents/skills/*/SKILL.md` files" (out of scope, tracked by `docs-skills-consolidation-pipeline`).

## 9. Execution sequence

1. Pre-flight (§1).
2. `opencode.json` edits (§2) — all in one commit candidate.
3. `INDEXING_AND_COGNITION.md` edits (§3).
4. `.gitignore` edits (§4).
5. Canonical spec creation (§5) + change-delta spec creation (§6).
6. Validation gate (§7).
7. Commit + push to `origin/infra/pangolin-newt-infisical-upgrade-2026-06-28` (new ref since none exists yet).
8. **STOP** — user restarts opencode; `research` subagent becomes dispatchable.

## 10. Recovery: previous bad push to q3-2026

- [x] 10.1 Force-pushed `fc7658c67:q3-2026-oideachais-consolidation --force-with-lease` to revert the q3 branch to its pre-push state.
- [x] 10.2 Confirmed `origin/q3-2026-oideachais-consolidation` is back at `fc7658c67`.
