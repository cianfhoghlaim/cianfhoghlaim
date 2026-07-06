# Tasks — `2026-07-06-add-dev-env-demo-tools-to-adk-agents`

## Phase 1 — Spec + scaffold (30 min)

- [x] 1.1 Create `openspec/changes/2026-07-06-add-dev-env-demo-tools-to-adk-agents/` directory
- [x] 1.2 Write `proposal.md` (this document)
- [x] 1.3 Write `specs/dev-env-demo-tools/spec.md` (the 7 Requirements, each with 1+ Scenario)
- [x] 1.4 Write `tasks.md` (this checklist)
- [x] 1.5 Run `openspec validate 2026-07-06-add-dev-env-demo-tools-to-adk-agents --strict` — must pass

## Phase 2 — Tool module (90 min)

- [x] 2.1 Create `cianfhoghlaim/agents/adk/tools/dev_env.py`
- [x] 2.2 Implement `drift_detect()` — async, returns `dict[str, Any]` with `{tool_name, current_version, latest_version, severity, recommendation}`
- [x] 2.3 Implement `ccc_search()` — wraps the v1 LanceDB index at `.cocoindex_code/lancedb/codebase_chunks.lance` with optional BGE-M3 semantic mode (default fast substring)
- [x] 2.4 Implement `ccc_index()` — wraps `bun run ccc:v1:index` (rebuild)
- [x] 2.5 Implement `firecrawl_refactor_discover()` — uses `firecrawl_research_search_papers` + `firecrawl_scrape`, with `USE_LOCAL_SCRAPES=true` fallback to `stedding/ingest_queue/<pkg>.json`
- [x] 2.6 Implement `hf_best_model()` — wraps the existing `huggingface-best` skill logic + `huggingface_hub.HfApi`
- [x] 2.7 Implement `openspec_list_specs()` + `openspec_validate()` — wrap the `openspec` CLI
- [x] 2.8 Implement `mise_lint_skills()` — wraps `mise run lint:skills` (parses "N skills pass" format)
- [x] 2.9 Wrap each function in `FunctionTool(func=…)`; export as `__all__`
- [x] 2.10 Run `ruff check` + `mypy --strict` — both clean

## Phase 3 — Demo agent (45 min)

- [x] 3.1 Create `cianfhoghlaim/agents/adk/dev_env_demo_agent.py`
- [x] 3.2 Define `dev_env_demo_agent = LlmAgent(name="dev_env_demo_agent", model=config.model_name, tools=[…all 8…], output_key="dev_env_demo_report")`
- [x] 3.3 Write the 7-section system prompt
- [x] 3.4 (Skipped — package `__init__.py` has a pre-existing pydantic-v2.13 incompat in `research_agent.py` that blocks the `from cianfhoghlaim.agents.adk import …` path. Direct module import works. See "Known issues" below.)

## Phase 4 — Marimo notebooks (90 min)

- [x] 4.1 Create `cianfhoghlaim/notebooks/meaisinfhoghlaim/dev_env/` directory
- [x] 4.2 `01_ccc_search.py` — 3 cells (search input + render)
- [x] 4.3 `02_drift_detect.py` — multiselect picker + colour-coded table
- [x] 4.4 `03_firecrawl_refactor_discover.py` — package picker + breaking-changes table
- [x] 4.5 `04_hf_best_model.py` — task/hardware/benchmark form + recommended card
- [x] 4.6 `05_openspec_list.py` — quadrant dropdown + grouped table
- [x] 4.7 `06_mise_lint_skills.py` — path input + lint report
- [x] 4.8 (Skipped — `mise.toml` `[tasks.marimo.dev-env]` namespace is nice-to-have, not required by the spec)

## Phase 5 — Recorded transcript + opencode.json (60 min)

- [x] 5.1 Create `docs/agents/dev-env-demo-transcript.md`
- [x] 5.2 Write 6 per-tool sections
- [x] 5.3 Write the 7th "chained tools" section — the `lancedb` 0.34→0.36 migration example
- [x] 5.4 Modify `opencode.json` — added new `agent.dev-env-demo` block
- [x] 5.5 Modify `openspec/AGENTS.md` — added `dev-env-demo-tools` row to the catalogue table

## Phase 6 — Quality gates + archive (15 min)

- [x] 6.1 `mise run lint:skills` — passes (53 skills, including the 1 newly-valid SKILL.md from the v4 consolidation)
- [x] 6.2 `ruff check` + `mypy --no-error-summary` on the new modules — clean
- [x] 6.3 `openspec validate 2026-07-06-add-dev-env-demo-tools-to-adk-agents --strict` — passes
- [ ] 6.4 Hand off to user for commit + archive

## Known issues (NOT blocking this change)

1. **Pre-existing pydantic-v2.13 incompat in `research_agent.py`** —
   `thinking_budget_tokens=2048` is no longer a valid field on the
   new `google.genai.types.ThinkingConfig` (Pydantic v2 forbids extra
   inputs). This blocks `from cianfhoghlaim.agents.adk import
   dev_env_demo_agent` at the package level. The dev_env_demo_agent
   module itself loads fine via `importlib.util.spec_from_file_location`
   (the workaround used by all 6 marimo notebooks). A separate
   follow-up change should be filed to remove the
   `thinking_budget_tokens` arg from `research_agent.py:114`.

2. **`bun run ccc:v1:search` has a known shell-escape bug** in
   `package.json` (the `ccc:v1:search` script uses double-quoted
   Python source that breaks when interpolated via bun). The
   `ccc_search` tool in this change bypasses the bun wrapper and
   calls `search_codebase` directly via `uv run python -c ...`. A
   follow-up should fix the bun script.

3. **`AGENTS.md` says "123 skills" but the actual count is 53** —
   the doc is out of date. The `mise_lint_skills` tool returns the
   real count, so agents that trust the tool over the doc are
   correct. A follow-up should update `AGENTS.md`.

4. **The `openspec list --specs --json` flag** is undocumented in
   the current openspec CLI — the tool parses the plain-text output
   as a fallback. A follow-up could add `--json` to the openspec
   CLI upstream.

