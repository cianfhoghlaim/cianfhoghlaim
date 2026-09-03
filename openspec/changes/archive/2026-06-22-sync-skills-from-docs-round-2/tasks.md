# Tasks: sync-skills-from-docs-round-2

## 1. Create OpenSpec change scaffolding

- [x] Create `openspec/changes/sync-skills-from-docs-round-2/` directory
      tree.
- [x] Write `proposal.md`.
- [x] Write `tasks.md` (this file).
- [x] Write 2 spec deltas (marimo-dashboards, official-media-marimo).
- [x] Run `openspec validate --strict`.

## 2. New skills (4)

- [x] Create `.agents/skills/change-detection/SKILL.md`
      (3-layer pattern).
- [x] Create `.agents/skills/pydantic-ai/SKILL.md`
      (Pydantic AI framework + AG-UI + Gateway + Logfire + DBOS).
- [x] Create `.agents/skills/stagehand/SKILL.md`
      (Browserbase V3 act/extract/observe/agent/CUA).
- [x] Create `.agents/skills/ag-ui/SKILL.md`
      (AG-UI SSE protocol).

## 3. Major expansions (4)

- [x] Rewrite `.agents/skills/tanstack-start/SKILL.md`
      (9-line stub → ~300 lines, KCG no-auth, `@tanstack/db`,
      BetterAuth only in `sruth/croilar/apps/portal`).
- [x] Expand `.agents/skills/google-adk/SKILL.md`
      (workflow primitives, A2A, neuro-symbolic, deployment,
      Firecrawl integration).
- [x] Expand `.agents/skills/agno/SKILL.md`
      (A2A protocol details, AgentOS OpenAPI URL, agentic chunking,
      Dagster+DLT+Agno, Z.ai GLM-4.6, Browserbase MCP).
- [x] Rewrite `.agents/skills/marimo/SKILL.md` + add 6 new
      reference files (deployment-cloudflare, data-pipelines,
      vector-search, layouts, lifecycle-modes, ai-chat, sql-cells).

## 4. Minor expansions (3) + merges (2)

- [x] Append KCG context to `.agents/skills/ducklake/SKILL.md`
      (Garage S3 + Lakekeeper + Lance Namespace sidecar).
- [x] Append 4-layer asset graph to `.agents/skills/dagster/SKILL.md`.
- [x] Append "Cognee is primary" + fix stale paths in
      `.agents/skills/graphiti/SKILL.md`.
- [x] Append Anti-Bot Fallback section (patchright) to
      `.agents/skills/browser/SKILL.md`.
- [x] Append KCG colpali cache location to
      `.agents/skills/cocoindex/SKILL.md`.

## 5. Delete the listed docs

- [x] `rm docs/03-agents/change-detection.md`
- [x] `rm docs/03-agents/colpali.md`
- [x] `rm docs/03-agents/copilotkit.md`
- [x] `rm docs/03-agents/crawl4ai-sdk.md`
- [x] `rm docs/03-agents/patchright.md`
- [x] `rm docs/03-agents/pydantic-ai.md`
- [x] `rm docs/03-agents/stagehand.md`
- [x] `rm docs/03-agents/GOOGLE_ADK.md`
- [x] `rm docs/03-agents/agno.md`
- [x] `rm docs/03-agents/ag-ui.md`
- [x] `rm docs/07-skills/baml.md`
- [x] `rm docs/07-skills/cocoindex.md`
- [x] `rm docs/07-skills/tanstack-start.md`
- [x] `rm docs/00-package-ecosystem/storage/ducklake.md`
- [x] `rm docs/00-package-ecosystem/ai-frameworks/google-adk.md`
- [x] `rm docs/00-package-ecosystem/orchestration/dagster-sdk.md`
- [x] `rm docs/00-core/graphiti.md`
- [x] `rm -rf docs/marimo/`

## 6. Verify

- [ ] Re-run `openspec validate sync-skills-from-docs-round-2 --strict`.
- [ ] Smoke-test any new skill imports (if Python).
- [ ] Re-index the codebase: `bun run ccc:index`.

## 7. Archive

- [ ] `openspec archive sync-skills-from-docs-round-2 --yes`.

## 8. Land the plane

- [ ] `git status`.
- [ ] `git add` only my changes (skill + docs + openspec).
- [ ] `git commit -m "..."`.
- [ ] `git push`.
