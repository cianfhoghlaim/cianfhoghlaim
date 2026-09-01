# Change: Cianfhoghlaim-Nua Certificate Pipeline v1 — LC/JC certificate generation

> **Status:** AUTHORED + IMPLEMENTED.
>
> **Phase 7 of 10** in the
> [`openspec/plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md`](../../plans/2026-09-01-cianfhoghlaim-nua-v6-era-v1.md)
> 10-phase integration of `gemini_hackathon/` learnings back into
> `cianfhoghlaim/`. The phase-by-phase authoring strategy (per
> operator direction 2026-09-01) means Phases 0-6 are already
> shipped.

## Why

The **Google "All Things Agentic" hackathon** (deadline 2026-08-31)
shipped a 7-stage LC/JC certificate pipeline into the sister repo
`~/dev/gemini_hackathon/`:

1. `extract_certification_criteria` — BAML extraction of the official
   NCCA criteria from the 5 policy PDFs.
2. `decompose_outcomes` — split the learner's LO codes.
3. `extract_exam_paper` + `extract_marking` — pull exam papers.
4. `search_official` — RAG over the 5 NCCA PDFs.
5. `generate_certificate_background` — Imagen3 image generation.
6. `compose_certificate` — PIL: background + text overlay + seal.
7. `save_to_provenance` — Firestore + the mastery-vector store.

This phase ships the OSS-first version into `cianfhoghlaim/`
(per operator direction 2026-09-01 — OSS-first, GCP-first stays
in the sister repo). The OSS replacement swaps Imagen3 → flux_schnell
and Firestore → Convex.

## What was shipped

### §1 — Author the canonical certificate types (1 file)

- **§1.1** `meaisinfhoghlaim/certificate/types.py` — 4 dataclasses
  (CertificationCitation + CertificationCriteria +
  CertificateOutcomeRecord + CertificateRecord).

### §2 — Author the canonical certificate rubric (1 file)

- **§2.1** `meaisinfhoghlaim/certificate/rubric.py` — the asset-
  comparison rubric (SSIM proxy + 2 coverage checks).
  - `NCCA_AWARD_DESCRIPTORS` (5 canonical)
  - `NCCA_KEY_COMPETENCIES` (6 with Staying Well)
  - `check_award_descriptor_coverage(vocabulary) -> (covered, total)`
  - `check_key_competency_coverage(competencies) -> (covered, total)`
  - `compute_ssim(image_b64, reference_b64) -> float` (perceptual-hash
    proxy; no scikit-image required)

### §3 — Author the 7-stage pipeline (1 file)

- **§3.1** `meaisinfhoghlaim/certificate/pipeline.py` — the orchestrator
  + 7 stage functions + the stdlib fallback for the background
  image generation (no PIL required).
  - `extract_certification_criteria(pdfs, subject, stage)` — Stage 1
  - `decompose_outcomes(subject, lo_codes)` — Stage 2
  - `extract_exam_paper(subject, year, level)` — Stage 3
  - `search_official(query, pdfs, top_k)` — Stage 4
  - `generate_certificate_background(subject, stage)` — Stage 5
  - `compose_certificate(background, title, subtitle, ...)` — Stage 6
  - `save_to_provenance(certificate, convex_client)` — Stage 7
  - `run_certificate_pipeline(learner_id, name, subject, ...)` —
    the orchestrator

### §4 — Author the canonical certification BAML (1 file)

- **§4.1** `baml_src/british_isles/ireland/education/certification.baml`
  - 3 canonical enums: `NCCACertificationStage` (5 stages) +
    `NCCAAwardDescriptor` (5 levels) + `NCCAKeyCompetency` (6 incl.
    Staying Well)
  - 2 output classes: `CertificationCitation` + `NCCAPolicyCriteria`
  - 1 function: `ExtractNCCAPolicyCriteria(pdf_text, subject_slug, stage)`
  - 1 BAML test block

### §5 — Author the NCCA policy PDF placeholder (1 file)

- **§5.1** `data/ireland/ncca_policy/README.md` — documents the 5
  canonical NCCA policy PDFs that ground every certificate. The
  actual PDFs are downloaded by `dlt_pipelines/ireland/ncca_policy.py`.

### §6 — Author the 7-test integration suite (1 file)

- **§6.1** `tests/test_phase7_certificate_pipeline.py` — 7 tests:
  - test_phase7_certificate_types_importable
  - test_phase7_certificate_rubric_ncca_constants
  - test_phase7_certificate_rubric_coverage_checks
  - test_phase7_certificate_pipeline_stages_importable
  - test_phase7_search_official_returns_citations
  - test_phase7_generate_certificate_background_stdlib
  - test_phase7_baml_function_reachable

### §7 — Regenerate baml_client (1 action)

- **§7.1** `uv run baml-cli generate --from baml_src` —
  regenerated `baml_client/` (14 files). The new
  `ExtractNCCAPolicyCriteria` function is reachable from runtime.

### §8 — Spec delta to `agent-memory-systems` (1 file)

- **§8.1** `openspec/changes/2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1/specs/agent-memory-systems/spec.md`
  — adds 2 new Requirements:
    - "Certificate pipeline MUST cite at least one NCCA policy page per claim"
    - "Certificate pipeline MUST run 7 stages end-to-end (OSS-first)"

## Impact

- **Audience:** every Cianfhoghlaim learner (LC + JC) who completes
  a learning journey.
- **Scope:** 6 new files (~800 LOC) + 1 BAML file.
- **LOC delta:** +~850.
- **Risk:** LOW — additive; the existing 7-stage pipeline in the
  sister repo continues to work.
- **Reversibility:** full.

## Dependencies

`Blocked by (soft):`

- `2026-09-01-baml-regeneration-blocker-v1/` — Phase 0.5
  (BAML regeneration) shipped earlier today.

`Blocked by (hard):` none.

`Extends:`

- [`openspec/specs/agent-memory-systems/spec.md`](../../specs/agent-memory-systems/spec.md)
  — adds 2 Requirements to the canonical agent memory spec.

`Affected repos:` `cianfhoghlaim` (this repo only).

## Out of scope

- Wholesale copy of `gemini_hackathon/gemini_hackathon/certificate/`
  — lifted selectively per the operator's earlier directive
  (deeply-per-sister-repo customisation, NOT wholesale copies).
- GCP-first certificate pipeline (Imagen3 + Firestore) — stays
  in the sister repo per the OSS-first posture.
- Real PDF generation — Phase 7 returns PNG bytes for both the
  PNG and PDF fields (the GCP-first version uses ReportLab for
  real PDF generation).
- Pil/Pillow integration for the compositor — Phase 7 uses a
  pure-stdlib PNG gradient as the fallback.

## Quality gates (ALL PASSED)

```bash
uv run openspec validate 2026-09-01-cianfhoghlaim-nua-certificate-pipeline-v1 --strict  ✅
uv run pytest tests/test_phase7_certificate_pipeline.py -v                                ✅ 7 passed
uv run pytest tests/test_adk_subject_actions.py tests/test_phase7_certificate_pipeline.py -v  ✅ 18 passed
uv run python -c "from baml_client.baml_client.sync_client import b; print(b.ExtractNCCAPolicyCriteria)"  ✅
```

---

*Last updated by build subagent at 2026-09-01.*