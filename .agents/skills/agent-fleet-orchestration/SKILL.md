---
name: agent-fleet-orchestration
description: The KCG 12-agent fleet orchestration pattern in `meaisinfhoghlaim/agents/`. Covers the 5 frameworks (Custom/ADK/Agno/Pipecat/CopilotKit), the 12 specialist agents (root, curriculum, translation, corpus, research, education_research, bunchloch_research, geospatial, statistics, curriculum_comparison, agui_curriculum, mcp_curriculum), the LiteLLM routing keyword map, the Letta memory layer, the RisingWave event streaming layer, the Langfuse + MLflow observability stack, the cross-quadrant observability contract, and the canonical add-a-new-agent workflow. Use when adding a new agent to the fleet, debugging a routing keyword misclassification, wiring Langfuse traces, integrating with the Letta memory layer, or understanding the cross-quadrant observability contract.
---

# Agent Fleet Orchestration

## Purpose

The `meaisinfhoghlaim/agents/` directory houses a **12-agent
fleet** that spans 5 frameworks. This is genuinely novel — there
is no other skill that documents the 12-agent × 5-framework
pattern, the LiteLLM routing keyword map, the Letta memory
layer, or the cross-quadrant observability contract. The
`google-adk` and `agno` skills are framework-specific; the
`agentic-frontend-frameworks` skill covers the AG-UI protocol.
This skill covers the **orchestration** of the 12 agents into
a single fleet.

## When to use this skill

Use when you need to:

- "Add a new agent to the fleet (the 13th agent)"
- "Debug a routing keyword misclassification"
- "Wire Langfuse traces to a new agent"
- "Integrate the agent with the Letta memory layer"
- "Understand the cross-quadrant observability contract"
- "Wire the agent to the RisingWave event stream"

## The 12 agents (the fleet)

| Agent | Framework | Speciality | Langfuse trace tag |
|:--|:--|:--|:--|
| `root_agent` | Custom | The query router + orchestrator | `agent.root` |
| `curriculum_agent` | ADK | The 5-nation curriculum search (NCCA + CfE + CfW + CCEA + SQA) | `agent.curriculum` |
| `translation_agent` | ADK | The 6-Celtic-language translation | `agent.translation` |
| `corpus_agent` | ADK | The Dúchas + Gaois + UD + Canúint + Téarma corpus search | `agent.corpus` |
| `research_agent` | ADK | The long-form research + citations | `agent.research` |
| `education_research_agent` | Agno | The cross-nation education policy research (LoopAgent) | `agent.education_research` |
| `bunchloch_research_agent` | Agno | The M4 MacBook-local research (SequentialAgent) | `agent.bunchloch_research` |
| `geospatial_agent` | ADK | The LSOA / Data Zone spatial analysis | `agent.geospatial` |
| `statistics_agent` | ADK | The education metrics + benchmarking | `agent.statistics` |
| `curriculum_comparison_agent` | ADK | The cross-nation curriculum mapping | `agent.curriculum_comparison` |
| `agui_curriculum_agent` | Agno | The AG-UI streaming curriculum agent (CopilotKit consumer) | `agent.agui_curriculum` |
| `mcp_curriculum_agent` | ADK | The MCP-server-bridged curriculum agent (for external clients) | `agent.mcp_curriculum` |

The 12 agents are registered in `meaisinfhoghlaim/agents/__init__.py`
(the canonical home for the agent registry).

## The 5 frameworks (the runtime)

| Framework | Implementation | Used by |
|:--|:--|:--|
| Custom | `meaisinfhoghlaim/agents/root_agent.py` (the query router + LiteLLM) | `root_agent` |
| ADK | `google.adk.agents.LlmAgent` (via `oideachais.agents.adk.*`) | `curriculum_agent`, `translation_agent`, `corpus_agent`, `research_agent`, `geospatial_agent`, `statistics_agent`, `curriculum_comparison_agent`, `mcp_curriculum_agent` |
| Agno | `meaisinfhoghlaim/agents/agno/team.py` (the EducationTeam) | `education_research_agent`, `bunchloch_research_agent`, `agui_curriculum_agent` |
| Pipecat | `meaisinfhoghlaim/agents/voice_agent.py` (the real-time audio transport) | (the voice agent is not in the 12 above; it's a separate voice channel) |
| CopilotKit | `oideachais/agents/adk/agui_curriculum_agent.py` (the AG-UI consumer) | (the CopilotKit consumer is the front-end; it's not an agent) |

The 5 frameworks share the LiteLLM gateway at
`litellm.cianfhoghlaim.ie:4000` as the single LLM proxy.

## The LiteLLM routing keyword map (the 12-bucket)

The `root_agent` does a **keyword-based classification** of the
user query and routes to one of the 12 agents. The keyword map:

| Agent | Keywords (in priority order) |
|:--|:--|
| `curriculum_agent` | "curriculum", "spec", "learning outcome", "ncca", "cfe", "cfw", "ccea", "sqa", "leaving cert", "gcse", "a-level" |
| `translation_agent` | "translate", "gaeilge", "irish", "scottish gaelic", "welsh", "cymraeg", "brezhoneg", "cornish", "manx" |
| `corpus_agent` | "corpus", "duchas", "gaois", "tearma", "logainm", "canuint", "foclóir" |
| `research_agent` | "research", "paper", "cite", "doi", "arxiv" |
| `education_research_agent` | "policy", "report", "oecd", "european commission", "unesco" |
| `bunchloch_research_agent` | "m4", "macbook", "local model", "federated", "on-device" |
| `geospatial_agent` | "geospatial", "lsoa", "data zone", "map", "school location" |
| `statistics_agent` | "statistics", "metric", "benchmark", "performance", "kpi" |
| `curriculum_comparison_agent` | "compare", "cross-nation", "side-by-side", "uk vs ireland" |
| `agui_curriculum_agent` | "ag-ui", "streaming", "copilot", "react" |
| `mcp_curriculum_agent` | "mcp", "model context protocol", "tool" |
| `default` | (no keyword match) → `root_agent` itself |

The 12-bucket map is in `meaisinfhoghlaim/agents/root_agent.py:ROUTING_KEYWORDS`.

## The Letta memory layer (the cross-agent state)

Every agent in the fleet reads + writes to the **Letta memory
layer** at `letta.cianfhoghlaim.ie:8283` (the long-term agent
memory). The contract:

- **Per-agent memory:** `letta.get_memory(agent_id=...)` returns
  a `Memory` object with the agent's conversation history +
  user preferences + learning state
- **Per-user memory:** `letta.get_user_memory(user_id=...)` returns
  a `UserMemory` object with the user's learning progress + skill
  tree + quest history
- **Per-quest memory:** `letta.get_quest_memory(quest_id=...)`
  returns a `QuestMemory` object with the quest state + collected
  achievements

The 3 memory types are documented in
`meaisinfhoghlaim/agents/letta_client.py:MemoryType`.

## The RisingWave event stream (the cross-agent events)

Every agent in the fleet publishes events to the **RisingWave
stream** at `risingwave.cianfhoghlaim.ie:4566` (the Kafka-compatible
event bus). The contract:

- **Topic:** `agent.events` (1 topic for the whole fleet)
- **Schema:** `{"agent_id": str, "event_type": str, "user_id": str, "timestamp": int, "payload": dict}`
- **Event types:** `agent.started`, `agent.completed`, `agent.failed`,
  `agent.routed`, `tool.called`, `tool.completed`, `memory.read`,
  `memory.written`, `citation.found`

The RisingWave connector is in
`meaisinfhoghlaim/agents/risingwave_publisher.py:RisingWavePublisher`.

## The Langfuse + MLflow observability stack (the 2 traces)

Every agent in the fleet is wrapped in **2 traces**:

1. **Langfuse** (`langfuse.cianfhoghlaim.ie:3000`) — the
   per-request LLM cost + latency + prompt version
2. **MLflow** (`mlflow.cianfhoghlaim.ie:5000`) — the per-experiment
   prompt comparison + hyperparameter sweep

The 2 traces are emitted from `meaisinfhoghlaim/agents/_shared/observability/tracing.py`
via the `langfuse_trace` + `mlflow_log` decorators.

## The cross-quadrant observability contract

The agent fleet integrates with the broader KCG observability
stack:

- **Oideachais** reads the agent traces via the FastAPI middleware
  at `oideachais/middleware/agui/streaming.py`
- **Tuatha** consumes the agent output via the TanStack Start
  CopilotKit component
- **Croílár** mirrors the agent state via the Convex subscriptions
- **Spaces** expose a subset of agents via the HF Space demos

The contract is documented in
`meaisinfhoghlaim/agents/_shared/observability/cross_quadrant.py`.

## Worked example: add the 13th agent (the 4-Framework Hybrid)

1. Add the agent to `meaisinfoghlaim/agents/__init__.py`:

   ```python
   from .hybrid_curriculum_agent import hybrid_curriculum_agent
   __all__ += ["hybrid_curriculum_agent"]
   ```

2. Create `meaisinfhoghlaim/agents/hybrid_curriculum_agent.py`
   that wraps both the ADK `curriculum_agent` and the Agno
   `education_research_agent` (the "4-Framework Hybrid").

3. Add the routing keyword to
   `meaisinfhoghlaim/agents/root_agent.py:ROUTING_KEYWORDS`:

   ```python
   "hybrid_curriculum_agent": ["hybrid", "4-framework", "all frameworks"],
   ```

4. Add the Langfuse trace tag (`agent.hybrid_curriculum`) +
   the MLflow experiment name.

5. Add the Letta memory type (`HybridCurriculumMemory`).

6. Add the RisingWave event type (`agent.hybrid.completed`).

7. Add a test in `meaisinfhoghlaim/tests/test_agents.py` that
   exercises the routing + the Letta memory + the RisingWave event.

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| `root_agent` routes to the wrong agent | The keyword list is ambiguous | Add more keywords to the correct bucket |
| An agent can't find the user's memory | The Letta client lost the connection | Check the Letta server is up + the API key is correct |
| Langfuse traces are missing | The `@langfuse_trace` decorator was forgotten | Add the decorator to the new agent |
| MLflow shows 2 competing experiments | The agent was registered twice | Pick one MLflow experiment name per agent |
| RisingWave events are dropped | The publisher buffer is full | Increase `buffer_size` in `risingwave_publisher.py` |
| The cross-quadrant mirror is stale | The Convex subscription disconnected | Restart the Convex WebSocket |

## Cross-references

- `.agents/skills/google-adk/SKILL.md` — the ADK framework patterns
- `.agents/skills/agno/SKILL.md` — the Agno framework patterns
- `.agents/skills/agentic-frontend-frameworks/SKILL.md` — the AG-UI + CopilotKit consumer
- `.agents/skills/agent-observability/SKILL.md` — the Langfuse + MLflow + RAGAS + Logfire + Datadog stack
- `.agents/skills/agent-memory-systems/SKILL.md` — the Letta + Graphiti + Cognee + LanceDB + FalkorDB memory stack
- `meaisinfhoghlaim/agents/__init__.py` — the 12-agent registry
- `meaisinfhoghlaim/agents/root_agent.py` — the query router + LiteLLM
- `meaisinfhoghlaim/agents/letta_client.py` — the Letta memory layer
- `meaisinfhoghlaim/agents/risingwave_publisher.py` — the RisingWave event stream
- `meaisinfhoghlaim/agents/_shared/observability/tracing.py` — the Langfuse + MLflow traces
