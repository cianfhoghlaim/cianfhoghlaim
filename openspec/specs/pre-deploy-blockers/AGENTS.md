# `pre-deploy-blockers` — Agent Routing

> The 3 pre-deploy blockers (GitHub issues #81 image digest pinning, #82 arm1-oci headroom check, #107 T1 stack docs follow-up) that have been open since 2026-06-26 / 2026-07-10. The 2 Komodo deploy pro...

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

- `openspec/specs/pre-deploy-blockers/spec.md` — the canonical spec
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## Adjacent specs

- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## DO NOT

- Hand-edit this file (the generator will overwrite it). To customise,
  edit `openspec/specs/pre-deploy-blockers/spec.md` and re-run
  `uv run python scripts/sync/spec_agents.py`.

## Skill pointers

- `ccc` — for semantic code search across the spec's implementation
- `openspec` — for the spec change workflow

<!-- generated: 2026-07-30; do not hand-edit -->
