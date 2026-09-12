# `dlt-pipeline-trigger-via-adk` — Agent Routing

> `dlt-pipeline-trigger-via-adk` wraps DLT pipeline invocations as ADK
> `FunctionTool`s so the orchestrator can drive DLT from any ADK runtime.

## Routing

Load this AGENTS.md when working on DLT pipeline orchestration via ADK.

## Quick start

```bash
openspec validate 2026-09-06-adk-gemini-deep-research-control-plane-v1 --strict
```

## Key sources

- `openspec/specs/dlt-pipeline-trigger-via-adk/spec.md`
- `agents/adk/pipeline_orchestrator/dlt_trigger_agent.py`
- `dlt_sources/_shared/gemini_deep_research.py`

## Adjacent specs

- `openspec/specs/adk-deep-research-control-plane/spec.md`
- `openspec/specs/pipeline-orchestrator-agent/spec.md`

## DO NOT

- Hand-edit this file. Edit the spec and re-run the sync script.

## Skill pointers

- `dlt` — for DLT source patterns
- `openspec` — for the spec change workflow

<!-- generated: 2026-09-06; do not hand-edit -->
