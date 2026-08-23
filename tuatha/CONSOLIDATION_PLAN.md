# CONSOLIDATION PLAN — `tuatha` v1

> **The British Isles Formative Assessment MMO** — the consolidated,
> independent Tuatha project. A self-contained Python sub-repo at
> `/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/` that
> supersedes the scattered `agents/tuatha/` and the prior
> top-level `tuatha/` skeleton.

---

## 1. Why

The Cianfhoghlaim monorepo (`/Users/cianmacandeisigh/dev/kings_college_galway/`)
carries the British Isles Formative Assessment MMO in 3 scattered locations:

1. **The `agents/tuatha/` tree** — 61 files (8 subject agents + 40
   subject-specific tools + 5 support files + 4 doc files + 1
   partial-refactor subdir)
2. **The prior top-level `tuatha/` skeleton** — 8 dirs + 1 Python
   file + 1 README + 1 random `resto_druid_wow_macros.txt`
3. **The `agents/meaisinfhoghlaim/media_intel/` module** — the
   10-tool media descriptor agent from this turn's prior
   `2026-08-23-tuatha-media-intel-gameplay-capture-research-v1`
   change

These 3 locations are NOT interconnected. They document overlapping
concerns of the same project. The canonical openspec spec
`openspec/specs/cianfhoghlaim-educational-mmo/spec.md` (which
supersedes the deprecated `tuatha-platform` spec) says:

> *"The historic skills `.agents/skills_backup/tuatha-mmo/` and
> `.agents/skills_backup/tuatha-platform/` are preserved as
> archaeology — they document an earlier Babylon.js 3D + SpacetimeDB
> v2 + Pent-Elemental Cosmology + Crypteolas financial token
> design that did not land. **The new build drops those themes
> but keeps the technological choices.**"*

The user is consolidating everything into a single coherent
**independent sub-project** at
`/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/`
that will become its own GitHub repo
(`github.com/cianmacandeisigh/tuatha.git`), similar to the
prior repo split that produced `kings_college_galway/leabharlann/`
and `kings_college_galway/bonneagar/` as independent repos.

## 2. The user-locked decisions (the 4 Q&A answers)

| Decision | Value | Source |
|:--|:--|:--|
| Repo URL | `github.com/cianmacandeisigh/tuatha.git` (user-owned, matching the `leabharlann` + `bonneagar` pattern at the parent `kings_college_galway` workspace) | user |
| Module name | `tuatha` (the directory is `tuatha`, the package is `tuatha`, the pyproject declares `name = "tuatha"`, all imports are `tuatha.*`) | user |
| Scope | **Full scope** — Step 1 (Archive) + Step 2 (Cross-repo refactor) + Step 3 (Build from scratch) | user |
| 3 educational agents | **Bring them in** under `tuatha/agents/educational/` (academic_history_agent + celtic_grammar_agent + celtic_morphology_agent) | user |
| 3 deprecated themes (Babylon.js / SpacetimeDB / Crypteolas) | **Hard-archive** to `tuatha/old/legacy_theming/`. No "experimental" sub-module. No "preserved-for-fork" flag. | user |

## 3. The 3-step execution

### Step 1 — Archive the prior state

```
mkdir -p /Users/cianmacandeisigh/dev/kings_college_galway/tuatha/old/
mv /Users/cianmacandeisigh/dev/kings_college_galway/tuatha/{*,.[!.]*} \
   /Users/cianmacandeisigh/dev/kings_college_galway/tuatha/old/prior_top_level_tuatha/
mv /Users/cianmacandeisigh/dev/kings_college_galway/agents/tuatha/{*,.[!.]*} \
   /Users/cianmacandeisigh/dev/kings_college_galway/tuatha/old/scattered_agents_tuatha/
# Hard-archive the 3 deprecated theming references
mkdir -p /Users/cianmacandeisigh/dev/kings_college_galway/tuatha/old/legacy_theming/
# Find every Babylon.js / SpacetimeDB / Crypteolas file across the repo
# (skills, openspec specs, anywhere) and move to legacy_theming/
```

Resulting `tuatha/old/` structure:

```
tuatha/old/
├── prior_top_level_tuatha/  (the pre-existing skeleton)
├── scattered_agents_tuatha/  (the 61-file scattered state)
└── legacy_theming/         (the hard-archived deprecated themes)
```

This step is **purely archival** — no deletion, no refactor.

### Step 2 — Refactor all cross-repo references to the British Isles theme

The user said: *"the likes of `agents/tuatha` and other prominent
references whether in `skills/`, `openspec/`, or `meaisinfhoghlaim` —
or anywhere else throughout the project — get refactored to be of
use of our agreed upon British Isles MMO theme and features but
with the benefits of the types of software-dev packages redefined
for our new purpose; while getting copied into the `tuatha/old/`
for reference to previous such implementations."*

**The cross-repo references to scan + refactor:**

| Reference | Where | Action |
|:--|:--|:--|
| `agents/tuatha/` (61 files) | already moved to `tuatha/old/scattered_agents_tuasha/` in Step 1 | already done in Step 1 |
| `agents/meaisinfhoghlaim/media_intel/` (3 files) | the just-shipped media_intel | move to `tuatha/agents/media_intel/` |
| `agents/agent_registry.py:AGENT_REGISTRY` (the `media_descriptor_agent` entry) | `agents/agent_registry.py` | re-path `module_path` from `agents.meaisinfhoghlaim.media_intel.media_descriptor_agent` to `tuatha.agents.media_intel.media_descriptor_agent` |
| `.agents/skills/tuatha-mmo/` (may exist from prior pivot) | `.agents/skills/` | archive + replace with `.agents/skills/tuatha/SKILL.md` |
| `.agents/skills/tuatha-platform/` | `.agents/skills/` | archive |
| `.agents/skills/celtic-asset-generation/` | `.agents/skills/` | archive or update |
| `.agents/skills/meaisinfhoghlaim/` (anything tuatha-specific) | `.agents/skills/` | update references |
| `openspec/specs/tuatha-platform/spec.md` | `openspec/specs/` | **DEPRECATE** per the `cianfhoghlaim-educational-mmo` spec directive |
| `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` | `openspec/specs/` | **This is the canonical spec.** Keep. The new tuatha implements it. |
| `openspec/changes/2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/` | `openspec/changes/` | The new tuatha carries over the work |
| `openspec/changes/2026-08-21-biiep-hackathon-agentic-educational-system-v1/` | `openspec/changes/` | The new tuatha carries over the 4 hackathon features |
| The 5 pending parent changes | `openspec/changes/` | These reference tuatha via celtic-history-research + ogham + geospatial + familiar + spacetimedb. They need a re-bump after the tuatha repo split. |

### Step 3 — Build the new `tuatha/` from scratch (the British Isles MMO)

See `BUILD_PLAN.md` for the per-step execution.

## 4. The British Isles Formative Assessment MMO theme

The new project ADOPTS the canonical theme per the
`cianfhoghlaim-educational-mmo` spec. The 8 NCCA Leaving
Certificate subjects are:

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
- A `<subject>_agent.py` ADK agent (8 total — math/appm/chem/geog/hist/engl/gael/comp)
- 5 per-subject tools (syllabus / past_paper / marking_scheme / formative_item / response_score)
- A per-subject DLT source + Dagster asset group + CocoIndex App + marimo notebook

**DROPS** the deprecated themes (per the `cianfhoghlaim-educational-mmo` spec):
- ~~Pent-Elemental Cosmology~~ (5 realms: Spirit / Water / Fire / Earth / Air)
- ~~Babylon.js 3D~~ game front-end
- ~~SpacetimeDB v2~~ game engine backend
- ~~Crypteolas financial token~~ (replaced with the educational-credential badge system)
- ~~Anam Cara~~ soul friend mechanic (the soul concept is now `tuatha-hackathon-features` + the 4 BIEP hackathon ideas)
- ~~Brown Ajah theming~~ (the 8 NCCA subject ↔ Tuatha Dé deity mapping is preserved as `tuatha/subjects/character.py` but the "Brown Ajah" name is dropped)

**KEEPS** the technological choices:
- The 8 NCCA subject agents (refactored into `tuatha/subjects/`)
- The 40 subject-specific tools (refactored into `tuatha/tools/`)
- The 12-agent fleet pattern (root_agent + curriculum_agent + ...)
- The 3 educational agents (academic_history_agent + celtic_grammar_agent + celtic_morphology_agent)
- The 4 BIEP hackathon features (Marking Grader + Adaptive Tutor + Equivalency Generator + Curriculum Change Sensor)
- The media_intel pipeline (10-tool media descriptor agent + the 5-class source registry)
- The BAML extraction + DLT + Dagster + CocoIndex + marimo pipeline stack
- The Hono + Convex + TanStack Start + CopilotKit web stack
- The LiteLLM + Cognee + Graphiti + LanceDB + Letta memory stack
- The educational-credential badge system (the `badges/` subdir; the previous `crypteolas/` financial-token system is archived)

## 5. The quality gates

```
G1: openspec validate 2026-08-25-tuatha-british-isles-mmo-consolidation-v1 --strict   PASS
G2: openspec validate --all --strict                                                   145/147 (or better)
G3: mise run lint:registry                                                            0 hardcoded model strings
G4: ruff check                                                                        All checks passed
G5: ast.parse                                                                         N/N passed
G6: Python import tuatha.* (no circular import)                                       IMPORTED OK
G7: git push origin main                                                              Pushed
```

## 6. The git workflow

- The new `tuatha/` becomes its own git repo (analogous to
  `kings_college_galway/leabharlann/` and
  `kings_college_galway/bonneagar/`). The current
  `kings_college_galway/` monorepo will retain a `tuatha/` directory
  that is a **git worktree** of the new repo, OR the new repo
  replaces the monorepo subdir entirely (operator's call).
- The default branch is `main` (matching `leabharlann` + `bonneagar`).
- The LICENSE is MIT (permissive; matches the parent's overall license).
- The CI is GitHub Actions + Dagger (per the BIEP hackathon change pattern).
- The deployment target is a private repo on
  `github.com/cianmacandeisigh/` (operator's call on public/private).

## 7. Operator actions

- Confirm the `github.com/cianmacandeisigh/tuatha.git` repo is
  created (I cannot initialize a fresh remote from this client)
- Decide whether the new tuatha should be a private or public repo
  (the prior `bonneagar` + `leabharlann` are private)
- Review the structure in `BUILD_PLAN.md` — if you want any sub-dir
  moved or added, this is the moment
- Confirm the commit strategy (single mega-commit per step, or one
  commit per Phase 3 sub-step)

---

**Last updated**: 2026-08-25.
**Owner**: Build agent (the consolidated plan).
