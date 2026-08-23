# `tuatha` — Developer Quick-Reference

> **The British Isles Formative Assessment MMO** — the
> canonical implementation of the
> [`cianfhoghlaim-educational-mmo`](../../openspec/specs/cianfhoghlaim-educational-mmo/spec.md)
> spec. A self-contained independent sub-project at
> `/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/`
> (the new top-level `tuatha/` dir; will become the independent
> GitHub repo at `github.com/cianmacandeisigh/tuatha.git`).

## Routing

Load this AGENTS.md when:

- You are adding or modifying anything in the new `tuatha/`
  sub-project (the 8 subject agents, the 40 per-subject tools,
  the 3 educational agents, the 4 BIEP hackathon features, the
  1 media_intel pipeline, the BAML contracts, the DLT sources,
  the Dagster asset groups, the CocoIndex v1 Apps, the marimo
  notebooks, the badges credential system, the web layer,
  the CI, the docs, the tests)
- You are updating the cross-repo references in the parent
  cianfhoghlaim monorepo (the parent's `agents/agent_registry.py`
  + the back-compat shim at `agents/meaisinfhoghlaim/media_intel/`)
- You are writing the openspec change that documents the
  consolidation (see the canonical change
  `2026-08-25-tuatha-british-isles-mmo-consolidation-v1`)

For the broader tuatha spec context, see
`openspec/specs/tuatha-british-isles-mmo/spec.md` (the new
canonical spec added by the consolidation change).

## Quick start

```bash
# Install
cd /Users/cianmacandeisigh/dev/kings_college_galway/tuatha/
uv sync

# Test
uv run pytest

# Lint + typecheck + openspec
ruff check
uv run mypy tuatha/
openspec validate --all --strict
```

## The 8 NCCA subject agents (per `tuatha/subjects/`)

| Subject | File | 5 tools per subject |
|:--|:--|:--|
| mathematics | `tuatha/subjects/mathematics.py` | syllabus / past_paper / marking_scheme / formative_item / response_score |
| applied_mathematics | `tuatha/subjects/applied_mathematics.py` | (same 5) |
| chemistry | `tuatha/subjects/chemistry.py` | (same 5) |
| geography | `tuatha/subjects/geography.py` | (same 5) |
| history | `tuatha/subjects/history.py` | (same 5) |
| english | `tuatha/subjects/english.py` | (same 5) |
| gaeilge | `tuatha/subjects/gaeilge.py` | (same 5 + the special `gael_gramadach_review`) |
| computer_science | `tuatha/subjects/computer_science.py` | (same 5) |

## The 3 educational agents (per `tuatha/agents/educational/`)

| Agent | File | Purpose |
|:--|:--|:--|
| `academic_history_agent` | `tuatha/agents/educational/academic_history_agent.py` | the cross-archive academic history (research paper retrieval + citation extraction) |
| `celtic_grammar_agent` | `tuatha/agents/educational/celtic_grammar_agent.py` | the Celtic grammar specialist (Irish + Welsh + Scottish Gaelic + Breton + Cornish + Manx) |
| `celtic_morphology_agent` | `tuatha/agents/educational/celtic_morphology_agent.py` | the Celtic morphology specialist (verb conjugation + noun declension + adjective agreement) |

## The 4 BIEP hackathon features (per `tuatha/agents/hackathon/`)

| Feature | File | Purpose |
|:--|:--|:--|
| `marking_grader` | `tuatha/agents/hackathon/marking_grader.py` | the Adaptive Marking Grader (student uploads answer + marking scheme → instant grade + feedback) |
| `adaptive_tutor` | `tuatha/agents/hackathon/adaptive_tutor.py` | the Adaptive Tutor Chat (stateful 6-jurisdiction syllabus tutor with persistent memory) |
| `equivalency_generator` | `tuatha/agents/hackathon/equivalency_generator.py` | the Cross-Jurisdiction Equivalency Generator (compare LC ↔ A-Level ↔ GCSE topics side-by-side) |
| `curriculum_change_sensor` | `tuatha/agents/hackathon/curriculum_change_sensor.py` | the Curriculum Change Detection Sensor (Dagster sensor that watches NCCA + AQA + SQA + WJEC + CCEA + IoM websites) |

## The 1 media_intel pipeline (per `tuatha/agents/media_intel/`)

| File | Purpose |
|:--|:--|
| `tuatha/agents/media_intel/__init__.py` | the re-export surface (TOOLS + TOOL_NAMES + all 10 tool functions + the agent + the wire) |
| `tuatha/agents/media_intel/records.py` | the `make_media_descriptor_record` helper |
| `tuatha/agents/media_intel/classifier.py` | the per-medium classifier (NEW) |
| `tuatha/agents/media_intel/explorer.py` | the per-medium + cross-medium explorer (NEW) |
| `tuatha/agents/media_intel/media_descriptor_agent.py` | the 10-tool ADK agent (moved from `agents/meaisinfhoghlaim/media_intel/`) |

The 10 ADK tools:
- 5 per-medium extractors: `extract_comic_descriptor_tool` / `extract_prose_descriptor_tool` / `extract_animation_descriptor_tool` / `extract_gameplay_descriptor_tool` / `extract_official_document_descriptor_tool`
- 5 corpus introspection: `list_sources` / `list_descriptors_by_class` / `summarise_corpus` / `compare_class_consistency` / `search_descriptors`

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new NCCA subject agent | `tuatha/subjects/<subject>.py` + `tuatha/tools/<subject>_<tool>.py` + `tuatha/baml/qpack_<subject>.baml` + `tuatha/dagster/per_subject.py` |
| Modify the 3 educational agents | `tuatha/agents/educational/<slug>_agent.py` |
| Add a new BIEP hackathon feature | `tuatha/agents/hackathon/<feature>.py` + the matching `tuatha/baml/<feature>.baml` |
| Modify the media_intel pipeline | `tuatha/agents/media_intel/<file>.py` + the matching `tuatha/baml/media_descriptor.baml` |
| Add a new BAML contract | `tuatha/baml/<name>.baml` + register in `tuatha/baml/clients.baml` |
| Add a new DLT source | `tuatha/dlt/<category>/<subject>.py` + `tuatha/dlt/<category>/<subject>/source.yaml` |
| Add a new Dagster asset | `tuatha/dagster/<file>.py` |
| Add a new marimo notebook | `tuatha/notebooks/<name>.py` |
| Add a new web app | `tuatha/web/apps/<app>/` + the matching Hono API route + the matching Convex schema |
| Add a new test | `tuatha/tests/test_<name>.py` |
| Modify the openspec spec | `openspec/specs/tuatha-british-isles-mmo/spec.md` (or its sub-specs) + re-run `mise run sync:spec-agents` |

## Key sources

- `openspec/specs/tuatha-british-isles-mmo/spec.md` — the new
  canonical spec
- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — the
  spec the new tuatha implements
- `tuatha/CONSOLIDATION_PLAN.md` — the high-level plan
- `tuatha/BUILD_PLAN.md` — the per-step execution plan
- `agents/agent_registry.py:AGENT_REGISTRY` — the registration
  for the 14 main agents + the 8 NCCA subject specialists
  (re-routed)
- `agents/meaisinfhoghlaim/media_intel/` — the back-compat shim
  for the media_descriptor_agent re-route

## Adjacent specs

- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — the
  spec the new tuatha implements
- `openspec/specs/tuatha-platform/spec.md` — the DEPRECATED
  spec (superseded by cianfhoghlaim-educational-mmo)
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the
  per-spec AGENTS.md convention
- `openspec/specs/agent-platform-cluster/spec.md` — the 8-stack
  agent cluster IaC
- `openspec/specs/agentic-frontend-frameworks/spec.md` — the
  TanStack Start + Convex + Hono + CopilotKit + AG-UI
- `openspec/specs/british-isles-education-pipeline-v3/spec.md` —
  the British Isles education pipeline (the prior pipeline the
  tuatha follows)
- `openspec/specs/british-isles-formative-assessment/spec.md` —
  the 5 curriculum frameworks + the 4 feedback channels
- `openspec/specs/centralized-model-registry/spec.md` — the
  24-entry VISION_MODELS + the 7-family MODEL_REGISTRY

## DO NOT

- **Never** add back the Pent-Elemental Cosmology + Babylon.js +
  SpacetimeDB + Crypteolas + Anam Cara + Brown Ajah theming —
  these are HARD-ARCHIVED per the consolidation change
- **Never** create a per-app `apps/<app>/apps/api/src/` for
  CopilotKit actions — they live at `tuatha/web/hono-api/src/routes/copilotkit/`
- **Never** hardcode a model string in any extractor — route
  through `MODEL_REGISTRY.resolve(family, role)`
- **Never** use a Plan B or Plan C Firecrawl tool when the
  keyless tier is active (Plan A is the default)
- **Never** commit a copyrighted comic panel image, animation
  frame still, or game screenshot to the repo (the
  `shippable: false` invariant — the descriptor is
  description-only)
- **Never** declare `shippable_default: true` without explicit
  operator override
- **Never** add a new source without a `source.yaml` manifest
- **Never** skip the `legal_notes` field in any `source.yaml`
- **Never** use "Wikipedia Foundation" as `rights_holder` — use
  the original publisher of the official document (e.g.,
  "An Garda Síochána", "Metropolitan Police Service", "Crown
  copyright")

## Skill pointers

| Skill | When to load |
|:--|:--|
| `ccc` | for semantic code search across the new tuatha/ project |
| `centralized-registry` | MODEL_REGISTRY + schema + codegen patterns |
| `british-isles-formative-assessment` | the 5 curriculum frameworks + the 4 feedback channels |
| `baml` | BAML extraction patterns + the 8-stage BAML lifecycle |
| `dlt` | DLT source patterns + the `source.yaml` manifest |
| `dagster` | the 5-layer KCG Component Architecture |
| `agent-fleet-orchestration` | the 12-agent fleet wiring + the 5-framework runtime + the LiteLLM routing keyword map |
| `dignified-python` | production Python standards |
| `motherduck` | the lakehouse / DuckDB / MotherDuck query surface |

## Cross-references

- `tuatha/CONSOLIDATION_PLAN.md` — the high-level consolidation plan
- `tuatha/BUILD_PLAN.md` — the per-step execution plan
- `../../specs/cianfhoghlaim-educational-mmo/spec.md` — the spec
  the new tuatha implements
- `../agents-sync/SKILL.md` — the Layer 10 of the knowledge-sync-loop

## Thematic guidelines

The new tuatha/ project ADOPTS the British Isles Formative
Assessment MMO theme. The 8 NCCA Leaving Certificate subjects
are the canonical content surface.

**KEEPS** (the technological choices):
- The 8 NCCA subject agents
- The 5 per-subject tools
- The 3 educational agents
- The 4 BIEP hackathon features
- The 1 media_intel pipeline
- The BAML + DLT + Dagster + CocoIndex + marimo pipeline stack
- The Hono + Convex + TanStack Start + CopilotKit web stack
- The LiteLLM + Cognee + Graphiti + LanceDB + Letta memory stack
- The educational-credential badge system

**DROPS** (the legacy theming):
- ~~Pent-Elemental Cosmology~~ (5 realms)
- ~~Babylon.js 3D~~ game front-end
- ~~SpacetimeDB v2~~ game engine backend
- ~~Crypteolas financial token~~
- ~~Anam Cara soul friend mechanic~~
- ~~Brown Ajah theming~~

The Celtic MMO design itself — which elements, what boons, the
4+1 element binding, the sub-nation mapping, the 2D particle
renderer choice, the iOS delivery vehicle — is the **downstream
theming change** gated on the corpus being populated. **NOT
in this change.**

---

**Last updated**: 2026-08-25.
**Owner**: Build agent (the new tuatha/ sub-project).
