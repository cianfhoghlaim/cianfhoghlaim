# Mega-3b — CocoIndex Modernization + CopilotKit UI + 4 Stage Factories + european_nations Factory v2

## Why

Mega-3a (`2026-08-26-mega-3a-baml-and-adk-v1`) shipped the 5 BAML
stage templates + the 4 stage ADK agents + the `BAMLFunctionTool`
helper. This Mega-3b change builds the matching **CocoIndex factory
plane** and the **CopilotKit UI plane** on top of those foundations:

- The 4 stage CocoIndex factories (LC + JC + A-Level + GCSE)
- The `european_nations/_factory.py` v2 (collapses 40 country files)
- The CocoIndex → BAML wiring (FF.6 from fast-follow)
- The CopilotKit pin migration (CK.1 — `cianfhoghlaim-mmo` v1.10 → v2.0)
- The 8 A2UI surfaces (CK.2-CK.12 — share 1 generator)

The current state has:
- **94 explicit `coco.App`** + **378 factory-generated Apps** (24K LOC across 190 .py files)
- **40 hand-written `european_nations/<country>/education_embedding.py`** files (~3,000 LOC)
- **`cianfhoghlaim-mmo` still on `@copilotkit/react-core@^1.10.0`** (the v2.0 pin drift)
- **4 hand-written web components** in `web/apps/cianfhoghlaim/components/`
- **8 A2UI surfaces to build** (chart, graph, playback, lineage, search, etc.)

The total duplication is **~10,000 LOC** in this change scope. The
planned additions are **~5,000 LOC** (the 4 stage factories + the
european_nations factory v2 + A2UI generator + CopilotKit migration).

**Net result: -5,000 LOC** while adding the CocoIndex plane + the
CopilotKit UI plane + 31 ADDED spec requirements across 13 specs.

## What changes — The 4 Stage CocoIndex Factories + european_nations Factory v2 + CopilotKit

### The 4 stage CocoIndex factories (one per stage, parallel to the 4 BAML templates)

| Stage | CocoIndex factory | Apps | Source |
|:--|:--|:--|:--|
| **Leaving Cycle** | `cocoindex_flows/biep_parity/ireland_lc_factory.py` (exists, 176 LOC) | 11 (6 subjects × 2 langs minus 1) | Existing — wire BAML |
| **Junior Cycle** | `cocoindex_flows/biep_parity/ireland_jc_factory.py` (new, ~300 LOC) | 16 (8 subjects × 2 langs) | This change |
| **A-Level** | `cocoindex_flows/biep_parity/england_alevel_factory.py` (new, ~400 LOC) | 45 (15 × 3 boards) | This change |
| **GCSE** | `cocoindex_flows/biep_parity/england_gcse_factory.py` (new, ~300 LOC) | 27 (9 × 3 boards) | This change |
| **Cross-stage qpack** | Already covered by the LC factory + the 4 above | — | — |

The existing `4_stage_factory.py` (394 LOC) and
`england_priority_factory.py` (222 LOC) will be the starting points
for the new factories.

### The european_nations factory v2

Collapses the 40 hand-written country files into 1 factory:

| Before | After |
|:--|:--|
| `cocoindex_flows/european_nations/{albania,austria,...}/education_embedding.py` (40 files, ~3,000 LOC) | `cocoindex_flows/european_nations/_factory.py` (1 file, ~500 LOC) |

The factory consumes the 40-country config table + generates 40
CocoIndex Apps.

### The CocoIndex → BAML wiring (FF.6 from fast-follow)

Every CocoIndex App calls at least 1 BAML function via `BAMLFunctionTool`.
The 47 BIEP CocoIndex Apps at `cocoindex_flows/biep_parity/*.py` get wired
to the 5 lc6 BAML functions from `lc_extraction_template.baml`.

### The CopilotKit pin migration (CK.1)

| Web app | Before | After |
|:--|:--|:--|
| `web/apps/cianfhoghlaim` | `@copilotkit/react-core/v2 ^1.0.0` ✓ | unchanged |
| `web/apps/cianfhoghlaim-mmo` | `@copilotkit/react-core ^1.10.0` ❌ | `@copilotkit/react-core/v2 ^1.67.1` ✓ |

### The 8 A2UI surfaces (CK.2-CK.12 — share 1 generator)

| Surface | Agent | Use case |
|:--|:--|:--|
| Chart | `statistics_agent` | Real-time BIEP stats |
| Graph | `corpus_agent` | Knowledge graph view |
| Playback | `research_agent` | Time-based playback |
| Lineage | `curriculum_agent` | Per-page PDF.js lineage |
| Search | `mcp_curriculum_agent` | Curriculum search |
| Subject grid | `root_agent` | 8 NCCA JC subjects |
| Dashboard | `curriculum_comparison_agent` | Cross-jurisdiction comparison |
| Translator | `translation_agent` | EN ↔ GA translation |

All 8 share 1 generator at
`web/apps/cianfhoghlaim/components/_shared/A2UISurfaceGenerator.tsx`.

## How changes — Phasing & Dedup Wins

### Phase 1: CocoIndex BAML wiring (Week 1)
- Wire BAML → CocoIndex for the 47 BIEP Apps (FF.6)
- Add `baml-py.Pdf.from_base64` direct input (FF.12)

### Phase 2: 4 stage CocoIndex factories (Weeks 2-4)
- Junior Cycle factory (new)
- A-Level factory (new)
- GCSE factory (new)
- LC factory (existing — wire BAML)

### Phase 3: european_nations factory v2 (Week 5)
- Collapse 40 country files → 1 factory
- Generate 40 CocoIndex Apps

### Phase 4: CopilotKit pin migration (Week 6)
- Bump `cianfhoghlaim-mmo` to v2.0
- Wire 12 ADK agents as `CopilotRuntime.agents`

### Phase 5: A2UI surfaces (Weeks 7-8)
- 1 generator + 8 thin surface files

### Phase 6: Tooling + observability (Weeks 9-10)
- 3 more CocoIndex + CopilotKit lint gates
- RAGAS + Snapshot

## Version Pins

- `cocoindex>=1.0.20` (already pinned)
- `@copilotkit/react-core/v2>=1.67.1` (new pin for `cianfhoghlaim-mmo`)

## Spec Deltas (31 ADDED across 13 specs)

| Spec | ADDED | Source |
|:--|:--|:--|
| `centralized-schema-registry` | 3 | CocoIndex → BAML wiring + 4 stage factory codegen + qpack invariant |
| `british-isles-education-pipeline-v3` | 4 | 4 stage factories + 8 NCCA JC + SSE + BAML lifecycle |
| `agent-platform-cluster` | 3 | A2UI surfaces + agent_ui_bridge + 12 ADK agents |
| `agentic-frontend-frameworks` | 5 | CK.1-5 + A2UI generator + marimo_to_copilotkit |
| `agent-fleet-orchestration` | 2 | CK.13 (A2A) + CK.20 (ag-ui-adk) |
| `agent-observability` | 1 | CK.9 (CopilotKit middleware) |
| `meaisinfhoghlaim-agent-frameworks` | 1 | CK.6 (orchestrator) |
| `indexing-and-cognition` | 2 | CocoIndex query API + entity resolution |
| `centralized-model-registry` | 1 | CopilotKit model routing |
| `dagster-5-layer-component-architecture` | 1 | CocoIndex → Dagster |
| `oideachais-marimo-dashboards` | 1 | Marimo → CopilotKit surface |
| `baml-schemas` | 4 | CocoIndex → BAML contract |
| `knowledge-sync-loop` | 3 | sync:cocoindex + drift detector |
| **TOTAL** | **31** | |

## Pre-Validation Checklist

- [ ] `mise run baml:generate` regenerates clean
- [ ] `mise run cocoindex:conformance` passes (47 R1-R4 compliant + 4 stage factories)
- [ ] `mise run lint:skills` passes (13 + 3 = 16 lint gates)
- [ ] `openspec validate 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 --strict`
- [ ] `mise run turbo build` passes
- [ ] Net LOC reduction report shows -5,000 LOC savings
- [ ] All 19/19 existing tests still pass + new ones added
- [ ] No conflict with the 3 Mega-3 predecessors (roadmap + fast-follow + Mega-3a)

## Cross-References

- Roadmap: `openspec/changes/2026-08-18-mega-3-roadmap-v1/proposal.md`
- Predecessor: `openspec/changes/2026-08-26-mega-3a-baml-and-adk-v1/proposal.md`
- Successor: `openspec/changes/2026-11-25-mega-3c-marimo-and-integration-v1/proposal.md` (next)
- Foundation: `agents/integrations/baml_function_tool.py` (BAMLFunctionTool helper)
- Foundation: `baml_src/british_isles/_shared/*.baml` (5 stage templates)