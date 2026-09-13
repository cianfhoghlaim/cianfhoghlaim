# Tasks: ADK + Gemini Deep Research Control Plane

## Stage 0 — Pre-flight
- [ ] T0.1 — Confirm `2026-08-26-mega-3a-baml-and-adk-v1` is archived
- [ ] T0.2 — Confirm `2026-08-15-centralized-registry-v1` is archived
- [x] T0.3 — Create the 4 new spec dirs under `openspec/specs/` (all 4 exist: `adk-deep-research-control-plane`, `dlt-pipeline-trigger-via-adk`, `cocoindex-pipeline-trigger-via-adk`, `pipeline-orchestrator-agent`, each with `spec.md` + `AGENTS.md`)
- [ ] T0.4 — Create the 7 change subdirs in sibling repos (cianchosaint, ciancheiltis, tuatha, gemini_hackathon) — out of scope; user said "DO NOT touch other repos"

## Stage 1 — NEW spec `adk-deep-research-control-plane`
- [x] T1.1 — Write `openspec/specs/adk-deep-research-control-plane/spec.md` (7 ADDED Requirements)
- [x] T1.2 — Write `openspec/specs/adk-deep-research-control-plane/AGENTS.md` (6-section outline)
- [x] T1.3 — Write the change's `specs/adk-deep-research-control-plane/spec.md` delta (ADDED Requirements)

## Stage 2 — NEW spec `dlt-pipeline-trigger-via-adk`
- [x] T2.1 — Write `openspec/specs/dlt-pipeline-trigger-via-adk/spec.md` (2 ADDED Requirements)
- [x] T2.2 — Write `openspec/specs/dlt-pipeline-trigger-via-adk/AGENTS.md`
- [x] T2.3 — Write the change's delta (`specs/dlt-pipeline-trigger-via-adk/` dir under the change — no delta needed because it's a NEW spec, not MODIFIED)

## Stage 3 — NEW spec `cocoindex-pipeline-trigger-via-adk`
- [x] T3.1 — Write `openspec/specs/cocoindex-pipeline-trigger-via-adk/spec.md` (2 ADDED Requirements)
- [x] T3.2 — Write `openspec/specs/cocoindex-pipeline-trigger-via-adk/AGENTS.md`
- [x] T3.3 — Write the change's delta (`specs/cocoindex-pipeline-trigger-via-adk/` — no delta needed; NEW spec)

## Stage 4 — NEW spec `pipeline-orchestrator-agent`
- [x] T4.1 — Write `openspec/specs/pipeline-orchestrator-agent/spec.md` (3 ADDED Requirements)
- [x] T4.2 — Write `openspec/specs/pipeline-orchestrator-agent/AGENTS.md`
- [x] T4.3 — Write the change's delta (`specs/pipeline-orchestrator-agent/` — no delta needed; NEW spec)

## Stage 5 — MODIFIED spec `agent-registry`
- [x] T5.1 — Read current `openspec/specs/agent-registry/spec.md`
- [x] T5.2 — Write MODIFIED Requirement for root_agent framework flip
- [x] T5.3 — Write the change's delta (`specs/agent-registry/spec.md`)

## Stage 6 — MODIFIED spec `browser-tools`
- [ ] T6.1 — Read current `openspec/specs/browser-tools/spec.md` — canonical `browser-tools` spec dir does NOT exist yet (the proposal treats it as MODIFIED but there is no baseline). Defer until a canonical spec lands.
- [ ] T6.2 — Write 3 MODIFIED Requirements (Gemini Deep Research as RESEARCH backend, 12 known issues fixed)
- [ ] T6.3 — Write the change's delta (change's `specs/browser-tools/` dir is currently empty)

## Stage 7 — MODIFIED spec `baml-schemas`
- [x] T7.1 — Read current `openspec/specs/baml-schemas/spec.md`
- [x] T7.2 — Write 1 ADDED Requirement for `ExtractGeminiDeepResearchReport`
- [x] T7.3 — Write the change's delta (`specs/baml-schemas/spec.md` — references `GeminiDeepResearchOutput` after the rename; see note below)

## Stage 8 — Agent surface
- [x] T8.1 — Create `agents/adk/pipeline_orchestrator/__init__.py`
- [x] T8.2 — Create `agents/adk/pipeline_orchestrator/dlt_trigger_agent.py`
- [x] T8.3 — Create `agents/adk/pipeline_orchestrator/cocoindex_index_agent.py`
- [x] T8.4 — Create `agents/adk/pipeline_orchestrator/baml_extract_agent.py`
- [x] T8.5 — Create `agents/adk/pipeline_orchestrator/orchestrator.py` (SequentialAgent + LoopAgent)
- [ ] T8.6 — Rewrite `agents/adk/root_agent.py` as ADK SequentialAgent — NOT done; proposal explicitly preserves the legacy Custom LiteLLM router for back-compat. New `agents/adk/cian_root_agent.py` provides the ADK `SequentialAgent`.
- [ ] T8.7 — Modify `agents/_workflow_handlers.py` to invoke root_agent — out of scope for this iteration
- [x] T8.8 — Modify `agents/agent_registry.py` to flip root_agent framework — already done before this session (root_agent now points to `cian_root_agent` + `framework=AgentFramework.ADK`)
- [ ] T8.9 — Modify `agents/integrations/agent_registry_runtime.py` to register new orchestrator — out of scope for this iteration

## Stage 9 — Browser stack
- [ ] T9.1 — Create `bonneagar/stacks/browser/sruth_browser/backends/paid/gemini_deep_research.py`
- [ ] T9.2 — Modify `browser_types.py` BACKEND_PRIORITY table
- [ ] T9.3 — Modify `backends/router.py` to wire new backend
- [ ] T9.4 — Modify `agents/orchestrator.py` to use `minimax` alias + `gemini-2.5-pro`
- [ ] T9.5 — Modify `agents/evaluator.py` to handle Deep Research `interactions` field
- [ ] T9.6 — Modify `frontend/adapters/agui.py` to stream Deep Research events
- [ ] T9.7 — Modify `baml/browser_extraction.baml` to add `GeminiDeepResearchOutput` (renamed from `GeminiDeepResearchReport` per the de-collision fix below)
- [ ] T9.8 — Fix `Dockerfile` CMD
- [ ] T9.9 — Create `Dockerfile.mcp`
- [ ] T9.10 — Create `sidecar.yaml`, `secrets.env`, `blueprint.yaml`, `.env.example`
- [ ] T9.11 — Delete `agent_os/`, `gemini-3-flash/`, `polymarket-research/`
- [ ] T9.12 — Modify `litellm_config.yaml` to add `gemini-deep-research` alias

## Stage 10 — DLT + BAML sources
- [ ] T10.1 — Create `dlt_sources/_shared/gemini_deep_research.py` (DLT source)
- [x] T10.2 — Create `baml_src/_shared/gemini_deep_research.baml` (file present; class renamed `GeminiDeepResearchReport` → `GeminiDeepResearchOutput` to avoid colliding with the pre-existing `GeminiDeepResearchReport` in `baml_src/processing/author_archive.baml:105` from `2026-06-16-author-archive-gemini-and-uos-ingestion`)

## Stage 11 — Cross-repo mirrors
- [ ] T11.1 — Mirror change to `cianchosaint/openspec/changes/2026-09-06-.../` — out of scope (user said "DO NOT touch other repos")
- [ ] T11.2 — Mirror change to `ciancheiltis/openspec/changes/2026-09-06-.../` — out of scope
- [ ] T11.3 — Mirror change to `tuatha/openspec/changes/2026-09-06-.../` — out of scope
- [ ] T11.4 — Mirror change to `gemini_hackathon/openspec/changes/2026-09-06-.../` — out of scope

## Stage 12 — Validation + handoff
- [ ] T12.1 — Run `mise run lint:skills` — not run in this session
- [x] T12.2 — Run `openspec validate 2026-09-06-adk-gemini-deep-research-control-plane-v1 --strict` — passes (`Change '2026-09-06-adk-gemini-deep-research-control-plane-v1' is valid`)
- [ ] T12.3 — Run `mise run sync:all` — not run (BAML generation is currently broken repo-wide by pre-existing `DomainExtractor` duplicates in `baml_src/_shared/templates/` — see archived `2026-09-13-pipeline-british-isles-synthesis-v1/proposal.md:35`; out of scope for this change)
- [ ] T12.4 — Run `mise run core:ci` — not run in this session
- [ ] T12.5 — Update relevant `AGENTS.md` files with new file counts — not run

## Notes (deferred to operator)

- `baml-cli generate --from baml_src` currently fails repo-wide on 18 pre-existing
  duplicate `DomainExtractor` function definitions in `baml_src/_shared/templates/*.baml`
  (the templates are by design but BAML rejects them as duplicates). This blocks
  `from baml_client.baml_client import b` for the entire repo, not just this
  change. The change does not regress this condition. Fix is tracked in the
  archived `2026-09-13-pipeline-british-isles-synthesis-v1` proposal.
- The new class `GeminiDeepResearchOutput` (was `GeminiDeepResearchReport`)
  avoids colliding with the pre-existing `GeminiDeepResearchReport` in
  `baml_src/processing/author_archive.baml:105`. The change's `specs/baml-schemas/spec.md`
  and the proposal `Impact` section document the rename.
- The legacy `agents.adk.root_agent.py` Custom LiteLLM router is preserved
  for back-compat per the proposal. `enhanced_orchestrator.py` and
  `curriculum_agent.py` continue to import legacy types from `.root_agent`;
  `agents/adk/cian_root_agent.py` now re-exports those types (`AgentContext`,
  `AgentDomain`, `AgentResponse`, `RootAgent`, `create_root_agent`) for
  future callers.
