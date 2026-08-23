# British Isles Education Pipeline v2 (BIEP v2) Capability

## Purpose

`british-isles-education-pipeline-v2` (BIEP v2) is the v2 umbrella that
extends the BIEP v1 flagship (`british-isles-education-pipeline`) to cover
the full set of secondary-school curricula in the Republic of Ireland and
England:

- **Leaving Certificate (Ireland, EN+GA)** — the 6 LC priority subjects
  from BIEP v1, now extended with the Change 3 4-path OCR/VLM ensemble
- **Junior Cycle (Ireland, EN+GA)** — 18 NCCA subjects + 16 short courses +
  36 CBAs (the Change 1 promotion from DLT-only to full extraction)
- **A-Level (England, EN)** — 9 priority subjects × 3 awarding bodies
  (AQA + OCR + Edexcel) (the Change 2 England pipeline)
- **GCSE (England, EN)** — the same 9 subjects × 3 awarding bodies, at
  GCSE level (also Change 2)

The corresponding source code lives at:

- `baml_src/british_isles/ireland/education/lc_extraction/`
  + `baml_src/british_isles/ireland/education/junior_cycle/`
  + `baml_src/british_isles/england/education/`
- `dlt/british_isles/ireland/education/{leaving_cert,junior_cycle,lc_extraction,...}.py`
  + `dlt/british_isles/ireland/education/junior_cycle_subjects/`
  + `dlt/british_isles/england/education/subjects/`
- `cocoindex_flows/subjects/*.py` (the 7 BIEP-v1 subject flows + 1 new JC flow)
  + `cocoindex_flows/british_isles/england/{aqa,ocr,edexcel}_education_embedding.py`
- `orchestration/defs/2_materials/lc_extraction/`
  + `orchestration/defs/2_materials/junior_cycle/`
  + `orchestration/defs/2_materials/england_education/`
  + `orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/`
- `notebooks/04_biep_v2/{00,01,02,03}_*.py` (the 4 new BIEP v2 notebooks)
- `bonneagar/stacks/unstract/workflow_data/{aqa_gcse_spec,ncca_jc_cba,sec_lc_marking}.json`
- `bonneagar/stacks/changedetection/monitors/{aqa,ocr,edexcel}_monitor.yaml`

## Background

The BIEP v1 flagship (`british-isles-education-pipeline/spec.md`) covers 6
LC subjects × 2 languages + gov.ie circulars — the v1 floor. The BIEP v2
extends to:

- The full 18-subject Junior Cycle (was DLT-only, becomes full BIEP)
- The 3 awarding bodies of England (was a thin scaffold, becomes full BIEP)
- The 4-path OCR/VLM ensemble with RAGAS voting (was single-path BAML,
  becomes ensemble of BAML + Unstract + qwen3-vl-8b + gemma-4-26B-A4B)
- The full audit trail marimo portal (was just the 6 BIEP subject
  notebooks, becomes 10 ibis-first notebooks across 4 jurisdictions)

The 5 sequential openspec changes that landed this v2 umbrella:

| Change | Status | Scope |
|:--|:--|:--|
| `2026-07-20-biep-v2-junior-cycle-extraction-v1` | ✅ archived | Junior Cycle full extraction |
| `2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1` | ✅ archived | England AQA + OCR + Edexcel |
| `2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1` | ✅ archived | OCR/VLM ensemble + RAGAS vote |
| `2026-07-23-biep-v2-marimo-portal-v1` | ✅ archived | 4 cross-jurisdiction notebooks |
| `2026-07-24-biep-v2-gov-uk-change-detection-v1` | ✅ archived | AQA/OCR/Edexcel change sensors |
## Requirements
### Requirement: v2 retirement — see british-isles-education-pipeline-v3

The system SHALL recognize that `british-isles-education-pipeline-v2` is a transitional retirement marker. The canonical capability is `british-isles-education-pipeline-v3` (25 requirements) which covers the 5-milestone sequential plan + the 6-deferred-jurisdiction plan (M5-M10) + the 2-scanner-domain plan + the 4-cadence scheduling policy + the 5-phase pattern (Ingestion → Extraction → Embedding → ibis logging → Analytics).

The original v1 spec `british-isles-education-pipeline` (41 requirements) covers the original LC subjects + gov.ie circulars; the v3 spec layers on top of v1 with the milestone plan + 8-jurisdiction expansion.

Per the 2026-08-22-openspec-audit-and-merge-v1 audit + the 2026-08-22-archive-biep-v1-v2-retirement-v1 retirement change.

#### Scenario: Agent looks up the canonical BIEP v3 spec

- **WHEN** an agent reads `openspec/list --specs` to find the 5-milestone BIEP plan
- **THEN** the agent SHOULD load `british-isles-education-pipeline-v3` (the canonical)
- **AND** the transitional v2 spec is preserved as a retirement marker

## Cross-references

- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the BIEP v1 flagship that this v2 umbrella subsumes
- [`ireland-primary-jc-dlt-baml`](../ireland-primary-jc-dlt-baml/spec.md) —
  the JC capability that v2 extends to full extraction
- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract (DuckLake namespace, DLT path contract, partition contract)
- [`meaisinfhoghlaim-ocr-htr`](../meaisinfhoghlaim-ocr-htr/spec.md) —
  the 26-model 6-backend OCR/VLM registry that v2 extends (adds Docling +
  Unstract backends + ensemble consensus requirement)
- [`cianfhoghlaim-marimo-dashboards`](../cianfhoghlaim-marimo-dashboards/spec.md) —
  the marimo dashboard capability that v2 extends (adds 4 BIEP v2 notebooks)
- [`cianfhoghlaim-baml-schemas`](../cianfhoghlaim-baml-schemas/spec.md) —
  the BAML extraction library that v2 extends with 9 new BAML files
  (4 JC + 5 England)
- [`cianfhoghlaim-cocoindex-v1-migration`](../cianfhoghlaim-cocoindex-v1-migration/spec.md) —
  the R1–R4 v1 conformance contract the 4 new CocoIndex Apps obey
- [`dagster-5-layer-component-architecture`](../dagster-5-layer-component-architecture/spec.md) —
  the 5-layer Dagster component architecture that all 154 BIEP v2 assets obey
- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) —
  the 94 Docker Compose stacks catalogue that v2 extends (adds 3
  ChangeDetection monitors for England)
- [`upstream-package-monitoring`](../upstream-package-monitoring/spec.md) —
  the upstream-monitoring spec that v2 extends (adds BIEP v2 England sibling
  sensor)
- [`agent-observability`](../agent-observability/spec.md) —
  the observability stack (Langfuse + MLflow + RAGAS + Logfire) that v2
  wires the Slack/email alerts + RAGAS voting through
- [`agentic-frontend-frameworks`](../agentic-frontend-frameworks/spec.md) —
  the TanStack Start + CopilotKit + Hono + oRPC umbrella that v2 uses for
  the public web view
- `archive/2026-07-20-biep-v2-junior-cycle-extraction-v1/` — the Change 1 archive
- `archive/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/` — the Change 2 archive
- `archive/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/` — the Change 3 archive
- `archive/2026-07-23-biep-v2-marimo-portal-v1/` — the Change 4 archive
- `archive/2026-07-24-biep-v2-gov-uk-change-detection-v1/` — the Change 5 archive
- `docs/research/biiep_v2_umbrella_audit.md` *(authoritative cross-jurisdiction audit)*
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
- `.agents/skills/dagster/SKILL.md` — the 5-layer component architecture
- `.agents/skills/motherduck/SKILL.md` — MotherDuck Dives + Flights
- `.agents/skills/marimo/SKILL.md` — marimo notebook patterns
- `.agents/skills/ibis/SKILL.md` — the ibis-first contract
- `.agents/skills/tanstack-start/SKILL.md` — TanStack Start patterns
- `.agents/skills/hono/SKILL.md` — Hono API patterns
- `.agents/skills/change-detection/SKILL.md` — ChangeDetection.io patterns
- `.agents/skills/agent-observability/SKILL.md` — Langfuse + RAGAS observability
- `.agents/skills/ragas/SKILL.md` — RAGAS trace-based metrics
- `.agents/skills/mlflow/SKILL.md` — MLflow experiment tracking

## Migrated from

This v2 umbrella subsumes the v1 BIEP spec
([`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md))
for the 4 jurisdictions it covers. The v1 spec remains canonical for the
6-subject LC + gov.ie circulars floor; v2 is the umbrella on top.
