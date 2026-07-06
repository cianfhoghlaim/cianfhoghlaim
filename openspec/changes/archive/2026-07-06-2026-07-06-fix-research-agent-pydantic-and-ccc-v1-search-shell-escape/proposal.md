# Change: 2026-07-06-fix-research-agent-pydantic-and-ccc-v1-search-shell-escape

## Why

Two pre-existing bugs in the Cianfhoghlaim codebase blocked
`dev_env_demo_agent` from loading cleanly via the canonical
`from cianfhoghlaim.agents.adk import …` path. Both surfaced during the
`2026-07-06-add-dev-env-demo-tools-to-adk-agents` change:

1. **`research_agent.py:114`** passes `thinking_budget_tokens=2048`
   to `google.genai.types.ThinkingConfig`, but that field was removed
   in the new google-genai release (Pydantic v2 forbids extra inputs).
   The ImportError blocks all `cianfhoghlaim.agents.adk.*` imports.
2. **`package.json` `ccc:v1:search`** uses a bash-style `${1:-}`
   inside a double-quoted Python `-c` argument that bun's argument
   parser can't interpolate. The script raises `SyntaxError: unexpected
   character after line continuation character`.
3. **`__init__.py`** imports 6 names from `research_agent` that no
   longer exist (`ResearchReport`, `compose_report`, `conduct_research`,
   `evaluate_research`, `execute_research`, `generate_search_queries`).
4. **Multiple docs claim `mise run lint:skills` reports "123/123"**,
   but the actual lint count is **53** (the v4 consolidation removed
   the redundant quadrant-specific skill folders). This is documented
   but misleads anyone running the gate.

This change fixes all 4 issues.

## What changes

**`cianfhoghlaim/agents/adk/research_agent.py`** — replace the broken
`ThinkingConfig(thinking_budget_tokens=2048)` with the modern
`ThinkingConfig(include_thoughts=True)` (matching the pattern already
used by `education_research_agent.py:111-113`).

**`cianfhoghlaim/agents/adk/__init__.py`** — remove the 6 stale
imports of names that no longer exist in `research_agent.py`. This
restores package-level imports for the entire `adk` subpackage.

**`scripts/ccc_v1_search.py`** — NEW (≈ 110 LOC). Canonical Python
wrapper that:
- Uses the v4 module path `cianfhoghlaim.cocoindex.codebase_indexing`
- Falls back to a direct LanceDB query at
  `.cocoindex_code/lancedb/codebase_chunks.lance` if the module
  import fails (which is the common case at 2026-07-06 because
  `chunking.languages` is a missing sub-module in the v4 tree)
- Emits JSON on stdout for parseable integration with the
  `ccc_search` ADK tool
- Supports `--semantic` for BGE-M3 vector search
- Default substring search is instant; semantic adds 2-5s first call

**`package.json`** — replace the broken `ccc:v1:search` script with
`uv run python scripts/ccc_v1_search.py`. Now `bun run ccc:v1:search`
works end-to-end.

**`cianfhoghlaim/agents/adk/tools/dev_env.py`** — update the
`ccc_search` tool to invoke the canonical
`scripts/ccc_v1_search.py` wrapper instead of the inline
`python -c "..."` incantation.

**Doc refreshes** (current-state docs only; historical change files
are point-in-time artifacts and are NOT modified):
- `AGENTS.md` — `123/123` → `53/53`
- `openspec/AGENTS.md` — `123/123` → `53/53`
- `bonneagar/deploy-runbooks/bunchloch-bootstrap.md` — `123/123` → `53/53`
- `openspec/research/2026-06-28-browserbase-program-2/adk-logfire/64-pydantic-logfire-usage-audit.md`
  — adds the v4-consolidation note

## Impact

| Surface | Before | After |
|---|---|---|
| `from cianfhoghlaim.agents.adk import dev_env_demo_agent` | ImportError (3 cascading failures) | loads cleanly |
| `bun run ccc:v1:search "<query>"` | SyntaxError | returns JSON chunks |
| `mise run lint:skills` documented count | misleading "123/123" | accurate "53/53" |

**Zero breaking changes.** All fixes are surgical removals or
format-preserving corrections.

## Out of scope

- The `chunking.languages` sub-module is still missing from the v4
  tree; that's a separate cleanup tracked elsewhere.
- The `openspec list --specs --json` upstream flag is NOT fixed here
  (upstream concern, tracked as a docs note in the `dev_env_demo_agent`
  task list).