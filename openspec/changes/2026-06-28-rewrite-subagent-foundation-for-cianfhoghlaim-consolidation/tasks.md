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

## 11. `skill_filter` audit pass (2026-06-29)

Follow-up discovered after §7 validation: the per-subagent
`skill_filter` arrays created in §2 referenced 35 legacy skill
names that no longer exist as top-level directories under
`.agents/skills/` (e.g. `oideachais-pipeline`, `kcg-pangolin-stack`,
`agent-fleet-orchestration`, `document-intelligence`, `tuatha-mmo`,
`pent-elemental-cosmology`, `croilar-stream-registry`,
`agent-experience`, `company-research`, `event-prospecting`,
`search`, `fetch`, `kubernetes`, `docker-compose`, etc.). Task 1.4
was ticked as "pass" but the actual `opencode.json` array entries
were stale. The audit pass replaces every entry with a current
top-level skill that resolves to an existing directory.

- [x] 11.1 Enumerate the 53 top-level skill directories under
  `.agents/skills/` (script: `os.listdir(".agents/skills")` filter
  to dirs with `SKILL.md` or known subskill bundles).
- [x] 11.2 Audit each of the 5 `skill_filter` arrays; identify
  missing/non-resolvable entries: data-platform=5 missing,
  infrastructure=10 missing, agent-platform=9 missing,
  frontend-apps=6 missing + 1 duplicate
  (`agentic-frontend-frameworks` listed twice), research=5 missing.
- [x] 11.3 Replace `data-platform` filter: removed `oideachais-pipeline`,
  `oideachais-storage`, `oideachais-cocoindex-v1`,
  `celtic-ocr-evaluation`, `embedding-pipeline`; added `dlthub`,
  `ibis`, `marimo`, `langfuse`, `mlflow`. Final 15 entries, all
  resolve to existing top-level directories.
- [x] 11.4 Replace `infrastructure` filter: removed `stack-ops`,
  `infrastructure-stacks`, `kcg-pangolin-stack`, `kcg-locket-sidecar`,
  `kcg-infrastructure-audit`, `kcg-bunchloch`, `kcg-convergence`,
  `kcg-deploy-runbooks`, `docker-compose`, `kubernetes`; added
  `dagger`, `cloudflare`, `dlthub`, `cocoindex`, `langfuse`, `mlflow`,
  `risingwave`, `olake`, `effect-ts`. Final 15 entries, all resolve.
- [x] 11.5 Replace `agent-platform` filter: removed
  `document-intelligence`, `celtic-language-ai`, `irish-llm-on-device`,
  `agent-fleet-orchestration`, `kcg-ml-models`, `graphiti`,
  `embedding-pipeline`, `peft`, `trl`; added `agno`, `google-adk`,
  `dignified-python`, `pydantic`, `ccc`, `dlthub`, `dagster`,
  `duckdb`, `cocoindex`. Final 23 entries, all resolve.
- [x] 11.6 Replace `frontend-apps` filter: removed
  `frontend-topology`, `ui-components`, `webapp-testing`,
  `copilotkit-develop`, `agent-experience`, `upstream-mirrors`;
  deduped `agentic-frontend-frameworks` (was listed twice);
  added `ag-ui`, `marimo`, `dignified-python`, `pydantic`, `ccc`,
  `langfuse`, `cocoindex`. Final 20 entries, all resolve, no
  duplicates.
- [x] 11.7 Replace `research` filter: removed `agent-experience`,
  `company-research`, `event-prospecting`, `search`, `fetch` (the
  latter 5 are subskills under `browserbase/` and inaccessible via
  the directory-based filter; they are accessible transitively via
  the `browserbase` parent entry); added `crawl4ai`, `langfuse`,
  `mlflow`, `baml`, `cocoindex`. Final 11 entries, all resolve.
- [x] 11.8 Update `INDEXING_AND_COGNITION.md` §8.1 table: replace the
  pre-v4 subagent rows (`oideachais`, `infrastructure` legacy,
  `meaisinfhoghlaim`, `croilar`, `tuatha`) with the 5 v4
  subagents (`data-platform`, `infrastructure`, `agent-platform`,
  `frontend-apps`, `research`); the per-subagent skill-count column
  now matches the new filter lengths.
- [x] 11.9 Update `INDEXING_AND_COGNITION.md` §8.4 health-check:
  fix `infrastructure=16` → `infrastructure=15`.
- [x] 11.10 Update `INDEXING_AND_COGNITION.md` §9.2 subagent
  migration table: fix `infrastructure=16` → `infrastructure=15`;
  append a "Skill name migration notes" footnote documenting the
  replacement of ~35 legacy names.
- [x] 11.11 Update `INDEXING_AND_COGNITION.md` "Last updated" date
  to 2026-06-29 with a one-line summary of the audit pass.
- [x] 11.12 Update `opencode.json` `build` agent prompt: replace
  "all 131 skills" with "all 53 top-level skills" (the actual
  count); add the per-subagent `skill_filter` count summary to
  step 4; dedupe the "dagster (orchestration)" line in the
  CONSULT list (it appeared twice); replace the dangling
  `celtic-asset-generation` + `infrastructure-stacks` references
  with current top-level skills (`baml`, `komodo`).
- [x] 11.13 Update `openspec/specs/agent-registry/spec.md` (and
  its change-delta mirror): fix `graphiti` → `graphiti-core` in
  the agent-platform Scenario (line 90); rewrite the `research`
  subagent Requirement body to acknowledge that subskills
  (`agent-experience`, `company-research`, `event-prospecting`,
  `search`, `fetch`) are nested under `browserbase/` and need
  not appear verbatim; replace the "131 skills" claim with the
  current 53-skill count + per-subagent `skill_filter` summary.
- [x] 11.14 Re-run final validation: `python3 -m json.tool
  opencode.json` exits 0; per-subagent counts `build=0, plan=0,
  data-platform=15, infrastructure=15, agent-platform=23,
  frontend-apps=20, research=11`; zero missing skill entries;
  zero duplicates.

## 12. Execution sequence (updated for §11)

1. Run pre-flight (§1) + the §11 audit.
2. `opencode.json` edits (§2) + §11.3-11.7 + §11.12 — all in
   one commit candidate.
3. `INDEXING_AND_COGNITION.md` edits (§3) + §11.8-11.11.
4. `.gitignore` edits (§4).
5. Canonical spec creation (§5) + change-delta spec creation
   (§6) + §11.13.
6. Validation gate (§7) + §11.14.
7. Commit + push to `origin/infra/pangolin-newt-infisical-upgrade-2026-06-28`.
8. **STOP** — user restarts opencode; `research` subagent becomes
   dispatchable.
