# Tasks: refresh-skills-to-2026-06

## 1. Append 2026-06 sections to 8 skills

- [x] Append to `.agents/skills/cocoindex/SKILL.md` (v1.0.1–1.0.7
      changelog: `memo_key`, `auto_refresh`, `stats_group`,
      new connectors, LiteLLM STT, 8 splitter languages, fixes)
- [x] Append to `.agents/skills/dagster/SKILL.md` (`dg` CLI +
      Components API; the 5 KCG code-locations)
- [x] Append to `.agents/skills/cognee/SKILL.md` (temporal
      cognify, session memory + `improve()`, `recall()`)
- [x] Append to `.agents/skills/oideachais-storage/SKILL.md`
      (DuckLake 1.0 GA, Lance Namespace sidecar, refreshed
      mental model)
- [x] Append to `.agents/skills/kcg-leabharlann-pipeline/SKILL.md`
      (CocoIndex v1 + Cognee 0.1+ temporal in the 5-stage flow)
- [x] Append to `.agents/skills/agent-observability/SKILL.md`
      (Langfuse v3, MLflow GenAI eval, RAGAS trace-based, Logfire MCP)
- [x] Append to `.agents/skills/agentic-frontend-frameworks/SKILL.md`
      (AG-UI protocol, Pydantic AI + Gateway, DBOS, Convex,
      Cloudflare)
- [x] Append to `.agents/skills/tuatha-mmo/SKILL.md`
      (Babylon.js 7 + WebGPU, SpacetimeDB v2, x402 on Base L2)

## 2. Validate

- [x] `openspec validate refresh-skills-to-2026-06 --strict`

## 3. Commit + push + archive

- [x] Commit with message
      `refresh-skills-to-2026-06: append 2026-06 package update section to 8 skills`
- [x] Archive the openspec change
- [x] `git push`
