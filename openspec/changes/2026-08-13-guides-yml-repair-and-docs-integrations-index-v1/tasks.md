# Tasks — guides.yml Repair & INTEGRATIONS_INDEX

## 1. Rewrite `.cocoindex_code/guides.yml` (all 26 entries)

- [ ] 1.1 Read the current guides.yml (441 lines, 26 entries)
- [ ] 1.2 Verify which paths exist on disk (run `find -e`)
- [ ] 1.3 Rewrite entry 1 "Cognee knowledge graph architecture"
      (the 7 dead `docs/01-cognee/*.md` → `.agents/skills/cognee/SKILL.md` + `.agents/skills/INDEXING_AND_COGNITION.md`)
- [ ] 1.4 Rewrite entry 2 "Platform architecture & infrastructure"
      (the 6 dead `docs/01-platform-architecture/*.md` → `.agents/skills/secrets-management/SKILL.md` + `.agents/skills/komodo/SKILL.md` + `.agents/skills/pangolin/SKILL.md` + `bonneagar/AGENTS.md`)
- [ ] 1.5 Rewrite entry 3 "Data platform: lakehouse, Dagster, DLT"
      (the 3 dead `docs/02-data-platform/*.md` → `dlt_sources/DATA_PLATFORM_ROUTER.md` + `dlt_sources/AGENTS.md` + `orchestration/AGENTS.md` + `motherduck/README.md`)
- [ ] 1.6 Rewrite entry 4 "AI/ML: models, training, OCR, RAG, Celtic AI"
      (the 7 dead `docs/04-ai-ml/*.md` → `.agents/skills/centralized-registry/SKILL.md` §11 OCR/VLM + `meaisinfhoghlaim/README.md`)
- [ ] 1.7 Rewrite entry 5 "Agent frameworks: ADK, Agno, Stagehand, Pydantic AI"
      (the 4 dead `docs/03-agents/*.md` → `.agents/skills/agent-fleet-orchestration/SKILL.md` + `agents/AGENTS.md`)
- [ ] 1.8 Rewrite entry 6 "Frontend stack: TanStack Start, Convex, Hono, Better Auth"
      (the 3 dead `docs/05-web/*.md` → `.agents/skills/agentic-frontend-frameworks/SKILL.md` + `web/apps/AGENTS.md`)
- [ ] 1.9 Rewrite entry 7 "Educational platform: oideachais, Leaving Cert"
      (the 4 dead `docs/06-product/educational-platform.md` + `docs/02-architecture/*.md` → `openspec/specs/british-isles-education-pipeline/spec.md` + `agents/meaisinfhoghlaim/AGENTS.md`)
- [ ] 1.10 Rewrite entry 8 "Celtic MMO: Tuatha, crypteolas, game dev"
      (the 3 dead `docs/06-product/*.md` → `agents/tuatha/AGENTS.md`)
- [ ] 1.11 Rewrite entry 9 "BAML: type-safe LLM extraction"
      (the 1 dead `docs/03-agents/baml-extraction.md` → `baml_src/AGENTS.md` + `baml_src/clients.baml`)
- [ ] 1.12 Rewrite entry 10 "Celtic language AI"
      (the 5 dead `docs/04-ai-ml/celtic-language-ai.md` + `docs/05-celtic-language/*.md` → `openspec/specs/celtic-language-pipeline/spec.md` + `meaisinfhoghlaim/alignment/`)
- [ ] 1.13 Rewrite entry 11 "Audit & consolidation history"
      (the 5 dead `docs/02-audit/*.md` → `docs/audits/2026-07-06-drift-audit.md` + `docs/audit/`)
- [ ] 1.14 Rewrite entry 12 "Patterns: BAML, data pipeline, embeddings, observability"
      (the 6 dead `docs/01-patterns/*.md` → per-area `.agents/skills/<skill>/SKILL.md` files)
- [ ] 1.15 Rewrite entry 13 "Pipelines: Dagster definitions, API, browser orchestrator"
      (the 8 dead `docs/03-pipelines/*.py` → `orchestration/AGENTS.md` + `dlt_sources/DATA_PLATFORM_ROUTER.md`)
- [ ] 1.16 Rewrite entry 14 "Standards: project conventions, observability patterns"
      (the 2 dead `docs/07-standards/*.md` → root `AGENTS.md` + `.agents/skills/dignified-python/SKILL.md`)
- [ ] 1.17 Rewrite entry 15 "Examples: BEADS tracker, data architecture, frontend"
      (the 8 dead `docs/08-examples/*.md` → `openspec/changes/` + `.agents/skills/`)
- [ ] 1.18 Rewrite entry 16 "Skills: agno, baml, cocoindex, dagster, dlt, duckdb, graphiti"
      (the 9 dead `docs/07-skills/*.md` → the real `.agents/skills/<skill>/SKILL.md` files — no `docs/07-skills/` mirror needed)
- [ ] 1.19 Rewrite entry 17 "Hackathons: Build Small 2026 + others"
      (the 3 dead `doc/hackathons/*.md` → `docs/research/` + `docs/legacy/cianfhoghlaim-pkg-readme.md`)
- [ ] 1.20 Rewrite entry 18 "Core: PROJECT_SPEC, CONSTRAINTS, AGENTS, CLAUDE"
      (the 4 dead `docs/{CLAUDE,PROJECT_SPEC,CONSTRAINTS,AGENTS}.md` → root `AGENTS.md` + `openspec/AGENTS.md`)
- [ ] 1.21 Rewrite entry 19 "Package ecosystem: external skill templates"
      (the 1 dead `docs/docs_examples_consolidated/` → `.agents/skills/_template/`)
- [ ] 1.22 Polish entries 20-26 (replace any stale sub-paths)
- [ ] 1.23 Update the header comment to reflect the new
       domain taxonomy

## 2. Create `docs/INTEGRATIONS_INDEX.md`

- [ ] 2.1 Verify `docs/` exists and has live subdirs (`audit/`,
      `audits/`, `legacy/`, `plans/`, `research/`, etc.)
- [ ] 2.2 Write the header + "Why this file exists" section
- [ ] 2.3 Write the 5 dead `docs/0X-*/` directories table
- [ ] 2.4 Write the 4 surviving `docs/` subdirectories table
- [ ] 2.5 Write the topic-by-topic mapping table (12 rows)
- [ ] 2.6 Write the "For agents" quick routing instructions
- [ ] 2.7 Cross-reference `INDEXING_AND_COGNITION.md` +
      `DATA_PLATFORM_ROUTER.md`

## 3. Add `mise run lint:guides-yml` validation gate

- [ ] 3.1 Create `scripts/lint_guides_yml.py` (~80 lines)
      - Walks every entry in `.cocoindex_code/guides.yml`
      - Extracts the `files:` list from each
      - Checks each path resolves on disk
      - Emits a JSON report
      - Exits 1 if any path is missing
- [ ] 3.2 Add the `[tasks."lint:guides-yml"]` block to `mise.toml`
- [ ] 3.3 Test `mise run lint:guides-yml` (after guides.yml
      rewrite) — expect "All 26 guides have valid paths"

## 4. Spec delta to `indexing-and-cognition`

- [ ] 4.1 Add an ADDED Requirement to
      `openspec/changes/2026-08-13-guides-yml-repair-and-docs-integrations-index-v1/specs/indexing-and-cognition/spec.md`
- [ ] 4.2 Add 2 Scenarios (WHEN a CCC search hits a stale guide /
      THEN the lint gate catches it; WHEN a new guide entry is added
      / THEN the path MUST resolve on disk)

## 5. Validation

- [ ] 5.1 `mise run lint:guides-yml` — all 26 entries pass
- [ ] 5.2 `openspec validate 2026-08-13-guides-yml-repair-and-docs-integrations-index-v1 --strict`
- [ ] 5.3 `mise run lint:skills` — 61/61 pass (no regression)
- [ ] 5.4 `mise run lint:drift-docs --dry-run` — no new drift
- [ ] 5.5 Spot-check `ccc search` for 4 sample queries

## 6. Commit + push (Landing the Plane)

- [ ] 6.1 `git pull --rebase`
- [ ] 6.2 `git status` — review
- [ ] 6.3 `git add openspec/changes/2026-08-13-guides-yml-repair-and-docs-integrations-index-v1/ .cocoindex_code/guides.yml docs/INTEGRATIONS_INDEX.md scripts/lint_guides_yml.py mise.toml`
- [ ] 6.4 `git commit -m "Repair guides.yml: rewrite 26 entries to point at real files + INTEGRATIONS_INDEX + lint:guides-yml"`
- [ ] 6.5 `git push`
- [ ] 6.6 `git status` — must show "up to date with origin"