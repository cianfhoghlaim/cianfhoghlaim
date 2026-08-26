# `oideachais-cocoindex-v1-migration` — Agent Routing

> The oideachais CocoIndex v1 migration surface covers the 7 v1 CocoIndex Apps (6 LC subjects + government_circulars) across the Cianfhoghlaim monorepo. It defines 1 invariant: the canonical migration p...

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

- `openspec/specs/oideachais-cocoindex-v1-migration/spec.md` — the canonical spec
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## Adjacent specs

- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## DO NOT

- Hand-edit this file (the generator will overwrite it). To customise,
  edit `openspec/specs/oideachais-cocoindex-v1-migration/spec.md` and re-run
  `uv run python scripts/sync/spec_agents.py`.

## Skill pointers

- `ccc` — for semantic code search across the spec's implementation
- `openspec` — for the spec change workflow

<!-- generated: 2026-08-25; do not hand-edit -->
