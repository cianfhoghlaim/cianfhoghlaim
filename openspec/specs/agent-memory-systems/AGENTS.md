# `agent-memory-systems` — Agent Routing

> `agent-memory-systems` is a capability of the Cianfhoghlaim platform. The

## Routing

Load this AGENTS.md when the parent spec (`./spec.md`) is in scope.
Use it to find the most relevant mise tasks + skills + adjacent files
without re-reading the full spec.

## Quick start

```bash
agents:smoke              # Run the 3 agent-fleet smoke tests
lint:registry              # Audit MODEL_REGISTRY hardcoded strings
```

## Key sources

- `openspec/specs/agent-memory-systems/spec.md` — the canonical spec
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## Adjacent specs

- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## DO NOT

- Hand-edit this file (the generator will overwrite it). To customise,
  edit `openspec/specs/agent-memory-systems/spec.md` and re-run
  `uv run python scripts/sync/spec_agents.py`.

## Skill pointers

- `ccc` — for semantic code search across the spec's implementation
- `openspec` — for the spec change workflow

<!-- generated: 2026-07-29; do not hand-edit -->
