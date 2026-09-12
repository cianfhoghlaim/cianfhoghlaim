# `pipeline-orchestrator-agent` — Agent Routing

> `pipeline-orchestrator-agent` is the bundle of 3 ADK agents
> (`dlt_trigger_agent`, `cocoindex_index_agent`, `baml_extract_agent`)
> wrapped in a `SequentialAgent` called `pipeline_orchestrator` that
> drives the canonical DLT → BAML → CocoIndex pipeline from inside the
> ADK runtime.

## Routing

Load this AGENTS.md when working on the pipeline orchestrator bundle.

## Quick start

```bash
openspec validate 2026-09-06-adk-gemini-deep-research-control-plane-v1 --strict
```

## Key sources

- `openspec/specs/pipeline-orchestrator-agent/spec.md`
- `agents/adk/pipeline_orchestrator/orchestrator.py` — the SequentialAgent
- `agents/adk/pipeline_orchestrator/{dlt_trigger,cocoindex_index,baml_extract}_agent.py`

## Adjacent specs

- `openspec/specs/adk-deep-research-control-plane/spec.md`
- `openspec/specs/dlt-pipeline-trigger-via-adk/spec.md`
- `openspec/specs/cocoindex-pipeline-trigger-via-adk/spec.md`

## DO NOT

- Hand-edit this file. Edit the spec and re-run the sync script.

## Skill pointers

- `openspec` — for the spec change workflow

<!-- generated: 2026-09-06; do not hand-edit -->
