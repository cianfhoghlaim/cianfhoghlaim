# Change: Tuatha British Isles MMO Consolidation v1

## Why

The Cianfhoghlaim monorepo (`/Users/cianmacandeisigh/dev/kings_college_galway/`)
currently carries the British Isles Formative Assessment MMO in
**3 scattered locations** that are not interconnected:

1. **`agents/tuatha/`** — 61 files (8 subject agents + 40 subject-
   specific tools + 5 support files + 4 doc files + 1 partial-
   refactor `agents/` subdir)
2. **The prior top-level `tuatha/` skeleton** at the monorepo
   root — 8 dirs + 1 file + 1 README + 1 random
   `resto_druid_wow_macros.txt` (now archived to
   `tuatha/old/prior_top_level_tuasha/`)
3. **`agents/meaisinfhoghlaim/media_intel/`** — the 10-tool
   media descriptor agent (now moved to
   `tuatha/agents/media_intel/`)

The canonical openspec spec
`openspec/specs/cianfhoghlaim-educational-mmo/spec.md`
(which supersedes the deprecated `tuatha-platform` spec) says:

> *"The historic skills `.agents/skills_backup/tuatha-mmo/` and
> `.agents/skills_backup/tuatha-platform/` are preserved as
> archaeology — they document an earlier Babylon.js 3D + SpacetimeDB
> v2 + Pent-Elemental Cosmology + Crypteolas financial token
> design that did not land. The new build drops those themes
> but keeps the technological choices."*

The change consolidates everything into a **single coherent
independent sub-project** at
`/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/`
that will become its own GitHub repo
(`github.com/cianmacandeisigh/tuatha.git`).

## What changes

### Layer 1 — Archive (the prior state → `tuatha/old/`)

The 3 sub-archives:

- `tuatha/old/prior_top_level_tuasha/` — the 12-item prior
  top-level skeleton (8 dirs + 1 file + 1 README + 1 .DS_Store +
  1 random `resto_druid_wow_macros.txt` + 2 plan files I made
  + the 2 plan files I just committed in the prior commit
  `eef6d60e7`)
- `tuatha/old/scattered_agents_tuasha/` — the 63-file scattered
  state from `agents/tuatha/` (61 source files + `__pycache__/`
  + `.DS_Store`)
- `tuatha/old/legacy_theming/` — the hard-archived
  Babylon.js / SpacetimeDB / Crypteolas / Pent-Elemental
  Cosmology / Anam Cara / Brown Ajah theming references
  (1 file: the `.agents/skills/babylonjs/SKILL.md`)

### Layer 2 — Cross-repo references (the re-routes)

- **`agents/agent_registry.py:AGENT_REGISTRY`** — the
  `media_descriptor_agent` entry's `module_path` is re-routed
  from `agents.meaisinfhoghlaim.media_intel.media_descriptor_agent`
  to `tuatha.agents.media_intel.media_descriptor_agent`
- **`agents/meaisinfhoghlaim/media_intel/`** — the 3 source
  files (`__init__.py` + `media_descriptor_agent.py` +
  `records.py`) are moved to `tuatha/agents/media_intel/`. A
  back-compat shim at the old location re-exports the
  canonical symbols from the new location.
- **`.agents/skills/babylonjs/`** — moved to
  `tuatha/old/legacy_theming/babylonjs/`. No new
  Babylon.js references in the new project.
- **The other legacy theming skills** (tuatha-mmo,
  tuatha-platform, celtic-asset-generation, spacetimedb,
  crypteolas) are in
  `.claude/worktrees/.../.agents/skills_backup/` — already
  archived, no further action.
- **`.agents/skills/tuatha/SKILL.md`** — a new canonical
  skill stub that points at the new
  `github.com/cianmacandeisigh/tuatha.git` repo

### Layer 3 — Build the new `tuatha/` project from scratch

The new project implements the
`openspec/specs/cianfhoghlaim-educational-mmo/spec.md`
canonical spec. The structure (per `tuatha/BUILD_PLAN.md`):

- `tuatha/{__init__,config,routing,orchestrator,operator,cross_subject,workflows}.py` —
  the 7 Python package modules
- `tuatha/subjects/{mathematics,applied_mathematics,chemistry,computer_science,english,gaeilge,geography,history}.py` —
  the 8 NCCA subject agents
- `tuatha/tools/<subject>_<tool>.py` — 40 per-subject tools
  (8 subjects × 5 tools)
- `tuatha/agents/educational/{academic_history_agent,celtic_grammar_agent,celtic_morphology_agent}.py` —
  the 3 educational agents
- `tuatha/agents/media_intel/{__init__,records,classifier,explorer,media_descriptor_agent}.py` —
  the 5 media_intel files
- `tuatha/agents/hackathon/{marking_grader,adaptive_tutor,equivalency_generator,curriculum_change_sensor}.py` —
  the 4 BIEP hackathon features
- `tuatha/baml/{qpack_<subject>,marking_grader,adaptive_tutor,equivalency_table,media_descriptor,clients}.baml` —
  13 BAML files
- `tuatha/dlt/`, `tuatha/dagster/`, `tuatha/cocoindex/`,
  `tuatha/notebooks/`, `tuatha/badges/`, `tuatha/ci/` — the
  consolidated pipeline stack
- `tuatha/docs/{ARCHITECTURE,AGENT_REGISTRY,THEMING,BIOGRAPHY}.md` —
  the 4 canonical docs
- `tuatha/tests/` — the 4 test files
- `tuatha/{pyproject.toml,mise.toml,LICENSE,README.md,AGENTS.md,DEVELOPMENT.md,docker-compose.yml}` —
  the 7 meta files
- `.github/workflows/ci.yml` + `.devcontainer/` + `.gitignore` +
  `.dockerignore` — the CI/dev-environment layer

## Out of scope

- The Celtic MMO design itself (which elements to use, what
  the boons look like, the 4+1 element binding, the sub-
  nation mapping) — deferred to a downstream theming change
  gated on the corpus being populated
- The Babylon.js 3D game front-end — hard-archived (the new
  project uses the TanStack Start 2D client per the canonical
  `cianfhoghlaim-educational-mmo` spec)
- The SpacetimeDB v2 game engine backend — hard-archived
  (the new project uses Convex + Hono + Dagster + DuckLake
  per the canonical spec)
- The Crypteolas financial token — hard-archived (the new
  project uses the educational-credential badge system per
  the canonical spec)
- The Pent-Elemental Cosmology + Anam Cara + Brown Ajah
  theming — hard-archived

## Dependencies

```markdown
## Dependencies

`Blocked by: 2026-09-01-celtic-mythology-content-system-v1` (the parent change that creates `baml/celtic/mythology.baml` + the 6 pantheons + the GeoAI helpers + the Celtic Mythology Agent + the Fibo+ComfyUI enablement).

`Blocked by: 2026-09-08-ogham-celtic-stones-pipeline-v1` (the parent change that creates `ogham_stones` + `anam_particles` Convex tables + the spatial grid utility + the Ogham Stone Agent — the agentic capture is informed by this).

`Blocked by: 2026-09-22-geospatial-british-isles-twin-v1` (the parent change that creates the 5 geospatial DLT sources + the `notebooks/_shared/spatial_grid.py` helper + the `notebooks/37_geospatial_explorer.py` UI).

`Blocked by: 2026-09-29-familiar-dynamic-nft-system-v1` (the parent change that creates the 3 Convex tables + the Anam Progression Agent + the Fibo enablement — the family-system research context).

`Blocked by: 2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1` (the parent change that formalises the renderer + backend rejection + archives the orphaned Rust crates).

`Blocked by (soft): 2026-08-21-biiep-hackathon-agentic-educational-system-v1` (the sibling tangent; the new tuatha carries over the 4 hackathon features).

`Blocked by (soft): 2026-08-23-tuatha-media-intel-gameplay-capture-research-v1` (the sibling tangent; the new tuatha carries over the media_intel work).

`Blocked by (soft): 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1` (every model string MUST route through `MODEL_REGISTRY`; every BAML function MUST codegen to Pydantic + Zod + Convex + DuckLake DDL).

`Affected repos: cianfhoghlaim, tuatha (new repo)`
```

## Impact

Affected specs (1 NEW + 2 MODIFIED + 0 collisions):

| Spec | Action | ADDED / MODIFIED Requirements |
|:--|:--|:--|
| `tuatha-british-isles-mmo` | **NEW** | 5 ADDED Requirements (the canonical British Isles Formative Assessment MMO spec for the new tuatha project) |
| `tuatha-platform` | MODIFIED | 1 ADDED Requirement (the deprecation notice: superseded by `cianfhoghlaim-educational-mmo`) |
| `cianfhoghlaim-educational-mmo` | MODIFIED | 1 ADDED Requirement (the canonical spec that the new tuatha implements) |

Affected code/config (executed in this change):

- `tuatha/CONSOLIDATION_PLAN.md` (the high-level plan, 195 lines)
- `tuatha/BUILD_PLAN.md` (the per-step execution plan, 284 lines)
- `tuatha/old/prior_top_level_tuasha/` (the 12-item prior top-level state)
- `tuatha/old/scattered_agents_tuasha/` (the 63-file scattered state)
- `tuatha/old/legacy_theming/babylonjs/SKILL.md` (the hard-archived Babylon.js skill)
- `tuatha/agents/media_intel/{__init__,records,media_descriptor_agent}.py` (moved from `agents/meaisinfhoghlaim/media_intel/`)
- `agents/agent_registry.py:AGENT_REGISTRY` (re-routed `media_descriptor_agent` module path to `tuatha.agents.media_intel.media_descriptor_agent`)
- `agents/meaisinfhoghlaim/media_intel/__init__.py` (the back-compat shim)

## Cross-references

- [`../../specs/cianfhoghlaim-educational-mmo/spec.md`](../../specs/cianfhoghlaim-educational-mmo/spec.md)
  — the canonical spec that the new tuatha implements
- [`../../specs/tuatha-platform/spec.md`](../../specs/tuatha-platform/spec.md)
  — the deprecated spec (DEPRECATED in this change)
- [`./specs/tuatha-british-isles-mmo/spec.md`](./specs/tuatha-british-isles-mmo/spec.md)
  — the new canonical spec for the new tuatha
- [`../../../tuatha/CONSOLIDATION_PLAN.md`](../../../tuatha/CONSOLIDATION_PLAN.md)
  — the high-level plan
- [`../../../tuatha/BUILD_PLAN.md`](../../../tuatha/BUILD_PLAN.md)
  — the per-step execution plan
- [`../2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/`](./2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/)
  — the sibling tangent (the new tuatha carries over the media_intel work)
- [`../2026-08-21-biiep-hackathon-agentic-educational-system-v1/`](./2026-08-21-biiep-hackathon-agentic-educational-system-v1/)
  — the sibling tangent (the new tuatha carries over the 4 hackathon features)
- [`../2026-09-01-celtic-mythology-content-system-v1/`](./2026-09-01-celtic-mythology-content-system-v1/)
  — the parent change (must archive first)
- [`../2026-09-08-ogham-celtic-stones-pipeline-v1/`](./2026-09-08-ogham-celtic-stones-pipeline-v1/)
  — the parent change (must archive first)
- [`../2026-09-22-geospatial-british-isles-twin-v1/`](./2026-09-22-geospatial-british-isles-twin-v1/)
  — the parent change (must archive first)
- [`../2026-09-29-familiar-dynamic-nft-system-v1/`](./2026-09-29-familiar-dynamic-nft-system-v1/)
  — the parent change (must archive first)
- [`../2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1/`](./2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1/)
  — the parent change (must archive first)
- [`../2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/`](../2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/)
  — the soft-blocker (every model + schema must route through it)
- [`../../AGENTS.md`](../../AGENTS.md) — the platform root
- [`../../../AGENTS.md`](../../../AGENTS.md) — the monorepo root

## The 6 quality gates

```
G1: openspec validate 2026-08-25-tuatha-british-isles-mmo-consolidation-v1 --strict   PASS
G2: openspec validate --all --strict                                                    145/147 (or better)
G3: mise run lint:registry                                                             0 hardcoded model strings
G4: ruff check                                                                         All checks passed
G5: ast.parse                                                                          N/N passed
G6: Python import tuatha.agents.media_intel.* (no circular import)                      IMPORTED OK
```
