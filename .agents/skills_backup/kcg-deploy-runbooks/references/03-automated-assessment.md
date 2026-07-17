---
title: 'Deploy Plan 03 — Automated Assessment & Grade Forecasting Oracle'
domain: deploy-plan
status: draft
description: 'OCR + BAML extraction + DuckDB/MotherDuck historical-grade analysis. Vision OCR for handwritten submissions, BAML rubric alignment, and statistical forecasting against historical boundaries.'
read_when:
  - 'designing OCR/HTR pipelines for student work'
  - 'extending grading rubrics with BAML'
  - 'forecasting outcomes from historical data'
supersedes: []
superseded_by: []
related_specs:
  - assessment-extraction
  - cianfhoghlaim-pipeline
related_apps:
  - sruth/meaisinfhoghlaim/ocr
  - sruth/meaisinfhoghlaim/agents/assessor
  - sruth/cianfhoghlaim/dlt_sources/ireland/sec.py
  - sruth/cianfhoghlaim/dagster_defs
related_llm_stack:
  - 'BAML (typed rubric alignment)'
  - 'litellm (model routing for vision OCR fallback)'
  - 'mlflow (model + rubric versioning)'
truth: sole
last_touched: 2026-06-13
---

# Deploy Plan 03 — Automated Assessment & Grade Forecasting Oracle

## 0. Why this plan

Replace the original Tangent 3 framing (which named Gemini Pro Vision,
GPT-4o, Google Cloud Vision, AWS Textract as separate options) with a
deploy plan grounded in the **OCR quadrant** (`sruth/meaisinfhoghlaim/ocr/`)
and the **BAML extraction** discipline. The goal is an oracle that:

1. Reads handwritten or typed student work via OCR.
2. Aligns the work to a BAML-extracted rubric.
3. Generates instant feedback.
4. Forecasts final grades from historical SEC/CCEA/Ofqual boundaries.

## 1. Monorepo grounding

| Asset | Path | Use |
|:--|:--|:--|
| Quadrant | `sruth/meaisinfhoghlaim/ocr/` | OCR/HTR models, Irish metrics, dataset generators |
| Quadrant | `sruth/cianfhoghlaim/` | DLT historical data, BAML extraction, Dagster orchestration |
| Skill | `.agents/skills/document-intelligence/SKILL.md` | OCR + layout analysis |
| Skill | `.agents/skills/baml/SKILL.md` | Typed rubric extraction |
| Skill | `.agents/skills/dagster/SKILL.md` | SDA patterns for the assessment pipeline |
| Skill | `.agents/skills/dlt/SKILL.md` | Historical-grade ingestion |

The 5-quadrant topology is in `docs/00-core/CLAUDE.md` §QUADRANT_MAP.

## 2. OCR/HTR pipeline

The OCR quadrant exposes 6 backends (per `sruth/meaisinfhoghlaim/ocr/README.md`):

| Backend | Best for | v1 use |
|:--|:--|:--|
| **Tesseract 5** (`pytesseract`) | Typed text | Quick fallback, low-cost |
| **PaddleOCR** | Multilingual including Latin script | Default for typed work |
| **TrOCR** (Microsoft) | Handwritten English | Default for handwritten en |
| **Pylaia** | Handwritten Irish / Latin | Default for handwritten ga |
| **Docling** | Layout-preserving PDF extraction | PDFs from publishers |
| **ColPali** | Late-interaction visual retrieval | v2: rubric-to-workpage matching |

For v1 we default to **TrOCR + Pylaia** (handwriting) and **PaddleOCR**
(typed), with Tesseract as the safety net. Selection is per-page
based on the document classifier in
`sruth/meaisinfhoghlaim/ocr/router.py` (a tiny BAML schema).

The layout analysis (equations, diagrams, crossed-out text) is handled
by **Docling** for PDFs and a custom `sruth/meaisinfhoghlaim/ocr/layout.py`
heuristic for images.

## 3. BAML rubric extraction

Each marking scheme is a BAML-typed object:

```baml
class MarkingScheme {
  paper_id string
  year int
  nation string
  qualification string
  subject string
  total_marks int
  grade_boundaries GradeBoundary[]     // H1/H2/.../O1 for ROI; 9/8/.../1 for UK
  questions Question[]
}

class Question {
  question_id string
  max_marks int
  rubric_steps RubricStep[]
  bloom_levels string[]
  topic_tags string[]                  // joins to LearningOutcome
}

class RubricStep {
  step_id string
  description string
  marks int
  partial_credit_policy string          // "ramp" | "binary" | "linear"
  common_errors string[]
}

class GradeBoundary {
  grade string                          // "H1" | "9" | "A*"
  min_marks int
  cumulative_pct float?
}
```

The extraction prompt is in
`sruth/cianfhoghlaim/baml_src/marking_scheme.baml` and runs as a Dagster
asset: `marking_schemes.rubric_extracted`.

## 4. Assessment engine

For a student submission:

1. **OCR** → raw text + layout JSON.
2. **BAML extraction** → `StudentResponse { question_id, claimed_answers: AnswerAttempt[] }`.
3. **Rubric alignment** → BAML prompt that compares the attempt to
   the rubric steps and emits a `MarkedAttempt`:
   ```baml
   class MarkedAttempt {
     question_id string
     awarded_marks int
     per_step_marks int[]
     feedback_en string
     feedback_target string               // ga|cy|gd|null
     citations RubricStepRef[]
     confidence float                      // 0..1
   }
   ```
4. **Feedback generation** → litellm call with the `MarkedAttempt` and
   the learner's `ConceptMastery` from Deploy Plan 02.
5. **Human-in-the-loop** flag — if OCR confidence < 0.7 OR alignment
   confidence < 0.6, route to a teacher queue.

The agent lives in `sruth/meaisinfhoghlaim/agents/assessor/` and is
exposed as a `fastapi` service at `/api/v1/assess`.

## 5. Grade forecasting

Forecast = function of:

- Current `MarkedAttempt` (this assessment)
- Historical cohort performance: students with similar attempt profiles
  → final grade distribution.

The data lives in MotherDuck (`cianfhoghlaim_grades.historical_attempts`
and `cianfhoghlaim_grades.historical_boundaries`). The forecasting model
is **DuckDB SQL**, not Python ML — for v1, we use:

```sql
WITH cohort AS (
  SELECT
    a.student_id,
    a.mark_pct,
    b.final_grade
  FROM cianfhoghlaim_grades.historical_attempts a
  JOIN cianfhoghlaim_grades.historical_final_grades b
    ON a.student_id = b.student_id
  WHERE a.qualification = $1
    AND a.subject = $2
    AND a.year < $forecast_year
)
SELECT
  final_grade,
  COUNT(*) AS n,
  AVG(mark_pct) AS avg_mark,
  STDDEV(mark_pct) AS sd_mark
FROM cohort
WHERE mark_pct BETWEEN $forecast_pct - 5 AND $forecast_pct + 5
GROUP BY final_grade
ORDER BY n DESC;
```

This gives a **distribution** over final grades. The `confidence
interval` is the empirical 5%-95% range.

For v2 we move to a Bayesian hierarchical model trained in
`sruth/meaisinfhoghlaim/evaluation/` (per the skill doc, v0.1+). The model
is logged to **mlflow** for traceability.

## 6. Student/teacher dashboard

A Marimo notebook at `sruth/cianfhoghlaim/notebooks/assessor_dashboard.py`
renders:

- Upload form (image / PDF)
- Live OCR preview
- Marked attempt breakdown
- Forecast distribution chart
- Per-concept mastery heatmap (links to Deploy Plan 02)

The notebook is published to MotherDuck as a Dive (per
`docs/05-web/frontend-topology.md` §5).

## 7. Phased action plan

| Phase | Scope | Exit criteria |
|:--|:--|:--|
| 0 | BAML `MarkingScheme` extractor | 100% precision on 20-paper gold set |
| 1 | OCR router (TrOCR + Pylaia + PaddleOCR) | 90% CER on a 50-page handwriting set |
| 2 | BAML `MarkedAttempt` extractor | 80% agreement with 2 human markers |
| 3 | MotherDuck historical-grade ingestion (8 sources) | 50 years of boundaries × 8 nations |
| 4 | Forecast query (DuckDB SQL) | 70% accuracy on holdout year |
| 5 | Marimo dashboard | Teacher can run a full assessment in <2 min |

## 8. Risks and mitigations

| Risk | Mitigation |
|:--|:--|
| OCR errors propagate to grading | Confidence threshold + human review queue |
| LLM bias in feedback | All feedback anchored to rubric citations; teacher audit log |
| Data privacy (student work) | Images processed ephemerally; OCR text stored in MotherDuck with row-level ACL |
| Boundary drift over years | Forecast uses rolling 5-year window; cohort similarity scoring weights recent years |

## 9. Out of scope (deferred)

- Auto-grading essays (only short-form + structured in v1) — v2
- Real-time classroom dashboard (v3)
- Plagiarism detection (v2 — leverage existing `infrastructure/browser/` semantics)

## 10. Cross-references

- `docs/00-core/CLAUDE.md` — 5-quadrant topology
- `docs/02-data-platform/storage-mental-model.md` — storage layering
- `docs/02-data-platform/cross-domain-registry.md` — `sruth/cianfhoghlaim/sources.yaml`
- `docs/04-ai-ml/llm-stack-hierarchy.md` — BAML + litellm ordering
- `openspec/specs/assessment-extraction/spec.md` — exam-paper ingestion
- `openspec/specs/cianfhoghlaim-pipeline/spec.md` — end-to-end pipeline
- `.agents/skills/document-intelligence/SKILL.md` — OCR + layout
- `.agents/skills/baml/SKILL.md` — BAML extraction
- `.agents/skills/dagster/SKILL.md` — SDA patterns
- `.agents/skills/mlflow/SKILL.md` — model versioning
