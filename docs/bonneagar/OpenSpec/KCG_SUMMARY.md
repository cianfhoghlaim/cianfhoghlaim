# OpenSpec — KCG Summary

## What It Is
OpenSpec is a spec-driven development tool that formalizes the workflow: write a proposal → define tasks → draft spec deltas → validate → implement → archive. It provides a structured way to manage change in complex projects through specification files and CLI tooling.

## Why This Matters for Kings' College Galway
The `openspec/` directory at the repo root uses OpenSpec for managing all architectural changes — new infrastructure stacks, data pipeline modifications, agent workflow updates. The `bun run spec:validate`, `bun run spec:list`, and `bun run spec:archive` commands are integrated into the turbo task graph. Spec-driven development ensures changes to the 89-stack infrastructure are documented, validated, and traceable.

## Key Patterns
- **Proposal → Tasks → Spec deltas → Validate → Archive** workflow
- **Strict validation**: `openspec validate --strict` catches schema errors before implementation
- **Spec deltas**: Changes are expressed as additions/removals to specification files
- **Archive**: Completed changes are moved to `openspec/changes/archive/` for history

## Source Files
Full test suite and source code removed (2026-06-05). Available at <https://github.com/...>. Live specs are in `openspec/` at the repo root.
