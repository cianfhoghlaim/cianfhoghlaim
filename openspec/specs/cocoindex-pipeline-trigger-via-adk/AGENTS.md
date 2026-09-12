# `cocoindex-pipeline-trigger-via-adk` — Agent Routing

> `cocoindex-pipeline-trigger-via-adk` wraps CocoIndex v1 App updates as
> ADK `FunctionTool`s so the orchestrator can drive CocoIndex from any
> ADK runtime.

## Routing

Load this AGENTS.md when working on CocoIndex orchestration via ADK.

## Quick start

```bash
openspec validate 2026-09-06-adk-gemini-deep-research-control-plane-v1 --strict
```

## Key sources

- `openspec/specs/cocoindex-pipeline-trigger-via-adk/spec.md`
- `agents/adk/pipeline_orchestrator/cocoindex_index_agent.py`
- `cocoindex_flows/_shared/_lifespan.py` (shared embedder)

## Adjacent specs

- `openspec/specs/adk-deep-research-control-plane/spec.md`
- `openspec/specs/pipeline-orchestrator-agent/spec.md`
- `openspec/specs/centralized-model-registry/spec.md`

## DO NOT

- Hand-edit this file. Edit the spec and re-run the sync script.

## Skill pointers

- `cocoindex` — for CocoIndex v1 App patterns
- `openspec` — for the spec change workflow

<!-- generated: 2026-09-06; do not hand-edit -->
