# `centralized-model-registry` — Agent Routing

> The canonical model registry surface covers the 76 entries / 7 model families (ocr_vision / text_llm / embedder / rerank / image_gen / voice / translation) across the Cianfhoghlaim monorepo. It define...

## Routing

Load this AGENTS.md when the parent spec (`./spec.md`) is in scope.
Use it to find the most relevant mise tasks + skills + adjacent files
without re-reading the full spec.

## Quick start

```bash
lint:registry              # Audit MODEL_REGISTRY
models:list              # List all 52 MODEL_REGISTRY entries
```

## Key sources

- `openspec/specs/centralized-model-registry/spec.md` — the canonical spec
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## Adjacent specs

- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the per-spec AGENTS.md convention

## DO NOT

- Hand-edit this file (the generator will overwrite it). To customise,
  edit `openspec/specs/centralized-model-registry/spec.md` and re-run
  `uv run python scripts/sync/spec_agents.py`.

## Skill pointers

- `ccc` — for semantic code search across the spec's implementation
- `openspec` — for the spec change workflow

<!-- generated: 2026-08-25; do not hand-edit -->
