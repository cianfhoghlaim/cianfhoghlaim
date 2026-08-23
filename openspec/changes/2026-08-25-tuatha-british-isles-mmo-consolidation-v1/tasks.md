# Tasks — Tuatha British Isles MMO Consolidation v1

## Phase 1 — Archive (the prior state → `tuatha/old/`) — DONE

- [x] **T1.1** Create `tuatha/old/{prior_top_level_tuasha,scattered_agents_tuasha,legacy_theming}/` + move the 12-item prior top-level `tuatha/*` to `tuatha/old/prior_top_level_tuasha/`. (The 2 plan files I just committed got moved with everything else; I pulled them back to `tuatha/`.)
- [x] **T1.2** Move the 63-file `agents/tuasha/*` to `tuatha/old/scattered_agents_tuasha/`. (61 source files + `__pycache__/` + `.DS_Store`.)
- [x] **T1.3** Hard-archive the 1 live Babylon.js skill (`.agents/skills/babylonjs/SKILL.md`) to `tuatha/old/legacy_theming/babylonjs/SKILL.md`. The other legacy theming skills (tuatha-mmo, tuatha-platform, celtic-asset-generation, spacetimedb, crypteolas) are in `.claude/worktrees/.../.agents/skills_backup/` — already archived, no further action.

## Phase 2 — Cross-repo re-routes — DONE for T2.1+T2.2; T2.3-T2.6 deferred to subsequent change

- [x] **T2.1** Re-route `agents/agent_registry.py:AGENT_REGISTRY` — the `media_descriptor_agent` entry's `module_path` is updated from `agents.meaisinfhoghlaim.media_intel.media_descriptor_agent` to `tuatha.agents.media_intel.media_descriptor_agent`.
- [x] **T2.2** Move the 3 `agents/meaisinfhoghlaim/media_intel/` files (`__init__.py` + `media_descriptor_agent.py` + `records.py`) to `tuatha/agents/media_intel/`. Add a back-compat shim at the old location that re-exports the canonical symbols.
- [ ] **T2.3** Author the new `.agents/skills/tuatha/SKILL.md` that points at the new `github.com/cianmacandeisigh/tuatha.git` repo. (deferred — the old `tuatha-mmo` + `tuatha-platform` skills are already in the `.claude/worktrees/.../.agents/skills_backup/` archive.)
- [ ] **T2.4** Deprecate `openspec/specs/tuatha-platform/spec.md` per the `cianfhoghlaim-educational-mmo` spec directive. (deferred — the spec already has the deprecation notice in its preamble; a re-confirmation can be added later.)
- [x] **T2.5** Author this openspec change (`2026-08-25-tuatha-british-isles-mmo-consolidation-v1/{proposal.md, tasks.md, design.md, PHASING.md, cross-repo-sync.md, specs/tuatha-british-isles-mmo/spec.md, specs/tuatha-british-isles-mmo/AGENTS.md}`).

## Phase 3 — Build the new `tuatha/` project from scratch (the per-step file list) — DEFERRED

- [ ] **T3.1** Initialize the new git repo at `github.com/cianmacandeisigh/tuatha.git` + add `origin` (operator's action; I cannot initialize a fresh remote from this client)
- [ ] **T3.2** Author the package meta: `pyproject.toml` + `mise.toml` + `LICENSE` + `README.md` + `AGENTS.md` + `DEVELOPMENT.md` (6 files)
- [ ] **T3.3** Author the canonical Python package: `tuatha/{__init__,config,routing,orchestrator,operator,cross_subject,workflows}.py` (7 files)
- [ ] **T3.4** Author the 8 subject agents: `tuatha/subjects/{mathematics,applied_mathematics,chemistry,computer_science,english,gaeilge,geography,history}.py` + `__init__.py` (9 files)
- [ ] **T3.5** Author the 40 tools: `tuatha/tools/<subject>_<tool>.py` (8 subjects × 5 tools) (40 files)
- [ ] **T3.6** Author the 3 educational agents: `tuatha/agents/educational/{academic_history_agent,celtic_grammar_agent,celtic_morphology_agent}.py` + `__init__.py` (4 files)
- [ ] **T3.7** Author the media_intel module: `tuatha/agents/media_intel/{__init__,records,classifier,explorer,media_descriptor_agent}.py` (5 files) — the `__init__.py` + `records.py` + `media_descriptor_agent.py` were moved from `agents/meaisinfhoghlaim/media_intel/` in T2.2; the `classifier.py` + `explorer.py` are new
- [ ] **T3.8** Author the 4 BIEP hackathon features: `tuatha/agents/hackathon/{marking_grader,adaptive_tutor,equivalency_generator,curriculum_change_sensor}.py` + `__init__.py` (5 files)
- [ ] **T3.9** Author the BAML surface: `tuatha/baml/{qpack_<subject>,marking_grader,adaptive_tutor,equivalency_table,media_descriptor,clients}.baml` (13 files)
- [ ] **T3.10** Author the DLT sources: `tuatha/dlt/{syllabus,past_paper,marking_scheme,formative_item,response_score}/<subject>.py` (8 subjects × 5 categories = 40 files)
- [ ] **T3.11** Author the Dagster asset groups: `tuatha/dagster/{per_subject,hackathon,media_intel}.py` (3 files)
- [ ] **T3.12** Author the CocoIndex v1 Apps: `tuatha/cocoindex/{per_subject,cross_subject,hackathon,media_intel}.py` (4 files)
- [ ] **T3.13** Author the marimo notebooks: `tuatha/notebooks/{per_subject,cross_subject,hackathon,media_intel}.py` (4 files)
- [ ] **T3.14** Author the badges credential system: `tuatha/badges/{models,mint,storage}.py` (3 files)
- [ ] **T3.15** Author the docs layer: `tuatha/docs/{ARCHITECTURE,AGENT_REGISTRY,THEMING,BIOGRAPHY}.md` (4 files)
- [ ] **T3.16** Author the tests layer: `tuatha/tests/{test_subject_router_smoke,test_media_intel_agent,test_hackathon_features,test_consolidation}.py` (4 files)
- [ ] **T3.17** Author the CI layer: `.github/workflows/ci.yml` + `tuatha/ci/dagger.py` (2 files)
- [ ] **T3.18** Author the dev-container + .gitignore + .dockerignore (3 files)
- [ ] **T3.19** git add + commit + push the new tuatha project to `github.com/cianmacandeisigh/tuatha.git` (1 commit, requires operator to initialize the remote)
- [ ] **T3.20** Run the 6 quality gates + final report

## Cross-cutting invariants (apply to every task)

- The new project is `tuatha` (not `cianchosaint` / `cianscull` / `british_isles_mmo`) — package name is `tuatha`, module name is `tuatha`, all imports are `tuatha.*`
- The new project repo URL is `github.com/cianmacandeisigh/tuatha.git` (user-owned, matching the `leabharlann` + `bonneagar` pattern at the parent `kings_college_galway` workspace)
- The British Isles Formative Assessment MMO theme is canonical (per `openspec/specs/cianfhoghlaim-educational-mmo/spec.md`)
- The 3 deprecated themes are HARD-ARCHIVED (no experimental sub-module, no fork-friendly flag):
  - ~~Pent-Elemental Cosmology~~ (5 realms: Spirit / Water / Fire / Earth / Air)
  - ~~Babylon.js 3D~~ game front-end
  - ~~SpacetimeDB v2~~ game engine backend
  - ~~Crypteolas financial token~~
  - ~~Anam Cara~~ soul friend mechanic
  - ~~Brown Ajah theming~~ (the 8 NCCA subject ↔ Tuatha Dé deity mapping is preserved as `tuatha/subjects/character.py` but the "Brown Ajah" name is dropped)
- Every model string routes through `MODEL_REGISTRY.resolve(family, role)` (no hardcoded model strings anywhere)
- Every BAML function emits to Pydantic + Zod + Convex + DuckLake DDL per the `centralized-schema-registry` contract
- Per-source `rights_holder` + `licence` are declared correctly (CC-BY-SA-4.0 for Wikipedia stubs, OGL-3.0 for UK gov, PSI for Éire gov, Crown copyright for Acts, fair-use-description for the NCCA PDFs)
- Concurrent-write safety: every file edit uses the `git status/diff` → edit → `git status/diff` → `git add <path>` protocol
- No `git add -A` (concurrent agents may have M files; never scoop them)
- No commit + push unless explicitly asked
