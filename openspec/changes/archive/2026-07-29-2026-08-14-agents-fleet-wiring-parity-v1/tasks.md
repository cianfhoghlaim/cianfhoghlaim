# Tasks — 2026-08-14-agents-fleet-wiring-parity-v1

## Phase 0 — Pre-flight (no edits) (15 min)

- [ ] 0.1 Verify the 3 hard blockers are archived:
      `openspec list` shows `2026-08-08-biep-v3-production-readiness-v1`,
      `2026-08-13-biep-v3-motherduck-flights-v1`,
      `2026-08-13-biep-v3-filesystem-and-language-pipelines-v1` as archived.
- [ ] 0.2 Verify the soft blocker is archived:
      `openspec list` shows `2026-08-04-skill-and-mcp-migration-v1` as archived.
- [ ] 0.3 Read `agents/tuatha/wiring.py` (full 600 LOC) to confirm the canonical pattern.
- [ ] 0.4 Read the 12 agent files in `agents/{adk,agno}/<slug>_agent.py` to confirm the current per-agent wiring.
- [ ] 0.5 Read `agents/routing_keywords.py` to confirm the 12-bucket seed.

## Phase 1 — Centralize the Agent Fleet (3 hours)

- [ ] 1.1 Create `agents/wiring.py` with `AgentFleetWiring` dataclass (12 entries × 8 fields × framework tuple).
- [ ] 1.2 Create `agents/_workflow_handlers.py` with 4 shared async dispatchers (`dispatch_study_plan`, `dispatch_deep_research`, `dispatch_literature_review`, `dispatch_summary`).
- [ ] 1.3 Create `agents/agent_registry.py` with `AGENT_REGISTRY` dict (12 entries mapping to `AgentFleetWiring`).
- [ ] 1.4 Create `agents/observability_hooks.py` with `LangfuseLogger` + `LogfireSpan` + `MLflowTracker` + `RAGASScorer` + `structlogLogger`.
- [ ] 1.5 Create `agents/memory_layer.py` with `MemoryLayer` Protocol + 5 concrete backends (Cognee + Graphiti + LanceDB + FalkorDB + Memgraph) + cached factory.
- [ ] 1.6 Create `agents/exceptions.py` with `AgentError` hierarchy + `with_retry()` decorator + `graceful_degradation` context manager.
- [ ] 1.7 Create `agents/pydantic_models.py` with `AgentRequest` + `AgentResponse` + `AgentContext` + `AgentTrace` Pydantic v2 base models.
- [ ] 1.8 Modify `agents/__init__.py` to re-export the 7 new modules + the `AGENT_REGISTRY` dict.
- [ ] 1.9 Modify `agents/{adk,agno}/<slug>_agent.py` (12 files) to adopt the new wiring.
- [ ] 1.10 Modify `agents/adk/root_agent.py` to re-export the 12 main agents + their wiring.
- [ ] 1.11 Modify `agents/tuatha/wiring.py` to re-export the 8 NCCA subject wirings through the `AGENT_REGISTRY`.
- [ ] 1.12 Verify all 12 + 8 + 3 agents load + their `wire` field is populated.

## Phase 2 — Documentation (1.5 hours)

- [ ] 2.1 Rewrite `agents/AGENTS.md` (full quadrant, mirroring `agents/tuatha/AGENTS.md` at 204 lines).
- [ ] 2.2 Create `agents/STATUS.md` (12 + 8 + 3 agents' current state).
- [ ] 2.3 Create `agents/DEVELOPMENT.md` (how to add a new agent to the fleet).
- [ ] 2.4 Create `agents/REPRODUCER.md` (how to reproduce the agent-platform cluster from zero).
- [ ] 2.5 Create `agents/api/AGENTS.md` (Hono routes layer).
- [ ] 2.6 Create `agents/tools/AGENTS.md` (tools layer).
- [ ] 2.7 Create `agents/meaisinfhoghlaim/AGENTS.md` (OCR/HTR/alignment sub-package).
- [ ] 2.8 Modify `agents/tuatha/AGENTS.md` (post-v7 path updates + new wiring layer reference).
- [ ] 2.9 Modify `agents/README.md` (replace 11-line stub with 30-line quick-start).

## Phase 3 — Production-ise & Reproducibility (1 hour)

- [ ] 3.1 Create `tests/test_agent_fleet_smoke.py` with 5 scenarios.
- [ ] 3.2 Create `tests/test_agent_wiring_audit.py` with the direct-import audit.
- [ ] 3.3 Create `tests/test_agent_registry_smoke.py` with 4 scenarios.
- [ ] 3.4 Create `scripts/reproducers/agents-fleet-reproducer.sh` (6 commands from cold to green).
- [ ] 3.5 Modify `mise.toml` to add `agents:smoke` + `agents:audit` tasks.

## Phase 4 — IaC Integration (1.5 hours)

- [ ] 4.1 Create `bonneagar/komodo/procedures/deploy-agent-fleet-bunchloch.toml` (4-stage omnibus).
- [ ] 4.2 Create `bonneagar/komodo/procedures/deploy-agent-fleet-arm1-oci.toml` (6-stage omnibus with `preflight:arm-oci`).
- [ ] 4.3 Create `bonneagar/komodo/procedures/deploy-agent-fleet-arm1-oci-cci.toml` (5-stage operator-monitoring variant).
- [ ] 4.4 Create `bonneagar/deploy-runbooks/agent-fleet-bunchloch-2026-08.md` (operator runbook).
- [ ] 4.5 Create `bonneagar/deploy-runbooks/agent-fleet-arm1-oci-2026-08.md` (operator runbook with WARP + Locket).
- [ ] 4.6 Create `bonneagar/pangolin/agent-fleet.yaml` (6-label resource definitions).
- [ ] 4.7 Create `bonneagar/blueprints/agent-fleet-bp.yaml` (Pangolin site blueprint).
- [ ] 4.8 Modify `bonneagar/scripts/validate-stacks.ts` to add the 3 new procedures to the validation set.

## Phase 5 — Spec Lock (1 hour)

- [ ] 5.1 Create `openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1/proposal.md` (this file).
- [ ] 5.2 Create `openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1/tasks.md` (this file).
- [ ] 5.3 Create `openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1/specs/meaisinfhoghlaim-agent-frameworks/spec.md` (3 ADDED Requirements).
- [ ] 5.4 Create `openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1/specs/agent-observability/spec.md` (2 ADDED Requirements).
- [ ] 5.5 Create `openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1/specs/agent-memory-systems/spec.md` (2 ADDED Requirements).
- [ ] 5.6 Create `openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1/specs/agent-platform-cluster/spec.md` (3 ADDED Requirements).
- [ ] 5.7 Run `openspec validate 2026-08-14-agents-fleet-wiring-parity-v1 --strict` and confirm exit 0.

## Phase 6 — Validation + commit (15 min)

- [ ] 6.1 `mise run lint:skills` (53/53, no regression)
- [ ] 6.2 `mise run agents:smoke` (3 test files, 12 total scenarios pass)
- [ ] 6.3 `mise run agents:audit` (0 violations)
- [ ] 6.4 `python -c "from cianfhoghlaim.agents import AGENT_REGISTRY; assert len(AGENT_REGISTRY) == 12; print('OK')"`
- [ ] 6.5 `python -c "from cianfhoghlaim.agents.tuatha import math_agent; assert math_agent is not None; print('OK')"`
- [ ] 6.6 `bun run validate-stacks` (0 hard failures for the 3 new procedures)
- [ ] 6.7 `git status` shows ~30 new files + ~12 modified files
- [ ] 6.8 Commit with the canonical `feat(agents):` message
- [ ] 6.9 Push to `origin pick-4-biep-v1`

## Phase 7 — Archive + final acceptance (10 min)

- [ ] 7.1 `openspec archive 2026-08-14-agents-fleet-wiring-parity-v1 --yes` succeeds
- [ ] 7.2 (Post-archive on bunchloch) `mise run agents:audit` reports 0 violations
- [ ] 7.3 (Post-archive on bunchloch) `km run procedure deploy-agent-fleet-bunchloch` completes within 10 min
- [ ] 7.4 (Post-archive on arm1-oci) `km run procedure deploy-agent-fleet-arm1-oci` completes within 15 min
- [ ] 7.5 (Post-archive) Update root `AGENTS.md` to reference the new `agents/AGENTS.md` + the 4 sub-package AGENTS.md files
- [ ] 7.6 (Post-archive) Update `openspec/AGENTS.md` to reference the archived change as the canonical "agents parity" reference