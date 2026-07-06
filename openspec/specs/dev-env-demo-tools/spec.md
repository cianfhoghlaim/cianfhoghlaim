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
## Requirements
### Requirement: Drift Detection Tool

The system SHALL provide a `drift_detect` async function that inspects a configured list of upstream packages against the latest released version on PyPI / HuggingFace Hub / GitHub Releases, returning a structured drift report.

The function MUST accept `packages: list[str]` (Python package names) and SHALL return a `dict` with the keys `tool_name`, `current_version`, `latest_version`, `severity` (one of `patch`, `minor`, `major`, `unreleased`, `unknown`), and `recommendation`.

#### Scenario: Major version drift detected

- **WHEN** the user calls `drift_detect(packages=["dlt"])` and `pyproject.toml` pins `dlt>=1.28.1,<2.0` while PyPI shows `dlt 1.30.0` is the latest 1.x
- **THEN** the function SHALL return `{"tool_name": "dlt", "current_version": "1.28.1", "latest_version": "1.30.0", "severity": "minor", "recommendation": "Pin to dlt>=1.30.0,<2.0 in pyproject.toml [project.dependencies]"}`
- **AND** SHALL NOT make any network call to mutate `pyproject.toml` or any other file

#### Scenario: Unknown package

- **WHEN** the user calls `drift_detect(packages=["nonexistent-pkg-xyz"])`
- **THEN** the function SHALL return `{"tool_name": "nonexistent-pkg-xyz", "severity": "unknown", "recommendation": "Package not found on PyPI — verify name"}`

### Requirement: CCC Semantic Search Tool

The system SHALL provide a `ccc_search` async function that wraps the local `bun run ccc:search` semantic-code-search command and returns parsed JSON chunks.

The function MUST accept `query: str`, optional `paths: list[str] | None`, optional `limit: int = 5`, and SHALL return `list[dict]` where each entry has `file_path`, `line_no`, `snippet`, and `relevance` (0–1).

#### Scenario: Search finds a relevant match

- **WHEN** the user calls `ccc_search(query="LANCE_DB shared lifespan pattern", paths=["cianfhoghlaim/cocoindex/_lifespan.py"])`
- **THEN** the function SHALL run `bun run ccc:search "LANCE_DB shared lifespan pattern" --paths cianfhoghlaim/cocoindex/_lifespan.py --limit 5`
- **AND** SHALL return up to 5 entries each with `file_path`, `line_no`, `snippet`, `relevance`

#### Scenario: CCC index missing

- **WHEN** `.cocoindex_code/target_sqlite.db` does not exist
- **THEN** the function SHALL auto-run `bun run ccc:init` first
- **AND** SHALL surface the init output in the function's stderr stream for the calling agent to observe

### Requirement: CCC Index Rebuild Tool

The system SHALL provide a `ccc_index` async function that rebuilds the local CocoIndex Code index from scratch and returns the count of indexed files plus duration.

The function MUST accept `paths: list[str] | None = None` and SHALL return `dict` with keys `indexed_files: int`, `duration_s: float`, and `stdout_tail: str`.

#### Scenario: Full rebuild succeeds

- **WHEN** the user calls `ccc_index(paths=None)` from the repo root
- **THEN** the function SHALL run `bun run ccc:index`
- **AND** SHALL return `{"indexed_files": <N>, "duration_s": <float>, "stdout_tail": "<last 20 lines>"}`

### Requirement: Firecrawl Refactor Discovery Tool

The system SHALL provide a `firecrawl_refactor_discover` async function that fetches the latest release notes, changelog, and breaking-change notes for a given package from its canonical upstream sources (PyPI, GitHub Releases, official blog) via the Firecrawl MCP server, and returns a structured refactoring brief.

The function MUST accept `package: str` (the package name or GitHub `owner/repo`) and optional `version_target: str | None = None`, and SHALL return a `dict` with `package`, `breaking_changes` (list of dicts each with `version`, `description`, `migration_step`), `source_urls`, and `fetched_at` (ISO timestamp).

#### Scenario: Discover dlt breaking changes

- **WHEN** the user calls `firecrawl_refactor_discover(package="dlt")`
- **THEN** the function SHALL use `firecrawl_research_search_papers` + `firecrawl_scrape` against `github.com/dlt-hub/dlt/releases` and the `dlthub` docs site
- **AND** SHALL return at least 1 entry in `breaking_changes` for each minor or major release in the past 90 days
- **AND** each entry SHALL include a concrete `migration_step`

#### Scenario: Network failure

- **WHEN** Firecrawl returns a 5xx error or times out
- **THEN** the function SHALL return `{"package": "dlt", "breaking_changes": [], "error": "firecrawl_unavailable: <status_code>"}`
- **AND** SHALL NOT raise an exception

#### Scenario: Local scrape fallback

- **WHEN** the env var `USE_LOCAL_SCRAPES=true` is set
- **THEN** the function SHALL read from the curated `stedding/ingest_queue/` snapshot instead of making a live Firecrawl call

### Requirement: HuggingFace Best Model Tool

The system SHALL provide a `hf_best_model` async function that recommends the best HuggingFace Hub model for a given task, hardware constraint, and benchmark preference, by delegating to the existing `huggingface-best` skill.

The function MUST accept `task: str`, optional `hardware: str | None = None` (e.g. `"m4-max-64gb"`, `"a100-80gb"`), optional `benchmark: str | None = None` (e.g. `"MTEB"`, `"HellaSwag"`), and SHALL return `dict` with `recommended_model` (str), `alternates` (list[str]), `benchmarks` (dict[str, float]), and `source_urls` (list[str]).

#### Scenario: Find best bge embedding model

- **WHEN** the user calls `hf_best_model(task="bge embedding for retrieval", hardware="m4-max-64gb", benchmark="MTEB")`
- **THEN** the function SHALL return at least 1 `recommended_model` whose MTEB score is within the top 5 of the published leaderboard
- **AND** SHALL include the model card URL in `source_urls`

#### Scenario: No matching model

- **WHEN** no HuggingFace model matches the task + hardware constraint
- **THEN** the function SHALL return `{"recommended_model": None, "alternates": [], "note": "no-match"}`

### Requirement: OpenSpec List + Validate Tools

The system SHALL provide `openspec_list_specs` and `openspec_validate` async functions that wrap the corresponding `openspec` CLI commands and return parsed JSON.

`openspec_list_specs` MUST accept optional `quadrant: str | None = None` and SHALL return `{"specs": list[dict]}` where each entry has `id`, `quadrant`, `one_liner`.

`openspec_validate` MUST accept `change_id: str` and SHALL return `{"valid": bool, "errors": list[str], "warnings": list[str]}`.

#### Scenario: List all specs

- **WHEN** the user calls `openspec_list_specs(quadrant=None)`
- **THEN** the function SHALL run `openspec list --specs --json`
- **AND** SHALL return all 37 specs (the existing 36 + the new `dev-env-demo-tools` once archived)

#### Scenario: Validate passes

- **WHEN** the user calls `openspec_validate(change_id="2026-07-06-add-dev-env-demo-tools-to-adk-agents")`
- **THEN** the function SHALL run `openspec validate 2026-07-06-add-dev-env-demo-tools-to-adk-agents --strict`
- **AND** SHALL return `{"valid": true, "errors": [], "warnings": []}`

#### Scenario: Validate fails on missing scenario

- **WHEN** the user calls `openspec_validate(change_id="bad-spec-without-scenario")` and the change is missing a Scenario block under an ADDED Requirement
- **THEN** the function SHALL return `{"valid": false, "errors": ["Requirement 'X' has no Scenario block"], "warnings": []}`

### Requirement: Mise Lint Skills Tool

The system SHALL provide a `mise_lint_skills` async function that runs `mise run lint:skills` and parses the 4-rule metadata validation output (frontmatter, name match, description length, line count).

The function MUST accept optional `path: str | None = None` (defaults to `.agents/skills/`) and SHALL return `dict` with `passed` (int), `failed` (int), `failures` (list of dicts each with `skill`, `rule`, `message`), and `duration_s` (float).

#### Scenario: All 123 skills pass

- **WHEN** the user calls `mise_lint_skills(path=".agents/skills/")` and all 123 skills pass the 4-rule lint
- **THEN** the function SHALL return `{"passed": 123, "failed": 0, "failures": [], "duration_s": <float>}`

#### Scenario: One skill fails the line-count rule

- **WHEN** the user calls `mise_lint_skills()` and one skill exceeds the 500-line cap
- **THEN** the function SHALL return `{"passed": 122, "failed": 1, "failures": [{"skill": "...", "rule": "line_count", "message": "..."}], "duration_s": <float>}`

### Requirement: Dev-Env Demo Agent

The system SHALL provide a `dev_env_demo_agent` Google ADK `LlmAgent` that wraps all 8 dev-env tools above, with a 7-section system prompt that demonstrates each tool and chains them in a real-world migration scenario.

The agent MUST export under `cianfhoghlaim.agents.adk.dev_env_demo_agent.dev_env_demo_agent` and SHALL refuse to mutate files (read-only by design — all tools are read or execute-CLI-with-dry-run only).

#### Scenario: Agent demos all 8 tools in one turn

- **WHEN** the user prompt is `"Demo all 8 dev-env tools"`
- **THEN** the agent SHALL call `ccc_search`, `ccc_index`, `drift_detect`, `firecrawl_refactor_discover`, `hf_best_model`, `openspec_list_specs`, `openspec_validate`, and `mise_lint_skills` in order
- **AND** SHALL produce a structured markdown report at `output_key="dev_env_demo_report"` summarising each tool's output

#### Scenario: Agent chains tools for a real migration

- **WHEN** the user prompt is `"I think lancedb might have changed its mount_table_target signature. Investigate and tell me what to do."`
- **THEN** the agent SHALL call `ccc_search` first to locate the call site, then `drift_detect(["lancedb"])`, then `firecrawl_refactor_discover("lancedb")`, then `hf_best_model` to suggest a newer bge embedding
- **AND** SHALL produce a migration brief at `output_key="dev_env_demo_report"` including the exact file path, the new signature, and a draft GitHub issue body

