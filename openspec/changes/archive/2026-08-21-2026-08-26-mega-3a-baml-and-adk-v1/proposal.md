# Mega-3a — BAML Modernization + ADK Agent Fleet + 4-Stage Templates + 8 NCCA Junior Cycle Subjects

## Why

The Mega-3 fast-follow (`2026-08-18-mega-3-fast-follow-v1`) shipped
the 5 integration helpers + 12 crown jewels + 6 dedup wins. This
Mega-3a change is the first of the 3 sequenced mega-changes that
build on that foundation — it lands **the 4 BAML stage templates**
(Leaving Cycle + Junior Cycle + A-Level + GCSE), **the 8 NCCA
Junior Cycle subjects at full scope**, and the **BAML 0.223.0
feature adoption** (spawn, host callables, catch, render_null_as,
multimodal, intersection bounds).

The current state has:
- **491 BAML stub prompts** (`"Auto-generated extraction prompt."`) across 272 files
- **8 hand-written `qpack_*.baml` files** (~2,670 LOC) duplicating the same pattern
- **6 hand-written `lc_extraction/*.baml` files** (~1,287 LOC) with `{% if subject == "x" %}` repeated
- **8 hand-written `junior_cycle/*.baml` files** (~518 LOC) duplicating per-subject logic
- **21 hand-written ADK agents** (~7,816 LOC) with ~80 hand-written Pydantic classes + 18 hand-written `FunctionTool` wrappers
- **No use of `spawn` / `host.callable` / `catch` / `render_null_as`** (all BAML 0.223.0 features)

The total duplication is **~14,200 LOC** in this change scope. The
planned additions are **~4,500 LOC** (the 4 stage templates + 8 JC
subjects + BAML feature adoption).

**Net result: -9,700 LOC** while adding the 4-stage plane, the 8 NCCA
Junior Cycle subjects, and BAML 0.223.0 feature adoption.

## What changes — The 4 Stage Templates + 8 NCCA Junior Cycle

### The 4 stage BAML templates (one per stage, parameterised by subject)

| Stage | Template file | Replaces | Subjects |
|:--|:--|:--|:--|
| **Leaving Cycle** | `baml_src/british_isles/_shared/lc_extraction_template.baml` (~250 LOC) | 6 `lc_extraction/*.baml` files (1,287 LOC) | 14 LC × EN + GA |
| **Junior Cycle** | `baml_src/british_isles/_shared/junior_cycle_template.baml` (~200 LOC) | 6 `junior_cycle/*.baml` files (518 LOC) | 8 JC × EN + GA |
| **A-Level** | `baml_src/british_isles/_shared/alevel_extraction_template.baml` (~250 LOC) | 15 A-Level files | 15 × 3 boards × EN |
| **GCSE** | `baml_src/british_isles/_shared/gcse_extraction_template.baml` (~250 LOC) | 9 GCSE files | 9 × 3 boards × EN |
| **qpack (cross-stage)** | `baml_src/british_isles/_shared/qpack_template.baml` (~250 LOC) | 8 `qpack_*.baml` files (2,670 LOC) | All 4 stages |

### The 8 NCCA Junior Cycle subjects at full scope

| # | Subject | NCCA code |
|:--|:--|:--|
| 1 | Mathematics | `JC-MATH` |
| 2 | English | `JC-ENGL` |
| 3 | Gaeilge | `JC-GAEL` |
| 4 | Science | `JC-SCI` |
| 5 | Geography | `JC-GEOG` |
| 6 | History | `JC-HIST` |
| 7 | CSPE | `JC-CSPE` |
| 8 | SPHE | `JC-SPHE` |

Each subject gets:
- 1 BAML function in the Junior Cycle template (per-subject `{% if %}` block)
- 1 CocoIndex App (via the `ireland_jc_factory.py` from Mega-3b)
- 1 ADK agent (`jc_subject_agent`)
- 1 A2UI surface (for the CopilotKit UI from Mega-3b)

### BAML 0.223.0 feature adoption

| Feature | Use in this change | Sub-tasks |
|:--|:--|:--|
| `spawn` + `await` (BEP-034) | The 4-path OCR ensemble (`ensembled_extraction.baml`) | A.1 |
| `host.callable` (BEP-3571) | `run_lct6_query` for the marimo lineage viewer | A.6 |
| `catch` / `catch_all` | Every `Extract*` function in the 6 LC extractors | A.3 |
| `render_null_as` | `-1` for missing `source_pages`, `year`, `total_marks` | A.4 |
| Intersection bounds `T extends A & B` | The `Document + Bilingual + HasMetadata` types | A.5 |
| `image` / `pdf` multimodal | The 6-stage PDF pipeline (Stages 1-3) | A.7 |
| `@assert` BAML test blocks | The 8 NCCA Junior Cycle qpack generators | A.8 |

## How changes — Phasing & Dedup Wins

### Phase 1: BAML 0.223.0 feature adoption (Week 1)
- A.1 spawn/await for the 4-path OCR ensemble
- A.2 concurrent function calls (race qwen3-vl-8b vs gemma-4)
- A.3 catch/catch_all for the 6 LC extractors
- A.4 render_null_as for the affected fields
- E.1-E.5 5 new lint gates

### Phase 2: 4 stage BAML templates (Weeks 2-4)
- B.1 BAML 14-LC-subject prompt template (the foundation)
- B.2 8 NCCA Junior Cycle subjects (extends B.1)
- B.3 15 A-Level subjects (extends B.1)
- B.4 9 GCSE subjects (extends B.1)
- B.5 qpack_template.baml — collapses the 8 qpack_*.baml files
- B.6 lc_extraction_template.baml — collapses the 6 lc_extraction/*.baml files

### Phase 3: Test coverage (Week 5)
- C.1-C.5 test blocks for the 5 canonical lc6 functions + the 4 stage templates

### Phase 4: Advanced BAML features (Week 6)
- A.5 intersection bounds
- A.6 host callables for `run_lct6_query`
- A.7 multimodal `image`/`pdf` inputs
- A.8 `@assert` test blocks

### Phase 5: Integration touchpoints (Weeks 7-8)
- D.1-D.9 wire BAML into CocoIndex, Dagster, marimo, Dives, TS, SSE, Collector, 12 agents

### Phase 6: Tooling + observability (Weeks 9-10)
- E.6-E.8 + F.1-F.5 RAGAS + Snapshot + template versioning + MLflow

## Version Pins

- `baml-py>=0.223.0,<0.224.0` (already pinned in `mise.toml`)
- `google-adk>=1.10.0` (for SequentialAgent, ParallelAgent, BuiltInPlanner, LongRunningFunctionTool)

## Spec Deltas (42 ADDED across 13 specs)

| Spec | ADDED | Source |
|:--|:--|:--|
| `baml-schemas` | 7 | A.1-A.8 + C.1-C.5 + the 4 stage templates |
| `british-isles-education-pipeline-v3` | 6 | B.1-B.6 + the 8 JC subjects |
| `centralized-schema-registry` | 2 | A.4 + the qpack codegen invariant |
| `centralized-registry` | 1 | The 4-stage plane extension (from the roadmap) |
| `dagster-5-layer-component-architecture` | 2 | A.3 + D.2 (the BAML extraction → Dagster asset chain) |
| `oideachais-pipeline` | 2 | A.7 (the 6-stage PDF pipeline → BAML multimodal) |
| `oideachais-university-deep-extraction` | 1 | A.6 (the `run_lct6_query` host callable) |
| `agent-observability` | 2 | F.1 + F.5 (BAML Collector + MLflow) |
| `agent-fleet-orchestration` | 2 | D.9 (12 ADK agents → BAML `image` outputs) |
| `agentic-frontend-frameworks` | 1 | D.7 (SSE streaming for the lineage viewer) |
| `knowledge-sync-loop` | 2 | E.6-E.8 (the baml sync layer) |
| `agent-platform-cluster` | 3 | ADK.1 + ADK.11 + ADK.15 |
| `meaisinfhoghlaim-agent-frameworks` | 5 | ADK.5 + ADK.6 + ADK.13 + the 8 NCCA JC + the 4 stage agents |
| **TOTAL** | **36 ADDED** | 13 specs |

## Pre-Validation Checklist

- [ ] `mise run baml:generate` regenerates clean
- [ ] `mise run cocoindex:conformance` passes (47 → 99 R1-R4 compliant Apps)
- [ ] `mise run lint:skills` passes (10 + 5 = 15 lint gates)
- [ ] `openspec validate 2026-08-26-mega-3a-baml-and-adk-v1 --strict`
- [ ] `mise run turbo build` passes
- [ ] Net LOC reduction report shows -9,700 LOC savings
- [ ] All 19/19 existing tests still pass + new ones added
- [ ] No conflict with `2026-08-18-mega-3-fast-follow-v1` (the 10 ADDED)
- [ ] No conflict with `2026-08-18-mega-3-roadmap-v1` (the 1 ADDED)

## Cross-References

- Roadmap: `openspec/changes/2026-08-18-mega-3-roadmap-v1/proposal.md`
- Predecessor: `openspec/changes/2026-08-18-mega-3-fast-follow-v1/proposal.md`
- Successor: `openspec/changes/2026-09-30-mega-3b-cocoindex-and-copilotkit-v1/proposal.md` (next)
- Pre-archived predecessors: `2026-08-17-biep-v3-bring-up-v1` (7 spec deltas) + `2026-08-17-hygiene-drift-cleanup-v1` (6 spec deltas)