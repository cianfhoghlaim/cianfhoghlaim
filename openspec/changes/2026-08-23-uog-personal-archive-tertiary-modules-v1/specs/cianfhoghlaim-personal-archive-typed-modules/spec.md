# cianfhoghlaim-personal-archive-typed-modules Specification

## Purpose

`cianfhoghlaim-personal-archive-typed-modules` is a capability of the
Cianfhoghlaim platform. It is the **F-granularity (per-question)
typed pipeline** that lifts
`leabharlann/ollscoil_na_gaillimhe/` (the user's three UoG courses'
artefacts: BA Maths & Education, HDip Software Design, Diploma in
Irish C1) + `cian_mac_an_déisigh_uí_liatháin/achievement/*transcript*.pdf`
to feature parity with the leaving-cycle subject pipeline.

The pipeline produces typed artefacts → assignments → questions →
topics → code cells → reading items → CA marks → transcript rows
at **F-granularity**, joins to the transcript for ground truth,
embeds in LanceDB, draws typed Cognee edges, and surfaces via
marimo + Convex + CopilotKit + Genie + ADK agent. **Transferable
to any user**: the same factory runs against any other student's
`leabharlann/<university>/` corpus, parameterised on a generic
`UniversityPersonalArchiveConfig`.

The corresponding source code lives at:

- `baml_src/british_isles/ireland/education/university/personal_archive_extraction.baml` (10 classes + 3 enums + 7 functions)
- `dlt_sources/filesystem/uog_personal_archive.py` (8 resources)
- `dlt_sources/filesystem/_htr_ensemble.py` (the 4-VLM consensus router)
- `dlt_sources/_lakehouse/personal_archive_destinations.py` (9 typed DuckLake tables)
- `dlt_sources/british_isles/ireland/education/university/personal_archive/uog_personal_archive_source.py` (the transferable factory)
- `scripts/graph_storage/cognify/rules/personal_archive_typed_edges.py` (10 typed Cognee edges)
- `orchestration/defs/uog_personal_archive.py` (the 6-asset Dagster group)

## Background

The user's three UoG courses produced the canonical personal
archive under `leabharlann/ollscoil_na_gaillimhe/`:

- `education/` (29 PDFs + 5 DOCX + 4 `.pages` + 4 PPTX) — the BA
  Maths & Education + HDip Software Design artefacts
- `irish/` (4 PDFs + 4 `.pages` + 2 DOCX) — the Diploma in Irish C1
- `mata/` (50+ scanned PDFs + `.pages`) — handwritten maths work
- `past/` (60+ scanned PDFs + `.pages`) — past papers + lecture
  scripts
- `software_development/` (15 `.ipynb` + 10 `.py` + 8 `.R`) — the
  HDip Software Design code artefacts

Plus the ground-truth transcripts at
`cian_mac_an_déisigh_uí_liatháin/achievement/*transcript*.pdf`
(`2013_2023_transcript_nuig.pdf` for the BA + HDip;
`ba_and_hdip_transcript.pdf`; the parchment JPEGs;
`torthai_ghaeilge.pdf` for the Irish Diploma).

The legacy `dlt_sources/filesystem/university_of_galway.py` source
yields **one row per file** with the legacy single-class
`ExtractUoGArtifact` BAML extraction. This change replaces that
with the F-granularity typed pipeline that the leaving-cycle
subject pipeline has — the per-question, per-topic, per-code-cell,
per-reading-item, per-CA-mark, per-transcript-row decomposition.

## ADDED Requirements

### Requirement: Filesystem scan + module-code detection

The DLT source SHALL walk `leabharlann/ollscoil_na_gaillimhe/`
recursively and yield one row per discovered file in the
`personal_archive_artefacts` resource. The `_classify_file` helper
SHALL match the regex `[A-Za-z]{2,4}\d{3,4}` against every path
component and assign the matching module code (e.g. `CT511`,
`ED305`, `MA216`, `GA101`).

#### Scenario: ED305 module code is detected from `ed305_assignment_2.pdf`

- **GIVEN** a file at
  `leabharlann/ollscoil_na_gaillimhe/education/ed305_assignment_2.pdf`
- **WHEN** `_classify_file()` is called
- **THEN** the returned tuple's module_code SHALL be `"ED305"`
- **AND** the artefact_kind SHALL be `ASSIGNMENT_SUBMISSION`
- **AND** the assignment_number SHALL be `2`
- **AND** the artefact_provenance SHALL be `PERSONAL_SUBMISSION`
- **AND** the `personal_archive_artefacts` row SHALL have
  `module_code = "ED305"` and `assignment_number = 2`

#### Scenario: No module code in path returns None

- **GIVEN** a file at
  `leabharlann/ollscoil_na_gaillimhe/education/closing_statement.pdf`
- **WHEN** `_classify_file()` is called
- **THEN** the returned tuple's module_code SHALL be `None`
- **AND** the artefact_kind SHALL be inferred from filename
  (here: `OTHER` since `closing_statement` does not match any
  known pattern)

#### Scenario: Empty personal archive yields one skipped row per resource

- **GIVEN** `UNIVERSITY_PERSONAL_ARCHIVE_PATH` points to a
  directory that does not exist or contains no PDF files
- **WHEN** the source runs
- **THEN** every resource SHALL yield exactly one row with
  `status = "skipped_no_real_files"`
- **AND** no exception is raised (CI never crashes)

### Requirement: Provenance detection

`_classify_file` SHALL classify each artefact's `artefact_provenance`
based on the path tokens:

- `Lecture` / `Problem` / `Model` / `Marking` / `Slides` →
  `LECTURE_PROVIDED`
- `transcript` / `achievement` → `TRANSCRIPT`
- filename starts with `cian_mac_liathain_` or `cian_mac_an_déisigh_` →
  `PERSONAL_SUBMISSION`
- else → `UNKNOWN`

#### Scenario: A file in `Lecture/` is LECTURE_PROVIDED

- **GIVEN** a file at
  `leabharlann/ollscoil_na_gaillimhe/education/Lecture/MA216_week_5.pdf`
- **WHEN** `_classify_file()` is called
- **THEN** the artefact_provenance SHALL be `LECTURE_PROVIDED`
- **AND** the artefact_kind SHALL be `LECTURE_NOTES`

#### Scenario: A transcript PDF is TRANSCRIPT

- **GIVEN** a file at
  `cian_mac_an_déisigh_uí_liatháin/achievement/2013_2023_transcript_nuig.pdf`
- **WHEN** `_classify_file()` is called
- **THEN** the artefact_provenance SHALL be `TRANSCRIPT`
- **AND** the artefact_kind SHALL be `TRANSCRIPT`

#### Scenario: A `cian_mac_liathain_` filename is PERSONAL_SUBMISSION

- **GIVEN** a file at
  `leabharlann/ollscoil_na_gaillimhe/software_development/cian_mac_liathain_ct511_assignment_1.pdf`
- **WHEN** `_classify_file()` is called
- **THEN** the artefact_provenance SHALL be `PERSONAL_SUBMISSION`
- **AND** the artefact_kind SHALL be `ASSIGNMENT_SUBMISSION`
- **AND** the module_code SHALL be `CT511`

### Requirement: HTR routing

The DLT source SHALL use `dlt_sources/filesystem/_htr_ensemble.py`
to route every file to one of the 5 HTR backends:

- `.pages` / `.heic` → `MULTI_VLM_CONSENSUS` (confidence 0.5)
- filename contains `handwritten` / `goodnotes` / `apple_pencil` →
  `MULTI_VLM_CONSENSUS` (confidence 0.5)
- pymupdf_chars_per_page < 100 → `MULTI_VLM_CONSENSUS` (confidence 0.4)
- else → `PYMUPDF_TYPED` (confidence 0.95)

The `htr_extract_pages` helper SHALL return the extracted markdown
text and the HTR confidence for the chosen backend.

#### Scenario: A `.pages` file routes to MULTI_VLM_CONSENSUS

- **GIVEN** a file with extension `.pages`
- **WHEN** `route_htr()` is called
- **THEN** the returned backend SHALL be `MULTI_VLM_CONSENSUS`
- **AND** the confidence SHALL be `0.5`

#### Scenario: A typed PDF with high chars/page uses PYMUPDF_TYPED

- **GIVEN** a PDF with `pymupdf_chars_per_page = 2500`
- **WHEN** `route_htr()` is called
- **THEN** the returned backend SHALL be `PYMUPDF_TYPED`
- **AND** the confidence SHALL be `0.95`
- **AND** the embedded text SHALL be the pymupdf extract

#### Scenario: A scanned PDF with <100 chars/page routes to consensus

- **GIVEN** a PDF with `pymupdf_chars_per_page = 47` (i.e. scanned)
- **WHEN** `route_htr()` is called
- **THEN** the returned backend SHALL be `MULTI_VLM_CONSENSUS`
- **AND** the confidence SHALL be `0.4`
- **AND** the embedded text SHALL be the 4-VLM ensemble consensus
  (falling back to nougat if all 4 disagree on >30%)

### Requirement: Per-artefact BAML extraction

The system SHALL provide a BAML function `ExtractUoGPersonalArchiveArtefact`
in `baml_src/british_isles/ireland/education/university/personal_archive_extraction.baml`
that emits a `UoGPersonalArchiveArtefact` row per discovered file,
detecting artefact_kind, inferring module_code if not given by the
caller, and classifying provenance.

#### Scenario: A lecture-note PDF is typed as LECTURE_NOTES

- **GIVEN** the BAML client receives the embedded text of
  `Lecture/MA216_week_5.pdf` with `file_name="MA216_week_5.pdf"`
  and `file_type="pdf"`
- **WHEN** `b.ExtractUoGPersonalArchiveArtefact(embedded_text, file_name, "pdf", None, LECTURE_PROVIDED)` runs
- **THEN** the returned `UoGPersonalArchiveArtefact` SHALL have
  - `artefact_kind = LECTURE_NOTES`
  - `artefact_provenance = LECTURE_PROVIDED`
  - `module_code = "MA216"` (inferred from filename)
  - `confidence ∈ [0.85, 1.0]`

#### Scenario: A transcript PDF is typed as TRANSCRIPT

- **GIVEN** the BAML client receives the embedded text of
  `2013_2023_transcript_nuig.pdf`
- **WHEN** `ExtractUoGPersonalArchiveArtefact(embedded_text, file_name, "pdf", None, TRANSCRIPT)` runs
- **THEN** the returned row SHALL have
  - `artefact_kind = TRANSCRIPT`
  - `artefact_provenance = TRANSCRIPT`
  - `module_code = None` (transcripts span many modules)

### Requirement: Per-assignment + per-question BAML extraction

The system SHALL provide a BAML function `ExtractUoGAssignment`
that emits a `UoGAssignment` row per assignment artefact, enumerating
every question with `question_text`, `my_answer_text`, `my_answer_latex`,
`my_mark`, `my_mark_breakdown`, and `answer_topic_tags`. Each
question is its own row in the `personal_archive_questions` DuckLake
table.

#### Scenario: An ED305 assignment with 3 questions yields 3 question rows

- **GIVEN** an ED305 assignment PDF with 3 questions (Q1 — "Discuss
  the role of the class teacher"; Q2 — "Critically evaluate behaviour
  management strategies"; Q3 — "Reflect on a critical incident")
- **WHEN** `b.ExtractUoGAssignment(embedded_text, file_name, "ED305", 1)` runs
- **THEN** the returned `UoGAssignment.questions[]` SHALL have 3
  entries
- **AND** each `UoGQuestion` SHALL have `question_id`, `question_number`,
  `question_text`, and (if visible) `my_answer_text`, `my_mark`,
  `my_mark_breakdown`
- **AND** the DuckLake `personal_archive_questions` table SHALL have
  3 rows for `module_code = "ED305"`

#### Scenario: A handwritten assignment uses HTR

- **GIVEN** an ED305 assignment PDF scanned (pymupdf_chars_per_page = 47)
- **WHEN** `b.ExtractUoGAssignment(embedded_text, file_name, "ED305", 1)` runs
- **THEN** each `UoGQuestion` SHALL have
  `htr_backend_used = MULTI_VLM_CONSENSUS`,
  `htr_confidence ∈ [0.4, 0.6]`, `is_handwritten = true`

### Requirement: Per-topic BAML extraction

The system SHALL provide a BAML function `ExtractUoGTopicList` that
emits a `UoGTopic[]` from the embedded text of any per-module
artefact (lecture notes, problem sheets, or assignments). The topics
are the canonical topics the user engaged with for that module.

#### Scenario: An MA216 lecture yields 5 topics

- **GIVEN** the embedded text of an MA216 lecture on probability
  and statistics
- **WHEN** `b.ExtractUoGTopicList(embedded_text, "MA216")` runs
- **THEN** the returned `UoGTopic[]` SHALL have 5 entries
- **AND** each entry SHALL have `topic_name` (e.g. "Random variables",
  "Hypothesis testing"), `topic_category` (e.g. "probability",
  "inferential_statistics"), `module_codes = ["MA216"]`,
  `occurrence_count ∈ [1, 100]`

#### Scenario: Topics are deduped across lectures

- **GIVEN** two MA216 lectures both mentioning "Hypothesis testing"
- **WHEN** the `personal_archive_topics` DuckLake table is materialised
- **THEN** there SHALL be exactly one row with
  `topic_name = "Hypothesis testing"` and
  `occurrence_count = 2` (the dedup key is `(module_code, topic_name)`)

### Requirement: Per-code-cell BAML extraction

The system SHALL provide a BAML function `ExtractUoGCodeCell` that
emits a `UoGCodeCell` row per `.ipynb` or `.py` file's cell (or
function). Each cell carries `cell_source`, `cell_output`, and
`demonstrates_topics` (the topics the cell illustrates).

#### Scenario: A CT511 notebook cell on REST API design yields 1 row

- **GIVEN** a CT511 notebook with a cell containing a Flask app
  demonstrating REST API design
- **WHEN** `b.ExtractUoGCodeCell(cell_source, cell_output, 5, "CT511")` runs
- **THEN** the returned `UoGCodeCell` SHALL have
  - `cell_index = 5`
  - `cell_type = "code"`
  - `source_text = "<flask source>"`
  - `output_text = "<flask output>"`
  - `demonstrates_topics = ["rest_api_design", "flask"]`
  - `module_code = "CT511"`

### Requirement: Per-lecture-reading-list BAML extraction

The system SHALL provide a BAML function `ExtractUoGLectureReadingList`
that emits a `UoGReadingItem[]` from the embedded text of a lecture
artefact or module descriptor. Each item carries ISBN-13, DOI, URL,
authors, format, and `is_essential`.

#### Scenario: An MA216 lecture yields 4 reading items

- **GIVEN** the embedded text of an MA216 lecture with 4 reading
  items (2 essential, 2 recommended)
- **WHEN** `b.ExtractUoGLectureReadingList(embedded_text, "MA216")` runs
- **THEN** the returned `UoGReadingItem[]` SHALL have 4 entries
- **AND** 2 SHALL have `is_essential = true`
- **AND** each entry SHALL have `format = ISBN_13 | DOI | URL`,
  `title`, `authors[]`, and the corresponding identifier

#### Scenario: An ISBN-13 reading item validates

- **GIVEN** a `UoGReadingItem` with `format = ISBN_13` and
  `isbn_13 = "9780262033848"`
- **WHEN** the deterministic eval runs
- **THEN** the eval SHALL confirm `isbn_13` matches `^\d{13}$`
- **AND** the eval SHALL fail loudly (asset_check fail) if the
  regex does not match

### Requirement: Transcript BAML extraction

The system SHALL provide a BAML function `ExtractStudentTranscript`
that emits a `StudentTranscriptRow[]` from the embedded text of any
`*transcript*.pdf`. One row per (student, module, academic_year)
with `grade`, `ects`, `nfq_level`, `programme_code`, and
`is_honours | is_resit`.

#### Scenario: A NUIG transcript PDF yields 12 rows

- **GIVEN** the embedded text of
  `2013_2023_transcript_nuig.pdf` covering the BA + HDip
- **WHEN** `b.ExtractStudentTranscript(embedded_text, "cian_mac_an_deisigh_ui_liathain")` runs
- **THEN** the returned `StudentTranscriptRow[]` SHALL have ≥12
  entries (one per module per academic year)
- **AND** each row SHALL have `student_id`,
  `institution_id = "ie-university-galway"`,
  `module_code`, `module_title`, `ects`, `nfq_level`,
  `academic_year`, `grade`, `is_honours`, `is_resit`,
  `transcript_pdf = "<absolute path>"`

#### Scenario: Transcript row joins to the CA mark row

- **GIVEN** a `StudentTranscriptRow` with
  `module_code = "ED305"`, `academic_year = 2018`, `grade = "B2"`
- **AND** a `UoGCaMark` with
  `module_code = "ED305"`, `ca_label = "ED305 Assignment 1"`,
  `mark = 62.0`, `max_mark = 100.0`, `academic_year = 2018`
- **WHEN** the typed-join asset runs
- **THEN** the join SHALL produce a row with `ca_mark = 62.0`
  and `transcript_grade = "B2"`
- **AND** the Cognee edge `Response-GRADED_AS-TranscriptGrade` SHALL
  be emitted with `match_confidence = 1.0` (the join key is
  exact `(module_code, academic_year)`)

### Requirement: Typed DuckLake tables

The system SHALL provide 9 typed DuckLake tables at
`dlt_sources/_lakehouse/personal_archive_destinations.py`:

1. `personal_archive_artefacts` — one row per file (every
   `UoGPersonalArchiveArtefact` column + partition keys)
2. `personal_archive_assignments` — one row per assignment (every
   `UoGAssignment` column except `questions[]`)
3. `personal_archive_questions` — one row per question (every
   `UoGQuestion` column)
4. `personal_archive_topics` — one row per topic (every `UoGTopic` column)
5. `personal_archive_reading_lists` — one row per reading item (every
   `UoGReadingItem` column)
6. `personal_archive_code_cells` — one row per code cell (every
   `UoGCodeCell` column)
7. `personal_archive_ca_marks` — one row per CA mark (every
   `UoGCaMark` column)
8. `personal_archive_modules` — one row per module summary (every
   `UoGModuleSummary` column except `ca_marks[]` and `topic_names[]`)
9. `student_transcripts` — one row per (student, module, academic_year)
   (every `StudentTranscriptRow` column)

`register_personal_archive_tables(con, schema_name="cianfhoghlaim.education.ie")`
SHALL issue `CREATE TABLE IF NOT EXISTS` for all 9 tables.

#### Scenario: All 9 tables exist after materialisation

- **WHEN** `register_personal_archive_tables(con)` is called
- **THEN** the 9 tables SHALL be created in the
  `cianfhoghlaim.education.ie` schema
- **AND** the marimo notebook SHALL be able to query them via
  `mo.sql(engine=md:cianfhoghlaim)`

#### Scenario: Question rows join to assignment rows

- **GIVEN** a `personal_archive_assignments` row with
  `assignment_id = "ed305_1"`
- **AND** 3 `personal_archive_questions` rows with the same
  `assignment_id`
- **WHEN** the marimo notebook queries
  `personal_archive_questions JOIN personal_archive_assignments ON question.assignment_id = assignment.assignment_id`
- **THEN** the join SHALL yield 3 rows (one per question)

### Requirement: 4 CocoIndex v1 Apps

The system SHALL provide 4 v1 CocoIndex Apps at
`cocoindex_flows/british_isles/ireland/education/university/personal_archive_embedding.py`:

1. `UoGPersonalArchiveArtefactsApp` — BGE-M3 1024-d on
   `artefact_title + embedded_text + key_topics`
2. `UoGPersonalArchiveQuestionsApp` — BGE-M3 1024-d on
   `question_text + my_answer_text + topic_tags`
3. `UoGPersonalArchiveTopicsApp` — BGE-M3 1024-d on
   `topic_name + topic_category`
4. `UoGPersonalArchiveLectureNotesApp` — BGE-M3 1024-d on
   `artefact_title + embedded_text`

All 4 SHALL use the canonical v1 pattern (`@coco.lifespan` +
`@coco.fn` + `lancedb.mount_table_target` +
`SentenceTransformerEmbedder("BAAI/bge-m3")`) and SHALL respect
the 100-batch minimum + `HNSW-DROP-THRESHOLD=50` rule.

#### Scenario: The 4 Apps are registered

- **WHEN** `cocoindex_flows/british_isles/ireland/education/university/personal_archive_embedding.py` is loaded
- **THEN** 4 `coco.App(coco.AppConfig(name="UoGPersonalArchive{Artefacts,Questions,Topics,LectureNotes}"), ...)` instances SHALL exist
- **AND** the total v1 App count SHALL go from 17 (post the UoG
  official docs superset change) to 21

#### Scenario: Semantic search over personal-archive topics

- **GIVEN** the `UoGPersonalArchiveTopicsApp` has materialised
- **WHEN** a developer runs
  `await search_personal_archive_topics("hypothesis testing", limit=5)`
- **THEN** the App returns the top-5 rows from the
  `personal_archive_topics` table ranked by BGE-M3 cosine similarity
- **AND** each row has `topic_id`, `topic_name`, `topic_category`,
  `module_codes`, `occurrence_count`

### Requirement: 10 Cognee typed edges

The system SHALL provide 10 Cognee typed edge rules at
`scripts/graph_storage/cognify/rules/personal_archive_typed_edges.py`:

1. `(:PersonalArchiveArtefact)-[:DESCRIBES]->(:PersonalArchiveModule)`
2. `(:PersonalArchiveArtefact)-[:CONTAINS]->(:PersonalArchiveQuestion)`
3. `(:PersonalArchiveQuestion)-[:ANSWERED_BY]->(:PersonalArchiveResponse)`
4. `(:PersonalArchiveResponse)-[:GRADED_AS]->(:StudentTranscriptGrade)`
5. `(:PersonalArchiveModule)-[:COVERS]->(:PersonalArchiveTopic)`
6. `(:PersonalArchiveTopic)-[:RELATED_TO]->(:PersonalArchiveTopic)`
7. `(:PersonalArchiveTopic)-[:FOUND_IN]->(:PersonalArchiveLectureArtefact)`
8. `(:PersonalArchiveArtefact)-[:PROVIDED_BY]->(:PersonalArchiveLecturer)`
9. `(:PersonalArchiveCodeCell)-[:DEMONSTRATES]->(:PersonalArchiveTopic)`
10. `(:PersonalArchiveReadingItem)-[:CITED_IN]->(:PersonalArchiveLectureArtefact)`

Each edge carries `match_confidence ∈ [0.0, 1.0]`. The emitters
SHALL be pure functions over the input iterables so they can be
unit-tested without a live Cognee graph.

#### Scenario: The CS4423 assignment connects to its transcript row

- **GIVEN** a `PersonalArchiveAssignment` row with
  `module_code = "CS4423"`, `assignment_number = 1`
- **AND** 4 `PersonalArchiveQuestion` rows with the same `assignment_id`
- **AND** a `StudentTranscriptGrade` row with
  `module_code = "CS4423"`, `academic_year = 2019`, `grade = "A1"`
- **WHEN** the cognify pass runs
- **THEN** the `Artefact-DESCRIBES-Module` edge SHALL be emitted
- **AND** the `Artefact-CONTAINS-Question` edges SHALL be emitted (4)
- **AND** the `Response-GRADED_AS-TranscriptGrade` edge SHALL be
  emitted with `match_confidence = 1.0`

#### Scenario: The 10 emitters are importable as a tuple

- **WHEN** `from scripts.graph_storage.cognify.rules.personal_archive_typed_edges import PERSONAL_ARCHIVE_EDGES`
- **THEN** `PERSONAL_ARCHIVE_EDGES` SHALL be a tuple of 10 callables

### Requirement: Marimo 8-tab BIEP notebook + CS4423 worked-example sidebar

The system SHALL provide a marimo notebook at
`notebooks/15_personal_archive.py` with the canonical 8-tab BIEP
pattern (Health / Filters / Materials / URL Health / Heatmap /
Recent / Lance Search / SQL Console), plus a **CS4423 worked-example
sidebar** that walks the reader through the per-question extraction
of one specific CS4423 assignment (the worked-example the user
wants in the thesis).

The notebook SHALL use `mo.sql(engine=md:cianfhoghlaim)` for the
underlying queries (the MotherDuck Postgres endpoint) so it loads
against the lakehouse, not against a local Parquet.

#### Scenario: The user opens the per-question extraction tab

- **WHEN** the user navigates to `/dashboards/personal-archive`
  and clicks the "Per-question extraction" tab (the worked-example
  sidebar)
- **THEN** the notebook SHALL display the CS4423 assignment with
  every question, the extracted answer text + LaTeX, the HTR
  backend + confidence, and the matched topic tags

#### Scenario: The user opens the transcript join tab

- **WHEN** the user navigates to the "Transcript join" tab
- **THEN** the notebook SHALL display a table of every
  `UoGCaMark` joined to its `StudentTranscriptRow` on
  `(module_code, academic_year)`, with `ca_mark`, `transcript_grade`,
  `delta_pct`, and the Cognee edge `match_confidence`

### Requirement: Convex + CopilotKit + Genie + ADK chat surface + transferability

The system SHALL surface the personal-archive data via:

1. **Convex** — `web/apps/oideachais-web/convex/schema.ts` adds
   `personal_archive_artefacts`, `personal_archive_questions`,
   `student_transcripts` tables + the `chatWithPersonalArchive`
   action (the canonical Convex action that the CopilotKit UI calls)
2. **CopilotKit** — `web/apps/oideachais-web/app/personal-archive/page.tsx`
   is the chat UI (uses AG-UI v2 protocol)
3. **Genie** — `observability/dashboards/personal_archive.json`
   is the Grafana dashboard
4. **ADK agent** — `agents/adk/personal_archive_module_assistant.py`
   is the agent (uses Google ADK + Gemini 2.5 Pro via LiteLLM)

The whole pipeline SHALL be **transferable** to any user:
`personal_archive_source(university_config: UniversityPersonalArchiveConfig) -> dlt.Source`
where `UniversityPersonalArchiveConfig` is a Pydantic v2 model
with the 9 env-var fields
(`personal_archive_path`, `registry_url`, `university_name`,
`institution_id`, `programme_code_regex`, `transcript_file_patterns`,
`assignment_file_pattern`, `lecture_notes_dir_pattern`,
`ducklake_destination`).

#### Scenario: A second student points the pipeline at their own directory

- **GIVEN** a second student creates a Pydantic config:
  ```python
  UniversityPersonalArchiveConfig(
      personal_archive_path=Path("/home/alice/leabharlann/ucd"),
      registry_url="https://www.ucd.ie",
      university_name="University College Dublin",
      institution_id="ie-ucd",
      programme_code_regex=r"[A-Z]{2,3}\d{3,4}",
      transcript_file_patterns=("*transcript*.pdf",),
      assignment_file_pattern="*assignment*.pdf",
      lecture_notes_dir_pattern="*Lectures*",
      ducklake_destination="motherduck",
  )
  ```
- **WHEN** `personal_archive_source(alice_config).run()` executes
- **THEN** the DLT source SHALL walk `/home/alice/leabharlann/ucd/`
- **AND** the BAML extraction SHALL use UoG-typed defaults but
  override `institution_id` to `"ie-ucd"`
- **AND** the DuckLake rows SHALL land in
  `cianfhoghlaim.education.ie.personal_archive_*` with
  `institution_id = "ie-ucd"` in the `module_code` partition

#### Scenario: Convex action proxies to the ADK agent

- **WHEN** the user submits a CopilotKit chat message
  "show me every question on Laplace transforms I ever got wrong"
- **THEN** the CopilotKit UI calls `chatWithPersonalArchive` Convex action
- **AND** the Convex action proxies to the
  `personal_archive_module_assistant` ADK agent
- **AND** the ADK agent queries the 9 DuckLake tables via the
  MotherDuck endpoint
- **AND** the response renders in the CopilotKit chat panel
  within 5 seconds
