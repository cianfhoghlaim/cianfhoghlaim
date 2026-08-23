# BUILD PLAN — `tuatha` v1 (the per-step execution plan)

> **The British Isles Formative Assessment MMO** — the per-step
> file-by-file execution plan. Complements
> `CONSOLIDATION_PLAN.md` (which is the high-level plan).

---

## The 3 phases + the 7 sub-steps

| Phase | Step | Scope | Est. files |
|:--|:--|:--|--:|
| **Phase A** (plan) | A.1 | Write the 2 plan files (CONSOLIDATION_PLAN + BUILD_PLAN) | 2 |
| **Phase A** (plan) | A.2 | git add + commit + push the 2 plan files to origin | 1 commit |
| **Phase 1** (archive) | 1.1 | Archive the current top-level `tuatha/*` to `tuatha/old/prior_top_level_tuasha/` | ~12 |
| **Phase 1** (archive) | 1.2 | Archive the current `agents/tuatha/*` to `tuatha/old/scattered_agents_tuasha/` | ~65 |
| **Phase 1** (archive) | 1.3 | Hard-archive the 3 deprecated theming references (Babylon.js / SpacetimeDB / Crypteolas) to `tuatha/old/legacy_theming/` | ~6 |
| **Phase 2** (cross-repo refactor) | 2.1 | Re-route `agents/agent_registry.py:AGENT_REGISTRY` to the new `tuatha.agents.media_intel.*` module path | 1 line |
| **Phase 2** (cross-repo refactor) | 2.2 | Re-path the 3 media_intel files from `agents/meaisinfhoghlaim/media_intel/` → `tuatha/agents/media_intel/` | 3 files |
| **Phase 2** (cross-repo refactor) | 2.3 | Scan + archive the legacy skills (`tuatha-mmo/`, `tuatha-platform/`, `celtic-asset-generation/`, `meaisinfhoghlaim/` anything tuatha-specific) | ~5 skills |
| **Phase 2** (cross-repo refactor) | 2.4 | Author the new `.agents/skills/tuatha/SKILL.md` that points at the new repo | 1 file |
| **Phase 2** (cross-repo refactor) | 2.5 | Deprecate `openspec/specs/tuatha-platform/spec.md` (per the `cianfhoghlaim-educational-mmo` spec directive) | 1 file edit |
| **Phase 2** (cross-repo refactor) | 2.6 | Author the openspec change `2026-08-25-tuatha-british-isles-mmo-consolidation-v1/` with the delta | 5 files |
| **Phase 3** (build from scratch) | 3.1 | Initialize the new git repo at `github.com/cianmacandeisigh/tuatha.git` + add `origin` | 0 |
| **Phase 3** (build from scratch) | 3.2 | Author the package meta: `pyproject.toml` + `mise.toml` + `LICENSE` + `README.md` + `AGENTS.md` + `DEVELOPMENT.md` | 6 |
| **Phase 3** (build from scratch) | 3.3 | Author the canonical Python package: `tuatha/__init__.py` + `tuatha/{config,routing,orchestrator,operator,cross_subject,workflows}.py` | 7 |
| **Phase 3** (build from scratch) | 3.4 | Author the 8 subject agents: `tuatha/subjects/{mathematics,applied_mathematics,chemistry,computer_science,english,gaeilge,geography,history}.py` | 8 |
| **Phase 3** (build from scratch) | 3.5 | Author the 40 tools: `tuatha/tools/<subject>_<tool>.py` (8 subjects × 5 tools) | 40 |
| **Phase 3** (build from scratch) | 3.6 | Author the 3 educational agents: `tuatha/agents/educational/{academic_history_agent,celtic_grammar_agent,celtic_morphology_agent}.py` | 3 |
| **Phase 3** (build from scratch) | 3.7 | Author the media_intel module: `tuatha/agents/media_intel/{__init__,records,classifier,explorer,media_descriptor_agent}.py` | 5 |
| **Phase 3** (build from scratch) | 3.8 | Author the 4 BIEP hackathon features: `tuatha/hackathon/{marking_grader,adaptive_tutor,equivalency_generator,curriculum_change_sensor}.py` | 4 |
| **Phase 3** (build from scratch) | 3.9 | Author the BAML surface: `tuatha/baml/{qpack_<subject>,marking_grader,adaptive_tutor,equivalency_table,media_descriptor,clients}.baml` (the 8 subject qpack + 3 hackathon + 1 media_descriptor + 1 clients) | 13 |
| **Phase 3** (build from scratch) | 3.10 | Author the DLT sources: `tuatha/dlt/{syllabus,past_paper,marking_scheme,formative_item,response_score}/<subject>.py` (8 subjects × 5 categories) | 40 |
| **Phase 3** (build from scratch) | 3.11 | Author the Dagster asset groups: `tuatha/dagster/{per_subject,hackathon,media_intel}.py` | 3 |
| **Phase 3** (build from scratch) | 3.12 | Author the CocoIndex v1 Apps: `tuatha/cocoindex/{per_subject,cross_subject}.py` | 2 |
| **Phase 3** (build from scratch) | 3.13 | Author the marimo notebooks: `tuatha/notebooks/{per_subject,cross_subject}.py` | 2 |
| **Phase 3** (build from scratch) | 3.14 | Author the badges credential system: `tuatha/badges/{models,mint,storage}.py` | 3 |
| **Phase 3** (build from scratch) | 3.15 | Author the docs layer: `tuatha/docs/{ARCHITECTURE,AGENT_REGISTRY,THEMING,BIOGRAPHY}.md` | 4 |
| **Phase 3** (build from scratch) | 3.16 | Author the tests layer: `tuatha/tests/{test_subject_router_smoke,test_media_intel_agent,test_hackathon_features,test_consolidation}.py` | 4 |
| **Phase 3** (build from scratch) | 3.17 | Author the CI layer: `.github/workflows/ci.yml` + `dagger.py` | 2 |
| **Phase 3** (build from scratch) | 3.18 | Author the dev-container + .gitignore + .dockerignore | 3 |
| **Phase 3** (build from scratch) | 3.19 | git add + commit + push the new tuatha project to origin | 1 commit |
| **Phase 3** (build from scratch) | 3.20 | Run the 6 quality gates + final report | 0 |

**Total estimated file count (after Phase 3):** ~300 files

---

## The directory tree (the canonical structure after Phase 3)

```
tuatha/
├── CONSOLIDATION_PLAN.md               (the high-level plan)
├── BUILD_PLAN.md                        (this file)
├── README.md                            (the canonical British Isles MMO README)
├── AGENTS.md                            (the routing doc)
├── DEVELOPMENT.md                       (the how-to-add-an-agent doc)
├── pyproject.toml                       (the package meta — uv-compatible)
├── mise.toml                            (the mise task namespace)
├── LICENSE                              (MIT, permissive)
├── docker-compose.yml                   (the local-dev stack)
├── tuatha/                                # the canonical Python sub-namespace
│   ├── __init__.py                      (re-exports: 8 subject agents + 3 educational + 4 hackathon + 1 media_intel + 1 orchestrator + 1 operator + 1 cross_subject)
│   ├── config.py                         (LiteLLM + Langfuse + Cognee + Letta + BAML clients config)
│   ├── routing.py                        (the SubjectAgentWiring factory + register in AGENT_REGISTRY)
│   ├── orchestrator.py                   (the TuathaOrchestrator)
│   ├── operator.py                       (the CianfhoghlaimOperator)
│   ├── cross_subject.py                  (the cross-subject specialist)
│   ├── workflows.py                      (the 4 per-subject workflow handlers: study_plan + exam_paper + marking_scheme + curriculum_change)
│   ├── callbacks/                        (the canonical callbacks: citation, audit)
│   │   ├── __init__.py
│   │   └── citation_callbacks.py
│   ├── mcp_server/                       (the MCP server surface)
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   └── server.py
│   ├── subjects/                         (the 8 NCCA subject agents)
│   │   ├── __init__.py                  (re-exports all 8 subject_agent LlmAgent instances)
│   │   ├── mathematics.py
│   │   ├── applied_mathematics.py
│   │   ├── chemistry.py
│   │   ├── computer_science.py
│   │   ├── english.py
│   │   ├── gaeilge.py
│   │   ├── geography.py
│   │   └── history.py
│   ├── tools/                            (the 40 + 2 consolidated tools)
│   │   ├── __init__.py
│   │   ├── curriculum_search.py           (the cross-subject tool)
│   │   ├── mythology_query.py             (the mythology tool — optional)
│   │   ├── mathematics_syllabus_lookup.py
│   │   ├── mathematics_past_paper_lookup.py
│   │   ├── mathematics_marking_scheme_lookup.py
│   │   ├── mathematics_formative_item_generate.py
│   │   ├── mathematics_response_score.py
│   │   ├── applied_mathematics_syllabus_lookup.py
│   │   ├── applied_mathematics_past_paper_lookup.py
│   │   ├── applied_mathematics_marking_scheme_lookup.py
│   │   ├── applied_mathematics_formative_item_generate.py
│   │   ├── applied_mathematics_response_score.py
│   │   ├── chemistry_syllabus_lookup.py
│   │   ├── chemistry_past_paper_lookup.py
│   │   ├── chemistry_marking_scheme_lookup.py
│   │   ├── chemistry_formative_item_generate.py
│   │   ├── chemistry_response_score.py
│   │   ├── computer_science_syllabus_lookup.py
│   │   ├── computer_science_past_paper_lookup.py
│   │   ├── computer_science_marking_scheme_lookup.py
│   │   ├── computer_science_formative_item_generate.py
│   │   ├── computer_science_response_score.py
│   │   ├── english_syllabus_lookup.py
│   │   ├── english_past_paper_lookup.py
│   │   ├── english_marking_scheme_lookup.py
│   │   ├── english_formative_item_generate.py
│   │   ├── english_response_score.py
│   │   ├── gaeilge_syllabus_lookup.py
│   │   ├── gaeilge_past_paper_lookup.py
│   │   ├── gaeilge_marking_scheme_lookup.py
│   │   ├── gaeilge_formative_item_generate.py
│   │   ├── gaeilge_response_score.py
│   │   ├── gaeilge_gramadach_review.py    (the existing special tool)
│   │   ├── geography_syllabus_lookup.py
│   │   ├── geography_past_paper_lookup.py
│   │   ├── geography_marking_scheme_lookup.py
│   │   ├── geography_formative_item_generate.py
│   │   ├── geography_response_score.py
│   │   ├── history_syllabus_lookup.py
│   │   ├── history_past_paper_lookup.py
│   │   ├── history_marking_scheme_lookup.py
│   │   ├── history_formative_item_generate.py
│   │   └── history_response_score.py
│   ├── agents/
│   │   ├── educational/                 (the 3 educational agents)
│   │   │   ├── __init__.py
│   │   │   ├── academic_history_agent.py
│   │   │   ├── celtic_grammar_agent.py
│   │   │   └── celtic_morphology_agent.py
│   │   ├── media_intel/                 (moved from agents/meaisinfhoghlaim/media_intel/)
│   │   │   ├── __init__.py
│   │   │   ├── records.py
│   │   │   ├── classifier.py
│   │   │   ├── explorer.py
│   │   │   └── media_descriptor_agent.py
│   │   └── hackathon/                   (the 4 BIEP hackathon features)
│   │       ├── __init__.py
│   │       ├── marking_grader.py
│   │       ├── adaptive_tutor.py
│   │       ├── equivalency_generator.py
│   │       └── curriculum_change_sensor.py
│   ├── baml/                             (the consolidated BAML client)
│   │   ├── __init__.py
│   │   ├── qpack_mathematics.baml
│   │   ├── qpack_applied_mathematics.baml
│   │   ├── qpack_chemistry.baml
│   │   ├── qpack_biology.baml
│   │   ├── qpack_english.baml
│   │   ├── qpack_gaeilge.baml
│   │   ├── qpack_geography.baml
│   │   ├── qpack_history.baml
│   │   ├── qpack_physics.baml
│   │   ├── marking_grader.baml
│   │   ├── adaptive_tutor.baml
│   │   ├── equivalency_table.baml
│   │   ├── media_descriptor.baml
│   │   └── clients.baml
│   ├── dlt/                              (the consolidated DLT sources: 8 subjects × 5 categories = 40 + the 3 educational + the 4 hackathon + the media_intel)
│   │   ├── __init__.py
│   │   ├── syllabus/<subject>.py
│   │   ├── past_paper/<subject>.py
│   │   ├── marking_scheme/<subject>.py
│   │   ├── formative_item/<subject>.py
│   │   ├── response_score/<subject>.py
│   │   ├── educational/...
│   │   ├── hackathon/...
│   │   └── media_intel/...
│   ├── dagster/                          (the consolidated Dagster asset groups)
│   │   ├── __init__.py
│   │   ├── per_subject.py
│   │   ├── hackathon.py
│   │   ├── media_intel.py
│   │   └── educational.py
│   ├── cocoindex/                        (the consolidated CocoIndex v1 Apps)
│   │   ├── __init__.py
│   │   ├── per_subject.py
│   │   ├── cross_subject.py
│   │   ├── hackathon.py
│   │   └── media_intel.py
│   ├── notebooks/                        (the consolidated marimo notebooks)
│   │   ├── __init__.py
│   │   ├── per_subject.py
│   │   ├── cross_subject.py
│   │   ├── hackathon.py
│   │   └── media_intel.py
│   ├── badges/                            (the consolidated Crypteolas-equivalent credential system)
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── mint.py
│   │   └── storage.py
│   └── ci/                               (the CI layer)
│       ├── __init__.py
│       └── dagger.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── AGENT_REGISTRY.md
│   ├── THEMING.md
│   └── BIOGRAPHY.md
├── tests/
│   ├── __init__.py
│   ├── test_subject_router_smoke.py
│   ├── test_media_intel_agent.py
│   ├── test_hackathon_features.py
│   └── test_consolidation.py
├── openspec/                            (the project-local openspec)
│   ├── AGENTS.md
│   ├── specs/
│   ├── changes/
│   └── archive/
├── .devcontainer/
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── .dockerignore
└── tuatha/old/                          (the archive)
    ├── prior_top_level_tuasha/  (the pre-existing skeleton)
    ├── scattered_agents_tuasha/  (the 61-file scattered state)
    └── legacy_theming/         (the hard-archived deprecated themes)
```

---

## The per-step file list

| Step | Files |
|:--|:--|
| A.1 | 2 plan files: `CONSOLIDATION_PLAN.md`, `BUILD_PLAN.md` |
| 1.1 | Archive: `tuatha/*` (12 files: 8 dirs + 1 README + 1 .py + 1 .DS_Store + 1 resto_druid_wow_macros.txt) → `tuatha/old/prior_top_level_tuasha/` |
| 1.2 | Archive: `agents/tuatha/*` (61 files + 1 `__pycache__/`) → `tuatha/old/scattered_agents_tuasha/` |
| 1.3 | Hard-archive: Babylon.js / SpacetimeDB / Crypteolas references (5-10 files) → `tuatha/old/legacy_theming/` |
| 2.1 | Re-route: `agents/agent_registry.py:AGENT_REGISTRY` (`media_descriptor_agent` line) |
| 2.2 | Re-path: `agents/meaisinfhoghlaim/media_intel/{__init__,records,media_descriptor_agent}.py` → `tuatha/agents/media_intel/` |
| 2.3 | Archive: `.agents/skills/{tuatha-mmo,tuatha-platform,celtic-asset-generation}/SKILL.md` + any tuatha-specific in meaisinfhoghlaim/ → `tuatha/old/legacy_skills/` |
| 2.4 | Author: `.agents/skills/tuatha/SKILL.md` (the new canonical skill stub) |
| 2.5 | Deprecate: `openspec/specs/tuatha-platform/spec.md` (add a deprecation notice) |
| 2.6 | Author: `openspec/changes/2026-08-25-tuatha-british-isles-mmo-consolidation-v1/{proposal.md, tasks.md, design.md, PHASING.md, cross-repo-sync.md, specs/tuatha-british-isles-mmo/spec.md, specs/tuatha-british-isles-mmo/AGENTS.md, specs/tuatha-platform/spec.md, specs/cianfhoghlaim-educational-mmo/spec.md, specs/repo-hygiene-agent-routing/spec.md}` (~10 files) |
| 3.1 | git: add `origin` remote (operator's action) |
| 3.2 | 6 meta files: `pyproject.toml`, `mise.toml`, `LICENSE`, `README.md`, `AGENTS.md`, `DEVELOPMENT.md` |
| 3.3 | 7 Python files: `tuatha/__init__.py` + 6 modules (`config`, `routing`, `orchestrator`, `operator`, `cross_subject`, `workflows`) |
| 3.4 | 8 subject agents: `tuatha/subjects/{math,appm,chem,comp,engl,gael,geog,hist}.py` + `__init__.py` |
| 3.5 | 40 tool files: `tuatha/tools/<subject>_<tool>.py` |
| 3.6 | 3 educational agents: `tuatha/agents/educational/{academic_history_agent,celtic_grammar_agent,celtic_morphology_agent}.py` + `__init__.py` |
| 3.7 | 5 media_intel files: `tuatha/agents/media_intel/{__init__,records,classifier,explorer,media_descriptor_agent}.py` |
| 3.8 | 4 hackathon features: `tuatha/agents/hackathon/{marking_grader,adaptive_tutor,equivalency_generator,curriculum_change_sensor}.py` + `__init__.py` |
| 3.9 | 13 BAML files: `tuatha/baml/{qpack_<subject>,marking_grader,adaptive_tutor,equivalency_table,media_descriptor,clients}.baml` |
| 3.10 | 40 DLT sources: `tuatha/dlt/{syllabus,past_paper,marking_scheme,formative_item,response_score}/<subject>.py` |
| 3.11 | 3 Dagster modules: `tuatha/dagster/{per_subject,hackathon,media_intel}.py` |
| 3.12 | 4 CocoIndex apps: `tuatha/cocoindex/{per_subject,cross_subject,hackathon,media_intel}.py` |
| 3.13 | 4 marimo notebooks: `tuatha/notebooks/{per_subject,cross_subject,hackathon,media_intel}.py` |
| 3.14 | 3 badges modules: `tuatha/badges/{models,mint,storage}.py` |
| 3.15 | 4 docs: `tuatha/docs/{ARCHITECTURE,AGENT_REGISTRY,THEMING,BIOGRAPHY}.md` |
| 3.16 | 4 tests: `tuatha/tests/{test_subject_router_smoke,test_media_intel_agent,test_hackathon_features,test_consolidation}.py` |
| 3.17 | 2 CI files: `.github/workflows/ci.yml` + `tuatha/ci/dagger.py` |
| 3.18 | 3 dev-container files: `.devcontainer/`, `.gitignore`, `.dockerignore` |
| 3.19 | git add + commit + push to `github.com/cianmacandeisigh/tuatha.git` |
| 3.20 | Run the 6 quality gates + final report |

---

## The commit strategy

Per the concurrent-write safety protocol (per the AGENTS.md):

- **One commit per step** (A.1, A.2, 1.1, 1.2, 1.3, 2.1, 2.2, ...)
- **Use `git add <path>` explicitly** — NEVER `git add -A`
- **Verify the staged state** with `git status` before commit
- **No `git push` unless the user explicitly says "push"** at that step

The full execution = 20+ commits across 3 phases. The pushes happen
at the natural phase boundaries.

---

**Last updated**: 2026-08-25.
**Owner**: Build agent (the per-step execution).
