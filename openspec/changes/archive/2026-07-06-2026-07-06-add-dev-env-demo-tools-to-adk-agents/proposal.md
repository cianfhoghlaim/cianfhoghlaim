# Change: 2026-07-06-add-dev-env-demo-tools-to-adk-agents

## Why

The Cianfhoghlaim dev environment is rich (12 MCP servers in `opencode.json`,
36 openspec specs, 574 pip-installed packages, 25 marimo notebooks, 94 Docker
Compose stacks, 12-agent fleet, 6 v1 CocoIndex Apps). But **none of the 8 NCCA
ADK agents (`math_agent`, `appm_agent`, `chem_agent`, `geog_agent`,
`hist_agent`, `engl_agent`, `gael_agent`, `comp_agent`) or the research agents
(`research_agent`, `education_research_agent`, `bunchloch_research_agent`,
`mcp_curriculum_agent`) can ask the dev-env about itself** — they cannot:

- Detect that a pin in `pyproject.toml` is out of date vs. the latest PyPI release (drift detection)
- Search the local codebase semantically via `bun run ccc:search` (the agent uses grep instead)
- Discover a breaking change in `dlt` 1.28 / `dagster` 1.13 / `motherduck` via Firecrawl
- Recommend the best HF model for a task (e.g. a new `bge-m3` v2)
- List the current pending openspec changes
- Run `mise run lint:skills` to validate the 123 skills

This is the **"boots-trapped" demo gap** — the dev environment's most
powerful features are not exposed as ADK `FunctionTool`s, so agents cannot
use them and cannot demo them to the user. This change closes that gap.

The user's prior chat sessions have repeatedly demonstrated each of these
patterns by hand:

- Running `bun run ccc:search "..."` before `grep`
- Using `firecrawl_scrape` to discover upstream breaking changes
- Reading `motherduck` / `dlt` changelogs via `firecrawl_research_search_papers`
- Asking `huggingface_best` "which bge model is best for retrieval"
- Running `openspec list --specs` to discover capabilities
- Running `mise run lint:skills` to validate metadata

This change crystallizes those patterns into 8 reusable tool functions + 6
demo notebooks + 1 demo ADK agent + 1 recorded transcript.

## What changes

**1 new Python module** — `cianfhoghlaim/agents/adk/tools/dev_env.py`
(≈ 380 LOC):

- 8 async functions, each wrapped in `google.adk.tools.FunctionTool`
- 1 module-level `__all__` exporting the 8 `FunctionTool` instances

**1 new ADK LlmAgent** — `cianfhoghlaim/agents/adk/dev_env_demo_agent.py`
(≈ 220 LOC):

- `LlmAgent` named `dev_env_demo_agent` with all 8 tools wired
- 7-section system prompt that walks the model through using each tool in
  order, chains them in a real-world migration scenario, and refuses to
  mutate files (read-only by design)
- `output_key="dev_env_demo_report"`

**6 new marimo notebooks** —
`cianfhoghlaim/notebooks/meaisinfhoghlaim/dev_env/01_ccc_search.py` through
`06_mise_lint_skills.py`:

- Each notebook has 2-3 cells: an `@app.cell` that imports the tool
  function and calls it on a real repo target; an `@app.cell` that displays
  the result in a `mo.ui.table` or `mo.md`; an optional 3rd cell with a
  follow-up call
- All 6 import from the same `dev_env` module (single source of truth)
- Each is wired into the existing `mise run marimo:*` task surface

**1 new demo transcript** — `docs/agents/dev-env-demo-transcript.md`
(≈ 350 lines):

- 6 sections, one per primary tool
- Each section: (a) the user prompt; (b) the LLM's reasoning trace; (c) the
  tool call (function name + args); (d) the tool result (verbatim); (e) the
  LLM's follow-up
- Section 7: a worked example showing **all 6 tools chained** to detect that
  `lancedb` 0.34 → 0.36 introduced a breaking `mount_table_target` signature
  change, surface the upstream changelog via Firecrawl, recommend the
  migration, and draft a GitHub issue body

**1 new openspec capability spec** —
`openspec/specs/dev-env-demo-tools/spec.md` (per the openspec spec-driven
workflow).

**Modified files** — 2:

- `opencode.json` — register the new `dev_env_demo_agent` in an
  `agent.dev-env-demo` block (mirrors the existing `agent.*` schema). Note:
  the dev-env tools themselves are NOT registered as MCP servers because
  they wrap CLIs and Python imports that live inside the Python environment,
  not as standalone daemons. ADK agents consume them via the canonical
  `from cianfhoghlaim.agents.adk.tools.dev_env import …` path; marimo
  notebooks consume them via `@app.cell` imports.
- `openspec/AGENTS.md` — append the new spec to the catalogue table.

## Impact

| Surface                           | Before                                         | After                                                       |
|-----------------------------------|------------------------------------------------|-------------------------------------------------------------|
| `math_agent.tools`                | 5 (all curriculum-specific)                    | 5 + opt-in to all 8 dev-env tools                           |
| `research_agent.tools`            | 1 (`google_search`)                            | 1 + opt-in to all 8 dev-env tools                           |
| `mcp_curriculum_agent.tools`      | 4 stubbed MCP wrappers                         | 4 + opt-in to all 8 dev-env tools                           |
| Dev-env demo path                 | Implicit (in chat only)                        | Explicit: 6 marimo notebooks + 1 LlmAgent + transcript      |
| Spec catalogue                    | 36 specs                                       | 37 specs (+1 `dev-env-demo-tools`)                          |
| Skill count                       | 123                                            | 123 (no new skill; tools reference existing `ccc`, `firecrawl`, `huggingface`, `openspec` skills) |

**Zero breaking changes.** All 8 tools are additions. Existing ADK agents
keep their existing tool lists; the demo agent is the canonical user of the
new tools.

## Non-goals

- **No new MCP server stack.** The 8 tools wrap CLIs (`bun`, `mise`,
  `openspec`) and inline HTTP calls (PyPI JSON, HF Hub API). They live in
  the Python module, not in a separate Docker Compose stack.
- **No new openspec validator rules.** The tools use the existing
  `openspec validate --strict` CLI.
- **No live web search via `firecrawl_scrape` by default.** The
  `firecrawl_refactor_discover` tool respects the canonical
  `USE_LOCAL_SCRAPES=true` env var fallback — if set, it uses the curated
  `stedding/ingest_queue/` snapshot instead of burning Firecrawl credits.
