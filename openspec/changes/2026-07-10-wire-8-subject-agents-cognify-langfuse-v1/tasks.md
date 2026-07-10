# Tasks — 2026-07-10-wire-8-subject-agents-cognify-langfuse-v1

## Step 1 — Extend the 8 subject agents to wire Letta + Langfuse + BAML end-to-end (5 h)

1. [x] Create `cianfhoghlaim/agents/tuatha/wiring.py` with:
   - `SUBJECT_WIRING` (8 entries: `gaeilge`, `mathematics`,
     `applied_mathematics`, `chemistry`, `computer_science`,
     `english`, `geography`, `history`)
   - `wire_subject_agent(wiring)` — returns `WireSubjectAgent`
     with `langfuse_wired`, `cognee_wired`, `memory_backend_kind`,
     `baml_prefix` flags
   - `emit_to_cognee(wiring, response, query, top_k=5)` — async
   - `open_langfuse_trace(wiring, verb="explain", **kw)` — context
     manager
   - `resolve_baml_function(wiring, suffix)` — looks up
     `b.Generate<Prefix><Suffix>`
   - `attach_subject_lifecycle(wiring)` — bundles the 3 handles
   - `SUBJECT_AGENT_DISABLE_WIRE=1` env-var escape hatch
2. [x] Wire `appm_agent.py` (start with the simplest):
   - `appm_agent_wire = wire_subject_agent(get_wiring("applied_mathematics"))`
   - `appm_agent_emit_to_cognee(...)` async function
   - `appm_agent_open_trace(...)` sync function
   - `appm_agent_baml_quest_pack_fn`, `appm_agent_baml_formative_item_fn`
   - Resolved eagerly at module load
3. [x] Wire `math_agent.py` (mirror of step 2 with `Math` prefix)
4. [x] Wire `gael_agent.py` (mirror with `Gael` prefix)
5. [x] Wire `hist_agent.py` (mirror with `Hist` prefix)
6. [x] Wire `geog_agent.py` (mirror with `Geog` prefix)
7. [x] Wire `chem_agent.py` (mirror with `Chem` prefix)
8. [x] Wire `comp_agent.py` (mirror with `Comp` prefix)
9. [x] Wire `engl_agent.py` (mirror with `Engl` prefix)

## Step 2 — Add 10+ new lifecycle tests (3 h)

10. [x] Create a `subject_agent_modules` fixture that imports all 8
    `<slug>_agent` modules via `importlib.import_module`
11. [x] Add `test_subject_agent_initializes_wire_metadata` (×8
    parametrized)
12. [x] Add `test_subject_agent_emits_to_cognee_dataset` (×8)
13. [x] Add `test_subject_agent_opens_langfuse_trace` (×8)
14. [x] Add `test_subject_agent_resolves_baml_functions` (×8)
15. [x] Add `test_storage_backend_protocol_is_used_not_graphiti_or_falkordb`
    — Step 4 acceptance gate
16. [x] Add `test_subject_router_module_re_exports_wiring`
17. [x] Add `test_subject_router_wiring_cognee_dataset_naming_rule`
18. [x] Add `test_subject_router_wiring_langfuse_trace_name_rule`
19. [x] Add `test_subject_router_wiring_baml_prefix_rule`
20. [x] Add `test_subject_agent_wire_subject_field_is_populated`
21. [x] Add `test_subject_agent_emit_to_cognee_handles_missing_cognee`
22. [x] Add `test_subject_agent_open_trace_returns_context_manager`
23. [x] Add `test_subject_router_with_disabled_wire_is_no_op`

## Step 3 — Wire the cognify step (2 h)

24. [x] Implement `emit_to_cognee(wiring, response, query, ...)` in
    `wiring.py`:
    - `await cognee.add(data=response, dataset_name=...)` 
    - `await cognee.search(query=..., top_k=5)` 
    - Returns `[hit.text for hit in hits]` — graceful on no-cognee
25. [x] Bind `<slug>_agent_emit_to_cognee` in every `<slug>_agent.py`
26. [x] Verify graceful no-op behaviour in
    `test_subject_agent_emit_to_cognee_handles_missing_cognee`

## Step 4 — `StorageBackend` Protocol surface (1 h)

27. [x] All 8 agent modules import via `get_default_backend()` from
    `cianfhoghlaim.storage.memf`
28. [x] No direct `from oideachais.graphiti...|oideachais.falkordb...`
    imports remain (Step 4 acceptance gate)
29. [x] Verify via `grep -rn "graphiti_client\|falkordb_client"
    cianfhoghlaim/agents/tuatha/*_agent.py` returns 0

## Step 5 — Extend the 8 `defs/5_agent_ops/<slug>/defs.yaml` (1 h)

30. [x] `gael_agent/defs.yaml` — add `cognify` + `langfuse_callbacks`
    blocks (dataset `oideachais_lc_gaeilge`, trace `agent.gael.explain`)
31. [x] `math_agent/defs.yaml` — same (dataset
    `oideachais_lc_mathematics`, trace `agent.math.explain`)
32. [x] `hist_agent/defs.yaml` — same (dataset `oideachais_lc_history`,
    trace `agent.hist.explain`)
33. [x] `geog_agent/defs.yaml` — same (dataset
    `oideachais_lc_geography`, trace `agent.geog.explain`)
34. [x] `chem_agent/defs.yaml` — same (dataset `oideachais_lc_chemistry`,
    trace `agent.chem.explain`)
35. [x] `comp_agent/defs.yaml` — same (dataset
    `oideachais_lc_computer_science`, trace `agent.comp.explain`)
36. [x] `engl_agent/defs.yaml` — same (dataset `oideachais_lc_english`,
    trace `agent.engl.explain`)
37. [x] `appm_agent/defs.yaml` — same (dataset
    `oideachais_lc_applied_mathematics`, trace `agent.appm.explain`)
38. [x] Verify every file parses via `yaml.safe_load(...)`

## Step 6 — OpenSpec change (this file's parent directory)

39. [x] Write `proposal.md`
40. [x] Write this `tasks.md`
41. [x] Write `specs/meaisinfhoghlaim-agent-frameworks/spec.md` (delta —
    4 ADDED Requirements)
42. [x] Write `specs/agent-memory-systems/spec.md` (delta —
    1 ADDED Requirement)
43. [x] Run `openspec validate 2026-07-10-wire-8-subject-agents-cognify-langfuse-v1 --strict`
    and confirm exit 0

## Step 7 — Commit + push

44. [x] `git add -A`
45. [x] Commit with the canonical Feat C message
46. [x] `git push --set-upstream origin pick-4-biep-v1`
