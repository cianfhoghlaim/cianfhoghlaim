# Wire 8 NCCA subject ADK specialists to Letta + Langfuse + cognify

## What changes

Production-ises T4's lazy-import wiring of the 8 NCCA subject
ADK specialists (`gael_agent`, `math_agent`, `appm_agent`,
`chem_agent`, `comp_agent`, `engl_agent`, `geog_agent`,
`hist_agent`) end-to-end. Each subject agent now eagerly wires
its full Letta + Langfuse + BAML + Cognee stack at module load
time (rather than via the T4 `subject_router.py:91-131` graceful-
degradation ladder that lazy-imported the agent module).

Concretely:

1. **Adds** `cianfhoghlaim/agents/tuatha/wiring.py`
   (~600 LOC, no graphiti/falkordb imports) — a shared wire-up
   layer that exposes:
   - `SUBJECT_WIRING` — the 8 (subject, module_slug, BAML prefix,
     Langfuse trace name, Cognee dataset, deity) tuples
   - `wire_subject_agent(wiring)` — eagerly resolve the Storage
     Backend Protocol + Langfuse client + Cognee-import probe +
     BAML function names
   - `emit_to_cognee(wiring, response, query)` — async, returns
     the top-5 closest historical responses; graceful no-op when
     `cognee` is not installed
   - `open_langfuse_trace(wiring, verb=...)` — context manager
     with the canonical `agent.<subject>.<verb>` trace name
   - `resolve_baml_function(wiring, suffix)` — looks up
     `b.Generate<Prefix><Suffix>` for the given wiring
   - `attach_subject_lifecycle(wiring)` — bundles the 3 handles
     (wire / emit_to_cognee / open_trace) into a single
     `WiredLifecycle` dataclass for the 8 subject modules
2. **Modifies** each of the 8 `<slug>_agent.py` files at
   `cianfhoghlaim/agents/tuatha/{gael,math,hist,geog,chem,comp,engl,appm}_agent.py`
   to attach 3 module-level wire-up handles:
   - `<slug>_agent_wire` (`WireSubjectAgent` instance)
   - `<slug>_agent_emit_to_cognee` (async fn)
   - `<slug>_agent_open_trace` (sync fn)
   - `<slug>_agent_baml_quest_pack_fn` /
     `<slug>_agent_baml_formative_item_fn` (BAML function refs
     that resolve to ``None`` when the BAML client hasn't been
     codegenned — never raises).
3. **Extends** the 8 `defs.yaml` files at
   `cianfhoghlaim/orchestration/defs/5_agent_ops/adk/<slug>_agent/defs.yaml`
   with two new blocks:
   - `cognify:` — `dataset: oideachais_lc_<subject>`, `top_k: 5`,
     `emit_on: [response_generated, tool_call_completed]`
   - `langfuse_callbacks:` —
     `trace_name: agent.<subject>.explain`, `flush_interval: 30s`
4. **Adds** 41 new lifecycle tests to
   `cianfhoghlaim/tests/test_subject_router_smoke.py` (the file
   already had the 20 smoke tests from T4). The new tests assert:
   - Every subject agent attaches the wire metadata at module
     load time
   - Every `_emit_to_cognee` is callable + async
   - Every `_open_trace` is callable + returns a context manager
   - Every BAML function resolution runs at load time
   - The 8 agents never import graphiti/falkordb directly
     (Step 4 acceptance gate)
   - The `cognee_dataset` naming rule
     (``oideachais_lc_<subject>``)
   - The `langfuse_trace_name` naming rule
     (``agent.<module_slug>.<verb>``)
   - The `baml_prefix` rule (matches the per-subject generator
     function naming)
   - `emit_to_cognee` is graceful when cognee is unavailable
   - `SUBJECT_AGENT_DISABLE_WIRE=1` env-var escape hatch works
   - The `attach_subject_lifecycle` bundled API works

2 spec deltas:

- `specs/meaisinfhoghlaim-agent-frameworks/spec.md` — MODIFIED:
  adds 4 ADDED Requirements (Letta wiring, Langfuse callbacks,
  cognify, StorageBackend-Protocol enforcement) to the existing
  spec; total goes from 10 → 14 Requirements.
- `specs/agent-memory-systems/spec.md` — MODIFIED: adds 1 ADDED
  Requirement enforcing the `MemoryBackend` Protocol on the 8
  NCCA subject agents (the Step 4 acceptance gate); total goes
  from 5 → 6 Requirements.

The 5-tangent modernization (post-v4) is now complete on the
agent-runtime side: T1 (infrastructure) + T2 (Irish LC data) +
T3 (cocoindex migration) + T4 (agent fleet + observability) +
T5 (cross-nation content audit) all link to this change as the
"production-isation" capstone.

## Dependencies

`Blocked by: none` (T4's `0bf713c45` "feat(agents): T4 agent-fleet
+ baml 0.212 + observability + storage facades" is already merged
on this branch and provides the StorageBackend Protocol + the 8
defs.yaml mounts).

`Blocked by (soft): 2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
(this change amends `meaisinfhoghlaim-agent-frameworks` and
`agent-memory-systems` per the v6 lockdown's spec-revision rules).

`Affected repos: cianfhoghlaim` (single-repo change).

## Acceptance gates

- `openspec validate 2026-07-10-wire-8-subject-agents-cognify-langfuse-v1 --strict`
  passes (no spec/format regressions)
- `python3 -m pytest cianfhoghlaim/tests/test_subject_router_smoke.py`
  reports ≥ 30 tests (20 existing + ≥ 10 new) — all pass
- `grep -rn "from oideachais.graphiti\|from oideachais.falkordb\|from cianfhoghlaim.graphiti\|from cianfhoghlaim.falkordb" cianfhoghlaim/agents/tuatha/*.py`
  returns 0 matches (Step 4 acceptance gate)
- `grep -n "graphiti_client\|falkordb_client" cianfhoghlaim/agents/tuatha/<slug>_agent.py`
  returns 0 matches (Step 4 secondary gate)
- The 8 `defs.yaml` files at
  `cianfhoghlaim/orchestration/defs/5_agent_ops/adk/<slug>_agent/defs.yaml`
  load cleanly via `yaml.safe_load(...)` and expose both
  `attributes.cognify` + `attributes.langfuse_callbacks` blocks
- All 8 `<slug>_agent.py` modules import without raising
  `ImportError`, `pydantic_core.ValidationError`, or
  `SyntaxError`

## Estimated effort

12 hours of focused work, organised as 5 numbered steps (see
`tasks.md`).

## Cross-repo sync

Not applicable — this is a single-repo change. `bonneagar` +
`leabharlann` are unaffected.

## Files touched

- **Add**: `cianfhoghlaim/agents/tuatha/wiring.py`
- **Modify** (8): `cianfhoghlaim/agents/tuatha/{gael,math,hist,geog,chem,comp,engl,appm}_agent.py`
- **Modify** (1): `cianfhoghlaim/tests/test_subject_router_smoke.py`
- **Modify** (8): `cianfhoghlaim/orchestration/defs/5_agent_ops/adk/<slug>_agent/defs.yaml`
- **Add** (4): the openspec change directory + 2 spec deltas
- Total: 1 added file (~600 LOC) + 17 modified files + 4 openspec files

## Risk

**Low**. The wire-up is graceful — every dependency probe is in a
`try/except Exception` block and the only externally observable
behaviour is that `agent.<slug>_wire` etc. get attached at module
load. The 20 existing smoke tests continue to pass because they go
through `subject_router.make_subject_agent(...)` which remains
the canonical entry point.
