# Tasks — `2026-07-06-fix-research-agent-pydantic-and-ccc-v1-search-shell-escape`

## Phase 1 — Fix `research_agent.py` pydantic-v2.13 incompat (5 min)

- [x] 1.1 Replace `ThinkingConfig(thinking_budget_tokens=2048)` with `ThinkingConfig(include_thoughts=True)` in `research_agent.py:113-116`
- [x] 1.2 Remove the 6 stale imports (`ResearchReport`, `compose_report`, `conduct_research`, `evaluate_research`, `execute_research`, `generate_search_queries`) from `__init__.py:118-127`
- [x] 1.3 Verify `from cianfhoghlaim.agents.adk.dev_env_demo_agent import dev_env_demo_agent` loads cleanly

## Phase 2 — Fix `ccc:v1:search` shell-escape bug (30 min)

- [x] 2.1 Write `scripts/ccc_v1_search.py` (canonical Python wrapper with substring + semantic fallback)
- [x] 2.2 Replace `package.json` `ccc:v1:search` with `uv run python scripts/ccc_v1_search.py`
- [x] 2.3 Update `dev_env.py` `ccc_search` tool to use the canonical wrapper
- [x] 2.4 Verify `bun run ccc:v1:search "LANCE_DB" --limit 3` returns JSON

## Phase 3 — Refresh skill-count docs (15 min)

- [x] 3.1 Update `AGENTS.md` `123/123` → `53/53`
- [x] 3.2 Update `openspec/AGENTS.md` `123/123` → `53/53`
- [x] 3.3 Update `bonneagar/deploy-runbooks/bunchloch-bootstrap.md` `123/123` → `53/53`
- [x] 3.4 Update `openspec/research/2026-06-28-browserbase-program-2/adk-logfire/64-pydantic-logfire-usage-audit.md` with v4-consolidation note

## Phase 4 — Quality gates + archive (10 min)

- [x] 4.1 `mise run lint:skills` — must still pass 53/53
- [x] 4.2 `ruff check` + `mypy` on the new files — clean
- [x] 4.3 `openspec validate 2026-07-06-fix-research-agent-pydantic-and-ccc-v1-search-shell-escape --strict` — must pass
- [ ] 4.4 Commit + push + archive

## Out of scope (tracked separately)

- The `chunking.languages` sub-module is still missing from the v4
  tree. Until it's restored, the `ccc_v1_search.py` wrapper falls
  back to a direct LanceDB query.
- The `openspec list --specs --json` upstream flag is documented as
  an upstream concern in the prior change's `tasks.md`.