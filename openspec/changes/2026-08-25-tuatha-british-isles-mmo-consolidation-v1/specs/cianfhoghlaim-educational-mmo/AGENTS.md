# `cianfhoghlaim-educational-mmo` — Agent Routing

> `cianfhoghlaim-educational-mmo` is the canonical capability
> for the **British Isles Formative Assessment MMO** — the spec
> the new `tuatha/` sub-project implements. The new
> `tuatha-british-isles-mmo` spec (added by the
> `2026-08-25-tuatha-british-isles-mmo-consolidation-v1`
> change) is the implementation surface.

## Routing

Load this AGENTS.md when the parent spec (`./spec.md`) is in scope.
Use it to find the most relevant mise tasks + skills + adjacent files
without re-reading the full spec.

## Quick start

```bash
sync:all              # Run all 7 sync layers
lint:drift-docs              # Validate every AGENTS.md number claim
# (the actual implementation is the new tuatha/ sub-project)
```

## Key sources

- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — the canonical spec
- `openspec/specs/tuatha-british-isles-mmo/spec.md` — the new
  implementation surface (added by the consolidation change)
- `openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/`
  — the consolidation change
- `openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/`
  — the sibling tangent (the media_intel work)
- `openspec/changes/2026-08-21-biiep-hackathon-agentic-educational-system-v1/`
  — the sibling tangent (the 4 hackathon features)
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## Adjacent specs

- `openspec/specs/tuatha-british-isles-mmo/spec.md` — the new
  implementation surface
- `openspec/specs/tuatha-platform/spec.md` — the DEPRECATED
  spec (superseded by this one)
- `openspec/specs/agent-platform-cluster/spec.md` — the 8-stack
  agent cluster IaC
- `openspec/specs/agentic-frontend-frameworks/spec.md` — the
  TanStack Start + Convex + Hono + CopilotKit + AG-UI

## DO NOT

- Hand-edit this file (the generator will overwrite it). To customise,
  edit `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` and re-run
  `uv run python scripts/sync/spec_agents.py`.

## Skill pointers

- `ccc` — for semantic code search across the spec's implementation
- `openspec` — for the spec change workflow

<!-- generated: 2026-07-29; do not hand-edit -->
