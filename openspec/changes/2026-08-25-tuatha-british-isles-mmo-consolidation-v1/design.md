# Design — Tuatha British Isles MMO Consolidation v1

## 1. The 3-layer architecture

### Layer 1 — Archive (`tuatha/old/`)

3 sub-archives preserve every prior state for reference:

```
tuatha/old/
├── prior_top_level_tuasha/    (12 items: 8 dirs + 1 .py + 1 README + 1 .DS_Store + 1 random .txt + the 2 plan files I just committed in the prior commit eef6d60e7)
├── scattered_agents_tuasha/   (63 items: 61 source files + 1 __pycache__/ + 1 .DS_Store — moved from agents/tuasha/)
└── legacy_theming/            (1 item: babylonjs/SKILL.md — the hard-archived Babylon.js skill)
```

The other legacy theming skills (tuatha-mmo, tuatha-platform,
celtic-asset-generation, spacetimedb, crypteolas) are in
`.claude/worktrees/.../.agents/skills_backup/` — already
archived, no further action.

### Layer 2 — Cross-repo re-routes

| Re-route | From | To |
|:--|:--|:--|
| The `media_descriptor_agent` registration | `agents.meaisinfhoghlaim.media_intel.media_descriptor_agent` | `tuatha.agents.media_intel.media_descriptor_agent` |
| The 3 media_intel source files | `agents/meaisinfhoghlaim/media_intel/` | `tuatha/agents/media_intel/` |
| The back-compat shim | (none) | `agents/meaisinfhoghlaim/media_intel/__init__.py` (re-exports the canonical symbols from the new location) |
| The Babylon.js skill | `.agents/skills/babylonjs/` | `tuatha/old/legacy_theming/babylonjs/` |
| The new canonical skill stub | (none) | `.agents/skills/tuatha/SKILL.md` (deferred to a subsequent change) |
| The deprecated `tuatha-platform` spec | (no deprecation header in `openspec/specs/tuatha-platform/spec.md` currently) | add the deprecation header (deferred to a subsequent change) |

### Layer 3 — The new `tuatha/` project from scratch

The structure (per `tuatha/BUILD_PLAN.md`):

```
tuatha/                                # the new independent repo
├── CONSOLIDATION_PLAN.md              # the high-level plan
├── BUILD_PLAN.md                       # the per-step execution plan
├── README.md                           # the canonical British Isles MMO README
├── AGENTS.md                           # the routing doc
├── DEVELOPMENT.md                      # the how-to-add-an-agent doc
├── pyproject.toml                      # the package meta
├── mise.toml                           # the mise task namespace
├── LICENSE                             # MIT
├── docker-compose.yml                  # the local-dev stack
├── tuatha/                               # the canonical Python sub-namespace
│   ├── __init__.py                     (re-exports)
│   ├── config.py                        (LiteLLM + Langfuse + Cognee + Letta + BAML clients)
│   ├── routing.py                       (the SubjectAgentWiring factory)
│   ├── orchestrator.py                  (the TuathaOrchestrator)
│   ├── operator.py                      (the CianfhoghlaimOperator)
│   ├── cross_subject.py                 (the cross-subject specialist)
│   ├── workflows.py                     (the 4 per-subject workflow handlers)
│   ├── callbacks/                       (the canonical callbacks: citation, audit)
│   ├── mcp_server/                      (the MCP server)
│   ├── subjects/                        (the 8 NCCA subject agents)
│   │   ├── mathematics.py
│   │   ├── applied_mathematics.py
│   │   ├── chemistry.py
│   │   ├── computer_science.py
│   │   ├── english.py
│   │   ├── gaeilge.py
│   │   ├── geography.py
│   │   └── history.py
│   ├── tools/                           (the 40 + 2 consolidated tools)
│   ├── agents/
│   │   ├── educational/                (the 3 educational agents)
│   │   │   ├── academic_history_agent.py
│   │   │   ├── celtic_grammar_agent.py
│   │   │   └── celtic_morphology_agent.py
│   │   ├── media_intel/                 (moved in T2.2)
│   │   │   ├── __init__.py
│   │   │   ├── records.py
│   │   │   ├── classifier.py           (NEW)
│   │   │   ├── explorer.py            (NEW)
│   │   │   └── media_descriptor_agent.py
│   │   └── hackathon/                   (the 4 BIEP hackathon features)
│   │       ├── marking_grader.py
│   │       ├── adaptive_tutor.py
│   │       ├── equivalency_generator.py
│   │       └── curriculum_change_sensor.py
│   ├── baml/                            (the consolidated BAML client — 13 files)
│   ├── dlt/                             (the consolidated DLT sources — 40 per-subject)
│   ├── dagster/                         (the consolidated Dagster asset groups)
│   ├── cocoindex/                       (the consolidated CocoIndex v1 Apps)
│   ├── notebooks/                       (the consolidated marimo notebooks)
│   ├── badges/                          (the educational-credential badge system)
│   └── ci/                              (the CI layer)
├── docs/                               (the 4 canonical docs)
├── tests/                              (the 4 test files)
├── openspec/                           (the project-local openspec)
├── .devcontainer/
├── .github/workflows/ci.yml
├── .gitignore
├── .dockerignore
└── tuatha/old/                          (the archive)
    ├── prior_top_level_tuasha/
    ├── scattered_agents_tuasha/
    └── legacy_theming/
```

Total: **~300 files**.

## 2. The British Isles Formative Assessment MMO theme

The 8 NCCA Leaving Certificate subjects are:

- mathematics
- applied_mathematics
- chemistry
- geography
- history
- english
- gaeilge
- computer_science

Each subject has:
- A `qpack_<subject>.baml` BAML contract
- A `<subject>_agent.py` ADK agent
- 5 per-subject tools (syllabus / past_paper / marking_scheme / formative_item / response_score)
- A per-subject DLT source + Dagster asset group + CocoIndex App + marimo notebook

**The 3 educational agents** (per `agents/meaisinfhoghlaim/educational/`):
- `academic_history_agent` — the cross-subject + cross-jurisdiction history research agent
- `celtic_grammar_agent` — the Irish grammar specialist (gaelicisation + dialectical forms + corpus reference)
- `celtic_morphology_agent` — the Celtic morphology specialist (prefix + suffix + infix patterns + calque identification)

**The 4 BIEP hackathon features** (per `openspec/changes/2026-08-21-biiep-hackathon-agentic-educational-system-v1/`):
- `marking_grader` — the Adaptive Marking Grader (student uploads answer + marking scheme → instant grade + feedback)
- `adaptive_tutor` — the Adaptive Tutor Chat (stateful 6-jurisdiction syllabus tutor with persistent memory)
- `equivalency_generator` — the Cross-Jurisdiction Equivalency Generator (compare LC ↔ A-Level ↔ GCSE topics side-by-side)
- `curriculum_change_sensor` — the Curriculum Change Detection Sensor (Dagster sensor that watches NCCA + AQA + SQA + WJEC + CCEA + IoM websites)

**The 1 media_intel pipeline** (moved from `agents/meaisinfhoghlaim/media_intel/`):
- `media_descriptor_agent` — the 10-tool ADK agent (5 per-medium extractors + 5 corpus introspection tools)
- The 5-class source registry (comics, prose, animation, games, official)
- The 7-axis medium-agnostic `MediaDescriptor` schema
- The 36 official records across 3 government sub-buckets (UK + Éire + Crown Dependencies)
- The 9 Celtic-history stub sources (gated for the downstream theming change)

## 3. The themes that get HARD-ARCHIVED

| Deprecated theme | Why archived | Where archived |
|:--|:--|:--|
| **Pent-Elemental Cosmology** (5 realms: Spirit / Water / Fire / Earth / Air) | Per the canonical `cianfhoghlaim-educational-mmo` spec, this design "did not land" | The Pent-Elemental references are in the agents/tuatha/ files (now in `tuatha/old/scattered_agents_tuasha/`) |
| **Babylon.js 3D** game front-end | Replaced with the TanStack Start 2D client per the canonical spec | `.agents/skills/babylonjs/SKILL.md` → `tuatha/old/legacy_theming/babylonjs/SKILL.md` |
| **SpacetimeDB v2** game engine backend | Replaced with Convex + Hono + Dagster + DuckLake per the canonical spec | The SpacetimeDB skill was already in `.claude/worktrees/.../.agents/skills_backup/` |
| **Crypteolas financial token** | Replaced with the educational-credential badge system per the canonical spec | The Crypteolas skill was already in `.claude/worktrees/.../.agents/skills_backup/` |
| **Anam Cara** soul friend mechanic | Per the canonical spec, the soul concept is now `tuatha-hackathon-features` + the 4 BIEP hackathon ideas | The Anam Cara references are in `tuatha/old/scattered_agents_tuasha/anam.md` |
| **Brown Ajah** theming (the 8 NCCA subject ↔ Tuatha Dé deity mapping) | Per the canonical spec, the "Brown Ajah" name is dropped | The Brown Ajah references are in `tuatha/old/scattered_agents_tuasha/subject_router.py` |

## 4. The drift the consolidation fixes (per the brief)

| Drift | Before | After |
|:--|:--|:--|
| `rights_holder: "Wikipedia Foundation"` for the 9 Celtic-history topics | in Class E (official) | MOVED to `celtic_history_research/` stubs with `rights_holder: "Wikipedia editors (CC-BY-SA-4.0)"` per licence |
| The 12 Wikipedia entries that were the original drift | in `agents/meaisinfhoghlaim/media_intel/` (a `meaisinfhoghlaim/` path, not a `tuasha/` path) | MOVED to `tuatha/agents/media_intel/` (the canonical British Isles MMO path) |
| The scattered `agents/tuasha/` | 61 files, 2 inconsistent layers (top-level + new `agents/` subdir) | ARCHIVED to `tuatha/old/scattered_agents_tuasha/` |
| The prior top-level `tuasha/` skeleton | 8 dirs + 1 file + 1 README + 1 random `.txt` (orphaned) | ARCHIVED to `tuatha/old/prior_top_level_tuasha/` |
| The Babylon.js skill (the only live theming reference) | at `.agents/skills/babylonjs/` | MOVED to `tuatha/old/legacy_theming/babylonjs/` |
| The media_descriptor_agent module path | `agents.meaisinfhoghlaim.media_intel.media_descriptor_agent` | `tuasha.agents.media_intel.media_descriptor_agent` |

## 5. The drift the consolidation creates (the costs)

| Cost | When it appears | How to resolve |
|:--|:--|:--|
| The new `tuatha/agents/media_intel/` is at the parent repo's `tuatha/` sub-dir (not yet a separate repo) | The new tuatha repo doesn't yet exist | Operator initializes `github.com/cianmacandeisigh/tuatha.git` + splits the parent dir into the new repo |
| The parent's other code that imports from `agents.meaisinfhoghlaim.media_intel.*` still works (via the back-compat shim) | The shim re-exports from the new location | Back-compat shim is removed in a subsequent change after the new tuatha repo is published |
| The `tuatha/old/` directories will accumulate stale state if not cleaned | Each subsequent change adds to the archive | A periodic `tuatha/old/` cleanup change is needed |

## 6. The future theming change is NOT in scope

Per the `media-intel-gameplay-capture-research-v1` change's reminder:

> *"The Celtic MMO design itself is not in this change. This change
> is the source pipeline. The design of the game (which elements,
> what the boons look like, the 4+1 element binding, the sub-
> nation mapping) is the downstream theming change gated on this
> corpus being populated."*

The new `tuatha/` project carries forward:
- The 5-class source registry
- The 7-axis `MediaDescriptor` schema
- The 8 NCCA subject agents
- The 4 BIEP hackathon features
- The 3 educational agents
- The BAML / DLT / Dagster / CocoIndex / marimo pipeline stack
- The web surface (TanStack Start + Convex + Hono + CopilotKit)

The Celtic MMO design itself — which elements, what boons, the
4+1 element binding, the sub-nation mapping, the 2D particle
renderer choice, the iOS delivery vehicle — is a downstream
theming change gated on the corpus being populated.

## 7. The 6 quality gates

```
G1: openspec validate 2026-08-25-tuatha-british-isles-mmo-consolidation-v1 --strict   PASS
G2: openspec validate --all --strict                                                    145/147 (or better)
G3: mise run lint:registry                                                             0 hardcoded model strings
G4: ruff check                                                                         All checks passed
G5: ast.parse                                                                          N/N passed
G6: Python import tuatha.agents.media_intel.* (no circular import)                      IMPORTED OK
```
