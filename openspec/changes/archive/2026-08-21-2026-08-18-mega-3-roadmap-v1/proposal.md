# Mega-3 Roadmap — The 4-Stage Plane Modernization (2026-08-18)

## Why

The Cianfhoghlaim platform has 5 deeply integrated packages — **BAML**, **CocoIndex**, **Google ADK**, **CopilotKit**, **Marimo** — each at its current production capability but with substantial duplication, sprawl, and unrealised value across the 4-stage education plane (Leaving Cycle + Junior Cycle + A-Level + GCSE).

The current state has:
- **320 .baml files** with **491 stub prompts** (`"Auto-generated extraction prompt."`)
- **190 CocoIndex files / 24K LOC** with **47 R1-R4 compliant Apps** + 40+ standalone files that should be factories
- **21 ADK agents / 7,816 LOC** with **~80 hand-written Pydantic classes** + **18 hand-written `FunctionTool` wrappers**
- **2 CopilotKit web apps** (v1.10 vs v2.0 pin drift) with **4 hand-written components**
- **201 Marimo notebooks / 60K LOC** with **5,500 LOC of duplicate PEP 723 headers** + **7 hand-written tier dashboards** (4,200 LOC)

The total duplication is **~43,429 LOC**. The planned additions are **~17,630 LOC** (the 5 integration helpers + the 4-stage templates/factories/dashboards/agents + the 60+ integration sub-tasks).

**Net result: -25,799 LOC** while adding:
- 4 BAML stage templates (LC + JC + A-Level + GCSE) covering 46 subjects
- 4 CocoIndex stage factories generating 99 Apps (replacing 40+ standalone files)
- 4 Marimo stage dashboards
- ~46 auto-generated ADK agents (replacing 21 hand-written)
- 5 integration helpers + 60+ cross-package integration sub-tasks
- 90 ADDED spec requirements across 17 specs

## What changes — The 4-Stage Plane

The same 1-template-file pattern applies to all 4 stages across all 4 packages:

```
                 BAML              CocoIndex          Marimo             ADK
Stage             (templates)         (factories)        (dashboards)       (agents)
═══════════════════════════════════════════════════════════════════════════════════
Leaving Cycle      lc_template.baml   ireland_lc_factory   19_ireland_...   lc_subject_agent
Junior Cycle       jc_template.baml   ireland_jc_factory   19_junior_...    jc_subject_agent
A-Level            alevel_template    england_alevel_...   20_england_...   alevel_subject_agent
GCSE               gcse_template      england_gcse_...     20_england_...   gcse_subject_agent
                                                                              (via BAMLFunctionTool)
```

Every row follows the same pattern: 1 template file generates 1 factory + 1 dashboard + 1 agent, all driven by the canonical BAML output.

## How — The 5-Step Rollout

### Step 0: `2026-08-18-mega-3-roadmap-v1` (THIS CHANGE — narrative only, 1 day)
Documents the 5-step rollout + the 4-stage plane + the -25,799 LOC dedup target.

### Step 1: `2026-08-18-mega-3-fast-follow-v1` (2 weeks)
**The 5 integration helpers + 12 crown jewels + 6 dedup wins:**
- `BAMLFunctionTool` (FF.1) — replaces 18 hand-written `FunctionTool` wrappers (-1,200 LOC)
- `marimo_baml` (FF.2) — replaces 19 `setup_biep_registry_header` calls (-400 LOC)
- `agent_ui_bridge.py` (FF.3) — full port of `ag-ui-adk.ADKAgent` (-150 LOC)
- `marimo_to_copilotkit.py` (FF.4) — replaces 4 component fetch patterns (-300 LOC)
- `cocoindex_query_api.py` (FF.5) — replaces 47 ad-hoc `lancedb.connect` calls (-800 LOC)
- Plus 12 crown jewels: BAML→CocoIndex (FF.6), ADK→CopilotKit (FF.7-8), BAML→ADK (FF.9), the baml tour (FF.10), 4-path OCR (FF.11), direct PDF input (FF.12)
- Plus 6 dedup wins: `cocoindex_flows/subjects/_factory.py` (FF.13), delete 13 shims (FF.14), `qpack_template.baml` (FF.16), delete 13 `_legacy/grading/*.baml` (FF.17), `FetchPanel.tsx` (FF.18)
- **Net savings this step: -8,833 LOC**

### Step 2: `2026-08-26-mega-3a-baml-and-adk-v1` (8-10 weeks)
**Plans 1 (BAML) + 2 (ADK) + 4 stage templates + 8 NCCA Junior Cycle subjects:**
- 30 BAML sub-tasks (A.1-A.8, B.1-B.6, C.1-C.5, D.1-D.9, E.1-E.8, F.1-F.5)
- 20 ADK sub-tasks (ADK.1-ADK.20)
- 4 stage BAML templates (LC + JC + A-Level + GCSE, ~950 LOC new, replaces ~4,700 LOC)
- 8 NCCA Junior Cycle subjects at full scope (~1,200 LOC new)
- Auto-generate 46 ADK stage agents from BAML (-5,500 LOC)
- Auto-generate 80 Pydantic classes (-2,400 LOC)
- **Net savings this step: -9,700 LOC**

### Step 3: `2026-09-30-mega-3b-cocoindex-and-copilotkit-v1` (8-10 weeks)
**Plans 3 (CocoIndex) + 4 (CopilotKit) + 4 stage factories + european_nations factory v2:**
- 20 CocoIndex sub-tasks (CO.1-CO.20)
- 20 CopilotKit sub-tasks (CK.1-CK.20)
- 4 stage CocoIndex factories (~1,000 LOC new, replaces ~1,500 LOC)
- `european_nations/_factory.py` v2 (~500 LOC new, replaces 40 files / ~3,000 LOC)
- **Net savings this step: -1,200 LOC**

### Step 4: `2026-11-25-mega-3c-marimo-and-integration-v1` (10-12 weeks)
**Plans 5 (Marimo) + 6 (Integration) + 4 stage dashboards:**
- 30 Marimo sub-tasks (MM.1-MM.30)
- 60 integration sub-tasks (IS-1.1 to IS-6.6)
- 4 stage Marimo dashboards (~600 LOC new, replaces ~1,200 LOC)
- `notebooks/_shared/_pep723_template.py` (-5,500 LOC duplicate headers)
- `notebooks/_shared/biiep_v3_dashboard_v2.py` (-4,200 LOC tier dashboards)
- **Net savings this step: -6,066 LOC**

## Net Combined Forecast

| Step | Dedup target | New code | Net |
|:--|:--|:--|:--|
| 0 (roadmap) | 0 | 0 | 0 |
| 1 (fast-follow) | -10,163 LOC | +1,330 LOC | **-8,833 LOC** |
| 2 (Mega-3a) | -14,200 LOC | +4,500 LOC | **-9,700 LOC** |
| 3 (Mega-3b) | -6,100 LOC | +4,900 LOC | **-1,200 LOC** |
| 4 (Mega-3c) | -12,966 LOC | +6,900 LOC | **-6,066 LOC** |
| **TOTAL** | **-43,429 LOC** | **+17,630 LOC** | **-25,799 LOC** |

## Spec Deltas (across all 4 changes)

| Spec | ADDED | Notes |
|:--|:--|:--|
| `agent-platform-cluster` | 5 | FF.1-FF.5 foundation + ADK.1/11/15 |
| `agent-fleet-orchestration` | 3 | ADK.2/3/4/9 + CK.13/20 |
| `agentic-frontend-frameworks` | 5 | CK.1-5 + ADK.16 + IS-5.x |
| `agent-observability` | 3 | F.1/F.5 + ADK.17/18 + CK.9 |
| `baml-schemas` | 8 | FF.1 + A.1-8 + C.1-5 + CO.1 |
| `centralized-schema-registry` | 4 | F.4 + IS-1.x + CO.16/18 |
| `centralized-model-registry` | 4 | A.1 + CO.4 + MM.7/10 + IS-4.1 |
| `british-isles-education-pipeline-v3` | 15 | CO.2/5/7/15 + MM.20/24/25/30 + IS-2.x + the 8 JC |
| `oideachais-pipeline` | 4 | A.7 + CO.6/14 + MM.7/8 |
| `oideachais-marimo-dashboards` | 9 | MM.1/9/10/21/26/27 + IS-3.x |
| `dagster-5-layer-component-architecture` | 4 | A.3 + D.2 + CO.13 + IS-1.1 |
| `oideachais-university-deep-extraction` | 2 | A.6 + IS-3.1 |
| `indexing-and-cognition` | 5 | CO.8/12 + MM.28 + IS-6.x |
| `knowledge-sync-loop` | 5 | E.6-8 + CO.16/18 + MM.20 + IS-5.x |
| `meaisinfhoghlaim-agent-frameworks` | 8 | ADK.5/6/13 + CK.6 + IS-2.x + the 8 JC + 8 NCCA |
| `centralized-registry` (new) | 5 | The 4 new helpers + 7-tab expansion |
| `mcp-curriculum` (new) | 1 | FF.11 (the 4-path OCR BAML) |
| **TOTAL** | **~90 ADDED across 17 specs** | |

## Dependencies Between Steps

```
Step 0 (roadmap) ──► Step 1 (fast-follow) ──► Step 2 (Mega-3a) ──► Step 3 (Mega-3b) ──► Step 4 (Mega-3c)
                              │                  │                  │                  │
                              ▼                  ▼                  ▼                  ▼
                       5 helpers         BAML + ADK          CocoIndex +      Marimo +
                                              +             CopilotKit        Integration
                       12 crown jewels   4 stage templates   european_nations  4 stage
                       6 dedup wins     8 NCCA JC           4 stage factories dashboards
```

Steps 2-4 can overlap by 2-4 weeks each (parallel where possible) because:
- **Mega-3a** can start as soon as `BAMLFunctionTool` (FF.1) lands
- **Mega-3b** can start as soon as the 12 ADK agents are wired (FF.7)
- **Mega-3c** can start as soon as all 5 helpers are stable (FF.1-FF.5)

## Pre-Validation Checklist

- [ ] Each step lands behind pinned versions (`baml-py>=0.223.0,<0.224.0`, `google-adk>=1.10.0`, `cocoindex>=1.0.20`, `@copilotkit/react-core/v2>=1.67.1`, `marimo>=0.14.10`)
- [ ] Each step emits a `dedup-report.md` showing the lines saved before/after
- [ ] No regression — all 19/19 existing tests still pass + new ones added
- [ ] The 4-stage plane is consistent — every stage has BAML + CocoIndex + Marimo + ADK parity
- [ ] No conflict with the just-archived `2026-08-17-biep-v3-bring-up-v1` (the 7 spec deltas, 16 ADDED + 0 MODIFIED)
- [ ] No conflict with the just-archived `2026-08-17-hygiene-drift-cleanup-v1` (the 6 spec deltas, 5 ADDED + 1 MODIFIED)