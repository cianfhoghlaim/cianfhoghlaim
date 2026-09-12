# `adk-deep-research-control-plane` — Agent Routing

> `adk-deep-research-control-plane` is the cross-pipeline orchestration
> surface that makes Google ADK the imperative orchestrator of the
> 12-agent fleet + the browser-stack + the DLT / BAML / CocoIndex
> pipelines, and makes Gemini Deep Research API the default `RESEARCH`
> backend with feature parity to Firecrawl / Crawl4AI.

## Routing

Load this AGENTS.md when the parent spec (`./spec.md`) is in scope.
Use it to find the most relevant mise tasks + skills + adjacent files
without re-reading the full spec.

## Quick start

```bash
openspec validate 2026-09-06-adk-gemini-deep-research-control-plane-v1 --strict
mise run sync:all
```

## Key sources

- `openspec/specs/adk-deep-research-control-plane/spec.md` — the canonical spec
- `agents/adk/pipeline_orchestrator/` — the 3 pipeline-trigger agents
- `agents/adk/root_agent.py` — the new ADK SequentialAgent root
- `bonneagar/stacks/browser/sruth_browser/backends/paid/gemini_deep_research.py` — the new backend

## Adjacent specs

- `openspec/specs/agent-registry/spec.md` — the declarative registry this flips
- `openspec/specs/browser-tools/spec.md` — the browser-stack backends
- `openspec/specs/baml-schemas/spec.md` — the BAML extraction schemas
- `openspec/specs/pipeline-orchestrator-agent/spec.md` — the 3-agent bundle

## DO NOT

- Hand-edit this file (the generator will overwrite it). To customise,
  edit `openspec/specs/adk-deep-research-control-plane/spec.md` and re-run
  `uv run python scripts/sync/spec_agents.py`.

## Skill pointers

- `ccc` — for semantic code search across the spec's implementation
- `openspec` — for the spec change workflow

<!-- generated: 2026-09-06; do not hand-edit -->
