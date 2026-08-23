# Tasks — 2026-08-23-uog-personal-archive-tertiary-modules-v1

## WS1 — openspec contract (this change)

- [x] `proposal.md`
- [x] `tasks.md`
- [ ] 1 sub-spec: `specs/cianfhoghlaim-personal-archive-typed-modules/spec.md`
  (with `### Requirement` + `#### Scenario` blocks for the 14
  requirement areas: filesystem scan + module-code detection;
  provenance detection; HTR routing; per-artefact BAML extraction;
  per-assignment + per-question BAML extraction; per-topic BAML
  extraction; per-code-cell BAML extraction; per-lecture-reading-list
  BAML extraction; transcript BAML extraction; typed DuckLake
  tables; 4 CocoIndex v1 Apps; 10 Cognee typed edges; marimo
  8-tab BIEP notebook + CS4423 worked-example sidebar; Convex +
  CopilotKit + Genie + ADK chat surface + transferability)

## WS2 — BAML schema

- [ ] `baml_src/british_isles/ireland/education/university/personal_archive_extraction.baml`
  - 3 new enums (`ArtefactProvenance`, `ArtefactKind`, `HTRBackend`)
  - 10 new classes (`UoGArtefactProvenanceMeta`,
    `UoGPersonalArchiveArtefact`, `UoGQuestion`, `UoGAssignment`,
    `UoGTopic`, `UoGReadingItem`, `UoGCodeCell`, `UoGCaMark`,
    `StudentTranscriptRow`, `UoGModuleSummary`)
  - 7 new functions (`ExtractUoGPersonalArchiveArtefact`,
    `ExtractUoGAssignment`, `ExtractUoGTopicList`,
    `ExtractUoGLectureReadingList`, `ExtractUoGCodeCell`,
    `ExtractStudentTranscript`, `BuildModuleSummary`)
  - All routed through `ExtractEn`
  - All functions have `catch_all` blocks returning safe defaults

## WS3 — DLT filesystem source

- [ ] `dlt_sources/filesystem/uog_personal_archive.py`
  - `@dlt.source(name="uog_personal_archive")` with **8** `@dlt.resource`s:
    - `personal_archive_artefacts` (merge on `artefact_id + content_hash`; partition: institution, module_code, artefact_kind, academic_year, artefact_provenance)
    - `personal_archive_assignments` (merge on `assignment_id + content_hash`; partition: module_code, assignment_number)
    - `personal_archive_questions` (merge on `question_id`; partition: module_code, question_id)
    - `personal_archive_topics` (merge on `topic_id`; partition: topic_category)
    - `personal_archive_reading_lists` (merge on `reading_id`; partition: module_code)
    - `personal_archive_code_cells` (merge on `cell_id`; partition: module_code, notebook_path)
    - `personal_archive_ca_marks` (merge on `ca_id`; partition: module_code)
    - `student_transcripts` (merge on `student_id + module_code + academic_year`; partition: student_id, programme_code, academic_year)
  - `_DEFAULT_PERSONAL_ARCHIVE_PATH` env-driven default
  - `_classify_file(path) -> (ArtefactKind, ArtefactProvenance, module_code | None, assignment_number | None)`
  - Module-code detection regex `[A-Za-z]{2,4}\d{3,4}` matched against any path component
  - Artefact-kind detection from filename + extension patterns
  - Provenance detection from path tokens
  - `compute_file_hash` from `dlt_sources/filesystem/_scanner.py`
  - Yield one placeholder `status="skipped_no_real_files"` row per resource when the personal archive path doesn't exist or is empty

## WS4 — HTR routing (helper module)

- [ ] `dlt_sources/filesystem/_htr_ensemble.py`
  - `def route_htr(file_path: Path, pymupdf_chars_per_page: float) -> tuple[HTRBackend, float]`
    - `.pages` / `.heic` → `MULTI_VLM_CONSENSUS`, 0.5
    - filename contains `handwritten` / `goodnotes` / `apple_pencil` → `MULTI_VLM_CONSENSUS`, 0.5
    - pymupdf_chars_per_page < 100 → `MULTI_VLM_CONSENSUS`, 0.4
    - else → `PYMUPDF_TYPED`, 0.95
  - `def htr_extract_pages(file_path: Path, backend: HTRBackend) -> tuple[str, float]`
    - For `PYMUPDF_TYPED` → `dlt_sources.british_isles.ireland.education._pdf_text.extract_pdf_text`
    - For `MULTI_VLM_CONSENSUS` → defer-import from
      `machine_learning.ocr.vlm_finetune_comparison` (or
      `meaisinfhoghlaim.ocr.ensemble.ensembled_extractor.EnsembledExtractor`
      fallback) and run the 4-VLM ensemble (nougat + olmocr-2-7b +
      CogVLM + gemma-3) with majority-vote consensus on extracted
      equations; fallback to nougat if all 4 disagree on >30%

## WS5 — DuckLake destination

- [ ] `dlt_sources/_lakehouse/personal_archive_destinations.py`
  - `register_personal_archive_tables(con, schema_name="cianfhoghlaim.education.ie") -> None`
  - `CREATE TABLE IF NOT EXISTS` for all 9 tables:
    `personal_archive_artefacts`, `personal_archive_assignments`,
    `personal_archive_questions`, `personal_archive_topics`,
    `personal_archive_reading_lists`, `personal_archive_code_cells`,
    `personal_archive_ca_marks`, `personal_archive_modules`,
    `student_transcripts`
  - Each table has its columns + a comment listing the partition keys
- [ ] Extend `dlt_sources/_lakehouse/destinations.py::get_destination()`
  - Accept `DUCKLAKE_DESTINATION` env var with values
    `local` | `motherduck` | `bonneagar`

## WS6 — CocoIndex v1 Apps (4 new apps)

- [ ] `cocoindex_flows/british_isles/ireland/education/university/personal_archive_embedding.py`
  - `UoGPersonalArchiveArtefactsApp` (BGE-M3 1024-d on `artefact_title + embedded_text + key_topics`)
  - `UoGPersonalArchiveQuestionsApp` (BGE-M3 1024-d on `question_text + my_answer_text + topic_tags`)
  - `UoGPersonalArchiveTopicsApp` (BGE-M3 1024-d on `topic_name + topic_category`)
  - `UoGPersonalArchiveLectureNotesApp` (BGE-M3 1024-d on `artefact_title + embedded_text`)

## WS7 — Cognee typed edges

- [ ] `scripts/graph_storage/cognify/rules/personal_archive_typed_edges.py`
  (created by the parallel subagent — NOT modified here)
- [ ] `scripts/graph_storage/cognify/rules/__init__.py`
  - Add `try/except ImportError` import of `personal_archive_typed_edges`
  - Wire into the cognify runner

## WS8 — Marimo 8-tab BIEP notebook

- [ ] `notebooks/15_personal_archive.py`
  - 8-tab BIEP notebook (Health / Filters / Materials / URL Health / Heatmap / Recent / Lance Search / SQL Console)
  - Sidebar: CS4423 worked-example (the worked-example the user wants in the thesis)
  - Uses `mo.sql(engine=md:cianfhoghlaim)` primary + local DuckDB fallback

## WS9 — Convex + CopilotKit + Genie + ADK chat surface

- [ ] `web/apps/oideachais-web/convex/schema.ts` — add `personal_archive_artefacts`, `personal_archive_questions`, `student_transcripts` tables + the `chatWithPersonalArchive` action
- [ ] `agents/adk/personal_archive_module_assistant.py` — the ADK module assistant
- [ ] `web/apps/oideachais-web/app/personal-archive/page.tsx` — the CopilotKit chat UI
- [ ] `observability/dashboards/personal_archive.json` — the Genie dashboard

## WS10 — Dagster assets

- [ ] `orchestration/defs/uog_personal_archive.py` (created by parallel subagent — NOT modified here)
- [ ] `orchestration/definitions.py` — register the asset group

## WS11 — Transferability

- [ ] `.env.example` — add the 9 `UNIVERSITY_PERSONAL_ARCHIVE_*` + `DUCKLAKE_DESTINATION` env vars
- [ ] `dlt_sources/british_isles/ireland/education/university/personal_archive/__init__.py`
- [ ] `dlt_sources/british_isles/ireland/education/university/personal_archive/uog_personal_archive_source.py`
  - `personal_archive_source(university_config: UniversityPersonalArchiveConfig) -> dlt.Source`
  - `UniversityPersonalArchiveConfig` Pydantic BaseModel with the 9 env-var fields
- [ ] `openspec/AGENTS.md` — insert the new spec in the priority table

## WS12 — Tests + observability + thesis figures

- [ ] `tests/personal_archive/` (4 modules: test_dlt_source.py, test_baml_extraction.py, test_cognee_edges.py, test_ducklake_destinations.py)
- [ ] `observability/dashboards/personal_archive.json` — Grafana dashboard for the 9 tables
- [ ] `figures/thesis/personal_archive_pipeline_chart.pdf` — the pipeline chart
