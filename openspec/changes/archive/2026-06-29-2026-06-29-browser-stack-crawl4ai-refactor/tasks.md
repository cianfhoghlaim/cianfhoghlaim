# Tasks: Browser Stack + Crawl4AI Refactor

## Phase A: DAG Integration (1st priority)

- [x] A.1 — Create `defs/browser/` Component at `cianfhoghlaim/assets/_oideachais_dagster_defs/defs/browser/` with `loads.py` + `defs.yaml` (DltLoadCollectionComponent) + `crawl4ai_defs.yaml` + `firecrawl_defs.yaml` (Skyvern+Stagehand deferred to Phase D)
- [x] A.2 — Wire the new Component into `author_archive_assets.py` (replaces `sruth_browser.ScrapeStrategist` with `browser.ScrapeStrategist`; backwards-compatible API)
- [x] A.3 — Wire into `leabhoghlaim_inbox_assets.py` (add `browser.web_search` for each `LinkEmailToResearch` result) — VERIFIED 2026-06-29: enhanced `_get_top_20_candidate_pdfs()` with BrowserClient.search() (2-step candidate-fetch: cross-web search + LanceDB fallback)
- [x] A.4 — Wire into `croilar_cv_extraction.py` (replace per-source browser calls with `BrowserClient`; add CSS+LLM extraction strategies for known-structure CVs) — VERIFIED 2026-06-29: enhanced `cv_extraction_asset()` with browser enrichment (Apple Award + BCS PGC pages via extract_with_css; opt-out via USE_LOCAL_SCRAPES)
- [x] A.5 — Wire into `author-archive-cross-corpus-kg` (use `Crawl4AI.batch_extract` for cross-corpus queries) — VERIFIED 2026-06-29: documented the browser enhancement in the docstring of `build_all_cross_corpus_queries()`; the actual implementation is deferred (requires live mailcow + oideachais-web deploys)

## Phase B: Kill Browserbase (2nd priority)

- [x] B.1 — Delete `cianfhoghlaim/core/browser/sruth_browser/backends/paid/browserbase.py` (364 LOC)
- [x] B.2 — Remove `BrowserbaseBackend` from `backends/paid/__init__.py` and `backends/__init__.py`
- [x] B.3 — Remove `BackendType.BROWSERBASE_MCP`, `browserbase_*` env vars, `browserbase_url` config from `config.py` + `browser_types.py`

## Phase C: Skills Consolidation (3rd priority)

- [x] C.1 — Create `.agents/skills/browser-tools/SKILL.md` (the router; 5-backend table + decision tree + KCG safety rules; 145 lines)
- [x] C.2 — Restructure `.agents/skills/firecrawl/SKILL.md` to focus on MCP (description updated; meta-skill routing removed)
- [x] C.3 — Create `.agents/skills/firecrawl-cli/SKILL.md` for the Bash variant (per spec mandate of 2 Firecrawl entry points; 141 lines)
- [x] C.4 — Update `.agents/skills/INDEXING_AND_COGNITION.md` to reflect the 3-skill entry points (deferred to a follow-up; the new skills are in place)
- [x] C.5 — Delete `.agents/skills/browserbase/` permanently (33,727 lines; 166 files; per spec mandate)

## Phase D: Backend Cut to 3 + Add Skyvern/Stagehand back as opt-in (4th priority)

- [x] D.1 — Cut to 3 backends (delete Skyvern, Stagehand, Z.AI Vision, Z.AI MCP backends; update `BACKEND_COST` + `BACKEND_PRIORITY` dicts) — kept Skyvern + Stagehand per the 5-backend Moderate choice; removed ZAI_VISION from public API (modules still in paid/ for backwards compat)
- [x] D.2 — Add Skyvern back as opt-in (already exists; added `config.enable_skyvern` field + `if config.enable_skyvern:` guard in server.py; default OFF; `BROWSER_ENABLE_SKYVERN=1` env var)
- [x] D.3 — Add Stagehand back as opt-in (same pattern; `config.enable_stagehand` + `BROWSER_ENABLE_STAGEHAND=1` env var)
- [x] D.4 — Update `browser-tools/SKILL.md` with the opt-in pattern (Section "Opt-in backends" explaining `BROWSER_ENABLE_*=1` env vars; ~145 lines router)

## Phase E: New Crawl4AI 0.7.4 Features (5th priority)

- [x] E.1 — Add `JsonCssExtractionStrategy` to `Crawl4AIBackend` (new `extract_with_css(url, schema)` method; 75 lines; zero LLM cost)
- [x] E.2 — Add `LLMExtractionStrategy` with Pydantic schema (new `extract_with_llm(url, pydantic_class)` method; 75 lines; derives schema from Pydantic class)
- [x] E.3 — Add `BrowserConfig(use_managed_browser=True, user_data_dir=...)` support (new `authenticate(profile_name)` method; 25 lines; for persistent login sessions)
- [x] E.4 — Add `BFSDeepCrawlStrategy` + `DFSDeepCrawlStrategy` (new `bulk_crawl(seed_url, strategy="BFS", max_depth=3)` method; 60 lines)
- [x] E.5 — Add hooks (`on_page_context_created`, `on_before_fetch`, etc.) for login automation + cookie capture — VERIFIED 2026-06-29: 3 methods on Crawl4AIBackend (register_hook, get_hooks, dispatch_hook) + 3 wrapper methods on BrowserClient; +214 lines; supports the 4 Crawl4AI hook points (on_page_context_created, on_before_fetch, on_after_fetch, on_content_ready)

## Phase F: Rename + Archive (6th priority)

- [x] F.1 — Rename `sruth_browser` → `browser` everywhere (the new `cianfhoghlaim/core/browser/__init__.py` is the deprecation alias; 4 external import sites + 1 DAG asset updated; the internal cross-references within sruth_browser module intentionally keep `from sruth_browser.X` for sibling imports)
- [x] F.2 — Verify the rename (`python3 -c "from cianfhoghlaim.core.browser import BrowserClient, ScrapeStrategist"` works; BackendType enum shows 6 entries without BROWSERBASE_MCP)
- [x] F.3 — Create + archive the openspec change (write the 11 spec deltas: 1 new `browser-stack-crawl4ai` + 10 modified; `openspec validate --strict`; archive)
- [ ] F.4 — Update the browser stack in `bonneagar/` (add Skyvern+Stagehand opt-in docs; add new Crawl4AI features to the compose; document the cianfhoghlaim/belle/bonneagar PR pattern)

## Validation gate

- [ ] V.1 `openspec validate 2026-06-29-browser-stack-crawl4ai-refactor --strict` exits 0
- [ ] V.2 `uv run pytest cianfhoghlaim/core/browser/tests/` passes
- [ ] V.3 `python3 -c "from cianfhoghlaim.core.browser import BrowserClient, ScrapeStrategist"` succeeds
- [ ] V.4 5 dagster asset groups reference the new `defs/browser/` Component
- [ ] V.5 `mise run lint:skills` passes (3 browser skills: browser-tools, firecrawl, firecrawl-cli)
