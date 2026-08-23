# 2026-08-23-uog-exam-papers-sso-v1

> Add an authenticated University of Galway exam-paper pipeline (DLT + BAML + Dagster + VLM).
> Part of the M.Sc. AI thesis: extend the existing K-12 (Leaving Cert / Junior Cycle) and
> public-tertiary (university-deep-extraction) pipelines to surface a *closed-corpus*
> subset of data — past exam papers locked behind the UoG Campus Identity SSO.

## Why

The Cianfhoghlaim platform already has:

- A **public** UoG deep-extraction pipeline
  (`openspec/changes/2026-07-15-cianfhoghlaim-university-deep-extraction-v1` /
  `dlt_sources/british_isles/ireland/education/_university_deep_factory.py`) that
  scrapes course catalogues, module lists, programmes, handbooks, and lecturer
  pages from `https://www.universityofgalway.ie`.
- An **SEC / Leaving Certificate** browser-automation pipeline
  (`dlt_sources/british_isles/ireland/education/sec_examinations_browser.py` +
  `bonneagar/stacks/browser/sruth_browser/tools/examinations_scraper.py`) that
  uses Stagehand to drive dropdowns on `https://www.examinations.ie`.
- A full **VLM extraction** layer
  (`baml_src/british_isles/ireland/education/university/mathematics_statistics_extraction.baml`
  + `machine_learning/ocr/vlm_finetune_comparison.py` registry of
  `glm-4.6v-flash / qwen3-vl / olmocr-2-7b / gemma-3`) and a Dagster
  `modal_curriculum_embeddings` pipeline on Modal T4 GPUs.

The **one surface still missing** is the UoG `exams` portal — the past-paper
index that the student sees after login at `auth.universityofgalway.ie` (which
sits behind Campus Identity SSO). This change adds the missing piece *as a
sealed-pipeline layer* that mirrors the existing patterns, so the rest of the
stack (BAML, CocoIndex, Cognee, marimo) gains feature-parity with Leaving
Certificate exam papers.

## What changes

| Layer | New artefact |
|---|---|
| Openspec contract | this change |
| Secret resolution | `bonneagar/stacks/browser/sruth_browser/core/secrets.py` (Infisical → `.env` → doc-only `op`) |
| Browser auth | `core/auth.py` Playwright persistent context + `UoGSsoLogin` |
| Browser backend ext. | `backends/selfhosted/cdp_backend.py` accepts `user_data_dir` + `storage_state_path` |
| Scraper | `tools/uog_exam_scraper.py` |
| DLT source | `dlt_sources/.../university/exam_papers/uog_exam_papers_source.py` |
| BAML schema | `baml_src/british_isles/ireland/education/university/uog_exam_paper_extraction.baml` |
| Dagster assets | `dlt_sources/.../university/exam_papers/uog_exam_assets.py` (5 assets) |
| VLM evaluation | `machine_learning/vlm/uog_exam_ocr.py` (4-VLM comparison on 20-paper gold set) |
| CocoIndex app | `core/cocoindex/uog_exam_embedding.py` `UoGExamPapersApp` (BGE-M3, 1024-d) |
| Cognee rule | `cognify/rules/uog_exam_cross_archive.py` (`UoGExamPaper-COVERS-UoGModuleDescriptor`) |
| Marimo notebook | `notebooks/_cianfhoghlaim/uog_exam_papers.py` (3 tabs) |

## Non-goals

- **GDPR / ethics approval.** Scraping authenticated content that the user
  already has permission to view is OK for thesis data; we will not redistribute
  the PDFs in this repo (they live under `downloads/uog_exam_papers/` which is
  in `.gitignore`). The thesis will cite UoG by name for source acknowledgement.
- **Generalising to every Irish university.** This change ships a single-tenant
  scraper for University of Galway. A follow-up change can lift the
  `UniversityDeepExtractionConfig` factory pattern (see
  `openspec/specs/cianfhoghlaim-university-deep-extraction/spec.md`) into a
  `UoGSsoConfig` Pydantic model if/when the same need surfaces elsewhere.
- **Live SSO in CI.** No CI runner will ever hold real credentials — the asset
  `uog_exam_login_health` is gated on `UoGSsoConfig.has_real_credentials()` and
  skips with `MaterializeResult(skipped)` in CI.

## Receipt of approver feedback

N/A — first proposal, awaiting reviewer @me (author) and @cairde-ai-tester.

