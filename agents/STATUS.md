# Agents Status — Current State of Each Agent

> **Snapshot 2026-08-14** — the 12-agent fleet + 8 NCCA subject
> specialists + 3 educational agents. Wired through the canonical
> `AGENT_REGISTRY` (added by the
> `2026-08-14-agents-fleet-wiring-parity-v1` change).

## State legend

- **Wired** — the agent is in `AGENT_REGISTRY`, has a `WireAgent`
  populated, all 5 observability layers + 5 memory backends
  available.
- **Partially wired** — the agent is in `AGENT_REGISTRY` but at
  least one observability layer or memory backend is missing.
- **In progress** — the agent is being migrated to the new
  wiring layer (work in flight).
- **Back-compat** — the agent is re-exported through
  `AGENT_REGISTRY` via `agents/tuatha/wiring.py`.

## The 12 main agents

| Agent | Framework | Status | Notes |
|:--|:--|:--|:--|
| `root_agent` | Custom | **Wired** | The query router + orchestrator. Routed through LiteLLM. |
| `curriculum_agent` | ADK | **Wired** | The 5-nation curriculum search. |
| `translation_agent` | ADK | **Wired** | The 6-Celtic-language translation. |
| `corpus_agent` | ADK | **Wired** | The Dúchas + Gaois + UD + Canúint + Téarma corpus search. |
| `research_agent` | ADK | **Wired** | The long-form research + citations. |
| `education_research_agent` | Agno | **Wired** | The cross-nation education policy research (LoopAgent). |
| `bunchloch_research_agent` | Agno | **Wired** | The M4 MacBook-local research (SequentialAgent). |
| `geospatial_agent` | ADK | **Wired** | The LSOA / Data Zone spatial analysis. |
| `statistics_agent` | ADK | **Wired** | The education metrics + benchmarking. |
| `curriculum_comparison_agent` | ADK | **Wired** | The cross-nation curriculum mapping. |
| `agui_curriculum_agent` | Agno | **Wired** | The AG-UI streaming curriculum agent (CopilotKit consumer). |
| `mcp_curriculum_agent` | ADK | **Wired** | The MCP-server-bridged curriculum agent. |

## The 8 NCCA subject specialists (back-compat)

| Agent | Subject | Status | Notes |
|:--|:--|:--|:--|
| `gael_agent` | Gaeilge | **Back-compat** | Re-exported via `agents/tuatha/wiring.py`. Tuatha Dé: Ogma. |
| `math_agent` | Mathematics | **Back-compat** | Re-exported. Tuatha Dé: The Dagda. |
| `appm_agent` | Applied Mathematics | **Back-compat** | Re-exported. Tuatha Dé: Lugh. |
| `chem_agent` | Chemistry | **Back-compat** | Re-exported. Tuatha Dé: Dian Cecht. |
| `comp_agent` | Computer Science | **Back-compat** | Re-exported. Tuatha Dé: — (modern subject). |
| `engl_agent` | English | **Back-compat** | Re-exported. Tuatha Dé: Brigid. |
| `geog_agent` | Geography | **Back-compat** | Re-exported. Tuatha Dé: Manannán mac Lir. |
| `hist_agent` | History | **Back-compat** | Re-exported. Tuatha Dé: The Morrígan. |

## The 3 educational agents

| Agent | Framework | Status | Notes |
|:--|:--|:--|:--|
| `academic_history_agent` | ADK | **Partially wired** | The cross-archive academic history. Still needs the new wiring layer integration. |
| `celtic_grammar_agent` | ADK | **Partially wired** | The Celtic grammar specialist. Still needs the new wiring layer integration. |
| `celtic_morphology_agent` | ADK | **Partially wired** | The Celtic morphology specialist. Still needs the new wiring layer integration. |

## The 5 framework stubs (deferred)

| Framework | Stub | Status | Notes |
|:--|:--|:--|:--|
| Pipecat | `agents/voice_agent.py` | **Deferred** | Real-time audio transport. Will become the `voice_agent` once the voice channel ships. |
| CopilotKit | `agents/adk/agui_curriculum_agent.py` (consumer) | **Deferred** | The CopilotKit consumer is the front-end; not an agent in itself. |

## The 5-layer observability stack

| Layer | Class | Status |
|:--|:--|:--|
| 1 | `LangfuseLogger` | **Wired** |
| 2 | `LogfireSpan` | **Wired** |
| 3 | `MLflowTracker` | **Wired** |
| 4 | `RAGASScorer` | **Wired** (heuristic fallback) |
| 5 | `structlogLogger` | **Wired** |

## The 5-backend memory layer

| Backend | Port | Status | Notes |
|:--|--:|:--|:--|
| Cognee | 8000 | **Production** | Structured knowledge graph (entities + relationships). |
| Graphiti | 8001 | **Production** | Temporal knowledge graph (bi-temporal). |
| LanceDB | 8002 | **Production** | Vector RAG (HNSW). |
| FalkorDB | 8003 | **Production** | Vector + graph hybrid (Redis-compatible). |
| Memgraph | 7687 | **Production** | Production graph (Cypher + MAGE). |

The cascade falls through to `in_memory_fallback` when all 5 are
unreachable.

## The 4 shared async dispatchers

| Dispatcher | Status | Notes |
|:--|:--|:--|
| `dispatch_study_plan` | **Wired** | Routes to curriculum_agent + NCCA subject agent. |
| `dispatch_deep_research` | **Wired** | Routes to research_agent / education_research_agent / bunchloch_research_agent. |
| `dispatch_literature_review` | **Wired** | Routes to corpus_agent + research_agent. |
| `dispatch_summary` | **Wired** | Routes to corpus_agent / translation_agent / statistics_agent. |

## The canonical exceptions

| Exception | Status | Notes |
|:--|:--|:--|
| `AgentError` | **Wired** | Base class for all agent-fleet exceptions. |
| `AgentConfigError` | **Wired** | Configuration error (missing dep, invalid path). |
| `AgentRuntimeError` | **Wired** | Runtime error during agent execution. |
| `AgentTimeoutError` | **Wired** | Agent execution timed out. |
| `AgentMemoryError` | **Wired** | Memory backend error. |
| `AgentObservabilityError` | **Wired** | Observability backend error. |
| `AgentDependencyMissingError` | **Wired** | Required dependency missing. |
| `with_retry()` | **Wired** | Retry decorator with exponential backoff. |
| `graceful_degradation` | **Wired** | Context manager that swallows dep-missing exceptions. |

## Production-ise status

| Test | Status | Notes |
|:--|:--|:--|
| `tests/test_agent_fleet_smoke.py` | **Written** (5 scenarios) | Will land with the change. |
| `tests/test_agent_wiring_audit.py` | **Written** (direct-import audit) | Will land with the change. |
| `tests/test_agent_registry_smoke.py` | **Written** (4 scenarios) | Will land with the change. |
| `scripts/reproducers/agents-fleet-reproducer.sh` | **Written** (6 commands) | Will land with the change. |
| `mise run agents:smoke` | **Defined** | Will land with the change. |
| `mise run agents:audit` | **Defined** | Will land with the change. |

## IaC status

| Procedure | Status | Notes |
|:--|:--|:--|
| `bonneagar/komodo/procedures/deploy-agent-fleet-bunchloch.toml` | **Written** | 4-stage omnibus for bunchloch. |
| `bonneagar/komodo/procedures/deploy-agent-fleet-arm1-oci.toml` | **Written** | 6-stage omnibus with `preflight:arm-oci`. |
| `bonneagar/komodo/procedures/deploy-agent-fleet-arm1-oci-cci.toml` | **Written** | 5-stage operator-monitoring variant. |
| `bonneagar/deploy-runbooks/agent-fleet-bunchloch-2026-08.md` | **Written** | Operator runbook for bunchloch. |
| `bonneagar/deploy-runbooks/agent-fleet-arm1-oci-2026-08.md` | **Written** | Operator runbook for arm1-oci. |

## Spec lock status

| Spec | Status | Notes |
|:--|:--|:--|
| `meaisinfhoghlaim-agent-frameworks` | **+3 ADDED Requirements** | 12-agent wiring, 4 dispatchers, graceful degradation. |
| `agent-observability` | **+2 ADDED Requirements** | 5-layer observability hooks, observability contract verification. |
| `agent-memory-systems` | **+2 ADDED Requirements** | 5-backend MemoryLayer Protocol, graceful degradation. |
| `agent-platform-cluster` | **+3 ADDED Requirements** | 3 bundling procedures, 2 operator runbooks. |

## Last verified

- **Date**: 2026-08-14
- **Verified by**: the openspec change
  `2026-08-14-agents-fleet-wiring-parity-v1`
- **Acceptance gates**: 10/10 passed (validated via
  `openspec validate --strict` + AST parse + runtime import test)