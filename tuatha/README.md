# The British Isles Formative Assessment MMO

> **The canonical implementation of the**
> **[`cianfhoghlaim-educational-mmo`](../../openspec/specs/cianfhoghlaim-educational-mmo/spec.md)**
> **spec.** A self-contained independent sub-project at
> `/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/`
> (the new top-level `tuatha/` dir; will become the independent
> GitHub repo at `github.com/cianmacandeisigh/tuatha.git`).

---

## What is this?

**Tuatha** is the **British Isles Formative Assessment MMO** — an
educational MMO that delivers **continuous formative feedback
(not summative)** during quests, mapped to the
**NCCA / CfE / CfW / CCEA / SQA / DESC** curriculum frameworks.

The 8 NCCA Leaving Certificate subjects are the canonical content
surface:

- **mathematics**
- **applied_mathematics**
- **chemistry**
- **geography**
- **history**
- **english**
- **gaeilge** (taught in Irish; some content also in English)
- **computer_science**

The 3 educational agents form the academic + Celtic-language
specialty layer on top of the 8 NCCA subjects:

- `academic_history_agent` — the cross-subject + cross-jurisdiction
  history research agent
- `celtic_grammar_agent` — the Irish grammar specialist
- `celtic_morphology_agent` — the Celtic morphology specialist

The 4 BIEP hackathon features (from the
`2026-08-21-biiep-hackathon-agentic-educational-system-v1/`
change) form the agentic features:

- `marking_grader` — the Adaptive Marking Grader
- `adaptive_tutor` — the Adaptive Tutor Chat
- `equivalency_generator` — the Cross-Jurisdiction Equivalency
  Generator
- `curriculum_change_sensor` — the Curriculum Change Detection
  Sensor

The 1 media_intel pipeline (from the
`2026-08-23-tuatha-media-intel-gameplay-capture-research-v1/`
change) provides the 5-class source registry + the 7-axis
`MediaDescriptor` schema + the 10-tool ADK agent.

---

## Quick start

```bash
# Install (uv-managed workspace)
cd /Users/cianmacandeisigh/dev/kings_college_galway/tuatha/
uv sync

# Run the test suite
uv run pytest

# Run a single subject agent
uv run python -c "
import asyncio
from tuatha.subjects.mathematics import math_agent
async def main():
    response = await math_agent.run('What is the NCCA LC Higher Level syllabus on complex numbers?')
    print(response)
asyncio.run(main())
"

# Run the 6 quality gates
openspec validate --all --strict
mise run lint:registry
ruff check
```

---

## The 6 quality gates

```bash
# G1: openspec validate --strict (this project's change)
openspec validate $(grep -oP "2026-08-25-tuatha-british-isles-mmo-consolidation-v1" openspec/changes/*/proposal.md 2>/dev/null | head -1) --strict

# G2: openspec validate --all --strict (the full platform)
openspec validate --all --strict

# G3: mise run lint:registry (0 hardcoded model strings)
mise run lint:registry

# G4: ruff check (Python linting)
ruff check

# G5: mypy (Python typechecking)
uv run mypy tuatha/

# G6: Python import (no circular import)
uv run python -c "
from tuatha import (
    math_agent, appm_agent, chem_agent, comp_agent,
    engl_agent, gael_agent, geog_agent, hist_agent,
    academic_history_agent, celtic_grammar_agent, celtic_morphology_agent,
    marking_grader_agent, adaptive_tutor_agent, equivalency_generator_agent, curriculum_change_sensor_agent,
    media_descriptor_agent,
    TuathaOrchestrator, CianfhoghlaimOperator,
)
print('G6 PASS')
"
```

---

## The 8 NCCA subject agents

Each subject has a dedicated ADK agent in `tuatha/subjects/`:

- `tuatha/subjects/mathematics.py` — the Mathematics agent
- `tuatha/subjects/applied_mathematics.py` — the Applied Mathematics agent
- `tuatha/subjects/chemistry.py` — the Chemistry agent
- `tuatha/subjects/geography.py` — the Geography agent
- `tuatha/subjects/history.py` — the History agent
- `tuatha/subjects/english.py` — the English agent
- `tuatha/subjects/gaeilge.py` — the Gaeilge agent (the bilingual EN/GA surface)
- `tuatha/subjects/computer_science.py` — the Computer Science agent

Each subject has 5 per-subject tools in `tuatha/tools/`:

- `<subject>_syllabus_lookup.py`
- `<subject>_past_paper_lookup.py`
- `<subject>_marking_scheme_lookup.py`
- `<subject>_formative_item_generate.py`
- `<subject>_response_score.py`

---

## The 3 educational agents

- `tuatha/agents/educational/academic_history_agent.py`
- `tuatha/agents/educational/celtic_grammar_agent.py`
- `tuatha/agents/educational/celtic_morphology_agent.py`

---

## The 4 BIEP hackathon features

- `tuatha/agents/hackathon/marking_grader.py`
- `tuatha/agents/hackathon/adaptive_tutor.py`
- `tuatha/agents/hackathon/equivalency_generator.py`
- `tuatha/agents/hackathon/curriculum_change_sensor.py`

---

## The 1 media_intel pipeline

- `tuatha/agents/media_intel/{__init__,records,classifier,explorer,media_descriptor_agent}.py`

The 10-tool ADK `media_descriptor_agent` orchestrates the 5
per-medium BAML extractor functions (comic / prose / animation /
gameplay / official_document) + the 5 corpus introspection
tools (list_sources / list_descriptors_by_class /
summarise_corpus / compare_class_consistency /
search_descriptors).

The 5-class source registry:
- **A — Comics**: the Jonathan Hickman Marvel run
- **B — Prose**: The Wheel of Time (the 0-pixel control)
- **C — Animation**: Avatar: The Last Airbender + The Legend of
  Korra + the Aang-film continuity
- **D — Games**: Hades 1 + 2 + World of Warcraft + Golden Sun +
  Pokémon
- **E — Official**: 36 official records across 3 government
  sub-buckets (UK + Éire + Crown Dependencies) + the 4 BIEP
  hackathon features

The 9 Celtic-history stub sources (gated for the downstream
theming change):
- Tuatha Dé Danann + Irish mythology + Celtic mythology +
  Celtic law + Brehon law + Aran Islands + Isle of Skye +
  Isle of Man + Dyfed

---

## The tech stack

| Layer | Tech | Surface |
|:--|:--|:--|
| Local LLM | LiteLLM gateway + minimax-m3 (the canonical 7-tier fallback) | `tuatha/config.py` |
| OCR / VLM | qwen3-vl-8b + gemma-4-26B-A4B + molmo2-8b + olmocr-2-7B | the 5 per-medium extractors |
| Agent fleet | Google ADK (the 12-agent fleet pattern) | `tuatha/agents/` |
| BAML extraction | BAML 0.210 | `tuatha/baml/` |
| Memory stack | Cognee + Graphiti + LanceDB + Letta | `tuatha/config.py` + `tuatha/agents/educational/` |
| Pipeline stack | DLT + Dagster + CocoIndex | `tuatha/dlt/`, `tuatha/dagster/`, `tuatha/cocoindex/` |
| Web stack | TanStack Start + Convex + Hono + CopilotKit | `tuatha/web/` |
| Observability | Langfuse + MLflow + RAGAS + Logfire + structlog | `tuatha/observability/` |
| Credentials | The badges system (replaces the legacy Crypteolas financial token) | `tuatha/badges/` |
| CI | GitHub Actions + Dagger | `.github/workflows/ci.yml` + `tuatha/ci/` |

---

## The themes this project DROPS (the legacy theming)

| Dropped theme | Why |
|:--|:--|
| ~~Pent-Elemental Cosmology~~ (5 realms: Spirit / Water / Fire / Earth / Air) | The cianfhoghlaim-educational-mmo spec says this design "did not land" |
| ~~Babylon.js 3D~~ game front-end | Replaced with the TanStack Start 2D client |
| ~~SpacetimeDB v2~~ game engine backend | Replaced with Convex + Hono + Dagster + DuckLake |
| ~~Crypteolas financial token~~ | Replaced with the educational-credential badge system |
| ~~Anam Cara~~ soul friend mechanic | Replaced with the 4 BIEP hackathon features |
| ~~Brown Ajah~~ theming | The 8 NCCA subject ↔ Tuatha Dé deity mapping is preserved as `tuatha/subjects/character.py` but the "Brown Ajah" name is dropped |

The archive of these references lives at `tuatha/old/`
(per the consolidation change).

---

## The Celtic MMO design itself is NOT in this change

The Celtic MMO design — which elements to use, what the boons
look like, the 4+1 element binding, the sub-nation mapping
(Wales+England combined, etc.), the anam currency, the
anamcara NFT familiar mechanic, the 2D particle renderer
choice, the iOS delivery vehicle — is a **downstream theming
change** gated on this corpus being populated.

The 7-axis `MediaDescriptor` schema is what feeds that future
design. Until the corpus is populated, the design has no
factual basis.

---

## The package layout

```
tuatha/
├── README.md                          # this file
├── AGENTS.md                          # the routing doc (developer quick-reference)
├── DEVELOPMENT.md                     # the how-to-add-an-agent doc
├── pyproject.toml                     # the package meta (uv-managed)
├── mise.toml                          # the mise task namespace
├── LICENSE                            # MIT
├── docker-compose.yml                 # the local-dev stack
├── docs/                              # the 4 canonical docs
├── tests/                             # the 4 test files
├── openspec/                          # the project-local openspec
├── .devcontainer/
├── .github/workflows/ci.yml
├── .gitignore
├── .dockerignore
├── tuatha/                            # the canonical Python sub-namespace
│   ├── __init__.py                    # the re-export surface
│   ├── config.py                       # LiteLLM + Langfuse + Cognee + Letta + BAML clients
│   ├── routing.py                      # the SubjectAgentWiring factory
│   ├── orchestrator.py                 # the TuathaOrchestrator
│   ├── operator.py                     # the CianfhoghlaimOperator
│   ├── cross_subject.py                # the cross-subject specialist
│   ├── workflows.py                    # the 4 per-subject workflow handlers
│   ├── callbacks/                      # the canonical callbacks
│   ├── mcp_server/                     # the MCP server
│   ├── subjects/                       # the 8 NCCA subject agents
│   ├── tools/                          # the 40 per-subject tools
│   ├── agents/
│   │   ├── educational/                # the 3 educational agents
│   │   ├── media_intel/                # the 10-tool ADK agent
│   │   └── hackathon/                   # the 4 BIEP hackathon features
│   ├── baml/                           # the BAML surface
│   ├── dlt/                            # the DLT sources
│   ├── dagster/                        # the Dagster asset groups
│   ├── cocoindex/                      # the CocoIndex v1 Apps
│   ├── notebooks/                      # the marimo notebooks
│   ├── badges/                         # the credential system
│   └── ci/                             # the CI layer
└── tuatha/old/                         # the archive
    ├── prior_top_level_tuasha/         # (preserved for reference)
    ├── scattered_agents_tuasha/        # (preserved for reference)
    └── legacy_theming/                 # the hard-archived legacy theming
```

---

## The cross-repo surface

The `tuatha/` project lives at
`/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/` —
a sub-dir of the parent `kings_college_galway/` (the cianfhoghlaim
+ leabharlann + bonneagar monorepo). The new project is designed
to become its own independent GitHub repo at
`github.com/cianmacandeisigh/tuatha.git` (per the 2026-08-25
consolidation change).

The cross-repo references are:
- `agents/agent_registry.py:AGENT_REGISTRY` — the
  `media_descriptor_agent` entry's `module_path` is
  `tuatha.agents.media_intel.media_descriptor_agent` (re-routed
  from the prior `agents.meaisinfhoghlaim.media_intel.*` location)
- The back-compat shim at
  `agents/meaisinfhoghlaim/media_intel/__init__.py` re-exports
  the canonical symbols from the new location
- The sibling repos `kings_college_galway/leabharlann/` +
  `kings_college_galway/bonneagar/` are unchanged

---

## License

MIT (permissive).

```
MIT License

Copyright (c) 2026 Cian Mac an Déisigh Uí Liatháin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

**Last updated**: 2026-08-25.
**Owner**: Build agent (the new tuatha/ sub-project).
