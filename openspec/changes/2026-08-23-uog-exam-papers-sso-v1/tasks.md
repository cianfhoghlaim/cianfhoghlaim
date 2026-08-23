# Tasks — 2026-08-23-uog-exam-papers-sso-v1

## WS0 — preflight

- [ ] Pick the working directory (`~/dev/kings_college_galway`) and verify
      the existing UoG deep-extraction tests still pass
      (`pytest dlt_sources/ tests/ -k "uog or university"`).
- [ ] Decide and pin the secret backend: **Infisical (self-hosted) →
      `.env` → doc-only `op`**.

## WS1 — openspec contract (this change)

- [x] `proposal.md`
- [x] `tasks.md`
- [ ] `specs/cianfhoghlaim-uog-exam-papers/spec.md` — 5 requirements + 12 scenarios
- [ ] `specs/cianfhoghlaim-uog-exam-papers/design/auth-credential-priority-chain.md`
      — explains why Infisical → `.env` → `op` and how the `Op` mention is doc-only

## WS2 — BAML schema

- [ ] `baml_src/british_isles/ireland/education/university/uog_exam_paper_extraction.baml`
      - classes: `UoGExamPaper`, `UoGSyllabusDescriptor`, `UoGLearningOutcome`,
        `UoGExamQuestionBloomTag`, `UoGSitting`, `UoGPaperFormat`,
        `UoGProvenanceKind`
      - functions: `ExtractUoGExamPaper(pdf_text)`, `ExtractUoGSyllabus(syllabus_pdf_text)`,
        `MapUoGExamQuestionsToLOs`, `ExtractUoGModuleCatalogueRow(html)`
- [ ] Reuse existing `ExamPaper`/`ExamSection`/`ExamQuestion` from
      `baml_src/british_isles/_cross/isles_education.baml` as a base for
      feature-parity comparison.

## WS3 — secret resolver

- [ ] `bonneagar/stacks/browser/sruth_browser/core/secrets.py`
      `class SecretsResolver` with `get(name) -> str | None`
      priority chain: Infisical (`INFISICAL_*`) → `.env` (`os.environ`) →
      log a one-line warning if `op` is detected (`OP_SERVICE_ACCOUNT_TOKEN`)
      so cloners aren't confused.
- [ ] Pydantic `UoGSsoConfig(BaseSettings)` with the same resolution chain
      for `student_id` + `student_password`.

## WS4 — browser auth

- [ ] `core/auth.py` — `UoGSsoLogin.login(page, secrets)`, persistent
      `user_data_dir`, `storage_state_path` re-use across runs.
- [ ] `backends/selfhosted/cdp_backend.py` — extend `initialize()` to accept
      `user_data_dir: Path | None` and `storage_state_path: Path | None`,
      threading the same kwargs through `BrowserBackend` base.
- [ ] `backends/selfhosted/stagehand_backend.py` — propagate the same kwargs.
- [ ] `exceptions.py` — add `UoGAuthExpired(BackendError)`.

## WS5 — scraper + DLT source

- [ ] `tools/uog_exam_scraper.py`
      - `UoGExamScraper` with `login`, `discover_module_codes(school_slug)`,
        `list_papers(module_code)`, `download(paper)`.
      - 4 sync wrappers (`uog_exam_papers_sync`, `uog_all_modules_sync`,
        `uog_exam_materials_sync`, `uog_examiner_reports_sync`).
- [ ] `dlt_sources/.../university/exam_papers/uog_exam_papers_source.py`
      - `@dlt.source(name="uog_exam_papers")`
      - 5 resources (papers, marking_schemes, model_solutions,
        supplementary_papers, all_exam_materials).
- [ ] `dlt_sources/.../university/exam_papers/uog_exam_assets.py`
      5 Dagster assets:
      1. `uog_exam_login_health` (asset-check style asset)
      2. `uog_exam_module_discovery` (`compute_kind="scrape"`)
      3. `uog_exam_papers_download` (`compute_kind="scrape"`)
      4. `uog_exam_papers_ocr_extract` (`compute_kind="baml"`)
      5. `uog_exam_los_map` (`compute_kind="baml"`)

## WS6 — VLM eval

- [ ] `machine_learning/vlm/uog_exam_ocr.py`
      `UoGExamVLMConfig`, paper→image-DPI→BAML-call wrapper.
- [ ] `dlt_sources/.../university/exam_papers/uog_exam_vlm_eval.py`
      new Dagster asset that runs 20 papers × 4 VLMs and logs to MLflow
      experiment `uog_vlm_exam_ocr`.

## WS7 — embeddings + graph + dashboard

- [ ] `core/cocoindex/uog_exam_embedding.py`
      `UoGExamPapersApp` (BGE-M3, 1024-d on `question_text + topic`).
- [ ] `cognify/rules/uog_exam_cross_archive.py`
      edge rule `UoGExamPaper-COVERS-UoGModuleDescriptor`.
- [ ] `notebooks/_cianfhoghlaim/uog_exam_papers.py`
      marimo with 3 tabs (M.Sc. AI past papers / All UoG schools / LO-coverage).

## WS8 — tests + observability

- [ ] `tests/uog_exam/` — fixtures + BAML round-trip + deterministic
      `exam_module_code_consistency` eval.
- [ ] `tests/uog_exam/test_secrets.py` — Infisical → `.env` priority order.
- [ ] `tests/uog_exam/test_uog_scraper.py` — Playwright mocked Stagehand.
- [ ] `@pytest.mark.opt_in` decorator for tests that gate on real credentials.

