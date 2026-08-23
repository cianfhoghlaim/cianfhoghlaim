# 2026-08-23 — Document the OpenCode agent dispatch matrix in AGENTS.md

## Why

The repo has **15 agents** under `.opencode/agents/*.md` + 15 entries in
`opencode.json` under the `agent` key. The previous dev-tooling refactor
established this structure but never documented:

1. **The 3-tier organization** (4 primary + 5 functional subagents + 10 domain subagents)
2. **When to dispatch each tier** (build for general, functional subagent for surface-specific, domain subagent for authoring tasks)
3. **The constraint that `research` is read-only** (cannot make changes)

The Plan's Phase 3A.2 identified this as a coverage gap: new agents
reading AGENTS.md had no idea what subagent to dispatch for a given
task.

## What changes

### 1. `AGENTS.md` — add a new "OpenCode Agent Dispatch Matrix" section

After the existing "## Best Practices" section, add a new section
documenting all 15 agents organized by tier:

| Tier | Count | Examples |
|:--|:--|:--|
| Primary | 4 | `build`, `plan` |
| Functional subagent | 5 | `data-platform`, `infrastructure`, `agent-platform`, `frontend-apps`, `research` |
| Domain subagent | 10 | `baml`, `dagster`, `mise`, `notebooks`, `orchestrator`, `proposal-author`, `deep-cuts`, `dev-env-demo` |

The section also documents the dispatch rules (always use `build` for
general tasks, prefer a functional subagent for surface-specific work,
prefer a domain subagent for authoring).

## Dependencies

- **Blocked by:** none
- **Affected repos:** cianfhoghlaim only
- **Out of scope:** any code/config changes (this is docs-only)

## Acceptance criteria

1. `AGENTS.md` contains a new "OpenCode Agent Dispatch Matrix" section listing all 15 agents
2. The dispatch rules are documented (build/functional/domain)
3. The `research`-is-read-only constraint is documented
4. `openspec validate 2026-08-23-agent-opencode-agent-coverage-expansion-v1 --strict` exits 0
5. `mise run lint:drift-docs` still passes (no count drift)

## Rollback plan

- `git checkout` AGENTS.md (revert to the pre-change version)
- No code changes; no API changes; no migration
