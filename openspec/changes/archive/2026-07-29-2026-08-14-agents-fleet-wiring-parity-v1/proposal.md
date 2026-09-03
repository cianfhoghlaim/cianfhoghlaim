## Superseded by recent IaC commits

All work proposed here has been shipped in the IaC cluster's recent commits. See the bons-locker-shim v0.2.0 release + the IaC stack contract reconciliation + the agent-platform cluster deploy for the authoritative record.

# Agent-Fleet Wiring Parity — Centralise the 12-agent fleet + 8 NCCA subject specialists + 3 educational agents

## Why

The Cianfhoghlaim agent-platform surface (`agents/`) has accumulated
4 classes of structural debt that block the agent-platform cluster
from converging to the same standard the `tuatha/`, `bonneagar/`,
and `dlt_sources/` work has established:

1. **No central `agents/wiring.py`** — the 12 main agents
   (root_agent + 8 ADK + 3 Agno) each wire their own Langfuse /
   Logfire / MLflow / Letta / Cognee dependencies a different way.
   Compare `agents/tuatha/wiring.py:SubjectAgentWiring` (the canonical
   pattern for the 8 NCCA subjects) — it does not exist for the 12
   main agents.
2. **No `agents/AGENTS.md`** — `agents/README.md` is 11 lines of
   stub. The tuatha quadrant has 204 lines covering the 12-bucket
   routing keyword map, the 5-framework runtime, the cross-quadrant
   observability contract. The agents quadrant has none of this.
3. **No IaC integration** — the agent-platform cluster (hermes +
   openclaw + openchamber + litellm + langfuse + lakehouse + mlflow +
   cognee + graphiti + lancedb) is deployed ad-hoc via `docker compose up`.
   `bonneagar/komodo/procedures/` IaC has `deploy-agent-platform-cluster-arm1-oci`
   but no equivalent for the 12 main agents.
4. **No production-ise tests** — `tests/test_memory_backend_smoke.py`
   (3 scenarios) covers the 8 NCCA subject agents' memory wiring.
   The 12 main agents have no equivalent smoke test, no direct-import
   audit, no reproducer shell script.

The recent stack improvements (the `tuatha-platform` →
`cianfhoghlaim-educational-mmo` retirement, the v7 flattening, the
`2026-07-13-storage-memory-facade-v1` production-ise, the
`2026-08-04-skill-and-mcp-migration-v1` repo-boundary lockdown, the
`2026-08-06-biep-v3-critical-path-fixes-v1` namespace fixes) have
established a **canonical 4-phase pattern** for adding new domain
areas:

- **Phase 1**: Centralize the wiring (analog of
  `agents/tuatha/wiring.py` + `dlt/common/site_crawler.py`)
- **Phase 2**: Document the area (analog of `agents/tuatha/AGENTS.md`
  + `bonneagar/AGENTS.md`)
- **Phase 3**: Production-ise + add IaC (analog of
  `tests/test_memory_backend_smoke.py` + `bonneagar/komodo/`)
- **Phase 4**: Lock the spec (analog of `meaisinfhoghlaim-agent-frameworks`
  ADDED Requirements)

This change closes the 4 gaps for `agents/` in one atomic pass.

## What Changes

### Phase 1 — Centralize the Agent Fleet (Wiring parity) (~1,750 LOC)

| File | Status | Purpose |
|:--|:--|:--|
| `agents/wiring.py` | NEW | `AgentFleetWiring` dataclass covers 12 main agents × module path × BAML prefix × Langfuse trace × Cognee dataset × Letta agent_id × LiteLLM routing key × framework tuple. Mirror of `agents/tuatha/wiring.py:SubjectAgentWiring`. |
| `agents/_workflow_handlers.py` | NEW | 4 shared async dispatcher functions: `dispatch_study_plan`, `dispatch_deep_research`, `dispatch_literature_review`, `dispatch_summary`. |
| `agents/agent_registry.py` | NEW | `AGENT_REGISTRY` dict: 12 entries mapping `agent_name` → `AgentFleetWiring` instance. The single source of truth. |
| `agents/observability_hooks.py` | NEW | `LangfuseLogger` + `LogfireSpan` + `MLflowTracker` + `RAGASScorer` + `structlogLogger` — the 5-layer observability wiring in one place. |
| `agents/memory_layer.py` | NEW | `MemoryLayer` Protocol + 5 concrete backends (Cognee + Graphiti + LanceDB + FalkorDB + Memgraph) + cached factory. |
| `agents/exceptions.py` | NEW | Canonical `AgentError` hierarchy + `with_retry()` decorator + `graceful_degradation` context manager. |
| `agents/pydantic_models.py` | NEW | Standardized Pydantic v2 base models for the 12 agents: `AgentRequest`, `AgentResponse`, `AgentContext`, `AgentTrace`. |
| `agents/__init__.py` | MODIFIED | Re-export the 7 new modules + the `AGENT_REGISTRY` dict + `attach_observability` + `attach_memory` + `dispatch_*` shortcuts. |
| `agents/{adk,agno}/<slug>_agent.py` (12 files) | MODIFIED | Each agent adopts the new wiring via `attach_observability(wiring)` + `attach_memory(wiring)` 1-liners. Zero behavioural change. |
| `agents/adk/root_agent.py` | MODIFIED | Re-export the 12 main agent modules + their wiring. |
| `agents/tuatha/wiring.py` | MODIFIED | Re-export the 8 NCCA subject wirings through the `AGENT_REGISTRY`. |

### Phase 2 — Documentation Parity (~2,000 LOC across 8 files)

| File | Status | Purpose |
|:--|:--|:--|
| `agents/AGENTS.md` | NEW (rewrite the 11-line stub) | Full quadrant AGENTS.md mirroring `agents/tuatha/AGENTS.md` (204 lines). |
| `agents/STATUS.md` | NEW | Current state of each of the 12 + 8 + 3 agents. |
| `agents/DEVELOPMENT.md` | NEW | "How to add a new agent to the fleet" — 8-step recipe. |
| `agents/REPRODUCER.md` | NEW | How to reproduce the agent-platform cluster from zero. |
| `agents/api/AGENTS.md` | NEW | Hono routes layer (8 route categories + 3 endpoint patterns). |
| `agents/tools/AGENTS.md` | NEW | Tools layer (9 tool modules + the dispatch pattern). |
| `agents/meaisinfhoghlaim/AGENTS.md` | NEW | OCR/HTR/alignment sub-package (10 OCR backends + 4 ensemble patterns + 3 alignment primitives). |
| `agents/tuatha/AGENTS.md` | MODIFIED | Post-v7 path updates + new wiring layer reference. |
| `agents/README.md` | MODIFIED | Replace 11-line stub with 30-line quick-start pointing to `agents/AGENTS.md`. |

### Phase 3 — Production-ise & Reproducibility (~600 LOC)

| File | Status | Purpose |
|:--|:--|:--|
| `tests/test_agent_fleet_smoke.py` | NEW | 5 smoke-test scenarios: factory resolve, wire metadata, dispatch happy path, missing-dep graceful degradation, retry-on-failure. |
| `tests/test_agent_wiring_audit.py` | NEW | Direct-import audit: 0 matches of `langfuse_client\|cognee_client\|letta_client\|graphiti_client\|falkordb_client\|memgraph_client` per agent. |
| `tests/test_agent_registry_smoke.py` | NEW | 4 scenarios: AGENT_REGISTRY has 12 entries, frameworks tuple is valid, Cognee dataset names match, Langfuse trace names match. |
| `scripts/reproducers/agents-fleet-reproducer.sh` | NEW | Operator's one-shot: 6 commands from cold to green. |
| `mise.toml` | MODIFIED | `agents:smoke` + `agents:audit` tasks. |

### Phase 4 — IaC Integration (Bonneagar parity) (~800 LOC)

| File | Status | Purpose |
|:--|:--|:--|
| `bonneagar/komodo/procedures/deploy-agent-fleet-bunchloch.toml` | NEW | Bundling procedure for bunchloch (4-stage omnibus). |
| `bonneagar/komodo/procedures/deploy-agent-fleet-arm1-oci.toml` | NEW | Bundling procedure for arm1-oci (6-stage omnibus with `preflight:arm-oci`). |
| `bonneagar/komodo/procedures/deploy-agent-fleet-arm1-oci-cci.toml` | NEW | Bundling procedure for the `arm1-oci-cci` variant (5-stage operator-monitoring). |
| `bonneagar/deploy-runbooks/agent-fleet-bunchloch-2026-08.md` | NEW | Operator runbook for bunchloch. |
| `bonneagar/deploy-runbooks/agent-fleet-arm1-oci-2026-08.md` | NEW | Operator runbook for arm1-oci (with WARP + Locket). |
| `bonneagar/pangolin/agent-fleet.yaml` | NEW | Agent-fleet public/private resource definitions. |
| `bonneagar/blueprints/agent-fleet-bp.yaml` | NEW | Pangolin site blueprint for the agent-platform cluster. |
| `bonneagar/scripts/validate-stacks.ts` | MODIFIED | Add the 3 new agent-fleet procedures to the validation set. |

### Phase 5 — Spec Lock (4 spec deltas)

| Spec | Change | Requirements |
|:--|:--|:--|
| `meaisinfhoghlaim-agent-frameworks` | MODIFIED | +3 ADDED Requirements: "12-agent fleet wiring via `agents/wiring.py`", "shared `_workflow_handlers.py`" with 4 dispatchers, "graceful degradation on missing dep" |
| `agent-observability` | MODIFIED | +2 ADDED Requirements: "shared 5-layer observability hooks via `agents/observability_hooks.py`", "observability contract verification" |
| `agent-memory-systems` | MODIFIED | +2 ADDED Requirements: "shared `MemoryLayer` Protocol via `agents/memory_layer.py`" with 5 backends, "graceful degradation when memory backend unavailable" |
| `agent-platform-cluster` | MODIFIED | +3 ADDED Requirements: "Bundling procedure `deploy-agent-fleet-bunchloch`", "Bundling procedure `deploy-agent-fleet-arm1-oci`", "operator runbooks `agent-fleet-*-2026-08.md`" |

## Dependencies

```yaml
Blocked by: none (the 3 v3 BIEP changes below are soft blockers)
Blocked by (soft): 2026-08-08-biep-v3-production-readiness-v1,
                   2026-08-13-biep-v3-motherduck-flights-v1,
                   2026-08-13-biep-v3-filesystem-and-language-pipelines-v1,
                   2026-08-04-skill-and-mcp-migration-v1
Affected repos: cianfhoghlaim
Cross-repo-sync: NOT REQUIRED (single-repo change)
```

> **Note on blockers**: The 4 v3 BIEP changes are informational
> dependencies for sequencing but do NOT enforce archiving. This
> change is self-contained — the wiring layer is additive, the
> doc files are additive, the test files are additive, the IaC
> procedures are additive. No existing 12-agent runtime depends
> on the v3 BIEP namespace fixes (`md:oideachais` → `md:cianfhoghlaim`)
> for this change to land. The 12 agents will continue to work
> against the legacy namespace until those changes archive.

## Acceptance Gates

The change archives when ALL pass:

1. `openspec validate 2026-08-14-agents-fleet-wiring-parity-v1 --strict` returns 0
2. `mise run lint:skills` (53/53, no regression)
3. `mise run agents:smoke` (3 test files, 12 total scenarios pass)
4. `mise run agents:audit` (direct-import audit + registry validation → 0 violations)
5. The 12 agents load via `python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; assert len(AGENT_REGISTRY) == 12"`
6. The 8 NCCA subject agents still load via `python -c "from cianfhoghlaim.agents.tuatha import math_agent; assert math_agent is not None"`
7. `bun run validate-stacks` (0 hard failures for the 3 new agent-fleet procedures)
8. The 3 bundled procedures (`deploy-agent-fleet-bunchloch`, `deploy-agent-fleet-arm1-oci`, `deploy-agent-fleet-arm1-oci-cci`) complete dry-run
9. `cc_validator` reports 0 compliance issues for the 4 spec deltas
10. `agent-observability` smoke test passes (5-layer observability hooks verified)

## Estimated effort

- Phase 1 (wiring): 3 hours
- Phase 2 (docs): 1.5 hours
- Phase 3 (tests): 1 hour
- Phase 4 (IaC): 1.5 hours
- Phase 5 (spec lock): 1 hour
- Validation: 30 min

**Total: ~8.5 hours** of focused work, organised as 12 numbered steps
(see `tasks.md`).

## Risk

| Risk | Mitigation |
|:--|:--|
| The 12 agents have heterogeneous error-handling patterns that don't trivially unify | The new `exceptions.py` is additive; existing per-agent try/except wrappers remain. Migration is opt-in per agent. |
| The 5 framework stubs (Pipecat + CopilotKit + 3 others) introduce dead code | The 5 stubs are behind `FRAMEWORK_AVAILABLE` flags; their loaders no-op in CI. Future-framework work fills them in. |
| 4 sub-package AGENTS.md files might be redundant with the top-level `agents/AGENTS.md` | Each sub-package AGENTS.md has a distinct audience (the route author, the tool author, the OCR/HTR engineer, the MMO game engineer). Top-level AGENTS.md is the routing reference. |
| The 3 new agent-fleet procedures might conflict with the existing `deploy-agent-platform-cluster-{bunchloch,arm1-oci}` | The new procedures are scoped to the 12 main agents (not the 3 surfaces). They call the existing cluster procedure as a prerequisite. |
| `agents/observability_hooks.py` might break the existing `observability/logfire_config.py` lazy imports | The new module only adds higher-level hooks; the existing lazy imports are preserved. |

## Non-Goals

- **Not migrating the 12 agents to a single framework** — the
  5-framework split (ADK + Agno + Custom + Pipecat + CopilotKit) is
  intentional for cross-framework parity.
- **Not adding new OCR backends** — the 10 backends in
  `meaisinfhoghlaim/ocr/` are the canonical set.
- **Not migrating the `agents/meaisinfhoghlaim/` sub-package to
  `meaisinfhoghlaim/`** — the v7 flattening kept the
  `agents/meaisinfhoghlaim/` sub-tree for the OCR/HTR/alignment cluster.
- **Not redesigning the agent registry data model** — the
  AGENT_REGISTRY is a flat dict, not a graph database. The Cognee
  knowledge graph covers the relationship side.