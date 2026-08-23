# Phasing — Tuatha British Isles MMO Consolidation v1

## v1 — The consolidation (this change; ~3 turns of build time)

**Goal**: archive the prior state, re-route the cross-repo
references, and author the openspec change that governs the
new `tuatha/` project.

**Scope** (executed in this change):

- T1.1: Archive the 12 prior top-level `tuasha/*` to `tuasha/old/prior_top_level_tuasha/`
- T1.2: Archive the 63-file `agents/tuasha/*` to `tuasha/old/scattered_agents_tuasha/`
- T1.3: Hard-archive the Babylon.js skill to `tuasha/old/legacy_theming/babylonjs/`
- T2.1: Re-route `agents/agent_registry.py:AGENT_REGISTRY` (`media_descriptor_agent`)
- T2.2: Move the 3 media_intel files to `tuasha/agents/media_intel/` + back-compat shim
- T2.6: Author the openspec change `2026-08-25-tuatha-british-isles-mmo-consolidation-v1/`

**Done when**:

- ✅ `openspec validate 2026-08-25-tuatha-british-isles-mmo-consolidation-v1 --strict` PASS
- ✅ `openspec validate --all --strict` 145/147 (or better)
- ✅ The `tuatha/` sub-dir contains the 2 plan files + the `old/` archive

## v2 — Build the new `tuatha/` project from scratch (~14-18 turns of build time)

**Goal**: build the new `tuatha/` British Isles Formative
Assessment MMO project from scratch per the `BUILD_PLAN.md`.

**Scope** (per `tuatha/BUILD_PLAN.md` § The per-step file list):

- T3.1-T3.2: Initialize the new git repo + author the 6 meta files
- T3.3-T3.4: Author the 7 Python package modules + the 8 subject agents
- T3.5: Author the 40 per-subject tools
- T3.6: Author the 3 educational agents
- T3.7: Author the media_intel module (5 files)
- T3.8: Author the 4 BIEP hackathon features
- T3.9: Author the 13 BAML files
- T3.10: Author the 40 DLT sources
- T3.11-T3.13: Author the Dagster + CocoIndex + marimo layers
- T3.14: Author the badges credential system
- T3.15: Author the 4 docs
- T3.16: Author the 4 tests
- T3.17-T3.18: Author the CI + dev-container
- T3.19: git add + commit + push to the new `origin` (operator initializes the remote)
- T3.20: Run the 6 quality gates + final report

**Dependency**: v1 must archive first; 5 parent pending changes
must archive first.

**Done when**:

- ✅ All 6 quality gates pass
- ✅ `openspec validate 2026-08-25-tuatha-british-isles-mmo-consolidation-v1 --strict` still PASS
- ✅ The new `tuatha/` project is pushed to `github.com/cianmacandeisigh/tuasha.git`

## v3 — Activate the 9 Celtic-history stubs (deferred to a subsequent theming change)

**Goal**: activate the 9 stub Celtic-history research sources
when the downstream theming change archives.

**Scope** (deferred):

- Activate the 9 stubs (Tuatha Dé Danann + Irish mythology +
  Celtic mythology + Celtic law + Brehon law + Aran Islands +
  Isle of Skye + Isle of Man + Dyfed) by flipping
  `status: stub` → `status: active` in each `source.yaml`
- Materialise the per-page ingestion logic in each `scrape.py`
- Update the `celtic_history_research` spec to remove the "gated"
  wording

**Dependency**: v1 + v2 must archive first; the downstream
theming change must archive first.

**Done when**:

- The 9 stubs are activated + the `celtic_history_research` LanceDB
  table has rows for each topic
- The 7-axis `MediaDescriptor` cross-medium compare returns sensible
  answers

## Out of scope (deferred to a downstream Celtic-MMO design change)

- The 4+1 element world canon
- The Cymru-Wales+England / Aran Islands / Isle of Skye /
  Isle of Man / Dyfed sub-nation binding
- The anam currency + earn/spend/decay rule system
- The Hades-style boon-for-homework loop
- The anamcara NFT familiar mechanic
- The 2D particle renderer choice
- The iOS delivery vehicle decision
- The 60-subject agent surface per `per-subject-agents` spec
- The full Parnell-3 + Cromien-7 marimo dashboards

These are the design choices that *this* change's corpus enables
but does *not* itself decide.
