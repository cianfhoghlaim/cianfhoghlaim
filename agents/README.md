# Agents

> **The Cianfhoghlaim Agent Fleet — the 12-agent fleet + 8 NCCA
> subject specialists + 3 educational agents.** A polyglot agent
> platform spanning 5 frameworks (Custom + ADK + Agno + Pipecat +
> CopilotKit) with the centralized wiring layer
> (`agents/wiring.py` + `agents/agent_registry.py`), the 5-layer
> observability stack, the 5-backend memory layer, and the 4
> shared async dispatchers.

## Quick start

For the canonical quadrant overview, see
[`agents/AGENTS.md`](AGENTS.md). It covers:

- The 12-agent fleet + the 8 NCCA subject specialists + the 3 educational agents
- The 5-framework runtime (Custom + ADK + Agno + Pipecat + CopilotKit)
- The 5-layer observability stack (Langfuse + Logfire + MLflow + RAGAS + structlog)
- The 5-backend memory layer (Cognee + Graphiti + LanceDB + FalkorDB + Memgraph)
- The 4 shared async dispatchers
- Quick routing for "I want to add X, where do I go?"

For the current state of each agent, see
[`agents/STATUS.md`](STATUS.md). For how to add a new agent, see
[`agents/DEVELOPMENT.md`](DEVELOPMENT.md). For how to reproduce
the fleet from zero, see [`agents/REPRODUCER.md`](REPRODUCER.md).

## Cross-References

- The main agent architecture: [`AGENTS.md`](../AGENTS.md)
- The skills library: [`.agents/skills/`](../.agents/skills/)
- The 12-agent fleet: [`agents/agent_registry.py`](agent_registry.py)
- The wiring layer: [`agents/wiring.py`](wiring.py)
- The 5-layer observability: [`agents/observability_hooks.py`](observability_hooks.py)
- The 5-backend memory layer: [`agents/memory_layer.py`](memory_layer.py)
- The 4 async dispatchers: [`agents/_workflow_handlers.py`](_workflow_handlers.py)
- The canonical exceptions: [`agents/exceptions.py`](exceptions.py)
- The Pydantic v2 base models: [`agents/pydantic_models.py`](pydantic_models.py)

## Sub-package AGENTS.md

- [`agents/api/AGENTS.md`](api/AGENTS.md) — the Hono API routes
- [`agents/tools/AGENTS.md`](tools/AGENTS.md) — the 9 tool modules
- [`agents/meaisinfhoghlaim/AGENTS.md`](meaisinfhoghlaim/AGENTS.md) — the OCR/HTR sub-package
- [`agents/tuatha/AGENTS.md`](tuatha/AGENTS.md) — the 8 NCCA subject specialists