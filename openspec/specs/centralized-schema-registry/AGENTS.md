# `centralized-schema-registry` — Agent Routing

> The centralized schema registry surface codifies BAML as the source of truth for schemas across the Cianfhoghlaim monorepo. It defines 5 invariants: the BAML .baml files (baml_src/) are the canonical ...

## Routing

Load this AGENTS.md when the parent spec (`./spec.md`) is in scope.
Use it to find the most relevant mise tasks + skills + adjacent files
without re-reading the full spec.

## Quick start

```bash
schema:generate              # Regenerate Zod + TanStack DB schemas
schema:validate              # CI drift gate for generated Zod schemas
```

## Key sources

- `openspec/specs/centralized-schema-registry/spec.md` — the canonical spec
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## Adjacent specs

- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## DO NOT

- Hand-edit this file (the generator will overwrite it). To customise,
  edit `openspec/specs/centralized-schema-registry/spec.md` and re-run
  `uv run python scripts/sync/spec_agents.py`.

## Skill pointers

- `ccc` — for semantic code search across the spec's implementation
- `openspec` — for the spec change workflow

<!-- generated: 2026-08-25; do not hand-edit -->
