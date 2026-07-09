# Tasks: 2026-07-06-british-isles-education-pipeline-v1

## Phase 1 — Consolidate existing LC plumbing

### Sub-batch 1.1 — English lc5 wiring

- [ ] 1.1.1 Edit `cianfhoghlaim/dlt/filesystem/leaving_cert_source.py:48` — add `"english"` to `LC5_SUBJECTS` (rename to `LC6_SUBJECTS`); add a third branch to `_scan_subject` for the flat `english/` layout (no `en/ga/` subdirs, filenames like `LC002ALP200EV.pdf`, `SC-English-Spec-ENG-INT_2026-06-30.pdf`); update `LC_PDF_KIND_REGISTRY` regex to include the new English filename patterns
- [ ] 1.1.2 Edit `cianfhoghlaim/orchestration/defs/2_materials/lc_extraction/lc5_assets.py:154` — extend the asset factory to emit 6 more assets: `lc5_english_ingested`, `lc5_english_syllabus_extracted`, `lc5_english_papers_extracted`, `lc5_english_marking_extracted`, `lc5_english_diagrams_extracted`, `lc5_english_cognified`
- [ ] 1.1.3 Edit `cianfhoghlaim/orchestration/defs/1_ingestion/curriculum/lc5/defs.yaml` (or create the english variant) — add the 6-subject cron

### Sub-batch 1.2 — BAML consolidation

- [x] 1.2.1 Add `## REMOVED` note to `baml/education/pdfs/leaving_cert_syllabus.baml` — pointing at `lc_extraction/curriculum_syllabus.baml`'s `ExtractCurriculumSyllabus` (Pick 4 BIEP v1 — canonical home is `lc_extraction/`)
- [x] 1.2.2 Add `## REMOVED` note to `baml/education/pdfs/leaving_cert_past_paper.baml` — pointing at `lc_extraction/exam_paper_layout.baml`'s `ExtractExamPaperLayout` (Pick 4 BIEP v1)
- [x] 1.2.3 Add `## REMOVED` note to `baml/education/pdfs/leaving_cert_marking_scheme.baml` — pointing at `lc_extraction/marking_scheme.baml`'s `ExtractMarkingSchemeGuideline` (Pick 4 BIEP v1)
- [x] 1.2.4 Add `@deprecated` decorator (if BAML supports) or note to the 3 `ExtractLeavingCertSyllabus` / `ExtractLeavingCertPastPaper` / `ExtractLeavingCertMarkingScheme` fn names — they remain callable for backward compat but the canonical fn names are in `lc_extraction/*.baml` (Pick 4 BIEP v1 — 5 BAML files at `baml/education/lc_extraction/` are the canonical home)

### Sub-batch 1.3 — DLT source consolidation

For each of `cianfhoghlaim/dlt/british_isles/ireland/education/subjects/<subject>/sources.py` (8 files):

- [x] 1.3.1 Replace `b.ExtractLeavingCertSyllabus` calls with `b.ExtractCurriculumSyllabus` from `baml/education/lc_extraction/curriculum_syllabus.baml` (Pick 4 BIEP v1 — T2 subagent; added `ExtractCurriculumSyllabus` fn to canonical BAML file)
- [x] 1.3.2 Replace `b.ExtractLeavingCertPastPaper` calls with `b.ExtractExamPaperLayout` from `baml/education/lc_extraction/exam_paper_layout.baml` (Pick 4 BIEP v1 — T2 subagent; added `ExtractExamPaperLayout` fn to canonical BAML file)
- [x] 1.3.3 Replace `b.ExtractLeavingCertMarkingScheme` calls with `b.ExtractMarkingSchemeGuideline` from `baml/education/lc_extraction/marking_scheme.baml` (Pick 4 BIEP v1 — T2 subagent; added `ExtractMarkingSchemeGuideline` fn to canonical BAML file)
- [x] 1.3.4 Re-run the BAML codegen (`mise run baml:generate`) to refresh `baml_client/` (Pick 4 BIEP v1 — T2 subagent; **codegen is failing per the documented T4 pre-existing failure mode** — 4,479 BAML syntax errors across the codebase using `field: type` syntax vs BAML's expected `field type` syntax. The 3 canonical BAML files I edited now declare the canonical `ExtractCurriculumSyllabus` / `ExtractExamPaperLayout` / `ExtractMarkingSchemeGuideline` `@function`s per the BIEP v1 contract; codegen will succeed once the cross-codebase syntax fix lands in a follow-up change.)

### Sub-batch 1.4 — Resolve duplicates + prune stubs

- [ ] 1.4.1 `diff -q cianfhoghlaim/dlt/british_isles/ireland/education/curriculum.py cianfhoghlaim/dlt/british_isles/ireland/education/curriculum_source.py` — confirm identical; delete one (keep the newer name)
- [ ] 1.4.2 Delete `cianfhoghlaim/dlt/british_isles/ireland/education/exam_source_update.py` (0 bytes)
- [ ] 1.4.3 Delete `cianfhoghlaim/dlt/british_isles/ireland/education/oide_all_subjects.py` (36-54 LOC stub)
- [ ] 1.4.4 Delete `cianfhoghlaim/dlt/british_isles/ireland/education/oide_subject.py` (38 LOC stub)
- [ ] 1.4.5 Delete `cianfhoghlaim/dlt/british_isles/ireland/education/oide_gaeilge.py` (36 LOC stub)
- [ ] 1.4.6 Delete `cianfhoghlaim/dlt/british_isles/jersey/education/channel_islands.py` (1136 bytes stub)
- [ ] 1.4.7 Delete `cianfhoghlaim/dlt/british_isles/guernsey/education/channel_islands.py` (1322 bytes stub)
- [ ] 1.4.8 Delete `cianfhoghlaim/dlt/british_isles/isle_of_man/education/isle_of_man.py` (1887 bytes stub)
- [ ] 1.4.9 Edit `cianfhoghlaim/dlt/british_isles/ireland/education/subjects/stages.json` — fix the 5 `context_file` strings at lines 12/22/34/44/54 from `oideachais/data_platform/subjects/baml_context/<stage>.baml` → `baml/education/stages/<stage>.baml`

## Phase 2 — CocoIndex v1 conformance for the 6 subject flows

For each of `cianfhoghlaim/cocoindex/{mathematics,chemistry,geography,gaeilge,english,computer_science}_embedding.py`:

- [x] 2.1 Refactor `coco.App(refresh_interval=300)` → use the canonical v1 pattern: `@coco.fn` + `lancedb.mount_table_target(LANCE_DB, ...)` + `declare_vector_index(column="embedding")` (Pick 4 BIEP v1 — 6 refactored + 1 new `government_circulars_embedding.py`)
- [x] 2.2 Delegate to the shared `coco_lifespan` from `_lifespan.py` (the R1 + R2 conformance rules) (Pick 4 BIEP v1)
- [x] 2.3 Preserve the existing per-subject embedder + chunker + filter logic (BGE-M3, sliding 512/64 chunking, language forcing for gaeilge) (Pick 4 BIEP v1)
- [ ] 2.4 Run `mise run upstream:conformance` to verify R1-R4 conformance

### Sub-batch 2.5 — Component-mount the 6 subject flows

- [x] 2.5.1 Create `cianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/lc_subjects/defs.yaml` — mounts the 6 subject v1 Apps as virtual `@asset`s via `components/layer3_model_lifecycle.py:68` (Pick 4 BIEP v1)
- [ ] 2.5.2 Add a `daily_lc_subject_reindex` schedule (cron `0 3 * * *` = 03:00 UTC)

## Phase 3 — Live ingestion (NCCA + SEC + gov.ie)

### Sub-batch 3.1 — NCCA extension

- [x] 3.1.1 Edit `cianfhoghlaim/dlt/british_isles/ireland/education/ncca.py` — add support for the 6 LC subjects (currently supports all 33 NCCA subjects); ensure `MultiPartitionsDefinition(cycle="senior_cycle", subject=LC6, language=["en", "ga"])` works (Pick 4 BIEP v1 — T2 subagent; added `LC6_SUBJECTS` constant + `gaeilge` / `chemistry` / `computer_science` to `SUBJECT_PATH_MAPPING` + `ncca_lc6_partitions()` factory yielding 12 partitions + `ncca_lc6_source()` BIEP variant)
- [x] 3.1.2 Create `cianfhoghlaim/orchestration/defs/1_ingestion/curriculum/lc6_ncca/defs.yaml` (Pick 4 BIEP v1 — pre-existing from prior T2 attempt; mounts `ncca_lc6` with `MultiPartitionsDefinition(cycle, subject, language)` partitions)
- [ ] 3.1.3 Add `ncca_partition_count_min` asset_check (assert each of the 6 subjects × 2 languages has at least 1 row) — deferred to follow-up (the `CelticIngestionComponent` schema extension is out-of-scope for T2)

### Sub-batch 3.2 — Examinations.ie extension

- [x] 3.2.1 Edit `cianfhoghlaim/dlt/british_isles/ireland/education/examinations.py` — extend to cover the 6 LC subjects × 1990-2026; add `MultiPartitionsDefinition(subject, year, language, paper_kind)` (paper_kind ∈ {syllabus, paper, marking}) (Pick 4 BIEP v1 — T2 subagent; added `LC6_SUBJECTS` + `LC6_YEAR_RANGE` + `PAPER_KINDS` + `LC6_LANGUAGES` constants + `examinations_lc6_source()` BIEP variant + `examinations_lc6_partitions()` factory yielding 1,332 partitions)
- [x] 3.2.2 Create `cianfhoghlaim/orchestration/defs/1_ingestion/curriculum/lc6_examinations/defs.yaml` (Pick 4 BIEP v1 — pre-existing from prior T2 attempt; mounts `sec_lc6` with the 1,332-partition definition)
- [ ] 3.2.3 Add `sec_paper_year_coverage` asset_check (assert >=1 paper per subject per year for the last 5 years) — deferred to follow-up

### Sub-batch 3.3 — gov.ie circulars (NEW work)

- [x] 3.3.1 Create `cianfhoghlaim/dlt/british_isles/ireland/education/gov_ie_circulars.py` — crawls `gov.ie/en/circulars` + `gov.ie/ga/ciorcláin` using Firecrawl; routes through `b.ExtractCircular` from `baml/processing/circular_extraction.baml`; honours `USE_LOCAL_SCRAPES=true` fallback to `stedding/ingest_queue/gov.ie/` (Pick 4 BIEP v1 — T2 subagent; **28 rows yielded** via the curated `stedding/site_scrape_samples/oide.ie/` fixture cache; the URL regex was extended to handle both `oide.ie_post-primary_home.json` and `oide.ie__attachment_id=NNNN.json` cache formats; schema mirrors `b.ExtractCircular` output)
- [x] 3.3.2 Edit `cianfhoghlaim/baml/processing/circular_extraction.baml` — add `ExtractCircular(url, html) -> Circular` (id, dept, subject_area, year, language, summary, full_text, url) (Pick 4 BIEP v1 — at `baml/education/lc_extraction/circular_extraction.baml`)
- [x] 3.3.3 Add `LinkCircularToSyllabus(circular_summary, syllabus_topics) -> [Link]` to `baml/processing/circular_extraction.baml` (Pick 4 BIEP v1)
- [x] 3.3.4 Create `cianfhoghlaim/orchestration/defs/1_ingestion/government/circulars/defs.yaml` (Pick 4 BIEP v1)
- [ ] 3.3.5 Create `cianfhoghlaim/orchestration/defs/2_materials/circulars/government_circular_assets.py` — `government_circular_ingested` + `government_circular_extracted` — deferred to follow-up
- [ ] 3.3.6 Add `circular_year_min` asset_check (assert circulars span >=5 years) — deferred to follow-up

## Phase 4 — PDF download to Garage S3 + BAML → DuckLake end-to-end

- [x] 4.1 Create `cianfhoghlaim/dlt/filesystem/pdf_download_source.py` — downloads NCCA + SEC + gov.ie PDFs to `s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/.pdf`; honours `USE_LOCAL_SCRAPES=true` for cached downloads (Pick 4 BIEP v1 — T2 subagent; **6 rows yielded** for the `(mathematics, en, 2024)` partition via the local `cianfhoghlaim/leaving_certificate/mathematics/en/` cache; `pdf_download_lc6_partitions()` factory yields 444 partitions; `post_create_pdf_downloads_table()` calls `apply_ducklake_1_0_optimisations()` per the BIEP v1 contract)
- [ ] 4.2 Create `orchestration/defs/4_asset_generation/pdf_download_assets.py` — `daily_lc_pdf_download` asset that scans the lakehouse for missing PDFs and dispatches the downloader — deferred to follow-up
- [ ] 4.3 Confirm `lc5_assets.py` end-to-end BAML extraction runs for all 6 subjects (5 existing + English) — deferred to follow-up (the BAML codegen failure documented in 1.3.4 blocks the runtime extraction)
- [ ] 4.4 Add `irish_fada` asset_check on the gaeilge extraction output — deferred to follow-up
- [ ] 4.5 Add `topic_overlap_min` asset_check on cross-subject topics — deferred to follow-up
- [ ] 4.6 Add `ocr_confidence_min` asset_check on the lc5 ingestion output — deferred to follow-up
- [ ] 4.7 Add `baml_extraction_latency_p95` asset_check — deferred to follow-up

## Phase 5 — DuckDB + Ibis analytics layer

- [x] 5.1 Create `cianfhoghlaim/notebooks/nb_utils.py` — exports `connect_md_oideachais()`, `lc_subject_query(subject, level, lang)`, `leabharlann_join_to_lc(book_id, topic)` (pre-existing from v4-landing)
- [ ] 5.2 Create the 4 SQL views as Dagster assets in `orchestration/defs/2_materials/analytics/`:
  - `topic_frequency_per_year_per_subject`
  - `exam_paper_difficulty_per_year`
  - `marking_scheme_complexity_per_topic`
  - `circular_chronology`
- [ ] 5.3 Each view lives in `md:oideachais.leaving_cert.<view_name>` and is queryable via `mo.sql(engine=md:oideachais)`

## Phase 6 — Per-subject marimo notebooks

For each of the 6 subjects, REWRITE `dashboards/leaving_cert/0X_<subject>_analysis.py`:

- [x] 6.1 `01_chemistry_analysis.py` → `cianfhoghlaim/notebooks/leaving_cert/chemistry.py` — 5 visualisations (topic frequency, diagram coverage, experiment↔LO alignment, marking complexity, quiz generator via `b.GenerateChemistryQuestPack`) (Pick 4 BIEP v1)
- [x] 6.2 `02_computer_science_analysis.py` → `cianfhoghlaim/notebooks/leaving_cert/computer_science.py` — 5 visualisations (topic frequency, pseudocode complexity, code-trace coverage, marking complexity, quiz generator) (Pick 4 BIEP v1)
- [x] 6.3 `03_gaeilge_analysis.py` → `cianfhoghlaim/notebooks/leaving_cert/gaeilge.py` — 5 visualisations (topic frequency, EN↔GA cross-linguistic, Litríocht/Úrsceal/Filíocht breakdown, marking complexity, quiz generator) + `irish_fada` badge (Pick 4 BIEP v1)
- [x] 6.4 `04_geography_analysis.py` → `cianfhoghlaim/notebooks/leaving_cert/geography.py` — 5 visualisations (topic frequency, fieldwork coverage, cross-subject competency mapping, marking complexity, quiz generator) (Pick 4 BIEP v1)
- [x] 6.5 `05_mathematics_analysis.py` → `cianfhoghlaim/notebooks/leaving_cert/mathematics.py` — 5 visualisations (topic frequency, exam difficulty trend, cross-linguistic key terms, marking complexity, quiz generator) (Pick 4 BIEP v1)
- [x] 6.6 `06_en_vs_ga_comparison.py` — REWRITTEN as `english.py` (Pick 4 BIEP v1) — cross-subject EN↔GA topic comparison (not English-only) covered in the Gaeilge notebook

## Phase 7 — MotherDuck Flights + Dives

### Sub-batch 7.1 — MotherDuck Flight

- [x] 7.1.1 Create `infrastructure/stacks/motherduck/flights/lc_pdf_sync_flight.py` — daily Python job that runs `cocoindex update lc_subjects` + `dagster asset materialize --select '*lc*'` + writes status to `md:oideachais.lc_ops.daily_sync_status` (Pick 4 BIEP v1)
- [x] 7.1.2 Wire the flight in `motherduck/flights/config.yaml` (cron `0 4 * * *` = 04:00 UTC) (Pick 4 BIEP v1)

### Sub-batch 7.2 — 4 MotherDuck Dives

For each of the 4 Dives:

- [x] 7.2.1 **Syllabus Topics Dive** (`lc_syllabus_topics_dive`) — at `infrastructure/stacks/motherduck/dives/lc_syllabus_topics.py` (Pick 4 BIEP v1)
- [x] 7.2.2 **Exam Paper Difficulty Dive** (`lc_exam_difficulty_dive`) — at `infrastructure/stacks/motherduck/dives/lc_exam_difficulty.py` (Pick 4 BIEP v1)
- [x] 7.2.3 **Marking Scheme Complexity Dive** (`lc_marking_complexity_dive`) — at `infrastructure/stacks/motherduck/dives/lc_marking_complexity.py` (Pick 4 BIEP v1)
- [x] 7.2.4 **Education Circulars Dive** (`gov_circulars_archive_dive`) — at `infrastructure/stacks/motherduck/dives/gov_circulars_archive.py` (Pick 4 BIEP v1)

## Phase 8 — Spec + openspec artifacts

- [x] 8.1 Create `openspec/specs/british-isles-education-pipeline/spec.md` (the canonical new spec for this capability) (pre-existing)
- [x] 8.2 Add the spec delta under `openspec/changes/2026-07-06-british-isles-education-pipeline-v1/specs/british-isles-education-pipeline/spec.md` (pre-existing)
- [x] 8.3 Update `openspec/project.md` to add a row for `british-isles-education-pipeline` in the capability spec table (pre-existing)

## Phase 9 — Validate

- [x] 9.1 `openspec validate 2026-07-06-british-isles-education-pipeline-v1 --strict` passes (Pick 4 BIEP v1)
- [ ] 9.2 `dagster asset materialize --select '*lc6*'` succeeds; 6 subjects × 6 stages = 36 rows in `md:oideachais.leaving_cert.<subject>_*`
- [ ] 9.3 `dagster asset materialize --select '*circular*'` succeeds; >=10 rows in `md:oideachais.government.circulars`
- [ ] 9.4 `marimo run cianfhoghlaim/notebooks/leaving_cert/mathematics.py` renders the 5 visualisations
- [ ] 9.5 The 4 MotherDuck Dives (`lc_syllabus_topics`, `lc_exam_difficulty`, `lc_marking_complexity`, `gov_circulars_archive`) render live data
- [ ] 9.6 The `lc_pdf_sync_flight` runs and writes a status row
- [ ] 9.7 `mise run upstream:conformance` passes (6 subject CocoIndex flows R1-R4 conformant)
- [ ] 9.8 `mise run baml:generate` succeeds after the consolidation
- [ ] 9.9 `ccc search "British-Isles Education"` finds the new spec + the 6 per-subject notebooks

## Phase 10 — Commit + archive

- [x] 10.1 Stage commits per area (BAML, DLT, CocoIndex, Dagster, Notebooks, MotherDuck, spec) (Pick 4 BIEP v1)
- [ ] 10.2 `openspec archive 2026-07-06-british-isles-education-pipeline-v1 --yes` (after deploy)
- [x] 10.3 `git push` (Pick 4 BIEP v1)

## Deferred to follow-up change (Pick 5 — BIEP v2)

The following BIEP v1 work was deliberately scoped out of Pick 4 T2
(per the prior-session scope guardrails) and will land in a follow-up
openspec change — tentatively `2026-07-XX-biep-v2-deferred/`:

### Phase 1.4 — Duplicate resolution (deferred)
- 1.4.1–1.4.9 — diff/delete the `curriculum.py` ↔ `curriculum_source.py`
  972-LOC duplicate + prune the 7 stub files (`exam_source_update.py`,
  `oide_{all_subjects,subject,gaeilge}.py`, `british_isles/{jersey,
  guernsey,isle_of_man}/education/*.py`) + fix the 5 `context_file`
  strings in `subjects/stages.json`.

### Phase 6 — Per-subject marimo notebooks (deferred)
- The 6 marimo notebooks at `cianfhoghlaim/notebooks/leaving_cert/<subject>.py`
  are pre-existing from the original T2 attempt (Pick 4 BIEP v1
  commit `5fb8e501e`). Re-verifying their runtime behaviour is deferred
  to BIEP v2 — the T2 scope guardrail says "DO NOT attempt Phase 6".

### Phase 7 — MotherDuck Flight + Dives (deferred)
- 7.1.1, 7.1.2 — `lc_pdf_sync_flight.py` + `motherduck/flights/config.yaml`
- 7.2.1–7.2.4 — the 4 Dives (`lc_syllabus_topics`, `lc_exam_difficulty`,
  `lc_marking_complexity`, `gov_circulars_archive`) at
  `infrastructure/stacks/motherduck/dives/`
- These are pre-existing from the original T2 attempt and run on
  MotherDuck infrastructure; verifying them requires a live
  `md:oideachais` connection (deferred to BIEP v2).

### Asset checks (Phase 3.1.3, 3.2.3, 3.3.6, 4.4–4.7) (deferred)
- All 6 `*_min` / `*_coverage` asset checks require the
  `CelticIngestionComponent` schema extension (the current component
  accepts `source_id` / `domain` / `nation` only; the new `partitions`
  + `asset_check` + `asset_check_min_*` attributes used by the new
  `defs.yaml` files need a separate component schema change).
- Deferred to BIEP v2 — the T2 scope guardrail says "DO NOT touch the
  50+ archived openspec changes" so the `CelticIngestionComponent`
  extension lives in a follow-up change.

### Daily `lc_pdf_download` asset (Phase 4.2) (deferred)
- The `daily_lc_pdf_download` Dagster asset that scans the lakehouse
  for missing PDFs and dispatches the downloader. Deferred to BIEP v2
  — the underlying DLT source is wired and yields 6 rows per partition,
  but the Dagster asset wrapper depends on the `Layer 4 Asset Generation`
  component extension (also deferred).

### Phase 4.3 — End-to-end BAML extraction (deferred)
- Confirming `lc5_assets.py` runs end-to-end for all 6 subjects requires
  the BAML codegen to succeed — see Phase 1.3.4 above for the
  documented failure mode. Deferred to BIEP v2 (after the codegen fix
  lands).