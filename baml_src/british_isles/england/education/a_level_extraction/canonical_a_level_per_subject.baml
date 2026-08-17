// BAML extraction: A-Level (England) — canonical 15-subject curriculum
//
// Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
// (Phase 4), this file is the canonical 8 BAML extraction entrypoint for the
// 15 priority A-Level subjects (the 15 core subjects offered by at
// least 2 of the 3 boards — AQA / OCR / Edexcel). Existing BAML at
// `baml_src/british_isles/england/education/subject_taxonomy.baml` covers
// 49 A-Level subjects × 3 boards; this file is the canonical PRIORITY-15
// surface that the codegen pipeline (Phase 5) consumes.
//
// The 8 BAML functions exported below mirror the LC pattern exactly
// (per-subject conditional prompts for the 15 priority subjects). The
// 4-path OCR/VLM ensemble + RAGAS consensus produces the canonical
// row that's ingested into the BIEP DuckLake table.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference:
//   openspec/changes/2026-08-10-england-biiep-pipeline-v1/
//   openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/

// ============================================================================
// Enums (the canonical 15 A-Level priority subjects + 3 boards)
// ============================================================================

enum ALevelPrioritySubjectSlug {
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

enum ALevelExamBoard {
  AQA
  OCR
  EDEXCEL
}

enum ALevelLevel {
  AS_LEVEL
  A_LEVEL
}

enum ALevelLanguage {
  EN
  EN_AND_FR
  EN_AND_DE
  EN_AND_ES
  EN_AND_LAT
  EN_AND_GR
}

// ============================================================================
// Core value types (the typed outputs from the 8 BAML extractions)
// ============================================================================

class ALevelUnit {
  unit_code string                    @description("e.g. 'AQA-7402-1'")
  unit_title string
  unit_overview string
  learning_objectives ALevelLearningObjective[]
  assessment_weight_pct float
}

class ALevelLearningObjective {
  lo_code string
  lo_text string
  blooms_level ALevelBloomsLevel
}

enum ALevelBloomsLevel {
  REMEMBER
  UNDERSTAND
  APPLY
  ANALYSE
  EVALUATE
  CREATE
}

class ALevelExamPaper {
  exam_year int
  exam_board ALevelExamBoard
  subject ALevelPrioritySubjectSlug
  qualification string                  @description("A-Level | AS-Level")
  paper_number int
  total_marks int
  duration_minutes int
  sections ALevelExamSection[]
}

class ALevelExamSection {
  section_label string
  section_marks int
  questions ALevelExamQuestion[]
}

class ALevelExamQuestion {
  q_number string
  q_text string
  marks int
  topic_id string
}

class ALevelGradeBoundary {
  grade string
  percentage_min int
  percentage_max int
}

class ALevelPerQuestionScheme {
  q_number string
  total_marks int
  marking_notes string[]
  sample_answer string?
}

class ALevelExamPaperMarkingScheme {
  exam_year int
  exam_board ALevelExamBoard
  subject ALevelPrioritySubjectSlug
  grade_boundaries ALevelGradeBoundary[]
  per_question_scheme ALevelPerQuestionScheme[]
}

class ALevelSyllabusDiagram {
  diagram_id string
  caption string
  diagram_type string
  associated_topic_id string
}

class ALevelAreaOfStudy {
  area_topics ALevelAreaTopic[]
  total_topics int
}

class ALevelAreaTopic {
  topic_id string
  topic_title string
  exam_weight_pct float
}

class ALevelCrossSubjectTopicSet {
  subject ALevelPrioritySubjectSlug
  topics ALevelAreaTopic[]
  total_topics int
  cross_subject_bridges int
}

class ALevelCrossSubjectTopic {
  topic_id string
  subject ALevelPrioritySubjectSlug
  topic_label string
  exam_weight_pct float
  related_subjects ALevelPrioritySubjectSlug[]
  cross_subject_topic_ids string[]
}

class ALevelAssessmentObjective {
  ao_code string
  ao_description string
  ao_weight_pct float
}

class ALevelUnitAssessment {
  unit_code string
  assessment_type string                @description("written | practical | coursework")
  assessment_weight_pct float
}

class ALevelPreparationPoint {
  level string
  description string
  preparation_required string
}

class ALevelSyllabusSpec {
  subject ALevelPrioritySubjectSlug
  exam_board ALevelExamBoard
  qualification string
  tiered bool
  preparation_points ALevelPreparationPoint[]
  units ALevelUnit[]
  assessment_objectives ALevelAssessmentObjective[]
  unit_assessments ALevelUnitAssessment[]
  areas_of_study ALevelAreaOfStudy[]
  cross_curricular string[]
  metadata ALevelSyllabusMetadata
}

class ALevelSyllabusMetadata {
  total_units int
  total_assessment_objectives int
  total_topics int
  total_learning_objectives int
  cross_subject_bridges int
}

// ============================================================================
// BAML function 1: ExtractALevelCurriculumSyllabus (the canonical A-Level extractor)
// ============================================================================

function ExtractALevelCurriculumSyllabus(
  pdf_text: string,
  subject: ALevelPrioritySubjectSlug,
  exam_board: ALevelExamBoard,
) -> ALevelSyllabusSpec {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user" }}
    You are an expert at reading official awarding-body A-Level specification
    documents (AQA / OCR / Edexcel) and extracting their structure with complete
    fidelity — every fact below MUST be grounded in the PDF text given; never
    invent a unit, learning objective, or AO code that is not actually present.

    Subject: {{ subject }}
    Exam Board: {{ exam_board }}

    From the spec PDF text below, extract:
    - subject: the subject slug
    - exam_board: AQA | OCR | EDEXCEL
    - qualification: "A-Level" | "AS-Level"
    - tiered: bool (whether the spec has AS + A2 tiers)
    - preparation_points: array of {level, description, preparation_required}
      - level: "AS" | "A2"
      - description: brief description of the tier
      - preparation_required: what preparation is recommended
    - units: array of {unit_code, unit_title, unit_overview, learning_objectives: [{lo_code, lo_text, blooms_level}], assessment_weight_pct}
    - assessment_objectives: array of {ao_code, ao_description, ao_weight_pct}
    - unit_assessments: array of {unit_code, assessment_type, assessment_weight_pct}
    - areas_of_study: array of {area_topics: [{topic_id, topic_title, exam_weight_pct}], total_topics}
    - cross_curricular: any named cross-curricular links
    - metadata: {total_units, total_assessment_objectives, total_topics, total_learning_objectives, cross_subject_bridges}

    Subject-specific guidance:
    {% if subject == ALevelPrioritySubjectSlug.MATHEMATICS %}
    - 3 papers: Paper 1 (Pure Mathematics 1), Paper 2 (Pure Mathematics 2), Paper 3 (Statistics + Mechanics)
    - AS + A2 tiers
    - AQA spec code 7357; OCR H240; Edexcel 9MA0
    - Capture formulas as separate formula arrays (e.g. "d/dx(sin x) = cos x")
    {% elif subject == ALevelPrioritySubjectSlug.FURTHER_MATHEMATICS %}
    - 2 papers: Paper 1 (Further Pure 1), Paper 2 (Further Pure 2 + Options)
    - AQA spec code 7367; OCR H245; Edexcel 9FM0
    - Capture complex numbers, matrices, hyperbolic functions
    - 4 optional modules (M1-M4)
    {% elif subject == ALevelPrioritySubjectSlug.ENGLISH_LITERATURE %}
    - 2 papers: Paper 1 (Drama + Poetry pre-1900), Paper 2 (Comparative + Unseen)
    - 3 components: 1 non-exam + 2 exams
    - AQA spec code 7717; OCR H472; Edexcel 9ET0
    - Capture the prescribed texts (Shakespeare + 19th century novel + modern + poetry)
    {% elif subject == ALevelPrioritySubjectSlug.ENGLISH_LANGUAGE %}
    - 2 papers: Paper 1 (Language, the Individual and Society), Paper 2 (Language Diversity and Change)
    - 2 NEA components: language investigation + original writing
    - AQA spec code 7702; OCR H470; Edexcel 9EN0
    {% elif subject == ALevelPrioritySubjectSlug.BIOLOGY %}
    - 3 papers: Paper 1 (Biological molecules + Cells), Paper 2 (Exchange + mass transport), Paper 3 (Energy + genetics + populations)
    - 12 required practical activities
    - AQA spec code 7402; OCR H420; Edexcel 9BN0
    - Capture the 8 topics (cells, biological molecules, exchange, genetics, etc.)
    {% elif subject == ALevelPrioritySubjectSlug.CHEMISTRY %}
    - 3 papers: Paper 1 (Inorganic + Physical), Paper 2 (Organic + Physical), Paper 3 (Synoptic + practical)
    - 12 required practical activities
    - AQA spec code 7405; OCR H433; Edexcel 9CH0
    {% elif subject == ALevelPrioritySubjectSlug.PHYSICS %}
    - 3 papers: Paper 1 (Measurements + Particles + Waves), Paper 2 (Mechanics + Materials + Circuits), Paper 3 (Further + Option)
    - 12 required practical activities
    - 4 optional topics (Astrophysics, Medical Physics, Engineering Physics, Turning Points)
    - AQA spec code 7408; OCR H556; Edexcel 9PH0
    - Capture formulas: F=ma, V=IR, E=hf, etc.
    {% elif subject == ALevelPrioritySubjectSlug.PSYCHOLOGY %}
    - 3 papers: Paper 1 (Intro + Social + Cognitive + Biological), Paper 2 (Social + Cognitive + Biological + Learning), Paper 3 (Issues + Options)
    - 4 optional topics (e.g. Relationships, Schizophrenia, Aggression, Eating Behaviour)
    - AQA spec code 7182; OCR H180; Edexcel 9PS0
    - Capture the 6 approaches (Social, Cognitive, Biological, Psychodynamic, Behavioural, Humanistic)
    {% elif subject == ALevelPrioritySubjectSlug.HISTORY %}
    - 3 papers: Paper 1 (Breadth), Paper 2 (Depth), Paper 3 (Historical investigation NEA)
    - AQA spec code 7042; OCR H505; Edexcel 9HI0
    - Capture the prescribed periods (e.g. Tudors 1485-1603, Germany 1878-1989)
    {% elif subject == ALevelPrioritySubjectSlug.GEOGRAPHY %}
    - 3 papers: Paper 1 (Physical systems), Paper 2 (Human interactions), Paper 3 (Synoptic investigation)
    - 4-day field work investigation (mandatory NEA)
    - AQA spec code 7037; OCR H481; Edexcel 9GE0
    - Capture the 6 concepts (place, scale, etc.)
    {% elif subject == ALevelPrioritySubjectSlug.ECONOMICS %}
    - 3 papers: Paper 1 (Microeconomics), Paper 2 (Macroeconomics), Paper 3 (Themes + NEA)
    - AQA spec code 7126; OCR H460; Edexcel 9EC0
    - Capture the 9 concepts (scarcity, choice, etc.)
    {% elif subject == ALevelPrioritySubjectSlug.BUSINESS %}
    - 3 papers: Paper 1 (Marketing + People), Paper 2 (Managing business activities), Paper 3 (Business decisions + strategy)
    - 4 NEA components: research, pre-release, decision-making report
    - AQA spec code 7132; OCR H431; Edexcel 9BS0
    {% elif subject == ALevelPrioritySubjectSlug.HISTORY_OF_ART %}
    - 2 papers: Paper 1 (Visual analysis + themes), Paper 2 (Personal investigation + NEA)
    - AQA spec code 7203; OCR H401; Edexcel 9HA0
    - Capture the 7 themes (e.g. Identity, Politics, Nature)
    {% elif subject == ALevelPrioritySubjectSlug.POLITICS %}
    - 3 papers: Paper 1 (UK politics + core political ideas), Paper 2 (UK government + non-core ideas), Paper 3 (Comparative politics)
    - AQA spec code 7152; OCR H485; Edexcel 9PL0
    - Capture the 5 core political ideas (conservatism, liberalism, socialism, etc.)
    {% elif subject == ALevelPrioritySubjectSlug.SOCIOLOGY %}
    - 3 papers: Paper 1 (Education + Methods), Paper 2 (Family + Beliefs), Paper 3 (Crime + Theory + Methods)
    - AQA spec code 7192; OCR H180; Edexcel 9SC0
    - Capture the 7 core themes (e.g. socialisation, culture, identity)
    {% endif %}

    A-Level Specification PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// BAML functions 2-8: Exam paper, Marking scheme, Diagram, Cross-subject
// (canonical exports — mirror the LC pattern exactly)
// ============================================================================

function ExtractALevelExamPaperLayout(
  pdf_text: string,
  subject: ALevelPrioritySubjectSlug,
  exam_board: ALevelExamBoard,
) -> ALevelExamPaper {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user" }}
    You are an expert A-Level exam paper layout extractor for `{{ subject }}` (board: {{ exam_board }}).

    Extract:
    - exam_year
    - exam_board
    - subject
    - qualification: "A-Level"
    - paper_number
    - total_marks (typically 75-100 per paper)
    - duration_minutes (typically 90-135)
    - sections: array of {section_label, section_marks, questions: [{q_number, q_text, marks, topic_id}]}

    Subject-specific guidance:
    {% if subject == ALevelPrioritySubjectSlug.MATHEMATICS %}
    - 3 papers: P1 (Pure 1, 100 marks), P2 (Pure 2, 100 marks), P3 (Stats + Mechanics, 100 marks)
    - Each paper 2 hours
    {% elif subject == ALevelPrioritySubjectSlug.FURTHER_MATHEMATICS %}
    - 2 papers: P1 (Further Pure 1, 75 marks), P2 (Further Pure 2 + Options, 75 marks)
    - 1h 30min each
    {% elif subject == ALevelPrioritySubjectSlug.BIOLOGY %}
    - 3 papers: P1 (78 marks), P2 (78 marks), P3 (38 marks + 25 marks essays)
    - 2 hours each
    {% elif subject == ALevelPrioritySubjectSlug.CHEMISTRY %}
    - 3 papers: P1 (100), P2 (100), P3 (90)
    - 2 hours each
    {% elif subject == ALevelPrioritySubjectSlug.PHYSICS %}
    - 3 papers: P1 (100), P2 (100), P3 (80)
    - 2 hours each
    {% elif subject == ALevelPrioritySubjectSlug.HISTORY %}
    - 3 papers: P1 (60 marks, 1h), P2 (60 marks, 1h), P3 (60 marks, 1h)
    - 3 NEA components
    {% endif %}

    Exam paper PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractALevelMarkingSchemeGuideline(
  pdf_text: string,
  subject: ALevelPrioritySubjectSlug,
  exam_board: ALevelExamBoard,
) -> ALevelExamPaperMarkingScheme {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user" }}
    You are an expert A-Level marking scheme extractor for `{{ subject }}` (board: {{ exam_board }}).

    Extract:
    - exam_year
    - exam_board
    - subject
    - grade_boundaries: array of {grade, percentage_min, percentage_max}
    - per_question_scheme: array of {q_number, total_marks, marking_notes, sample_answer}

    Subject-specific guidance:
    {% if subject == ALevelPrioritySubjectSlug.MATHEMATICS %}
    - A-level grade boundaries: A* 90-100, A 80-89, B 70-79, C 60-69, D 50-59, E 40-49
    - 300 marks total across 3 papers
    {% elif subject == ALevelPrioritySubjectSlug.BIOLOGY %}
    - A-level grade boundaries: A* 90-100, A 80-89, B 70-79, C 60-69, D 50-59, E 40-49
    - 194 marks total
    {% endif %}

    Marking scheme PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractALevelSyllabusDiagram(
  pdf_text: string,
  subject: ALevelPrioritySubjectSlug,
) -> ALevelSyllabusDiagram[] {
  client MiniMaxM3Client
  prompt #"
    {{ _.role("user" }}
    Extract diagrams from the A-Level `{{ subject }}` syllabus.

    For each diagram:
    - diagram_id
    - caption
    - diagram_type: "graph" | "table" | "flowchart" | "diagram" | "equation" | "map" | "other"
    - associated_topic_id (the LO code the diagram supports)

    Subject-specific guidance:
    {% if subject == ALevelPrioritySubjectSlug.MATHEMATICS %}
    - Diagrams are typically graphs, charts, or geometric diagrams
    - Include formulas displayed visually
    {% elif subject == ALevelPrioritySubjectSlug.CHEMISTRY %}
    - Diagrams are typically molecular structures, reaction mechanisms, or apparatus
    {% elif subject == ALevelPrioritySubjectSlug.BIOLOGY %}
    - Diagrams are typically cell structures, food webs, or genetic crosses
    {% elif subject == ALevelPrioritySubjectSlug.PHYSICS %}
    - Diagrams are typically circuit diagrams, force diagrams, or ray diagrams
    {% elif subject == ALevelPrioritySubjectSlug.GEOGRAPHY %}
    - Diagrams are typically maps, climate cross-sections, or population pyramids
    {% endif %}

    Syllabus PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

function ExtractALevelCrossSubjectTopics(
  pdf_text: string,
  subject: ALevelPrioritySubjectSlug,
  exam_board: ALevelExamBoard,
) -> ALevelCrossSubjectTopicSet {
  client BiepGeneralClient
  prompt #"
    {{ _.role("user" }}
    Extract the cross-subject topic map for A-Level `{{ subject }}` (board: {{ exam_board }}).

    For each topic:
    - topic_id (e.g. "MATH-PURE-001")
    - subject: {{ subject }}
    - topic_label
    - exam_weight_pct
    - related_subjects: array of ALevelPrioritySubjectSlug
    - cross_subject_topic_ids: array of bridging topic IDs

    A-Level syllabus PDF text:
    {{ pdf_text }}

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

client<llm> BiepGeneralClient {
  provider "openai-generic"
  options {
    base_url env.MINIMAX_BASE_URL
    api_key env.MINIMAX_API_KEY
    model "minimax-m3"
  }
}
