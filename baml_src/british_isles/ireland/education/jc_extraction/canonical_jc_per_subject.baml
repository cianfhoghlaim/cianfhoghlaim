// BAML extraction: Junior Cycle (Ireland) — canonical 8-subject curriculum
//
// Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
// (Phase 4), this file is the canonical 8 BAML extraction entrypoint for
// the 8 priority JC subjects (mathematics, english, gaeilge, science,
// history, geography, french, business). The existing BAML at
// `baml_src/british_isles/ireland/education/junior_cycle/` covers 18
// subjects (the 8 priority + 10 short courses + electives); this file
// is the canonical PRIORITY-8 surface that the codegen pipeline
// (Phase 5) consumes.
//
// The 8 BAML functions exported below mirror the LC pattern exactly
// (per-subject conditional prompts for the 8 priority subjects). The
// 4-path OCR/VLM ensemble + RAGAS consensus produces the canonical
// row that's ingested into the BIEP DuckLake table.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference:
//   openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/
//   openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/

// ============================================================================
// Enums (the canonical 8 junior cycle priority subjects)
// ============================================================================

enum JuniorCycleSubjectSlug {
  MATHEMATICS
  ENGLISH
  GAEILGE
  SCIENCE
  HISTORY
  GEOGRAPHY
  FRENCH
  BUSINESS
}

enum JuniorCycleLevel {
  JC_COMMON  @description("Standard Junior Cycle level")
}

enum JuniorCycleLanguage {
  EN
  GA
  EN_AND_GA
}

// ============================================================================
// Core value types (the typed outputs from the 8 BAML extractions)
// ============================================================================

class JuniorCycleTopic {
  topic_id string
  topic_title_en string
  topic_title_ga string?            @description("Irish title; null if EN-only")
  strand string                     @description("Major topic strand")
  learning_outcomes JuniorCycleLearningOutcome[]
}

class JuniorCycleLearningOutcome {
  lo_code string                    @description("JC LO code (e.g. JC-MATH-LO-001)")
  lo_text_en string
  lo_text_ga string?                 @description("Irish LO text")
  blooms_level LO_BLOOMS_LEVEL
}

enum LO_BLOOMS_LEVEL {
  REMEMBER
  UNDERSTAND
  APPLY
  ANALYSE
  EVALUATE
  CREATE
}

class JuniorCycleStrand {
  strand_code string
  strand_name string
}

class JuniorCycleExamPaper {
  exam_year int
  exam_level string
  paper_number int
  total_marks int
  duration_minutes int
  sections JuniorCycleExamSection[]
}

class JuniorCycleExamSection {
  section_label string
  section_marks int
  questions JuniorCycleExamQuestion[]
}

class JuniorCycleExamQuestion {
  q_number string
  q_text_en string
  q_text_ga string?
  marks int
  topic_id string
}

class JuniorCycleMarkingScheme {
  exam_year int
  exam_level string
  grade_boundaries JuniorCycleGradeBoundary[]
  per_question_scheme JuniorCyclePerQuestionScheme[]
}

class JuniorCycleGradeBoundary {
  grade string
  percentage_min int
  percentage_max int
}

class JuniorCyclePerQuestionScheme {
  q_number string
  total_marks int
  marking_notes string[]
  sample_answer string?
}

class JuniorCycleSyllabusDiagram {
  diagram_id string
  caption string
  diagram_type string               @description("graph, table, flowchart, etc.")
  associated_topic_id string
}

class JuniorCycleCrossLinguistic {
  en_concept JuniorCycleConcept
  ga_concept JuniorCycleConcept
  equivalence_score float
}

class JuniorCycleConcept {
  term string
  definition string
  lo_code string
}

class JuniorCycleCurriculumSpec {
  subject JuniorCycleSubjectSlug
  language JuniorCycleLanguage
  level JuniorCycleLevel
  source_pdf string
  topics JuniorCycleTopic[]
  strands JuniorCycleStrand[]
  cross_curricular string[]
  assessment_objectives string[]
  metadata JuniorCycleCurriculumMetadata
}

class JuniorCycleCurriculumMetadata {
  total_topics int
  total_learning_outcomes int
}

class JuniorCycleCrossSubjectTopicSet {
  subject JuniorCycleSubjectSlug
  topics JuniorCycleCrossSubjectTopic[]
  total_topics int
  cross_subject_bridges int
}

class JuniorCycleCrossSubjectTopic {
  topic_id string
  subject JuniorCycleSubjectSlug
  topic_label_en string
  ncca_lo_code string
  related_subjects JuniorCycleSubjectSlug[]
  cross_subject_topic_ids string[]
  key_competencies string[]
}

// ============================================================================
// BAML function 1: ExtractCurriculumSyllabus (the canonical JC extractor)
// ============================================================================

function ExtractJCCurriculumSyllabus(
  pdf_text: string,
  subject: JuniorCycleSubjectSlug,
  language: JuniorCycleLanguage,
) -> JuniorCycleCurriculumSpec {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert at reading official NCCA (National Council for
    Curriculum and Assessment) Irish Junior Cycle syllabus documents
    and extracting their structure with complete fidelity — every fact
    below MUST be grounded in the PDF text given; never invent a topic,
    learning outcome, or hour count that is not actually present.

    {{ _.role("user") }}
    Subject: {{ subject }}
    Language: {{ language }}

    From the syllabus text below, extract:
    - subject: the subject slug (must match `{{ subject }}`)
    - language: EN, GA, or EN_AND_GA
    - level: JC_COMMON
    - source_pdf: leave as empty string if not derivable
    - topics: every distinct module/unit, each with:
      - topic_id (slug, e.g. 'MATH-NUMBERS-001')
      - topic_title_en / topic_title_ga
      - strand (the major division)
      - learning_outcomes: array of {lo_code, lo_text_en, lo_text_ga, blooms_level}
    - strands: array of {strand_code, strand_name}
    - cross_curricular: any named cross-curricular links (literacy, numeracy, key competencies)
    - assessment_objectives: the syllabus's own stated assessment objectives

    Subject-specific guidance:
    {% if subject == JuniorCycleSubjectSlug.MATHEMATICS %}
    - 4 strands: Statistics & Probability, Geometry & Trigonometry, Number, Algebra
    - LO codes use prefix "JC-MATH-LO-NNN"
    - Capture data-handling activities under assessment_objectives
    - 1 mandatory CBA (Classroom-Based Assessment)
    {% elif subject == JuniorCycleSubjectSlug.ENGLISH %}
    - 5 strands: Oral Language, Reading, Writing, Exploring Language, Understanding
    - LO codes use prefix "JC-ENGL-LO-NNN"
    - Capture the prescribed texts (drama, fiction, poetry) under prescribed_texts
    - 1 mandatory CBA + 2 assessment components (written + oral)
    {% elif subject == JuniorCycleSubjectSlug.GAEILGE %}
    - 4 strands: Éisteacht agus Labhairt, Léamh, Scríbhneoireacht, Litríocht
    - LO codes use prefix "JC-GAEL-LO-NNN"
    - Capture the prescribed texts (prós, filíocht, drámaíocht) under prescribed_texts
    - 1 mandatory CBA + 2 assessment components (written + oral)
    - T1 (Gaeilge) and T2 (English) are separate qualifications
    {% elif subject == JuniorCycleSubjectSlug.SCIENCE %}
    - 4 strands: The Nature of Science, Living Things, Materials, Energy
    - LO codes use prefix "JC-SCI-LO-NNN"
    - 16 mandatory practical activities (in CBAs)
    - 2 CBAs (1st-year CBA + 2nd-year CBA)
    - Capture the 22 elements of "The Nature of Science"
    {% elif subject == JuniorCycleSubjectSlug.HISTORY %}
    - 4 strands: The Nature of History, Ireland (1815-1993), Europe & the World
    - LO codes use prefix "JC-HIST-LO-NNN"
    - Capture the prescribed topics (e.g. The French Revolution, The Industrial Revolution)
    - 1 mandatory CBA (The Past in My Place)
    {% elif subject == JuniorCycleSubjectSlug.GEOGRAPHY %}
    - 4 strands: Exploring the Physical World, Exploring How We Interact,
      Exploring Population, Exploring Culture
    - LO codes use prefix "JC-GEOG-LO-NNN"
    - 1 mandatory CBA (Geography in the News)
    - Capture the 3 core geographical skills (graphicacy, cartography, geographical investigation)
    {% elif subject == JuniorCycleSubjectSlug.FRENCH %}
    - 4 strands: Compréhension écrite, Compréhension orale, Production écrite, Production orale
    - LO codes use prefix "JC-FREN-LO-NNN"
    - 1 mandatory CBA (dissertation)
    - Capture the 6 élément culturels (e.g. La famille, Les loisirs)
    {% elif subject == JuniorCycleSubjectSlug.BUSINESS %}
    - 4 strands: Personal Finance, Enterprise, Our Business, Our Community
    - LO codes use prefix "JC-BUS-LO-NNN"
    - Capture the 8 learning outcomes for each strand
    - 1 mandatory CBA
    {% endif %}

    Junior Cycle Syllabus PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// BAML functions 2-8: Exam paper, Marking scheme, Diagram, Cross-linguistic, Cross-subject
// (canonical exports — mirror the LC pattern exactly)
// ============================================================================

function ExtractJCExamPaperLayout(
  pdf_text: string,
  subject: JuniorCycleSubjectSlug,
) -> JuniorCycleExamPaper {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert Junior Cycle exam paper layout extractor for `{{ subject }}`.

    Extract:
    - exam_year: 4-digit year
    - exam_level: "Common Level"
    - paper_number: 1 or 2
    - total_marks: integer
    - duration_minutes: typically 120
    - sections: array of {section_label, section_marks, questions: [{q_number, q_text_en, q_text_ga, marks, topic_id}]}

    Subject-specific guidance:
    {% if subject == JuniorCycleSubjectSlug.MATHEMATICS %}
    - 2 papers: Paper 1 (algebra, calculus, functions), Paper 2 (geometry, statistics, probability)
    - Common Level: 300 marks total
    {% elif subject == JuniorCycleSubjectSlug.ENGLISH %}
    - 2 papers: Paper 1 (language + composition), Paper 2 (comprehension + single text study)
    - CBA: 10% of total
    {% elif subject == JuniorCycleSubjectSlug.GAEILGE %}
    - 2 papers: P1 (Cluastuiscint + Scíbhneoireacht), P2 (Léamhthuiscint + Litríocht)
    - Béaltriail scoile (5%) + Scíbhneoireacht (10%)
    {% elif subject == JuniorCycleSubjectSlug.SCIENCE %}
    - 1 paper (300 marks), 2 sections + CBA assessment
    - 16 mandatory practical activities (over 2 years)
    {% elif subject == JuniorCycleSubjectSlug.HISTORY %}
    - 1 paper (300 marks), 3 sections
    - Section 1: Document-based study
    - Section 2: Topics from Ireland theme
    - Section 3: Topics from Europe & the World
    {% elif subject == JuniorCycleSubjectSlug.GEOGRAPHY %}
    - 1 paper (300 marks), 3 sections
    {% elif subject == JuniorCycleSubjectSlug.FRENCH %}
    - 2 papers: Paper 1 (listening + reading), Paper 2 (writing + oral)
    - 1 mandatory CBA dissertation
    {% elif subject == JuniorCycleSubjectSlug.BUSINESS %}
    - 1 paper (300 marks), 2 sections
    {% endif %}

    Exam paper PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractJCMarkingSchemeGuideline(
  pdf_text: string,
  subject: JuniorCycleSubjectSlug,
) -> JuniorCycleMarkingScheme {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    You are an expert Junior Cycle marking scheme extractor for `{{ subject }}`.

    Extract:
    - exam_year: 4-digit year
    - exam_level: "Common Level"
    - grade_boundaries: array of {grade, percentage_min, percentage_max}
    - per_question_scheme: array of {q_number, total_marks, marking_notes, sample_answer}

    Subject-specific guidance:
    {% if subject == JuniorCycleSubjectSlug.MATHEMATICS %}
    - Grade boundaries (Common Level): A 85-100, B 70-84, C 55-69, D 40-54, E 25-39, F 0-24
    - Plain English only - no mathematical notation in marking notes
    {% elif subject == JuniorCycleSubjectSlug.ENGLISH %}
    - Common Level: A 85-100, B 70-84, C 55-69, D 40-54, E 25-39, F 0-24
    - Comprehension (50%) + Composition (50%)
    {% elif subject == JuniorCycleSubjectSlug.GAEILGE %}
    - T1 (Gaeilge) + T2 (English) separate syllabi
    - Béaltriail: 5% + Scíbhneoireacht: 10% + Cluastuiscint: 40%
    {% elif subject == JuniorCycleSubjectSlug.SCIENCE %}
    - Common Level: A 85-100, B 70-84, C 55-69, D 40-54, E 25-39, F 0-24
    - Written + Practical + CBA components
    {% endif %}

    Marking scheme PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractJCSyllabusDiagram(
  pdf_text: string,
  subject: JuniorCycleSubjectSlug,
) -> JuniorCycleSyllabusDiagram[] {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user") }}
    Extract diagrams from the Junior Cycle `{{ subject }}` syllabus.

    For each diagram:
    - diagram_id (e.g. "Figure 1.1")
    - caption
    - diagram_type: "graph" | "table" | "flowchart" | "diagram" | "equation" | "other"
    - associated_topic_id (the LO code the diagram supports)

    Subject-specific guidance:
    {% if subject == JuniorCycleSubjectSlug.MATHEMATICS %}
    - Most diagrams are graphs, charts, or geometric diagrams
    {% elif subject == JuniorCycleSubjectSlug.SCIENCE %}
    - Diagrams are typically labelled diagrams of biological specimens,
      chemical apparatus, or physics experiments
    {% elif subject == JuniorCycleSubjectSlug.GEOGRAPHY %}
    - Diagrams are typically maps, climate cross-sections, or population graphs
    {% endif %}

    Syllabus PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractJCCrossLinguisticConcept(
  pdf_text_en: string,
  pdf_text_ga: string?,
  subject: JuniorCycleSubjectSlug,
) -> JuniorCycleCrossLinguistic[] {
  client GaeilgeJCClient
  prompt #"
    {{ _.role("user") }}
    You are an expert at cross-linguistic concept mapping between English
    and Irish (Gaeilge) versions of the same Junior Cycle `{{ subject }}` syllabus.

    For each cross-linguistic concept you find:
    - en_concept: {term, definition, lo_code}
    - ga_concept: {term, definition, lo_code}
    - equivalence_score: 0.0-1.0

    English PDF text:
    {{ pdf_text_en }}

    Irish PDF text:
    {{ pdf_text_ga }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// BAML function 8: ExtractCrossSubjectTopics (the competency backbone)
// ============================================================================

function ExtractJCCrossSubjectTopics(
  subject: JuniorCycleSubjectSlug,
  language: JuniorCycleLanguage,
  pdf_text: string,
  source_pdf: string,
) -> JuniorCycleCrossSubjectTopicSet {
  client BiepJuniorCycleClient
  prompt #"
    {{ _.role("user") }}
    Extract the cross-subject topic map for Junior Cycle `{{ subject }}`.

    For each topic:
    - topic_id (e.g. "JC-MATH-LO-001")
    - subject: {{ subject }}
    - topic_label_en
    - ncca_lo_code (e.g. "JC-MATH-LO-001")
    - related_subjects: array of JuniorCycleSubjectSlug
    - cross_subject_topic_ids: array of bridging topic IDs
    - key_competencies: array of NCCA Key Competencies

    Junior Cycle syllabus PDF text:
    {{ pdf_text }}

    Source PDF:
    {{ source_pdf }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// Clients (the 4 extraction backends)
// ============================================================================

client<llm> MiniMaxM3Client {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
}

client<llm> GaeilgeJCClient {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
}

client<llm> BiepJuniorCycleClient {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
}
