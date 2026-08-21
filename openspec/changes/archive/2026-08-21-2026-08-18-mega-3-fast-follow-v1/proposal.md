# Mega-3 Fast-Follow — The 5 Integration Helpers + 12 Crown Jewels + 6 Dedup Wins

## Why

The Mega-3 roadmap (`openspec/changes/2026-08-18-mega-3-roadmap-v1`)
identifies that the 5 canonical packages (BAML + CocoIndex + Google ADK
+ CopilotKit + Marimo) need **5 integration helpers** to bridge them,
**12 crown jewels** to wire the highest-impact paths, and **6 dedup
wins** to remove redundancy before the 3 sequenced mega-changes land.

The current state has **~25,000 LOC of duplication** that the 4-stage
plane architecture addresses. This change captures the foundation:
the 5 helpers, the 12 wires, and the 6 dedup wins that the 3
mega-changes build on.

## What changes — The 18 Sub-tasks

### The 5 Integration Helpers

| # | Helper | LOC | Dedup win |
|:--|:--|:--|:--|
| FF.1 | `agents/integrations/baml_function_tool.py` — wraps any BAML `async def` as a `FunctionTool` | ~200 | -1,200 LOC |
| FF.2 | `notebooks/_shared/marimo_baml.py` — exposes `b.Extract*` as `mo.ui.chat` + `mo.ai.llm` | ~200 | -400 LOC |
| FF.3 | `agents/integrations/agent_ui_bridge.py` — full port of `ag-ui-adk.ADKAgent` + `CopilotKitRuntime` | ~300 | -150 LOC |
| FF.4 | `notebooks/_shared/marimo_to_copilotkit.py` — mounts every notebook as a CopilotKit tool | ~200 | -300 LOC |
| FF.5 | `cocoindex_flows/_shared/cocoindex_query_api.py` — every CocoIndex App exposes a `search()` closure | ~250 | -800 LOC |

### The 12 Crown Jewels (the highest-impact wires)

| # | Wire | Replaces |
|:--|:--|:--|
| FF.6 | Wire 5 lc6 BAML functions into the 47 BIEP CocoIndex Apps | Direct LLM calls in CocoIndex |
| FF.7 | Wire 12 ADK agents as `CopilotRuntime.agents = { ... }` | Manual AG-UI bridges |
| FF.8 | Adopt A2UI Protocol for 12 ADK agents | Hand-written React components |
| FF.9 | Wire 6 LC-subject BAML functions as `curriculum_agent`'s tools | Hand-written `FunctionTool` wrappers |
| FF.10 | Build `notebooks/00_baml_tour.py` — the educative tour | No BAML tour exists today |
| FF.11 | Wire 4-path OCR ensemble BAML function into `ensembled_extraction` CocoIndex App | Sequential Python orchestration |
| FF.12 | Adopt `baml_py.Pdf.from_base64` direct input in 47 CocoIndex Apps | Embed→string→BAML handoff |

### The 6 Dedup Wins

| # | Dedup | LOC saved |
|:--|:--|:--|
| FF.13 | `cocoindex_flows/subjects/_factory.py` — collapse 4 hand-written files | -504 LOC |
| FF.14 | Delete 13 `cocoindex_flows/biep_parity/*_education_embedding.py` shims | -169 LOC |
| FF.15 | Defer to Mega-3b: `european_nations/_factory.py` v2 (40 files → 1) | -2,500 LOC (lands in Mega-3b) |
| FF.16 | `baml_src/british_isles/_shared/qpack_template.baml` — collapse 8 `qpack_*.baml` files | -1,670 LOC |
| FF.17 | Delete 13 `_legacy/grading/*.baml` files | -350 LOC |
| FF.18 | `web/apps/cianfhoghlaim/components/_shared/FetchPanel.tsx` — collapse 4 component patterns | -300 LOC |

## How changes — Sequencing & Dependencies

The 18 sub-tasks split into 5 dependency-ordered phases:

| Phase | Sub-tasks | Effort |
|:--|:--|:--|
| **Phase A: Build helpers** | FF.1, FF.2, FF.3, FF.4, FF.5 | 1 week |
| **Phase B: Wire helpers** | FF.6, FF.7, FF.9, FF.11, FF.12 | 3 days |
| **Phase C: Dedup wins** | FF.13, FF.14, FF.16, FF.17, FF.18 | 2 days |
| **Phase D: Surface adoption** | FF.8 (A2UI) | 1 day |
| **Phase E: Education tour** | FF.10 (baml_tour) | 1 day |

The total effort is ~2 weeks. All 18 sub-tasks land in this single
change to keep the validation gate atomic.

## Version Pins

This change lands behind:

- `baml-py>=0.223.0,<0.224.0` (already pinned in `mise.toml`)
- `google-adk>=1.10.0` (for `SequentialAgent`, `ParallelAgent`, `LongRunningFunctionTool`, `BuiltInPlanner`)
- `cocoindex>=1.0.20` (already pinned in `pyproject.toml`)
- `@copilotkit/react-core/v2>=1.67.1` (per the `2026-08-17-biep-v3-bring-up-v1` change)
- `marimo>=0.14.10` (for `mo.ui.chat` streaming, `mo.ui.anywidget`)

## Spec Deltas (10 ADDED across 7 specs)

| Spec | ADDED | Source |
|:--|:--|:--|
| `agent-platform-cluster` | 2 | FF.1 (BAMLFunctionTool) + FF.3 (agent_ui_bridge) |
| `agent-fleet-orchestration` | 1 | FF.7 (12 ADK agents as CopilotKit) |
| `agentic-frontend-frameworks` | 2 | FF.4 (marimo_to_copilotkit) + FF.8 (A2UI Protocol) |
| `baml-schemas` | 1 | FF.6 (BAML→CocoIndex) + FF.9 (BAML→ADK) |
| `centralized-schema-registry` | 1 | FF.6 (BAML→CocoIndex codegen invariant) |
| `british-isles-education-pipeline-v3` | 2 | FF.11 (4-path OCR BAML→CocoIndex) + FF.10 (baml_tour) |
| `centralized-model-registry` | 1 | FF.5 (cocoindex_query_api) |
| **TOTAL** | **10 ADDED** | 7 specs |

## Pre-Validation Checklist

- [ ] `mise run baml:generate` regenerates clean
- [ ] `mise run cocoindex:conformance` passes (47 R1-R4 Apps still valid)
- [ ] `mise run lint:skills` passes (10 existing + 0 new gates in this change)
- [ ] `openspec validate 2026-08-18-mega-3-fast-follow-v1 --strict`
- [ ] `mise run turbo build` passes
- [ ] Net LOC reduction report (`dedup-report.md`) shows -8,833 LOC savings
- [ ] All 19/19 existing tests still pass + new ones added
- [ ] No conflict with the just-archived `2026-08-17-biep-v3-bring-up-v1` (the 7 spec deltas)
- [ ] No conflict with the just-archived `2026-08-17-hygiene-drift-cleanup-v1` (the 6 spec deltas)

## Cross-References

- Roadmap: `openspec/changes/2026-08-18-mega-3-roadmap-v1/proposal.md`
- This change is Step 1 of 5 in the Mega-3 rollout
- After this change, Mega-3a (BAML + ADK + 4 stage templates) can start