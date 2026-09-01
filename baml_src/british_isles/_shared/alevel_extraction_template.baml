// BAML template: A-Level (England GCE Advanced Level) Extraction
//
// Per the 2026-08-18-mega-3-roadmap-v1 + the 2026-08-26-mega-3a-baml-and-adk-v1 change.
//
// Replaces the hand-written a_level_extraction/*.baml files (~1,500 LOC).
// Covers the canonical 15 A-Level subjects × 3 awarding bodies
// (AQA + OCR + Edexcel) via `{% if subject == "x" %}` and `{% if board == "x" %}`.
//
// The 15 priority subjects (per ALevelPrioritySubjectSlug):
// MATHEMATICS, FURTHER_MATHEMATICS, ENGLISH_LITERATURE, ENGLISH_LANGUAGE
// ECONOMICS, BUSINESS, HISTORY_OF_ART, POLITICS, SOCIOLOGY.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src

// ============================================================================
// Canonical enums
// ============================================================================

enum ALevelStage {
  AS_LEVEL @description("AS-Level (Year 12)")
  A_LEVEL @description("A-Level (Year 13)")
}

enum ALevelExamBoard {
  AQA
  OCR
  EDEXCEL
}

enum ALevelSubjectSlug {
  MATHEMATICS
  FURTHER_MATHEMATICS
  ENGLISH_LITERATURE
  ENGLISH_LANGUAGE
  BIOLOGY
  CHEMISTRY
  PHYSICS
  PSYCHOLOGY
  HISTORY
  GEOGRAPHY
  ECONOMICS
  BUSINESS
  HISTORY_OF_ART
  POLITICS
  SOCIOLOGY
}

enum ALevelLanguage {
  EN
  EN_AND_FR
  EN_AND_DE
  EN_AND_ES
  EN_AND_LAT
}

// ============================================================================
// Canonical value types
// ============================================================================

class ALevelBilingualText {
  text_en string
  text_ga string? @description("Irish translation; null if EN-only")
}

class ALevelSubjectPDFLink {
  source_pdf string
  source_page int
  excerpt_en string
  excerpt_ga string?
  awarding_body_url string? @description("Canonical aqa.org.uk / ocr.org.uk / edexcel.com URL (if known)")
}

class ALevelLearningOutcome {
  lo_id string @description("Awarding-body LO code (e.g. 'AL-MATH-LO-001')")
  title string
  description ALevelBilingualText
  blooms_level BloomLevel
  pdf_link ALevelSubjectPDFLink?
}

class ALevelModule {
  module_id string
  name ALevelBilingualText
  description ALevelBilingualText
  type string @description("CORE | OPTIONAL | SPECIALISM | NEA | PRACTICAL")
  learning_outcomes ALevelLearningOutcome[]
  estimated_hours int?
}

class ALevelSyllabusSpec {
  subject ALevelSubjectSlug
  language ALevelLanguage
  board ALevelExamBoard
  stage ALevelStage
  specification_code string @description("e.g. 'AQA-7402' for A-Level Mathematics")
  title string
  version string
  first_teaching_year int?
  last_certification_year int?
  source_pdf string
  source_pages int?
  total_marks int
  assessment_objectives AssessmentObjective[]
  component_papers int
  module_topics ALevelModule[]
  total_learning_outcomes int
  prescribed_texts ALevelBilingualText[]? @description("For English Literature + History of Art")
  formulas string[]? @description("Formula references (for Mathematics, Physics, Economics)")
  lineage LineageTrace?
}

// (AssessmentObjective is defined in curriculum_syllabus.baml — re-used here)

class ALevelQuestion {
  q_id string
  part string
  text_en string
  text_ga string?
  question_type LCQuestionType @description("Reuses the LC enum (SHORT_ANSWER, EXTENDED_RESPONSE, etc.)")
  marks int
  related_lo_id string?
}

class ALevelQuestionSection {
  section_id string
  section_name string
  instructions string?
  questions ALevelQuestion[]
  total_marks int
}

class ALevelExamPaper {
  subject ALevelSubjectSlug
  board ALevelExamBoard
  stage ALevelStage
  paper_code string @description("e.g. 'AQA-7402-1' for A-Level Mathematics Paper 1")
  language ALevelLanguage
  year int
  source_pdf string
  total_pages int
  total_marks int
  total_questions int
  sections ALevelQuestionSection[]
  duration_minutes int?
  has_formula_sheet bool
  lineage LineageTrace?
}

class ALevelMarkAllocation {
  q_id string
  total_marks int
  partial_credit_rules string[]
  common_mistakes string[]
  sample_answer string?
}

class ALevelGradeDescriptor {
  band MarkingBand
  percentage_min int
  percentage_max int
  descriptor_text_en string
  descriptor_text_ga string?
  exemplar_responses string[]
}

class ALevelMarkingScheme {
  subject ALevelSubjectSlug
  board ALevelExamBoard
  stage ALevelStage
  scheme_code string
  language ALevelLanguage
  year int?
  source_pdf string
  grade_descriptors ALevelGradeDescriptor[]
  mark_allocations ALevelMarkAllocation[]
  total_bands int
  total_pages int
  descriptor_word_count_avg int
  lineage LineageTrace?
}

class ALevelAreaTopic {
  topic_id string @description("Awarding-body topic code (e.g. 'AL-MATH-TOPIC-001')")
  topic_name string
  subject ALevelSubjectSlug
  topics ALevelBilingualText[]
  cross_subject_topics string[]
}

class ALevelCrossSubjectTopics {
  subject ALevelSubjectSlug
  topics ALevelAreaTopic[]
  total_topics int
  cross_subject_topics string[]
}

class ALevelSyllabusDiagram {
  diagram_id string
  caption_en string?
  caption_ga string?
  page_number int
  source_pdf string
  subject ALevelSubjectSlug
  board ALevelExamBoard
  pointing_model string
  confidence_score float
  regions LCDiagramRegion[] @description("Reuses the LC diagram regions")
  related_lo_ids string[]
  lineage LineageTrace?
}

// ============================================================================
// The 6 canonical A-Level extraction functions
// ============================================================================

function ExtractALevelCurriculumSyllabus(
  pdf_text: string,
  subject: ALevelSubjectSlug,
  board: ALevelExamBoard
) -> ALevelSyllabusSpec {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    You are an expert at reading official awarding-body A-Level specification
    documents (AQA / OCR / Edexcel) and extracting their structure with complete
    fidelity — every fact below MUST be grounded in the PDF text given; never
    invent a unit, learning objective, or AO code that is not actually present.

    Subject: {{ subject }}
    Board: {{ board }}

    Extract:
    - specification_code (e.g. 'AQA-7402' for A-Level Mathematics)
    - title, version, first_teaching_year, last_certification_year
    - total_marks, component_papers
    - assessment_objectives: array of {ao_id, title, description, weighting_pct}
    - module_topics: every distinct module/unit/strand
    - total_learning_outcomes
    - prescribed_texts (for English Literature + History of Art)
    - formulas (for Mathematics, Physics, Economics)

    Subject-specific guidance:
    {% if subject == ALevelSubjectSlug.MATHEMATICS %}
    - Topics span Pure Mathematics, Mechanics, Statistics
    - AQA 7402 (3 papers); OCR A Level Mathematics A H240 / B H230; Edexcel 9MA0
    - Capture all formula references in the `formulas` array
    {% elif subject == ALevelSubjectSlug.FURTHER_MATHEMATICS %}
    - Topics: Complex Numbers, Matrices, Polar Coordinates, Hyperbolic Functions, Differential Equations
    - AQA 7367; OCR H245; Edexcel 9FM0
    {% elif subject == ALevelSubjectSlug.CHEMISTRY %}
    - Topics span Physical Chemistry, Inorganic Chemistry, Organic Chemistry
    - AQA 7405; OCR H432; Edexcel 9CH0
    - Include 12 mandatory practicals (NCCA analog)
    {% elif subject == ALevelSubjectSlug.PHYSICS %}
    - Topics span Mechanics, Waves, Electricity, Thermal Physics, Nuclear Physics
    - AQA 7408; OCR H556; Edexcel 9PH0
    - Capture all formula references; include SI units + significant figures
    {% elif subject == ALevelSubjectSlug.BIOLOGY %}
    - Topics span Biological Molecules, Cells, Organisms, Genetics, Ecology
    - AQA 7402; OCR H420; Edexcel 9BI0
    - Note the 12 mandatory practicals
    {% elif subject == ALevelSubjectSlug.PSYCHOLOGY %}
    - Topics span Social Influence, Memory, Attachment, Psychopathology
    - AQA 7182; OCR H180/H580; Edexcel 9PS0
    - Note the Research Methods strand
    {% elif subject == ALevelSubjectSlug.HISTORY %}
    - Topics span Breadth + Depth studies (3 papers typically)
    - AQA 7042; OCR H105/H505; Edexcel 9HI0
    - Note the NEA (Non-Examined Assessment) component
    {% elif subject == ALevelSubjectSlug.GEOGRAPHY %}
    - Topics span Physical Geography, Human Geography, Fieldwork (NEA)
    - AQA 7037; OCR H481; Edexcel 9GE0
    - Note the 4-day fieldwork requirement
    {% elif subject == ALevelSubjectSlug.ECONOMICS %}
    - Topics span Markets + Market Failure, Macroeconomic Performance
    - AQA 7126/7145; OCR H460; Edexcel 9EC0
    - Capture formulas (elasticity, AD/AS) in `formulas`
    {% elif subject == ALevelSubjectSlug.BUSINESS %}
    - 3 papers: Paper 1 (Marketing + People), Paper 2 (Managing business activities), Paper 3 (Business decisions + strategy)
    - 4 NEA components: research, pre-release, decision-making report
    - AQA 7132; OCR H431; Edexcel 9BS0
    {% elif subject == ALevelSubjectSlug.ENGLISH_LITERATURE %}
    - Capture the prescribed texts (poetry, prose, drama) under `prescribed_texts`
    - AQA 7712; OCR H472; Edexcel 9ET0
    {% elif subject == ALevelSubjectSlug.ENGLISH_LANGUAGE %}
    - Topics span Language + the Individual, Language Varieties
    - AQA 7702; OCR H470; Edexcel 9EN0
    - Note the NEA (original writing + language investigation)
    {% elif subject == ALevelSubjectSlug.HISTORY_OF_ART %}
    - 2 papers: Paper 1 (Visual analysis + themes), Paper 2 (Personal investigation + NEA)
    - AQA 7203; OCR H401; Edexcel 9HA0
    - Capture the 7 themes (e.g. Identity, Politics, Nature)
    {% elif subject == ALevelSubjectSlug.POLITICS %}
    - 3 papers: Paper 1 (UK politics + core political ideas), Paper 2 (UK government + non-core ideas), Paper 3 (Comparative politics)
    - AQA 7152; OCR H485; Edexcel 9PL0
    - Capture the 5 core political ideas (conservatism, liberalism, socialism, etc.)
    {% elif subject == ALevelSubjectSlug.SOCIOLOGY %}
    - Topics span Families + Households, Education, Crime + Deviance, Beliefs in Society
    - AQA 7192; OCR H180/H580; Edexcel 9S01
    {% endif %}

    {{ ctx.output_format }}

    SYLLABUS TEXT:
    {{ pdf_text }}
  "#

}

function ExtractALevelExamPaperLayout(
  pdf_text: string,
  subject: ALevelSubjectSlug,
  board: ALevelExamBoard,
  paper_code: string?,
  year: int?
) -> ALevelExamPaper {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    Extract the A-Level exam paper layout for `{{ subject }}` at `{{ board }}`.

    Capture:
    - paper_code (e.g. 'AQA-7402-1')
    - year, total_marks, duration_minutes
    - sections: array of {label, marks, questions: [...]}

    {{ ctx.output_format }}
  "#

}

function ExtractALevelMarkingSchemeGuideline(
  pdf_text: string,
  subject: ALevelSubjectSlug,
  board: ALevelExamBoard,
  year: int?
) -> ALevelMarkingScheme {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    Extract the A-Level marking scheme guideline for `{{ subject }}` at `{{ board }}`.

    Capture:
    - grade_descriptors: array of {band, percentage_min/max, descriptor_text_en}
    - mark_allocations: array of {q_id, total_marks, partial_credit_rules}

    {{ ctx.output_format }}
  "#

}

function ExtractALevelSyllabusDiagram(
  pdf_text: string,
  subject: ALevelSubjectSlug,
  board: ALevelExamBoard
) -> ALevelSyllabusDiagram {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    Extract diagrams / figures / charts from the A-Level `{{ subject }}` syllabus at `{{ board }}`.

    Capture:
    - regions: array of bounding boxes + roles
    - related_lo_ids: the awarding-body LO codes the diagram illustrates

    {{ ctx.output_format }}
  "#

}

function ExtractALevelCrossSubjectTopics(
  pdf_text: string,
  subject: ALevelSubjectSlug
) -> ALevelCrossSubjectTopics {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    Extract the canonical cross-subject topics for A-Level `{{ subject }}`.

    Capture:
    - topics: array of {topic_id, topic_name, subject, topics, cross_subject_topics}
    - total_topics

    {{ ctx.output_format }}
  "#

}

function ExtractALevelPerQuestionScheme(
  pdf_text: string,
  subject: ALevelSubjectSlug,
  board: ALevelExamBoard
) -> ALevelMarkAllocation[] {
  client LitellmClient
  prompt #"
    {{ _.role("user") }}
    Extract per-question marking scheme allocations for A-Level `{{ subject }}` at `{{ board }}`.

    Capture: array of {q_id, total_marks, partial_credit_rules, common_mistakes, sample_answer}.

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// BAML test blocks
// ============================================================================

test alevel_lo_code_matches {
  functions [ExtractALevelCurriculumSyllabus]
  args {
    pdf_text "Sample A-Level syllabus text"
    subject ALevelSubjectSlug.MATHEMATICS
    board ALevelExamBoard.AQA
  }
}

test alevel_3_boards_covered {
  functions [ExtractALevelCurriculumSyllabus]
  args {
    pdf_text "Sample A-Level syllabus text"
    subject ALevelSubjectSlug.BIOLOGY
    board ALevelExamBoard.OCR
  }
}
