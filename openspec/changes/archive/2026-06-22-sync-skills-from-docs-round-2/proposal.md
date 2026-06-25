# Change: sync-skills-from-docs-round-2

## Why

A second round of `docs/*` consolidation. The user listed 17 specific
files plus the `docs/marimo/` directory, totalling ~4,000 lines of
example docs and the `docs/marimo/` directory (2.6 MB, 16 curated
`.py` example files + `marimo_cloudflare.md` + `marimo-reference.md`).

Three concrete patterns recur:

1. **Wrong-API-version docs are dangerous.** `docs/07-skills/cocoindex.md`
   documents the deprecated v0 API; the `cocoindex` skill (just
   rewritten in `sync-skills-from-docs`) is v1. Leaving the doc in
   place will mislead agents into writing broken code.
2. **New agent + browser-automation skills are missing entirely.**
   `change-detection`, `pydantic-ai`, `stagehand`, `ag-ui` have no
   skill but are first-class project dependencies.
3. **KCG-specific context is in short stub docs, not the canonical
   skills.** `ducklake.md` (36 lines), `dagster-sdk.md` (37 lines),
   `google-adk.md` (37 lines), `graphiti.md` (58 lines) all contain
   project-specific pointers that should live in the canonical
   skills, not as separate 30-50 line files.

## What Changes

### New skills (4)

- `.agents/skills/change-detection/SKILL.md` — 3-layer pattern
  (DLT incremental → Dagster sitemap-hash sensor →
  ChangeDetection.io), the `infrastructure/stacks/tools/changedetection/`
  Compose stack, the `sources.yaml` pairing rule
- `.agents/skills/pydantic-ai/SKILL.md` — Pydantic's agent framework;
  AG-UI protocol integration, Pydantic AI Gateway, Logfire MCP
  instrumentation, DBOS durable execution
- `.agents/skills/stagehand/SKILL.md` — Browserbase V3 SDK;
  act/extract/observe/agent, CUA, hybrid mode, DeepLocator, multi-page
- `.agents/skills/ag-ui/SKILL.md` — AG-UI SSE protocol bridging
  CopilotKit (UI) ↔ Hono (API) ↔ Agno/Google ADK (backend)

### Major expansions (3)

- `.agents/skills/google-adk/SKILL.md` — add workflow primitives
  (SequentialAgent, LoopAgent, ParallelAgent, Coordinator Pattern),
  A2A Protocol, neuro-symbolic OWL truth-anchoring, deployment
  (`make deploy` → Agent Engine), Firecrawl integration
- `.agents/skills/agno/SKILL.md` — add A2A Protocol details,
  AgentOS OpenAPI URL, agentic chunking pattern, Dagster+DLT+Agno
  architecture, Z.ai GLM-4.6 via `OpenAILike`, Browserbase MCP
- `.agents/skills/tanstack-start/SKILL.md` — rewrite 9-line stub to
  absorb the 453-line generic reference, with KCG context
  (no auth on `sruth/oideachais/web`, `@tanstack/db` for offline diff-sync,
  BetterAuth only in `sruth/croilar/apps/portal`)
- `.agents/skills/marimo/SKILL.md` + new `references/` — 32 new
  patterns from the 16 curated `.py` files, plus the marimo-on-Cloudflare
  Workers + Container deployment, PEP 723, `mo.sql(engine=)`, multi-column
  layout, `@app.setup` / `@app.function` / `mo.app_meta().mode`,
  `mo.status.{spinner,progress_bar}`, DLT + LanceDB pipeline pattern

### Minor expansions (4) — append 5-10 line "KCG context" blocks

- `.agents/skills/ducklake/SKILL.md` — add the KCG-specific topology
  (Garage S3 + Lakekeeper + Lance Namespace sidecar, port 9000)
- `.agents/skills/dagster/SKILL.md` — add 4-layer asset graph
  (Ingestion → Materials → Model Lifecycle → Asset Generation)
  + port list (3335 engineering, 3000 croilar-dagster)
- `.agents/skills/google-adk/SKILL.md` (covered above as major)
- `.agents/skills/graphiti/SKILL.md` — add "Cognee is the primary KG;
  Graphiti is the optional bi-temporal complement" framing;
  fix stale pre-restructure paths (`bonneagar/`, `sruth/`) →
  `infrastructure/stacks/machine_learning/graphiti/`,
  `meaisínfhoghlaim/agents/`

### Merges into existing skills (2)

- `colpali.md` → fold KCG cache location (`stedding/huggingface/hub/`)
  + `vidore/colpali-v1.3` into `cocoindex/SKILL.md`; the v1 API is
  already in `references/multimodal-image-search.md`
- `patchright.md` → fold 15-line Anti-Bot Fallback section into
  `browser/SKILL.md` (Playwright API drop-in, Cloudflare/CAPTCHA
  escalation path to Browserbase)

### Docs to delete (after skill updates)

The user listed 17 specific files + the whole `docs/marimo/`
directory:

- `docs/03-agents/{change-detection, colpali, copilotkit, crawl4ai-sdk,
  patchright, pydantic-ai, stagehand, GOOGLE_ADK, agno, ag-ui}.md`
- `docs/07-skills/{baml, cocoindex, tanstack-start}.md` (baml +
  cocoindex are redundant/wrong; tanstack-start is canonical)
- `docs/00-package-ecosystem/storage/ducklake.md`
- `docs/00-package-ecosystem/ai-frameworks/google-adk.md`
- `docs/00-package-ecosystem/orchestration/dagster-sdk.md`
- `docs/00-core/graphiti.md`
- `docs/marimo/` (whole directory, 2.6 MB)

### Project rules PRESERVED (not changed)

- **Cognee is the primary KG** (now documented in `graphiti` skill)
- **No auth on `sruth/oideachais/web` / `sruth/tuatha/ui`** (now documented in
  `tanstack-start` skill)
- **CocoIndex v1 only** (the `cocoindex` skill is v1; the v0 doc
  in `docs/07-skills/cocoindex.md` is deleted)
- **`sruth/oideachais/baml_src/` is the BAML home** (unchanged)
- **`sruth/oideachais/dlt_sources/` is the dlt home** (unchanged)

## Impact

- **Affected specs (2)**:
  - `oideachais-marimo-dashboards` — adds 4 new requirements
    (Cloudflare deployment, PEP 723 script blocks, multi-column
    layout, DLT + LanceDB pipeline pattern)
  - `official-media-marimo` — adds 2 new requirements (Cloudflare
    deployment, streamlit-compatible layout)
- **Affected code**: none. Skills are documentation.
- **Affected skills** (12 total): 4 new
  (change-detection, pydantic-ai, stagehand, ag-ui) +
  8 expanded (google-adk, agno, tanstack-start, marimo, ducklake,
  dagster, graphiti, cocoindex, browser, browserbase).

## Success criteria

- `openspec validate sync-skills-from-docs-round-2 --strict` passes
- The 4 new skills exist at `.agents/skills/{change-detection,
  pydantic-ai, stagehand, ag-ui}/SKILL.md`
- `marimo` skill is rewritten with 32 new patterns + 6 new
  reference files (deployment-cloudflare, data-pipelines,
  vector-search, layouts, lifecycle-modes, ai-chat)
- `tanstack-start` skill is rewritten from 9 lines to ~300+ lines
  (absorbs the 453-line doc)
- `google-adk` and `agno` skills are expanded to ~500-700 lines
  (absorb the workflow primitives / A2A / AgentOS / neuro-symbolic
  patterns)
- `ducklake`, `dagster`, `graphiti` skills have new "KCG context"
  sections
- `browser` skill has the new "Anti-Bot Fallback" section
  (patchright → Playwright → Browserbase ladder)
- The 18 docs files + `docs/marimo/` directory are removed

## Rollback

Skills-only. Rollback = restore the 18 docs files + `docs/marimo/`
directory from git (`git checkout HEAD~1 -- docs/`). No data, code,
or runtime state is affected.

## Out of scope

- Restructuring the marimo skill into a sub-skill dispatcher
  (preserved as a single SKILL.md + 6 references)
- Adding new KCG agents (the project already has them)
- Replacing the `ccc` CLI (its `docs/03-agents/copilotkit.md`-class
  skill cards are unchanged)
- Other files in `docs/03-agents/` (e.g. `agent-frameworks.md.superseded`,
  `BAML_COMPREHENSIVE_GUIDE.md.superseded`, `MCP.md`, `MCP_RESEARCH.md.superseded`)
  that the user did not include in the list
