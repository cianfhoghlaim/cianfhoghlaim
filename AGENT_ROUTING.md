# Agent Routing — Subagent Dispatch Map

Use this file when a task must be delegated by `subagent_type`. The canonical runtime definitions remain in `opencode.json`; this document is the concise routing surface for agents working from repository context.

## Priority routing

| `subagent_type` | Canonical directories | `agent_count` | `primary_contact` |
|:--|:--|--:|:--|
| `data-platform` | `dlt_sources/`, `orchestration/`, `baml_src/`, `cocoindex/`, `notebooks/`, `motherduck/` | 1 | Data platform maintainer |
| `infrastructure` | `bonneagar/iac/`, `bonneagar/stacks/`, `bonneagar/komodo/`, `bonneagar/pangolin/` | 1 | Infrastructure maintainer |
| `agent-platform` | `agents/`, `meaisinfhoghlaim/` | 1 | Agent platform maintainer |
| `frontend-apps` | `web/apps/`, `web/hono-api/`, `web/packages/` | 1 | Frontend maintainer |
| `research` | `openspec/research/`, `docs/`, live upstream sources | 1 | Research maintainer |
| `notebooks` | `notebooks/` | 1 | Notebook maintainer |
| `baml` | `baml_src/`, `baml_client/` | 1 | Schema maintainer |
| `dagster` | `orchestration/` | 1 | Orchestration maintainer |
| `mise` | `mise.toml`, `scripts/` | 1 | Developer-experience maintainer |

## Dispatch rules

1. Pick the narrowest matching `subagent_type`; use a functional specialist (`notebooks`, `baml`, `dagster`, `mise`) before its broader parent.
2. Split cross-area work into parallel, directory-disjoint assignments.
3. Read the target directory's `AGENTS.md` before editing.
4. Route model or schema changes through `centralized-registry` regardless of directory.
5. Keep infrastructure changes under `bonneagar/`; never write into the separate `leabharlann/` worktree.

## Canonical references

- `opencode.json` — executable subagent registry and prompts
- `AGENTS.md` — repository rules and area ownership
- `openspec/specs/agent-registry/spec.md` — registry requirements
- `.agents/skills/INDEXING_AND_COGNITION.md` — code and documentation discovery workflow
