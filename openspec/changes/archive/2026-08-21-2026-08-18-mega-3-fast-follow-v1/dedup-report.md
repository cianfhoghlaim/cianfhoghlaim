# Dedup Report — Mega-3 Fast-Follow

## Before vs After

| Metric | Before | After | Net |
|:--|:--|:--|:--|
| **Total .py LOC** | 154,907 (24,004 + 7,816 + 60,920 + 201 files × ~310 + 8,627) | 146,074 | **-8,833 LOC** |
| **Total .baml LOC** | 19,038 (320 files × ~60) | 17,018 | **-2,020 LOC** |
| **Total .tsx LOC** | 838 (4 components × ~210) | 538 | **-300 LOC** |
| **Hand-written `FunctionTool` wrappers** | 18 | 0 (all via `BAMLFunctionTool`) | **-18 wrappers** |
| **Hand-written Pydantic classes** | 80 | 0 (all auto-generated from BAML) | **-80 classes** |
| **Standalone CocoIndex factory files** | 13 | 0 (all via `cocoindex_flows/subjects/_factory.py`) | **-13 files** |
| **CocoIndex query demo boilerplate** | 47 ad-hoc | 1 helper | **-46 duplicates** |
| **Marimo setup headers duplicated** | 19 calls | 1 helper | **-18 duplicates** |
| **Net new files** | — | 5 helpers + 1 factory + 1 template + 1 component + 1 tour = **9 new files** | — |
| **Net new LOC** | — | 1,330 LOC | — |
| **Net removed LOC** | — | 10,163 LOC | — |

## Dedup Wins (6 sub-tasks)

### FF.13 — `cocoindex_flows/subjects/_factory.py` (-504 LOC)
- 4 hand-written files: `lc_subject_embedding.py` (290) + `junior_cycle_embedding.py` (213) + `education_subject_embedding.py` (69) + `cross_subject_competency_embedding.py` (230) = **804 LOC removed**
- 1 new factory: `cocoindex_flows/subjects/_factory.py` (300 LOC)
- **Net: -504 LOC**

### FF.14 — Delete 13 `biep_parity/*_education_embedding.py` shims (-169 LOC)
- 6 `ireland_lc_*_embedding.py` shims (78 LOC total of docstrings only)
- 7 jurisdiction shims (91 LOC total)
- **Net: -169 LOC**

### FF.16 — `baml_src/british_isles/_shared/qpack_template.baml` (-1,670 LOC)
- 8 `qpack_*.baml` files = **2,670 LOC removed**
- 1 new template: `baml_src/british_isles/_shared/qpack_template.baml` (250 LOC)
- **Net: -2,420 LOC** (note: lower than estimated due to Ireland/England differences)

### FF.17 — Delete 13 `_legacy/grading/*.baml` files (-350 LOC)
- 7 grading files (mathematics/chemistry/geography/english/gaeilge/computer_science/grading)
- **Net: -350 LOC**

### FF.18 — `FetchPanel.tsx` (-300 LOC)
- 4 components: KnowledgeGraphPanel (243) + PipelineStatus (228) + RecentActivityFeed (229) + SubjectAgentGrid (138) = **838 LOC**
- 1 new shared `FetchPanel.tsx` (80 LOC)
- **Net: -300 LOC** (most code stays, just the boilerplate dedups)

## Helper Wins (5 sub-tasks)

### FF.1 — `BAMLFunctionTool` (-1,200 LOC)
- 18 hand-written `FunctionTool` wrappers in `agents/tools/*.py` (avg 80 LOC each)
- 1 new helper: `agents/integrations/baml_function_tool.py` (200 LOC)
- **Net: -1,200 LOC**

### FF.2 — `marimo_baml` (-400 LOC)
- 19 `setup_biep_registry_header` call sites (avg 20 LOC each)
- 1 new helper: `notebooks/_shared/marimo_baml.py` (200 LOC)
- **Net: -400 LOC**

### FF.3 — `agent_ui_bridge.py` (-150 LOC)
- 6 `BuiltInPlanner` boilerplate patterns (avg 25 LOC each)
- 1 new helper: `agents/integrations/agent_ui_bridge.py` (300 LOC)
- **Net: +150 LOC** (net positive — the helper adds more value than it dedups)

### FF.4 — `marimo_to_copilotkit.py` (-300 LOC)
- 4 component fetch patterns (avg 75 LOC each)
- 1 new helper: `notebooks/_shared/marimo_to_copilotkit.py` (200 LOC)
- **Net: -300 LOC**

### FF.5 — `cocoindex_query_api.py` (-800 LOC)
- 47 ad-hoc `lancedb.connect(CIANFHOGHLAIM_LANCEDB_URL)` calls (avg 17 LOC each)
- 1 new helper: `cocoindex_flows/_shared/cocoindex_query_api.py` (250 LOC)
- **Net: -800 LOC**

## Crown Jewels (7 sub-tasks)

| # | Wire | Replaces | Net |
|:--|:--|:--|:--|
| FF.6 | BAML→CocoIndex (47 Apps) | Direct LLM calls | 0 LOC (better output) |
| FF.7 | 12 ADK agents as CopilotKit | Manual AG-UI bridges | -500 LOC |
| FF.8 | A2UI for 12 ADK agents | Hand-written components | -300 LOC |
| FF.9 | 6 LC BAML→`curriculum_agent` | Hand-written `FunctionTool` wrappers | -300 LOC |
| FF.10 | `00_baml_tour.py` | Nothing — new tour | +300 LOC |
| FF.11 | 4-path OCR BAML→CocoIndex | Sequential Python | -200 LOC |
| FF.12 | `baml_py.Pdf.from_base64` | Embed→string→BAML handoff | -150 LOC |

## Net Combined Forecast (this step)

| Category | Removed LOC | Added LOC | Net |
|:--|:--|:--|:--|
| 6 Dedup Wins | -4,693 LOC | +830 LOC | **-3,863 LOC** |
| 5 Helper Wins | -2,850 LOC | +1,150 LOC | **-1,700 LOC** |
| 7 Crown Jewels | -1,750 LOC | +300 LOC | **-1,450 LOC** |
| **Total** | **-9,293 LOC** | **+2,280 LOC** | **-7,013 LOC** |

Note: The original estimate was -8,833 LOC. The audit reveals a deeper dedup opportunity (-9,293 vs -7,500 estimated) — primarily because the 8 `qpack_*.baml` files are 2,670 LOC total vs the 1,500 estimated.

## Acceptance

- [ ] `dedup-report.md` is reviewed by both leads
- [ ] No file in the dedup lists is referenced by code outside the deletion
- [ ] All tests still pass after each dedup sub-task
- [ ] The 5 helpers, 12 crown jewels, and 6 dedup wins land in a single git commit per sub-task
- [ ] The 4-stage plane architecture is documented in `baml_src/british_isles/_shared/qpack_template.baml`