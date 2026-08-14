# Tasks: Firecrawl MCP × ccc Dual-Search Architecture

## Phase A — Concept guides + sync plumbing (4 tasks, ~1.5 hours)

- [ ] A1 Append the **27th concept guide `firecrawl-search`** to
  `.cocoindex_code/guides.yml` (description: the canonical "use
  firecrawl_search vs ccc:search" routing reference; files: new
  AGENTS.md section + new SKILL.md paragraphs + the
  `FirecrawlMCPClient` wrapper).
- [ ] A2 Append the **28th concept guide `firecrawl-mcp-tools`** to
  `.cocoindex_code/guides.yml` (description: the 12 MCP tools +
  their use cases; files: the `FirecrawlMCPClient.client.py` wrapper
  + the new `firecrawl-mcp` skill if added).
- [ ] A3 Append the **29th concept guide `firecrawl-research-index`**
  to `.cocoindex_code/guides.yml` (description: the 43M-paper index
  for BAML rationale + RAGAS rubric citations; files: the
  `FirecrawlMCPClient.research_*` methods).
- [ ] A4 Append the **30th concept guide `firecrawl-developer-index`**
  to `.cocoindex_code/guides.yml` (description: the GitHub
  issues/PRs/README/curated docs index for primary-source debugging;
  files: the `FirecrawlMCPClient.developer_search` method).
- [ ] A5 Append the **31st concept guide `firecrawl-corpus`** to
  `.cocoindex_code/guides.yml` (description: the agent reference
  corpus — software stack + education sources — built by the Phase 4a
  change; files: `agents/meaisinfhoghlaim/firecrawl_mcp/corpus.py`
  + `notebooks/01_corpus/01_software_stack_crawl.py` +
  `notebooks/01_corpus/02_education_corpus_crawl.py`).
- [ ] A6 Create `scripts/sync/firecrawl-ccc.sh` — mirrors
  `scripts/sync/baml-ccc.sh` (echoes the 5 new concept guides + runs
  `bun run ccc:index`).
- [ ] A7 Add `[tasks."sync:firecrawl"]` to `mise.toml` (calls the new
  script + writes `stedding/sync-reports/firecrawl-ccc-{date}.md`).
- [ ] A8 Add the `firecrawl-search` smoke test to
  `scripts/bring-up-smoke-test.sh` (grep for `firecrawl-search` in
  `.cocoindex_code/guides.yml`).
- [ ] A9 `bun run ccc:index` + `mise run lint:guides-yml` to verify
  the 31 guides resolve.

## Phase B — Documentation updates (1 task, ~30 minutes)

- [ ] B1 Update `AGENTS.md` §"Priority quick reference" with a new
  `firecrawl_search` row + a new "Dual-search architecture" diagram
  (extends the existing §"CCC + Cognee dual-search diagram" to a
  3-way Y-shape with firecrawl_mcp as the 3rd leg).
- [ ] B2 Update `openspec/AGENTS.md` with a "When to use
  firecrawl_search vs ccc:search" routing table (12 rows: code-only,
  docs-only, upstream-state, known-URL, find-URLs, traverse-site,
  autonomous-research, recurring-check, papers, primary-source,
  login-gated, self-debug).
- [ ] B3 Update 6 SKILL.md files (one paragraph each):
  - `.agents/skills/browser-tools/SKILL.md`
  - `.agents/skills/centralized-registry/SKILL.md`
  - `.agents/skills/agent-fleet-orchestration/SKILL.md`
  - `.agents/skills/secrets-management/SKILL.md`
  - `.agents/skills/knowledge-sync-loop/SKILL.md`
  - `.agents/skills/INDEXING_AND_COGNITION.md`
- [ ] B4 `mise run lint:skills && mise run lint:drift-docs`.

## Phase C — FirecrawlMCPClient wrapper (3 tasks, ~2 hours)

- [ ] C1 Create `agents/meaisinfhoghlaim/firecrawl_mcp/__init__.py`
  with the public API surface (`FirecrawlMCPClient` + module docstring
  listing the 12 wrapped tools + the credit-cost annotations).
- [ ] C2 Create `agents/meaisinfhoghlaim/firecrawl_mcp/client.py`
  (~200 LOC) — `FirecrawlMCPClient` class wrapping all 12 MCP tools
  (`search`, `scrape`, `crawl`, `map`, `agent`, `interact`,
  `batch_scrape`, `monitor_create`, `monitor_check`,
  `research_search_papers`, `research_inspect_paper`,
  `developer_search`, `parse`). Every method:
  - Has a Pydantic response model
  - Is decorated with `@observe(name=...)` from
    `langfuse.decorators` (per the `agent-observability` skill)
  - Has a docstring with the credit cost + the canonical Firecrawl
    docs URL
  - Emits a `firecrawl_meta.scrapes` row via the centralized logger
    (the table is created in Phase 4a but the logger already accepts
    the writes)
- [ ] C3 Create `agents/meaisinfhoghlaim/firecrawl_mcp/AGENTS.md`
  with the per-spec-agent-routing 6-section outline (routing
  sentence, quick start, key sources, adjacent specs, DO NOT, skill
  pointers).

## Phase D — Validation (3 tasks, ~30 minutes)

- [ ] D1 `openspec validate
  2026-08-14-firecrawl-mcp-ccc-dual-search-v1 --strict` returns 0
  errors.
- [ ] D2 `bun run ccc:search "firecrawl dual search"` returns ≥1 hit
  pointing at the new AGENTS.md section + the 5 new guides.
- [ ] D3 `mise run sync:all` passes.
- [ ] D4 `git add openspec/changes/2026-08-14-firecrawl-mcp-ccc-dual-search-v1/ .cocoindex_code/guides.yml AGENTS.md openspec/AGENTS.md mise.toml scripts/sync/firecrawl-ccc.sh scripts/bring-up-smoke-test.sh .agents/skills/{browser-tools,centralized-registry,agent-fleet-orchestration,secrets-management,knowledge-sync-loop,INDEXING_AND_COGNITION}.md agents/meaisinfhoghlaim/firecrawl_mcp/`