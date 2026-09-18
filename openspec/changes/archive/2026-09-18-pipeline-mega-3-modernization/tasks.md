# Tasks: pipeline-mega-3-modernization

## 1. Mega-3 Roadmap + Sequencing (per `2026-08-18-mega-3-roadmap-v1`)

- [ ] **M1.1** Finalise the 5-step rollout plan: Roadmap → Fast-Follow → 3a → 3b → 3c
- [ ] **M1.2** Document the 4-stage plane (LC + JC + A-Level + GCSE) + the -25,799 LOC net deduplication target
- [ ] **M1.3** Record the cross-batch dependency graph in `design.md`
- [ ] **M1.4** Stage the rollout as 5 sequenced openspec changes (Roadmap + Fast-Follow + 3a + 3b + 3c)

## 2. Foundation: 5 Integration Helpers + 12 Crown Jewels + 6 Dedup Wins (per `2026-08-18-mega-3-fast-follow-v1`)

- [ ] **M2.1** `BAMLFunctionTool` helper — wrap any BAML function as an ADK FunctionTool
- [ ] **M2.2** `marimo_baml` helper — marimo cell that calls a BAML function with progress UI
- [ ] **M2.3** `agent_ui_bridge` helper — bridge agent output to marimo cell reactive state
- [ ] **M2.4** `marimo_to_copilotkit` helper — marimo cell → CopilotKit action
- [ ] **M2.5** `cocoindex_query_api` helper — typed query API over CocoIndex App
- [ ] **M2.6–M2.17** 12 crown-jewel wires (FF.6–FF.12) — hook the integration helpers into the highest-leverage call sites
- [ ] **M2.18–M2.23** 6 dedup wins (FF.13–FF.18) totalling -8,833 LOC
  - [ ] collapse 4 hand-written CocoIndex files into one factory
  - [ ] delete 13 shims that the helpers replaced
  - [ ] collapse 8 `qpack_*.baml` files into stage template
  - [ ] delete 13 `_legacy/grading/*.baml` files
  - [ ] consolidate `FetchPanel.tsx` into reusable component
  - [ ] (1 more — see `2026-08-18-mega-3-fast-follow-v1`)

## 3. Mega-3a — BAML Stage Templates + ADK Agent Fleet + 8 NCCA JC Subjects (per `2026-08-26-mega-3a-baml-and-adk-v1`)

- [ ] **M3.1** BAML stage template for Leaving Certificate (LC) — replaces 14,200 LOC of per-subject duplication
- [ ] **M3.2** BAML stage template for Junior Certificate (JC)
- [ ] **M3.3** BAML stage template for A-Level
- [ ] **M3.4** BAML stage template for GCSE
- [ ] **M3.5** BAML stage template for `qpack` (question-pack)
- [ ] **M3.6** Adopt BAML 0.223.0 features (`spawn`, `host.callable`, `catch`, `render_null_as`, multimodal, intersection bounds)
- [ ] **M3.7–M3.14** 8 NEW NCCA Junior Cycle subjects at full scope (Math, English, Gaeilge, Science, Geography, History, CSPE, SPHE)
  - [ ] each gets 1 BAML function + 1 CocoIndex App + 1 ADK agent + 1 A2UI surface
- [ ] **M3.15** CocoIndex stage factory: 4 factories generating 99 Apps total
- [ ] **M3.16** ADK agent auto-generation: ~46 agents replacing 21 hand-written
- [ ] **M3.17** Marimo stage dashboards: 4 dashboards (1 per stage)
- [ ] **M3.18** Net LOC: -9,700 (verify)

## 4. Verification

- [ ] Run `openspec validate pipeline-mega-3-modernization --strict` — pass
- [ ] Run `openspec validate --all --strict` — pass
- [ ] Run `mise run lint:drift-docs` — pass (count claims remain accurate)
- [ ] Run `mise run lint:locale-refs` — pass (Mega-3 doesn't introduce stale locale refs)
- [ ] Confirm the 3 sequenced dated changes (Roadmap + Fast-Follow + 3a) are archived under `openspec/changes/archive/2026-09-13-pipeline-mega-3-modernization/`

## Verification

```bash
cd ~/dev/cianfhoghlaim
openspec validate pipeline-mega-3-modernization --strict
openspec validate --all --strict
```
