# `british-isles-education-pipeline-v3` — Agent Routing

> `british-isles-education-pipeline-v3` (BIEP v3) is the v3 umbrella

## Routing

Load this AGENTS.md when the parent spec (`./spec.md`) is in scope.
Use it to find the most relevant mise tasks + skills + adjacent files
without re-reading the full spec.

## Quick start

```bash
sync:paths              # Layer 1: pre-v7 path drift
biep:v3:gate              # BIEP v3 milestone gate
```

## Key sources

- `openspec/specs/british-isles-education-pipeline-v3/spec.md` — the canonical spec
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## Adjacent specs

- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## DO NOT

- Hand-edit this file (the generator will overwrite it). To customise,
  edit `openspec/specs/british-isles-education-pipeline-v3/spec.md` and re-run
  `uv run python scripts/sync/spec_agents.py`.

## Skill pointers

- `ccc` — for semantic code search across the spec's implementation
- `openspec` — for the spec change workflow

<!-- generated: 2026-07-30; do not hand-edit -->
