// =============================================================================
// Personal Archive BAML Schema — feature-parity with Leaving Cert subject pipeline
// =============================================================================
//
// Lifts `leabharlann/ollscoil_na_gaillimhe/` (the user's three UoG courses'
// artefacts: BA Maths & Education, HDip Software Design, Diploma in Irish
// C1) + `cian_mac_an_déisigh_uí_liatháin/achievement/*transcript*.pdf`
// to F-granularity typed extraction: artefacts → assignments → questions
// → topics → code cells → reading items → CA marks → transcript rows.
//
// ADDS the canonical personal-archive surface on top of the existing
// `uog_official_docs_extraction.baml` (the public-side classes) and
// `uog_exam_paper_extraction.baml` (the authenticated exam papers).
//
// All 7 functions route through the canonical `ExtractEn` LiteLLM
// client (per `baml_src/clients.baml`).
//
// The `UoGQuestion` class is intentionally F-granular — each question
// is its own row, with `my_answer_text`, `my_answer_latex`, `my_mark`
// downstream marimo notebook can show "every question on Laplace
// transforms I ever got wrong" (the user's worked-example).
//
// Reference: openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
//             specs/cianfhoghlaim-personal-archive-typed-modules/spec.md

// =============================================================================
// Enums
// =============================================================================

enum ArtefactProvenance {
  LECTURE_PROVIDED       @description("Distributed by the lecturer as standard for that year's cohort (lecture notes, problem sheets, past papers shared in class). Not the student's own work.")
  PERSONAL_SUBMISSION    @description("Authored by the student (assignment submission, exam script, personal notes, code)")
  THIRD_PARTY_REFERENCE  @description("Reference work the student used (textbook chapter, online tutorial)")
  TRANSCRIPT             @description("Official academic transcript / record")
  UNKNOWN
}

enum ArtefactKind {
  ASSIGNMENT_SUBMISSION
  ASSIGNMENT_BRIEF
  MARKING_SCHEME
  MODEL_SOLUTION
  PAST_EXAM_PAPER
  PAST_EXAM_SCRIPT
  LECTURE_NOTES
  PROBLEM_SHEET
  LAB_NOTEBOOK
  SOURCE_CODE
  READING_ITEM
  TRANSCRIPT
  SCANNED_PAGE
  OTHER
}

enum HTRBackend {
  NOUGAT
  OLMOCR_2_7B
  COGVLM
  GEMMA_3
  MULTI_VLM_CONSENSUS
  PYMUPDF_TYPED
  NONE
}

// =============================================================================
// UoGArtefactProvenanceMeta — the HTR + provenance metadata block on every artefact
// =============================================================================

class UoGArtefactProvenanceMeta {
  htr_required bool
  htr_backend_used HTRBackend?
  htr_confidence float?
  htr_page_count int?
  lecture_year int?
  lecturer_name string?
  course_code_on_artefact string?
}

// =============================================================================
// UoGPersonalArchiveArtefact — the top-level row per discovered file
// =============================================================================

class UoGPersonalArchiveArtefact {
  artefact_id string
  artefact_kind ArtefactKind
  artefact_provenance ArtefactProvenance
  module_code string
  module_title string?
  programme_code string?
  academic_year int?
  semester string?
  file_path string
  file_hash string
  bytes int
  file_extension string
  embedded_text string?
  confidence float
  provenance_meta UoGArtefactProvenanceMeta
  content_hash string
  scraped_at string
}

// =============================================================================
// UoGQuestion — F-granular row (one per question)
// =============================================================================

class UoGQuestion {
  question_id string
  assignment_id string
  question_number string
  question_text string
  expected_topic string?
  max_marks int?
  my_answer_text string?
  my_answer_latex string?
  my_mark int?
  my_mark_breakdown string?
  is_handwritten bool
  htr_backend_used HTRBackend?
  htr_confidence float?
  answer_topic_tags string[]
  confidence float
}

// =============================================================================
// UoGAssignment — wrapper around questions[] for one assignment artefact
// =============================================================================

class UoGAssignment {
  assignment_id string
  artefact_id string
  module_code string
  assignment_number int
  assignment_title string?
  total_marks int?
  weight_percent float?
  submission_deadline string?
  question_count int
  questions UoGQuestion[]
  confidence float
}

// =============================================================================
// UoGTopic — one row per (module_code, topic_name) tuple
// =============================================================================

class UoGTopic {
  topic_id string
  topic_name string
  topic_category string
  module_codes string[]
  occurrence_count int
  confidence float
}

// =============================================================================
// UoGReadingItem — one row per reading-list entry
// =============================================================================

class UoGReadingItem {
  reading_id string
  module_code string
  title string
  authors string[]
  format ReadingFormat
  isbn_13 string?
  doi string?
  url string?
  is_essential bool
  confidence float
}

// =============================================================================
// UoGCodeCell — one row per notebook cell / source-code function
// =============================================================================

class UoGCodeCell {
  cell_id string
  module_code string
  notebook_path string
  cell_index int
  cell_type string
  source_text string
  runtime_seconds float?
  output_text string?
  demonstrates_topics string[]
  confidence float
}

// =============================================================================
// UoGCaMark — one row per continuous-assessment mark (extracted from assignment front-pages)
// =============================================================================

class UoGCaMark {
  ca_id string
  module_code string
  ca_label string
  ca_weight_percent float?
  mark float?
  max_mark float?
  academic_year int?
  extracted_from_artefact_id string?
  confidence float
}

// =============================================================================
// StudentTranscriptRow — one row per (student, module, academic_year)
// =============================================================================

class StudentTranscriptRow {
  student_id string
  institution_id string
  programme_code string
  programme_title string
  module_code string
  module_title string
  ects int?
  nfq_level int?
  academic_year int
  semester string?
  grade string
  is_honours bool
  is_resit bool
  transcript_pdf string
  source_url string?
  scraped_at string
  confidence float
}

// =============================================================================
// UoGModuleSummary — the per-module summary (built at the end of the pipeline)
// =============================================================================

class UoGModuleSummary {
  module_code string
  module_title string
  programme_code string?
  artefact_count int
  assignment_count int
  question_count int
  topic_count int
  code_cell_count int
  reading_count int
  transcript_grade string?
  transcript_academic_year int?
  ca_marks UoGCaMark[]
  topic_names string[]
  first_artefact_year int?
  last_artefact_year int?
  confidence float
}

// =============================================================================
// Functions
// =============================================================================

function ExtractUoGPersonalArchiveArtefact(
  embedded_text: string,
  file_name: string,
  file_type: string,
  inferred_module_code: string?,
  provenance_hint: ArtefactProvenance
) -> UoGPersonalArchiveArtefact {
  client ExtractEn
  prompt #"
  {{ _.role("user") }}
  You are an expert at extracting University of Galway (or Irish university) personal-archive artefact metadata from rendered text.

  File: {{ file_name }} ({{ file_type }})
  Provenance hint: {{ provenance_hint }}
  Inferred module code (from path regex, may be wrong): {{ inferred_module_code }}

  Body:
  {{ embedded_text }}

  Extract every field described in the UoGPersonalArchiveArtefact shape. The artefact_kind MUST be one of the 14 ArtefactKind enum values (ASSIGNMENT_SUBMISSION / ASSIGNMENT_BRIEF / MARKING_SCHEME / MODEL_SOLUTION / PAST_EXAM_PAPER / PAST_EXAM_SCRIPT / LECTURE_NOTES / PROBLEM_SHEET / LAB_NOTEBOOK / SOURCE_CODE / READING_ITEM / TRANSCRIPT / SCANNED_PAGE / OTHER). The module_code MUST match the regex `^[A-Z]{2,4}\\d{3,4}$` if it can be inferred; otherwise leave null. The provenance_meta block MUST record which HTR backend would be needed (or NONE if the artefact is typed text).

  Special considerations:
  - If the file is a transcript (e.g. '2013_2023_transcript_nuig.pdf'), set artefact_kind = TRANSCRIPT and artefact_provenance = TRANSCRIPT. module_code is null (transcripts span many modules).
  - If the file is a lecture note (in a 'Lecture/' subdir), set artefact_kind = LECTURE_NOTES and artefact_provenance = LECTURE_PROVIDED.
  - If the file starts with 'cian_mac_liathain_' or 'cian_mac_an_déisigh_', set artefact_provenance = PERSONAL_SUBMISSION.
  - If the file is handwritten (filename contains 'handwritten' / 'goodnotes' / 'apple_pencil', or extension is '.pages' / '.heic'), set provenance_meta.htr_backend_used = MULTI_VLM_CONSENSUS.
  - Otherwise, set provenance_meta.htr_backend_used = PYMUPDF_TYPED (the typed-text case).

  {{ ctx.output_format }}
"#

}

function ExtractUoGAssignment(
  embedded_text: string,
  file_name: string,
  module_code: string,
  assignment_number: int?
) -> UoGAssignment {
  client ExtractEn
  prompt #"
  {{ _.role("user") }}
  You are an expert at extracting University of Galway (or Irish university) personal-archive assignment + per-question data from rendered text.

  File: {{ file_name }}
  Module code: {{ module_code }}
  Assignment number (from path, may be null): {{ assignment_number }}

  Body:
  {{ embedded_text }}

  Extract:
  - assignment_id: kebab-case slug, e.g. 'ed305_1' or 'ct511_2'.
  - artefact_id: a kebab-case id derived from the file hash, e.g. 'artefact_ed305_1_<sha256[:8]>'. Use a placeholder 'artefact_<file_stem>' if you don't have the hash.
  - assignment_title: the assignment title (e.g. 'ED305 Assignment 1 — Behaviour Management').
  - total_marks: the total mark available (e.g. 100), if visible.
  - weight_percent: the weighting toward the module grade (e.g. 30.0), if visible.
  - submission_deadline: ISO-8601 date, if visible.
  - questions[]: enumerate every question on the assignment. For each:
    - question_number: 'Q1', 'Q2', 'Q3.a', etc. Preserve the original numbering.
    - question_text: the full question text.
    - expected_topic: the topic the question targets, e.g. 'behaviour_management' or 'hypothesis_testing'. Lower-snake-case.
    - max_marks: the marks available for this question (e.g. 20).
    - my_answer_text: the student's answer (if visible in the embedded text). Preserve the original wording.
    - my_answer_latex: the LaTeX-rendered answer (if you can transcribe equations). Null if no equations.
    - my_mark: the mark the student received (if visible). Null if not visible.
    - my_mark_breakdown: the mark breakdown (e.g. '12/15 for content + 3/5 for references').
    - is_handwritten: true if the question is handwritten (the embedded text would have been HTR'd).
    - htr_backend_used: the HTR backend that was used (or NONE for typed text).
    - htr_confidence: the HTR confidence 0.0-1.0.
    - answer_topic_tags: 1-5 topic tags (lower-snake-case), e.g. ['behaviour_management', 'reflection'].

  Each question is its own row in the DuckLake personal_archive_questions table (F-granularity). The question_id MUST be unique within the assignment.

  Special considerations:
  - If the assignment is handwritten, set every question's is_handwritten = true and htr_backend_used = MULTI_VLM_CONSENSUS.
  - For computing assignments, my_answer_latex MUST preserve the LaTeX verbatim (e.g. '\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}').
  - If a question has no visible student answer (e.g. the assignment is a brief without a submission), leave my_answer_text and my_mark as null.

  {{ ctx.output_format }}
"#

}

function ExtractUoGTopicList(
  embedded_text: string,
  module_code: string
) -> UoGTopic[] {
  client ExtractEn
  prompt #"
  {{ _.role("user") }}
  You are an expert at extracting the canonical topic list from a University of Galway (or Irish university) lecture / problem-sheet / assignment text.

  Module code: {{ module_code }}

  Body:
  {{ embedded_text }}

  Extract a list of `UoGTopic` records. Each topic is a canonical name (lower-snake-case or CamelCase, but consistent) + a topic_category (the broader discipline bucket, e.g. 'probability', 'inferential_statistics', 'machine_learning', 'software_engineering', 'irish_language', 'assessment', 'behaviour_management').

  Each topic MUST have:
  - topic_id: kebab-case slug, e.g. 'ma216_hypothesis_testing'.
  - topic_name: human-readable name, e.g. 'Hypothesis testing'.
  - topic_category: the broader bucket, e.g. 'inferential_statistics'.
  - module_codes: ['{{ module_code }}'] (one-element list).
  - occurrence_count: 1 (single source).
  - confidence: 0.0-1.0.

  Special considerations:
  - Topics MUST be canonical: 'Hypothesis testing' and 'Hypothesis Testing' are the SAME topic (use lower-snake-case `hypothesis_testing`).
  - Aim for 3-15 topics per lecture / problem-sheet / assignment.

  {{ ctx.output_format }}
"#
}

function ExtractUoGLectureReadingList(
  embedded_text: string,
  module_code: string
) -> UoGReadingItem[] {
  client ExtractEn
  prompt #"
  {{ _.role("user") }}
  You are an expert at extracting University of Galway (or Irish university) per-module reading-list items from lecture notes / module descriptor text.

  Module code: {{ module_code }}

  Body:
  {{ embedded_text }}

  Extract a list of `UoGReadingItem` records. Each item MUST have:
  - reading_id: kebab-case slug, e.g. 'ma216_goodfellow_deep_learning'.
  - module_code: '{{ module_code }}'.
  - title: the book / paper / resource title.
  - authors[]: ordered list of author / editor names.
  - format: ISBN_13 / DOI / URL / INTERNAL_REF / OTHER.
  - isbn_13: 13-digit ISBN (when format = ISBN_13), must match `^\\d{13}$`.
  - doi: Digital Object Identifier (without 'doi:' prefix), when format = DOI.
  - url: free-form URL, when format = URL or DOI.
  - is_essential: true if the reading is marked 'essential' or 'core'; false if 'recommended' or 'further reading'.

  Special considerations:
  - ISBN-13 validation: every ISBN_13 record MUST have a valid isbn_13 (regex `^\\d{13}$`). The deterministic eval will fail if the regex does not match.
  - DOIs SHOULD include the URL prefix (e.g. 'https://doi.org/10.1038/nature12373') in the `url` field.

  {{ ctx.output_format }}
"#
}

function ExtractUoGCodeCell(
  cell_source: string,
  cell_output: string?,
  cell_index: int,
  module_code: string
) -> UoGCodeCell {
  client ExtractEn
  prompt #"
  {{ _.role("user") }}
  You are an expert at extracting structured per-cell metadata from a University of Galway (or Irish university) personal-archive code cell (Jupyter notebook `.ipynb` cell, or a function in a `.py` file).

  Module code: {{ module_code }}
  Cell index: {{ cell_index }}

  Source:
  ```
  {{ cell_source }}
  ```

  Output:
  ```
  {{ cell_output }}
  ```

  Extract a single `UoGCodeCell` record:
  - cell_id: kebab-case slug, e.g. '<module>_<notebook>_<cell_index>'.
  - module_code: '{{ module_code }}'.
  - notebook_path: the path to the notebook / file the cell lives in (placeholder 'unknown' if not provided).
  - cell_index: {{ cell_index }}.
  - cell_type: 'code' (or 'markdown' if it's a markdown cell).
  - source_text: the full cell source code.
  - runtime_seconds: if the output is text-only, leave null; if the cell's runtime is visible in the notebook metadata, include it.
  - output_text: the cell's output (text representation).
  - demonstrates_topics: 1-5 topic tags (lower-snake-case), e.g. ['rest_api_design', 'flask', 'routing'].

  Special considerations:
  - Code cells MUST include 1-5 topic tags that describe what the cell demonstrates.
  - Preserve the source code verbatim — do NOT sanitise or rewrite.

  {{ ctx.output_format }}
"#

}

function ExtractStudentTranscript(
  pdf_text: string,
  student_id: string
) -> StudentTranscriptRow[] {
  client ExtractEn
  prompt #"
  {{ _.role("user") }}
  You are an expert at extracting structured per-module transcript rows from a University of Galway (or Irish university) official academic transcript PDF.

  Student ID: {{ student_id }}

  Transcript body (markdown or plain text):
  {{ pdf_text }}

  Output ONE `StudentTranscriptRow` per module per academic year. Each row MUST have:
  - student_id: '{{ student_id }}'.
  - institution_id: 'ie-university-galway' (or the equivalent kebab-case id for any other Irish university: 'ie-university-trinity' for TCD, 'ie-ucd' for UCD, etc.).
  - programme_code: the programme code, e.g. 'BAED' (BA Education), 'BAMAS' (BA Mathematical Science), 'HDSD' (Higher Diploma in Software Design), 'DIPC1' (Diploma in Irish C1).
  - programme_title: the full programme title, e.g. 'Bachelor of Arts (Education, Mathematics)'.
  - module_code: the module code, e.g. 'MA216', 'ED305', 'CT511', 'GA101'.
  - module_title: the module title.
  - ects: the ECTS credit value (e.g. 5, 10).
  - nfq_level: the NFQ level (6..10).
  - academic_year: the academic year the row applies to (e.g. 2018 for '2017-18').
  - semester: 'semester_1', 'semester_2', or 'year_long'.
  - grade: the grade, e.g. 'A1', 'B2', 'C3', 'D1', 'F', 'PASS', 'DISTINCTION', 'MERIT'.
  - is_honours: true if the module is at Honours level (NFQ 8 Hons).
  - is_resit: true if this row represents a resit attempt.
  - transcript_pdf: the absolute path to the transcript PDF (placeholder 'unknown' if not provided).
  - source_url: the canonical URL this transcript was scraped from, or null.
  - scraped_at: ISO-8601 timestamp.
  - confidence: 0.0-1.0.

  Special considerations:
  - Output one row per (student, module, academic_year) tuple — DO NOT deduplicate by module_code alone.
  - The transcript_pdf field is the ground truth source — every row joins back to it via the `transcript_pdf` column.

  {{ ctx.output_format }}
"#
}

function BuildModuleSummary(
  artefact_rows: UoGPersonalArchiveArtefact[],
  assignment_rows: UoGAssignment[],
  topic_rows: UoGTopic[],
  transcript_rows: StudentTranscriptRow[],
  module_code: string
) -> UoGModuleSummary {
  client ExtractEn
  prompt #"
  {{ _.role("user") }}
  You are an expert at building the per-module summary row for a University of Galway (or Irish university) personal-archive pipeline.

  Module code: {{ module_code }}

  Input rows (already typed by the upstream BAML functions):
  - artefact_rows: {{ artefact_rows }}
  - assignment_rows: {{ assignment_rows }}
  - topic_rows: {{ topic_rows }}
  - transcript_rows: {{ transcript_rows }}

  Build a single `UoGModuleSummary` row that aggregates the 4 inputs:
  - module_code: '{{ module_code }}'.
  - module_title: the most common module_title from artefact_rows, or null if absent.
  - programme_code: the most common programme_code from artefact_rows, or null.
  - artefact_count: count of artefact_rows for this module_code.
  - assignment_count: count of assignment_rows for this module_code.
  - question_count: sum of questions across all assignments.
  - topic_count: count of topic_rows for this module_code.
  - code_cell_count: 0 unless code_cell_rows are passed.
  - reading_count: 0 unless reading_rows are passed.
  - transcript_grade: the transcript grade from the matching transcript_row (if any).
  - transcript_academic_year: the academic_year from the matching transcript_row.
  - ca_marks: the CA marks for this module_code (placeholder list if not passed).
  - topic_names: the topic_name[] across all topics.
  - first_artefact_year: the earliest academic_year across artefact_rows.
  - last_artefact_year: the latest academic_year across artefact_rows.
  - confidence: 0.0-1.0 (the minimum across the input confidences).

  Special considerations:
  - The transcript_grade + transcript_academic_year is the GROUND TRUTH join target — it is the answer to "what grade did the student actually get on the official transcript?"
  - The ca_marks list is the TYPED INPUT — it is the answer to "what CA marks did the student get for this module?"

  {{ ctx.output_format }}
"#

}
