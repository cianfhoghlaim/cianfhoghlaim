## MODIFIED Requirements

### Requirement: 12 Agents × 5 Dagster Assets per Agent (L5 Agent Operations)

The `meaisinfhoghlaim-platform` capability SHALL emit every agent
in the 12-agent fleet through `CelticAgentOpsComponent`, which
registers exactly 5 Dagster assets per agent:

1. `agent_health_{name}` — `compute_kind="adk"|"agno"|"custom"` —
   pings the agent's HTTP endpoint and reports `latency_ms` +
   `last_observed_at` as MaterializeResult metadata. Schedule:
   `AutomationCondition.cron("*/5 * * * *")`.
2. `agent_routing_{name}` — verifies the agent's `routing_keywords`
   are registered in `meaisinfhoghlaim/agents/root_agent.py:ROUTING_KEYWORDS`
   and the keyword classification returns the expected bucket.
3. `agent_memory_{name}` — reads + writes a sentinel record to
   the agent's Letta memory namespace (`letta.cianfhoghlaim.ie:8283`)
   to verify the memory backend is reachable.
4. `agent_event_{name}` — publishes a `agent.{name}.ready` event
   to the RisingWave stream at `risingwave.cianfhoghlaim.ie:4566`
   to verify the event bus is reachable.
5. `agent_trace_{name}` — emits a Langfuse trace (v3 OTLP/HTTP)
   tagged with `agent.{name}` and a synthetic `agent_smoke_test`
   span. **Per user direction, the synthetic smoke-test span is
   dropped** (`MaterializeResult(metadata={"langfuse_span_dropped":
   True, "trace_tag": ...})`) so the trace history is not polluted.

The 12 agents map to the L5 sub-folders as follows:

| Framework | Agents | L5 sub-folder |
|:--|:--|:--|
| Custom | `root_agent` (1) | `5_agent_ops/custom/` |
| ADK | 8 agents (`curriculum_agent`, `translation_agent`, `corpus_agent`, `research_agent`, `geospatial_agent`, `statistics_agent`, `curriculum_comparison_agent`, `mcp_curriculum_agent`) | `5_agent_ops/adk/` |
| Agno | 3 agents (`education_research_agent`, `bunchloch_research_agent`, `agui_curriculum_agent`) | `5_agent_ops/agno/` |
| Pipecat | `voice_agent` (1) | **DEFERRED to a follow-on change** per user direction |

Total emitted in this change: 12 agents × 5 assets = **60 new L5
assets** added to the Dagster graph in the
`5_agent_ops/{custom|adk|agno}/` group.

The `routing_keywords` list is APPENDED to
`meaisinfhoghlaim/agents/root_agent.py:ROUTING_KEYWORDS` at
Component scaffold time, so a new agent's keywords are routable
in the root_agent without a manual code edit.

#### Scenario: A developer scaffolds a new agent via the Component

- **WHEN** `dg scaffold defs CelticAgentOpsComponent hybrid_curriculum_agent --agent-name hybrid_curriculum_agent --framework agno --memory-backend letta --event-stream risingwave --langfuse-trace-tag agent.hybrid_curriculum --routing-keywords hybrid 4-framework all-frameworks` runs
- **THEN** a YAML defs file is created at `defs/5_agent_ops/agno/hybrid_curriculum_agent/defs.yaml`
- **AND** 5 new assets are emitted: `5_agent_ops/agno/hybrid_curriculum_agent/agent_health_hybrid_curriculum_agent`, `agent_routing_*`, `agent_memory_*`, `agent_event_*`, `agent_trace_*`
- **AND** the 3 keywords `["hybrid", "4-framework", "all-frameworks"]` are appended to `root_agent.py:ROUTING_KEYWORDS["hybrid_curriculum_agent"]`
- **AND** `dg check yaml` reports the new assets pass
- **AND** `dg list defs` shows 5 new assets in the `5_agent_ops/agno/` group

#### Scenario: All 5 emitted assets materialise for a healthy agent

- **GIVEN** `5_agent_ops/adk/curriculum_agent/{health,routing,memory,event,trace}` are emitted
- **WHEN** `dg launch --select "5_agent_ops/adk/curriculum_agent/*"` runs
- **THEN** all 5 assets materialise successfully
- **AND** `agent_health_curriculum_agent` returns `MaterializeResult(metadata={"latency_ms": <ms>, "last_observed_at": <iso>})`
- **AND** `agent_routing_curriculum_agent` verifies the keyword `curriculum` is in the `ROUTING_KEYWORDS["curriculum_agent"]` bucket
- **AND** `agent_memory_curriculum_agent` confirms Letta memory read+write succeeded
- **AND** `agent_event_curriculum_agent` publishes the `agent.curriculum_agent.ready` event to RisingWave at `risingwave.cianfhoghlaim.ie:4566`
- **AND** `agent_trace_curriculum_agent` returns `MaterializeResult(metadata={"langfuse_span_dropped": True, "trace_tag": "agent.curriculum"})` (per user direction, no trace is persisted)

#### Scenario: A missing agent endpoint fails the health asset and blocks downstream L2 assets

- **GIVEN** the `curriculum_agent` HTTP endpoint at `adk.cianfhoghlaim.ie:7777/curriculum/health` returns 503
- **WHEN** `dg launch --select 5_agent_ops/adk/curriculum_agent/agent_health_curriculum_agent` runs
- **THEN** the asset materialises with `MaterializeResult(metadata={"healthy": false, "status_code": 503})`
- **AND** a Sensor is fired (`5_agent_ops/adk/curriculum_agent_down`) that pages the operator via n8n
- **AND** the downstream `2_materials/baml_extraction/leaving_cert_math` asset is BLOCKED via `AutomationCondition.all_deps_blocked()` until the health asset recovers

#### Scenario: The pipecat voice agent is deferred

- **WHEN** `dg list defs --json | jq '.[] | .group_name' | grep pipecat` runs
- **THEN** 0 hits SHALL appear (the `5_agent_ops/pipecat/` sub-folder is intentionally absent in this change)
- **AND** a follow-on change `2026-07-add-pipecat-voice-agent-to-l5` (tracked but out of scope here) will add the 13th L5 sub-folder + 5 emitted assets
