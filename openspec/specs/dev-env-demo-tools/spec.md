# Spec: `dev-env-demo-tools`

## Purpose

The Cianfhoghlaim dev environment offers powerful primitives (semantic
code search via CocoIndex Code, package drift detection against PyPI,
upstream breaking-change discovery via Firecrawl, HuggingFace model
recommendation, openspec discovery and validation, skill metadata
linting). These primitives are currently invoked by hand; this spec
defines them as a reusable capability surface that any Google ADK
`LlmAgent` can consume via `FunctionTool` wrappers.

## Capability summary

A `LlmAgent` can call the following 8 tools to inspect and reason about
the Cianfhoghlaim dev environment without leaving its tool surface:

| Tool | Wraps | Use case |
|:--|:--|:--|
| `ccc_search` | Local CocoIndex Code LanceDB index | Semantic code search before grep |
| `ccc_index` | `bun run ccc:v1:index` | Rebuild the index after major file moves |
| `drift_detect` | PyPI JSON API | Detect pinned-vs-latest drift for any Python package |
| `firecrawl_refactor_discover` | Firecrawl MCP server | Fetch upstream breaking changes for a package |
| `hf_best_model` | HuggingFace Hub API | Recommend the best HF model for a task + hardware + benchmark |
| `openspec_list_specs` | `openspec list --specs` CLI | Discover capability specs by quadrant |
| `openspec_validate` | `openspec validate --strict` CLI | Validate an in-flight change |
| `mise_lint_skills` | `mise run lint:skills` CLI | Run the 4-rule metadata lint on all skills |

The tools live in `cianfhoghlaim/agents/adk/tools/dev_env.py` and are
consumed three ways:

1. By the canonical **`dev_env_demo_agent`** — a `LlmAgent` whose
   system prompt walks the LLM through using each tool.
2. By **marimo notebooks** under
   `cianfhoghlaim/notebooks/meaisinfhoghlaim/dev_env/`.
3. By any **other ADK agent** that opts in (e.g. the 8 NCCA subject
   specialists) by adding the `*_TOOL` wrappers to their `tools=`
   list.

## Non-goals

- The 8 tools do NOT mutate any file. They are read-only by design.
- The 8 tools do NOT require a separate Docker Compose stack or MCP
  server — they live in the Python module and call CLIs / HTTP APIs
  directly.
- The spec does NOT introduce new openspec validator rules; it
  reuses the existing `openspec validate --strict` CLI.

## Cross-references

- `openspec/changes/2026-07-06-add-dev-env-demo-tools-to-adk-agents/`
- `cianfhoghlaim/agents/adk/tools/dev_env.py`
- `cianfhoghlaim/agents/adk/dev_env_demo_agent.py`
- `cianfhoghlaim/notebooks/meaisinfhoghlaim/dev_env/`
- `docs/agents/dev-env-demo-transcript.md`
- `opencode.json` (the `agent.dev-env-demo` block)
