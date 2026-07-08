# Change: 2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams

## Why

The Cianfhoghlaim data platform has 41 PDFs + 2 JPGs across 5 NCCA
Leaving Certificate subjects (chemistry / computer_science / gaeilge
/ geography / mathematics) under
`cianfhoghlaim/leaving_certificate/{<subject>}/<en|ga>/` that are
unprocessed. The existing pipeline only has 2-of-5 subject defs
(`leaving_cert_mathematics` + `leaving_cert_gaeilge` from the 2025-09
rewrite); chemistry, computer_science, geography are missing.

Per user direction:
- Focus the pipeline on **chemistry, computer_science, gaeilge,
  geography, mathematics** (the 5 active LC subjects; applied
  mathematics / biology / business / english / french / history /
  technology / ukrainian are deferred).
- Use the v4 OCR/VLM registry's `select_ocr_backend()` heuristic to
  route each PDF.
- Extract both text AND diagrams (per "Yes, extract diagrams" decision).

## What changes

This change creates a complete 7-stage pipeline for the 5 LC subjects:

### Stage 1 — VLM/OCR routing

Each PDF is routed via `select_ocr_backend(pdf_path)`:

| Filename pattern                                | Model key          |
|:--|:--|
| Irish-language PDFs (gaeilge/)                  | `glm-4.6v-flash`   |
| Exam papers (LC###ALP/EV/IV.pdf)                 | `qwen3-vl-8b`       |
| Syllabi (SC###Syllabus, SC-Chemistry-Spec, Siollabais) | `gemma-4-26B-A4B` |
| Marking schemes (SCSEC##_guideline_material_*.pdf) | `molmo2-8b`     |
| Scanned JPGs (geography has 1)                  | `docling-serve`    |
| Default fallback                                 | `qwen3-vl-8b`       |

### Stage 2 — BAML extraction (5 new classes)

5 new BAML files in
`cianfhoghlaim/baml_src/education/lc_extraction/`:

1. `curriculum_syllabus.baml` — `class SyllabusDocument`, `class ModuleTopic`, `class LearningOutcome`
2. `exam_paper_layout.baml` — `class ExamPaper`, `class Question`, `class QuestionSection`
3. `marking_scheme.baml` — `class MarkingScheme`, `class MarkAllocation`, `class GradeDescriptor`, `enum MarkingBand`
4. `cross_linguistic.baml` — `class CrossLinguisticConcept` (EN ↔ GA topic mapping)
5. `syllabus_diagram.baml` — `class SyllabusDiagram`, `class DiagramRegion` (NEW: extracted via molmo2-8b)

### Stage 3 — DuckLake (6 tables per subject = 30 tables)

5 DuckLake schemas: `lc_chemistry_*`, `lc_computer_science_*`,
`lc_gaeilge_*`, `lc_geography_*`, `lc_mathematics_*`. Each schema has
6 tables: `<subject>_syllabus`, `<subject>_papers`,
`<subject>_marking`, `<subject>_topics`, `<subject>_cross_ling`,
`<subject>_diagrams`.

### Stage 4 — LanceDB embeddings (BGE-M3, 5 tables, 1 per subject)

5 LanceDB tables: `lc_<subject>_embeddings`. HNSW index per subject.

### Stage 5 — Cognee cognify (5 datasets)

5 Cognee datasets: `oideachais_chemistry`, `oideachais_computer_science`,
`oideachais_gaeilge`, `oideachais_geography`, `oideachais_mathematics`.

### Stage 6 — Graphiti temporal episodes (5 streams)

5 Graphiti episode streams, one per subject. Bi-temporal: `event_time`
from BAML extraction, `ingest_time` from scan timestamp.

### Stage 7 — FalkorDB cross-subject graph

Nodes: Subject, Topic, LearningOutcome, Question, Year, ModuleKind.
Edges: `HAS_TOPIC`, `ASSESSED_BY`, `EVOLVED_TO`,
`EN_CORRESPONDS_TO_GA` (cross-linguistic).

## Files

- 5 BAML files: `cianfhoghlaim/baml_src/education/lc_extraction/*.baml`
- 1 DLT source: `cianfhoghlaim/dlt/filesystem/leaving_cert_source.py`
- 1 Dagster assets module: `cianfhoghlaim/dagster/defs/2_materials/lc_extraction/lc5_assets.py`
- 3 defs.yaml files (L1 ingestion, L2 materials, L3 model lifecycle)
- 16 dev notebooks: `cianfhoghlaim/notebooks/dashboards/leaving_cert/{01..16}_*.py`
- Openspec change files (proposal + tasks + 1 spec delta)

## Impact

- **Affected specs:** `oideachais-pipeline` (1 spec delta — adds LC5 pipeline)
- **Affected code:** 26 new files (5 BAML + 1 DLT + 1 dagster + 3 defs + 16 notebooks)
- **Affected hosts:** `bunchloch` only
- **Risk:** low — all BAML calls return stubs if BAML is unavailable; all VLM/OCR calls degrade gracefully
- **Audit gates:** `openspec validate --strict` + `marimo parse notebooks/dashboards/leaving_cert/*.py`

## Non-goals

- **Not including the 8 other LC subjects** (applied_mathematics / biology / business / english / french / history / technology / ukrainian). Add in a follow-up change.
- **Not building the dagster-local image** — the 11 Python packages added in Change A are picked up on next `docker build`.
- **Not wiring the per-subject ADK agents** (math_agent / appm_agent / etc.) — deferred to `2026-07-XX-wire-adk-agents-to-lc-pipeline`.
- **Not wiring the marimo notebooks to live data** — the notebooks use stub data; follow-up `2026-07-XX-wire-marimo-to-live-data` change.
- **Not loading the new LC5 + Gemini 6-corpus assets in the dagster daemon yet.** The new assets use `from dagster import ...` which gets shadowed by `cianfhoghlaim/dagster/` (a legacy code tree) when cianfhoghlaim is on sys.path. The fix (renaming `cianfhoghlaim/dagster/` to `cianfhoghlaim/orchestration/` or similar) is a separate refactor tracked as `2026-07-XX-rename-cianfhoghlaim-orchestration-to-avoid-shadowing`. The .py asset files are correct and would load in any environment without the shadowing.
