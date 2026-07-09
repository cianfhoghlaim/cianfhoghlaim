# Change: 2026-07-06-british-isles-education-pipeline-v1

## Why

The Cianfhoghlaim platform's British-Isles Education pipeline is the
project's primary content domain — it is what the agent fleet, the
ducklake lakehouse, the CocoIndex v1 embeddings, the BAML extractions,
the MotherDuck Dives, and the leaving_certificate sample corpus all
serve. v1 brings the 6 priority Irish Leaving Certificate subjects
(Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science)
to a fully-functional, end-to-end-runnable pipeline, and adds
`gov.ie` education circulars as the cross-cutting ingestion surface.

The 2026-07-06 audit (`docs/audits/2026-07-06-drift-audit.md`) found that
5 of 6 subjects (maths, chem, geo, gaeilge, CS) already have working
`lc5_documents` DLT source + BAML extraction + CocoIndex flow + Dagster
assets (`orchestration/defs/2_materials/lc_extraction/lc5_assets.py:92-238`).
What v1 adds:

1. **English lc5 wiring** (the only subject missing from `lc5_documents`)
2. **BAML + DLT path consolidation** (the 2 parallel function families for
   the same 3 LC document kinds)
3. **CocoIndex v1 conformance** for the 6 subject flows (R4 violation —
   yields dicts instead of using `lancedb.mount_table_target`)
4. **`gov.ie` education circulars** DLT source + Dagster asset + MotherDuck
   Dive (genuine new work — no source exists today)
5. **Educational assets** generation (quizzes, diagrams) per subject
6. **MotherDuck Flights + Dives** for the analytics layer (4 new Dives
   for syllabus topics, exam paper difficulty, marking scheme complexity,
   education circulars)

The audit also confirmed the cross-nation BAML schema is already complete
(`baml/education/cross_nation/multi_nation_curriculum.baml`) — v1 lays the
Ireland-specific groundwork; **Scotland / Wales / Northern-England / Jersey /
Guernsey / IoM are out of scope for v1** and deferred to v2.

The end-state v1 capability: **a teacher (or student) can run
`mise run dagster:oideachais`, select the 6-subject pipeline, click
"Materialize all", and within minutes see:**

- All NCCA syllabuses + examinations.ie LC papers + marking schemes + gov.ie
  circulars for the 6 subjects downloaded to Garage S3
  (`s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<file>.pdf`)
- BAML-extracted structured data in DuckLake tables
  (`md:oideachais.leaving_cert.<subject>_syllabus`,
  `..._<subject>_papers`, `..._<subject>_marking`, `..._<subject>_circulars`)
- BGE-M3 embeddings in LanceDB (`oideachais.lc.<subject>.<level>_<lang>`)
- Cognee knowledge graphs (`oideachais_<subject>`)
- Graphiti bi-temporal episode streams per subject
- MotherDuck Dives showing topic frequency per year per subject,
  exam paper difficulty trends, marking scheme complexity, and the gov.ie
  circulars archive

## What changes

### B.1 Consolidate the existing LC plumbing

- **Wire English into lc5**: extend
  `cianfhoghlaim/dlt/filesystem/leaving_cert_source.py:48` to include
  `"english"` in `LC5_SUBJECTS`; add a third branch to `_scan_subject`
  for the flat `english/` layout (no `en/ga/` subdirs); extend the asset
  factory at `lc5_assets.py:154` to emit 5 more assets
  (`lc5_english_ingested`, `lc5_english_syllabus_extracted`,
  `lc5_english_papers_extracted`, `lc5_english_marking_extracted`,
  `lc5_english_diagrams_extracted`, `lc5_english_cognified`).
- **BAML consolidation**: fold the legacy
  `baml/education/pdfs/{leaving_cert_syllabus,leaving_cert_past_paper,leaving_cert_marking_scheme}.baml`
  into `baml/education/lc_extraction/{curriculum_syllabus,exam_paper_layout,marking_scheme}.baml`
  via ## REMOVED notes; mark the legacy trio as `@deprecated`.
- **DLT source consolidation**: migrate the 8
  `dlt/british_isles/ireland/education/subjects/<subject>/sources.py` files
  to call the canonical BAML fn names (`b.ExtractCurriculumSyllabus` etc.
  from `lc_extraction/*.baml`).
- **Resolve `curriculum.py` (972 LOC) vs `curriculum_source.py` (972 LOC)**
  duplicate in `dlt/british_isles/ireland/education/`.
- **Prune empty/stub DLT files**: `exam_source_update.py` (0 bytes),
  `oide_{all_subjects,subject,gaeilge}.py` (36-54 LOC),
  `british_isles/{jersey,guernsey,isle_of_man}/education/*.py` (1-2 KB stubs).
- **Fix `stages.json` legacy refs** at lines 12/22/34/44/54.

### B.2 CocoIndex v1 conformance for the 6 subject flows

For each of `cocoindex/{mathematics,chemistry,geography,gaeilge,english,computer_science}_embedding.py`:

- Refactor from manual `table.add()` yields to canonical v1 pattern
  using `@coco.fn` + `lancedb.mount_table_target(LANCE_DB, ...)` +
  `declare_vector_index(column="embedding")`.
- Delegate to the shared `coco_lifespan` from `_lifespan.py`
  (the R1 + R2 conformance rules).
- Preserve the existing per-subject embedder + chunker + filter logic.
- Add an asset in `orchestration/defs/3_model_lifecycle/cocoindex_v1/lc_subjects/defs.yaml`
  that runs `cocoindex update --all lc_subjects` on a daily cron.

### B.3 Live ingestion (NCCA + SEC + gov.ie)

- **Extend `dlt/british_isles/ireland/education/ncca.py`** to cover all 6
  LC subjects in EN + GA, with `MultiPartitionsDefinition(cycle, subject, language)`.
- **Extend `dlt/british_isles/ireland/education/examinations.py`** for LC
  papers + marking schemes per subject per year (1990-2026). Reuse the
  existing `curriculumonline_syllabi.py` partition style.
- **New `dlt/british_isles/ireland/education/gov_ie_circulars.py`** —
  crawls `gov.ie/en/circulars` and `gov.ie/ga/ciorcláin` using Firecrawl
  (or Crawl4AI as fallback), routes through `b.ExtractCircular` from
  `baml/processing/circular_extraction.baml`. Writes to
  `oideachais.government.circulars` DuckLake table with columns
  `(circular_id, dept, subject_area, year, language, summary, full_text, url)`.
- **Wire `stedding/ingest_queue/{ncca,examinations,gov.ie}/`** local scrapes
  cache as the `USE_LOCAL_SCRAPES=true` fallback.
- **Dagster defs.yaml**:
  - `orchestration/defs/1_ingestion/curriculum/lc6_ncca/defs.yaml`
    (the 6-subject NCCA partitions)
  - `orchestration/defs/1_ingestion/curriculum/lc6_examinations/defs.yaml`
    (the 6-subject SEC partitions)
  - `orchestration/defs/1_ingestion/government/circulars/defs.yaml`
- **Asset checks** on the new sources: `ncca_partition_count_min`,
  `sec_paper_year_coverage`, `circular_year_min`.

### B.4 PDF download to Garage S3 + BAML → DuckLake end-to-end

- **New `dlt/filesystem/pdf_download_source.py`** that downloads NCCA + SEC
  + gov.ie PDFs to `s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<filename>.pdf`.
  Honours `USE_LOCAL_SCRAPES=true` for cached downloads.
- **End-to-end BAML extraction**: `orchestration/defs/2_materials/lc_extraction/lc5_assets.py`
  already defines the 30 assets (5 subjects × 6 BAML stages); v1 adds
  English to make 36 total, plus 1 gov.ie circular asset per circular.
- **Asset checks** on the BAML outputs: `irish_fada` (gaeilge-only),
  `topic_overlap_min` (cross-subject), `ocr_confidence_min`,
  `baml_extraction_latency_p95`.

### B.5 DuckDB + Ibis analytics layer

- **SQL views** in `md:oideachais.leaving_cert`:
  - `topic_frequency_per_year_per_subject` (pivot of BAML topic extraction)
  - `exam_paper_difficulty_per_year` (weighted by marks + part complexity)
  - `marking_scheme_complexity_per_topic` (avg descriptors per topic)
  - `circular_chronology` (gov.ie circulars by dept + year + subject_area)
- **Shared `nb_utils.py`** at `cianfhoghlaim/notebooks/nb_utils.py` — exports
  `connect_md_oideachais()`, `lc_subject_query(subject, level, lang)`,
  `leabharlann_join_to_lc(book_id, topic)` — every per-subject notebook
  imports this.
- **DuckDB + LanceDB integration template** (the canonical
  `mo.sql(engine=md:oideachais)` SQL example) — added to `marimo` skill
  as part of the drift-cleanup change.

### B.6 Per-subject marimo notebooks

For each of the 6 subjects, REWRITE the existing
`dashboards/leaving_cert/<subject>_analysis.py` notebook (Phase 2.2 of the
drift-cleanup change handles the structural rewrite — v1 wires it to
live data + adds the British-Isles Education-specific visualisations):

- **Mathematics** (5 notebook cells):
  1. Topic frequency per year (line chart)
  2. Exam paper difficulty trend (bar chart)
  3. Cross-linguistic topic mapping (Gaeilge ↔ Mathematics key terms)
  4. Marking scheme complexity (heatmap)
  5. Asset generator: 10 quiz items per topic via
     `b.GenerateMathsQuestPack` from `baml/education/subjects/qpack_mathematics.baml`

- **Chemistry** (5 cells):
  1. Topic frequency per year
  2. Diagram extraction coverage (count of diagrams per PDF per topic)
  3. Experiment ↔ Learning Outcome alignment
  4. Marking scheme complexity
  5. Asset generator: `b.GenerateChemistryQuestPack`

- **Geography** (5 cells):
  1. Topic frequency per year (Physical / Regional / Economic split)
  2. Fieldwork requirement coverage
  3. Cross-subject competency mapping (uses `cross_subject_competency_embedding.py` LanceDB table)
  4. Marking scheme complexity
  5. Asset generator: `b.GenerateGeographyQuestPack`

- **Gaeilge** (5 cells):
  1. Topic frequency per year (with `irish_fada` asset_check badge)
  2. Cross-linguistic concept coverage (EN ↔ GA)
  3. Litríocht / Úrsceal / Filíocht breakdown
  4. Marking scheme complexity
  5. Asset generator: `b.GenerateGaeilgeQuestPack`

- **English** (5 cells):
  1. Topic frequency per year (Comparative / Cultural / Language split)
  2. Single-text vs comparative-text mode
  3. Poetry / prose / drama breakdown
  4. Marking scheme complexity
  5. Asset generator: `b.GenerateEnglishQuestPack`

- **Computer Science** (5 cells):
  1. Topic frequency per year (algorithms / data / systems / web split)
  2. Pseudocode complexity
  3. Code-trace question coverage
  4. Marking scheme complexity
  5. Asset generator: `b.GenerateComputerScienceQuestPack`

### B.7 MotherDuck Flights + Dives

**Flight** — `lc_pdf_sync_flight`:
- Schedules a daily `cocoindex update lc_subjects` + `dagster asset materialize --select '*lc*'`
- Writes a status row to `md:oideachais.lc_ops.daily_sync_status`

**4 Dives** (MotherDuck live dashboards):

1. **Syllabus Topics Dive** — topic frequency per subject per year,
   filterable by level (Higher / Ordinary / Foundation) and language (en/ga).
   Drill-down: click a topic → list the syllabuses that mention it + the
   years it appeared in exams.

2. **Exam Paper Difficulty Dive** — per-subject per-year per-paper
   difficulty score (computed from BAML extraction: mark weight × part
   complexity). Drill-down: click a paper → view the questions + the
   matching marking scheme descriptors.

3. **Marking Scheme Complexity Dive** — per-subject per-topic average
   descriptor count + grade-band distribution. Drill-down: click a topic
   → view the full marking scheme text for the years it appeared.

4. **Education Circulars Dive** — `gov.ie` circulars by dept + year +
   subject area. Filterable by dept (DES / NCCA / SEC / DoE) and language
   (en/ga). Drill-down: click a circular → view summary + full text.

### B.8 Spec deltas (in `specs/british-isles-education-pipeline/spec.md`)

The new spec `british-isles-education-pipeline` covers the canonical
contract for the 6 LC subjects + gov.ie circulars. v1 is Ireland-only;
v2 will add the cross-nation (Scotland / Wales / England / NI) extension
on top of this v1 base.

## What does NOT change

- The existing `ncca-leaving-cert-root-pdfs` spec (5 root PDFs).
- The existing `rewrite-cianfhoghlaim-leaving-cert-v2` umbrella change.
- The existing `2026-07-03-leaving-cert-5-subject-pipeline-with-diagrams`
  change (its 5 subjects continue to work; English gets added in v1).
- The agent fleet (the user removed `agents/tuatha/agents/adk/` — the
  British-Isles Education pipeline is consumed by the teacher/agent
  surfaces, not by the agent fleet directly).

## Files (NEW + modified)

### New Python files

- `cianfhoghlaim/dlt/filesystem/pdf_download_source.py` (PDF downloader)
- `cianfhoghlaim/dlt/british_isles/ireland/education/gov_ie_circulars.py`
  (gov.ie circulars DLT source)
- `cianfhoghlaim/notebooks/nb_utils.py` (shared notebook helpers)
- `cianfhoghlaim/notebooks/dashboards/education/cross_subject_competency.py`
  (new cross-subject notebook using `cross_subject_competency_embedding.py`
  LanceDB table)
- `cianfhoghlaim/notebooks/dashboards/circulars/government_circulars_archive.py`
  (gov.ie circulars Dive notebook)
- `cianfhoghlaim/notebooks/dashboards/circulars/syllabus_to_circular_link.py`
  (cross-archive: which gov.ie circulars reference which NCCA syllabuses)
- `cianfhoghlaim/dlt/common/curriculum_registry.py` (extend to include gov.ie)

### New BAML functions

- `baml/processing/circular_extraction.baml` — add `ExtractCircular` +
  `LinkCircularToSyllabus` (the latter is the cross-archive edge)
- `baml/education/cross_nation/circulars.baml` — new file for the
  cross-nation circular schema (deferred to v2 but the schema lives here)

### New CocoIndex flows

- `cocoindex/government_circulars_embedding.py` (v1-conformant;
  `oideachais.government.circulars.lc6` LanceDB table)

### New Dagster assets

- `orchestration/defs/1_ingestion/curriculum/lc6_ncca/defs.yaml`
- `orchestration/defs/1_ingestion/curriculum/lc6_examinations/defs.yaml`
- `orchestration/defs/1_ingestion/government/circulars/defs.yaml`
- `orchestration/defs/3_model_lifecycle/cocoindex_v1/lc_subjects/defs.yaml`
- `orchestration/defs/3_model_lifecycle/cocoindex_v1/government_circulars/defs.yaml`
- New assets in `orchestration/defs/2_materials/lc_extraction/lc5_assets.py`:
  6× English assets (`lc5_english_ingested`, ... `_syllabus_extracted`, ...
  `_papers_extracted`, ... `_marking_extracted`, ... `_diagrams_extracted`,
  `lc5_english_cognified`)
- New `orchestration/defs/2_materials/circulars/government_circular_assets.py`

### Modified Python files

- `cianfhoghlaim/dlt/filesystem/leaving_cert_source.py:48` — add English
  to `LC5_SUBJECTS`, add 3rd branch to `_scan_subject`
- `cianfhoghlaim/dlt/british_isles/ireland/education/subjects/<s>/sources.py`
  (×8) — migrate to canonical BAML fn names
- `cianfhoghlaim/dlt/british_isles/ireland/education/curriculum.py` vs
  `curriculum_source.py` — resolve duplicate
- `cianfhoghlaim/cocoindex/{mathematics,chemistry,geography,gaeilge,english,computer_science}_embedding.py`
  (×6) — refactor to v1-conformant pattern
- `cianfhoghlaim/notebooks/dashboards/leaving_cert/0X_*.py` (×16) — wire
  to live lakehouse + add British-Isles Education visualisations
- `cianfhoghlaim/notebooks/root_pdfs_explorer.py` — wire to live
  `oideachais.lc.root.*` LanceDB table

### New openspec

- `openspec/changes/2026-07-06-british-isles-education-pipeline-v1/`
  (this change)
- `openspec/specs/british-isles-education-pipeline/spec.md` (the new spec)

## Acceptance

- `openspec validate 2026-07-06-british-isles-education-pipeline-v1 --strict`
  passes.
- `dagster asset materialize --select '*lc6*'` succeeds; the
  `lc6_<subject>_*` assets produce rows in
  `md:oideachais.leaving_cert.<subject>_*` DuckLake tables for all 6 subjects.
- `dagster asset materialize --select '*circular*'` succeeds; the
  `government_circulars` asset produces rows in
  `md:oideachais.government.circulars`.
- `marimo run cianfhoghlaim/notebooks/dashboards/leaving_cert/05_mathematics_analysis.py`
  renders the 5 visualisations against live lakehouse data.
- The 4 MotherDuck Dives (`lc_syllabus_topics`, `lc_exam_difficulty`,
  `lc_marking_complexity`, `gov_circulars_archive`) are reachable from the
  MotherDuck workspace and render live data.
- The daily `lc_pdf_sync_flight` runs and writes a status row.
- `bglakehouse dq --check irish_fada --subject gaeilge` passes.
- `ccc search "British-Isles Education"` finds the new spec + the
  per-subject notebooks.