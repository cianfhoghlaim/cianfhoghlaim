# Mega-3c — Marimo Modernization + Cross-Package Integration + 4 Stage Marimo Dashboards

## Why

Mega-3a shipped the 5 BAML stage templates + the 4 stage ADK agents.
Mega-3b shipped the CocoIndex plane (4 stage factories + european_nations
collapse + CopilotKit v2.0 migration + A2UI surface generator).
This Mega-3c change lands the **Marimo plane** + the **cross-package
integration** that ties all 5 packages together:

- The 4 stage Marimo dashboards (one per stage: LC + JC + A-Level + GCSE)
- The `biiep_v3_dashboard_v2` collapse (the 7 tier dashboards share
  1 helper — -4,200 LOC)
- The `_pep723_template.py` collapse (the 201 PEP 723 headers share
  1 template — -5,500 LOC)
- The 60 cross-package integration sub-tasks (BAML ↔ CocoIndex ↔
  Marimo ↔ ADK ↔ CopilotKit)
- The 30 Marimo sub-tasks (chat, streaming, generative UI, multi-provider,
  FastAPI auth, etc.)

The current state has:
- **201 .py Marimo notebooks** (60,920 LOC)
- **5,500 LOC of duplicate PEP 723 headers** (the same `# /// script` block in 201 files)
- **4,200 LOC of tier dashboard duplication** (7 tier dashboards sharing the same 8-cell operator console)
- **No use of `mo.ui.chat` streaming, no `mo.ai.llm`, no A2UI surfaces**
- **60 integration sub-tasks pending** (BAML → CocoIndex, BAML → ADK, ADK → CopilotKit, etc.)

The total duplication is **~10,766 LOC** in this change scope. The
planned additions are **~6,900 LOC** (the 4 stage dashboards + the
integration helpers + the marimo helpers).

**Net result: -6,066 LOC** while adding the Marimo plane + the
integration surface + 18 ADDED spec requirements across 7 specs.

## What changes — The 4 Stage Marimo Dashboards + Integration Surface

### The 4 stage Marimo dashboards (one per stage)

| Stage | Marimo dashboard | LOC |
|:--|:--|:--|
| **Leaving Cycle** | `notebooks/19_ireland_pipeline_dashboard.py` (existing, 237 LOC) | +200 (per-stage wiring) |
| **Junior Cycle** | `notebooks/19_junior_cycle_pipeline_dashboard.py` (new, ~150 LOC) | +150 |
| **A-Level** | `notebooks/20_england_alevel_pipeline_dashboard.py` (new, ~150 LOC) | +150 |
| **GCSE** | `notebooks/20_england_gcse_pipeline_dashboard.py` (new, ~150 LOC) | +150 |

Each stage dashboard uses the canonical `build_biep_v3_dashboard(jurisdiction=..., milestone=...)` helper from `notebooks/_shared/biiep_v3_dashboard_v2.py`.

### The `_pep723_template.py` collapse (Phase 1)

Every Marimo notebook currently has the same `# /// script` block (PEP 723
inline metadata, 9 dependencies). The template collapse:

| Before | After |
|:--|:--|
| 201 files × 8 lines = ~1,600 LOC of duplicate headers | 1 template file (~50 LOC) + 201 thin notebook files |

The template is at `notebooks/_shared/_pep723_template.py` and
includes the canonical 9 dependencies (marimo, ibis, pandas, altair,
pyarrow, anywidget, traitlets, duckdb, python-dotenv).

### The `biiep_v3_dashboard_v2` collapse (Phase 2)

The 7 tier dashboards (19_ireland, 20_england, 21_sct_wls_ni, 22_crown,
23_8_jurisdiction, 26_aistear, 27_primary) all share the same 8-cell
operator console. The v2 helper:

| Before | After |
|:--|:--|
| 7 files × ~600 LOC = 4,200 LOC | 1 helper (~300 LOC) + 7 thin wrappers |

The v2 helper at `notebooks/_shared/biiep_v3_dashboard_v2.py` exposes
`build_biep_v3_dashboard(jurisdiction=..., milestone=...)` (parameterised).

### The cross-package integration surface (Phase 3-7)

| Integration helper | LOC | Wires |
|:--|:--|:--|
| `agents/integrations/agent_ui_bridge.py` (FF.3) | 300 | ADK → CopilotKit (AG-UI Protocol) |
| `notebooks/_shared/marimo_baml.py` (FF.2) | 200 | BAML → Marimo (chat + ai.llm) |
| `notebooks/_shared/marimo_to_copilotkit.py` (FF.4) | 200 | Marimo → CopilotKit (tool) |
| `cocoindex_flows/_shared/cocoindex_query_api.py` (FF.5) | 250 | CocoIndex → Marimo (search closure) |
| `BAMLFunctionTool` (FF.1) | 200 | BAML → ADK (tool) |

## How changes — Phasing & Dedup Wins

### Phase 1: PEP 723 template collapse (Week 1)
- 201 notebooks → 1 template + 201 thin notebooks (-5,500 LOC)

### Phase 2: biiep_v3_dashboard_v2 collapse (Week 2)
- 7 tier dashboards → 1 helper + 7 thin wrappers (-4,200 LOC)

### Phase 3: 4 stage Marimo dashboards (Weeks 3-4)
- LC dashboard (existing — wire to v2 helper)
- JC dashboard (new)
- A-Level dashboard (new)
- GCSE dashboard (new)

### Phase 4: Marimo patterns tour (Week 5)
- `00_marimo_patterns_tour.py` enhancements
- `mo.ui.chat` streaming + `mo.ai.llm` + A2UI surfaces + multi-provider

### Phase 5: Cross-package integration (Weeks 6-10)
- The 60 IS-* sub-tasks (BAML ↔ CocoIndex ↔ Marimo ↔ ADK ↔ CopilotKit)

### Phase 6: FastAPI + auth (Week 11)
- Mount the 6 BIEP notebooks as FastAPI endpoints
- Adopt the `frameworks/fastapi-auth/` pattern

## Version Pins

- `marimo>=0.14.10` (already pinned in `mise.toml`)

## Spec Deltas (18 ADDED across 7 specs)

| Spec | ADDED | Source |
|:--|:--|:--|
| `oideachais-marimo-dashboards` | 6 | MM.1, .9, .10, .21, .26, .27 (per the BAML plan) |
| `agentic-frontend-frameworks` | 2 | MM.12, .13 (FastAPI + auth) |
| `british-isles-education-pipeline-v3` | 4 | MM.20, .24, .25, .30 (4 stage dashboards + lineage viewer) |
| `centralized-model-registry` | 2 | MM.7, .10 (the model selector) |
| `oideachais-pipeline` | 2 | MM.7, .8 (BAML → Marimo → oideachais) |
| `knowledge-sync-loop` | 1 | MM.20 (sync:baml extension) |
| `indexing-and-cognition` | 1 | MM.28 (CocoIndex → Marimo dataset analysis) |
| **TOTAL** | **18** | |

## Pre-Validation Checklist

- [ ] `mise run baml:generate` regenerates clean
- [ ] `mise run cocoindex:conformance` passes
- [ ] `mise run lint:skills` passes (16 lint gates)
- [ ] `openspec validate 2026-11-25-mega-3c-marimo-and-integration-v1 --strict`
- [ ] `mise run turbo build` passes
- [ ] Net LOC reduction report shows -6,066 LOC savings
- [ ] All 19/19 existing tests still pass + new ones added
- [ ] No conflict with the 4 Mega-3 predecessors (roadmap + fast-follow + Mega-3a + Mega-3b)

## Cross-References

- Roadmap: `openspec/changes/2026-08-18-mega-3-roadmap-v1/proposal.md`
- Predecessor: `openspec/changes/2026-09-30-mega-3b-cocoindex-and-copilotkit-v1/proposal.md`
- Foundation: `agents/integrations/baml_function_tool.py` (BAMLFunctionTool helper from Mega-3a)
- Foundation: `web/apps/cianfhoghlaim/components/_shared/A2UISurfaceGenerator.tsx` (A2UI generator from Mega-3b)