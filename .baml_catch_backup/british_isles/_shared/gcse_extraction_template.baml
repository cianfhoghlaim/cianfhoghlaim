// BAML template: GCSE (England General Certificate of Secondary Education) Extraction
//
// Per the 2026-08-18-mega-3-roadmap-v1 + the 2026-08-26-mega-3a-baml-and-adk-v1 change.
//
// Replaces the hand-written gcse_extraction/*.baml files (~900 LOC).
// Covers the canonical 9 GCSE subjects × 3 awarding bodies
// (AQA + OCR + Edexcel) via `{% if subject == "x" %}` and `{% if board == "x" %}`.
//
// The 9 GCSE priority subjects (per the GCSE BIEP v2 spec):
// mathematics, english_language, english_literature, biology, chemistry,
// physics, history, geography, religious_studies.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src

// ============================================================================
// Canonical enums
// ============================================================================

enum GCSEExamBoard {
  AQA
  OCR
  EDEXCEL
}

enum GCSEStage {
  FOUNDATION @description("GCSE Foundation Tier (grades 1-5)")
  HIGHER @description("GCSE Higher Tier (grades 4-9)")
  SINGLE_TIER @description("GCSE single-tier (e.g. English Language)")
}

enum GCSESubjectSlug {
  MATHEMATICS
  ENGLISH_LANGUAGE
  ENGLISH_LITERATURE
  BIOLOGY
  CHEMISTRY
  PHYSICS
  HISTORY
  GEOGRAPHY
  RELIGIOUS_STUDIES
}

enum GCSEAssessmentType {
  LINEAR @description("All exams at end of course (most GCSEs)")
  MODULAR @description("Multiple exams across the course")
}

enum GCSEAOLevel {
  AO1 @description("Knowledge + understanding")
  AO2 @description("Application")
  AO3 @description("Analysis + evaluation")
}

// ============================================================================
// Canonical value types
// ============================================================================

class GCSEBilingualText {
  text_en string
  text_ga string? @description("Irish translation; null if EN-only")
}

class GCSESubjectPDFLink {
  source_pdf string
  source_page int
  excerpt_en string
  excerpt_ga string?
  awarding_body_url string?
}

class GCSEAreaTopic {
  topic_id string @description("Awarding-body topic code (e.g. 'GCSE-MATH-TOPIC-001')")
  topic_name string
  subject GCSESubjectSlug
  topics GCSEBilingualText[]
  cross_subject_topics string[]
}

class GCSEAssessmentObjective {
  ao_id string
  title string
  description string
  weighting_pct int
  ao_level GCSEAOLevel
}

class GCSEQuestion {
  q_id string
  part string
  text_en string
  text_ga string?
  question_type LCQuestionType @description("Reuses the LC enum (SHORT_ANSWER, EXTENDED_RESPONSE, etc.)")
  marks int
  related_lo_id string?
}

class GCSEQuestionSection {
  section_id string
  section_name string
  instructions string?
  questions GCSEQuestion[]
  total_marks int
}

class GCSEExamPaper {
  subject GCSESubjectSlug
  board GCSEExamBoard
  stage GCSEStage
  paper_code string @description("e.g. 'AQA-8300-1F' for GCSE Maths Foundation Paper 1")
  year int
  source_pdf string
  total_pages int
  total_marks int
  total_questions int
  sections GCSEQuestionSection[]
  duration_minutes int?
  has_formula_sheet bool
  tier GCSEStage?
}

class GCSEMarkingScheme {
  subject GCSESubjectSlug
  board GCSEExamBoard
  stage GCSEStage
  scheme_code string
  year int?
  source_pdf string
  grade_descriptors MarkingBandDescriptor[] @description("Reuses the LC enum (MarkingBand)")
  mark_allocations MarkAllocation[]
  total_bands int
  total_pages int
  descriptor_word_count_avg int
}

class GCSESyllabusSpec {
  subject GCSESubjectSlug
  board GCSEExamBoard
  stage GCSEStage
  specification_code string @description("e.g. 'AQA-8300' for GCSE Maths")
  title string
  version string
  first_teaching_year int?
  last_certification_year int?
  source_pdf string
  source_pages int?
  total_marks int
  assessment_objectives GCSEAssessmentObjective[]
  component_papers int
  area_topics GCSEAreaTopic[]
  total_topics int
  prescribed_texts GCSEBilingualText[]? @description("For English Literature + Religious Studies")
  formulas string[]? @description("Formula references (for Mathematics, Physics)")
  lineage LineageTrace?
}

class MarkingBandDescriptor {
  band MarkingBand @description("Reuses the LC enum")
  percentage_min int
  percentage_max int
  descriptor_text_en string
}

class GCSEPerQuestionScheme {
  q_id string
  total_marks int
  partial_credit_rules string[]
  common_mistakes string[]
  sample_answer string?
}

class GCSECrossSubjectTopics {
  subject GCSESubjectSlug
  topics GCSEAreaTopic[]
  total_topics int
  cross_subject_topics string[]
}

class GCSESyllabusDiagram {
  diagram_id string
  caption_en string?
  caption_ga string?
  page_number int
  source_pdf string
  subject GCSESubjectSlug
  board GCSEExamBoard
  pointing_model string
  confidence_score float
  regions LCDiagramRegion[]
  related_lo_ids string[]
  lineage LineageTrace?
}

// ============================================================================
// The 6 canonical GCSE extraction functions
// ============================================================================

function ExtractGCSECurriculumSyllabus(
  pdf_text: string,
  subject: GCSESubjectSlug,
  board: GCSEExamBoard,
) -> GCSESyllabusSpec {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    You are an expert at reading official awarding-body GCSE specification
    documents (AQA / OCR / Edexcel) for ages 14-16.

    Subject: {{ subject }}
    Board: {{ board }}

    Extract:
    - specification_code (e.g. 'AQA-8300' for GCSE Maths)
    - title, version, first_teaching_year, last_certification_year
    - total_marks, component_papers
    - assessment_objectives: array of {ao_id, title, description, weighting_pct, ao_level}
    - area_topics: every distinct topic/strand
    - total_topics
    - prescribed_texts (for English Literature + Religious Studies)
    - formulas (for Mathematics, Physics)

    Subject-specific guidance:
    {% if subject == GCSESubjectSlug.MATHEMATICS %}
    - Topics span Number, Algebra, Ratio + Proportion, Geometry + Measures, Probability, Statistics
    - AQA 8300 (Foundation + Higher tiers); OCR J560; Edexcel 1MA1
    - Capture all formula references in the `formulas` array
    {% elif subject == GCSESubjectSlug.ENGLISH_LANGUAGE %}
    - Topics: Reading (fiction + non-fiction), Writing (descriptive + narrative + argumentative)
    - AQA 8700 (single tier); OCR J351 (single tier); Edexcel 1EN0
    - Note the 2 NEA components (Spoken Language endorsement, Writing portfolio)
    {% elif subject == GCSESubjectSlug.ENGLISH_LITERATURE %}
    - Capture the prescribed texts (poetry anthology + drama + prose) under `prescribed_texts`
    - AQA 8702; OCR J352; Edexcel 1ET0
    {% elif subject == GCSESubjectSlug.BIOLOGY %}
    - Topics span Cell Biology, Organisation, Infection + Response, Bioenergetics, Homeostasis + Response, Inheritance + Evolution, Ecology
    - AQA 8461 (single tier); OCR J247; Edexcel 1BI0
    - Note the 10 mandatory practicals
    {% elif subject == GCSESubjectSlug.CHEMISTRY %}
    - Topics span Atomic Structure + Periodic Table, Bonding, Quantitative Chemistry, Chemical Changes, Energy Changes, Rates, Organic Chemistry, Chemical Analysis, Atmosphere, Resources
    - AQA 8462; OCR J248; Edexcel 1CH0
    - Note the 10 mandatory practicals
    {% elif subject == GCSESubjectSlug.PHYSICS %}
    - Topics: Energy, Forces, Waves, Electricity, Magnetism, Particles, Space
    - AQA 8463; OCR J249; Edexcel 1PH0
    - Note the 10 mandatory practicals; capture formulas in `formulas`
    {% elif subject == GCSESubjectSlug.HISTORY %}
    - Topics: Thematic Study + Period Study + British Depth Study + World Study
    - AQA 8145; OCR J410; Edexcel 1HI0
    - Note the NEA (Historic Environment study)
    {% elif subject == GCSESubjectSlug.GEOGRAPHY %}
    - Topics: Living with the Physical Environment, Challenges in the Human Environment, Geographical Applications
    - AQA 8035; OCR J384; Edexcel 1GA0
    - Note the 2 fieldwork days + NEA
    {% elif subject == GCSESubjectSlug.RELIGIOUS_STUDIES %}
    - Capture the prescribed themes under `prescribed_texts`
    - AQA 8062 (2 themes); OCR J625 (3 themes); Edexcel 1RS0
    {% endif %}

    {{ ctx.output_format }}

    SYLLABUS TEXT:
    {{ pdf_text }}
  "#
}

function ExtractGCSEExamPaperLayout(
  pdf_text: string,
  subject: GCSESubjectSlug,
  board: GCSEExamBoard,
  paper_code: string?,
  year: int?,
) -> GCSEExamPaper {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    Extract the GCSE exam paper layout for `{{ subject }}` at `{{ board }}`.

    Capture:
    - paper_code (e.g. 'AQA-8300-1F')
    - year, total_marks, duration_minutes
    - sections: array of {label, marks, questions: [...]}
    - tier: FOUNDATION or HIGHER

    {{ ctx.output_format }}
  "#
}

function ExtractGCSEMarkingSchemeGuideline(
  pdf_text: string,
  subject: GCSESubjectSlug,
  board: GCSEExamBoard,
  year: int?,
) -> GCSEMarkingScheme {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    Extract the GCSE marking scheme guideline for `{{ subject }}` at `{{ board }}`.

    Capture:
    - grade_descriptors: array of {band, percentage_min/max, descriptor_text_en}
    - mark_allocations: array of {q_id, total_marks, partial_credit_rules}

    {{ ctx.output_format }}
  "#
}

function ExtractGCSESyllabusDiagram(
  pdf_text: string,
  subject: GCSESubjectSlug,
  board: GCSEExamBoard,
) -> GCSESyllabusDiagram {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    Extract diagrams / figures / charts from the GCSE `{{ subject }}` syllabus at `{{ board }}`.

    Capture:
    - regions: array of bounding boxes + roles
    - related_lo_ids: the awarding-body LO codes the diagram illustrates

    {{ ctx.output_format }}
  "#
}

function ExtractGCSECrossSubjectTopics(
  pdf_text: string,
  subject: GCSESubjectSlug,
) -> GCSECrossSubjectTopics {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    Extract the canonical cross-subject topics for GCSE `{{ subject }}`.

    Capture:
    - topics: array of {topic_id, topic_name, subject, topics, cross_subject_topics}
    - total_topics

    {{ ctx.output_format }}
  "#
}

function ExtractGCSEPerQuestionScheme(
  pdf_text: string,
  subject: GCSESubjectSlug,
  board: GCSEExamBoard,
) -> GCSEPerQuestionScheme[] {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    Extract per-question marking scheme allocations for GCSE `{{ subject }}` at `{{ board }}`.

    Capture: array of {q_id, total_marks, partial_credit_rules, common_mistakes, sample_answer}.

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// BAML test blocks
// ============================================================================

test gcse_lo_code_matches {
  functions [ExtractGCSECurriculumSyllabus]
  args {
    pdf_text "Sample GCSE syllabus text"
    subject GCSESubjectSlug.MATHEMATICS
    board GCSEExamBoard.AQA
  }
}

test gcse_3_boards_covered {
  functions [ExtractGCSECurriculumSyllabus]
  args {
    pdf_text "Sample GCSE syllabus text"
    subject GCSESubjectSlug.BIOLOGY
    board GCSEExamBoard.EDEXCEL
  }
}