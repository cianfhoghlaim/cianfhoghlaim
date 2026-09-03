# `infrastructure-stacks` — Agent Routing

> `infrastructure-stacks` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_ind...

## Routing

Load this AGENTS.md when the parent spec (`./spec.md`) is in scope.
Use it to find the most relevant mise tasks + skills + adjacent files
without re-reading the full spec.

## Quick start

```bash
cic:stack-doctor              # Validate all 89 stacks against the 6-file GOLD_STANDARD
stack-doctor:strict              # CI gate + grammar check
```

## Key sources

- `openspec/specs/infrastructure-stacks/spec.md` — the canonical spec
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## Adjacent specs

- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## DO NOT

- Hand-edit this file (the generator will overwrite it). To customise,
  edit `openspec/specs/infrastructure-stacks/spec.md` and re-run
  `uv run python scripts/sync/spec_agents.py`.

## Skill pointers

- `ccc` — for semantic code search across the spec's implementation
- `openspec` — for the spec change workflow

<!-- generated: 2026-07-29; do not hand-edit -->
