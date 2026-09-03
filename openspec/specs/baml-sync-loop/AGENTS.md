# `baml-sync-loop` — Agent Routing

> The Layer 7 of the 6-layer pull-based sync architecture. Validates the 320 .baml files (558 functions + 838 classes + 288 enums + 33 LLM clients) + closes the biggest remaining gap in the sync loop.

## Routing

Load this AGENTS.md when the parent spec (`./spec.md`) is in scope.
Use it to find the most relevant mise tasks + skills + adjacent files
without re-reading the full spec.

## Quick start

```bash
sync:all              # Run all 7 sync layers
lint:drift-docs              # Validate every AGENTS.md number claim
```

## Key sources

- `openspec/specs/baml-sync-loop/spec.md` — the canonical spec
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## Adjacent specs

- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## DO NOT

- Hand-edit this file (the generator will overwrite it). To customise,
  edit `openspec/specs/baml-sync-loop/spec.md` and re-run
  `uv run python scripts/sync/spec_agents.py`.

## Skill pointers

- `ccc` — for semantic code search across the spec's implementation
- `openspec` — for the spec change workflow

<!-- generated: 2026-07-30; do not hand-edit -->
